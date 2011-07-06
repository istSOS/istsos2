
#from SOS.responders import GOresponse
import sys
from SOS.config import sosConfig
from SOSutils import utils_override as _uo
from SOS import sosException

import matplotlib.pyplot as plt
import scikits.timeseries as ts
import scikits.timeseries.lib.plotlib as tpl

from datetime import datetime
from datetime import timedelta
from dateutil.relativedelta import relativedelta
import pytz
import isodate as iso

from dateutil.rrule import *
from dateutil.parser import *

import numpy as np
from numpy import ma

utc = pytz.utc


#===================#
#  UtuilsException  #
#===================#

class UtuilsException(Exception):
    def __init__(self,ivalue,msg):
        Exception.__init__(self,ivalue,msg)
        self.value = ivalue
        print msg
    def __str__(self):
        return self.value 

#===============#
#  istSOSserie  #
#===============#

class istSOSserie:
    """
    convert GO.response.observation object to time series
    """
    def __init__(self):
        """
        convert an observation in a time series object
        arguments:
            -obs: GO.response.observation object
        """
        self.property=None
        self.procedure=None
        self.station=None
        self.start_date=None
        self.end_date=None
        self.tserie=None
        self.uom=None
    
    """======================================================================"""
        
    def setObs(self,obs):
        """
        set property according to SOS observation
        """
        #print "*********************************"
        #print "%s - has %s data!\n" %(obs.procedure,len(obs.data))
        #print "*********************************"
        self.property = obs.observedProperty
        self.uom = obs.uom
        self.procedure = obs.procedure.split(":")[-1]
        for f in obs.foi_urn:
            if f.split(":")[-2]=="station":
                self.station=f.split(":")[-1]
        
        _times=[]
        _values=[]
        if len(obs.data)>0:
            #print "========================="
            #print "%s - has %s data!\n" %(obs.procedure,len(obs.data))
            for d in obs.data:
                _times.append(iso.datetime_isoformat(d[0]))
                _values.append(d[1])
            dates = ts.date_array(dlist=_times,autosort=False,freq=obs.timeResUnit)

        else:
            #print "========================="
            #print "%s - has no data!\n" %(obs.procedure)
            
            dates=ts.date_array(
                                start_date=iso.datetime_isoformat(obs.samplingTime[0]),
                                end_date=iso.datetime_isoformat(obs.samplingTime[1]),freq=obs.timeResUnit
                                )
            for i in range(0,len(dates)):
                _values.append(None)
        
        self.tserie = ts.time_series(_values,dates)
        #del times,values
        self.start_date = datetime(self.tserie.dates[0].year,
                                    self.tserie.dates[0].month,
                                    self.tserie.dates[0].day,
                                    self.tserie.dates[0].hour,
                                    self.tserie.dates[0].minute,
                                    self.tserie.dates[0].second)
        self.end_date = datetime(self.tserie.dates[-1].year,
                                    self.tserie.dates[-1].month,
                                    self.tserie.dates[-1].day,
                                    self.tserie.dates[-1].hour,
                                    self.tserie.dates[-1].minute,
                                    self.tserie.dates[-1].second)


     
    """======================================================================"""
        
    def setText(self,fname,obsProperty,procedure=None,uom=None):
        """
        set property according to istFile
        """
        self.property = obsProperty
        self.procedure = procedure
        self.uom = uom
        
        if not os.path.isfile(fname):
            raise sosUtils.UtuilsException(1,"File not found")
        
        """ GET PROCEDURE INFOS """
        finfo = filename.split("/")[-1].split('@')
        self.procedure = finfo[0]
        self.end_date = dt.strptime(finfo[1].split(".")[0], "%Y%m%d%H%M%S")
        
        """ READ FILE """
        try:
        	data=np.loadtxt(fname, dtype={'names': ('date', 'time', 'val'), 'formats': ('S10', 'S8', 'f4')})
        except:
        	return False

        """ CREATE RAW TIMESERIES """
        #convert date format
        T = [datetime.strptime("%s %s" %(d['date'],d['time']),"%d/%m/%Y %H:%M:%S") for d in data]
        #create date array
        dates = ts.date_array(dlist=T,autosort=False,freq='SECOND')
        #create values array
        vals = [d['val'] for d in data]
        #create regular timeseries every second filling missing values with 0
        self.tserie = ts.time_series(vals,dates)

        self.start_date = min(self.tserie.dates)

    """======================================================================"""
        
    def setArray(self,start_date,end_date,dates,vals,obsProperty,procedure,uom=None):
        """
        set property according to istFile
        """
        self.property = obsProperty
        self.procedure = procedure
        self.uom = uom

        self.start_date = start_date
        self.end_date = end_date
        
        da = ts.date_array(dlist=dates,autosort=False,freq='SECOND')

        """ CREATE RAW TIME SERIE """
        self.tserie = ts.time_series(vals,da)

    """======================================================================"""
        
    def resample(self,frequency="M",frunit=10,mode="mean",fill_null=None,start_date=None,end_date=None):
        """
        resample a given istSOSserie at given freq and unit
        arguments:
            -frequency: admissible values are YEARLY, MONTHLY, WEEKLY, DAILY, HOURLY, MINUTELY, or SECONDLY
            -frunit: unit of frequency for each step
            -fillval: value to be used to fill nulls
        """
        if not mode in ["sum","mean","max","min"]:
            raise UtuilsException(1,"mode shall be one of: sum,mean,max,min")
        
        # fill nulls
        if not fill_null==None:
            self.tserie = self.tserie.fill_missing_dates()
        else:
            self.tserie = self.tserie.fill_missing_dates()
        
        '''
        self.start_date = datetime(self.tserie.dates[0].year, self.tserie.dates[0].month, self.tserie.dates[0].day, 
                                        self.tserie.dates[0].hour, self.tserie.dates[0].minute, self.tserie.dates[0].second,tzinfo=utc)

        self.end_date = datetime(self.tserie.dates[-1].year, self.tserie.dates[-1].month, self.tserie.dates[-1].day, 
                                        self.tserie.dates[-1].hour, self.tserie.dates[-1].minute, self.tserie.dates[-1].second,tzinfo=utc)
        '''

        if not start_date==None:
            if start_date >= self.start_date and start_date < self.end_date:
                self.start_date = start_date #iso.parse_datetime(start_date)
        
        if not end_date==None:
            if end_date <= self.end_date and start_date > self.start_date:
                self.end_date = end_date #iso.parse_datetime(end_date)
        
        if frequency.upper() in ["T", "MINUTE", "MINUTELY"] and frunit>=10:
            timestep = relativedelta(minutes=frunit)
            #unitstep = relativedelta(minutes=1)
            unitstep = relativedelta(seconds=1)
        elif frequency.upper() in ["H", "HOUR", "HOURLY"]:
            timestep = relativedelta(hours=frunit)
            unitstep = relativedelta(minutes=1)
        elif frequency.upper() in ["D", "DAY", "DAILY"]:
            timestep = relativedelta(days=frunit)
            unitstep = relativedelta(hours=1)
        elif frequency.upper() in ["W", "WEEK", "WEEKLY"]:
            timestep = relativedelta(days=7*frunit)
            unitstep = relativedelta(days=1)
        elif frequency.upper() in ["M", "MONTH", "MONTHLY"]:
            timestep = relativedelta(months=frunit)
            unitstep = relativedelta(days=1)
        elif frequency.upper() in ["Y", "YEAR", "YEARLY"]:
            timestep = relativedelta(years=frunit)
            unitstep = relativedelta(months=1)
        else:
            raise UtuilsException(1,"frequency shall be one of: YEARLY, MONTHLY, WEEKLY, DAILY, HOURLY or MINUTELY")
        
        format = "%Y-%m-%d %H:%M%z"
        
        #resample serie according the selected method
        Tsampl=[]
        Vsampl=[]
        low_int = self.start_date+unitstep
        #up_int = self.start_date+timestep
        if mode == "sum":
            while (low_int+timestep) <= (self.end_date+unitstep):
                up_int=low_int+timestep
                
                #print "UP:" + str(up_int)
                #print "END:" + str(low_int)
                #print self.tserie[low_int.strftime(format):up_int.strftime(format)]
                
                Vsampl.append(self.tserie[low_int.strftime(format):up_int.strftime(format)].sum(0,float))
                Tsampl.append(up_int-unitstep)
                #print (up_int-unitstep)
                low_int = up_int
        elif mode=="mean":
            while (low_int+timestep) <= self.end_date:
                up_int=low_int+timestep
                """
                print "UP:" + str(up_int)
                print "END:" + str(low_int)
                print self.tserie[low_int.strftime(format):up_int.strftime(format)]
                """
                Vsampl.append(self.tserie[low_int.strftime(format):up_int.strftime(format)].mean(0,float))
                Tsampl.append(up_int-unitstep)
                low_int = up_int
        elif mode=="max":
            while (low_int+timestep) <= self.end_date:
                up_int=low_int+timestep
                Vsampl.append(self.tserie[low_int.strftime(format):up_int.strftime(format)].max(0,float))
                Tsampl.append(up_int-unitstep)
                low_int = up_int
        elif mode=="min":
            while (low_int+timestep) <= self.end_date:
                up_int=low_int+timestep
                Vsampl.append(self.tserie[low_int.strftime(format):up_int.strftime(format)].min(0,float))
                Tsampl.append(up_int-unitstep)
                low_int = up_int
        else:
            raise UtuilsException(1,"mode should be one of sum/mean/max/min")

        self.tserie = ts.time_series(Vsampl,
                    ts.date_array(dlist=Tsampl,autosort=False,freq="MINUTE"),
                    dtype=float
                    )

        if not fill_null==None:
            self.tserie.fill_value = fill_null

    """======================================================================"""
    
    def insert_fix_measure(self,pgdb,SOSschema,qindex=1,tz=""):
        """
        insert the current time series object into a istSOS database
        -pgdb: istSOS database connection
        -SOSschema: schema name of sos database implementation
        -id_geom: id of the measurement associated geometry
        -qindex= quality index to be assigned to inserted measures
        """
        
        print "Inserting '%s' data" % (self.procedure)
        
        # Retrive id from procedure name given
        # Questa SQL non funziona!! Vedi docs sulle "left join"
        '''
        sql = "SELECT id_prc, id_geom_fk "
        sql += "FROM meteoist.procedures "
        sql += "LEFT JOIN meteoist.measures "
        sql += "ON id_prc = id_prc_fk "
        sql += "AND name_prc = '%s' LIMIT 1" % (self.procedure)
        '''
        '''
        sql = "SELECT id_prc, id_geom_fk FROM %s.procedures, %s.measures " % (SOSschema, SOSschema)
        sql += "WHERE id_prc = id_prc_fk "
        sql += "AND name_prc = '%s' LIMIT 1" % (self.procedure)
        try:
            res = pgdb.execute(sql)[0]
        except e:
            raise sosException.SOSException(3,"SQL: %s"%(e.message))
            
        idPrc = res["id_prc"]
        idGeom = res["id_geom_fk"]
        '''
        
        # Prima cerco l'id della procedura, poi quello della geometria
        # questo perche e' possibile che non esistano ancora delle misure 
        # inserite per la procedura cercata
        sql = "SELECT id_prc from %s.procedures " % SOSschema
        sql += "WHERE name_prc = '%s' " % (self.procedure)
        
        idPrc = "None"
        try:
            print "  - Looking for id_prc"
            res = pgdb.execute(sql)
            if len(res)==1:
                idPrc = res[0]["id_prc"]
                print " - id_prc=%s" % (idPrc)
            else:
                print "  -> id_prc not found!!"
                raise sosException.SOSException(3,"SQL: %s not found!"%(self.procedure))
        except e:
            print "  - id_prc not found!!"
            raise sosException.SOSException(3,"SQL: %s"%(e.message))
        except:
            print "  - id_prc not found!!"
            raise sosException.SOSException(3,"SQL: id_prc not found!!")
            
        #if str(idPrc) == "None":
        #    print "  - id_prc not found!!"
        #    raise sosException.SOSException(3,"SQL: %s not found!"%(self.procedure))
        
        
            
        # Adesso cerco l'id della geometria
        sql = "SELECT id_geom_fk from %s.measures " % SOSschema
        sql += "WHERE id_prc_fk = '%s' LIMIT 1" % (idPrc)
        
        res = None
        idGeom = "null"
        try:
            res = pgdb.execute(sql)
            if len(res)==1:
                idGeom = res[0]["id_geom_fk"]                
            else:
                idGeom = "null"
        except:
            print "  - idGeom not found using null value.."
            #raise sosException.SOSException(3,"SQL: %s"%(e.message))
        
        if str(idGeom) == "None":
            idGeom = "null"
        print " - id_geom_fk=%s" % (idGeom)
        print "\n"
            
        #print ">> IDPRC: " + str(idPrc)
        #print ">> IDGEOM: " + str(idGeom)
        
        sql = "INSERT INTO %s.measures (id_qi_fk,id_prc_fk,id_geom_fk,time_msr,val_msr)" %(SOSschema)
        sql += " VALUES (" + str(qindex) + ", " + str(idPrc) + ", " + str(idGeom) + ", %(t)s::timestamptz, %(val)s )"
        
        
        # convert series to dictionary of (datetime, value) tuples which can be interpreted
        # by the database module. Note that masked values will get converted to None
        # with the tolist method. None gets translated to NULL when inserted into the
        # database.
        filled = self.tserie.filled()
        #print filled 
        
        l = []
        for i in range(len(filled)):
            d = {
                't' : filled.dates[i].strftime("%Y-%m-%d %H:%M:%S"+tz),
                'val' : str(filled.data[i])
                }
            l.append(d)
        dicto = tuple(l)
        #print dicto
        del l

        # insert time series data
        pgdb.insertMany(sql,dicto)
        #print dicto
        
        return True

#===============#
#  istSOSseries #
#===============#

class istSOSseries:
    """
    convert a GO.response.observations object in a time series array
    attributes:
        series: dictionary of istSOSserie grouped by observedProperty
        start: start datetime of selected period
        end: stop datetime of selected period
        frequency: series frequency
        frunit: frequency interval
        fmt: string date format
    """
    def __init__(self,GO,frequency="T",frunit=10):
        #TODO add control on GO type
        """
        GO: GO.response.observations object
        frequency: desired frequency according to dateutils
                    YEARLY, MONTHLY, WEEKLY, DAILY, HOURLY, MINUTELY, or SECONDLY
                    (todo add other frequency according to scikits.timeseries.const.freq_constants)
        frunit: unit of frequency for each step
        """
        self.series = {}
        self.start = GO.period[0]
        self.end = GO.period[1]
        self.frunit = frunit
        self.max = None
        self.min = None
        
        if frequency.upper() in ["T","MINUTE","MINUTELY","MIN"]:
            self.frequency = "MINUTE"
            self.fmt = '%Y-%m-%d %H:%M'
        elif frequency.upper() in ["H", "HOUR", "HOURLY"]:
            self.frequency = "HOUR"
            self.fmt = '%Y-%m-%d %H'
        elif frequency.upper() in ["D", "DAY", "DAILY"]:
            self.frequency = "DAY"
            self.fmt = '%Y-%m-%d'
        elif frequency.upper() in ["W", "WEEK", "WEEKLY"]:
            self.frequency = "WEEK"
            self.fmt = '%Y-%m-%d'
        elif frequency.upper() in ["M","MONTH","MONTHLY"]:
            self.frequency = "MONTH"
            self.fmt = '%Y-%m'
        elif frequency.upper() in ["Y","YEAR","YEARLY"]:
            self.frequency = "YEAR"
            self.fmt = '%Y'
        
        for ob in GO.obs:
            # create serie from GO
            #print "PRE: %s" %(len(ob.data))
            ists=istSOSserie()
            ists.setObs(ob)
            
            #print ists.tserie.data
            #print ob.observedProperty.lower()

            if ob.observedProperty.lower() == "rainfall":
                mode="sum"
            else:
                mode="mean"
            #print "\nresample according parameters: %s,%s,%s\n" %(self.frequency,frunit,mode)
            ists.resample(frequency=self.frequency,frunit=frunit,mode=mode,start_date=self.start,end_date=self.end)
            #myserie.resample(frequency="T",frunit=30,mode="sum",fill_null=0)
            #print "\nresampledone!\n"
            #print ists.tserie.data

            # append serie to this object
            if not self.series.has_key(ob.observedProperty):
                self.series[ob.observedProperty]=[]
            self.series[ob.observedProperty].append(ists)
    
    def sosPlot(self,fname,style="-",plwidth=8.2):
        """
        plot istSOSseries by observed property
        """
        if plwidth < 8.2:
            plwidth = 8.2
        print >> sys.stderr, "plwidth = %s" , plwidth
        h = plwidth * (3 / 8.2)
        
        dim = (plwidth,h*len(self.series.keys())+1)
        #dim = (plwidth,h)
        print >> sys.stderr, "dim = %s" , dim
        """
        if s=="small":
            dim=(8.2,3*len(self.series.keys())+0.4)
        elif s=="x-small":
            dim=(4.1,1.5*len(self.series.keys())+0.4)
        elif s=="mean":        
            dim=(12.3,4.5*len(self.series.keys())+0.6)
        elif s=="large":      print
            dim=(16.4,6*len(self.series.keys())+0.8)
        """
        print >> sys.stderr, "application debug #1"
        fig = tpl.tsfigure(figsize=dim,dpi=600)
        #fig = tpl.tsfigure()        
        i=0
        l=len(self.series.keys())
        for key, tss in self.series.iteritems():
            print >> sys.stderr, "application debug #2"
            i=i+1
            leglist=[]
            fsp = fig.add_tsplot(l,1,i)
            #tpl.title(key)
            tpl.title(' ')
            #tpl.suptitle(key, fontsize=12, x = 0.5, horizontalalignment = 'center')
            tpl.ylabel("%s (%s)\n" %(unicode(key,"utf-8"),unicode(tss[0].uom,"utf-8")),fontsize= 'small', family='Helvetica', horizontalalignment='center')
            #tpl.xlabel("%s" %(unicode("Time (UTC)","utf-8")),family='Helvetica') 
            tpl.grid(True)
            tpl.subplots_adjust(hspace=0.5,wspace=0.2,bottom=0.2,left=0.1,right=0.8,top=0.9)

            for id,tsi in enumerate(tss):
                print >> sys.stderr, "application debug #3"
                #series = ts.fill_missing_dates(tsi.tserie,freq=self.frequency)
                leglist.append(tsi.station)
                fsp.tsplot(tsi.tserie,style)
            
            leg = fsp.legend(leglist, bbox_to_anchor=(0., 1.02, 1., .102), loc=3,
                           ncol=2, mode="expand", borderaxespad=0.)

            #leg = fsp.legend(leglist,bbox_to_anchor=(1.05, 1), loc=2, borderaxespad=0., shadow=True)

            for t in leg.get_texts():
                print >> sys.stderr, "application debug #4"
                t.set_fontsize('xx-small')
                #t.set_fontsize(4) 
            
        print >> sys.stderr, "application debug #4"
        
        plt.savefig(fname)
        
    def sosReport(self,mode="text",fname=None,sep=","):
        """
        create a report of the series
        """
        fcontent=""
        
        names=["date"]
        dtlis=[]
        for key, tss in self.series.iteritems():
            for id,tsi in enumerate(tss):
                dtlis.append(tsi.tserie)
                names.append(tsi.procedure)
        stack=apply(ts.stack,dtlis)
        dates=stack.dates.tolist()
        
        if mode=="text":
            txt = sep.join(names)
            txt += "\n"
            for l in range(stack.shape[0]):
                txt += "%s" %(iso.datetime_isoformat(dates[l]))
                #txt += sosConfig.timezone + sep
                txt += "+01:00" + sep
                txt += sep.join([str(round(st, 2)) for st in stack.data[l]])
                txt += "\n"
            fcontent += txt

        if fname:
            file = open(fname, 'w')
            file.write(fcontent)
            file.close()
        else:
            return fcontent

        
        
        
        
        
        
        
        
        
        
        
        

