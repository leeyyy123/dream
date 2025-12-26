from flask import Blueprint, request, jsonify
from flask_jwt_extended import jwt_required, get_jwt_identity, create_access_token
import hashlib

from utils.status import Status
from sql.database import get_db
from sql.LogSql import GetClientIP, GetUserAgent
from sql.UserSql import UserCheckLogin

# 超级管理员配置
AdminEmail = "admin@dream.com"
AdminPasswordHash = "8d969eef6ecad3c29a3a629280e686cf0c3f5d5a86aff3ca12020c923adc6c92"  # "123456"

# Create blueprint
admin_bp = Blueprint('admin', __name__, url_prefix='/Admin')

@admin_bp.before_app_request
def handle_options():
    """处理跨域预检请求"""
    if request.method == 'OPTIONS':
        response = jsonify({'status': 'preflight'})
        response.headers.add('Access-Control-Allow-Headers', 'Content-Type,Authorization')
        response.headers.add('Access-Control-Allow-Methods', 'GET,PUT,POST,DELETE,OPTIONS')
        response.headers.add('Access-Control-Allow-Origin', '*')
        return response

@admin_bp.before_request
def before_request():
    """请求前处理，建立数据库连接"""
    try:
        connection = get_db()
        request.connection = connection
    except Exception as e:
        print(f"Database connection creation failed: {str(e)}")
        request.connection = None

@admin_bp.route('/Login', methods=['POST','OPTIONS'])
def admin_login():
    """管理员登录"""
    try:
        data = request.get_json()
        if not data or 'Email' not in data or 'Password' not in data:
            return jsonify(Status.ErrorRequest.ToResponse("参数不完整"))

        email = data['Email']
        password = data['Password']

        # 验证管理员账号
        if email != AdminEmail:
            return jsonify(Status.AuthFailed.ToResponse("管理员账号不存在"))

        # 验证密码
        password_hash = hashlib.sha256(password.encode()).hexdigest()
        if password_hash != AdminPasswordHash:
            return jsonify(Status.AuthFailed.ToResponse("密码错误"))

        # 创建token
        access_token = create_access_token(identity=email, additional_claims={'is_admin': True})

        response = Status.OK.ToResponse("管理员登录成功")
        response['Token'] = access_token
        response['Email'] = email
        return jsonify(response)

    except Exception as e:
        print(f"管理员登录异常: {str(e)}")
        return jsonify(Status.ErrorRequest.ToResponse(str(e)))

@admin_bp.route('/GetLogs', methods=['GET','OPTIONS'])
@jwt_required()
def get_logs():
    """获取日志列表"""
    try:
        connection = getattr(request, 'connection', None)
        if isinstance(connection, Status):
            return jsonify(connection.ToResponse())

        # 验证管理员权限
        current_email = get_jwt_identity()
        if current_email != AdminEmail:
            return jsonify(Status.PermissionDenied.ToResponse("权限不足"))

        # 获取查询参数
        log_type = request.args.get('logType')
        start_date = request.args.get('startDate')
        end_date = request.args.get('endDate')
        page = int(request.args.get('page', 1))
        page_size = min(int(request.args.get('pageSize', 20)), 100)

        # 构建查询条件
        conditions = []
        params = []

        if log_type:
            conditions.append("LogType = %s")
            params.append(log_type)

        if start_date:
            conditions.append("Timestamp >= %s")
            params.append(start_date)

        if end_date:
            conditions.append("Timestamp <= %s")
            params.append(end_date)

        where_clause = " WHERE " + " AND ".join(conditions) if conditions else ""

        # 计算总数
        count_sql = f"SELECT COUNT(*) as total FROM Logs{where_clause}"
        with connection.cursor() as count_cursor:
            count_cursor.execute(count_sql, params)
            total = count_cursor.fetchone()['total']

        # 分页查询
        offset = (page - 1) * page_size
        sql = f"""
            SELECT l.LogID, l.UserID, u.UserName, l.LogType, l.ActionDescription,
                   l.IP, l.Timestamp
            FROM Logs l
            LEFT JOIN Users u ON l.UserID = u.UserID
            {where_clause}
            ORDER BY l.Timestamp DESC
            LIMIT %s OFFSET %s
        """
        params.extend([page_size, offset])
        with connection.cursor() as cursor:
            cursor.execute(sql, params)
            logs = cursor.fetchall()

        # 格式化时间
        for log in logs:
            if log['Timestamp']:
                log['Timestamp'] = log['Timestamp'].isoformat()

        result = {
            'logs': logs,
            'pagination': {
                'currentPage': page,
                'pageSize': page_size,
                'totalItems': total,
                'totalPages': (total + page_size - 1) // page_size
            }
        }

        return jsonify({
            "Code": 200,
            "Msg": "获取日志成功",
            "Data": result
        })

    except Exception as e:
        print(f"获取日志异常: {str(e)}")
        return jsonify(Status.ErrorRequest.ToResponse(str(e)))

@admin_bp.route('/DeleteLogs', methods=['DELETE','OPTIONS'])
@jwt_required()
def delete_logs():
    """批量删除日志"""
    try:
        connection = getattr(request, 'connection', None)
        if isinstance(connection, Status):
            return jsonify(connection.ToResponse())

        # 验证管理员权限
        current_email = get_jwt_identity()
        if current_email != AdminEmail:
            return jsonify(Status.PermissionDenied.ToResponse("权限不足"))

        data = request.get_json()
        if not data or 'logIds' not in data:
            return jsonify(Status.ErrorRequest.ToResponse("参数不完整"))

        log_ids = data['logIds']

        if not log_ids:
            return jsonify(Status.ErrorRequest.ToResponse("日志ID列表不能为空"))

        # 删除日志
        placeholders = ','.join(['%s'] * len(log_ids))
        sql = f"DELETE FROM Logs WHERE LogID IN ({placeholders})"
        with connection.cursor() as cursor:
            cursor.execute(sql, log_ids)
            affected_rows = cursor.rowcount
            connection.commit()

        return jsonify({
            "Code": 200,
            "Msg": f"成功删除{affected_rows}条日志",
            "Data": {'deletedCount': affected_rows}
        })

    except Exception as e:
        print(f"删除日志异常: {str(e)}")
        connection.rollback()
        return jsonify(Status.ErrorRequest.ToResponse(str(e)))

@admin_bp.route('/GetEmotions', methods=['GET','OPTIONS'])
@jwt_required()
def get_emotions():
    """获取所有情绪"""
    try:
        connection = getattr(request, 'connection', None)
        if isinstance(connection, Status):
            return jsonify(connection.ToResponse())

        # 验证管理员权限
        current_email = get_jwt_identity()
        if current_email != AdminEmail:
            return jsonify(Status.PermissionDenied.ToResponse("权限不足"))

        with connection.cursor() as cursor:
            sql = "SELECT EmotionID, EmotionName, Color FROM Emotions ORDER BY EmotionID"
            cursor.execute(sql)
            emotions = cursor.fetchall()

        return jsonify({
            "Code": 200,
            "Msg": "获取情绪成功",
            "Data": emotions
        })

    except Exception as e:
        print(f"获取情绪异常: {str(e)}")
        return jsonify(Status.ErrorRequest.ToResponse(str(e)))

@admin_bp.route('/AddEmotion', methods=['POST','OPTIONS'])
@jwt_required()
def add_emotion():
    """添加新情绪"""
    try:
        connection = getattr(request, 'connection', None)
        if isinstance(connection, Status):
            return jsonify(connection.ToResponse())

        # 验证管理员权限
        current_email = get_jwt_identity()
        if current_email != AdminEmail:
            return jsonify(Status.PermissionDenied.ToResponse("权限不足"))

        data = request.get_json()
        if not data or 'EmotionName' not in data or 'Color' not in data:
            return jsonify(Status.ErrorRequest.ToResponse("参数不完整"))

        emotion_name = data['EmotionName'].strip()
        color = data['Color'].strip()

        if not emotion_name or not color:
            return jsonify(Status.ErrorRequest.ToResponse("情绪名称和颜色不能为空"))

        # 验证颜色格式
        if not color.startswith('#') or len(color) != 7:
            return jsonify(Status.ErrorRequest.ToResponse("颜色格式不正确，请使用#RRGGBB格式"))

        with connection.cursor() as cursor:
            sql = "INSERT INTO Emotions (EmotionName, Color) VALUES (%s, %s)"
            cursor.execute(sql, (emotion_name, color))
            connection.commit()

        return jsonify({
            "Code": 200,
            "Msg": "添加情绪成功",
            "Data": {"EmotionName": emotion_name, "Color": color}
        })

    except Exception as e:
        print(f"添加情绪异常: {str(e)}")
        connection.rollback()
        return jsonify(Status.ErrorRequest.ToResponse(str(e)))

@admin_bp.route('/DeleteEmotion/<int:emotion_id>', methods=['DELETE','OPTIONS'])
@jwt_required()
def delete_emotion(emotion_id):
    """删除情绪"""
    try:
        connection = getattr(request, 'connection', None)
        if isinstance(connection, Status):
            return jsonify(connection.ToResponse())

        # 验证管理员权限
        current_email = get_jwt_identity()
        if current_email != AdminEmail:
            return jsonify(Status.PermissionDenied.ToResponse("权限不足"))

        with connection.cursor() as cursor:
            # 检查是否有梦境使用了该情绪
            check_sql = "SELECT COUNT(*) as count FROM DreamEmotions WHERE EmotionID = %s"
            cursor.execute(check_sql, (emotion_id,))
            count = cursor.fetchone()['count']

            if count > 0:
                return jsonify(Status.ErrorRequest.ToResponse(f"该情绪已被{count}个梦境使用，无法删除"))

            sql = "DELETE FROM Emotions WHERE EmotionID = %s"
            cursor.execute(sql, (emotion_id,))
            connection.commit()

        return jsonify({
            "Code": 200,
            "Msg": "删除情绪成功",
            "Data": {"EmotionID": emotion_id}
        })

    except Exception as e:
        print(f"删除情绪异常: {str(e)}")
        connection.rollback()
        return jsonify(Status.ErrorRequest.ToResponse(str(e)))

@admin_bp.route('/GetDreamTypes', methods=['GET','OPTIONS'])
@jwt_required()
def get_dream_types():
    """获取所有梦境类型"""
    try:
        connection = getattr(request, 'connection', None)
        if isinstance(connection, Status):
            return jsonify(connection.ToResponse())

        # 验证管理员权限
        current_email = get_jwt_identity()
        if current_email != AdminEmail:
            return jsonify(Status.PermissionDenied.ToResponse("权限不足"))

        with connection.cursor() as cursor:
            sql = "SELECT TypeID, TypeName, Color FROM DreamTypes ORDER BY TypeID"
            cursor.execute(sql)
            dream_types = cursor.fetchall()

        return jsonify({
            "Code": 200,
            "Msg": "获取梦境类型成功",
            "Data": dream_types
        })

    except Exception as e:
        print(f"获取梦境类型异常: {str(e)}")
        return jsonify(Status.ErrorRequest.ToResponse(str(e)))

@admin_bp.route('/AddDreamType', methods=['POST','OPTIONS'])
@jwt_required()
def add_dream_type():
    """添加新梦境类型"""
    try:
        connection = getattr(request, 'connection', None)
        if isinstance(connection, Status):
            return jsonify(connection.ToResponse())

        # 验证管理员权限
        current_email = get_jwt_identity()
        if current_email != AdminEmail:
            return jsonify(Status.PermissionDenied.ToResponse("权限不足"))

        data = request.get_json()
        if not data or 'TypeName' not in data or 'Color' not in data:
            return jsonify(Status.ErrorRequest.ToResponse("参数不完整"))

        type_name = data['TypeName'].strip()
        color = data['Color'].strip()

        if not type_name or not color:
            return jsonify(Status.ErrorRequest.ToResponse("类型名称和颜色不能为空"))

        # 验证颜色格式
        if not color.startswith('#') or len(color) != 7:
            return jsonify(Status.ErrorRequest.ToResponse("颜色格式不正确，请使用#RRGGBB格式"))

        with connection.cursor() as cursor:
            sql = "INSERT INTO DreamTypes (TypeName, Color) VALUES (%s, %s)"
            cursor.execute(sql, (type_name, color))
            connection.commit()

        return jsonify({
            "Code": 200,
            "Msg": "添加类型成功",
            "Data": {"TypeName": type_name, "Color": color}
        })

    except Exception as e:
        print(f"添加梦境类型异常: {str(e)}")
        connection.rollback()
        return jsonify(Status.ErrorRequest.ToResponse(str(e)))

@admin_bp.route('/DeleteDreamType/<int:type_id>', methods=['DELETE','OPTIONS'])
@jwt_required()
def delete_dream_type(type_id):
    """删除梦境类型"""
    try:
        connection = getattr(request, 'connection', None)
        if isinstance(connection, Status):
            return jsonify(connection.ToResponse())

        # 验证管理员权限
        current_email = get_jwt_identity()
        if current_email != AdminEmail:
            return jsonify(Status.PermissionDenied.ToResponse("权限不足"))

        with connection.cursor() as cursor:
            # 检查是否有梦境使用了该类型
            check_sql = "SELECT COUNT(*) as count FROM DreamTypesRelation WHERE TypeID = %s"
            cursor.execute(check_sql, (type_id,))
            count = cursor.fetchone()['count']

            if count > 0:
                return jsonify(Status.ErrorRequest.ToResponse(f"该类型已被{count}个梦境使用，无法删除"))

            sql = "DELETE FROM DreamTypes WHERE TypeID = %s"
            cursor.execute(sql, (type_id,))
            connection.commit()

        return jsonify({
            "Code": 200,
            "Msg": "删除类型成功",
            "Data": {"TypeID": type_id}
        })

    except Exception as e:
        print(f"删除梦境类型异常: {str(e)}")
        connection.rollback()
        return jsonify(Status.ErrorRequest.ToResponse(str(e)))

@admin_bp.route('/GetPublicDreams', methods=['GET','OPTIONS'])
@jwt_required()
def get_public_dreams():
    """获取所有公开的梦境"""
    try:
        connection = getattr(request, 'connection', None)
        if isinstance(connection, Status):
            return jsonify(connection.ToResponse())

        # 验证管理员权限
        current_email = get_jwt_identity()
        if current_email != AdminEmail:
            return jsonify(Status.PermissionDenied.ToResponse("权限不足"))

        # 获取查询参数
        page = int(request.args.get('page', 1))
        page_size = min(int(request.args.get('pageSize', 20)), 100)

        # 计算总数
        count_sql = "SELECT COUNT(*) as total FROM Dreams WHERE IsPublic = TRUE"
        with connection.cursor() as count_cursor:
            count_cursor.execute(count_sql)
            total = count_cursor.fetchone()['total']

        # 分页查询
        offset = (page - 1) * page_size
        sql = """
            SELECT d.DreamID, d.UserID, d.Title, d.Content, d.DreamDate,
                   d.SleepQuality, d.LucidityLevel, d.RecordTime, d.IsPublic,
                   u.UserName
            FROM Dreams d
            JOIN Users u ON d.UserID = u.UserID
            WHERE d.IsPublic = TRUE
            ORDER BY d.DreamDate DESC, d.RecordTime DESC
            LIMIT %s OFFSET %s
        """
        with connection.cursor() as cursor:
            cursor.execute(sql, (page_size, offset))
            dreams = cursor.fetchall()

        # 格式化日期时间并获取关联数据
        for dream in dreams:
            if dream['DreamDate']:
                dream['DreamDate'] = dream['DreamDate'].isoformat()
            if dream['RecordTime']:
                dream['RecordTime'] = dream['RecordTime'].isoformat()

            # 获取情绪
            with connection.cursor() as emotion_cursor:
                emotion_cursor.execute("""
                    SELECT e.EmotionID, e.EmotionName, e.Color
                    FROM DreamEmotions de
                    JOIN Emotions e ON de.EmotionID = e.EmotionID
                    WHERE de.DreamID = %s
                """, (dream['DreamID'],))
                dream['Emotions'] = emotion_cursor.fetchall()

            # 获取类型
            with connection.cursor() as type_cursor:
                type_cursor.execute("""
                    SELECT dt.TypeID, dt.TypeName, dt.Color
                    FROM DreamTypesRelation dtr
                    JOIN DreamTypes dt ON dtr.TypeID = dt.TypeID
                    WHERE dtr.DreamID = %s
                """, (dream['DreamID'],))
                dream['DreamTypes'] = type_cursor.fetchall()

        result = {
            'dreams': dreams,
            'pagination': {
                'currentPage': page,
                'pageSize': page_size,
                'totalItems': total,
                'totalPages': (total + page_size - 1) // page_size
            }
        }

        return jsonify({
            "Code": 200,
            "Msg": "获取公开梦境成功",
            "Data": result
        })

    except Exception as e:
        print(f"获取公开梦境异常: {str(e)}")
        return jsonify(Status.ErrorRequest.ToResponse(str(e)))
