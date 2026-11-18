#!/bin/bash
set -e

cd /var/www/html

# Instala las dependencias. En desarrollo el código se monta desde el computador,
# y la carpeta vendor de la imagen queda tapada, por eso se instalan otra vez.
composer install --no-interaction --prefer-dist --optimize-autoloader

# Permisos de escritura para Laravel.
# El || true evita que el contenedor se detenga si el disco no deja cambiar el dueño.
chown -R www-data:www-data storage bootstrap/cache || true

exec docker-php-entrypoint apache2-foreground