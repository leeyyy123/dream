from flask import Blueprint, request, jsonify, g
from flask_jwt_extended import create_access_token
import hashlib

# 导入项目模块
from utils.status import Status
from sql.UserSql import UserCheckLogin, UserCheckEmailExists, UserInsert
from utils.Objects import Users
from sql.database import get_db
from sql.LogSql import LogLoginSuccess, LogLoginFailed, LogRegistrationSuccess, LogRegistrationFailed, GetClientIP, GetUserAgent


# 超级管理员配置
AdminEmail = "admin@dream.com"  # 超级管理员邮箱
AdminPassword = "8d969eef6ecad3c29a3a629280e686cf0c3f5d5a86aff3ca12020c923adc6c92"  # "123456"的哈希

# Create blueprint
auth_bp = Blueprint('auth', __name__, url_prefix='/Auth')

@auth_bp.before_app_request
def handle_options():
    """处理跨域预检请求"""
    if request.method == 'OPTIONS':
        response = jsonify({'status': 'preflight'})
        response.headers.add('Access-Control-Allow-Headers', 'Content-Type,Authorization')
        response.headers.add('Access-Control-Allow-Methods', 'GET,PUT,POST,DELETE,OPTIONS')
        response.headers.add('Access-Control-Allow-Origin', '*')
        return response

@auth_bp.before_request
def before_request():
    """请求前处理，建立数据库连接"""
    try:
        connection = get_db()
        request.connection = connection
    except Exception as e:
        print(f"Database connection creation failed: {str(e)}")
        request.connection = None

@auth_bp.route('/Login', methods=['POST','OPTIONS'])
def login():
    """用户登录"""
    try:
        data = request.get_json()

        if not data or 'Email' not in data or 'Password' not in data:
            response = Status.ErrorRequest.ToResponse("参数不完整")
            response['Token'] = None
            response['UserID'] = None
            return jsonify(response)

        email = data['Email'].strip()
        password = data['Password']

        # 获取客户端信息用于日志记录
        client_ip = GetClientIP(request)
        user_agent = GetUserAgent(request)

        print(f"Login attempt: {email} - IP: {client_ip}")

        # 获取数据库连接
        connection = getattr(request, 'connection', Status.DatabaseConnectionError)
        if isinstance(connection, Status):
            response = connection.ToResponse()
            response['Token'] = None
            response['UserID'] = None
            return jsonify(response)

        # 超级管理员登录
        if email == AdminEmail and hashlib.sha256(password.encode()).hexdigest() == AdminPassword:
            # 记录超级管理员登录成功日志
            log_status = LogLoginSuccess(connection, -1, email, client_ip, user_agent)
            if log_status != Status.OK:
                print(f"Log recording failed: {email}")

            additional_claims = {
                'role': 'super_admin',
                'is_superuser': True,
                'permissions': ['read', 'write', 'delete', 'admin', 'manage_users']
            }
            access_token = create_access_token(
                identity=email,
                additional_claims=additional_claims
            )
            response = Status.SuperLogin.ToResponse()
            response['Token'] = access_token
            response['UserID'] = -1  # 超级管理员ID为-1
            return jsonify(response)

        # 普通用户登录
        query_status, user_id = UserCheckLogin(connection, email, password)
        if query_status == Status.OK and user_id:
            # 记录普通用户登录成功日志
            log_status = LogLoginSuccess(connection, user_id, email, client_ip, user_agent)
            if log_status != Status.OK:
                print(f"Log recording failed: {email}")

            additional_claims = {
                'role': 'user',
                'is_superuser': False,
                'permissions': ['read']
            }
            access_token = create_access_token(
                identity=email,
                additional_claims=additional_claims
            )
            response = Status.OK.ToResponse()
            response['Token'] = access_token
            response['UserID'] = user_id
            return jsonify(response)

        # 登录失败 - 记录登录失败日志
        error_reason = "Invalid username or password"
        if query_status == Status.UserUnexist:
            error_reason = "User does not exist"
        elif query_status == Status.ErrorPassword:
            error_reason = "Incorrect password"

        # 记录登录失败日志
        log_status = LogLoginFailed(connection, email, client_ip, user_agent, error_reason)
        if log_status != Status.OK:
            print(f"Login failed log recording failed: {email}")

        response = query_status.ToResponse()
        response['Token'] = None
        response['UserID'] = None
        return jsonify(response)

    except Exception as e:
        print(f"Login API exception: {str(e)}")
        response = Status.ErrorRequest.ToResponse(str(e))
        response['Token'] = None
        response['UserID'] = None
        return jsonify(response)

@auth_bp.route("/Sign", methods=['POST','OPTIONS'])
def sign():
    """直接注册用户（不需要验证码）"""
    try:
        data = request.get_json()

        if (not data or
                'Name' not in data or
                'Email' not in data or
                'Password' not in data):
            response = Status.ErrorRequest.ToResponse("参数不完整")
            return jsonify(response)

        username = data['Name'].strip()
        email = data['Email'].strip()
        password = data['Password'].strip()

        # 获取客户端信息用于日志记录
        client_ip = GetClientIP(request)
        user_agent = GetUserAgent(request)

        connection = getattr(request, 'connection', None)
        if isinstance(connection, Status):
            response = connection.ToResponse()
            return jsonify(response)

        # 超级管理员不能注册
        if email == AdminEmail:
            return jsonify(Status.ErrorRequest.ToResponse("超级管理员不能通过此方式注册"))

        # 检查邮箱是否已存在
        check_status = UserCheckEmailExists(connection, email)
        if check_status != Status.OK:
            return jsonify(check_status.ToResponse())

        # 直接注册用户
        query_status = UserInsert(connection, Users(
            Name=username,
            Email=email,
            Password=password
        ))

        # 记录注册日志
        print(f"Registration query_status: {query_status}, email: {email}")
        if query_status == Status.OK:
            # 获取用户ID
            try:
                # 尝试获取刚插入的用户ID
                with connection.cursor() as cursor:
                    cursor.execute("SELECT LAST_INSERT_ID() as user_id")
                    result = cursor.fetchone()
                    print(f"Raw result from LAST_INSERT_ID(): {result}, type: {type(result)}")

                    if result:
                        if isinstance(result, dict):
                            user_id = result.get('user_id')
                        else:
                            user_id = result[0] if len(result) > 0 else None
                        print(f"Processed user_id: {user_id}, type: {type(user_id)}")
                    else:
                        user_id = None
                        print("No result returned from LAST_INSERT_ID()")

                    if user_id:
                        log_status = LogRegistrationSuccess(connection, user_id, email, username, client_ip, user_agent)
                        print(f"LogRegistrationSuccess returned: {log_status}")
                        if log_status != Status.OK:
                            print(f"Registration success log recording failed: {email}")
                    else:
                        print(f"Failed to get user_id for registration success log: {email}")
            except Exception as e:
                print(f"Get user ID or record registration log failed: {e}, email: {email}")
        else:
            # 记录注册失败日志
            print(f"Registration failed, recording failed log for: {email}, status: {query_status}")
            log_status = LogRegistrationFailed(connection, email, username, client_ip, user_agent, str(query_status))
            if log_status != Status.OK:
                print(f"Registration failed log recording failed: {email}")

        response = query_status.ToResponse()
        return jsonify(response)

    except Exception as e:
        print(f"Registration API exception: {str(e)}")
        return jsonify(Status.ErrorRequest.ToResponse(str(e)))

@auth_bp.route("/Verify", methods=['POST', 'OPTIONS'])
def verify():
    """验证注册"""
    try:
        data = request.get_json()
        if (not data or
                'Name' not in data or
                'Email' not in data or
                'Password' not in data or
                'VerifyCode' not in data):
            response = Status.ErrorRequest.ToResponse("参数不完整")
            return jsonify(response)

        username = data['Name'].strip()
        email = data['Email'].strip()
        password = data['Password']
        verify_code = data['VerifyCode']

        # 获取客户端信息用于日志记录
        client_ip = GetClientIP(request)
        user_agent = GetUserAgent(request)

        # 获取数据库连接
        connection = getattr(request, 'connection', None)
        if isinstance(connection, Status):
            response = connection.ToResponse()
            return jsonify(response)

        # 检查用户是否已存在
        check_status = UserCheckEmailExists(connection, email)
        if check_status == Status.UserExist:
            return jsonify(Status.UserExist.ToResponse())

        # 验证验证码
        redis_status = redis_verify_code(email, verify_code)
        if redis_status != Status.OK:
            return jsonify(redis_status.ToResponse())

        # 注册新用户
        query_status = UserInsert(connection, Users(
            Name=username,
            Email=email,
            Password=password
        ))

        # 记录注册日志
        print(f"Verification registration query_status: {query_status}, email: {email}")
        if query_status == Status.OK:
            delete_verification_code(email)  # 注册成功后删除验证码

            # 获取用户ID并记录注册成功日志
            try:
                with connection.cursor() as cursor:
                    cursor.execute("SELECT LAST_INSERT_ID() as user_id")
                    result = cursor.fetchone()
                    print(f"Verification raw result from LAST_INSERT_ID(): {result}, type: {type(result)}")

                    if result:
                        if isinstance(result, dict):
                            user_id = result.get('user_id')
                        else:
                            user_id = result[0] if len(result) > 0 else None
                        print(f"Verification processed user_id: {user_id}, type: {type(user_id)}")
                    else:
                        user_id = None
                        print("Verification no result returned from LAST_INSERT_ID()")

                    if user_id:
                        log_status = LogRegistrationSuccess(connection, user_id, email, username, client_ip, user_agent)
                        print(f"Verification LogRegistrationSuccess returned: {log_status}")
                        if log_status != Status.OK:
                            print(f"Verification registration success log recording failed: {email}")
                    else:
                        print(f"Verification failed to get user_id for registration success log: {email}")
            except Exception as e:
                print(f"Verification get user ID or record registration log failed: {e}, email: {email}")
        else:
            # 记录注册失败日志
            print(f"Verification registration failed, recording failed log for: {email}, status: {query_status}")
            log_status = LogRegistrationFailed(connection, email, username, client_ip, user_agent, str(query_status))
            if log_status != Status.OK:
                print(f"Verification registration failed log recording failed: {email}")

        response = query_status.ToResponse()
        return jsonify(response)

    except Exception as e:
        print(f"Verification registration API exception: {str(e)}")
        return jsonify(Status.ErrorRequest.ToResponse(str(e)))

