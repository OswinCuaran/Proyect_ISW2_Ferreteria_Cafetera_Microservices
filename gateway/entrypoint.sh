#!/bin/bash
set -e
cd /var/www/html
composer install --no-interaction --prefer-dist --optimize-autoloader
grep -q '^APP_KEY=base64:' .env || php artisan key:generate --force
php artisan migrate --force --seed
chown -R www-data:www-data storage bootstrap/cache || true
exec docker-php-entrypoint apache2-foreground