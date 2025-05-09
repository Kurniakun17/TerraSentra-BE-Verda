FROM python:3.11

WORKDIR /app

# Install dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy project files
COPY . .

COPY ee-account-key.json /service-account-key.json
ENV GOOGLE_APPLICATION_CREDENTIALS=/service-account-key.json
ENV DB_NAME=postgres
ENV DB_USER=postgres.liavfvdhtpfhmnuuejyl
ENV DB_PASSWORD=TerraSentra123!
ENV DB_HOST=aws-0-ap-southeast-1.pooler.supabase.com
ENV DB_PORT=5432


EXPOSE 8080

# Run the application
CMD ["uvicorn", "app:app", "--host", "0.0.0.0", "--port", "8080"]