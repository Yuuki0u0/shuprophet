import os
from flask import Blueprint, request, jsonify, g, send_from_directory
from werkzeug.utils import secure_filename
from extensions import db
from models.db_models import User
from utils.auth_utils import login_required

user_bp = Blueprint('user', __name__, url_prefix='/api/user')

AVATARS_DIR = os.path.join(os.path.dirname(os.path.dirname(__file__)), 'avatars')
if not os.path.exists(AVATARS_DIR):
    os.makedirs(AVATARS_DIR)

ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg', 'gif', 'webp'}


def _allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS


@user_bp.route('/profile', methods=['PUT'])
@login_required
def update_profile():
    user = User.query.get(g.user_id)
    data = request.json or {}
    if 'nickname' in data:
        user.nickname = data['nickname'].strip()[:80]
    if 'bio' in data:
        user.bio = data['bio'].strip()[:500]
    db.session.commit()
    return jsonify({'user': _pub_user(user)})


@user_bp.route('/avatar', methods=['POST'])
@login_required
def upload_avatar():
    if 'file' not in request.files:
        return jsonify({'error': '未找到文件'}), 400
    file = request.files['file']
    if file.filename == '' or not _allowed_file(file.filename):
        return jsonify({'error': '不支持的文件格式'}), 400

    ext = file.filename.rsplit('.', 1)[1].lower()
    filename = f'avatar_{g.user_id}.{ext}'
    filepath = os.path.join(AVATARS_DIR, secure_filename(filename))
    file.save(filepath)

    user = User.query.get(g.user_id)
    user.avatar_url = f'/api/user/avatars/{filename}'
    db.session.commit()
    return jsonify({'avatar_url': user.avatar_url})


@user_bp.route('/avatars/<path:filename>', methods=['GET'])
def serve_avatar(filename):
    return send_from_directory(AVATARS_DIR, filename)


@user_bp.route('/<int:user_id>', methods=['GET'])
def get_user_public(user_id):
    user = User.query.get(user_id)
    if not user:
        return jsonify({'error': '用户不存在'}), 404
    return jsonify({'user': _pub_user(user)})


def _pub_user(user):
    return {
        'id': user.id,
        'username': user.username,
        'nickname': user.nickname,
        'avatar_url': user.avatar_url,
        'bio': user.bio,
        'created_at': user.created_at.isoformat()
    }
