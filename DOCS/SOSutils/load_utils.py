import numpy as np
from numpy import ma
import scikits.timeseries as ts
import sys, os, os.path, operator
from datetime import datetime as dt
from datetime import timedelta as td
import SOSutils, SOS
from SOS import sosDatabase
from SOS.config import sosConfig
from SOSutils import ts_utils as ld

def loadFixDataFolder(path):
    if os.path.exists (path) :
        files = os.listdir(path)
    else:
        raise SOSutils.UtuilsException(1,"path does not exists")
    """ GET ALL FILES IN FOLDER """
    for file in files :
        fullfile = os.path.join(path, file)
        if os.path.isfile(fullfile):
            """ LOAD DATA AT 10min freq """
            loadFixDataFile(fullfile)
            
    return True
            

def loadFixDataFile(filename):
    """========================================================"""
    """ parse, resample at 10 minutes, and insert observations """
    """ from file lines formatted as: 10/05/2009 18:56:44 0.1  """
    """ and filename as: P_BED@YYYYMMDDHHmmSS.dat              """
    """========================================================"""
    msr_geo_id={'P_BED':1,'P_OLI':2,'P_FUS':3,'P_LOD':4,'P_GNO':5,
		'P_MAG':6,'P_CAM':7,'P_CHI':8,'P_ARO':9,'P_SOM':10,'P_FRA':11,
		'R_CAV':12,'P_CAV':13,'U_CAV':14,'T_CAV':15,'P_MEN':16,'P_GIU':17,
		'P_PAL':18,'P_SAM':19,'P_LUZ':20,'P_CAD':21,'P_CVM':22,'P_ISO':23,
		'T_ISO':24,'T_NOV':25,'P_NOV':26,'P_CAR':27,'T_CAR':28,'T_COL':29,
		'P_COL':30,'P_GRA':31,'T_GRA':32,'T_PON':33,'P_PON':34,'B_TRE':35,
		'T_TRE':36,'U_TRE':37,'P_TRE':38}

    if not os.path.isfile(filename):
        raise sosUtils.UtuilsException(1,"File not found")
    
    """ READ FILE """
    try:
    	data=np.loadtxt(filename, dtype={'names': ('date', 'time', 'val'), 'formats': ('S10', 'S8', 'f4')})
    except:
    	return False
    
    """ CREATE RAW TIMESERIES """
    #convert date format
    T = [dt.strptime("%s %s" %(d['date'],d['time']),"%d/%m/%Y %H:%M:%S") for d in data]
    #create date array
    dates = ts.date_array(dlist=T,autosort=False,freq='SECOND')
    #create values array
    vals = [d[2] for d in data]
    #create regular timeseries every minute filling missing values with 0
    rawts = ts.time_series(vals,dates)
    
    """ GET PROCEDURE INFOS """
    finfo = filename.split("/")[-1].split('@')
    procedure_name = finfo[0]
    end = dt.strptime(finfo[1].split(".")[0], "%Y%m%d%H%M%S")
    end_datetime = dt(end.year,end.month,end.day,end.hour,end.minute-end.minute%10,00,00)
    pgdb = sosDatabase.sosPgDB(sosConfig.connection["user"],
	                   sosConfig.connection["password"],
	                   sosConfig.connection["dbname"],
	                   sosConfig.connection["host"],
	                   sosConfig.connection["port"])
    
    sql  = "SELECT max(time_msr)::text as begin FROM %s.measures,%s.procedures" %(sosConfig.schema,sosConfig.schema)
    sql += " WHERE id_prc=id_prc_fk and name_prc='%s'" %(procedure_name)
    
    try:
	    res = pgdb.execute(sql)
	    start_datetime = dt.strptime(res["begin"][0], "%Y-%m-%d %H:%M:%S")
    except:
	    print "WARNING: no measure found in DB"
    start=min(rawts.dates)
    start_datetime = dt(start.year,start.month,start.day,start.hour,start.minute-start.minute%10,00,00)
    
    """ CREATE 10minutes TIMESERIES """
    """ aggregate with sum if rain  """
    """ or mean elsewhere           """
    if procedure_name[0]=="P":
	ts10min = ld.ts_resample(rawts,start_date=start_datetime,end_date=end_datetime,
	                         tsval=10,tsfreq="MINUTE",mode="sum",fill_null=0)
    else:
	ts10min = ld.ts_resample(rawts,start_date=start_datetime,end_date=end_datetime,
	                         tsval=10,tsfreq="MINUTE",mode="mean",fill_null=0)
    
    """ INSERT OBSERVATION INTO istSOS DB """
    ld.fixTs2istSOS(fixts=ts10min,procedure_name=procedure_name,qi=1,id_geom=msr_geo_id[procedure_name])
    
    return True

    
    
    
