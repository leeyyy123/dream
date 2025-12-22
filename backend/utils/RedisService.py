import redis
import random
import time
from utils.status import Status

printdebug = True

# Redis配置
REDIS_CONFIG = {
    'host': 'localhost',
    'port': 6379,
    'db': 0,
    'decode_responses': True
}

def get_redis_connection():
    """获取Redis连接"""
    try:
        r = redis.Redis(**REDIS_CONFIG)
        r.ping()  # 测试连接
        return r, Status.OK
    except Exception as e:
        if printdebug:
            print(f"Redis连接失败: {e}")
        return None, Status.RedisConnectionError

def redis_set_key(email: str, expire_time: int = 300):
    """设置验证码，默认5分钟过期"""
    try:
        redis_conn, status = get_redis_connection()
        if status != Status.OK:
            return status, None

        # 生成6位随机验证码
        verify_code = str(random.randint(100000, 999999))

        # 存储验证码到Redis，设置过期时间
        key = f"dream_verify_code:{email}"
        redis_conn.setex(key, expire_time, verify_code)

        if printdebug:
            print(f"验证码已设置: {email} -> {verify_code}")

        return Status.OK, verify_code
    except Exception as e:
        if printdebug:
            print(f"Redis设置失败: {e}")
        return Status.RedisOperationError, None

def redis_verify_code(email: str, input_code: str):
    """验证验证码"""
    try:
        redis_conn, status = get_redis_connection()
        if status != Status.OK:
            return status

        key = f"dream_verify_code:{email}"
        stored_code = redis_conn.get(key)

        if stored_code is None:
            return Status.SigninVerifyCodeExpired

        if stored_code != input_code:
            return Status.SigninVerifyCodeError

        return Status.OK
    except Exception as e:
        if printdebug:
            print(f"Redis验证失败: {e}")
        return Status.RedisOperationError

def delete_verification_code(email: str):
    """删除验证码"""
    try:
        redis_conn, status = get_redis_connection()
        if status != Status.OK:
            return status

        key = f"dream_verify_code:{email}"
        redis_conn.delete(key)

        if printdebug:
            print(f"验证码已删除: {email}")

        return Status.OK
    except Exception as e:
        if printdebug:
            print(f"Redis删除失败: {e}")
        return Status.RedisOperationError