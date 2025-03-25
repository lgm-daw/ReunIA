# Usa Python 3.10 como base
FROM python:3.10

# Establece el directorio de trabajo dentro del contenedor
WORKDIR /app

# Copia solo requirements.txt primero para aprovechar el cacheo de Docker
COPY requirements.txt .

# Instala dependencias
RUN pip install --no-cache-dir -r requirements.txt

# Copia el resto del código del backend
COPY . .

# Asegurar permisos de ejecución si se necesita
RUN chmod +x /app

# Exponer el puerto 8000
EXPOSE 8000

# Configurar variable de entorno para Cloud Run
ENV PORT=8000

# Comando para ejecutar FastAPI (Usa `PORT` dinámico de Cloud Run)
CMD ["uvicorn", "app:app", "--host", "0.0.0.0", "--port", "8000"]
