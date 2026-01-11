# 使用Node.js官方镜像作为构建环境
FROM node:20 AS builder

# 设置工作目录
WORKDIR /app

# 复制package.json和package-lock.json（如果存在）
COPY package*.json ./

# 安装依赖
RUN npm ci --only=production

# 复制源代码
COPY . .

# 构建应用
RUN npm run build

# 使用Nginx作为生产环境
FROM nginx:alpine

# 复制Nginx配置文件
COPY ./nginx.conf /etc/nginx/nginx.conf

# 从构建阶段复制构建产物到Nginx的HTML目录
COPY --from=builder /app/dist /usr/share/nginx/html

# 暴露端口
EXPOSE 80

# 启动Nginx
CMD ["nginx", "-g", "daemon off;"]