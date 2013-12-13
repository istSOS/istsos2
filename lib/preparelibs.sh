# APSScheduler - Correcting imports in python files
find lib/apscheduler/ -name '*.py' -print0 | xargs -0 -n 1 sed -i -e 's/from apscheduler/from lib.apscheduler/g'
