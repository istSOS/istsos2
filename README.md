# istsos2
Easily manage your sensor network and distribute your data in a standard way

istSOS is an OGC SOS server implementation written in Python. istSOS allows for managing and dispatch observations from monitoring sensors according to the Sensor Observation Service standard.

The project provides also a Graphical user Interface that allows for easing the daily operations and a RESTful Web api for automatizing administration procedures.

For further information, please refer to the istSOS website: <http://istsos.org/>

istSOS is released under the GPL License, and runs on all major platforms (Windows, Linux, Mac OS X), even though tests were conducted under a Linux environment.


> Newer version of istSOS will contain Sensor Things API OGC service. Will be updated soon!

## Start istSOS with docker-compose

The faste way to use istSOS is with docker.

Create a docker-compose.yml file:

```bash
version: '3.7'

services:
  istsos-db:
    image: postgis/postgis:12-2.5-alpine
    restart: always
    container_name: istsos-db
    environment:
      POSTGRES_USER: postgres
      POSTGRES_PASSWORD: postgres
      POSTGRES_DB: istsos
      TZ: Europe/Zurich
    volumes:
      - istsos-db-data:/var/lib/postgresql/data

  istsos:
    image: istsos/istsos:2.4.2
    container_name: istsos
    restart: always
    ports:
      - 80:80

volumes:
    istsos-db-data:
        name: istsos-db-data

```

And start the containers by running the following command:


```bash
docker-compose up -d
```

Open your browser and go to http://localhost/istsos/admin you should be able to see the web admin page.
Before creating a new istsos service instance go to the "Database" page and set "istsos-db" as Host.

## To build the docker image from source

clone the repository

```bash
git clone https://github.com/istSOS/istsos2.git
cd istsos2
```

Build the image with docker

```bash
version=$(cat ./VERSION.txt)
docker build --no-cache -t istsos/istsos:$version .
```

## Push to docker hub

```bash
version=$(cat ./VERSION.txt)
docker build --no-cache -t istsos/istsos:$version .
docker push istsos/istsos:$version
```

Tag latest and push

```bash
docker image tag istsos/istsos:$version istsos/istsos:latest
docker push istsos/istsos:latest
```
