from flask import Blueprint, request, jsonify, g
from flask_jwt_extended import jwt_required, get_jwt_identity
from utils.status import Status
from sql.database import get_db
from sql.DreamSql import DreamCreate, DreamGetList, DreamGetDetail
from sql.EmotionTypeSql import GetAllEmotions, GetAllDreamTypes
from sql.LogSql import LogDreamRecordSuccess, LogDreamRecordFailed, LogDreamUpdate, GetClientIP, GetUserAgent

# Create blueprint
dream_bp = Blueprint('dream', __name__, url_prefix='/Dream')

@dream_bp.before_app_request
def handle_options():
    """处理跨域预检请求"""
    if request.method == 'OPTIONS':
        response = jsonify({'status': 'preflight'})
        response.headers.add('Access-Control-Allow-Headers', 'Content-Type,Authorization')
        response.headers.add('Access-Control-Allow-Methods', 'GET,PUT,POST,DELETE,OPTIONS')
        response.headers.add('Access-Control-Allow-Origin', '*')
        return response

@dream_bp.before_request
def before_request():
    """请求前处理，建立数据库连接"""
    try:
        connection = get_db()
        request.connection = connection
    except Exception as e:
        print(f"Database connection creation failed: {str(e)}")
        request.connection = None

@dream_bp.route('/Create', methods=['POST','OPTIONS'])
@jwt_required()
def create_dream():
    """创建梦境记录"""
    try:
        # 获取客户端信息用于日志记录
        client_ip = GetClientIP(request)
        user_agent = GetUserAgent(request)

        # 获取请求数据
        data = request.get_json()
        if not data:
            response = Status.ErrorRequest.ToResponse("请求体不能为空")
            return jsonify(response)

        # 验证必填字段
        required_fields = ['Title', 'Content', 'DreamDate']
        for field in required_fields:
            if field not in data or not data[field]:
                error_msg = f"缺少必填字段: {field}"
                return jsonify(Status.ErrorRequest.ToResponse(error_msg))

        title = data['Title'].strip()
        content = data['Content'].strip()
        dream_date = data['DreamDate']
        sleep_quality = data.get('SleepQuality', 3)
        lucidity_level = data.get('LucidityLevel', 3)
        is_public = data.get('IsPublic', False)
        emotion_ids = data.get('EmotionIds', [])
        dream_type_ids = data.get('DreamTypeIds', [])

        # 数据验证
        if len(title) < 1:
            return jsonify(Status.ErrorRequest.ToResponse("梦境标题不能为空"))
        if len(title) > 100:
            return jsonify(Status.ErrorRequest.ToResponse("梦境标题不能超过100个字符"))
        if len(content) < 10:
            return jsonify(Status.ErrorRequest.ToResponse("梦境内容至少需要10个字符"))
        if len(content) > 2000:
            return jsonify(Status.ErrorRequest.ToResponse("梦境内容不能超过2000个字符"))

        # 验证数值范围
        if not (1 <= sleep_quality <= 5):
            return jsonify(Status.ErrorRequest.ToResponse("睡眠质量必须在1-5之间"))
        if not (1 <= lucidity_level <= 5):
            return jsonify(Status.ErrorRequest.ToResponse("梦境清晰度必须在1-5之间"))

        # 验证情绪和梦境类型数据
        if not isinstance(emotion_ids, list):
            return jsonify(Status.ErrorRequest.ToResponse("情绪ID列表必须是数组格式"))
        if not isinstance(dream_type_ids, list):
            return jsonify(Status.ErrorRequest.ToResponse("梦境类型ID列表必须是数组格式"))

        # 验证日期格式
        try:
            from datetime import datetime
            dream_date_obj = datetime.strptime(dream_date, '%Y-%m-%d').date()
        except ValueError:
            return jsonify(Status.ErrorRequest.ToResponse("日期格式不正确，请使用YYYY-MM-DD格式"))

        # 获取数据库连接
        connection = getattr(request, 'connection', None)
        if isinstance(connection, Status):
            return jsonify(connection.ToResponse())

        # 获取当前用户信息
        current_email = get_jwt_identity()
        if not current_email:
            return jsonify(Status.AuthFailed.ToResponse("未找到用户信息"))

        # 查询用户ID
        with connection.cursor() as cursor:
            cursor.execute("SELECT UserID FROM Users WHERE Email = %s", (current_email,))
            user_result = cursor.fetchone()
            if not user_result:
                return jsonify(Status.UserUnexist.ToResponse())

            user_id = user_result['UserID']

        # 创建梦境记录
        dream_status = DreamCreate(
            connection,
            user_id=user_id,
            title=title,
            content=content,
            dream_date=dream_date_obj,
            sleep_quality=sleep_quality,
            lucidity_level=lucidity_level,
            is_public=is_public,
            emotion_ids=emotion_ids,
            dream_type_ids=dream_type_ids
        )

        # 记录日志
        if dream_status == Status.OK:
            log_status = LogDreamRecordSuccess(
                connection, user_id, title, dream_date, sleep_quality,
                lucidity_level, is_public, client_ip, user_agent
            )
            if log_status != Status.OK:
                print(f"梦境记录日志记录失败: {title}")

            response = Status.OK.ToResponse("梦境记录成功")
            return jsonify(response)
        else:
            # 记录失败日志
            log_status = LogDreamRecordFailed(
                connection, user_id, title, dream_date, str(dream_status),
                client_ip, user_agent
            )
            if log_status != Status.OK:
                print(f"梦境记录失败日志记录失败: {title}")

            return jsonify(dream_status.ToResponse())

    except Exception as e:
        print(f"创建梦境异常: {str(e)}")
        return jsonify(Status.ErrorRequest.ToResponse(str(e)))

@dream_bp.route('/GetList', methods=['GET','OPTIONS'])
@jwt_required()
def get_dream_list():
    """获取用户梦境列表"""
    try:
        # 获取数据库连接
        connection = getattr(request, 'connection', None)
        if isinstance(connection, Status):
            return jsonify(connection.ToResponse())

        # 获取当前用户信息
        current_email = get_jwt_identity()
        if not current_email:
            return jsonify(Status.AuthFailed.ToResponse("未找到用户信息"))

        # 查询用户ID
        with connection.cursor() as cursor:
            cursor.execute("SELECT UserID FROM Users WHERE Email = %s", (current_email,))
            user_result = cursor.fetchone()
            if not user_result:
                return jsonify(Status.UserUnexist.ToResponse())

            user_id = user_result['UserID']

        # 获取查询参数
        page = int(request.args.get('page', 1))
        page_size = min(int(request.args.get('pageSize', 20)), 100)  # 限制最大页面大小
        date_from = request.args.get('dateFrom')
        date_to = request.args.get('dateTo')
        keyword = request.args.get('keyword', '').strip()

        # 参数验证
        if page < 1:
            page = 1
        if page_size < 1:
            page_size = 20

        # 获取梦境列表
        result, status = DreamGetList(
            connection=connection,
            user_id=user_id,
            page=page,
            page_size=page_size,
            date_from=date_from,
            date_to=date_to,
            keyword=keyword if keyword else None
        )

        if status == Status.OK:
            return jsonify({
                "Code": 200,
                "Msg": "获取梦境列表成功",
                "Data": result
            })
        else:
            return jsonify(status.ToResponse())

    except ValueError as e:
        return jsonify(Status.ErrorRequest.ToResponse(f"参数错误: {str(e)}"))
    except Exception as e:
        print(f"获取梦境列表异常: {str(e)}")
        return jsonify(Status.ErrorRequest.ToResponse(str(e)))

@dream_bp.route('/GetDetail/<int:dream_id>', methods=['GET','OPTIONS'])
@jwt_required()
def get_dream_detail(dream_id):
    """获取梦境详情"""
    try:
        # 获取数据库连接
        connection = getattr(request, 'connection', None)
        if isinstance(connection, Status):
            return jsonify(connection.ToResponse())

        # 获取当前用户信息
        current_email = get_jwt_identity()
        if not current_email:
            return jsonify(Status.AuthFailed.ToResponse("未找到用户信息"))

        # 查询用户ID
        with connection.cursor() as cursor:
            cursor.execute("SELECT UserID FROM Users WHERE Email = %s", (current_email,))
            user_result = cursor.fetchone()
            if not user_result:
                return jsonify(Status.UserUnexist.ToResponse())

            user_id = user_result['UserID']

        # 获取梦境详情
        dream_detail, status = DreamGetDetail(connection, dream_id, user_id)

        if status == Status.OK:
            return jsonify({
                "Code": 200,
                "Msg": "获取梦境详情成功",
                "Data": dream_detail
            })
        else:
            return jsonify(status.ToResponse())

    except Exception as e:
        print(f"获取梦境详情异常: {str(e)}")
        return jsonify(Status.ErrorRequest.ToResponse(str(e)))

@dream_bp.route('/GetEmotions', methods=['GET','OPTIONS'])
@jwt_required()
def get_emotions():
    """获取所有情绪"""
    try:
        # 获取数据库连接
        connection = getattr(request, 'connection', None)
        if isinstance(connection, Status):
            return jsonify(connection.ToResponse())

        # 获取所有情绪
        emotions, status = GetAllEmotions(connection)

        if status == Status.OK:
            return jsonify({
                "Code": 200,
                "Msg": "获取情绪列表成功",
                "Data": emotions
            })
        else:
            return jsonify(status.ToResponse())

    except Exception as e:
        print(f"获取情绪列表异常: {str(e)}")
        return jsonify(Status.ErrorRequest.ToResponse(str(e)))

@dream_bp.route('/GetDreamTypes', methods=['GET','OPTIONS'])
@jwt_required()
def get_dream_types():
    """获取所有梦境类型"""
    try:
        # 获取数据库连接
        connection = getattr(request, 'connection', None)
        if isinstance(connection, Status):
            return jsonify(connection.ToResponse())

        # 获取所有梦境类型
        dream_types, status = GetAllDreamTypes(connection)

        if status == Status.OK:
            return jsonify({
                "Code": 200,
                "Msg": "获取梦境类型列表成功",
                "Data": dream_types
            })
        else:
            return jsonify(status.ToResponse())

    except Exception as e:
        print(f"获取梦境类型列表异常: {str(e)}")
        return jsonify(Status.ErrorRequest.ToResponse(str(e)))