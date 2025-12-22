# Arxiv 文献综述系统（MVP）

该仓库提供一个最小可运行的 arXiv 文献综述系统，后端基于 FastAPI + Celery + PostgreSQL + Redis，前端为简单 HTML 页面，默认使用 Mock Provider 可离线运行。

## 快速开始

1. **启动服务**

   ```bash
   docker-compose up --build
   ```

2. **初始化数据库**

   进入 API 容器执行 Alembic 迁移：

   ```bash
   docker-compose exec api alembic upgrade head
   ```

3. **访问前端**

   打开浏览器访问 `http://localhost:8000/frontend/index.html`（通过卷挂载可直接读取前端文件），先注册再登录。

4. **运行流程**

   - 创建项目（输入 topic/keywords）。
   - 点击 Run 启动流水线（触发 Celery 任务）。
   - WebSocket 会实时显示阶段与日志（Mock Provider 下立即完成）。
   - 导出结果会生成 Markdown 文件并记录到 `exports` 表。

## 项目结构

- `backend/app`：FastAPI 应用、路由、领域服务、Provider/Adapter。
- `backend/alembic`：数据库迁移脚本。
- `frontend/index.html`：最小交互页面。
- `docker-compose.yml`：包含 api、worker、redis、postgres 服务。
- `.env`：运行时配置（Mock Provider 默认配置）。

## 主要接口（/api/v1）
- `POST /auth/register` 注册
- `POST /auth/token` 登录，返回 JWT
- `GET /projects`、`POST /projects`、`GET /projects/{id}`、`DELETE /projects/{id}`
- `POST /projects/{id}/run` 启动 Celery 任务
- `GET /projects/{id}/status`、`GET /projects/{id}/papers`、`GET /projects/{id}/exports`
- `WS /ws/projects/{project_id}?token=...` 订阅实时事件

## 开发与测试

- 在本机直接运行 API：`uvicorn app.main:app --reload`
- 运行自动化测试（使用 SQLite 与 Mock Provider）：

  ```bash
  cd backend
  pytest
  ```

## 开发模式

- API 默认监听 `8000` 端口，可通过 `uvicorn app.main:app --reload` 本地运行。
- 使用 Mock Provider，不需要外部 LLM/PDF 依赖即可跑通流程。
- 若切换 OpenAI 兼容接口，可在 `.env` 中配置 `OPENAI_COMPAT_BASE_URL` 与 `OPENAI_COMPAT_API_KEY`。
