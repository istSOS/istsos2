# This Python file uses the following encoding: utf-8

import sys
import os
import numpy as np
import pprint
from SOSutils import ts_utils
from SOS import sosDatabase
from SOS.config import sosConfig
from SOS import sosException
from SOSutils.acquisition.conf import *
#from SOSutils.acquisition.conf import LastUpdate
from SOSutils.acquisition import FtpWorker
from SOSutils.acquisition import RunReader
from SOSutils.acquisition.log import logger
from datetime import datetime, date, time

print "*******************************************************"
print "RUNACQUISITION ON DATE: %s" % datetime.now()
print "*******************************************************"
lastUpFile = sosConfig.acq["lastUpFile"] # '/usr/lib/python2.6/SOSutils/acquisition/conf/LastUpdate.py'
backUpPath = sosConfig.acq["rawPath"] #'/var/www/sos/raw/' # last back slash is mandatory !

oggi = logger.resetLog()

procOk = {}
procOk = FtpWorker.main()

"""  
if not FtpWorker.main():
    sys.exit(2)
  
try:
"""    

readObj = RunReader.main(procOk)
procOk = readObj['logObj']
statReaders = readObj['readers']

if(len(statReaders)>0):
    procOk
    logger.titleLog("3. Ricampionamento e inserimento delle osservazioni nel database")
    print "\n Preparing for resampling and inserting"
    print " --------------------------------------\n"
    start = datetime.now()
    for key in statReaders:
        readers = statReaders[key]
        stationCheck = True
        for rd in readers:
            if stationCheck:
                start_date = rd.prevUpdate
                end_date = rd.lastUpdate
                dates = rd.getMeasuresDatesArray()
                vals = rd.getMeasuresValuesArray()
                obsProperty = rd.getObs()
                procedure = rd.getObs() + "_" + rd.name
                frunit = int(rd.type["min"])
                #print "----------------\n"
                #print vals
                #print dates
                #print "----------------\n"            
                print "  " + procedure
                print "  - start_date = %s" % start_date
                print "  - end_date = %s" % end_date
                print "  - frunit = %s" % frunit
                print "  - date = %s" % len(dates)
                print "  - data = %s" % len(vals)
                if len(dates)>0:
                    print "  - First value = %s" % vals[0]
                    print "  - First date = %s" % dates[0]
                    print "  - Last value = %s" % vals[len(vals)-1]
                    print "  - Last date = %s" % dates[len(vals)-1]
                print "  - obsProperty = %s" % obsProperty
                print "  - procedure = %s" % procedure
                print ""
                
                logger.infoLog(" - Preparazione di %s: " % (procedure))
                
                ts = ts_utils.istSOSserie()
                ts.setArray(start_date,end_date,dates,vals,obsProperty,procedure)
                #print ts.tserie.data
                #print ts.tserie.dates
                
                # se pioggia -> resample!
                # resample(frequency="M",frunit=10,mode="ave",fill_null=None,start_date=None,end_date=None)
                
                if obsProperty=="P":
                    logger.infoLog("    - Ricampionamento : ", False)
                    print " - Resampling (SUM) rain data with frunit = " + str(frunit)
                    ts.resample("T", frunit, "sum", 0)
                    logger.infoLog("OK")
                    
                    
                #def resample(self,frequency="M",frunit=10,mode="mean",fill_null=None,start_date=None,end_date=None):
            
                #ts.resample("T", frunit, "sum")
                #print "--------------------"
                #ts.tserie.mask=False
                #print ts.tserie.dates
                #print "********************************************"
                #print ts.tserie.data
                #ts.tserie.fill_missing_data(fill_value=0)
                #print ts.tserie["12-Oct-2009 07:10":"13-Oct-2009 18:00:00"].sum(0,float)
                #print "********************************************"
                #print ts.tserie.filled()
                #print "********************************************"
                if not procOk.has_key(rd.name):
                    procOk[rd.name] = {}
                procOk[rd.name]['DB'] = False
                try:
                    logger.infoLog("    - Inserimento DB: ", False)
                    pgdb = sosDatabase.sosPgDB(sosConfig.connection["user"],
                                       sosConfig.connection["password"],
                                       sosConfig.connection["dbname"],
                                       sosConfig.connection["host"],
                                       sosConfig.connection["port"])
                    ts.insert_fix_measure(pgdb,"meteoist")
                    logger.infoLog("OK")
                    procOk[rd.name]['DB'] = True
                except:
                    dbExc = " - Eccezione durante l'inserimento delle osservazioni:\n\n"
                    dbExc += str(sys.exc_info()[0])
                    #logger.exceptLog(dbExc);
                    logger.exceptLog("\n    - Inserimento di %s -> DB ERROR: %s" % (procedure,str(sys.exc_info()[0])))
                    stationCheck = False
                    continue
                
                
                '''
                LastUpdate.lastUpdate[rd.name] = end_date.strftime("%d-%m-%Y %H:%M:%S")
                luc = open(lastUpFile, "w")
                luc.write("lastUpdate = %s" % pprint.pformat(LastUpdate.lastUpdate, 4, 2, 1))
                luc.close()
                '''
                
                # **********************************************************************
                # Organizza file di back up
                # **********************************************************************
                print "\n Storing historic raw data file"
                
                if not procOk.has_key(rd.name):
                    procOk[rd.name] = {}
                procOk[rd.name]['HIS'] = False
                
                backUpFilePath = None
                yr = None
                mt = None
                backUpFile = None
                #backNextDate = None

                ms = rd.getMeasuresIstSOS()
                print len(ms)
                logger.infoLog("    - Creazione file storici: ", False)
                try:
                    for m in ms:
                        #print ((yr == None) and (mt == None))
                        #print ((yr!=m.getEventime().year) or (mt!=m.getEventime().month))
                        if ((yr == None) and (mt == None)) or ((yr!=m.getEventime().year) or (mt!=m.getEventime().month)):
                            yr = m.getEventime().year
                            mt = m.getEventime().month
                            
                            #print "yr=" + str(yr)
                            #print "mt=" + str(mt)
                            
                            #backNextDate = datetime(yr, mt+1, 1, 0, 0)
                            
                            backUpFilePath = backUpPath+str(m.getEventime().year)+"/"+str(m.getEventime().month)
                            FtpWorker.makedir(backUpFilePath)
                            backUpFilePath = backUpFilePath + "/"+rd.getObs()+"_"+rd.name+".DAT"
                            print backUpFilePath
                            # Se esiste gia lo apro in append mode
                            if backUpFile != None:
                                backUpFile.close()
                            
                            if os.path.isfile(backUpFilePath):
                                backUpFile = open(backUpFilePath, "a")
                            else:
                                backUpFile = open(backUpFilePath, "w")
                            
                        backUpFile.write(m.csv())
                        backUpFile.write("\n")
                    if backUpFile != None:
                        backUpFile.close()
                    logger.infoLog("OK")
                    procOk[rd.name]['HIS'] = True
                except:
                    logger.infoLog("ERROR")
                    logger.exceptLog(" Creazione file storici di %s: ERROR" % procedure)
                        

                
                    
                
                
                if not procOk.has_key(rd.name):
                    procOk[rd.name] = {}
                procOk[rd.name]['LUP'] = False
                
                logger.infoLog("    - Aggiornamento dell'ultima data di inserimento: ", False)
                LastUpdate.lastUpdate[rd.name] = end_date.strftime("%d-%m-%Y %H:%M:%S")
                luc = open(lastUpFile, "w")
                luc.write("lastUpdate = %s" % pprint.pformat(LastUpdate.lastUpdate, 4, 2, 1))
                luc.close()
                logger.infoLog("OK")
                procOk[rd.name]['LUP'] = True
                
    logger.infoLog("\nDurata inserimento: " + str((datetime.now())-start))
    
    aloe = 'OK' # At least one error
    thead = "PROC\t"
    jone = True
    table = ""
    for lKey, lValue in procOk.items():
        table = table + lKey + "\t"
        for llKey, llValue in procOk[lKey].items():
            if jone:
                thead = thead + llKey + "\t"
            if llValue == False:
                aloe = "ERR"
                table = table + "ERR" + "\t" 
                #break
            else:
                table = table + "OK" + "\t" 
                
        table = table + "\n"
        jone = False
        #if aloe == "ERR":
        #    break
    table = thead+ "\n" + table
    import time
    time.sleep(10)
    logger.mail("milan.antonovic@gmail.com", "[ISTSOS] Acquisizione %s %s "  % (aloe, oggi), table) 
       
    print "1:\n%s" % table    
else:
    print "Error: Zero readers returned!!"
    sys.exit(2)
    

#logger.zipLogs(oggi.strftime('%d.%m.%Y_%H.%M'))
"""
except:
    print "Error while Trasforming Raw data: ", sys.exc_info()[0]
    sys.exit(2)
"""
