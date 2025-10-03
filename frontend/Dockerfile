# syntax=docker/dockerfile:1.7

########### Build stage
FROM node:20-alpine AS build
WORKDIR /app

# install deps with caching
COPY package*.json ./
RUN npm ci

# copy source and build
COPY . .
# If you have Vite envs, you can pass them as build args:
# ARG VITE_API_BASE=/api
# ENV VITE_API_BASE=$VITE_API_BASE
RUN npm run build

RUN if [ -d dist ]; then cp -r dist /tmp/static; \
    elif [ -d build ]; then cp -r build /tmp/static; \
    else echo "No dist/ or build/ found. Check your build tool."; exit 1; fi

########### Runtime stage
FROM nginx:1.27-alpine
WORKDIR /usr/share/nginx/html

# Nginx config (SPA + optional /api proxy)
COPY docker/nginx.conf /etc/nginx/conf.d/default.conf

# Copy static assets (change dist -> build if using CRA)
COPY --from=build /tmp/static ./

EXPOSE 80
# simple, safe healthcheck (no heredoc)
HEALTHCHECK --interval=30s --timeout=3s --start-period=10s --retries=3 \
  CMD wget -qO- http://127.0.0.1/ >/dev/null 2>&1 || exit 1
