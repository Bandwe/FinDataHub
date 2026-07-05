# FinDataHub 本地源码部署记录

## 当前可用部署方式

本地源码部署使用独立 Python 虚拟环境和项目默认 SQLite 数据库。仓库已提交构建后的前端静态文件，因此仅运行源码后端不需要 Node.js；修改前端后需要重新构建。

```bash
cd FinDataHub
python3 -m venv .venv
.venv/bin/pip install -r backend/requirements.txt
.venv/bin/python backend/init_data.py
./scripts/start_source_backend.sh
```

访问地址：

- 前端页面：http://127.0.0.1:5002
- 健康检查：http://127.0.0.1:5002/health

可选环境变量：

```bash
FINDATA_HOST=127.0.0.1
FINDATA_PORT=5002
FINDATA_DEBUG=0
```

验证命令：

```bash
./scripts/verify_source_backend.sh
```

## 部署验证清单

运行 `./scripts/verify_source_backend.sh` 会验证：

- `/health` 返回 200
- `/` 返回静态前端 `index.html`
- `/api/companies/all` 返回公司列表
- `/api/profit_rate?page=1&per_page=3` 返回分页数据

## 部署注意事项

1. `pandas==2.0.3` 与 pip 自动选择的 `numpy==2.0.2` 在 Python 3.9 上二进制不兼容，会报：

   ```text
   ValueError: numpy.dtype size changed, may indicate binary incompatibility
   ```

   处理方式：在 `backend/requirements.txt` 中增加 `numpy<2`。

2. 当前 `backend/config.py` 实际使用 SQLite：

   ```python
   SQLALCHEMY_DATABASE_URI = f'sqlite:///{os.path.join(DATA_DIR, "findata.db")}'
   ```

3. 源码后端默认使用 5002，桌面打包入口默认使用 5001。都可以通过 `FINDATA_PORT` 覆盖。

4. 修改前端源码后需要运行 `npm run build` 并把 `frontend/dist` 同步到 `backend/static`。

## 数据位置

SQLite 数据库位于：

```text
FinDataHub/data/findata.db
```

备份时关闭服务后复制该文件即可。
