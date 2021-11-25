# Create the virtualenv with docker

Build the images

```bash
version=$(cat ./VERSION.txt)
docker build --no-cache \
  -t ghcr.io/istsos/istsos2/istsos-scripts:$version .
```

Publish

```bash
version=$(cat ./VERSION.txt)
docker push ghcr.io/istsos/istsos2/istsos-scripts:$version
docker tag ghcr.io/istsos/istsos2/istsos-scripts:$version \ 
    ghcr.io/istsos/istsos2/istsos-scripts:latest
docker push ghcr.io/istsos/istsos2/istsos-scripts:latest
```

Run in interactive mode:


```bash
docker run --rm -it \
  --network="host" \
  -w /app \
  ghcr.io/istsos/istsos2/istsos-scripts:latest /bin/bash
```

## Update foi 

Update the coordinates taking as input a csv configuration file.

Given a CSV file like this:

```csv
A_AETCAN_AIR,AET,691140,153780,1140,21781
A_BOL_PTC,PortoCeresio ,712688,84295,290,21781
A_BOL_PTC_LAM,Porto Ceresio (Italia) ,712560,83610,290,21781
A_BOL_R_PTC,PortoCeresio,712688,84295,290,21781
A_BON_QUA,Quartino,713525,113128,201,21781
A_CAL_AIR,Batola,692060,152560,1100,21781
```

And a yaml file like this:

```yaml
database:
    host: localhost
    port: 9434
    user: postgres
    password: postgres
    dbname: istsos
    schema: defmin

folders:
    services: /services
    csv: /data/locations.csv
```

```bash
docker run --rm -it \
  --network="host" \
  -v /folder/where/the/csv/is/located/:/data/  \
  -v /folder/where/the/istsos/service/folder/is/located/:/services/  \
  -w /app/scripts \
  ghcr.io/istsos/istsos2/istsos-scripts:latest \
  python update-coordinates.py /data/config.yaml
```


Run the acquisition script

```bash
docker run --rm -it \
  --network="host" \
  -v $PWD/acquisition:/app/acquisition  \
  -v /home/milan/workspace/istsos/istsos2/scripts:/app/scripts  \
  -v /mnt/acq/:/mnt/acq/  \
  -w /app \
  ghcr.io/istsos/istsos2/istsos-scripts:latest \
  python ./acquisition/acquisition.py
```

Move data from one istsos to one other

```bash
docker run --rm -it \
  --network="host" \
  -v /home/milan/workspace/istsos/istsos2/scripts:/app/scripts  \
  -w /app \
  ghcr.io/istsos/istsos2/istsos-scripts:latest \
  python scripts/istsos2istsos.py -v \
    -procedure T_TRE \
    --function AVG \
    --resolution PT1H \
    -nv -999.9 \
    -b 2019-08-05T15:00:00+02:00 \
    --surl http://localhost/istsos \
    --ssrv sosraw \
    --dsrv sos \
    --suser admin \
    --spwd my_secret \
    --duser admin \
    --dpwd my_secret
```
