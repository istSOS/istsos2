# Create the virtualenv with docker

Build the images

```bash
docker build --no-cache \
  -t docker.pkg.github.com/istsos/istsos2/istsos-scripts:2.4.1 .
```

Publish

```bash
docker push docker.pkg.github.com/istsos/istsos2/istsos-scripts:2.4.1
```

Run the script
```bash
docker run --rm -it \
  --network="host" \
  -v $PWD/acquisition:/app/acquisition  \
  -v /home/milan/workspace/istsos/istsos2/scripts:/app/scripts  \
  -v /mnt/acq/:/mnt/acq/  \
  -w /app \
  istsos/istsos-scripts:2.4.1 \
  python ./acquisition/acquisition.py
```
