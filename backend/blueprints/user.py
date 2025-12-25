from flask import Blueprint, request, jsonify, g, send_file, Response
from flask_jwt_extended import jwt_required, get_jwt_identity
from werkzeug.utils import secure_filename
import io
import uuid
from datetime import datetime
from utils.status import Status
from sql.database import get_db
from sql.UserSql import UserGetInfo, UpdateUserInfo
from sql.StatisticsSql import GetDreamStatistics
from sql.ImageSql import ImageInsert, ImageGetById, compress_image_data

# Create blueprint
user_bp = Blueprint('user', __name__, url_prefix='/User')

@user_bp.before_request
def handle_options():
    """处理跨域预检请求"""
    if request.method == 'OPTIONS':
        response = jsonify({'status': 'preflight'})
        response.headers.add('Access-Control-Allow-Headers', 'Content-Type,Authorization')
        response.headers.add('Access-Control-Allow-Methods', 'GET,PUT,POST,DELETE,OPTIONS')
        response.headers.add('Access-Control-Allow-Origin', '*')
        return response

@user_bp.before_request
def before_request():
    """请求前处理，建立数据库连接"""
    try:
        connection = get_db()
        request.connection = connection
    except Exception as e:
        print(f"Database connection creation failed: {str(e)}")
        request.connection = None

@user_bp.route('/GetInfo', methods=['GET','OPTIONS'])
@jwt_required()
def get_user_info():
    """获取当前用户信息"""
    try:
        # 获取当前用户的邮箱
        current_email = get_jwt_identity()

        if not current_email:
            return jsonify(Status.AuthFailed.ToResponse("未找到用户信息"))

        # 获取数据库连接
        connection = getattr(request, 'connection', None)
        if isinstance(connection, Status):
            return jsonify(connection.ToResponse())

        # 检查是否是超级管理员
        if current_email == "admin@dream.com":
            admin_info = {
                "UserID": -1,
                "UserName": "超级管理员",
                "Email": "admin@dream.com",
                "AvatarUrl": None,
                "Role": "super_admin"
            }
            response = Status.OK.ToResponse()
            response['Data'] = admin_info
            return jsonify(response)

        # 查询普通用户信息
        user_info, user_status = UserGetInfo(connection, current_email)
        if user_status == Status.OK and user_info:
            response = Status.OK.ToResponse()
            response['Data'] = user_info
            return jsonify(response)
        else:
            return jsonify(user_status.ToResponse())

    except Exception as e:
        print(f"Get user info exception: {str(e)}")
        return jsonify(Status.ErrorRequest.ToResponse(str(e)))

@user_bp.route('/UpdateInfo', methods=['PUT','OPTIONS'])
@jwt_required()
def update_user_info():
    """更新当前用户信息"""
    try:
        # 获取数据库连接
        connection = getattr(request, 'connection', None)
        if isinstance(connection, Status):
            return jsonify(connection.ToResponse())

        # 获取当前用户信息
        current_email = get_jwt_identity()
        if not current_email:
            return jsonify(Status.AuthFailed.ToResponse("未找到用户信息"))

        # 查询用户ID
        with connection.cursor() as cursor:
            cursor.execute("SELECT UserID FROM Users WHERE Email = %s", (current_email,))
            user_result = cursor.fetchone()
            if not user_result:
                return jsonify(Status.UserUnexist.ToResponse())
            user_id = user_result['UserID']

        # 获取请求体数据
        data = request.get_json()
        if not data:
            return jsonify(Status.ParamsError.ToResponse("缺少请求数据"))

        # 构建用户信息字典
        user_info = {}

        if 'userName' in data:
            user_info['userName'] = data['userName']

        if 'gender' in data:
            # 验证gender值
            valid_genders = ['M', 'F', 'O', '']
            if data['gender'] not in valid_genders:
                return jsonify(Status.ParamsError.ToResponse("性别值无效"))
            user_info['gender'] = data['gender']

        if 'birthDate' in data:
            user_info['birthDate'] = data['birthDate']

        if 'phone' in data:
            user_info['phone'] = data['phone']

        if 'address' in data:
            user_info['address'] = data['address']

        # 调用更新函数
        status = UpdateUserInfo(connection, user_id, user_info)

        if status == Status.OK:
            response = Status.OK.ToResponse("用户信息更新成功")
            return jsonify(response)
        elif status == Status.ParamsError:
            return jsonify(Status.ParamsError.ToResponse("没有需要更新的字段"))
        else:
            return jsonify(status.ToResponse())

    except Exception as e:
        print(f"Update user info exception: {str(e)}")
        return jsonify(Status.ErrorRequest.ToResponse(str(e)))

@user_bp.route('/GetStatistics', methods=['GET','OPTIONS'])
@jwt_required()
def get_user_statistics():
    """获取用户统计数据"""
    try:
        # 获取数据库连接
        connection = getattr(request, 'connection', None)
        if isinstance(connection, Status):
            return jsonify(connection.ToResponse())

        # 获取当前用户信息
        current_email = get_jwt_identity()
        if not current_email:
            return jsonify(Status.AuthFailed.ToResponse("未找到用户信息"))

        # 查询用户ID
        with connection.cursor() as cursor:
            cursor.execute("SELECT UserID FROM Users WHERE Email = %s", (current_email,))
            user_result = cursor.fetchone()
            if not user_result:
                return jsonify(Status.UserUnexist.ToResponse())

            user_id = user_result['UserID']

        # 获取统计数据
        statistics, status = GetDreamStatistics(connection, user_id)

        if status == Status.OK:
            response = {
                "Code": 200,
                "Msg": "获取统计数据成功",
                "Data": statistics
            }
            return jsonify(response)
        else:
            return jsonify(status.ToResponse())

    except Exception as e:
        print(f"获取统计数据异常: {str(e)}")
        return jsonify(Status.ErrorRequest.ToResponse(str(e)))

@user_bp.route('/UploadAvatar', methods=['POST','OPTIONS'])
@jwt_required()
def upload_avatar():
    """上传用户头像"""
    try:
        # 获取数据库连接
        connection = getattr(request, 'connection', None)
        if isinstance(connection, Status):
            return jsonify(connection.ToResponse())

        # 获取当前用户信息
        current_email = get_jwt_identity()
        if not current_email:
            return jsonify(Status.AuthFailed.ToResponse("未找到用户信息"))

        # 获取用户ID
        with connection.cursor() as cursor:
            cursor.execute("SELECT UserID FROM Users WHERE Email = %s", (current_email,))
            user_result = cursor.fetchone()
            if not user_result:
                return jsonify(Status.UserUnexist.ToResponse())
            user_id = user_result['UserID']

        # 检查是否有上传的文件
        if 'avatar' not in request.files:
            return jsonify(Status.ParamsError.ToResponse("未找到上传文件"))

        file = request.files['avatar']
        if file.filename == '':
            return jsonify(Status.ParamsError.ToResponse("未选择文件"))

        # 验证文件类型
        allowed_extensions = {'png', 'jpg', 'jpeg', 'gif', 'webp'}
        filename = secure_filename(file.filename)
        file_ext = filename.rsplit('.', 1)[1].lower() if '.' in filename else ''

        if file_ext not in allowed_extensions:
            return jsonify(Status.ParamsError.ToResponse("不支持的图片格式"))

        # 验证MIME类型
        mime_type = file.mimetype
        if not mime_type or not mime_type.startswith('image/'):
            return jsonify(Status.ParamsError.ToResponse("文件类型错误"))

        # 读取文件数据
        file_data = file.read()
        file_size = len(file_data)

        # 验证文件大小 (最大5MB)
        max_size = 5 * 1024 * 1024
        if file_size > max_size:
            return jsonify(Status.ParamsError.ToResponse("图片大小不能超过5MB"))

        # 获取图片尺寸
        try:
            from PIL import Image
            img = Image.open(io.BytesIO(file_data))
            width, height = img.size
        except Exception as e:
            print(f"图片解析失败: {e}")
            return jsonify(Status.ParamsError.ToResponse("图片文件损坏"))

        # 压缩图片数据
        compressed_data, compression_ratio = compress_image_data(file_data)

        # 生成图片名称
        image_name = f"avatar_{user_id}_{uuid.uuid4().hex[:8]}.{file_ext}"

        # 插入图片记录
        image_id, status = ImageInsert(
            connection,
            image_name=image_name,
            original_name=filename,
            mime_type=mime_type,
            file_size=file_size,
            width=width,
            height=height,
            compressed_data=compressed_data,
            compression_ratio=compression_ratio
        )

        if status != Status.OK:
            return jsonify(status.ToResponse("头像保存失败"))

        # 更新用户头像URL
        avatar_url = f"/User/Avatar/{user_id}"
        with connection.cursor() as cursor:
            cursor.execute(
                "UPDATE Users SET AvatarUrl = %s WHERE UserID = %s",
                (avatar_url, user_id)
            )
            connection.commit()

        response = Status.OK.ToResponse("头像上传成功")
        response['Data'] = {
            'AvatarUrl': avatar_url,
            'ImageID': image_id
        }
        return jsonify(response)

    except Exception as e:
        print(f"上传头像异常: {str(e)}")
        return jsonify(Status.ErrorRequest.ToResponse(str(e)))

@user_bp.route('/Avatar/<int:user_id>', methods=['GET'])
def get_avatar(user_id):
    """获取用户头像"""
    try:
        connection = get_db()
        if isinstance(connection, Status):
            return jsonify(connection.ToResponse())

        # 查询用户头像URL
        with connection.cursor() as cursor:
            cursor.execute("SELECT AvatarUrl FROM Users WHERE UserID = %s", (user_id,))
            user_result = cursor.fetchone()

            if not user_result or not user_result['AvatarUrl']:
                # 返回默认头像
                return jsonify({"Code": 201, "Msg": "用户未设置头像"})

        # 从头像URL中提取ImageID (如果URL格式是 /User/Avatar/{user_id})
        # 我们需要通过用户ID查找最新的头像记录
        with connection.cursor() as cursor:
            cursor.execute("""
                SELECT ImageID, MimeType, CompressedData
                FROM Images
                WHERE ImageName LIKE %s
                ORDER BY CreatedTime DESC
                LIMIT 1
            """, (f"avatar_{user_id}%",))
            image_result = cursor.fetchone()

            if not image_result:
                return jsonify({"Code": 201, "Msg": "头像不存在"})

            # 解压数据
            import zlib
            compressed_data = image_result['CompressedData']
            image_data = zlib.decompress(compressed_data)

            # 返回图片
            return Response(
                image_data,
                mimetype=image_result['MimeType'],
                headers={
                    'Cache-Control': 'public, max-age=86400'  # 缓存1天
                }
            )

    except Exception as e:
        print(f"获取头像异常: {str(e)}")
        return jsonify(Status.ErrorRequest.ToResponse(str(e)))