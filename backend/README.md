# Dream 记梦 - 后端服务

基于 Flask 的用户认证后端服务，支持用户登录、注册、密码重置等功能。

## 功能特性

- 🔐 **用户认证** - 登录、注册、密码重置
- 📧 **邮件验证** - 基于SMTP的邮箱验证码
- 🔑 **JWT Token** - 安全的用户身份验证
- 🗄️ **数据库支持** - MySQL数据存储
- 💾 **缓存服务** - Redis验证码存储
- 🛡️ **安全加密** - SM3密码加密

## 环境要求

- Python 3.8+
- MySQL 5.7+
- Redis 6.0+

## 安装配置

### 1. 安装依赖

```bash
cd dream/backend
pip install -r requirements.txt
```

### 2. 配置环境变量

```bash
# 复制配置文件模板
cp .env.example .env

# 编辑配置文件
nano .env
```

配置说明：

```env
# 数据库配置
DB_HOST=localhost
DB_PORT=3306
DB_USER=root
DB_PASSWORD=your_mysql_password
DB_NAME=dream

# JWT配置
JWT_SECRET_KEY=your-secret-key-change-in-production

# 邮件配置 (使用QQ邮箱示例)
EMAIL_SENDER=your_email@qq.com
EMAIL_PASSWORD=your_qq_authorization_code  # QQ邮箱授权码
EMAIL_SMTP_SERVER=smtp.qq.com
EMAIL_SMTP_PORT=465

# 服务器配置
FLASK_DEBUG=True
HOST=0.0.0.0
PORT=8888
```

### 3. 数据库初始化

确保MySQL服务已启动，然后执行DDL脚本：

```sql
mysql -u root -p
source backend/sql/ddl.sql
```

### 4. 启动服务

```bash
# 方式1: 使用启动脚本
python run.py

# 方式2: 直接启动
python app.py
```

服务将在 `http://localhost:8888` 启动

## API 接口

### 用户认证相关

#### 1. 用户登录
```
POST /Auth/Login
Content-Type: application/json

{
  "Email": "user@example.com",
  "Password": "sm3_encrypted_password"
}
```

#### 2. 发送注册验证码
```
POST /Auth/Sign
Content-Type: application/json

{
  "Name": "用户名",
  "Email": "user@example.com",
  "Password": "sm3_encrypted_password"
}
```

#### 3. 验证注册
```
POST /Auth/Verify
Content-Type: application/json

{
  "Name": "用户名",
  "Email": "user@example.com",
  "Password": "sm3_encrypted_password",
  "VerifyCode": "123456"
}
```

#### 4. 发送重置密码验证码
```
POST /Auth/ResetPassword
Content-Type: application/json

{
  "Email": "user@example.com"
}
```

#### 5. 更新密码
```
POST /Auth/UpdatePassword
Content-Type: application/json

{
  "Email": "user@example.com",
  "Password": "new_sm3_encrypted_password",
  "VerifyCode": "123456"
}
```

#### 6. 检查Token有效性
```
GET /CheckJWTToken
Authorization: Bearer your_jwt_token
```

#### 7. 健康检查
```
GET /health
```

## 响应格式

所有API响应都遵循统一格式：

```json
{
  "Code": 200,
  "Msg": "成功",
  "Token": "jwt_token",  // 仅登录接口返回
  "UserID": 123          // 仅登录接口返回
}
```

### 状态码说明

- `200` - 成功
- `201` - 结果为空
- `202` - 超级管理员登录
- `401` - 认证失败
- `501` - 登录失败
- `502` - 用户已存在
- `503` - 用户不存在
- `510` - 数据库连接错误
- `518` - 邮件发送失败
- `520` - 验证码错误
- `521` - 验证码过期

## 邮件配置说明

### QQ邮箱配置

1. 登录QQ邮箱
2. 设置 -> 账户 -> POP3/IMAP/SMTP/Exchange/CardDAV/CalDAV服务
3. 开启"IMAP/SMTP服务"
4. 获取授权码
5. 将授权码填入 `EMAIL_PASSWORD` 配置项

### 其他邮箱

参考对应邮箱的SMTP配置，修改 `SMTP_CONFIG` 中的服务器地址和端口。

## 安全配置

1. **密码加密**: 使用SM3算法加密密码存储
2. **JWT Token**: 配置强密钥的 `JWT_SECRET_KEY`
3. **数据库**: 使用强密码和适当的用户权限
4. **邮件**: 使用授权码而非明文密码

## 开发调试

开启调试模式：
```bash
export FLASK_DEBUG=True
python run.py
```

查看详细日志：
```bash
export FLASK_DEBUG=True
python run.py 2>&1 | tee debug.log
```

## 部署说明

生产环境配置建议：

1. 使用强密码和安全的JWT密钥
2. 关闭调试模式 `FLASK_DEBUG=False`
3. 使用 HTTPS
4. 配置防火墙
5. 使用专业的WSGI服务器如 Gunicorn

## 故障排除

### 常见问题

1. **数据库连接失败**
   - 检查MySQL服务是否启动
   - 检查数据库配置是否正确
   - 检查用户权限

2. **Redis连接失败**
   - 检查Redis服务是否启动
   - 检查Redis配置

3. **邮件发送失败**
   - 检查邮箱配置
   - 确认授权码正确
   - 检查网络连接

4. **Token验证失败**
   - 检查JWT_SECRET_KEY配置
   - 确认Token格式正确

## 技术栈

- **框架**: Flask 2.3.3
- **数据库**: MySQL + PyMySQL
- **缓存**: Redis
- **认证**: Flask-JWT-Extended
- **加密**: SM3
- **邮件**: SMTP

## 许可证

MIT License