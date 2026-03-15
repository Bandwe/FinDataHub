# FinDataHub - 财务数据管理平台

一个基于 Web 的上市公司财务数据管理平台，支持多维度财务数据的增删改查、Excel 导入导出、可视化分析等功能。

## 功能特性

- **8个数据模块**：毛利率与净利率、扣非净利润增长、ROE与净资产、PE估值、股东结构、股东户数、研发投入、研发团队
- **数据管理**：支持手动录入、编辑、删除财务数据
- **Excel 导入导出**：支持模板下载、数据批量导入、导出
- **数据查询**：支持关键词搜索、年份筛选、指标范围筛选
- **数据可视化**：集成 ECharts 图表，支持折线图、柱状图展示
- **公司管理**：统一管理上市公司基础信息

## 技术栈

### 后端
- Python 3.9+
- Flask 3.0
- SQLAlchemy (ORM)
- MySQL 8.0
- Pandas (Excel处理)

### 前端
- Vue 3
- Element Plus (UI组件库)
- ECharts (图表)
- Axios (HTTP请求)
- Vite (构建工具)

## 项目结构

```
FinDataHub/
├── backend/                 # 后端代码
│   ├── app.py              # Flask应用入口
│   ├── config.py           # 配置文件
│   ├── models.py           # 数据模型
│   ├── requirements.txt    # Python依赖
│   ├── api/                # API路由
│   │   ├── companies.py
│   │   ├── profit_rate.py
│   │   ├── non_recurring.py
│   │   ├── roe_net_asset.py
│   │   ├── pe_valuation.py
│   │   ├── shareholder_structure.py
│   │   ├── shareholder_count.py
│   │   ├── rd_expense.py
│   │   ├── rd_staff.py
│   │   └── templates.py
│   └── utils/              # 工具函数
│       └── excel_parser.py
├── frontend/               # 前端代码
│   ├── src/
│   │   ├── api/           # API请求
│   │   ├── views/         # 页面组件
│   │   ├── router/        # 路由配置
│   │   ├── App.vue
│   │   └── main.js
│   ├── package.json
│   └── vite.config.js
└── database/
    └── init.sql           # 数据库初始化脚本
```

## 快速开始

### 1. 环境要求

- Python 3.9+
- Node.js 16+
- MySQL 8.0

### 2. 数据库配置

```bash
# 登录MySQL
mysql -u root -p

# 执行初始化脚本
source database/init.sql
```

### 3. 后端启动

```bash
cd backend

# 创建虚拟环境
python -m venv venv

# 激活虚拟环境
# Windows:
venv\Scripts\activate
# macOS/Linux:
source venv/bin/activate

# 安装依赖
pip install -r requirements.txt

# 配置数据库连接（可选，默认使用本地MySQL）
export DB_HOST=localhost
export DB_PORT=3306
export DB_USER=root
export DB_PASSWORD=your_password
export DB_NAME=findata

# 启动服务
python run.py
```

后端服务默认运行在 http://127.0.0.1:5000

### 4. 前端启动

```bash
cd frontend

# 安装依赖
npm install

# 启动开发服务器
npm run dev
```

前端服务默认运行在 http://127.0.0.1:5173

### 5. 访问应用

打开浏览器访问 http://127.0.0.1:5173

## 默认数据

系统初始化时自动创建以下示例公司：
- 长电科技 (600584)
- 华天科技 (002185)
- 通富微电 (002156)
- 中芯国际 (688981)
- 北方华创 (002371)

## API 文档

### 公司管理
- `GET /api/companies` - 获取公司列表
- `POST /api/companies` - 新增公司
- `PUT /api/companies/<id>` - 更新公司
- `DELETE /api/companies/<id>` - 删除公司

### 数据模块
各模块API格式类似，以利润率模块为例：
- `GET /api/profit_rate` - 获取数据列表
- `POST /api/profit_rate` - 新增记录
- `PUT /api/profit_rate/<id>` - 更新记录
- `DELETE /api/profit_rate/<id>` - 删除记录
- `POST /api/profit_rate/import` - 导入Excel
- `GET /api/profit_rate/export` - 导出Excel

### 模板下载
- `GET /api/templates/<module_name>` - 下载导入模板

支持的模块名：profit_rate, non_recurring, roe_net_asset, pe_valuation, shareholder_structure, shareholder_count, rd_expense, rd_staff

## 开发说明

### 添加新模块

1. 后端：
   - 在 `models.py` 中定义数据模型
   - 在 `api/` 目录下创建新的API文件
   - 在 `api/__init__.py` 中导入新模块

2. 前端：
   - 在 `src/views/` 创建新的视图组件
   - 在 `src/router/index.js` 添加路由
   - 在 `src/api/` 添加API请求函数（可选）

### 数据库迁移

使用 Flask-SQLAlchemy 自动创建表：

```python
from app import app
from models import db

with app.app_context():
    db.create_all()
```

## 生产部署

### 后端部署

1. 使用 Gunicorn 作为WSGI服务器：
```bash
gunicorn -w 4 -b 0.0.0.0:5000 app:app
```

2. 使用 Nginx 反向代理

### 前端部署

```bash
cd frontend
npm run build
```

将 `dist` 目录部署到Web服务器

## 许可证

MIT License

## 联系方式

如有问题或建议，欢迎提交 Issue 或 Pull Request。
