# ==============================================================================
# Dockerfile para Frontend - Automotriz JJ
# Multi-stage build: Node Alpine (build) + Nginx Alpine (serve)
# ==============================================================================

# ============================================
# STAGE 1: Build de la aplicación React
# ============================================
FROM node:18-alpine AS builder

# Metadata
LABEL maintainer="Automotriz JJ"
LABEL description="Frontend React - Build Stage"

# Establecer directorio de trabajo
WORKDIR /app

# Copiar package files primero (para aprovechar cache)
COPY package*.json ./

# Instalar dependencias
RUN npm ci --only=production=false

# Copiar el resto del código
COPY / ./

# Build de producción
RUN npm run build

# ============================================
# STAGE 2: Servidor Nginx para servir archivos
# ============================================
FROM nginx:alpine

# Metadata
LABEL maintainer="Automotriz JJ"
LABEL description="Frontend React con Nginx"
LABEL version="2.0"

# Copiar archivos compilados desde el stage de build
COPY --from=builder /app/dist /usr/share/nginx/html

# Copiar configuración personalizada de Nginx
COPY nginx.conf /etc/nginx/conf.d/default.conf

# Exponer puerto 80
EXPOSE 80

# Healthcheck
HEALTHCHECK --interval=30s --timeout=10s --start-period=5s --retries=3 \
    CMD wget --no-verbose --tries=1 --spider http://localhost:80 || exit 1

# Nginx se inicia automáticamente con la imagen base
CMD ["nginx", "-g", "daemon off;"]