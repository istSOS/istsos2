#BUILD WITH: 'docker build -t istsos-web:v1.0.0 -f Dockerfile .'
#RUN WITH: 'docker run --rm -d --name istsos-web-c -p 80:80 istsos-web:v1.0.0'
#RUN TO DEBUG: 'docker run --rm -it --name istsos-web-c -p 80:80 istsos-web:v1.0.0 bash'

# Build Stage
FROM debian:buster as build-stage

RUN apt-get update && \
    apt-get install -y rsync grsync

WORKDIR /app

COPY ./ /app/

RUN rm -rf _build && \
    mkdir -p _build/istsos/interface/admin && \
    mkdir _build/istsos/interface/modules && \
    mkdir _build/istsos/logs && \
    mkdir _build/istsos/services && \
    cp -r interface/admin/www/* _build/istsos/interface/admin && \
    cp -r interface/modules/requests/src/xml _build/istsos/interface/modules/requests && \
    rsync -a --exclude=*.pyc istsoslib/* _build/istsos/istsoslib && \
    rsync -a --exclude=*.pyc scripts/* _build/istsos/scripts && \
    cp services/default.cfg.example  _build/istsos/services/default.cfg && \
    rsync -a --exclude=*.pyc walib/* _build/istsos/walib && \
    rsync -a --exclude=*.pyc wnslib/* _build/istsos/wnslib && \
    cp *.py  _build/istsos/ && \
    cp *.txt  _build/istsos/ && \
    cp httpd-istsos.conf _build/istsos/ && \
    cd _build && \
    rm -rf `find . -type d -name .svn`

FROM httpd:2.4.48-alpine3.14

WORKDIR /usr/share

COPY --from=build-stage /app/_build/ /usr/share/

RUN chmod 755 -R /usr/share/istsos && \
    chown -R daemon:daemon /usr/share/istsos/services && \
    chown -R daemon:daemon /usr/share/istsos/logs && \
    mkdir /usr/local/apache2/conf/sites-available /usr/local/apache2/conf/sites-enabled && \
    mkdir -p /var/www/html && \
    echo "LoadModule wsgi_module /usr/lib/apache2/mod_wsgi.so" >> /usr/local/apache2/conf/httpd.conf && \
    echo "IncludeOptional /usr/local/apache2/conf/sites-enabled/*.conf " >> /usr/local/apache2/conf/httpd.conf && \
    cp /usr/share/istsos/httpd-istsos.conf /usr/local/apache2/conf/sites-available && \
    ln -s /usr/local/apache2/conf/sites-available/httpd-istsos.conf /usr/local/apache2/conf/sites-enabled/httpd-istsos.conf
    
RUN apk update && \
    set -ex && \   
    apk add --no-cache \
        apache2-mod-wsgi \
        py3-pip \
        musl \
        xz-libs \
        zlib \
        libxml2-dev \
        libxslt \
        libc-dev \
        py3-lxml \
        libxslt-dev \ 
        postgresql-dev \
        gcc \
        python3-dev \
        musl-dev
RUN pip3 install -r /usr/share/istsos/requirements.txt

EXPOSE 80
