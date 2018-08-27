FROM python:3.7-stretch

# Copy python requirements file
COPY requirements.txt /tmp/requirements.txt

# install dependencies
RUN apt-get update && apt-get install -y \
    python-numpy \
    python-scipy \
    libffi-dev \
    libjpeg-turbo-progs \
    python-setuptools \
    python-dev \
    python3-dev \
    cmake \
    libtiff5-dev \
    libjpeg62-turbo-dev \
    zlib1g-dev \
    libfreetype6-dev \
    liblcms2-dev \
    libwebp-dev \
    tcl8.6-dev \
    tk8.6-dev \
    python-tk \
    python3-tk \
    libharfbuzz-dev \
    libfribidi-dev \
    nginx \
    uwsgi \
    uwsgi-plugin-python3 \
    supervisor \
    && pip3 install --upgrade pip setuptools \
    && pip3 install -r /tmp/requirements.txt \
    && apt-get clean


RUN groupadd -g 999 nginx && \
    useradd -r -u 999 -g nginx nginx

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
