# Etapa 7, secao 7.6: "clona e roda". Este Dockerfile + o
# docker-compose.yml da raiz sao o que torna "vi o repositorio" e
# "estou marcando um horario na interface" a distancia de um comando.

FROM python:3.12-slim

WORKDIR /app

# Copia so o requirements primeiro: o cache de camada do Docker
# reaproveita a instalacao de dependencias enquanto so o codigo
# mudar, sem reinstalar tudo a cada build.
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY . .

EXPOSE 8000

# Aplica as migrations (Etapa 4, alembic/) antes de subir a API --
# um banco recem-criado pelo docker-compose comeca vazio, sem
# tabelas, entao isso precisa rodar toda vez que o container sobe.
CMD ["sh", "-c", "alembic upgrade head && uvicorn app.main:app --host 0.0.0.0 --port 8000"]
