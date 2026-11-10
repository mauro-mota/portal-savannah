#!/bin/sh
set -eu
cd "$(dirname "$0")"
if [ "$(id -u)" != 0 ]; then echo 'Execute como root na VPS.'; exit 1; fi
if [ "$PWD" != /root/portal-empresa ]; then echo 'Este agendamento espera /root/portal-empresa.'; exit 1; fi
if [ -e /etc/cron.d/portal-empresa ]; then echo 'Agendamento já existe. Nada alterado.'; exit 0; fi
cat > /etc/cron.d/portal-empresa <<'EOF'
SHELL=/bin/sh
PATH=/usr/local/sbin:/usr/local/bin:/usr/sbin:/usr/bin:/sbin:/bin
0 6 * * * root cd /root/portal-empresa && sh backup.sh >> /var/log/portal-backup.log 2>&1
EOF
chmod 644 /etc/cron.d/portal-empresa
echo 'Backup agendado às 06h no fuso da VPS. Copie os backups para fora do servidor.'
