FROM python:3.7-alpine

# Copy python requirements file
COPY requirements.txt /tmp/requirements.txt

# install dependencies
RUN apk --no-cache add \
    # Pillow dependencies
    jpeg-dev \
    zlib-dev \
    freetype-dev \
    # hosting dependencies
    nginx \
    supervisor \
    && apk add --no-cache --virtual .build-deps \
        musl-dev \
        g++ \
        linux-headers \
    && pip install -r /tmp/requirements.txt \
    && apk del .build-deps \
    && rm /etc/nginx/conf.d/default.conf \
    && rm -r /root/.cache

# Copy the Nginx global conf
COPY nginx.conf /etc/nginx/
# Copy the Flask Nginx site conf
COPY flask-site-nginx.conf /etc/nginx/conf.d/
# Copy the base uWSGI ini file to enable default dynamic uwsgi process number
COPY uwsgi.ini /etc/uwsgi/
# Custom Supervisord config
COPY supervisord.conf /etc/supervisord.conf

# Add app
COPY ./src /src
WORKDIR /src

CMD ["/usr/bin/supervisord"]
EXPOSE 80
