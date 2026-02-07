# 项目部署文档

本项目支持使用 Docker 和 Docker Compose 进行一键部署。

## 1. 部署前准备

### 1.1 环境要求
- 服务器操作系统：Linux (Ubuntu/CentOS) 或 Windows Server
- 软件依赖：
  - Docker Engine (v20.10+)
  - Docker Compose (v2.0+)

### 1.2 获取代码
将项目代码上传至服务器：
```bash
# 假设上传至 /opt/training-agent
cd /opt/training-agent
```

## 2. 配置说明

### 2.1 环境变量配置
在 `backend` 目录下创建 `.env` 文件，用于配置敏感信息（如 API Key）。
你可以复制示例文件进行修改：

```bash
cd backend
cp .env.example .env
vim .env
```

`.env` 文件内容示例：
```ini
DEEPSEEK_API_KEY=sk-xxxxxxxxxxxxxxxxxxxxxxxx  # 替换为你的 DeepSeek API Key
DEEPSEEK_BASE_URL=https://api.deepseek.com
DEEPSEEK_MODEL=deepseek-chat
```

### 2.2 数据文件准备
本项目需要依赖就业市场数据（CSV文件）。请确保数据文件已上传到服务器指定目录。

默认配置下，Docker 会将项目根目录下的 `events_kg/input/就业市场数据(2)` 挂载到容器内。
请确保以下文件存在于 `events_kg/input/就业市场数据(2)/` 目录中：
- `职位.csv` (编码: GBK)
- `宣讲会.csv` (编码: GBK)
- `招聘会.csv` (编码: GBK)

**注意**：代码中默认使用 `GBK` 编码读取 CSV 文件。如果你的服务器环境或上传工具有自动转码功能，请确认文件编码是否仍为 GBK，否则可能出现乱码。

## 3. 启动服务

在项目根目录下执行以下命令构建并启动服务：

```bash
# 构建并后台启动
docker-compose up -d --build
```

查看服务状态：
```bash
docker-compose ps
```

查看日志：
```bash
# 查看后端日志
docker-compose logs -f backend

# 查看前端日志
docker-compose logs -f frontend
```

## 4. 访问服务

服务启动后，可以通过浏览器访问：

- **前端页面**：`http://服务器IP` (默认 80 端口)
- **后端 API**：`http://服务器IP/api` (通过 Nginx 转发)
- **API 文档**：`http://服务器IP/api/docs` (Swagger UI)

## 5. 维护与更新

### 更新代码
```bash
git pull  # 或者重新上传代码
docker-compose up -d --build  # 重新构建并重启
```

### 停止服务
```bash
docker-compose down
```

### 常见问题
1. **端口冲突**：如果 80 或 8000 端口被占用，请修改 `docker-compose.yml` 中的 `ports` 映射。
2. **数据未加载**：检查 `docker-compose.yml` 中的 `volumes` 路径是否正确，以及服务器上是否存在对应的数据文件。
