# 🌙 梦境记录与分析系统 (Dream Journal & Analysis System)

一个基于 Vue 3 + Flask 的梦境记录与智能分析Web应用，帮助用户记录、管理和分析自己的梦境，通过数据可视化发现梦境模式和心理状态。

## ✨ 功能特性

### 📝 梦境管理
- **梦境记录**: 创建、编辑、删除梦境记录
- **详细信息**: 支持记录标题、内容、日期、睡眠质量、清晰度等
- **情绪标注**: 多种情绪标签（开心、悲伤、焦虑、兴奋等）
- **类型分类**: 丰富的梦境类型（噩梦、美梦、现实梦境、超现实梦境等）
- **搜索筛选**: 按日期、关键词、情绪、类型筛选梦境

### 📊 智能分析
- **数据统计**: 梦境数量、分析天数等基础统计
- **趋势图表**: 每日梦境数量折线图，展示梦境活跃度
- **情绪分析**: 情绪分布柱状图，了解情绪变化趋势
- **类型分析**: 梦境类型饼状图，发现梦境模式
- **睡眠质量**: 睡眠质量和梦境清晰度分布分析
- **历史记录**: 保存和查看历史分析报告

### 👤 用户管理
- **用户注册**: 支持邮箱注册和验证
- **安全登录**: JWT令牌认证
- **个人资料**: 完善的个人信息管理
- **头像上传**: 个性化头像设置
- **密码重置**: 安全的密码找回机制

### 🎨 用户体验
- **响应式设计**: 完美适配桌面端和移动端
- **现代UI**: 基于渐变色和卡片设计的精美界面
- **交互丰富**: 流畅的动画和用户友好的交互
- **主题统一**: 梦幻主题的色彩和设计风格

## 🏗️ 技术架构

### 前端技术栈
```
frontend/
├── Vue 3                    # 渐进式JavaScript框架
├── Vite                     # 现代前端构建工具
├── Vue Router               # 官方路由管理器
├── Composition API          # Vue 3组合式API
├── CSS3                     # 样式设计
└── JavaScript ES6+          # 现代JavaScript语法
```

### 后端技术栈
```
backend/
├── Flask                    # Python Web框架
├── Flask-Blueprints        # 模块化应用架构
├── Flask-CORS              # 跨域资源共享
├── MySQL                    # 关系型数据库
├── Redis                    # 内存数据库（缓存）
├── JWT                      # JSON Web令牌认证
└── SQLAlchemy              # Python ORM框架
```

## 📁 项目结构

```
dream/                              # 项目根目录
├── frontend/                       # 前端应用 (Vue 3 + Vite)
│   ├── public/
│   │   └── index.html              # HTML入口文件
│   ├── src/
│   │   ├── App.vue                 # 根组件
│   │   ├── main.js                 # 应用入口文件
│   │   ├── components/             # 公共组件 (未使用，功能内联在页面组件中)
│   │   ├── views/                  # 页面组件
│   │   │   ├── LoginView.vue       # 登录页面
│   │   │   ├── HomeView.vue        # 主页（导航+内容区域）
│   │   │   ├── CreateDreamView.vue # 创建梦境页面
│   │   │   ├── MyDreamsView.vue    # 梦境列表页面
│   │   │   ├── DreamAnalysisView.vue # 梦境分析页面
│   │   │   └── ProfileView.vue     # 个人信息页面
│   │   ├── services/               # API 服务
│   │   │   └── api.js              # 统一的API接口管理
│   │   ├── router/                 # 路由配置
│   │   │   └── index.js            # 路由定义和配置
│   │   └── assets/                 # 静态资源
│   ├── package.json                # 前端依赖配置
│   ├── vite.config.js              # Vite构建配置
│   └── README.md                   # 前端说明文档
│
├── backend/                        # 后端服务 (Flask + 蓝图)
│   ├── app.py                      # Flask应用入口
│   ├── run.py                      # 应用启动脚本
│   ├── blueprints/                 # Flask蓝图（模块化路由）
│   │   ├── __init__.py             # 蓝图初始化
│   │   ├── auth.py                 # 用户认证蓝图 (登录/注册/密码重置)
│   │   ├── user.py                 # 用户管理蓝图 (个人信息)
│   │   ├── dream.py                # 梦境管理蓝图 (CRUD操作)
│   │   └── analysis.py             # 分析功能蓝图 (梦境分析报告)
│   ├── sql/                        # 数据库操作层
│   │   ├── database.py             # 数据库连接管理
│   │   ├── mysql.py                # MySQL连接配置
│   │   ├── UserSql.py              # 用户数据操作
│   │   ├── DreamSql.py             # 梦境数据操作
│   │   ├── EmotionTypeSql.py       # 情绪类型数据操作
│   │   ├── AnalysisSql.py          # 分析数据操作
│   │   ├── LogSql.py               # 日志数据操作
│   │   ├── check_tables.py         # 数据库表检查
│   │   ├── init_emotions_types_data.py # 初始化情绪和类型数据
│   │   └── ddl.sql                 # 数据库表结构定义
│   ├── utils/                      # 工具类
│   │   ├── Objects.py              # 通用对象和工具函数
│   │   ├── RedisService.py         # Redis缓存服务
│   │   └── status.py               # 响应状态码定义
│   ├── .env                        # 环境变量配置（数据库连接等）
│   ├── .env.example                # 环境变量配置模板
│   ├── requirements.txt            # Python依赖包列表
│   └── README.md                   # 后端说明文档
│
└── README.md                       # 项目总体说明文档
```

## 🚀 快速开始

### 环境要求
- Node.js 16.0+
- Python 3.8+
- MySQL 8.0+
- Redis 6.0+

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
cp .env.example .env
# 编辑 .env 文件，配置数据库连接信息

# 初始化数据库
python sql/check_tables.py
python sql/init_emotions_types_data.py

# 启动后端服务
python run.py
```

#### 3. 前端设置
```bash
# 进入前端目录
cd frontend

# 安装依赖
npm install

# 启动开发服务器
npm run dev

# 或构建生产版本
npm run build
```

#### 4. 访问应用
- 前端开发服务器: http://localhost:5173
- 后端API服务: http://localhost:8888
- 应用主页: http://localhost:5173/main/home

## 📊 API文档

### 认证相关 (`/Auth`)
- `POST /Auth/Login` - 用户登录
- `POST /Auth/Sign` - 用户注册
- `POST /Auth/Verify` - 验证注册码
- `POST /Auth/ResetPassword` - 请求密码重置
- `POST /Auth/UpdatePassword` - 更新密码

### 用户管理 (`/User`)
- `GET /User/GetInfo` - 获取用户信息

### 梦境管理 (`/Dream`)
- `POST /Dream/Create` - 创建梦境
- `GET /Dream/GetList` - 获取梦境列表
- `GET /Dream/GetDetail/{id}` - 获取梦境详情
- `PUT /Dream/Update/{id}` - 更新梦境
- `DELETE /Dream/Delete/{id}` - 删除梦境
- `GET /Dream/GetEmotions` - 获取情绪列表
- `GET /Dream/GetDreamTypes` - 获取梦境类型列表

### 分析管理 (`/Analysis`)
- `POST /Analysis/Create` - 创建分析报告
- `GET /Analysis/GetList` - 获取分析列表
- `GET /Analysis/GetDetail/{id}` - 获取分析详情
- `DELETE /Analysis/Delete/{id}` - 删除分析

## 🎨 设计特色

### 视觉设计
- **梦幻主题**: 基于月光、梦境的柔和色彩
- **渐变背景**: `#FFFEF2 → #F5DEB3 → #FFDAB9` 温暖渐变
- **卡片设计**: 现代化的圆角卡片和阴影效果
- **统一色彩**: `#5D4E37`（深棕）、`#8B7355`（中棕）、`#C19A6B`（浅棕）

### 交互体验
- **流畅动画**: CSS3动画和过渡效果
- **响应式布局**: Grid和Flexbox实现的自适应布局
- **智能表单**: 表单验证和用户友好的错误提示
- **数据可视化**: SVG图表实现的数据展示

## 🔧 开发规范

### 前端开发
- 使用 **Vue 3 Composition API**
- 遵循 **组件化开发** 思想
- 统一的 **API调用** 管理
- 响应式的 **CSS设计**
- 统一的 **错误处理** 和 **加载状态**

### 后端开发
- **Flask蓝图** 模块化架构
- **统一响应格式**: `{Code: 200, Msg: "success", Data: {}}`
- **数据验证** 和 **错误处理**
- **JWT令牌** 认证机制
- **Redis缓存** 提升性能

## 🐛 常见问题

### Q: 前端无法连接后端API？
A: 检查后端服务是否启动，以及环境变量配置是否正确。

### Q: 数据库连接失败？
A: 确认MySQL服务运行正常，检查`.env`文件中的数据库配置。

### Q: 注册时收不到验证码？
A: 检查邮箱服务配置，或跳过验证码直接注册。

### Q: 梦境分析数据不准确？
A: 确保有足够的梦境数据，检查情绪和类型标签是否正确设置。

## 🤝 贡献指南

1. Fork 本仓库
2. 创建特性分支 (`git checkout -b feature/AmazingFeature`)
3. 提交更改 (`git commit -m 'Add some AmazingFeature'`)
4. 推送到分支 (`git push origin feature/AmazingFeature`)
5. 开启 Pull Request

## 📄 许可证

本项目采用 MIT 许可证 - 查看 [LICENSE](LICENSE) 文件了解详情。

## 👥 开发团队

- **前端开发**: Vue 3 + Vite
- **后端开发**: Flask + MySQL
- **UI/UX设计**: 响应式设计 + 数据可视化
- **数据库设计**: 关系型数据库 + 缓存系统

## 📞 联系方式

如有问题或建议，请通过以下方式联系：

- 📧 Email: your-email@example.com
- 🐛 Issues: [GitHub Issues](https://github.com/your-username/dream/issues)
- 📖 文档: [项目文档](https://your-docs-site.com)

---

**🌙 开始记录你的梦境之旅，探索内心的奥秘！**