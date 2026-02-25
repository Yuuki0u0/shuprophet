import jwt
import datetime
from functools import wraps
from flask import request, jsonify, g
from extensions import SECRET_KEY


def generate_token(user_id):
    payload = {
        'user_id': user_id,
        'exp': datetime.datetime.utcnow() + datetime.timedelta(days=7),
        'iat': datetime.datetime.utcnow()
    }
    return jwt.encode(payload, SECRET_KEY, algorithm='HS256')


def decode_token(token):
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=['HS256'])
        return payload['user_id']
    except (jwt.ExpiredSignatureError, jwt.InvalidTokenError):
        return None


def login_required(f):
    @wraps(f)
    def decorated(*args, **kwargs):
        token = request.headers.get('Authorization', '').replace('Bearer ', '')
        if not token:
            return jsonify({'error': '请先登录'}), 401
        user_id = decode_token(token)
        if user_id is None:
            return jsonify({'error': '登录已过期，请重新登录'}), 401
        g.user_id = user_id
        return f(*args, **kwargs)
    return decorated
