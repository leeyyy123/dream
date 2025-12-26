from flask import Flask
from flask_cors import CORS
from flask_jwt_extended import JWTManager
import os

# 导入蓝图
from blueprints.auth import auth_bp
from blueprints.user import user_bp
from blueprints.dream import dream_bp
from blueprints.analysis import analysis_bp
from blueprints.ai import ai_bp
from blueprints.admin import admin_bp
from sql.database import init_app

def create_app():
    """创建Flask应用"""
    app = Flask(__name__)

    # 配置
    app.config['JWT_SECRET_KEY'] = os.getenv('JWT_SECRET_KEY', 'your-secret-key-change-in-production')
    app.config['JWT_ACCESS_TOKEN_EXPIRES'] = False  # Token永不过期（生产环境建议设置过期时间）

    # 初始化CORS
    CORS(app, origins=['*'], methods=['GET', 'POST', 'PUT', 'DELETE', 'OPTIONS'])

    # 初始化JWT
    jwt = JWTManager(app)

    # 注册数据库初始化函数
    init_app(app)

    # 注册蓝图
    app.register_blueprint(auth_bp)
    app.register_blueprint(user_bp)
    app.register_blueprint(dream_bp)
    app.register_blueprint(analysis_bp)
    app.register_blueprint(ai_bp)
    app.register_blueprint(admin_bp)

    # 创建一个简单的检查JWT Token的端点
    @app.route('/CheckJWTToken', methods=['GET'])
    def check_jwt_token():
        """检查JWT Token是否有效"""
        from flask_jwt_extended import get_jwt_identity, verify_jwt_in_request

        try:
            verify_jwt_in_request()
            current_user = get_jwt_identity()
            return {
                "Code": 200,
                "Msg": "Token有效",
                "User": current_user
            }
        except Exception as e:
            return {
                "Code": 401,
                "Msg": "Token无效或已过期"
            }

    # 健康检查端点
    @app.route('/health', methods=['GET'])
    def health_check():
        """健康检查"""
        return {
            "status": "healthy",
            "service": "Dream Backend",
            "version": "1.0.0"
        }

    # 全局错误处理
    @app.errorhandler(404)
    def not_found(error):
        return {
            "Code": 404,
            "Msg": "接口不存在"
        }, 404

    @app.errorhandler(500)
    def internal_error(error):
        return {
            "Code": 500,
            "Msg": "服务器内部错误"
        }, 500

    return app

# 创建应用实例
app = create_app()

if __name__ == '__main__':
    # 开发环境配置
    debug_mode = os.getenv('FLASK_DEBUG', 'True').lower() == 'true'
    port = int(os.getenv('PORT', 8888))
    host = os.getenv('HOST', '0.0.0.0')

    print(f"Dream Backend Server Starting...")
    print(f"Server: http://{host}:{port}")
    print(f"Debug Mode: {debug_mode}")
    print(f"Email Service: {'yes' if os.getenv('EMAIL_PASSWORD') else 'no, Need to configure'}")

    app.run(
        host=host,
        port=port,
        debug=debug_mode
    )