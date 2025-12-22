from flask import Blueprint, request, jsonify, g
from flask_jwt_extended import jwt_required, get_jwt_identity
from utils.status import Status
from sql.database import get_db
from sql.UserSql import UserGetInfo

# Create blueprint
user_bp = Blueprint('user', __name__, url_prefix='/User')

@user_bp.before_request
def handle_options():
    """处理跨域预检请求"""
    if request.method == 'OPTIONS':
        response = jsonify({'status': 'preflight'})
        response.headers.add('Access-Control-Allow-Headers', 'Content-Type,Authorization')
        response.headers.add('Access-Control-Allow-Methods', 'GET,PUT,POST,DELETE,OPTIONS')
        response.headers.add('Access-Control-Allow-Origin', '*')
        return response

@user_bp.before_request
def before_request():
    """请求前处理，建立数据库连接"""
    try:
        connection = get_db()
        request.connection = connection
    except Exception as e:
        print(f"Database connection creation failed: {str(e)}")
        request.connection = None

@user_bp.route('/GetInfo', methods=['GET','OPTIONS'])
@jwt_required()
def get_user_info():
    """获取当前用户信息"""
    try:
        # 获取当前用户的邮箱
        current_email = get_jwt_identity()

        if not current_email:
            return jsonify(Status.AuthFailed.ToResponse("未找到用户信息"))

        # 获取数据库连接
        connection = getattr(request, 'connection', None)
        if isinstance(connection, Status):
            return jsonify(connection.ToResponse())

        # 检查是否是超级管理员
        if current_email == "admin@dream.com":
            admin_info = {
                "UserID": -1,
                "UserName": "超级管理员",
                "Email": "admin@dream.com",
                "AvatarUrl": None,
                "Role": "super_admin"
            }
            response = Status.OK.ToResponse()
            response['Data'] = admin_info
            return jsonify(response)

        # 查询普通用户信息
        user_info, user_status = UserGetInfo(connection, current_email)
        if user_status == Status.OK and user_info:
            response = Status.OK.ToResponse()
            response['Data'] = user_info
            return jsonify(response)
        else:
            return jsonify(user_status.ToResponse())

    except Exception as e:
        print(f"Get user info exception: {str(e)}")
        return jsonify(Status.ErrorRequest.ToResponse(str(e)))