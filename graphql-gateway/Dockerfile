FROM node:18-alpine

# Establecer directorio de trabajo
WORKDIR /app

# Copiar archivos de dependencias
COPY package*.json ./

# Instalar dependencias
RUN npm ci --only=production

# Copiar código fuente
COPY src/ ./src/

# Exponer puerto
EXPOSE 4000

# Variable de entorno para producción
ENV NODE_ENV=production

# Comando de inicio
CMD ["node", "src/server.js"]
