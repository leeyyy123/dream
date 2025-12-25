import pymysql
import zlib
from datetime import datetime
from utils.status import Status

printdebug = True


def ImageInsert(connection, image_name: str, original_name: str, mime_type: str,
                file_size: int, width: int, height: int, compressed_data: bytes,
                compression_ratio: float = None):
    """插入图片记录"""
    try:
        with connection.cursor() as cursor:
            sql = """
                INSERT INTO Images (
                    ImageName, OriginalName, MimeType, FileSize, Width, Height,
                    CompressedData, CompressionRatio, CreatedTime, IsActive
                ) VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
            """
            params = (
                image_name,
                original_name,
                mime_type,
                file_size,
                width,
                height,
                compressed_data,
                compression_ratio,
                datetime.now(),
                True
            )

            cursor.execute(sql, params)
            image_id = cursor.lastrowid
            connection.commit()

            if printdebug:
                print(f"图片插入成功: ID={image_id}, 原始文件名={original_name}, 大小={file_size}")

            return image_id, Status.OK

    except pymysql.Error as e:
        if printdebug:
            print(f"图片插入数据库错误: {e}")
        connection.rollback()
        return None, Status.DatabaseInsertError
    except Exception as e:
        if printdebug:
            print(f"图片插入异常: {e}")
        return None, Status.DatabaseInsertError


def ImageGetById(connection, image_id: int):
    """根据ID获取图片"""
    try:
        with connection.cursor() as cursor:
            sql = """
                SELECT ImageID, ImageName, OriginalName, MimeType, FileSize,
                       Width, Height, CompressedData, CompressionRatio,
                       CreatedTime, IsActive
                FROM Images
                WHERE ImageID = %s AND IsActive = TRUE
            """
            params = (image_id,)
            cursor.execute(sql, params)
            image = cursor.fetchone()

            if not image:
                return None, Status.RecordNotFound

            image_dict = {
                'ImageID': image['ImageID'],
                'ImageName': image['ImageName'],
                'OriginalName': image['OriginalName'],
                'MimeType': image['MimeType'],
                'FileSize': image['FileSize'],
                'Width': image['Width'],
                'Height': image['Height'],
                'CompressedData': image['CompressedData'],
                'CompressionRatio': image['CompressionRatio'],
                'CreatedTime': image['CreatedTime'].isoformat() if image['CreatedTime'] else None,
                'IsActive': image['IsActive']
            }

            if printdebug:
                print(f"图片查询成功: ID={image_id}")

            return image_dict, Status.OK

    except pymysql.Error as e:
        if printdebug:
            print(f"图片查询数据库错误: {e}")
        return None, Status.DatabaseSelectError
    except Exception as e:
        if printdebug:
            print(f"图片查询异常: {e}")
        return None, Status.DatabaseSelectError


def ImageDelete(connection, image_id: int):
    """软删除图片（设置为非活跃状态）"""
    try:
        with connection.cursor() as cursor:
            sql = "UPDATE Images SET IsActive = FALSE WHERE ImageID = %s"
            params = (image_id,)
            cursor.execute(sql, params)
            connection.commit()

            affected_rows = cursor.rowcount
            if affected_rows == 0:
                return Status.RecordNotFound

            if printdebug:
                print(f"图片删除成功: ID={image_id}")

            return Status.OK

    except pymysql.Error as e:
        if printdebug:
            print(f"图片删除数据库错误: {e}")
        connection.rollback()
        return Status.DatabaseDeleteError
    except Exception as e:
        if printdebug:
            print(f"图片删除异常: {e}")
        return Status.DatabaseDeleteError


def compress_image_data(image_data: bytes, level: int = 6) -> tuple[bytes, float]:
    """
    压缩图片数据
    :param image_data: 原始图片数据
    :param level: 压缩级别 (0-9, 默认6)
    :return: (压缩后的数据, 压缩比率)
    """
    try:
        compressed_data = zlib.compress(image_data, level=level)
        compression_ratio = len(compressed_data) / len(image_data) if image_data else 0
        return compressed_data, round(compression_ratio, 2)
    except Exception as e:
        if printdebug:
            print(f"图片压缩失败: {e}")
        return image_data, 1.0
