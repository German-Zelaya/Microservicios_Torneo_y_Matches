# Imagen base
FROM node:20-alpine

# Crear directorio de la app
WORKDIR /app

# Copiar package.json y package-lock.json
COPY package*.json ./

# Instalar dependencias
RUN npm install

# Copiar el resto del código
COPY . .

# Exponer puertos (REST + gRPC)
EXPOSE 3002 50052

# Variables de entorno (puede ser opcional si usas .env)
ENV NODE_ENV=production

# Comando para iniciar el servicio
CMD ["npm", "run", "start"]
