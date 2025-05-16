# 前端Dockerfile
FROM node:18-alpine as build

WORKDIR /app

# 复制package.json和package-lock.json
COPY package*.json ./

# 安装依赖
RUN npm ci

# 复制源代码
COPY . .

# 构建前端应用
RUN npm run build

# 生产环境阶段
FROM nginx:alpine

# 从构建阶段复制构建产物
COPY --from=build /app/dist /usr/share/nginx/html

# 复制nginx配置
COPY ./nginx.conf /etc/nginx/conf.d/default.conf

EXPOSE 80

CMD ["nginx", "-g", "daemon off;"]
