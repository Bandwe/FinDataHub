# FinDataHub 项目解析与重构方案

## 当前项目画像

FinDataHub 是一个本地优先的财务数据管理 Web 应用。

- 后端：Flask + Flask-SQLAlchemy + SQLite
- 前端：Vue 3 + Element Plus + ECharts
- 数据处理：pandas/openpyxl 负责 Excel 导入导出
- 发布形态：源码运行、Flask 托管已构建前端、历史 PyInstaller 打包产物

核心业务由三层构成：

1. 公司主数据：`company`
2. 固定财务模块：利润率、扣非净利润、ROE、PE、股东结构、股东户数、研发投入、研发人员
3. 自定义模块：`custom_module` + `module_keyword` + `custom_module_data`

请求流：

```text
Vue 页面 -> axios /api -> Flask Blueprint -> SQLAlchemy Model -> SQLite
```

导入导出流：

```text
Excel 文件 -> openpyxl/pandas -> 字段映射 -> upsert/insert -> SQLite -> Excel 导出
```

## 建议的目标结构

当前代码能跑，但固定模块的 CRUD、分页、导入、导出存在重复。建议重构成“模块配置驱动”的结构：

```text
backend/
  app.py
  config.py
  extensions.py
  models/
    company.py
    financial_metrics.py
    custom_module.py
  modules/
    registry.py
    schemas.py
    crud.py
    import_export.py
  api/
    companies.py
    fixed_modules.py
    custom_modules.py
  services/
    excel_service.py
    validation_service.py
  tests/
    test_health.py
    test_fixed_modules.py
    test_import_export.py

frontend/src/
  api/
    request.js
    modules.js
  components/
    DataTable.vue
    ModuleForm.vue
    CompareDialog.vue
    ImportDialog.vue
  views/
    ModulePage.vue
    CompanyManage.vue
    ModuleManage.vue
```

## 后端重构重点

1. 建立模块注册表

   把每个模块的模型、路由名、主键维度、展示字段、导入字段、导出字段放入统一 registry，避免每新增一个模块就复制一套 API 文件。

2. 抽通用 CRUD 服务

   固定模块都包含列表、创建、更新、删除、导入、导出。可以用 `ModuleCrudService` 统一处理查询、分页、唯一性检查和提交事务。

3. 统一响应与错误处理

   当前各 API 自己拼 `{'code': 200}`，部分异常直接返回字符串。建议统一 `success(data)`、`fail(message, status)`、全局异常 handler，并把数据库错误回滚集中处理。

4. 增加输入校验层

   目前主要靠手写 `if not data.get(...)`。建议使用轻量 schema 层，明确字段类型、必填、范围、枚举值和日期格式。

5. 引入迁移机制

   `db.create_all()` 适合原型，不适合长期维护。建议使用 Flask-Migrate/Alembic 管理 schema 变更。

## 前端重构重点

1. 把 8 个固定模块页面合并为配置驱动的 `ModulePage.vue`

   每个模块只保留配置：标题、接口路径、表格列、表单字段、筛选项、图表指标。

2. 抽通用表格和表单组件

   当前每个视图文件 500 行左右，功能重复。可以拆成 `DataTable`、`FilterBar`、`ModuleForm`、`ImportExportToolbar`、`ChartPanel`。

3. API 层统一

   把 `profitRate.js`、`roeNetAsset.js` 等拆散文件合并成 `modules.js`，通过模块名生成 CRUD 请求。

4. 统一端口和环境变量

   Vite 代理现在是 5002，README 和 Flask 入口不一致。建议前端使用 `.env.development`：

   ```text
   VITE_API_BASE=/api
   VITE_DEV_PROXY_TARGET=http://127.0.0.1:5002
   ```

## 数据与产品优化

1. 明确“真实数据”和“示例数据”的边界

   `init_data.py` 应只在开发环境执行，生产运行不应自动混入示例数据。

2. 导入流程做成三段式

   解析预览 -> 校验报告 -> 用户确认入库。当前已有预览雏形，但错误粒度和字段映射反馈还可以更清晰。

3. 加数据质量规则

   示例：年份范围、百分比上下限、PE/EPS 合理范围、股东比例合计提示、公司代码格式。

4. 给每次导入建立批次记录

   保存导入文件名、操作者、时间、成功/失败条数和错误明细，便于回滚和追溯。

## 工程流程优化

完整执行流程见：

```text
docs/OPTIMIZATION_WORKFLOW.md
```

推荐流程：

```text
依赖锁定 -> 本地 smoke test -> API 合约测试 -> 导入导出回归 -> 前端页面验收 -> 打包
```

最低可落地清单：

1. 依赖：维护 `requirements.txt`，固定会影响二进制兼容的包，例如 `numpy<2`。
2. 启动：统一源码入口为 `scripts/start_source_backend.sh`。
3. 验证：统一健康检查和核心 API smoke test 为 `scripts/verify_source_backend.sh`。
4. 测试：补 `pytest` 覆盖健康检查、公司 CRUD、每个固定模块列表和 Excel 导入导出。
5. 发布：打包前先清空旧 dist，运行 smoke test，再生成平台包。

## 优先级建议

P0：

- 修复依赖锁定
- 统一端口说明
- 移除或修复不可用打包产物
- 增加后端 smoke test

P1：

- 后端固定模块 API 配置化
- 前端 8 个模块页面合并为通用 `ModulePage`
- Excel 导入增加批次和校验报告

P2：

- Alembic 数据库迁移
- 权限认证和操作日志
- 图表配置化和多公司对比增强
