# Usa una imagen base de Python (ligera)
FROM python:3.11-slim

# Establece el directorio de trabajo
WORKDIR /app

# Copia solo el archivo de dependencias
COPY requirements.txt .

# Instala dependencias
RUN pip install --no-cache-dir -r requirements.txt

# Copia el resto del código
COPY . .

# Expone el puerto de Streamlit
EXPOSE 8501

# Comando para ejecutar Streamlit
CMD ["streamlit", "run", "frontend.py", "--server.port=8501", "--server.address=0.0.0.0"]
