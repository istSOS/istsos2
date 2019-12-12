#!/bin/bash

# required

# Remove the x flag on install
chmod -x debian/install

# sudo apt-get install devscripts
# sudo apt-get install debhelper

revision=$(git rev-list --count HEAD)
version=$(cat ./VERSION.txt)
datetime=$(LC_TIME=en_US date +"%a, %e %b %Y %T %z")
itp=$(LC_TIME=en_US date +"%Y%m%d")

rm -rf _build

mkdir _build
mkdir _build/istsos
mkdir _build/istsos/interface
mkdir _build/istsos/interface/modules
mkdir _build/istsos/logs
mkdir _build/istsos/services

rsync -a interface/admin/www/* _build/istsos/interface/admin
rsync -a interface/modules/requests/build/requests/* _build/istsos/interface/modules/requests
cp -r interface/modules/requests/src/xml _build/istsos/interface/modules/requests
# rsync -a interface/modules/status/www/istsosStatus/* _build/istsos/interface/modules/status
rsync -a --exclude=*.pyc istsoslib/* _build/istsos/istsoslib
rsync -a --exclude=*.pyc scripts/* _build/istsos/scripts
cp services/default.cfg.example  _build/istsos/services/default.cfg
rsync -a --exclude=*.pyc walib/* _build/istsos/walib
rsync -a --exclude=*.pyc wnslib/* _build/istsos/wnslib
cp *.py  _build/istsos/
cp *.txt  _build/istsos/

cd _build
rm -rf `find . -type d -name .svn`
tar -zcvf istsos_$version.orig.tar.gz istsos

cd ..
cp -rf debian _build/istsos/debian

sed -i 's/VERSION/'"$version"'/g' _build/istsos/debian/changelog
sed -i 's/ITP/'"$itp"'/g' _build/istsos/debian/changelog
sed -i 's/DATETIME/'"$datetime"'/g' _build/istsos/debian/changelog
sed -i 's/VERSION/'"$version"'/g' _build/istsos/debian/files

cd _build/istsos
debuild -us -uc -d
cd ..

mv python3-istsos_$version-1_all.deb python3-istsos_$version.deb

mv istsos_$version.orig.tar.gz istsos-$version.tar.gz
# rm -rf istsos

# cd ../docs

# make html
# cd _build
# mv html v$version
# tar -zcvf istsos-$version.doc.tar.gz v$version

# mv istsos-$version.doc.tar.gz ../../_build/



