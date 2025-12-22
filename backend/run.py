#!/usr/bin/env python3
"""
Dream Backend 启动脚本
"""

import os
import sys
from dotenv import load_dotenv

# 加载环境变量
load_dotenv()

# 添加项目根目录到Python路径
current_dir = os.path.dirname(os.path.abspath(__file__))
parent_dir = os.path.dirname(current_dir)
sys.path.insert(0, parent_dir)

if __name__ == '__main__':
    from backend.app import app

    # 开发环境配置
    debug_mode = os.getenv('FLASK_DEBUG', 'True').lower() == 'true'
    port = int(os.getenv('PORT', 8888))
    host = os.getenv('HOST', '0.0.0.0')

    print("🌙 Dream 记梦 - 后端服务")
    print("=" * 50)
    print(f"🚀 启动服务器: http://{host}:{port}")
    print(f"🔧 调试模式: {'开启' if debug_mode else '关闭'}")

    # 检查配置
    email_configured = bool(os.getenv('EMAIL_PASSWORD') and os.getenv('EMAIL_PASSWORD') != 'your_qq_authorization_code')
    print(f"📧 邮件服务: {'✅ 已配置' if email_configured else '❌ 未配置'}")

    db_configured = bool(os.getenv('DB_PASSWORD'))
    print(f"🗄️ 数据库: {'✅ 已配置' if db_configured else '❌ 未配置'}")

    print("=" * 50)
    print("📋 API端点:")
    print("  POST /Auth/Login - 用户登录")
    print("  POST /Auth/Sign - 发送注册验证码")
    print("  POST /Auth/Verify - 验证注册")
    print("  POST /Auth/ResetPassword - 发送重置密码验证码")
    print("  POST /Auth/UpdatePassword - 更新密码")
    print("  GET  /CheckJWTToken - 检查Token有效性")
    print("  GET  /health - 健康检查")
    print("=" * 50)
    print("💡 提示: 请确保MySQL和Redis服务已启动")
    print()

    try:
        app.run(
            host=host,
            port=port,
            debug=debug_mode
        )
    except KeyboardInterrupt:
        print("\n👋 服务器已停止")
    except Exception as e:
        print(f"\n❌ 启动失败: {e}")
        sys.exit(1)