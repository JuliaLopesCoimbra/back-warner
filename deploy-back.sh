#!/bin/bash
set -e

# Carrega variáveis de ambiente do arquivo .env.deploy (não versionado)
ENV_FILE="$(dirname "$0")/.env.deploy"
if [ -f "$ENV_FILE" ]; then
  set -a
  source "$ENV_FILE"
  set +a
else
  echo "Erro: arquivo $ENV_FILE não encontrado."
  echo "Crie o arquivo com as variáveis: DATABASE_URL, CORS_ORIGINS, APP_SECRET"
  exit 1
fi

echo "==> git pull"
git pull

echo "==> Parando container antigo (se existir)"
sudo docker stop back-warner 2>/dev/null || true
sudo docker rm   back-warner 2>/dev/null || true

echo "==> Build da imagem"
sudo docker build -t back-warner .

echo "==> Iniciando container"
DOCKER_ENV=(-e "DATABASE_URL=$DATABASE_URL" -e "APP_SECRET=$APP_SECRET")
[ -n "$CORS_ORIGINS" ] && DOCKER_ENV+=(-e "CORS_ORIGINS=$CORS_ORIGINS")

sudo docker run -d \
  --name back-warner \
  -p 8001:8000 \
  --restart always \
  "${DOCKER_ENV[@]}" \
  back-warner

echo "==> Logs (Ctrl+C para sair)"
sudo docker logs -f back-warner
