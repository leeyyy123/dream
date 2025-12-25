import pymysql
import time
import hashlib
from utils.Objects import Users
from utils.status import Status
from datetime import datetime

printdebug = True

def UserCheckLogin(connection, email: str, password: str):
    """检查用户登录"""
    try:
        # 对密码进行SHA-256哈希
        password_hash = hashlib.sha256(password.encode()).hexdigest()

        with connection.cursor() as cursor:
            # 查询用户是否存在且密码匹配
            sql_select = "SELECT UserID FROM Users WHERE Email=%s AND Password=%s LIMIT 1"
            params_select = (email, password_hash)
            cursor.execute(sql_select, params_select)
            user = cursor.fetchone()

            if not user:
                if printdebug:
                    print(f"登录失败: 用户不存在或密码错误 - {email}")
                return Status.LoginFailed, None

            # 登录成功，更新最后登录时间
            user_id = user['UserID']
            current_time = datetime.now()

            sql_update = "UPDATE Users SET LastLogin=%s WHERE UserID=%s"
            params_update = (current_time, user_id)
            cursor.execute(sql_update, params_update)
            connection.commit()

            if printdebug:
                print(f"登录成功: 用户ID={user_id}, 邮箱={email}")

            return Status.OK, user_id

    except pymysql.Error as e:
        if printdebug:
            print(f"用户登录数据库错误: {e}")
        connection.rollback()
        return Status.DatabaseSelectError, None
    except Exception as e:
        if printdebug:
            print(f"用户登录异常: {e}")
        return Status.DatabaseSelectError, None

def UserCheckEmailExists(connection, email: str):
    """检查邮箱是否已存在"""
    try:
        with connection.cursor() as cursor:
            sql_select = "SELECT UserID FROM Users WHERE Email=%s LIMIT 1"
            params = (email,)
            cursor.execute(sql_select, params)
            user = cursor.fetchone()

            if not user:
                # 用户不存在，可以注册
                return Status.OK
            else:
                # 用户已存在
                return Status.UserExist

    except pymysql.Error as e:
        if printdebug:
            print(f"检查邮箱存在性数据库错误: {e}")
        return Status.DatabaseSelectError
    except Exception as e:
        if printdebug:
            print(f"检查邮箱存在性异常: {e}")
        return Status.DatabaseSelectError

def UserInsert(connection, user: Users, max_retries: int = 3):
    """插入新用户"""
    retries = 0
    if printdebug:
        print(f"开始用户数据插入: {user.Email}")

    while retries < max_retries:
        try:
            # 对密码进行SHA-256哈希
            password_hash = hashlib.sha256(user.Password.encode()).hexdigest()

            with connection.cursor() as cursor:
                sql = """
                    INSERT INTO Users (UserName, Email, Password, RegisterTime)
                    VALUES (%s, %s, %s, %s)
                """
                params = (
                    user.Name,
                    user.Email,
                    password_hash,
                    datetime.now()
                )

                cursor.execute(sql, params)
                connection.commit()

                if printdebug:
                    print(f"用户插入成功: {user.Email}")
                return Status.OK

        except pymysql.Error as e:
            retries += 1
            if printdebug:
                print(f"用户数据插入失败 (第{retries}次尝试): {e}")
            connection.rollback()

            if retries < max_retries:
                time.sleep(1)  # 等待1秒后重试

    return Status.DatabaseInsertError

def UserGetInfo(connection, email: str):
    """获取用户信息"""
    try:
        with connection.cursor() as cursor:
            sql_select = """
                SELECT UserID, UserName, Email, AvatarUrl, Gender, BirthDate, Phone, Address, RegisterTime, LastLogin
                FROM Users
                WHERE Email=%s
                LIMIT 1
            """
            params = (email,)
            cursor.execute(sql_select, params)
            user = cursor.fetchone()

            if not user:
                return None, Status.UserUnexist

            # 转换datetime为字符串
            user_dict = {
                "UserID": user['UserID'],
                "UserName": user['UserName'],
                "Email": user['Email'],
                "AvatarUrl": user['AvatarUrl'],
                "Gender": user['Gender'],
                "BirthDate": user['BirthDate'].isoformat() if user['BirthDate'] else None,
                "Phone": user['Phone'],
                "Address": user['Address'],
                "RegisterTime": user['RegisterTime'].isoformat() if user['RegisterTime'] else None,
                "LastLogin": user['LastLogin'].isoformat() if user['LastLogin'] else None,
                "Role": "user"
            }

            if printdebug:
                print(f"用户信息获取成功: {email}")
            return user_dict, Status.OK

    except pymysql.Error as e:
        if printdebug:
            print(f"用户信息查询数据库错误: {e}")
        return None, Status.DatabaseSelectError
    except Exception as e:
        if printdebug:
            print(f"用户信息查询异常: {e}")
        return None, Status.DatabaseSelectError

def UpdateUserPassword(connection, user_email: str, new_password: str):
    """更新用户密码"""
    try:
        with connection.cursor() as cursor:
            sql_update = "UPDATE Users SET Password=%s WHERE Email=%s"
            params_update = (new_password, user_email)
            cursor.execute(sql_update, params_update)
            connection.commit()

            if printdebug:
                print(f"密码更新成功: {user_email}")
            return Status.OK

    except pymysql.Error as e:
        if printdebug:
            print(f"用户密码更新失败: {e}")
        connection.rollback()
        return Status.DatabaseUpdateError
    except Exception as e:
        if printdebug:
            print(f"用户密码更新异常: {e}")
        return Status.DatabaseUpdateError

def UpdateUserInfo(connection, user_id: int, user_info: dict):
    """更新用户个人信息

    Args:
        connection: 数据库连接
        user_id: 用户ID
        user_info: 用户信息字典，可包含:
                   - userName: 用户名
                   - gender: 性别 (M/F/O)
                   - birthDate: 出生日期
                   - phone: 手机号
                   - address: 地址
    """
    try:
        with connection.cursor() as cursor:
            # 构建动态UPDATE语句
            update_fields = []
            params = []

            if 'userName' in user_info and user_info['userName']:
                update_fields.append("UserName = %s")
                params.append(user_info['userName'])

            if 'gender' in user_info and user_info['gender']:
                update_fields.append("Gender = %s")
                params.append(user_info['gender'])

            if 'birthDate' in user_info:
                if user_info['birthDate']:
                    update_fields.append("BirthDate = %s")
                    params.append(user_info['birthDate'])
                else:
                    update_fields.append("BirthDate = NULL")

            if 'phone' in user_info:
                if user_info['phone']:
                    update_fields.append("Phone = %s")
                    params.append(user_info['phone'])
                else:
                    update_fields.append("Phone = NULL")

            if 'address' in user_info:
                if user_info['address']:
                    update_fields.append("Address = %s")
                    params.append(user_info['address'])
                else:
                    update_fields.append("Address = NULL")

            if not update_fields:
                return Status.ParamsError

            # 添加user_id到参数
            params.append(user_id)

            sql = f"UPDATE Users SET {', '.join(update_fields)} WHERE UserID = %s"
            cursor.execute(sql, params)
            connection.commit()

            if printdebug:
                print(f"用户信息更新成功: 用户ID={user_id}, 更新字段={update_fields}")

            return Status.OK

    except pymysql.Error as e:
        if printdebug:
            print(f"用户信息更新数据库错误: {e}")
        connection.rollback()
        return Status.DatabaseUpdateError
    except Exception as e:
        if printdebug:
            print(f"用户信息更新异常: {e}")
        return Status.DatabaseUpdateError