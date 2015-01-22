# APSScheduler - Correcting imports in python files
find lib/apscheduler/ -name '*.py' -print0 | xargs -0 -n 1 sed -i -e 's/from apscheduler/from lib.apscheduler/g'
find lib/pytz/ -name '*.py' -print0 | xargs -0 -n 1 sed -i -e 's/from pytz/from lib.pytz/g'
find lib/pytz/ -name '*.py' -print0 | xargs -0 -n 1 sed -i -e 's/import pytz/import lib.pytz/g'
