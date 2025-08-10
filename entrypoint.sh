#!/usr/bin/env sh
set -e

# Wait for dependencies if needed (e.g., databases). Not required for DynamoDB resource only.

python manage.py collectstatic --noinput
python manage.py migrate --noinput || true

exec "$@"

