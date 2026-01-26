# Build stage
FROM node:20-alpine as build
WORKDIR /leaderboardx-fe-root
COPY package.json package-lock.json* ./
RUN npm install --production=false
COPY tsconfig.json vite.config.ts index.html ./
COPY .env ./
COPY src ./src
RUN npm run build

# Runtime stage
FROM nginx:alpine
COPY --from=build /leaderboardx-fe-root/dist /usr/share/nginx/html
COPY nginx.conf /etc/nginx/conf.d/default.conf
EXPOSE 80
CMD ["nginx", "-g", "daemon off;"]
