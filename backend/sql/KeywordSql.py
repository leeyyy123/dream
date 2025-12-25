"""
关键词相关数据库操作
"""
import pymysql
from utils.status import Status

printdebug = True


def AddDreamKeywords(connection, dream_id: int, keywords_data):
    """
    为梦境添加关键词
    :param connection: 数据库连接
    :param dream_id: 梦境ID
    :param keywords_data: 关键词数据列表
        [{"text": "关键词", "category": "person", "weight": 2}, ...]
    :return: Status
    """
    try:
        if not keywords_data:
            return Status.OK

        with connection.cursor() as cursor:
            sql = """
                INSERT INTO Keywords (DreamID, KeywordText, Category, Weight)
                VALUES (%s, %s, %s, %s)
            """

            values = []
            for keyword in keywords_data:
                text = keyword.get('text', '').strip()
                category = keyword.get('category', 'other')
                weight = keyword.get('weight', 2)

                # 验证category
                valid_categories = ['person', 'place', 'object', 'event', 'symbol', 'other']
                if category not in valid_categories:
                    category = 'other'

                # 验证weight
                if not isinstance(weight, int) or weight < 1 or weight > 3:
                    weight = 2

                if text:
                    values.append((dream_id, text, category, weight))

            if values:
                cursor.executemany(sql, values)
                connection.commit()

                if printdebug:
                    print(f"成功添加 {len(values)} 个关键词: 梦境ID={dream_id}")

            return Status.OK

    except pymysql.Error as e:
        if printdebug:
            print(f"添加关键词数据库错误: {e}")
        connection.rollback()
        return Status.DatabaseInsertError
    except Exception as e:
        if printdebug:
            print(f"添加关键词异常: {e}")
        connection.rollback()
        return Status.DatabaseInsertError


def GetDreamKeywords(connection, dream_id: int):
    """
    获取梦境的关键词
    :param connection: 数据库连接
    :param dream_id: 梦境ID
    :return: (关键词列表, Status)
    """
    try:
        with connection.cursor() as cursor:
            sql = """
                SELECT KeywordID, KeywordText, Category, Weight
                FROM Keywords
                WHERE DreamID = %s
                ORDER BY Weight DESC, KeywordText
            """
            cursor.execute(sql, (dream_id,))
            keywords = cursor.fetchall()

            if printdebug:
                print(f"获取梦境关键词成功: 梦境ID={dream_id}, 关键词数={len(keywords)}")

            return keywords, Status.OK

    except pymysql.Error as e:
        if printdebug:
            print(f"获取关键词数据库错误: {e}")
        return None, Status.DatabaseSelectError
    except Exception as e:
        if printdebug:
            print(f"获取关键词异常: {e}")
        return None, Status.DatabaseSelectError


def DeleteDreamKeywords(connection, dream_id: int):
    """
    删除梦境的所有关键词
    :param connection: 数据库连接
    :param dream_id: 梦境ID
    :return: Status
    """
    try:
        with connection.cursor() as cursor:
            sql = "DELETE FROM Keywords WHERE DreamID = %s"
            cursor.execute(sql, (dream_id,))
            connection.commit()

            if printdebug:
                print(f"删除梦境关键词成功: 梦境ID={dream_id}")

            return Status.OK

    except pymysql.Error as e:
        if printdebug:
            print(f"删除关键词数据库错误: {e}")
        connection.rollback()
        return Status.DatabaseDeleteError
    except Exception as e:
        if printdebug:
            print(f"删除关键词异常: {e}")
        connection.rollback()
        return Status.DatabaseDeleteError
