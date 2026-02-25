from flask import Flask, request, jsonify, send_from_directory, g
from flask_cors import CORS
import os
import pandas as pd
import numpy as np
from scipy.signal import savgol_filter
from sklearn.metrics import mean_absolute_error, mean_squared_error
import time
from models.arima_predictor import predict_with_arima

from werkzeug.utils import secure_filename
from models.prediction_tool import analyze_and_predict
from models.agent_chain import get_conversational_response, generate_standalone_report, smart_predict
from agent.reasoner import TSReasoner
from utils.auth_utils import login_required, decode_token
from blueprints.credits import check_and_consume_chat

from extensions import db, SECRET_KEY, DATABASE_URL

# --- 初始化 Flask 应用 ---
app = Flask(__name__, static_folder='../dist')
app.config['SECRET_KEY'] = SECRET_KEY
app.config['SQLALCHEMY_DATABASE_URI'] = DATABASE_URL or (
    'sqlite:///' + os.path.join(os.path.abspath(os.path.dirname(__file__)), 'shu_prophet.db')
)
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
CORS(app)

# 初始化数据库
db.init_app(app)

# 注册蓝图
from blueprints.auth import auth_bp
from blueprints.user import user_bp
from blueprints.community import community_bp
from blueprints.credits import credits_bp
from blueprints.admin import admin_bp
app.register_blueprint(auth_bp)
app.register_blueprint(user_bp)
app.register_blueprint(community_bp)
app.register_blueprint(credits_bp)
app.register_blueprint(admin_bp)

# 创建数据库表
with app.app_context():
    from models.db_models import User, Post, Comment, PostLike, RedeemCode, DailyUsage, CreditLog
    try:
        db.create_all()
    except Exception:
        pass

# --- 定义路径 ---
STATIC_DATA_DIR = 'static_data'
UPLOADS_DIR = 'uploads'
if not os.path.exists(UPLOADS_DIR):
    os.makedirs(UPLOADS_DIR)

# --- 数据预处理与计算函数 ---
def _sanitize(obj):
    """递归将 numpy 类型转为 Python 原生类型。"""
    if isinstance(obj, dict):
        return {k: _sanitize(v) for k, v in obj.items()}
    if isinstance(obj, (list, tuple)):
        return [_sanitize(v) for v in obj]
    if isinstance(obj, (np.integer,)):
        return int(obj)
    if isinstance(obj, (np.floating,)):
        return float(obj)
    if isinstance(obj, (np.bool_,)):
        return bool(obj)
    if isinstance(obj, np.ndarray):
        return obj.tolist()
    return obj

def smooth(y, win=11, poly=3):
    """Savitzky-Golay平滑函数"""
    if len(y) < win:
        return y
    return savgol_filter(y, window_length=win, polyorder=poly)

# --- 思考模式辅助函数 ---
_THINK_KEYWORDS = ['思考', '深度分析', '详细分析', '推理', '深入', '仔细',
                   'think', 'analyze', 'deep', 'reason', '为什么', '原因',
                   '分析一下', '帮我看看', '诊断']

def _should_think(message: str) -> bool:
    """根据用户消息判断是否启用思考模式。"""
    if not message:
        return False
    msg = message.lower()
    return any(kw in msg for kw in _THINK_KEYWORDS)

def _format_trajectory(trajectory: dict) -> list:
    """将推理轨迹格式化为前端可展示的结构。"""
    steps = trajectory.get("steps", [])
    formatted = []
    for s in steps:
        obs = s.get("observation", {})
        # 生成简洁的结果摘要
        summary_parts = []
        for k, v in obs.items():
            if k == "tool":
                continue
            sv = str(v)
            if len(sv) > 50:
                sv = sv[:47] + "..."
            summary_parts.append(f"{k}={sv}")
        formatted.append({
            "step": s["step"],
            "thought": s["thought"],
            "tool": s["action"],
            "result": ", ".join(summary_parts) if summary_parts else "done",
            "time": s.get("timestamp", 0)
        })
    return formatted

# --- API 路由 ---

@app.route('/api/datasets', methods=['GET'])
def get_datasets():
    """API: 获取所有可用的科研数据集文件名。"""
    datasets_path = os.path.join(STATIC_DATA_DIR, 'research_datasets')
    try:
        files = [f for f in os.listdir(datasets_path) if f.endswith('.csv')]
        return jsonify(files)
    except FileNotFoundError:
        return jsonify([])

@app.route('/api/parse-csv', methods=['POST'])
def parse_csv():
    """
    【静态核心API - 终极版】: 
    读取CSV(含模型名称)，执行预处理，计算MAE/MSE，并返回所有数据。
    """
    data = request.json
    dataset_file = data.get('dataset')
    if not dataset_file:
        return jsonify({"error": "Missing dataset filename"}), 400

    file_path = os.path.join(STATIC_DATA_DIR, 'research_datasets', dataset_file)

    try:
        # 1. 读取CSV（第一行是列名）
        raw = pd.read_csv(file_path)

        # 2. 从列名中提取模型名称
        model_names_raw = raw.columns.tolist()

        # 3. 数据清理与处理
        INVALID = -1.0145037163717687
        TOL = 1e-6

        response = {"actual_data": {}, "model_predictions": []}

        # 先处理并存储Ground Truth数据
        gt_x_col, gt_y_col = 'actual_x', 'actual_y'
        gt_df_raw = raw[[gt_x_col, gt_y_col]].dropna()
        gt_df = gt_df_raw.loc[~np.isclose(gt_df_raw[gt_y_col], INVALID, atol=TOL)].astype(float)
        gt_df = gt_df.groupby(gt_x_col, as_index=False)[gt_y_col].mean()
        gt_y_smooth = smooth(gt_df[gt_y_col].values)
        gt_processed_data = list(zip(gt_df[gt_x_col].values, gt_y_smooth))
        response["actual_data"] = {"model_name": "Actual", "data": gt_processed_data}

        # 循环处理所有预测模型
        model_cols = [col for col in raw.columns if col.endswith('_x') and col != 'actual_x']
        for model_x_col in model_cols:
            model_name = model_x_col.replace('_x', '')
            model_y_col = model_name + '_y'

            if model_y_col not in raw.columns:
                continue

            pred_df_raw = raw[[model_x_col, model_y_col]].dropna()
            pred_df = pred_df_raw.loc[~np.isclose(pred_df_raw[model_y_col], INVALID, atol=TOL)].astype(float)
            pred_df = pred_df.groupby(model_x_col, as_index=False)[model_y_col].mean()

            pred_y_smooth = smooth(pred_df[model_y_col].values)
            pred_processed_data = list(zip(pred_df[model_x_col].values, pred_y_smooth))

            # 计算性能指标
            gt_y_interpolated = np.interp(pred_df[model_x_col], gt_df[gt_x_col], gt_y_smooth)
            mae = mean_absolute_error(gt_y_interpolated, pred_y_smooth)
            mse = mean_squared_error(gt_y_interpolated, pred_y_smooth)

            response["model_predictions"].append({
                "model_name": model_name,
                "data": pred_processed_data,
                "metrics": {
                    "mae": round(mae, 4),
                    "mse": round(mse, 4)
                }
            })
        
        time.sleep(1.5)
        return jsonify(response)

    except Exception as e:
        return jsonify({"error": f"Backend Error: {str(e)}"}), 500

@app.route('/api/live-predict', methods=['POST'])
def live_predict():
    """【动态核心API】: 接收用户上传的文件并进行实时预测。"""
    if 'file' not in request.files:
        return jsonify({"error": "No file part"}), 400
    file = request.files['file']
    if file.filename == '':
        return jsonify({"error": "No selected file"}), 400
    if file:
        filepath = os.path.join(UPLOADS_DIR, file.filename)
        file.save(filepath)
        prediction_result = predict_with_arima(filepath, steps=10)
        return jsonify(prediction_result)
    return jsonify({"error": "File upload failed"}), 500

# --- 核心升级：新增一个只处理文本消息的API ---
@app.route('/api/agent-message', methods=['POST'])
@login_required
def agent_message():
    """【智能助理对话API】: 接收用户文本消息，返回助理的文本回复。"""
    data = request.json
    user_message = data.get('message')
    session_id = data.get('session_id', 'default_session')

    if not user_message:
        return jsonify({"error": "消息内容不能为空"}), 400

    # 简单问候直接返回静态回复，不消耗配额和AI调用
    _GREETING_KEYWORDS = ['你好', '您好', 'hello', 'hi', '嗨', '在吗']
    if user_message.strip().lower() in _GREETING_KEYWORDS:
        return jsonify({"reply": (
            "你好！我是**鼠先知 (SHU Prophet)** AI智能助理 🐭\n\n"
            "我可以帮你进行时间序列数据的分析与预测。"
            "只需上传一个CSV文件（含X、Y两列），"
            "我就能为你生成专业的预测报告。\n\n"
            "有什么我可以帮你的吗？"
        )})

    # 检查用量并消耗配额
    ok, err = check_and_consume_chat(g.user_id)
    if not ok:
        return jsonify({"error": err}), 403

    try:
        agent_reply = get_conversational_response(user_message, session_id)
    except Exception as e:
        return jsonify({"reply": "抱歉，AI服务暂时不可用，请稍后再试。"}), 200

    return jsonify({"reply": agent_reply})

# --- 智能助理文件处理API（支持思考模式）---
@app.route('/api/agent-upload-predict', methods=['POST'])
@login_required
def agent_upload_predict():
    """智能助理文件处理API: 接收文件+可选消息，支持思考模式深度推理。"""
    # 检查用量并消耗配额
    ok, err = check_and_consume_chat(g.user_id)
    if not ok:
        return jsonify({"error": err}), 403

    if 'file' not in request.files:
        return jsonify({"error": "请求中未找到文件部分"}), 400

    file = request.files['file']
    if file.filename == '':
        return jsonify({"error": "未选择任何文件"}), 400

    # 获取用户附带的文本消息
    user_message = request.form.get('message', '')

    if file:
        filename = secure_filename(file.filename)
        filepath = os.path.join(UPLOADS_DIR, filename)
        file.save(filepath)

        try:
            # 1. ARIMA 基础分析
            analysis_result = analyze_and_predict(filepath)
            report_markdown = generate_standalone_report(analysis_result)
        except Exception as e:
            return jsonify({"error": f"数据分析失败: {str(e)}"}), 500

        # 2. 智能预测引擎
        smart_result = None
        summary = analysis_result.get("summary_stats", {})
        data_y = summary.get("historical_y", [])
        forecast_steps = summary.get("forecast_steps", 10)

        if len(data_y) >= 10:
            try:
                smart_result = smart_predict(data_y, steps=forecast_steps)
            except Exception:
                pass

        # 3. 思考模式：深度推理分析
        thinking_result = None
        if _should_think(user_message) and len(data_y) >= 10:
            try:
                reasoner = TSReasoner()
                raw = reasoner.predict(data_y, steps=forecast_steps)
                thinking_result = _sanitize({
                    "trajectory": _format_trajectory(raw.get("trajectory", {})),
                    "data_profile": raw.get("data_profile", {}),
                    "predictions": raw.get("predictions", []),
                    "confidence": raw.get("confidence", {}),
                })
            except Exception:
                pass

        response_data = {
            "report": report_markdown,
            "chart_data": analysis_result.get("chart_data", None),
            "smart_prediction": smart_result,
            "thinking": thinking_result,
        }

        return jsonify(_sanitize(response_data))

    return jsonify({"error": "文件上传失败"}), 500

@app.route('/api/smart-predict', methods=['POST'])
def smart_predict_api():
    """【鼠先知智能预测引擎API】: 接收文件，执行三阶段Agent协作预测。"""
    if 'file' not in request.files:
        return jsonify({"error": "请求中未找到文件部分"}), 400

    file = request.files['file']
    if file.filename == '':
        return jsonify({"error": "未选择任何文件"}), 400

    steps = request.form.get('steps', 10, type=int)

    if file:
        filename = secure_filename(file.filename)
        filepath = os.path.join(UPLOADS_DIR, filename)
        file.save(filepath)

        try:
            df = pd.read_csv(filepath, dtype=str, encoding='utf-8-sig')
            if df.shape[1] < 2:
                return jsonify({"error": "CSV文件必须至少包含两列"}), 400

            y_col = df.columns[1]
            data_y = pd.to_numeric(df[y_col], errors='coerce').dropna().tolist()

            if len(data_y) < 10:
                return jsonify({"error": f"有效数据点过少({len(data_y)}个)，至少需要10个"}), 400

            result = smart_predict(data_y, steps=steps)
            return jsonify(result)
        except Exception as e:
            return jsonify({"error": f"预测失败: {str(e)}"}), 500

    return jsonify({"error": "文件上传失败"}), 500

@app.route('/api/agent-reason', methods=['POST'])
def agent_reason():
    """【思考模式推理API】: 执行完整推理循环，返回预测结果与推理轨迹。"""
    if 'file' not in request.files:
        return jsonify({"error": "请求中未找到文件部分"}), 400

    file = request.files['file']
    if file.filename == '':
        return jsonify({"error": "未选择任何文件"}), 400

    steps = request.form.get('steps', 10, type=int)

    if file:
        filename = secure_filename(file.filename)
        filepath = os.path.join(UPLOADS_DIR, filename)
        file.save(filepath)

        try:
            df = pd.read_csv(filepath, dtype=str, encoding='utf-8-sig')
            if df.shape[1] < 2:
                return jsonify({"error": "CSV文件必须至少包含两列"}), 400

            y_col = df.columns[1]
            data_y = pd.to_numeric(df[y_col], errors='coerce').dropna().tolist()

            if len(data_y) < 10:
                return jsonify({"error": f"有效数据点过少({len(data_y)}个)，至少需要10个"}), 400

            reasoner = TSReasoner()
            result = reasoner.predict(data_y, steps=steps)
            return jsonify(_sanitize(result))
        except Exception as e:
            return jsonify({"error": f"推理失败: {str(e)}"}), 500

    return jsonify({"error": "文件上传失败"}), 500

# --- 服务前端静态文件的路由 ---
# 这个路由捕获所有不是API的请求
@app.route('/', defaults={'path': ''})
@app.route('/<path:path>')
def serve(path):
    # 如果请求的是一个存在的文件 (如/assets/index.js), 则直接发送该文件
    if path != "" and os.path.exists(os.path.join(app.static_folder, path)):
        return send_from_directory(app.static_folder, path)
    # 否则，发送入口index.html，让Vue Router接管路由
    else:
        return send_from_directory(app.static_folder, 'index.html')

if __name__ == '__main__':
    app.run(debug=True, port=5000)
