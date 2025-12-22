#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import pymysql
import json
from datetime import datetime
from utils.status import Status

printdebug = True

def AnalysisCreate(connection, user_id: int, start_date: datetime.date, end_date: datetime.date,
                  result: dict, recommendation: str = ""):
    """创建分析记录"""
    try:
        with connection.cursor() as cursor:
            sql = """
                INSERT INTO Analyses (
                    UserID, StartDate, EndDate, Result, Recommendation, CreatedAt
                ) VALUES (%s, %s, %s, %s, %s, %s)
            """
            params = (
                user_id,
                start_date,
                end_date,
                json.dumps(result, ensure_ascii=False),
                recommendation,
                datetime.now()
            )

            cursor.execute(sql, params)
            analysis_id = cursor.lastrowid
            connection.commit()

            if printdebug:
                print(f"分析记录创建成功: ID={analysis_id}, 用户ID={user_id}")

            return Status.OK

    except pymysql.Error as e:
        if printdebug:
            print(f"分析记录创建数据库错误: {e}")
        connection.rollback()
        return Status.DatabaseInsertError
    except Exception as e:
        if printdebug:
            print(f"分析记录创建异常: {e}")
        return Status.DatabaseInsertError

def AnalysisGetList(connection, user_id: int, page: int = 1, page_size: int = 20):
    """获取用户分析记录列表"""
    try:
        with connection.cursor() as cursor:
            # 计算总数
            cursor.execute("SELECT COUNT(*) as total FROM Analyses WHERE UserID = %s", (user_id,))
            total = cursor.fetchone()['total']

            # 分页查询
            offset = (page - 1) * page_size
            sql = """
                SELECT AnalysisID, StartDate, EndDate, Result, Recommendation, CreatedAt
                FROM Analyses
                WHERE UserID = %s
                ORDER BY CreatedAt DESC
                LIMIT %s OFFSET %s
            """
            params = [user_id, page_size, offset]
            cursor.execute(sql, params)
            analyses = cursor.fetchall()

            # 处理日期格式
            for analysis in analyses:
                if analysis['CreatedAt']:
                    analysis['CreatedAt'] = analysis['CreatedAt'].isoformat()
                if analysis['StartDate']:
                    analysis['StartDate'] = analysis['StartDate'].isoformat()
                if analysis['EndDate']:
                    analysis['EndDate'] = analysis['EndDate'].isoformat()

            result = {
                'analyses': analyses,
                'pagination': {
                    'current_page': page,
                    'page_size': page_size,
                    'total_items': total,
                    'total_pages': (total + page_size - 1) // page_size
                }
            }

            if printdebug:
                print(f"分析记录列表查询成功: 用户ID={user_id}, 总数={total}")

            return result, Status.OK

    except pymysql.Error as e:
        if printdebug:
            print(f"分析记录列表查询数据库错误: {e}")
        return None, Status.DatabaseSelectError
    except Exception as e:
        if printdebug:
            print(f"分析记录列表查询异常: {e}")
        return None, Status.DatabaseSelectError

def AnalysisGetDetail(connection, analysis_id: int, user_id: int):
    """获取分析记录详情"""
    try:
        with connection.cursor() as cursor:
            sql = """
                SELECT AnalysisID, UserID, StartDate, EndDate, Result, Recommendation, CreatedAt
                FROM Analyses
                WHERE AnalysisID = %s AND UserID = %s
            """
            params = (analysis_id, user_id)
            cursor.execute(sql, params)
            analysis = cursor.fetchone()

            if not analysis:
                return None, Status.RecordNotFound

            # 处理日期格式
            analysis_dict = {
                'AnalysisID': analysis['AnalysisID'],
                'UserID': analysis['UserID'],
                'StartDate': analysis['StartDate'].isoformat(),
                'EndDate': analysis['EndDate'].isoformat(),
                'Result': analysis['Result'],
                'Recommendation': analysis['Recommendation'],
                'CreatedAt': analysis['CreatedAt'].isoformat()
            }

            if printdebug:
                print(f"分析记录详情查询成功: 分析ID={analysis_id}")

            return analysis_dict, Status.OK

    except pymysql.Error as e:
        if printdebug:
            print(f"分析记录详情查询数据库错误: {e}")
        return None, Status.DatabaseSelectError
    except Exception as e:
        if printdebug:
            print(f"分析记录详情查询异常: {e}")
        return None, Status.DatabaseSelectError

def AnalysisDelete(connection, analysis_id: int, user_id: int):
    """删除分析记录"""
    try:
        with connection.cursor() as cursor:
            sql = "DELETE FROM Analyses WHERE AnalysisID = %s AND UserID = %s"
            params = (analysis_id, user_id)
            cursor.execute(sql, params)
            connection.commit()

            affected_rows = cursor.rowcount
            if affected_rows == 0:
                return Status.RecordNotFound

            if printdebug:
                print(f"分析记录删除成功: 分析ID={analysis_id}, 用户ID={user_id}")

            return Status.OK

    except pymysql.Error as e:
        if printdebug:
            print(f"分析记录删除数据库错误: {e}")
        connection.rollback()
        return Status.DatabaseDeleteError
    except Exception as e:
        if printdebug:
            print(f"分析记录删除异常: {e}")
        return Status.DatabaseDeleteError

def GetAnalysisDreamStats(connection, user_id: int, start_date: datetime.date, end_date: datetime.date):
    """获取指定时间段的梦境统计数据"""
    try:
        with connection.cursor() as cursor:
            # 获取该时间段内的所有梦境
            sql = """
                SELECT DreamID FROM Dreams
                WHERE UserID = %s AND DreamDate BETWEEN %s AND %s
            """
            cursor.execute(sql, (user_id, start_date, end_date))
            dream_ids = [row['DreamID'] for row in cursor.fetchall()]

            if not dream_ids:
                return {
                    'totalDreams': 0,
                    'emotionStats': {},
                    'typeStats': {},
                    'sleepQualityStats': {1: 0, 2: 0, 3: 0, 4: 0, 5: 0},
                    'lucidityStats': {1: 0, 2: 0, 3: 0, 4: 0, 5: 0},
                    'dailyDreamCounts': []
                }, Status.OK

            # 获取梦境详细信息
            dream_ids_str = ','.join(map(str, dream_ids))
            sql = """
                SELECT d.DreamID, d.Title, d.DreamDate, d.SleepQuality, d.LucidityLevel,
                       d.Content
                FROM Dreams d
                WHERE d.DreamID IN ({})
                ORDER BY d.DreamDate DESC
            """.format(dream_ids_str)
            cursor.execute(sql)
            dreams = cursor.fetchall()

            # 统计数据
            emotion_counts = {}
            type_counts = {}
            sleep_quality_counts = {1: 0, 2: 0, 3: 0, 4: 0, 5: 0}
            lucidity_counts = {1: 0, 2: 0, 3: 0, 4: 0, 5: 0}
            daily_counts = {}

            for dream in dreams:
                # 睡眠质量统计
                sleep_quality = dream['SleepQuality']
                if sleep_quality >= 1 and sleep_quality <= 5:
                    sleep_quality_counts[sleep_quality] += 1

                # 清晰度统计
                lucidity = dream['LucidityLevel']
                if lucidity >= 1 and lucidity <= 5:
                    lucidity_counts[lucidity] += 1

                # 按日期统计
                dream_date = dream['DreamDate'].isoformat() if hasattr(dream['DreamDate'], 'isoformat') else str(dream['DreamDate'])
                daily_counts[dream_date] = daily_counts.get(dream_date, 0) + 1

            # 获取情绪统计
            if dream_ids:
                sql = """
                    SELECT e.EmotionName, COUNT(*) as count
                    FROM DreamEmotions de
                    JOIN Emotions e ON de.EmotionID = e.EmotionID
                    WHERE de.DreamID IN ({})
                    GROUP BY e.EmotionName
                    ORDER BY count DESC
                """.format(dream_ids_str)
                cursor.execute(sql)
                for row in cursor.fetchall():
                    emotion_counts[row['EmotionName']] = row['count']

            # 获取类型统计
            if dream_ids:
                sql = """
                    SELECT dt.TypeName, COUNT(*) as count
                    FROM DreamTypesRelation dtr
                    JOIN DreamTypes dt ON dtr.TypeID = dt.TypeID
                    WHERE dtr.DreamID IN ({})
                    GROUP BY dt.TypeName
                    ORDER BY count DESC
                """.format(dream_ids_str)
                cursor.execute(sql)
                for row in cursor.fetchall():
                    type_counts[row['TypeName']] = row['count']

            # 生成日期范围
            date_range = []
            current_date = start_date
            while current_date <= end_date:
                date_range.append(current_date.isoformat())
                current_date = datetime.combine(current_date, datetime.min.time()) + datetime.timedelta(days=1)

            daily_dream_counts = [
                {'date': date, 'count': daily_counts.get(date, 0)}
                for date in date_range
            ]

            result = {
                'totalDreams': len(dreams),
                'emotionStats': emotion_counts,
                'typeStats': type_counts,
                'sleepQualityStats': sleep_quality_counts,
                'lucidityStats': lucidity_counts,
                'dailyDreamCounts': daily_dream_counts
            }

            if printdebug:
                print(f"梦境统计数据生成成功: 用户ID={user_id}, 时间段={start_date}~{end_date}")

            return result, Status.OK

    except pymysql.Error as e:
        if printdebug:
            print(f"梦境统计数据获取数据库错误: {e}")
        return None, Status.DatabaseSelectError
    except Exception as e:
        if printdebug:
            print(f"梦境统计数据获取异常: {e}")
        return None, Status.DatabaseSelectError