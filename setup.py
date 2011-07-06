import os
from setuptools import setup, find_packages

version = '1.1rc2'

README = os.path.join(os.path.dirname(__file__), 'README')
long_description = open(README).read() + 'nn'

setup(name='istSOS',
      version=version,
      description=("A Sensor Observation Service V 1.0 (SOS) implementation"),
      long_description=long_description,
      classifiers=[
        "Programming Language :: Python",
        ("Topic :: Software Development :: Libraries :: Python Modules"),
        ],
      keywords='SOS OGC',
      author='Massimiliano Cannata, Milan Antonovic',
      author_email='istSOS@gmail.com',
      url='http://istgeo.ist.supsi.ch/istSOS/',
      license='GPLv2',
      packages=["istSOS","istSOS.filters","istSOS.renderers","istSOS.responders"],
      package_data = {'' : ["service","database","testClient"] },
      install_requires=['psycopg2','isodate','GDAL','pytz']
      )

