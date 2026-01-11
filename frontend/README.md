# Agent Poem 前端 Docker 部署指南

## 概述

本项目提供了一种使用 Docker 部署前端应用的方法。通过 Docker 容器化技术，您可以快速部署和运行前端应用。

## 构建和运行

### 单独构建前端镜像

如果您只想构建前端镜像，可以使用以下命令：

```bash
# 在 frontend 目录下执行
docker build -t agent-poem/frontend .
```

### 运行前端容器

构建完成后，可以通过以下命令运行前端容器：

```bash
docker run -d -p 80:80 --name agent-poem-frontend agent-poem/frontend
```

### 使用 Docker Compose 运行完整应用

为了方便起见，我们提供了完整的 `docker-compose.yml` 文件，可以一键部署前后端及依赖服务：

```bash
# 在项目根目录下执行
docker-compose up -d
```

这将启动以下服务：
- MySQL 数据库
- Redis 缓存
- Milvus 向量数据库
- 后端 API 服务
- 前端服务

## 环境配置

前端使用 Nginx 作为 Web 服务器，并通过反向代理将 `/api/` 路径的请求转发到后端服务。

Nginx 配置文件位于 `nginx.conf`，其中包含了 API 代理配置：

```nginx
location /api/ {
    proxy_pass http://backend:8000/;
    proxy_http_version 1.1;
    proxy_set_header Upgrade $http_upgrade;
    proxy_set_header Connection 'upgrade';
    proxy_set_header Host $host;
    proxy_set_header X-Real-IP $remote_addr;
    proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
    proxy_set_header X-Forwarded-Proto $scheme;
    proxy_cache_bypass $http_upgrade;
}
```

## 访问应用

- 前端应用：http://localhost
- 后端 API：http://localhost/api/
- MySQL：localhost:3306
- Redis：localhost:6379

## 自定义配置

如果您需要自定义 Nginx 配置，可以修改 `nginx.conf` 文件，然后重新构建镜像。

## 故障排除

如果遇到问题，请检查：

1. 确保 Docker 和 Docker Compose 已正确安装
2. 检查端口是否已被占用
3. 查看容器日志：
   ```bash
   docker logs agent-poem-frontend
   ```

## 技术栈

- Vue 3
- TypeScript
- Vite
- Nginx
- Docker

## 注意事项

- 生产环境中，请确保修改默认的数据库密码
- 如需修改后端API地址，请在Nginx配置中调整代理设置
- 前端构建产物位于 Docker 镜像的 `/usr/share/nginx/html` 目录