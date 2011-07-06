cp /home/ist/Desktop/istSOS-SVN/trunk/dist/istSOS-1.0-rc1.2.tar.gz /home/ist/Downloads/
cd /home/ist/Downloads/
tar -xvzf istSOS-1.0-rc1.2.tar.gz istSOS-1.0-rc1.2
cd istSOS-1.0-rc1.2
rm -rf /usr/local/lib/python2.6/dist-packages/istSOS-1.0_rc1.2-py2.6.egg
python setup.py install
/etc/init.d/apache2 restart
