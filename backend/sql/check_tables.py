#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import pymysql
import os

def check_and_create_tables():
    """检查并创建情绪和类型表"""

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

        print("检查现有表...")

        # 检查表是否存在
        cursor.execute("SHOW TABLES LIKE 'Emotions'")
        emotions_exists = cursor.fetchone()

        cursor.execute("SHOW TABLES LIKE 'DreamTypes'")
        types_exists = cursor.fetchone()

        print(f"Emotions表存在: {bool(emotions_exists)}")
        print(f"DreamTypes表存在: {bool(types_exists)}")

        # 如果表存在，查看结构
        if emotions_exists:
            print("\nEmotions表结构:")
            cursor.execute("DESCRIBE Emotions")
            for row in cursor.fetchall():
                print(f"  {row}")

        if types_exists:
            print("\nDreamTypes表结构:")
            cursor.execute("DESCRIBE DreamTypes")
            for row in cursor.fetchall():
                print(f"  {row}")

        # 删除旧表并重新创建
        print("\n删除旧表...")
        cursor.execute("DROP TABLE IF EXISTS DreamEmotions")
        cursor.execute("DROP TABLE IF EXISTS DreamTypesRelation")
        cursor.execute("DROP TABLE IF EXISTS DreamTypes")
        cursor.execute("DROP TABLE IF EXISTS Emotions")
        connection.commit()

        print("重新创建表...")

        # 创建情绪表
        cursor.execute("""
            CREATE TABLE Emotions (
                EmotionID INT AUTO_INCREMENT PRIMARY KEY,
                Name VARCHAR(50) NOT NULL UNIQUE,
                Color VARCHAR(7) NOT NULL,
                Description TEXT,
                CreatedAt TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                UpdatedAt TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP
            ) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci
        """)

        # 创建梦境类型表
        cursor.execute("""
            CREATE TABLE DreamTypes (
                TypeID INT AUTO_INCREMENT PRIMARY KEY,
                Name VARCHAR(50) NOT NULL UNIQUE,
                Color VARCHAR(7) NOT NULL,
                Description TEXT,
                CreatedAt TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                UpdatedAt TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP
            ) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci
        """)

        # 情绪数据
        emotions_data = [
            ('喜悦', '#FFD93D', '感到快乐、愉悦的情绪状态'),
            ('平静', '#98D8AA', '内心安宁、平和的状态'),
            ('好奇', '#6BC5F2', '对事物产生兴趣和探索欲望'),
            ('爱', '#FF9E9E', '对他人的关爱和情感连接'),
            ('恐惧', '#7B2CBF', '感到害怕、不安的情绪'),
            ('焦虑', '#FF6B6B', '担忧、紧张的情绪状态'),
            ('悲伤', '#5D8AA8', '感到失落、难过的情绪'),
            ('愤怒', '#C40C0C', '感到生气、不满的情绪'),
            ('困惑', '#A0A0A0', '感到迷茫、不解的状态'),
            ('中性', '#E0E0E0', '无明显情绪倾向的状态'),
            ('羞耻', '#DDA0DD', '感到尴尬、不好意思的情绪'),
            ('敬畏', '#003153', '感到震撼、崇高的情绪')
        ]

        # 插入情绪数据
        for emotion in emotions_data:
            cursor.execute("""
                INSERT INTO Emotions (Name, Color, Description)
                VALUES (%s, %s, %s)
            """, emotion)

        print(f"插入 {len(emotions_data)} 种情绪")

        # 梦境类型数据
        types_data = [
            ('冒险', '#FFA500', '充满探索和挑战的梦境'),
            ('飞行', '#87CEEB', '在空中自由飞翔的梦境'),
            ('坠落', '#8B4513', '从高处坠落的感觉'),
            ('被追逐', '#DC143C', '被追赶的紧张梦境'),
            ('牙齿脱落', '#F5F5DC', '牙齿掉落或损坏的梦境'),
            ('遇见逝者', '#D8BFD8', '与已故亲人朋友相遇'),
            ('迷路', '#696969', '找不到方向或道路'),
            ('受困', '#2F4F4F', '被困在某个空间中'),
            ('清醒梦', '#00FF7F', '意识到自己在做梦的梦境'),
            ('重复梦', '#4B0082', '反复出现的相似梦境'),
            ('噩梦', '#301934', '令人恐惧不安的噩梦'),
            ('预知梦', '#8A2BE2', '似乎预示未来的梦境'),
            ('春梦', '#C71585', '与性爱相关的梦境'),
            ('神话梦', '#DA9100', '涉及神话、超自然元素'),
            ('日常梦', '#F0F0F0', '反映日常生活的梦境'),
            ('超现实梦', '#9FE2BF', '逻辑混乱、超现实的场景'),
            ('疗愈梦', '#50C878', '带来治愈和安慰的梦境')
        ]

        # 插入梦境类型数据
        for dream_type in types_data:
            cursor.execute("""
                INSERT INTO DreamTypes (Name, Color, Description)
                VALUES (%s, %s, %s)
            """, dream_type)

        print(f"插入 {len(types_data)} 种梦境类型")

        # 创建关联表
        cursor.execute("""
            CREATE TABLE DreamEmotions (
                DreamID INT NOT NULL,
                EmotionID INT NOT NULL,
                Intensity ENUM('low', 'medium', 'high') DEFAULT 'medium',
                PRIMARY KEY (DreamID, EmotionID),
                FOREIGN KEY (DreamID) REFERENCES Dreams(DreamID) ON DELETE CASCADE,
                FOREIGN KEY (EmotionID) REFERENCES Emotions(EmotionID) ON DELETE CASCADE
            ) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci
        """)

        cursor.execute("""
            CREATE TABLE DreamTypesRelation (
                DreamID INT NOT NULL,
                TypeID INT NOT NULL,
                IsPrimary BOOLEAN DEFAULT FALSE,
                PRIMARY KEY (DreamID, TypeID),
                FOREIGN KEY (DreamID) REFERENCES Dreams(DreamID) ON DELETE CASCADE,
                FOREIGN KEY (TypeID) REFERENCES DreamTypes(TypeID) ON DELETE CASCADE
            ) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci
        """)

        connection.commit()

        # 验证数据
        cursor.execute("SELECT COUNT(*) as count FROM Emotions")
        emotion_count = cursor.fetchone()['count']

        cursor.execute("SELECT COUNT(*) as count FROM DreamTypes")
        type_count = cursor.fetchone()['count']

        print(f"\n验证结果:")
        print(f"情绪总数: {emotion_count}")
        print(f"梦境类型总数: {type_count}")

        cursor.close()
        connection.close()

        print("\n初始化完成!")

    except Exception as e:
        print(f"错误: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    check_and_create_tables()