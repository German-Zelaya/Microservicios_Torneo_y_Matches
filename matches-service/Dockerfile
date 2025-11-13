# ========================================
# Matches Service - Go/Fiber
# Multi-stage build para optimizar tamaño
# ========================================

# Stage 1: Build
FROM golang:1.25-alpine AS builder

# Instalar dependencias de compilación
RUN apk add --no-cache git

# Establecer directorio de trabajo
WORKDIR /app

# Copiar archivos de dependencias
COPY go.mod go.sum ./

# Descargar dependencias
RUN go mod download

# Copiar el código fuente
COPY . .

# Compilar la aplicación
RUN CGO_ENABLED=0 GOOS=linux go build -a -installsuffix cgo -o main ./cmd/main.go

# Stage 2: Runtime
FROM alpine:latest

# Instalar certificados SSL y zona horaria
RUN apk --no-cache add ca-certificates tzdata

WORKDIR /root/

# Copiar el binario compilado desde el stage anterior
COPY --from=builder /app/main .

# Exponer puerto
EXPOSE 8002

# Comando para ejecutar la aplicación
CMD ["./main"]