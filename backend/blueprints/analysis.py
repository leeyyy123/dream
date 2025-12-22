from flask import Blueprint, request, jsonify, g
from flask_jwt_extended import jwt_required, get_jwt_identity
from utils.status import Status
from sql.database import get_db
from sql.AnalysisSql import (
    AnalysisCreate, AnalysisGetList, AnalysisGetDetail, AnalysisDelete,
    GetAnalysisDreamStats
)
from sql.LogSql import LogAnalysisSuccess, LogAnalysisFailed, GetClientIP, GetUserAgent

# Create blueprint
analysis_bp = Blueprint('analysis', __name__, url_prefix='/Analysis')

@analysis_bp.before_app_request
def handle_options():
    """处理跨域预检请求"""
    if request.method == 'OPTIONS':
        response = jsonify({'status': 'preflight'})
        response.headers.add('Access-Control-Allow-Headers', 'Content-Type,Authorization')
        response.headers.add('Access-Control-Allow-Methods', 'GET,PUT,POST,DELETE,OPTIONS')
        response.headers.add('Access-Control-Allow-Origin', '*')
        return response

@analysis_bp.before_request
def before_request():
    """请求前处理，建立数据库连接"""
    try:
        connection = get_db()
        request.connection = connection
    except Exception as e:
        print(f"Database connection creation failed: {str(e)}")
        request.connection = None

@analysis_bp.route('/Create', methods=['POST','OPTIONS'])
@jwt_required()
def create_analysis():
    """创建分析记录"""
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
        required_fields = ['StartDate', 'EndDate']
        for field in required_fields:
            if field not in data or not data[field]:
                error_msg = f"缺少必填字段: {field}"
                return jsonify(Status.ErrorRequest.ToResponse(error_msg))

        start_date = data['StartDate']
        end_date = data['EndDate']
        result = data.get('Result', {})
        recommendation = data.get('Recommendation', '')

        # 验证日期格式
        try:
            from datetime import datetime
            start_date_obj = datetime.strptime(start_date, '%Y-%m-%d').date()
            end_date_obj = datetime.strptime(end_date, '%Y-%m-%d').date()
        except ValueError:
            return jsonify(Status.ErrorRequest.ToResponse("日期格式不正确，请使用YYYY-MM-DD格式"))

        # 验证日期范围
        if start_date_obj > end_date_obj:
            return jsonify(Status.ErrorRequest.ToResponse("起始日期不能晚于结束日期"))

        # 验证日期范围不能超过一年
        from datetime import timedelta
        if (end_date_obj - start_date_obj) > timedelta(days=365):
            return jsonify(Status.ErrorRequest.ToResponse("分析时间段不能超过一年"))

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

        # 创建分析记录
        analysis_status = AnalysisCreate(
            connection,
            user_id=user_id,
            start_date=start_date_obj,
            end_date=end_date_obj,
            result=result,
            recommendation=recommendation
        )

        # 记录日志
        if analysis_status == Status.OK:
            log_status = LogAnalysisSuccess(
                connection, user_id, start_date, end_date, client_ip, user_agent
            )
            if log_status != Status.OK:
                print(f"分析记录日志记录失败: {start_date}~{end_date}")

            response = Status.OK.ToResponse("分析记录创建成功")
            return jsonify(response)
        else:
            # 记录失败日志
            log_status = LogAnalysisFailed(
                connection, user_id, start_date, end_date, str(analysis_status),
                client_ip, user_agent
            )
            if log_status != Status.OK:
                print(f"分析记录失败日志记录失败: {start_date}~{end_date}")

            return jsonify(analysis_status.ToResponse())

    except Exception as e:
        print(f"创建分析记录异常: {str(e)}")
        return jsonify(Status.ErrorRequest.ToResponse(str(e)))

@analysis_bp.route('/GetList', methods=['GET','OPTIONS'])
@jwt_required()
def get_analysis_list():
    """获取用户分析记录列表"""
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

        # 参数验证
        if page < 1:
            page = 1
        if page_size < 1:
            page_size = 20

        # 获取分析记录列表
        result, status = AnalysisGetList(
            connection=connection,
            user_id=user_id,
            page=page,
            page_size=page_size
        )

        if status == Status.OK:
            return jsonify({
                "Code": 200,
                "Msg": "获取分析记录列表成功",
                "Data": result
            })
        else:
            return jsonify(status.ToResponse())

    except ValueError as e:
        return jsonify(Status.ErrorRequest.ToResponse(f"参数错误: {str(e)}"))
    except Exception as e:
        print(f"获取分析记录列表异常: {str(e)}")
        return jsonify(Status.ErrorRequest.ToResponse(str(e)))

@analysis_bp.route('/GetDetail/<int:analysis_id>', methods=['GET','OPTIONS'])
@jwt_required()
def get_analysis_detail(analysis_id):
    """获取分析记录详情"""
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

        # 获取分析记录详情
        analysis_detail, status = AnalysisGetDetail(connection, analysis_id, user_id)

        if status == Status.OK:
            return jsonify({
                "Code": 200,
                "Msg": "获取分析记录详情成功",
                "Data": analysis_detail
            })
        else:
            return jsonify(status.ToResponse())

    except Exception as e:
        print(f"获取分析记录详情异常: {str(e)}")
        return jsonify(Status.ErrorRequest.ToResponse(str(e)))

@analysis_bp.route('/Delete/<int:analysis_id>', methods=['DELETE','OPTIONS'])
@jwt_required()
def delete_analysis(analysis_id):
    """删除分析记录"""
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

        # 删除分析记录
        status = AnalysisDelete(connection, analysis_id, user_id)

        if status == Status.OK:
            return jsonify(Status.OK.ToResponse("分析记录删除成功"))
        else:
            return jsonify(status.ToResponse())

    except Exception as e:
        print(f"删除分析记录异常: {str(e)}")
        return jsonify(Status.ErrorRequest.ToResponse(str(e)))

@analysis_bp.route('/GetDreamStats', methods=['GET','OPTIONS'])
@jwt_required()
def get_dream_stats():
    """获取指定时间段的梦境统计数据"""
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
        start_date = request.args.get('startDate')
        end_date = request.args.get('endDate')

        if not start_date or not end_date:
            return jsonify(Status.ErrorRequest.ToResponse("请提供起始和结束日期"))

        # 验证日期格式
        try:
            from datetime import datetime
            start_date_obj = datetime.strptime(start_date, '%Y-%m-%d').date()
            end_date_obj = datetime.strptime(end_date, '%Y-%m-%d').date()
        except ValueError:
            return jsonify(Status.ErrorRequest.ToResponse("日期格式不正确，请使用YYYY-MM-DD格式"))

        # 获取统计数据
        stats_data, status = GetAnalysisDreamStats(
            connection=connection,
            user_id=user_id,
            start_date=start_date_obj,
            end_date=end_date_obj
        )

        if status == Status.OK:
            return jsonify({
                "Code": 200,
                "Msg": "获取梦境统计数据成功",
                "Data": stats_data
            })
        else:
            return jsonify(status.ToResponse())

    except Exception as e:
        print(f"获取梦境统计数据异常: {str(e)}")
        return jsonify(Status.ErrorRequest.ToResponse(str(e)))