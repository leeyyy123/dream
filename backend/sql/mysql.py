import pymysql
import os
from utils.status import Status

printdebug = True  # 全局调试开关

def ConnectDB():
    """连接MySQL数据库"""
    try:
        # 从环境变量获取配置，如果没有则使用默认值
        db_config = {
            'host': os.getenv('DB_HOST', 'localhost'),
            'port': int(os.getenv('DB_PORT', 3306)),
            'user': os.getenv('DB_USER', 'root'),
            'password': os.getenv('DB_PASSWORD', 'No2023053913'),
            'database': os.getenv('DB_NAME', 'dream'),
            'charset': 'utf8mb4',
            'cursorclass': pymysql.cursors.DictCursor,
            'autocommit': False,
            'init_command': "SET NAMES utf8mb4 COLLATE utf8mb4_unicode_ci"
        }

        if printdebug:
            print(f"尝试连接数据库: {db_config['host']}:{db_config['port']}/{db_config['database']}")

        connection = pymysql.connect(**db_config)

        # 确保连接使用正确的字符集
        with connection.cursor() as cursor:
            cursor.execute("SET NAMES utf8mb4 COLLATE utf8mb4_unicode_ci")
            cursor.execute("SET CHARACTER SET utf8mb4")
            cursor.execute("SET character_set_connection=utf8mb4")
            connection.commit()

        if printdebug:
            print("数据库连接成功，字符集已设置为utf8mb4")

        return connection

    except pymysql.Error as e:
        if printdebug:
            print(f"数据库连接失败: {e}")
        return Status.DatabaseConnectionError
    except Exception as e:
        if printdebug:
            print(f"数据库连接异常: {e}")
        return Status.DatabaseConnectionError