# 1. Front React -> arquivos estáticos dentro do Spring Boot
FROM node:22-slim AS front
WORKDIR /app/frontend
COPY frontend/package.json frontend/package-lock.json ./
RUN npm ci
COPY frontend ./
RUN npx vite build

# 2. Backend Java -> driftor.jar (já com o front dentro)
FROM maven:3.9-eclipse-temurin-21 AS back
WORKDIR /app/backend
COPY backend ./
COPY --from=front /app/backend/static ./static
RUN mvn -q -DskipTests package

# 3. Imagem final: Java na porta 8080 e o motor Python na 8000 (só por dentro)
FROM python:3.12-slim
COPY --from=eclipse-temurin:21-jre /opt/java/openjdk /opt/java/openjdk
ENV PATH=/opt/java/openjdk/bin:$PATH PYTHONUNBUFFERED=1
WORKDIR /srv
COPY motor/requirements.txt motor/
RUN pip install --no-cache-dir -r motor/requirements.txt
COPY motor/motor.py motor/
COPY --from=back /app/backend/target/driftor.jar .
EXPOSE 8080
CMD ["sh", "-c", "uvicorn motor:app --app-dir motor --port 8000 & exec java -Xmx320m -jar driftor.jar"]
