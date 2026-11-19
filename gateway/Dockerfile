FROM php:8.4-apache

# Dependencias del sistema y extensiones de PHP que necesita Laravel
RUN apt-get update && apt-get install -y \
    git unzip libpng-dev libonig-dev libxml2-dev libicu-dev \
    && docker-php-ext-install pdo_mysql mbstring bcmath gd intl \
    && a2enmod rewrite \
    && sed -ri -e 's!/var/www/html!/var/www/html/public!g' /etc/apache2/sites-available/*.conf \
    && sed -ri -e 's!AllowOverride None!AllowOverride All!g' /etc/apache2/apache2.conf \
    && sed -ri -e 's!Listen 80!Listen 8000!g' /etc/apache2/ports.conf \
    && sed -ri -e 's!<VirtualHost \*:80>!<VirtualHost *:8000>!g' /etc/apache2/sites-available/000-default.conf \
    && rm -rf /var/lib/apt/lists/*

# Composer copiado desde su imagen oficial
COPY --from=composer:2 /usr/bin/composer /usr/bin/composer
# Carpeta de trabajo dentro del contenedor
WORKDIR /var/www/html
# Copia el código dentro de la imagen
COPY . .
# Instala las dependencias de Laravel
RUN composer install --no-interaction --prefer-dist --optimize-autoloader
# Script de arranque
COPY entrypoint.sh /usr/local/bin/laravel-entrypoint.sh
RUN chmod +x /usr/local/bin/laravel-entrypoint.sh
# Puerto del Gateway
EXPOSE 8000
ENTRYPOINT ["laravel-entrypoint.sh"]