
import sys
from os import path
sys.path.append(path.abspath("/home/maxi/istsos_GC_SVN/trunk/webadmin/service/walibs"))

import waDatabase
import waConfig
import wapickle
from qicheck import qualityCheck
import datetime
import wapickle


pgdb=waDatabase.PgDB(waConfig.connection['user'],
                    waConfig.connection['password'],
                    waConfig.connection['dbname'],
                    waConfig.connection['host'],
                    waConfig.connection['port'])



qc0_list = wapickle.waunpickle('updateQC0.cfg')
now = datetime.datetime.utcnow().strftime("%Y-%m-%dT%H:%M:%S.%fZ")

for lev in qc0_list:
    #QCobj = qualityCheck.qualityCheck(pgdb,lev[0],lev[1])
    #QCobj.executeQC_IN(lb=lev[2],ub=lev[3],qcode=210,timeint=(lev[3],None))
    print "QCobj = qualityCheck.qualityCheck(pgdb,%s,%s)" %(lev[0],lev[1])
    print "QCobj.executeQC_IN(lb=%s,ub=%s,qcode=210,timeint=(%s, None))" %(lev[2],lev[3],lev[4])
    print "['%s','%s',%s,%s,'%s']" %(lev[0],lev[1],lev[2],lev[3],)



trevQC = qualityCheck.qualityCheck(pgdb,'P_TRE','urn:ogc:def:parameter:x-ist::meteo:air:rainfall')

trevQC.executeQC_IN(lb=0.8,ub=2,qcode=210,timeint=('2010-11-01T12:00+01','2011-11-01T23:00+01'))

trevQC.executeQC_IN(lb=0.8,ub=2,qcode=100,timeint=(None,'2011-05-28T12:00+01'))
