# FinDataHub 完整优化流程

## 优化目标

把当前“能本地运行的原型项目”优化成“可稳定部署、可持续扩展、可测试回归、可安全导入数据”的本地财务数据管理系统。

优化不建议一次性大改，而是按阶段推进：

```text
稳定可跑 -> 统一工程入口 -> 抽象重复模块 -> 强化导入导出 -> 补测试与发布 -> 做产品体验优化
```

## 阶段 0：现状冻结与基线确认

目标：先明确当前能工作的状态，避免优化过程中把可用功能改坏。

工作项：

1. 固定当前源码部署方式。
2. 记录数据库位置、端口、启动命令、验证命令。
3. 保留一份可回滚的数据备份。
4. 建立 smoke test，覆盖首页、健康检查、公司列表、核心模块列表。

当前已完成：

- 源码部署目录：项目根目录
- 虚拟环境：`.venv`
- 数据库：`data/findata.db`
- 启动脚本：`scripts/start_source_backend.sh`
- 验证脚本：`scripts/verify_source_backend.sh`
- 访问地址：http://127.0.0.1:5002

验收标准：

```bash
./scripts/verify_source_backend.sh
```

返回：

```text
FinDataHub source backend verified at http://127.0.0.1:5002
```

## 阶段 1：P0 稳定化

目标：先修影响部署、启动、依赖、端口和数据安全的问题。

### 1.1 依赖锁定

问题：

- `pandas==2.0.3` 会被 pip 搭配到不兼容的 `numpy==2.0.2`。
- 当前已通过 `numpy<2` 修复。

继续优化：

1. 增加 `requirements-dev.txt`，把测试工具和开发工具与运行依赖分开。
2. 生成锁定文件，例如 `requirements-lock.txt`，记录实际可用版本。
3. 每次升级依赖后先跑 smoke test，再跑导入导出测试。

推荐文件：

```text
backend/requirements.txt
backend/requirements-dev.txt
backend/requirements-lock.txt
```

验收标准：

```bash
.venv/bin/python - <<'PY'
import flask, pandas, numpy, openpyxl
print("imports ok")
PY
```

### 1.2 端口与启动入口统一

问题：

- README、`app.py`、`run.py`、Vite proxy 的端口说明不一致。

当前建议：

- 源码后端统一使用 `127.0.0.1:5002`。
- `FINDATA_PORT` 可覆盖端口。
- 入口统一使用 `scripts/start_source_backend.sh`。

验收标准：

```bash
FINDATA_PORT=5002 ./scripts/start_source_backend.sh
```

浏览器可访问：

```text
http://127.0.0.1:5002
```

### 1.3 打包产物处理

处理流程：

1. 不把 `dist_package` 作为源码仓库的一部分提交。
2. 通过 GitHub Actions 或本地 PyInstaller 流程重新生成发布包。
3. 打包前先跑源码 smoke test，再打包，再对打包产物做同样 smoke test。

验收标准：

- 文档明确“当前可靠部署方式是源码部署”。
- 发布前必须验证新打包产物，不复用历史包。

### 1.4 数据备份与恢复

流程：

1. 停止服务。
2. 复制 `data/findata.db`。
3. 记录备份时间。
4. 恢复时替换该文件，再启动服务验证。

建议目录：

```text
backups/
  findata-YYYYMMDD-HHMMSS.db
```

验收标准：

```bash
sqlite3 data/findata.db '.tables'
```

能看到核心表：

```text
company
profit_rate
non_recurring
roe_net_asset
pe_valuation
shareholder_structure
shareholder_count
rd_expense
rd_staff
custom_module
module_keyword
custom_module_data
```

## 阶段 2：后端结构优化

目标：减少固定模块重复代码，建立可维护的业务结构。

### 2.1 建立模块注册表

当前问题：

- 8 个固定模块各有独立 API 文件。
- 列表、创建、更新、删除、导出逻辑高度相似。
- 新增一个固定模块需要复制一整套文件。

目标结构：

```text
backend/modules/
  registry.py
  crud.py
  import_export.py
  validation.py
```

模块注册表示例：

```python
MODULES = {
    "profit_rate": {
        "model": ProfitRate,
        "endpoint": "profit_rate",
        "unique_fields": ["company_id", "year"],
        "order_fields": ["year", "company_code"],
        "columns": [
            {"key": "gross_profit_margin", "label": "销售毛利率(%)", "type": "number"},
            {"key": "net_profit_margin", "label": "销售净利率(%)", "type": "number"},
        ],
    },
}
```

迁移流程：

1. 先只把查询分页抽出来，不改路由。
2. 再抽创建、更新、删除。
3. 再抽导入导出。
4. 每抽一个模块，跑对应 API 回归。

验收标准：

- 固定模块 API 行为不变。
- 删除重复查询构造逻辑。
- 新增模块只需要改注册表和模型。

### 2.2 统一响应格式

当前格式大体是：

```json
{"code": 200, "data": {}}
```

建议封装：

```python
def ok(data=None, message="ok"):
    return jsonify({"code": 200, "message": message, "data": data})

def fail(message, status=400, code=None):
    return jsonify({"code": code or status, "message": message}), status
```

流程：

1. 新增 `backend/api/responses.py`。
2. 先在新代码使用。
3. 再逐个替换旧 API。
4. 前端 request interceptor 保持兼容。

验收标准：

- 成功响应都包含 `code/message/data`。
- 失败响应都包含 `code/message`。
- HTTP 状态码和业务 code 不冲突。

### 2.3 统一异常和事务

当前问题：

- 多处手动 `db.session.commit()`。
- 异常处理分散。
- 部分导入逻辑中有裸 `except`。

优化流程：

1. 增加全局异常 handler。
2. 数据库写入统一进入 service 层。
3. service 失败时统一 rollback。
4. 导入场景保留单行错误，不让整批失败。

验收标准：

- API 内部异常不会返回 HTML 错误页。
- 数据库异常会 rollback。
- 导入错误能精确定位到行号和字段。

### 2.4 输入校验

当前问题：

- 多数接口只检查是否为空。
- 日期、百分比、枚举、年份范围缺少统一校验。

建议校验规则：

```text
company.code：非空，唯一，长度合理
year：1900-2100
percent：建议 -100 到 1000，按字段细分
type：actual 或 forecast
stat_date：YYYY-MM-DD
```

流程：

1. 先加纯函数校验，不引入重型框架。
2. 给每个模块配置字段类型和范围。
3. 在 create/update/import 入口复用。

验收标准：

- 前端错误提示明确。
- API 返回字段级错误信息。
- Excel 导入能输出错误报告。

### 2.5 数据库迁移

当前问题：

- `db.create_all()` 适合初始化，不适合后续结构演进。

流程：

1. 引入 Flask-Migrate/Alembic。
2. 生成当前 schema 的 baseline migration。
3. 后续所有表结构变更走 migration。
4. 发布前先在备份数据库上演练迁移。

验收标准：

- 不再通过删除数据库解决结构变化。
- 每次 schema 变化都有 migration 文件。

## 阶段 3：前端结构优化

目标：把 8 个重复页面合并成配置驱动页面，降低维护成本。

### 3.1 建立前端模块配置

目标文件：

```text
frontend/src/modules/financialModules.js
```

配置内容：

```javascript
export const financialModules = {
  profit_rate: {
    title: '毛利率与净利率',
    route: '/profit-rate',
    endpoint: '/profit_rate',
    columns: [],
    formFields: [],
    chartMetrics: [],
  },
}
```

流程：

1. 先把表格列配置抽出来。
2. 再抽表单字段。
3. 再抽筛选条件。
4. 最后抽图表指标。

验收标准：

- 8 个固定模块共用同一个 `ModulePage.vue`。
- 新增模块不再复制一个 500 行视图文件。

### 3.2 抽通用组件

建议组件：

```text
DataToolbar.vue
DataFilter.vue
DataTable.vue
ModuleFormDialog.vue
ImportDialog.vue
ChartPanel.vue
CompanyCompareDialog.vue
```

流程：

1. 先抽只读组件，例如表格。
2. 再抽交互组件，例如表单弹窗。
3. 最后抽导入、导出、对比。

验收标准：

- 单个页面文件控制在 200 行以内。
- 表格、表单、导入导出行为一致。

### 3.3 API 层统一

当前问题：

- 每个模块一个 API 文件，重复 CRUD 方法。

目标：

```text
frontend/src/api/modules.js
```

方法：

```javascript
export function listModule(endpoint, params) {}
export function createModule(endpoint, data) {}
export function updateModule(endpoint, id, data) {}
export function deleteModule(endpoint, id) {}
export function importModule(endpoint, file) {}
export function exportModule(endpoint, params) {}
```

验收标准：

- 固定模块 API 文件减少。
- 所有模块统一错误处理、loading 状态、导出逻辑。

## 阶段 4：导入导出优化

目标：让 Excel 导入从“能导入”变成“可预览、可校验、可追溯、可回滚”。

### 4.1 三段式导入

流程：

```text
上传文件 -> 解析预览 -> 校验报告 -> 用户确认 -> 入库 -> 导入结果
```

预览阶段不写数据库，只返回：

```json
{
  "rows": [],
  "errors": [],
  "warnings": [],
  "summary": {
    "total": 100,
    "valid": 95,
    "invalid": 5
  }
}
```

验收标准：

- 用户确认前不会写入数据库。
- 错误能定位到 sheet、行号、列名。

### 4.2 字段映射优化

流程：

1. 自动识别表头。
2. 对未匹配字段给出建议。
3. 允许用户手动映射。
4. 保存最近一次映射规则。

验收标准：

- Excel 表头轻微差异不会直接失败。
- 导入报告能显示字段映射关系。

### 4.3 导入批次记录

建议新增表：

```text
import_batch
  id
  filename
  module_name
  status
  total_count
  success_count
  error_count
  created_at

import_error
  id
  batch_id
  sheet_name
  row_number
  field_name
  message
```

验收标准：

- 能查看历史导入记录。
- 能下载失败明细。
- 能按批次追溯数据来源。

## 阶段 5：测试体系

目标：每次改动后能快速判断系统有没有坏。

### 5.1 后端测试

建议覆盖：

```text
test_health.py
test_companies.py
test_fixed_modules.py
test_import_export.py
test_custom_modules.py
```

最小测试：

1. `/health` 返回 200。
2. 公司 CRUD。
3. 每个固定模块列表返回 200。
4. Excel 模板下载返回 xlsx。
5. 导入预览不写数据库。

验收标准：

```bash
.venv/bin/python -m pytest
```

### 5.2 前端测试

如果后续允许安装 Node，再做：

1. `npm run build` 构建测试。
2. Playwright 打开首页。
3. 检查左侧菜单、表格渲染、API 请求无错误。
4. 验证导入弹窗、公司选择、图表切换。

验收标准：

```bash
npm run build
npx playwright test
```

## 阶段 6：发布流程

目标：把“本地能跑”变成“可重复发布”。

发布前流程：

```text
清理旧产物
安装依赖
初始化测试数据库
运行后端测试
运行前端构建
复制前端 dist 到 backend/static
源码启动 smoke test
打包
打包产物 smoke test
生成发布说明
```

发布验收：

1. 新目录解压后能启动。
2. 不依赖开发机已有包。
3. 首次启动能创建数据库。
4. 首页和核心 API 正常。
5. 数据文件位置明确。

## 阶段 7：产品体验优化

目标：让财务数据管理更顺手，而不是只完成 CRUD。

### 7.1 首页仪表盘

建议展示：

- 公司数量
- 最近导入批次
- 各模块数据量
- 数据更新时间
- 异常数据提醒

### 7.2 数据质量提示

建议提示：

- 某公司缺失年份。
- 某指标同比异常。
- 股东结构占比异常。
- PE/EPS 为空或极端。

### 7.3 分析视图

建议：

- 多公司同指标趋势对比。
- 单公司多指标组合分析。
- 年度区间筛选。
- 图表导出。

### 7.4 权限和审计

如果多人使用，补：

- 登录
- 角色权限
- 操作日志
- 导入记录
- 删除确认和恢复机制

## 推荐执行顺序

第一轮，1-2 天：

1. 固化当前源码部署。
2. 修 README 和端口说明。
3. 增加 smoke test。
4. 增加数据库备份脚本。

第二轮，3-5 天：

1. 后端模块注册表。
2. 固定模块 CRUD service。
3. 统一响应和异常。
4. 补后端 pytest。

第三轮，5-8 天：

1. 前端模块配置。
2. 合并 8 个固定模块页面。
3. 抽通用表格、表单、导入导出组件。
4. 做前端构建验证。

第四轮，3-5 天：

1. 导入预览。
2. 校验报告。
3. 导入批次记录。
4. 失败明细下载。

第五轮，2-4 天：

1. 重新打包。
2. 打包产物 smoke test。
3. 发布说明。
4. 数据备份与恢复演练。

## 不建议一开始做的事

1. 不建议先大规模重写 UI。
2. 不建议先引入复杂权限系统。
3. 不建议直接切 MySQL，除非明确有多用户并发需求。
4. 不建议手工维护历史打包产物，发布包应由可复现流程生成。
5. 不建议一次性把后端和前端同时大重构。

## 最终验收清单

工程验收：

- 一条命令启动。
- 一条命令验证。
- 依赖可重复安装。
- README 与真实行为一致。
- 打包产物经过 smoke test。

后端验收：

- CRUD 行为一致。
- 错误响应统一。
- 导入可预览、可校验、可追溯。
- 有基础测试覆盖。
- schema 变更可迁移。

前端验收：

- 固定模块配置驱动。
- 页面重复代码明显减少。
- 表格、表单、筛选、导入导出体验一致。
- 构建通过。

产品验收：

- 用户知道数据存在哪里。
- 用户能备份和恢复。
- 导入失败知道为什么失败。
- 关键财务指标能对比、筛选、导出。
