import pymysql
import json
from datetime import datetime
from utils.status import Status
from utils.Objects import Users
from .EmotionTypeSql import AddDreamEmotions, AddDreamTypes
from .KeywordSql import AddDreamKeywords, GetDreamKeywords

printdebug = True

def DreamCreate(connection, user_id: int, title: str, content: str, dream_date: datetime.date,
               sleep_quality: int, lucidity_level: int, is_public: bool, emotion_ids=None, dream_type_ids=None,
               keywords=None):
    """创建梦境记录"""
    try:
        with connection.cursor() as cursor:
            sql = """
                INSERT INTO Dreams (
                    UserID, Title, Content, DreamDate, SleepQuality,
                    LucidityLevel, IsPublic, RecordTime
                ) VALUES (%s, %s, %s, %s, %s, %s, %s, %s)
            """
            params = (
                user_id,
                title,
                content,
                dream_date,
                sleep_quality,
                lucidity_level,
                is_public,
                datetime.now()
            )

            cursor.execute(sql, params)
            dream_id = cursor.lastrowid
            connection.commit()

            if printdebug:
                print(f"梦境创建成功: ID={dream_id}, 用户ID={user_id}, 标题={title}")

            # 添加情绪关联（如果有）
            if emotion_ids:
                emotions_data = [{'emotion_id': emotion_id, 'intensity': 5, 'is_primary': False} for emotion_id in emotion_ids]
                if emotions_data:
                    emotion_status = AddDreamEmotions(connection, dream_id, emotions_data)
                    if emotion_status != Status.OK:
                        print(f"添加情绪关联失败: 梦境ID={dream_id}")
                        # 不影响整体创建，只记录错误
                    else:
                        print(f"成功添加 {len(emotions_data)} 种情绪关联: 梦境ID={dream_id}")

            # 添加梦境类型关联（如果有）
            if dream_type_ids:
                types_data = [{'type_id': type_id, 'confidence': 1.0} for type_id in dream_type_ids]
                if types_data:
                    type_status = AddDreamTypes(connection, dream_id, types_data)
                    if type_status != Status.OK:
                        print(f"添加梦境类型关联失败: 梦境ID={dream_id}")
                        # 不影响整体创建，只记录错误
                    else:
                        print(f"成功添加 {len(types_data)} 种类型关联: 梦境ID={dream_id}")

            # 添加关键词关联（如果有）
            if keywords:
                keyword_status = AddDreamKeywords(connection, dream_id, keywords)
                if keyword_status != Status.OK:
                    print(f"添加关键词关联失败: 梦境ID={dream_id}")
                    # 不影响整体创建，只记录错误
                else:
                    print(f"成功添加 {len(keywords)} 个关键词: 梦境ID={dream_id}")

            return Status.OK

    except pymysql.Error as e:
        if printdebug:
            print(f"梦境创建数据库错误: {e}")
        connection.rollback()
        return Status.DatabaseInsertError
    except Exception as e:
        if printdebug:
            print(f"梦境创建异常: {e}")
        return Status.DatabaseInsertError

def DreamGetList(connection, user_id: int, page: int = 1, page_size: int = 20,
                   is_public: bool = None, date_from: str = None, date_to: str = None,
                   keyword: str = None):
    """获取梦境列表"""
    try:
        with connection.cursor() as cursor:
            # 构建查询条件
            where_conditions = ["UserID = %s"]
            params = [user_id]

            if is_public is not None:
                where_conditions.append("IsPublic = %s")
                params.append(is_public)

            if date_from:
                where_conditions.append("DreamDate >= %s")
                params.append(date_from)

            if date_to:
                where_conditions.append("DreamDate <= %s")
                params.append(date_to)

            if keyword:
                where_conditions.append("(Title LIKE %s OR Content LIKE %s)")
                params.extend([f"%{keyword}%", f"%{keyword}%"])

            where_clause = " AND ".join(where_conditions)

            # 计算总数
            count_sql = f"SELECT COUNT(*) as total FROM Dreams WHERE {where_clause}"
            cursor.execute(count_sql, params)
            total = cursor.fetchone()['total']

            # 分页查询
            offset = (page - 1) * page_size
            sql = f"""
                SELECT d.DreamID, d.Title, d.DreamDate, d.SleepQuality, d.LucidityLevel,
                       d.IsPublic, d.RecordTime,
                       LEFT(d.Content, 100) as ContentPreview
                FROM Dreams d
                WHERE {where_clause}
                ORDER BY d.RecordTime DESC
                LIMIT %s OFFSET %s
            """
            params.extend([page_size, offset])

            cursor.execute(sql, params)
            dreams = cursor.fetchall()

            # 为每个梦境查询情绪和类型信息
            for dream in dreams:
                dream_id = dream['DreamID']

                # 查询情绪信息
                cursor.execute("""
                    SELECT e.EmotionID, e.EmotionName, e.Color,
                           de.Intensity, de.IsPrimary
                    FROM DreamEmotions de
                    JOIN Emotions e ON de.EmotionID = e.EmotionID
                    WHERE de.DreamID = %s
                    ORDER BY de.IsPrimary DESC, de.Intensity DESC
                """, (dream_id,))
                dream['Emotions'] = cursor.fetchall()

                # 查询类型信息
                cursor.execute("""
                    SELECT dt.TypeID, dt.TypeName, dt.Color,
                           dtr.Confidence
                    FROM DreamTypesRelation dtr
                    JOIN DreamTypes dt ON dtr.TypeID = dt.TypeID
                    WHERE dtr.DreamID = %s
                    ORDER BY dtr.Confidence DESC
                """, (dream_id,))
                dream['DreamTypes'] = cursor.fetchall()

            # 处理日期格式
            for dream in dreams:
                if dream['RecordTime']:
                    dream['RecordTime'] = dream['RecordTime'].isoformat()
                if dream['DreamDate']:
                    dream['DreamDate'] = dream['DreamDate'].isoformat()

            result = {
                'dreams': dreams,
                'pagination': {
                    'current_page': page,
                    'page_size': page_size,
                    'total_items': total,
                    'total_pages': (total + page_size - 1) // page_size
                }
            }

            if printdebug:
                print(f"梦境列表查询成功: 用户ID={user_id}, 总数={total}")

            return result, Status.OK

    except pymysql.Error as e:
        if printdebug:
            print(f"梦境列表查询数据库错误: {e}")
        return None, Status.DatabaseSelectError
    except Exception as e:
        if printdebug:
            print(f"梦境列表查询异常: {e}")
        return None, Status.DatabaseSelectError

def DreamGetDetail(connection, dream_id: int, user_id: int):
    """获取梦境详情"""
    try:
        with connection.cursor() as cursor:
            sql = """
                SELECT DreamID, UserID, Title, Content, DreamDate, SleepQuality,
                       LucidityLevel, IsPublic, RecordTime
                FROM Dreams
                WHERE DreamID = %s AND UserID = %s
            """
            params = (dream_id, user_id)
            cursor.execute(sql, params)
            dream = cursor.fetchone()

            if not dream:
                return None, Status.RecordNotFound

            # 查询情绪信息
            cursor.execute("""
                SELECT e.EmotionID, e.EmotionName, e.Color,
                       de.Intensity, de.IsPrimary
                FROM DreamEmotions de
                JOIN Emotions e ON de.EmotionID = e.EmotionID
                WHERE de.DreamID = %s
                ORDER BY de.IsPrimary DESC, de.Intensity DESC
            """, (dream_id,))
            emotions = cursor.fetchall()

            # 查询类型信息
            cursor.execute("""
                SELECT dt.TypeID, dt.TypeName, dt.Color,
                       dtr.Confidence
                FROM DreamTypesRelation dtr
                JOIN DreamTypes dt ON dtr.TypeID = dt.TypeID
                WHERE dtr.DreamID = %s
                ORDER BY dtr.Confidence DESC
            """, (dream_id,))
            dream_types = cursor.fetchall()

            # 查询关键词信息
            keywords, keyword_status = GetDreamKeywords(connection, dream_id)
            if keyword_status != Status.OK:
                keywords = []

            # 处理日期格式
            dream_dict = {
                'DreamID': dream['DreamID'],
                'UserID': dream['UserID'],
                'Title': dream['Title'],
                'Content': dream['Content'],
                'DreamDate': dream['DreamDate'].isoformat(),
                'SleepQuality': dream['SleepQuality'],
                'LucidityLevel': dream['LucidityLevel'],
                'IsPublic': dream['IsPublic'],
                'RecordTime': dream['RecordTime'].isoformat(),
                'Emotions': emotions,
                'DreamTypes': dream_types,
                'Keywords': keywords
            }

            if printdebug:
                print(f"梦境详情查询成功: 梦境ID={dream_id}")

            return dream_dict, Status.OK

    except pymysql.Error as e:
        if printdebug:
            print(f"梦境详情查询数据库错误: {e}")
        return None, Status.DatabaseSelectError
    except Exception as e:
        if printdebug:
            print(f"梦境详情查询异常: {e}")
        return None, Status.DatabaseSelectError

def DreamUpdate(connection, dream_id: int, user_id: int, title: str = None,
               content: str = None, dream_date: datetime.date = None,
               sleep_quality: int = None, lucidity_level: int = None,
               is_public: bool = None):
    """更新梦境记录"""
    try:
        with connection.cursor() as cursor:
            # 构建更新语句
            update_fields = []
            params = []

            if title is not None:
                update_fields.append("Title = %s")
                params.append(title)
            if content is not None:
                update_fields.append("Content = %s")
                params.append(content)
            if dream_date is not None:
                update_fields.append("DreamDate = %s")
                params.append(dream_date)
            if sleep_quality is not None:
                if not (1 <= sleep_quality <= 5):
                    return Status.ParamsError.ToResponse("睡眠质量必须在1-5之间")
                update_fields.append("SleepQuality = %s")
                params.append(sleep_quality)
            if lucidity_level is not None:
                if not (1 <= lucidity_level <= 5):
                    return Status.ParamsError.ToResponse("梦境清晰度必须在1-5之间")
                update_fields.append("LucidityLevel = %s")
                params.append(lucidity_level)
            if is_public is not None:
                update_fields.append("IsPublic = %s")
                params.append(is_public)

            if not update_fields:
                return Status.ParamsError.ToResponse("没有提供要更新的字段")

            # 添加WHERE条件参数
            params.extend([datetime.now(), dream_id, user_id])

            sql = f"""
                UPDATE Dreams
                SET {', '.join(update_fields)}, RecordTime = %s
                WHERE DreamID = %s AND UserID = %s
            """

            cursor.execute(sql, params)
            connection.commit()

            affected_rows = cursor.rowcount
            if affected_rows == 0:
                return Status.RecordNotFound

            if printdebug:
                print(f"梦境更新成功: 梦境ID={dream_id}, 用户ID={user_id}")

            return Status.OK

    except pymysql.Error as e:
        if printdebug:
            print(f"梦境更新数据库错误: {e}")
        connection.rollback()
        return Status.DatabaseUpdateError
    except Exception as e:
        if printdebug:
            print(f"梦境更新异常: {e}")
        return Status.DatabaseUpdateError

def DreamDelete(connection, dream_id: int, user_id: int):
    """删除梦境记录"""
    try:
        with connection.cursor() as cursor:
            sql = "DELETE FROM Dreams WHERE DreamID = %s AND UserID = %s"
            params = (dream_id, user_id)
            cursor.execute(sql, params)
            connection.commit()

            affected_rows = cursor.rowcount
            if affected_rows == 0:
                return Status.RecordNotFound

            if printdebug:
                print(f"梦境删除成功: 梦境ID={dream_id}, 用户ID={user_id}")

            return Status.OK

    except pymysql.Error as e:
        if printdebug:
            print(f"梦境删除数据库错误: {e}")
        connection.rollback()
        return Status.DatabaseDeleteError
    except Exception as e:
        if printdebug:
            print(f"梦境删除异常: {e}")
        return Status.DatabaseDeleteError