#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import pymysql
from utils.status import Status

printdebug = True

def GetAllEmotions(connection):
    """获取所有情绪"""
    try:
        with connection.cursor() as cursor:
            sql = """
                SELECT EmotionID, EmotionName, Color
                FROM Emotions
                ORDER BY EmotionID
            """
            cursor.execute(sql)
            emotions = cursor.fetchall()

            if printdebug:
                print(f"获取到 {len(emotions)} 种情绪")

            return emotions, Status.OK

    except pymysql.Error as e:
        if printdebug:
            print(f"获取情绪数据库错误: {e}")
        return None, Status.DatabaseSelectError
    except Exception as e:
        if printdebug:
            print(f"获取情绪异常: {e}")
        return None, Status.DatabaseSelectError

def GetAllDreamTypes(connection):
    """获取所有梦境类型"""
    try:
        with connection.cursor() as cursor:
            sql = """
                SELECT TypeID, TypeName, Color
                FROM DreamTypes
                ORDER BY TypeID
            """
            cursor.execute(sql)
            dream_types = cursor.fetchall()

            if printdebug:
                print(f"获取到 {len(dream_types)} 种梦境类型")

            return dream_types, Status.OK

    except pymysql.Error as e:
        if printdebug:
            print(f"获取梦境类型数据库错误: {e}")
        return None, Status.DatabaseSelectError
    except Exception as e:
        if printdebug:
            print(f"获取梦境类型异常: {e}")
        return None, Status.DatabaseSelectError

def GetEmotionById(connection, emotion_id):
    """根据ID获取情绪"""
    try:
        with connection.cursor() as cursor:
            sql = """
                SELECT EmotionID, EmotionName, Color
                FROM Emotions
                WHERE EmotionID = %s
            """
            cursor.execute(sql, (emotion_id,))
            emotion = cursor.fetchone()

            if not emotion:
                return None, Status.RecordNotFound

            if printdebug:
                print(f"获取到情绪: ID={emotion_id}, 名称={emotion['EmotionName']}")

            return emotion, Status.OK

    except pymysql.Error as e:
        if printdebug:
            print(f"获取情绪数据库错误: {e}")
        return None, Status.DatabaseSelectError
    except Exception as e:
        if printdebug:
            print(f"获取情绪异常: {e}")
        return None, Status.DatabaseSelectError

def GetDreamTypeById(connection, type_id):
    """根据ID获取梦境类型"""
    try:
        with connection.cursor() as cursor:
            sql = """
                SELECT TypeID, TypeName, Color
                FROM DreamTypes
                WHERE TypeID = %s
            """
            cursor.execute(sql, (type_id,))
            dream_type = cursor.fetchone()

            if not dream_type:
                return None, Status.RecordNotFound

            if printdebug:
                print(f"获取到梦境类型: ID={type_id}, 名称={dream_type['TypeName']}")

            return dream_type, Status.OK

    except pymysql.Error as e:
        if printdebug:
            print(f"获取梦境类型数据库错误: {e}")
        return None, Status.DatabaseSelectError
    except Exception as e:
        if printdebug:
            print(f"获取梦境类型异常: {e}")
        return None, Status.DatabaseSelectError

def AddDreamEmotions(connection, dream_id, emotions):
    """为梦境添加情绪"""
    try:
        with connection.cursor() as cursor:
            sql = """
                INSERT INTO DreamEmotions (DreamID, EmotionID, Intensity, IsPrimary)
                VALUES (%s, %s, %s, %s)
            """

            for emotion_data in emotions:
                cursor.execute(sql, (
                    dream_id,
                    emotion_data['emotion_id'],
                    emotion_data.get('intensity', 5),
                    emotion_data.get('is_primary', False)
                ))

            connection.commit()

            if printdebug:
                print(f"为梦境ID={dream_id}添加了 {len(emotions)} 种情绪")

            return Status.OK

    except pymysql.Error as e:
        if printdebug:
            print(f"添加梦境情绪数据库错误: {e}")
        connection.rollback()
        return Status.DatabaseInsertError
    except Exception as e:
        if printdebug:
            print(f"添加梦境情绪异常: {e}")
        return Status.DatabaseInsertError

def AddDreamTypes(connection, dream_id, types):
    """为梦境添加类型"""
    try:
        with connection.cursor() as cursor:
            sql = """
                INSERT INTO DreamTypesRelation (DreamID, TypeID, Confidence)
                VALUES (%s, %s, %s)
            """

            for type_data in types:
                cursor.execute(sql, (
                    dream_id,
                    type_data['type_id'],
                    type_data.get('confidence', 1.0)
                ))

            connection.commit()

            if printdebug:
                print(f"为梦境ID={dream_id}添加了 {len(types)} 种类型")

            return Status.OK

    except pymysql.Error as e:
        if printdebug:
            print(f"添加梦境类型数据库错误: {e}")
        connection.rollback()
        return Status.DatabaseInsertError
    except Exception as e:
        if printdebug:
            print(f"添加梦境类型异常: {e}")
        return Status.DatabaseInsertError

def GetDreamEmotions(connection, dream_id):
    """获取梦境的情绪"""
    try:
        with connection.cursor() as cursor:
            sql = """
                SELECT e.EmotionID, e.EmotionName, e.Color,
                       de.Intensity, de.IsPrimary
                FROM DreamEmotions de
                JOIN Emotions e ON de.EmotionID = e.EmotionID
                WHERE de.DreamID = %s
                ORDER BY de.IsPrimary DESC, de.Intensity DESC
            """
            cursor.execute(sql, (dream_id,))
            emotions = cursor.fetchall()

            if printdebug:
                print(f"获取到梦境ID={dream_id}的 {len(emotions)} 种情绪")

            return emotions, Status.OK

    except pymysql.Error as e:
        if printdebug:
            print(f"获取梦境情绪数据库错误: {e}")
        return None, Status.DatabaseSelectError
    except Exception as e:
        if printdebug:
            print(f"获取梦境情绪异常: {e}")
        return None, Status.DatabaseSelectError

def GetDreamTypes(connection, dream_id):
    """获取梦境的类型"""
    try:
        with connection.cursor() as cursor:
            sql = """
                SELECT dt.TypeID, dt.TypeName, dt.Color,
                       dtr.Confidence
                FROM DreamTypesRelation dtr
                JOIN DreamTypes dt ON dtr.TypeID = dt.TypeID
                WHERE dtr.DreamID = %s
                ORDER BY dtr.Confidence DESC
            """
            cursor.execute(sql, (dream_id,))
            dream_types = cursor.fetchall()

            if printdebug:
                print(f"获取到梦境ID={dream_id}的 {len(dream_types)} 种类型")

            return dream_types, Status.OK

    except pymysql.Error as e:
        if printdebug:
            print(f"获取梦境类型数据库错误: {e}")
        return None, Status.DatabaseSelectError
    except Exception as e:
        if printdebug:
            print(f"获取梦境类型异常: {e}")
        return None, Status.DatabaseSelectError