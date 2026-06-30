FROM node:20-alpine AS build

WORKDIR /app
COPY package*.json ./
RUN npm config set registry https://registry.npmmirror.com/ && \
    npm install && \
    npm cache clean --force

COPY . .
RUN npm run build

FROM nginx:alpine
LABEL maintainer="zhou7419"
COPY --from=build /app/dist /usr/share/nginx/html
COPY nginx.conf /etc/nginx/conf.d/default.conf
RUN rm -f /etc/nginx/conf.d/default.conf.bak /etc/nginx/nginx.conf.bak

EXPOSE 80
CMD ["nginx", "-g", "daemon off;"]
