#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import pymysql
import json
from datetime import datetime, timedelta
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

            # 处理日期格式和解析结果
            for analysis in analyses:
                if analysis['CreatedAt']:
                    analysis['CreatedAt'] = analysis['CreatedAt'].isoformat()
                if analysis['StartDate']:
                    analysis['StartDate'] = analysis['StartDate'].isoformat()
                if analysis['EndDate']:
                    analysis['EndDate'] = analysis['EndDate'].isoformat()

                # 解析 Result JSON 字段
                if analysis['Result']:
                    try:
                        result_data = json.loads(analysis['Result']) if isinstance(analysis['Result'], str) else analysis['Result']
                        if 'stats' in result_data:
                            analysis['DreamCount'] = result_data['stats'].get('totalDreams', 0)
                        else:
                            analysis['DreamCount'] = 0
                    except:
                        analysis['DreamCount'] = 0
                else:
                    analysis['DreamCount'] = 0

                # 添加 DateFrom 和 DateTo 字段（与 StartDate/EndDate 相同）
                analysis['DateFrom'] = analysis['StartDate']
                analysis['DateTo'] = analysis['EndDate']

            result = {
                'Analyses': analyses,
                'Pagination': {
                    'CurrentPage': page,
                    'PageSize': page_size,
                    'TotalItems': total,
                    'TotalPages': (total + page_size - 1) // page_size
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
                    'keywordStats': {
                        'byCategory': {},
                        'topKeywords': []
                    },
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

            # 获取情绪统计和完整信息
            if dream_ids:
                sql = """
                    SELECT e.EmotionID, e.EmotionName, e.Color, COUNT(*) as count
                    FROM DreamEmotions de
                    JOIN Emotions e ON de.EmotionID = e.EmotionID
                    WHERE de.DreamID IN ({})
                    GROUP BY e.EmotionID, e.EmotionName, e.Color
                    ORDER BY count DESC
                """.format(dream_ids_str)
                cursor.execute(sql)
                for row in cursor.fetchall():
                    emotion_counts[row['EmotionName']] = {
                        'count': row['count'],
                        'color': row['Color'],
                        'id': row['EmotionID']
                    }

            # 获取类型统计和完整信息
            if dream_ids:
                sql = """
                    SELECT dt.TypeID, dt.TypeName, dt.Color, COUNT(*) as count
                    FROM DreamTypesRelation dtr
                    JOIN DreamTypes dt ON dtr.TypeID = dt.TypeID
                    WHERE dtr.DreamID IN ({})
                    GROUP BY dt.TypeID, dt.TypeName, dt.Color
                    ORDER BY count DESC
                """.format(dream_ids_str)
                cursor.execute(sql)
                for row in cursor.fetchall():
                    type_counts[row['TypeName']] = {
                        'count': row['count'],
                        'color': row['Color'],
                        'id': row['TypeID']
                    }

            # 获取关键词统计（按分类和文本）
            keyword_stats = {
                'byCategory': {},
                'topKeywords': []
            }

            if dream_ids:
                # 按分类统计关键词
                sql = """
                    SELECT Category, COUNT(*) as count
                    FROM Keywords
                    WHERE DreamID IN ({})
                    GROUP BY Category
                    ORDER BY count DESC
                """.format(dream_ids_str)
                cursor.execute(sql)
                for row in cursor.fetchall():
                    category = row['Category']
                    keyword_stats['byCategory'][category] = row['count']

                # 获取出现频率最高的关键词（词云数据）
                sql = """
                    SELECT KeywordText, Category, COUNT(*) as count
                    FROM Keywords
                    WHERE DreamID IN ({})
                    GROUP BY KeywordText, Category
                    ORDER BY count DESC
                    LIMIT 50
                """.format(dream_ids_str)
                cursor.execute(sql)
                for row in cursor.fetchall():
                    keyword_stats['topKeywords'].append({
                        'text': row['KeywordText'],
                        'category': row['Category'],
                        'count': row['count']
                    })

            # 生成日期范围
            date_range = []
            current_date = start_date
            while current_date <= end_date:
                date_range.append(current_date.isoformat())
                current_date = current_date + timedelta(days=1)

            daily_dream_counts = [
                {'date': date, 'count': daily_counts.get(date, 0)}
                for date in date_range
            ]

            result = {
                'totalDreams': len(dreams),
                'emotionStats': emotion_counts,
                'typeStats': type_counts,
                'keywordStats': keyword_stats,
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
            import traceback
            print(f"详细错误: {traceback.format_exc()}")
        return None, Status.DatabaseSelectError
    except Exception as e:
        if printdebug:
            print(f"梦境统计数据获取异常: {e}")
            import traceback
            print(f"详细错误: {traceback.format_exc()}")
        return None, Status.DatabaseSelectError