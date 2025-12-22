import pymysql
from datetime import datetime
from utils.status import Status

printdebug = True

def GetDreamStatistics(connection, user_id: int):
    """获取用户的梦境统计数据"""
    try:
        with connection.cursor() as cursor:
            # 梦境总数
            cursor.execute("SELECT COUNT(*) as total FROM Dreams WHERE UserID = %s", (user_id,))
            total_dreams = cursor.fetchone()['total']

            # 分析报告总数
            cursor.execute("SELECT COUNT(*) as total FROM Analyses WHERE UserID = %s", (user_id,))
            total_analyses = cursor.fetchone()['total']

            # 本月记录数
            cursor.execute("""
                SELECT COUNT(*) as monthly_total
                FROM Dreams
                WHERE UserID = %s
                AND YEAR(DreamDate) = YEAR(CURRENT_DATE())
                AND MONTH(DreamDate) = MONTH(CURRENT_DATE())
            """, (user_id,))
            monthly_dreams = cursor.fetchone()['monthly_total']

            # 最近梦境记录（获取最近3条）
            cursor.execute("""
                SELECT DreamID, Title, DreamDate, RecordTime,
                       LEFT(Content, 50) as ContentPreview
                FROM Dreams
                WHERE UserID = %s
                ORDER BY RecordTime DESC
                LIMIT 3
            """, (user_id,))
            recent_dreams = cursor.fetchall()

            # 处理日期格式
            for dream in recent_dreams:
                if dream['RecordTime']:
                    dream['RecordTime'] = dream['RecordTime'].isoformat()
                if dream['DreamDate']:
                    dream['DreamDate'] = dream['DreamDate'].isoformat()

            result = {
                'totalDreams': total_dreams,
                'totalAnalyses': total_analyses,
                'monthlyDreams': monthly_dreams,
                'recentDreams': recent_dreams
            }

            if printdebug:
                print(f"统计数据获取成功: 用户ID={user_id}, 梦境总数={total_dreams}, 分析报告={total_analyses}, 本月记录={monthly_dreams}")

            return result, Status.OK

    except pymysql.Error as e:
        if printdebug:
            print(f"统计数据查询数据库错误: {e}")
        return None, Status.DatabaseSelectError
    except Exception as e:
        if printdebug:
            print(f"统计数据查询异常: {e}")
        return None, Status.DatabaseSelectError