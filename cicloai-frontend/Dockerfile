FROM node:20-alpine AS builder

WORKDIR /app

ARG VITE_APP_NAME=CicloAI
ARG VITE_ENABLE_MOCKS=true
ARG VITE_API_BASE_URL=http://localhost:8000/api/v1
ARG VITE_RECAPTCHA_ENTERPRISE_SITE_KEY=6LcYJMcsAAAAANnSzsP1VP4bJ86DKcGQzhVbZNO2

ENV VITE_APP_NAME=$VITE_APP_NAME \
    VITE_ENABLE_MOCKS=$VITE_ENABLE_MOCKS \
    VITE_API_BASE_URL=$VITE_API_BASE_URL \
    VITE_RECAPTCHA_ENTERPRISE_SITE_KEY=$VITE_RECAPTCHA_ENTERPRISE_SITE_KEY

COPY package.json package-lock.json ./
RUN npm ci

COPY . .
RUN npm run build

FROM nginx:1.27-alpine

COPY nginx.conf /etc/nginx/conf.d/default.conf
COPY --from=builder /app/dist /usr/share/nginx/html

EXPOSE 80

