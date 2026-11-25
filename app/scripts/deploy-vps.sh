#!/usr/bin/env bash
set -Eeuo pipefail

root_dir=$(git -C "$(dirname "${BASH_SOURCE[0]}")/.." rev-parse --show-toplevel)
cd "$root_dir"

if [[ ! -f .env ]]; then
  echo "Brak .env. Skopiuj .env.example do .env i uzupełnij sekrety przed wdrożeniem." >&2
  exit 1
fi

if [[ ! -f .env.mail ]]; then
  install -m 600 .env.mail.example .env.mail
  echo "Utworzono prywatny .env.mail z pustymi ustawieniami SMTP."
fi

compose=(sudo docker compose --env-file .env -f docker-compose.production.yml -f docker-compose.nginx.yml)
backup_compose='docker compose --env-file .env -f docker-compose.production.yml -f docker-compose.nginx.yml'

sudo install -d -m 0700 /srv/ad/backups
sudo env COMPOSE_COMMAND="$backup_compose" BACKUP_DIR=/srv/ad/backups ./scripts/backup-postgres.sh

"${compose[@]}" config -q
"${compose[@]}" up -d --build

for service_path in 'backend /health' 'frontend /_health'; do
  read -r service path <<< "$service_path"
  "${compose[@]}" exec -T "$service" python -c \
    'import sys,time,urllib.error,urllib.request; url="http://127.0.0.1:8000"+sys.argv[1] if sys.argv[2]=="backend" else "http://127.0.0.1:5000"+sys.argv[1]; last=None
for _ in range(30):
 try:
  response=urllib.request.urlopen(url, timeout=3)
  if response.status == 200: print(sys.argv[2]+" health check: OK"); break
 except Exception as error: last=error; time.sleep(2)
else: raise SystemExit(sys.argv[2]+" health check failed: "+str(last))' "$path" "$service"
done

"${compose[@]}" ps
echo "Wdrożenie zakończone. Sprawdź publiczne adresy app i api przez HTTPS."
