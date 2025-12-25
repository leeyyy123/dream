"""
AI对话历史数据库操作
"""

import pymysql
import json
from datetime import datetime
from utils.status import Status

printdebug = True


def SaveAIChatHistory(connection, user_id: int, source_type: str, source_id: int, messages: list):
    """保存AI对话历史"""
    try:
        with connection.cursor() as cursor:
            # 将消息列表转换为JSON
            messages_json = json.dumps(messages, ensure_ascii=False)

            # 检查是否已存在该来源的对话历史
            check_sql = """
                SELECT ChatID FROM AIChats
                WHERE UserID = %s AND SourceType = %s AND SourceID = %s
                LIMIT 1
            """
            cursor.execute(check_sql, (user_id, source_type, source_id))
            existing_chat = cursor.fetchone()

            if existing_chat:
                # 更新现有对话
                update_sql = """
                    UPDATE AIChats
                    SET Messages = %s, UpdatedAt = %s
                    WHERE ChatID = %s
                """
                cursor.execute(update_sql, (messages_json, datetime.now(), existing_chat['ChatID']))

                if printdebug:
                    print(f"AI对话历史更新成功: 用户ID={user_id}, 来源={source_type}/{source_id}")
            else:
                # 插入新对话
                insert_sql = """
                    INSERT INTO AIChats (UserID, SourceType, SourceID, Messages, CreatedAt, UpdatedAt)
                    VALUES (%s, %s, %s, %s, %s, %s)
                """
                cursor.execute(insert_sql, (
                    user_id, source_type, source_id, messages_json,
                    datetime.now(), datetime.now()
                ))

                if printdebug:
                    print(f"AI对话历史保存成功: 用户ID={user_id}, 来源={source_type}/{source_id}")

            connection.commit()
            return Status.OK

    except pymysql.Error as e:
        if printdebug:
            print(f"保存AI对话历史数据库错误: {e}")
        connection.rollback()
        return Status.DatabaseInsertError
    except Exception as e:
        if printdebug:
            print(f"保存AI对话历史异常: {e}")
        return Status.DatabaseInsertError


def GetAIChatHistory(connection, user_id: int, source_type: str, source_id: int):
    """获取AI对话历史"""
    try:
        with connection.cursor() as cursor:
            sql = """
                SELECT ChatID, Messages, CreatedAt, UpdatedAt
                FROM AIChats
                WHERE UserID = %s AND SourceType = %s AND SourceID = %s
                ORDER BY UpdatedAt DESC
                LIMIT 1
            """
            cursor.execute(sql, (user_id, source_type, source_id))
            chat = cursor.fetchone()

            if not chat:
                return None, Status.ResultEmpty

            # 解析消息JSON
            try:
                messages = json.loads(chat['Messages']) if chat['Messages'] else []
            except json.JSONDecodeError:
                messages = []

            result = {
                'ChatID': chat['ChatID'],
                'Messages': messages,
                'CreatedAt': chat['CreatedAt'].isoformat() if chat['CreatedAt'] else None,
                'UpdatedAt': chat['UpdatedAt'].isoformat() if chat['UpdatedAt'] else None
            }

            if printdebug:
                print(f"AI对话历史获取成功: 用户ID={user_id}, 来源={source_type}/{source_id}, 消息数={len(messages)}")

            return result, Status.OK

    except pymysql.Error as e:
        if printdebug:
            print(f"获取AI对话历史数据库错误: {e}")
        return None, Status.DatabaseSelectError
    except Exception as e:
        if printdebug:
            print(f"获取AI对话历史异常: {e}")
        return None, Status.DatabaseSelectError


def DeleteAIChatHistory(connection, user_id: int, source_type: str, source_id: int):
    """删除AI对话历史"""
    try:
        with connection.cursor() as cursor:
            sql = """
                DELETE FROM AIChats
                WHERE UserID = %s AND SourceType = %s AND SourceID = %s
            """
            cursor.execute(sql, (user_id, source_type, source_id))
            connection.commit()

            if printdebug:
                print(f"AI对话历史删除成功: 用户ID={user_id}, 来源={source_type}/{source_id}")

            return Status.OK

    except pymysql.Error as e:
        if printdebug:
            print(f"删除AI对话历史数据库错误: {e}")
        connection.rollback()
        return Status.DatabaseDeleteError
    except Exception as e:
        if printdebug:
            print(f"删除AI对话历史异常: {e}")
        return Status.DatabaseDeleteError
