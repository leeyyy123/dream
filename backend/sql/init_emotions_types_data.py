#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import pymysql
import os

def init_emotions_and_types():
    """初始化情绪和梦境类型数据"""

    config = {
        'host': os.getenv('DB_HOST', 'localhost'),
        'port': int(os.getenv('DB_PORT', 3306)),
        'user': os.getenv('DB_USER', 'root'),
        'password': os.getenv('DB_PASSWORD', 'No2023053913'),
        'database': os.getenv('DB_NAME', 'dream'),
        'charset': 'utf8mb4',
        'cursorclass': pymysql.cursors.DictCursor
    }

    try:
        connection = pymysql.connect(**config)
        cursor = connection.cursor()

        print("=== 初始化情绪数据 ===")

        # 情绪数据（按照提供的颜色和描述）
        emotions = [
            ('喜悦', '#FFD93D'),
            ('平静', '#98D8AA'),
            ('好奇', '#6BC5F2'),
            ('爱', '#FF9E9E'),
            ('恐惧', '#7B2CBF'),
            ('焦虑', '#FF6B6B'),
            ('悲伤', '#5D8AA8'),
            ('愤怒', '#C40C0C'),
            ('困惑', '#A0A0A0'),
            ('中性', '#E0E0E0'),
            ('羞耻', '#DDA0DD'),
            ('敬畏', '#003153')
        ]

        # 清空并插入情绪数据
        cursor.execute("DELETE FROM Emotions")

        for emotion in emotions:
            cursor.execute("""
                INSERT INTO Emotions (EmotionName, Color)
                VALUES (%s, %s)
            """, emotion)

        print(f"成功插入 {len(emotions)} 种情绪")

        print("\n=== 初始化梦境类型数据 ===")

        # 梦境类型数据（按照提供的颜色）
        dream_types = [
            ('冒险', '#FFA500'),
            ('飞行', '#87CEEB'),
            ('坠落', '#8B4513'),
            ('被追逐', '#DC143C'),
            ('牙齿脱落', '#F5F5DC'),
            ('遇见逝者', '#D8BFD8'),
            ('迷路', '#696969'),
            ('受困', '#2F4F4F'),
            ('清醒梦', '#00FF7F'),
            ('重复梦', '#4B0082'),
            ('噩梦', '#301934'),
            ('预知梦', '#8A2BE2'),
            ('春梦', '#C71585'),
            ('神话梦', '#DA9100'),
            ('日常梦', '#F0F0F0'),
            ('超现实梦', '#9FE2BF'),
            ('疗愈梦', '#50C878')
        ]

        # 清空并插入梦境类型数据
        cursor.execute("DELETE FROM DreamTypes")

        for dream_type in dream_types:
            cursor.execute("""
                INSERT INTO DreamTypes (TypeName, Color)
                VALUES (%s, %s)
            """, dream_type)

        print(f"成功插入 {len(dream_types)} 种梦境类型")

        connection.commit()

        # 验证数据
        print("\n=== 数据验证 ===")
        cursor.execute("SELECT EmotionID, EmotionName, Color FROM Emotions ORDER BY EmotionID")
        emotions_result = cursor.fetchall()

        cursor.execute("SELECT TypeID, TypeName, Color FROM DreamTypes ORDER BY TypeID")
        types_result = cursor.fetchall()

        print(f"情绪总数: {len(emotions_result)}")
        print("情绪列表:")
        for emotion in emotions_result:
            print(f"  ID: {emotion['EmotionID']}, 名称: {emotion['EmotionName']}, 颜色: {emotion['Color']}")

        print(f"\n梦境类型总数: {len(types_result)}")
        print("梦境类型列表:")
        for dream_type in types_result:
            print(f"  ID: {dream_type['TypeID']}, 名称: {dream_type['TypeName']}, 颜色: {dream_type['Color']}")

        cursor.close()
        connection.close()

        print("\n数据初始化完成！")

    except Exception as e:
        print(f"初始化失败: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    init_emotions_and_types()