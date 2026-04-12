# Build stage
FROM node:18-alpine AS build

WORKDIR /app

# Copy package files
COPY package.json package-lock.json ./
RUN npm ci --legacy-peer-deps

# Copy source code
COPY . .

# Build Angular app
RUN npm run build -- --configuration production

# Production stage
FROM nginx:alpine

# Copy built app
COPY --from=build /app/dist/trading-monitoring-dashboard /usr/share/nginx/html

# Copy nginx config
COPY nginx.conf /etc/nginx/nginx.conf

# Expose port
EXPOSE 80

# Health check
HEALTHCHECK --interval=30s --timeout=3s --start-period=5s --retries=3 \
    CMD wget --quiet --tries=1 --spider http://localhost:80 || exit 1

CMD ["nginx", "-g", "daemon off;"]