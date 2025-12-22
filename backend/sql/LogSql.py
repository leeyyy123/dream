import pymysql
import json
from datetime import datetime
from utils.status import Status
import sys

printdebug = True

def LogUserAction(connection, user_id: int, log_type: str, action_description: str,
                 ip_address: str, user_agent: str = None, additional_data: dict = None):
    """记录用户操作日志"""
    try:
        # 验证日志类型是否合法
        valid_log_types = ['login', 'logout', 'record', 'update', 'delete', 'analysis', 'error']
        if log_type not in valid_log_types:
            if printdebug:
                print(f"Invalid log type: {log_type}")
            return Status.ErrorRequest

        # 将额外的数据转换为JSON字符串
        additional_json = None
        if additional_data:
            try:
                additional_json = json.dumps(additional_data, ensure_ascii=False)
            except (TypeError, ValueError) as e:
                if printdebug:
                    print(f"JSON serialization failed: {e}")
                additional_json = None

        with connection.cursor() as cursor:
            sql = """
                INSERT INTO Logs (UserID, LogType, ActionDescription, IP, UserAgent, AdditionalData, Timestamp)
                VALUES (%s, %s, %s, %s, %s, %s, %s)
            """
            params = (
                user_id if user_id and user_id > 0 else None,  # 超级管理员ID为-1，设为NULL
                log_type,
                action_description,
                ip_address,
                user_agent,
                additional_json,
                datetime.now()
            )

            cursor.execute(sql, params)
            connection.commit()

            if printdebug:
                print(f"Log recorded successfully: UserID={user_id}, Type={log_type}, Action={action_description}")

            return Status.OK

    except pymysql.Error as e:
        if printdebug:
            print(f"Log database error: {e}")
        connection.rollback()
        return Status.DatabaseInsertError
    except Exception as e:
        if printdebug:
            print(f"Log recording exception: {e}")
        return Status.DatabaseInsertError

def LogLoginSuccess(connection, user_id: int, email: str, ip_address: str, user_agent: str = None):
    """记录登录成功日志"""
    action_description = f"用户登录成功: {email}"
    additional_data = {
        "email": email,
        "login_status": "success"
    }
    return LogUserAction(connection, user_id, 'login', action_description, ip_address, user_agent, additional_data)

def LogLoginFailed(connection, email: str, ip_address: str, user_agent: str = None, error_reason: str = None):
    """记录登录失败日志"""
    action_description = f"用户登录失败: {email}"
    additional_data = {
        "email": email,
        "login_status": "failed",
        "error_reason": error_reason
    }
    return LogUserAction(connection, None, 'login', action_description, ip_address, user_agent, additional_data)

def LogRegistrationSuccess(connection, user_id: int, email: str, username: str, ip_address: str, user_agent: str = None):
    """记录注册成功日志"""
    action_description = f"用户注册成功: {username} ({email})"
    additional_data = {
        "email": email,
        "username": username,
        "registration_status": "success"
    }
    return LogUserAction(connection, user_id, 'record', action_description, ip_address, user_agent, additional_data)

def LogRegistrationFailed(connection, email: str, username: str, ip_address: str, user_agent: str = None, error_reason: str = None):
    """记录注册失败日志"""
    action_description = f"用户注册失败: {username} ({email})"
    additional_data = {
        "email": email,
        "username": username,
        "registration_status": "failed",
        "error_reason": error_reason
    }
    return LogUserAction(connection, None, 'error', action_description, ip_address, user_agent, additional_data)


def GetClientIP(request):
    """从请求中获取客户端IP地址"""
    try:
        # 优先获取真实IP（经过代理的情况）
        if request.headers.get('X-Forwarded-For'):
            ip = request.headers.get('X-Forwarded-For').split(',')[0].strip()
        elif request.headers.get('X-Real-IP'):
            ip = request.headers.get('X-Real-IP')
        elif request.headers.get('CF-Connecting-IP'):  # Cloudflare
            ip = request.headers.get('CF-Connecting-IP')
        else:
            ip = request.remote_addr or '127.0.0.1'

        # 限制IP长度，防止注入攻击
        return ip[:45] if ip else '127.0.0.1'
    except Exception:
        return '127.0.0.1'

def GetUserAgent(request):
    """从请求中获取User-Agent"""
    try:
        user_agent = request.headers.get('User-Agent', '')
        # 限制User-Agent长度
        return user_agent[:500] if user_agent else None
    except Exception:
        return None

def LogDreamRecordSuccess(connection, user_id: int, title: str, dream_date: str,
                         sleep_quality: int, lucidity_level: int, is_public: bool,
                         ip_address: str, user_agent: str = None):
    """记录梦境创建成功日志"""
    action_description = f"用户记录梦境: {title}"
    additional_data = {
        "dream_title": title,
        "dream_date": dream_date,
        "sleep_quality": sleep_quality,
        "lucidity_level": lucidity_level,
        "is_public": is_public,
        "action": "dream_create"
    }
    return LogUserAction(connection, user_id, 'record', action_description, ip_address, user_agent, additional_data)

def LogDreamRecordFailed(connection, user_id: int, title: str, error_reason: str,
                          ip_address: str, user_agent: str = None):
    """记录梦境创建失败日志"""
    action_description = f"用户记录梦境失败: {title}"
    additional_data = {
        "dream_title": title,
        "error_reason": error_reason,
        "action": "dream_create_failed"
    }
    return LogUserAction(connection, user_id, 'error', action_description, ip_address, user_agent, additional_data)

def LogDreamUpdate(connection, user_id: int, dream_id: int, title: str, ip_address: str, user_agent: str = None):
    """记录梦境更新日志"""
    action_description = f"用户更新梦境: {title} (ID: {dream_id})"
    additional_data = {
        "dream_id": dream_id,
        "dream_title": title,
        "action": "dream_update"
    }
    return LogUserAction(connection, user_id, 'update', action_description, ip_address, user_agent, additional_data)

def LogDreamDelete(connection, user_id: int, dream_id: int, title: str, ip_address: str, user_agent: str = None):
    """记录梦境删除日志"""
    action_description = f"用户删除梦境: {title} (ID: {dream_id})"
    additional_data = {
        "dream_id": dream_id,
        "dream_title": title,
        "action": "dream_delete"
    }
    return LogUserAction(connection, user_id, 'delete', action_description, ip_address, user_agent, additional_data)

def LogAnalysisSuccess(connection, user_id: int, start_date: str, end_date: str,
                       ip_address: str, user_agent: str = None):
    """记录分析创建成功日志"""
    action_description = f"用户创建分析: {start_date} ~ {end_date}"
    additional_data = {
        "start_date": start_date,
        "end_date": end_date,
        "action": "analysis_create"
    }
    return LogUserAction(connection, user_id, 'analysis', action_description, ip_address, user_agent, additional_data)

def LogAnalysisFailed(connection, user_id: int, start_date: str, end_date: str, error_reason: str,
                        ip_address: str, user_agent: str = None):
    """记录分析创建失败日志"""
    action_description = f"用户创建分析失败: {start_date} ~ {end_date}"
    additional_data = {
        "start_date": start_date,
        "end_date": end_date,
        "error_reason": error_reason,
        "action": "analysis_create_failed"
    }
    return LogUserAction(connection, user_id, 'error', action_description, ip_address, user_agent, additional_data)