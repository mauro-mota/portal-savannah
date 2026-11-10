#!/bin/sh
set -eu
cd "$(dirname "$0")"
if [ -f .env ]; then
  echo 'O .env já existe. Nada foi alterado; mantenha suas senhas atuais.'
  exit 0
fi
umask 077
portal_domain="${1:-localhost}"
case "$portal_domain" in
  *[!a-zA-Z0-9.-]*|'') echo 'Use somente o domínio, sem https://, espaços ou barras.'; exit 1;;
esac
production=0
hosts='localhost,127.0.0.1'
origins='http://localhost:8000,http://127.0.0.1:8000'
if [ "$portal_domain" != localhost ]; then
  production=1
  hosts="$portal_domain"
  origins="https://$portal_domain"
fi
cat > .env <<EOF
DJANGO_SECRET_KEY=$(openssl rand -hex 48)
POSTGRES_PASSWORD=$(openssl rand -hex 24)
POSTGRES_DB=portal
POSTGRES_USER=portal
PRODUCTION=$production
ALLOWED_HOSTS=$hosts
CSRF_TRUSTED_ORIGINS=$origins
PORTAL_DOMAIN=$portal_domain
EOF
echo 'Configuração criada. As senhas estão no .env; não compartilhe esse arquivo.'
