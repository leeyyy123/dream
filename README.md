# 梦境记录与分析系统 (Dream Journal & Analysis System)

一个基于 Vue 3 + Flask 的全栈梦境记录与智能分析Web应用，帮助用户记录、管理和分析自己的梦境，通过AI智能分析发现梦境模式和心理状态。

## 项目简介

本系统是一个完整的梦境管理平台，集成了AI智能分析、数据可视化、用户管理等功能。用户可以方便地记录梦境内容，通过AI获取关键词提取和深度分析，查看统计图表了解梦境模式，管理员可以管理平台内容和查看系统日志。

## 核心功能

### 梦境管理
- **梦境记录**: 创建、编辑、删除梦境，支持富文本内容输入
- **详细信息**: 记录梦境标题、内容、日期、睡眠质量（1-5星）、梦境清晰度（1-5星）
- **情绪标注**: 支持10种预定义情绪标签（快乐、焦虑、恐惧、愤怒、悲伤等）
- **类型分类**: 支持15种预定义梦境类型（噩梦、清醒梦、飞行梦、追逐梦等）
- **关键词管理**: AI自动提取关键词，支持手动添加和编辑
- **隐私控制**: 每个梦境可设置为公开或私密

### AI智能分析
- **关键词提取**: 自动识别梦中的人物、地点、物品、事件、象征符号
- **情绪识别**: AI智能分析梦境中的情绪，提供情绪分布
- **类型判断**: 自动判断梦境类型（噩梦、清醒梦、预知梦等）
- **深度分析**: 从心理学角度提供梦境解读，包含象征解读、情绪分析、生活关联、积极启示
- **AI对话助手**: 提供专业的心理咨询风格对话，解答梦境相关问题
- **多梦总结**: 批量分析多个梦境，发现梦境模式和趋势

### 数据可视化
- **词云图**: 展示梦境中出现频率最高的关键词
- **情绪分布**: 饼图展示各类情绪的占比
- **类型分布**: 展示不同梦境类型的分布情况
- **月度趋势**: 折线图展示每月梦境记录数量
- **睡眠质量**: 统计睡眠质量和清晰度的分布

### 用户管理
- **用户注册**: 支持邮箱注册，密码SHA256加密存储
- **安全登录**: JWT令牌认证，支持普通用户和管理员双模式
- **个人资料**: 完善的个人信息管理（用户名、邮箱、性别、生日、手机、地址等）
- **资料编辑**: 支持修改个人信息和密码
- **头像设置**: 个性化头像上传和显示

### 管理员功能
- **系统日志**: 查看所有用户操作日志（登录、注册、创建梦境等）
- **内容管理**: 查看和管理所有公开梦境
- **配置管理**: 添加/删除自定义情绪和梦境类型
- **日志清理**: 批量清理指定天数前的历史日志
- **数据统计**: 查看平台整体数据统计

## 技术架构

### 前端技术栈
```
frontend/
├── Vue 3 (Composition API)     # 渐进式JavaScript框架
├── Vite                        # 现代前端构建工具
├── Vue Router 4                # 官方路由管理器
├── Element Plus                # 企业级UI组件库
├── ECharts                     # 数据可视化图表库
├── ECharts-WordCloud           # 词云图插件
├── Axios                       # HTTP客户端
└── Tailwind CSS                # 实用优先的CSS框架
```

### 后端技术栈
```
backend/
├── Flask                       # Python Web框架
├── Flask-JWT-Extended          # JWT令牌认证
├── Flask-CORS                  # 跨域资源共享
├── PyMySQL                     # MySQL数据库驱动
├── Redis                       # 内存数据库（缓存）
├── 智谱AI GLM-4                # AI分析服务
└── Blueprint                   # 模块化应用架构
```

## 项目结构

```
dream/                                   # 项目根目录
├── frontend/                            # 前端应用 (Vue 3 + Vite)
│   ├── public/
│   │   └── index.html                   # HTML入口文件
│   ├── src/
│   │   ├── App.vue                      # 根组件
│   │   ├── main.js                      # 应用入口文件
│   │   ├── views/                       # 页面组件
│   │   │   ├── LoginView.vue            # 登录/注册页面
│   │   │   ├── HomeView.vue             # 主页
│   │   │   ├── CreateDreamView.vue      # 创建/编辑梦境页面
│   │   │   ├── MyDreamsView.vue         # 我的梦境列表页面
│   │   │   ├── DreamAnalysisView.vue    # 梦境分析页面
│   │   │   ├── ProfileView.vue          # 个人资料页面
│   │   │   ├── AIChatView.vue           # AI对话页面
│   │   │   ├── AdminLoginView.vue       # 管理员登录页面
│   │   │   └── AdminDashboardView.vue   # 管理员面板
│   │   ├── router/
│   │   │   └── index.js                 # 路由配置
│   │   ├── services/
│   │   │   └── api.js                   # API服务封装
│   │   └── assets/                      # 静态资源
│   ├── package.json                     # 前端依赖配置
│   └── vite.config.js                   # Vite构建配置
│
├── backend/                             # 后端服务 (Flask)
│   ├── app.py                           # Flask应用入口
│   ├── run.py                           # 应用启动脚本
│   ├── blueprints/                      # Flask蓝图模块
│   │   ├── auth.py                      # 用户认证蓝图
│   │   ├── user.py                      # 用户管理蓝图
│   │   ├── dream.py                     # 梦境管理蓝图
│   │   ├── analysis.py                  # 分析功能蓝图
│   │   ├── ai.py                        # AI服务蓝图
│   │   └── admin.py                     # 管理员蓝图
│   ├── sql/                             # 数据库操作层
│   │   ├── database.py                  # 数据库连接管理
│   │   ├── ddl.sql                      # 数据库表结构定义
│   │   ├── UserSql.py                   # 用户数据操作
│   │   ├── DreamSql.py                  # 梦境数据操作
│   │   ├── AnalysisSql.py               # 分析数据操作
│   │   ├── EmotionTypeSql.py            # 情绪类型操作
│   │   ├── LogSql.py                    # 日志数据操作
│   │   ├── StatisticsSql.py             # 统计数据操作
│   │   ├── ImageSql.py                  # 图片数据操作
│   │   └── init_emotions_types_data.py  # 初始化数据
│   ├── services/                        # 业务服务层
│   │   └── AIService.py                 # AI服务封装（智谱AI）
│   ├── utils/                           # 工具类
│   │   ├── Objects.py                   # 数据对象定义
│   │   ├── status.py                    # 状态码定义
│   │   └── RedisService.py              # Redis服务
│   ├── requirements.txt                 # Python依赖包列表
│   └── .env                             # 环境变量配置
│
├── 系统功能编写过程.md                   # 系统开发文档
├── 系统测试用例.md                       # 测试用例文档
└── README.md                             # 项目说明文档
```

## 数据库设计

### 核心数据表
- **Users**: 用户表（邮箱、密码、用户名、个人信息）
- **Dreams**: 梦境主表（标题、内容、日期、睡眠质量、清晰度、隐私设置）
- **Keywords**: 关键词表（关键词文本、分类、权重）
- **Emotions**: 情绪表（情绪名称、颜色标识）
- **DreamTypes**: 梦境类型表（类型名称、颜色标识）
- **DreamEmotions**: 梦境-情绪关联表
- **DreamTypesRelation**: 梦境-类型关联表
- **Analyses**: 分析报告表
- **Logs**: 系统日志表
- **AIChats**: AI对话历史表

## 快速开始

### 环境要求
- Node.js 16.0+
- Python 3.8+
- MySQL 8.0+
- Redis 6.0+ (可选，用于验证码)

### 安装步骤

#### 1. 克隆项目
```bash
git clone <repository-url>
cd dream
```

#### 2. 后端设置
```bash
# 进入后端目录
cd backend

# 创建虚拟环境
python -m venv venv

# 激活虚拟环境
# Windows
venv\Scripts\activate
# Linux/Mac
source venv/bin/activate

# 安装依赖
pip install -r requirements.txt

# 配置环境变量
# 复制 .env.example 并修改配置
cp .env.example .env
```

编辑 `.env` 文件，配置数据库连接信息：
```env
DB_HOST=localhost
DB_USER=root
DB_PASSWORD=your_password
DB_NAME=dream_db
ZHIPU_API_KEY=your_zhipu_api_key  # 智谱AI密钥
JWT_SECRET_KEY=your_secret_key
```

#### 3. 数据库初始化
```bash
# 登录MySQL
mysql -u root -p

# 创建数据库
CREATE DATABASE dream_db CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci;

# 导入表结构
USE dream_db;
source backend/sql/ddl.sql;

# 初始化情绪和类型数据
# 在Python中运行
python backend/sql/init_emotions_types_data.py
```

#### 4. 启动后端服务
```bash
cd backend
python run.py
```

后端服务运行在: http://localhost:5000

#### 5. 前端设置
```bash
# 进入前端目录
cd frontend

# 安装依赖
npm install

# 启动开发服务器
npm run dev
```

前端服务运行在: http://localhost:5173

#### 6. 访问应用
- 前端应用: http://localhost:5173
- 后端API: http://localhost:5000/api

### 默认账号
- **超级管理员**: admin@dream.com / 123456
- **测试用户**: 请自行注册

## API文档

### 认证相关 (`/api/Auth`)
- `POST /api/Auth/Login` - 用户登录（支持普通用户和管理员）
- `POST /api/Auth/Sign` - 用户注册
- `POST /api/Auth/Verify` - 验证注册（需验证码）

### 用户管理 (`/api/User`)
- `GET /api/User/GetInfo` - 获取用户信息
- `PUT /api/User/UpdateInfo` - 更新用户信息
- `PUT /api/User/UpdatePassword` - 修改密码
- `GET /api/User/Statistics` - 获取用户统计数据
- `POST /api/User/UploadAvatar` - 上传头像

### 梦境管理 (`/api/Dream`)
- `POST /api/Dream/Create` - 创建梦境
- `GET /api/Dream/List` - 获取梦境列表（分页）
- `GET /api/Dream/Detail/{id}` - 获取梦境详情
- `PUT /api/Dream/Update/{id}` - 更新梦境
- `DELETE /api/Dream/Delete/{id}` - 删除梦境
- `GET /api/Dream/Emotions` - 获取情绪列表
- `GET /api/Dream/DreamTypes` - 获取梦境类型列表

### AI服务 (`/api/AI`)
- `POST /api/AI/ExtractKeywords` - 提取梦境关键词
- `POST /api/AI/Analyze` - 生成梦境分析报告
- `POST /api/AI/Chat` - AI对话
- `POST /api/AI/Summary` - 多梦总结分析

### 分析管理 (`/api/Analysis`)
- `GET /api/Analysis/Statistics` - 获取统计数据
- `POST /api/Analysis/Create` - 创建分析报告
- `GET /api/Analysis/List` - 获取分析列表
- `GET /api/Analysis/Detail/{id}` - 获取分析详情

### 管理员 (`/api/Admin`)
- `GET /api/Admin/Dreams` - 获取所有公开梦境
- `GET /api/Admin/Logs` - 获取系统日志
- `DELETE /api/Admin/Logs/Clear` - 清理历史日志
- `POST /api/Admin/Emotions` - 添加情绪类型
- `DELETE /api/Admin/Emotions/{id}` - 删除情绪类型
- `POST /api/Admin/DreamTypes` - 添加梦境类型
- `DELETE /api/Admin/DreamTypes/{id}` - 删除梦境类型

### 统一响应格式
```json
{
  "Code": 200,           # 状态码: 200成功, 400客户端错误, 500服务器错误
  "Msg": "success",      # 消息描述
  "Data": {}             # 响应数据
}
```

## 功能特色

### AI智能分析
- 集成智谱AI GLM-4模型
- 自动提取梦境关键词（人物、地点、物品、事件、象征）
- 智能识别梦境情绪和类型
- 生成专业的心理学分析报告
- 提供AI对话助手，支持梦境相关问题咨询

### 数据可视化
- 使用ECharts实现丰富的图表展示
- 词云图展示高频关键词
- 饼图展示情绪和类型分布
- 折线图展示梦境记录趋势
- 柱状图展示统计数据

### 用户体验
- 响应式设计，完美适配桌面和移动端
- 基于Element Plus的现代化UI设计
- 流畅的页面过渡和交互效果
- 完善的表单验证和错误提示
- 专业的配色方案和视觉设计

### 系统安全
- JWT令牌认证机制
- 密码SHA256加密存储
- 完善的权限控制（用户权限、管理员权限）
- 系统操作日志记录
- SQL注入防护

## 开发规范

### 前端开发
- 使用 Vue 3 Composition API
- 组件化开发思想
- 统一的API调用管理（services/api.js）
- 响应式CSS设计
- 统一的错误处理和加载状态

### 后端开发
- Flask蓝图模块化架构
- 统一响应格式
- 完善的数据验证和错误处理
- JWT令牌认证
- 数据库操作封装（SQL层）
- 系统日志记录

### 代码规范
- 遵循PEP 8 Python编码规范
- 使用ESLint进行代码检查
- 有意义的变量和函数命名
- 添加必要的注释和文档

## 部署说明

### 生产环境部署

#### 后端部署
```bash
# 使用Gunicorn部署
pip install gunicorn
gunicorn -w 4 -b 0.0.0.0:5000 app:app
```

#### 前端部署
```bash
# 构建生产版本
npm run build

# 部署dist目录到Web服务器
```

#### Nginx配置示例
```nginx
server {
    listen 80;
    server_name your-domain.com;

    # 前端静态文件
    location / {
        root /path/to/frontend/dist;
        try_files $uri $uri/ /index.html;
    }

    # 后端API代理
    location /api {
        proxy_pass http://localhost:5000;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
    }
}
```

## 常见问题

### Q: 前端无法连接后端API？
A:
1. 检查后端服务是否正常运行
2. 检查 `frontend/src/services/api.js` 中的 API_BASE_URL 配置
3. 确认后端CORS配置正确
4. 查看浏览器控制台的网络请求错误信息

### Q: 数据库连接失败？
A:
1. 确认MySQL服务正常运行
2. 检查 `.env` 文件中的数据库配置
3. 确认数据库已创建（`dream_db`）
4. 检查数据库用户权限

### Q: AI功能无法使用？
A:
1. 确认已在 `.env` 中配置 `ZHIPU_API_KEY`
2. 检查智谱AI API密钥是否有效
3. 确认网络连接正常
4. 查看后端日志中的AI服务错误信息

### Q: 关键词提取返回空结果？
A:
1. 确保梦境内容至少10个字符
2. 检查AI服务是否正常
3. 尝试重新提取关键词

### Q: 登录后提示未授权？
A:
1. 检查Token是否正确保存到localStorage
2. 确认Token格式正确（Bearer Token）
3. 检查JWT_SECRET_KEY配置
4. 查看浏览器控制台和后端日志

## 项目文档

- [系统功能编写过程.md](./系统功能编写过程.md) - 详细的系统开发文档
- [系统测试用例.md](./系统测试用例.md) - 完整的测试用例文档（168个测试用例）

## 开发路线图

### 已完成
- 用户认证系统（注册、登录、JWT）
- 梦境CRUD功能
- AI关键词提取
- AI梦境分析
- AI对话助手
- 数据可视化（词云、饼图、折线图）
- 用户个人资料管理
- 管理员后台
- 系统日志记录

### 计划中
- 邮箱验证码注册
- 密码找回功能
- 梦境导出（PDF/Excel）
- 多语言支持
- 移动端APP
- 梦境分享功能
- 社区交流功能
- 更多AI分析维度

## 贡献指南

欢迎贡献代码、报告问题或提出建议！

1. Fork 本仓库
2. 创建特性分支 (`git checkout -b feature/AmazingFeature`)
3. 提交更改 (`git commit -m 'Add some AmazingFeature'`)
4. 推送到分支 (`git push origin feature/AmazingFeature`)
5. 开启 Pull Request

### 提交规范
- feat: 新功能
- fix: 修复bug
- docs: 文档更新
- style: 代码格式调整
- refactor: 代码重构
- test: 测试相关
- chore: 构建/工具变动

## 许可证

本项目采用 MIT 许可证 - 查看 [LICENSE](LICENSE) 文件了解详情。

## 联系方式

如有问题或建议，请通过以下方式联系：

- Email: your-email@example.com
- Issues: [GitHub Issues](https://github.com/your-username/dream/issues)
- 项目文档: 查看项目根目录下的文档文件

## 致谢

- Vue.js - 渐进式JavaScript框架
- Flask - Python Web框架
- Element Plus - Vue 3 UI组件库
- ECharts - 数据可视化图表库
- 智谱AI - AI分析服务支持

---

开始记录你的梦境之旅，探索内心的奥秘！
