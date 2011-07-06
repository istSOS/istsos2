from SOS import sosDatabase
from SOS.config import sosConfig

import numpy as np
from numpy import ma
import scikits.timeseries as ts
from datetime import datetime as dt
from datetime import timedelta as td


class UtuilsException(Exception):
    def __init__(self,ivalue,msg):
        Exception.__init__(self,ivalue,msg)
        self.value = ivalue
        print msg
    def __str__(self):
        return self.value    
    
def ts_resample(myts,start_date,end_date,tsval,tsfreq,mode,fill_null=None):
    """
    Aggregate a time series to a given frequency
      arguments:
        -myts: timeseries object
        -start_date: datetime object at timestep resolution
        -end_date: datetime object at timestep resolution
        -timestep: timedelta object
        -mode: aggregation mode (sum,mean,min,max)
        -fill_null: value to fill missing data
    """
    Tsampl=[]
    Vsampl=[]
    if fill_null:
        myts = myts.fill_missing_dates(fill_value=fill_null)
        
    if tsfreq in ["S", "SECOND", "SECONDLY"]:
        timestep = td(seconds=tsval)
        lowint=dt(start_date.year,start_date.month,start_date.day,start_date.hour,start_date.minute,start_date.second)
        format="%Y-%m-%d %H:%M:%s.000001"
    elif tsfreq in ["T", "MINUTE", "MINUTELY"]:
        timestep = td(minutes=tsval)
        lowint=dt(start_date.year,start_date.month,start_date.day,start_date.hour,start_date.minute)
        format="%Y-%m-%d %H:%M:00.000001"
        #print "===================="
        #print "%s-%s-%s\n" %(timestep,lowint,format)
        #print "===================="
    elif tsfreq in ["H", "HOUR", "HOURLY"]:
        timestep = td(hours=tsval)
        lowint=dt(start_date.year,start_date.month,start_date.day,start_date.hour)
        format="%Y-%m-%d %H:00:00.000001"
    elif tsfreq in ["D", "DAY", "DAILY"]:
        timestep = td(days=tsval)
        lowint=dt(start_date.year,start_date.month,start_date.day)
        format="%Y-%m-%d %00:00:00.000001"
        
    if mode=="sum":
        while (lowint+timestep) <= end_date:
            #print "P:%s-%s" %(lowint.strftime(format),upint.strftime(format))
            upint=lowint+timestep
            #print "%s|%s=%s|%s=%s\n" %(lowint.strftime(format),lowint,upint.strftime(format),upint,format)
            Vsampl.append(myts[lowint.strftime(format):upint.strftime(format)].sum())
            Tsampl.append(upint)
            #print " %s,%s,%s,%s,%s,%s\n" %(Vsampl[-1],Tsampl[-1],myts[lowint.strftime(format):upint.strftime(format)],lowint.strftime(format),upint.strftime(format),timestep)
            lowint=upint
    elif mode=="mean":
        while lowint+timestep <= end_date:
            upint=lowint+timestep
            Vsampl.append(myts[lowint.strftime(format):upint.strftime(format)].mean())
            Tsampl.append(upint)
            lowint=upint
    elif mode=="max":
        while lowint+timestep <= end_date:
            upint=lowint+timestep
            Vsampl.append(myts[lowint.strftime(format):upint.strftime(format)].max())
            Tsampl.append(upint)
            lowint=upint
    elif mode=="min":
        while lowint+timestep <= end_date:
            upint=lowint+timestep
            Vsampl.append(myts[lowint.strftime(format):upint.strftime(format)].min())
            Tsampl.append(upint)
            lowint=upint
    else:
        raise UtuilsException(1,"mode not supported")
    Dsampl = ts.date_array(dlist=Tsampl,autosort=False,freq=tsfreq)
    return ts.time_series(Vsampl,Dsampl)

def fixTs2istSOS(fixts,procedure_id=None,procedure_name=None,qi=0,id_geom=None,tz=None):
    """
    get a TimeSeries and insert observation into the SOS database
      arguments:
          - fixts: time series
          - procedure_id: id of the procedure the TimeSerie belong 
          - procedure_name: name of the procedure the TimeSerie belong
          - qi = quality index of the TimeSerie
          - id_geom = id of the geometry they were observed at
          - tz = time zone of the TimeSeries datetime values
    """
    pgdb = sosDatabase.sosPgDB(sosConfig.connection["user"],
                           sosConfig.connection["password"],
                           sosConfig.connection["dbname"],
                           sosConfig.connection["host"],
                           sosConfig.connection["port"])

    if not tz:
        tz=""
    
    if not procedure_name and procedure_id:
        sql = "INSERT INTO %s.measures (id_qi_fk,id_prc_fk,id_geom_fk,time_msr,val_msr)" %(sosConfig.schema)
        sql += " VALUES (%(qi)s, %(id_proc)s, %(id_geom)s, %(t)s::timestamptz, %(val)s )"
    
    elif not procedure_id and procedure_name:
        sql = "INSERT INTO %s.measures (id_qi_fk,id_prc_fk,id_geom_fk,time_msr,val_msr)" %(sosConfig.schema)
        sql += " SELECT %(qi)s, id_prc, %(id_geom)s, %(t)s::timestamptz, %(val)s"
        sql += " FROM %s.procedures" %(sosConfig.schema)
        sql += " WHERE name_prc=%(name_pr)s"
        
    else:
        raise UtuilsException(1,"one of procedure name or id is required") 
           
    l = []    
    for i in range(len(fixts)):
        d = {'qi' : qi,
             'id_proc' : procedure_id,
             'id_geom' : id_geom,
             't' : fixts.dates[i].strftime("%Y-%m-%d %H:%M:%S"+tz),
             'val' : str(fixts.data[i]),
             'name_pr' : procedure_name
             }
        #print "%s" %(d)
        l.append(d)
    dicto = tuple(l)
    del l
    #print "%s\n" %(sql)
    pgdb.insertMany(sql,dicto)
    return True


