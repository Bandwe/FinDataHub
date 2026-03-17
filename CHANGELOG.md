# Changelog

所有重要的变更都将记录在此文件中。

格式基于 [Keep a Changelog](https://keepachangelog.com/zh-CN/1.0.0/)，
并且本项目遵循 [语义化版本](https://semver.org/lang/zh-CN/)。

---

## [1.0.0] - 2026-03-18

### 🎉 首次正式发布

FinDataHub 金融数据管理系统 v1.0.0 正式发布！

### ✨ 新功能

#### 核心功能
- **公司管理** - 支持公司的增删改查，包含代码、名称、主营业务、备注等信息
- **数据导入导出** - 支持 Excel 格式的批量数据导入和导出
- **数据可视化** - 集成 ECharts 图表，支持折线图、柱状图展示
- **公司对比** - 支持多公司数据对比分析

#### 财务数据模块
- **毛利率与净利率** - 管理销售毛利率和净利率数据
- **扣非净利润增长** - 跟踪扣除非经常性损益后的净利润增长情况
- **ROE与净资产** - 记录净资产收益率和净资产数据
- **PE估值** - 管理市盈率、股价、每股收益等估值数据
- **股东结构** - 记录机构持股、散户持股、大股东持股等结构数据
- **股东户数** - 跟踪股东总人数及变化趋势
- **研发投入** - 管理研发费用、研发占比、费用增长率等数据
- **研发团队** - 记录研发人员规模、学历结构等信息

#### 自定义模块（新增）
- **模块管理** - 支持创建自定义数据模块
- **关键词配置** - 灵活配置模块的数据字段（支持字符串、数字、日期类型）
- **动态表单** - 根据配置自动生成数据录入表单
- **动态表格** - 根据配置自动展示数据表格
- **模块菜单集成** - 自定义模块自动添加到左侧导航菜单

### 🔧 技术特性

#### 后端技术栈
- Flask 2.x - Web 框架
- SQLAlchemy 2.x - ORM 数据库操作
- SQLite - 数据存储
- Pandas - 数据处理
- OpenPyXL - Excel 文件操作

#### 前端技术栈
- Vue 3.x - 前端框架
- Element Plus 2.x - UI 组件库
- ECharts 5.x - 数据可视化
- Vue Router 4.x - 路由管理
- Vite - 构建工具

### 📁 项目结构
```
FinDataHub/
├── backend/              # 后端代码
│   ├── api/             # API 路由
│   ├── models.py        # 数据模型
│   ├── app.py           # 应用入口
│   └── run.py           # 启动脚本
├── frontend/            # 前端代码
│   ├── src/
│   │   ├── api/        # API 接口
│   │   ├── views/      # 页面组件
│   │   ├── components/ # 公共组件
│   │   └── router/     # 路由配置
│   └── package.json
├── data/               # 数据库文件
└── README.md
```

### 🚀 部署说明

#### 环境要求
- Python 3.8+
- Node.js 16+
- SQLite 3.x

#### 快速启动
```bash
# 后端
cd backend
pip install -r requirements.txt
python3 run.py

# 前端
cd frontend
npm install
npm run dev
```

### 📝 数据库模型

#### 核心表
- `company` - 公司信息表
- `profit_rate` - 利润率表
- `non_recurring` - 扣非净利润表
- `roe_net_asset` - ROE与净资产表
- `pe_valuation` - PE估值表
- `shareholder_structure` - 股东结构表
- `shareholder_count` - 股东户数表
- `rd_expense` - 研发投入表
- `rd_staff` - 研发人员表

#### 自定义模块表
- `custom_module` - 自定义模块表
- `module_keyword` - 模块关键词表
- `custom_module_data` - 自定义模块数据表

### 🐛 已知问题
- 暂无

### 🔮 未来规划
- [ ] 用户认证和权限管理
- [ ] 数据备份和恢复
- [ ] 多数据库支持（MySQL、PostgreSQL）
- [ ] 数据定时同步
- [ ] 移动端适配
- [ ] API 文档自动生成

### 👥 贡献者
- Bandwe

### 📄 许可证
MIT License

---

## 版本历史

### 版本号说明
- **主版本号**：重大功能更新，可能包含不兼容的 API 修改
- **次版本号**：新功能添加，向下兼容
- **修订号**：问题修复，向下兼容

### 标签规范
- `v1.0.0` - 正式发布版本
- `v1.0.0-beta.1` - 测试版本
- `v1.0.0-rc.1` - 候选发布版本