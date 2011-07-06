
import urllib
import parse_GO
from xml.dom import minidom

def getObservation(GOrequest):
    xml_response = urllib.urlretrieve(GOrequest)
    xmldoc = minidom.parse(xml_response[0])
    requestObject = xmldoc.firstChild
    xmlobs = requestObject.getElementsByTagName('om:Observation')
    obs = []
    for xmlob in xmlobs:
        obs.append(parse_GO.om_Observation(xmlob))
    return obs

def get_zoo_aggr_fun(zooName,freq,start=None):
    if type(zooName)==type("abc"):
        res={"fagg":None,"fseq":None}
        #set starting time
        if not start:
            frt = "as.numeric(time(%s)[1])" %(zooName)
            frtd = "time(%s)[1]" %(zooName)
        else:
            frt = "as.numeric(as.POSIXct(strptime(%s,'%%FT%%T'),tz='UTC')))" %(start)
            frtd = "as.POSIXct(strptime(%s,'%%FT%%T'),tz='UTC'))" %(start)
        #create aggregate function and regular time sequence              
        if type(freq) == type(1):
            res["fagg"] = "as.POSIXct(sampsec(time(%s),time(%s)[1],%s), origin='1970-01-01', tz='UTC')" %(zooName,zooName,freq)
            res["fseq"] = "as.POSIXct(seq( %s, to=as.numeric(time(%s)[length(time(%s))]) + %s, by=%s), origin='1970-01-01', tz='UTC')" %(frt,zooName,zooName,freq,freq)
        elif type(freq) == type("abc") and freq in ["hourly","daily","weekly","monthly","yearly","quarterly"]:
            if freq == "hourly":
                freq=3600
                res["fagg"] = "as.POSIXct(sampsec(time(%s),time(%s)[1],%s), origin='1970-01-01', tz='UTC')" %(zooName,zooName,freq)
                res["fseq"] = "as.POSIXct(seq( %s, to=as.numeric(time(%s)[length(time(%s))]) + %s, by=%s), origin='1970-01-01', tz='UTC')" %(frt,zooName,zooName,freq,freq)
            elif freq == "daily":
                res["fagg"] = "as.Date(time(%s))" %(zooName)
                res["fseq"] = "seq(as.Date(%s),to=as.Date(time(%s)[length(time(%s))]),by='day')" %(frtd,zooName,zooName) 
            elif freq == "weekly":
                res["fagg"] = "as.Date(sampday(time(%s),time(%s)[1],7), origin='1970-01-01', tz='UTC')" %(zooName,zooName)
                res["fseq"] = "seq(as.Date(%s),to=as.Date(time(%s)[length(time(%s))]),by=7)" %(frtd,zooName,zooName)
            elif freq == "monthly":
                res["fagg"] = "as.yearmon(time(%s))" %(zooName)
                res["fseq"] = "as.yearmon(seq(as.Date(%s),to=as.Date(time(%s)[length(time(%s))]),by='month'))" %(frtd,zooName,zooName) 
            elif freq == "yearly":
                res["fagg"] = "format(time(%s),'%%Y')"  %(zooName)
                res["fseq"] = "format(seq(as.Date(%s),to=as.Date(time(%s)[length(time(%s))]),by='year'),'%%Y')" %(frtd,zooName,zooName) 
            elif freq == "quarterly":
                res["fagg"] = "as.yearqtr(time(%s))" %(zooName)
                res["fseq"] = "seq(as.yearqtr(as.Date(%s)),to=as.yearqtr(as.Date(time(%s)[length(time(%s))])),by=1/4)" %(frtd,zooName,zooName)
        return res


#define R vars
import rpy2.robjects as robjects
robjects.r.library("zoo")
#------------
r = robjects.r
r_strptime = robjects.r['strptime']
r_aspos = robjects.r['as.POSIXct']
r_zoo = robjects.r['zoo']
r("Sys.setenv(TZ = 'UTC')")

r("""
sampsec <- function(tp,tpo,fr){ 
    r=c();
    for (i in 1:length(tp) ) {
        if( (as.numeric(tp[i])-as.numeric(tpo)) %% fr == 0) {
               r[i] <- as.numeric(tp[i])
        }
        else {
               r[i] <- (as.numeric(tp[i]) - ((as.numeric(tp[i])-as.numeric(tpo)) %% fr ) + fr )
        }
    }
    return(r)
}
""")

r("""
sampday <- function(tp,tpo,fr){ 
    r=c();
    tpt = as.Date(tp)
    tpot = as.Date(tpo)
    for (i in 1:length(tpt) ) {
        if( (as.numeric(tpt[i])-as.numeric(tpot)) %% fr == 0) {
               r[i] <- as.numeric(tpt[i])
        }
        else {
               r[i] <- (as.numeric(tpt[i]) - ((as.numeric(tpt[i])-as.numeric(tpot)) %% fr ) + fr )
        }
    }
    return(r)
}
""")

#------------AGGREGATE-------
   
def aggregate_report(obs,freq=None,by='PROPERTY',start=None,p_name=None,p_width=700,p_height=500,f_name=None,stat=True):
    res={'plot':[],'serie':[],'summary':[]}
    
    if by=='PROPERTY':
        #find all TimeSeries observing the same property
        opr_list=[]
        for i in obs:
            opr_list += i.result['vals'].keys()

        opr_list = list(set(opr_list))
        zooObj_tmp=[]
        zooNames=[]
        data_i=[]
        data_f=[]
        zoo_procs=[]
        i=0
        for op in opr_list:
            Names=[]
            opName = op.split('@')[0]
            for ob in obs:
                if ob.result['vals'].has_key(op):
                    i=i+1
                    time=None
                    data={}
                    #one zoo series for each om:observation
                    #--check if ob.procedure has op value
                    time = robjects.StrVector(ob.result['time'])
                    data[ob.procedure] = robjects.FloatVector(ob.result['vals'][op])
                    #=============
                    robjects.globalEnv["time_%s" %(i)] = time
                    robjects.globalEnv["data_%s" %(i)] = r['data.frame'](**data)
                    r( "%s_%s <- zoo(data_%s,as.POSIXct(strptime(time_%s,'%%FT%%T'),tz='UTC'))" %(ob.procedure,opName,i,i) )
                    Names.append("%s_%s" %(ob.procedure,opName))
                    #=============
            #bind all zoo series in a tmp zoo object
            bind_cmd = 'cbind('+ (",".join(Names)) +')'
            zooName = "%s_tmp" %(opName)
            #print "========"
            #print "OBJ ZOO"
            #print "========"
            r('%s<-%s'%(zooName,bind_cmd))
            r("write.zoo(%s,file='orig_%s.txt',index.name='EventTime')" %(zooName,zooName) )
            
            if p_name or f_name or stat:
                functions = get_zoo_aggr_fun(zooName,freq,start)
                
                #set aggregation mode
                if opName=="rainfall":
                    mode="sum"
                else:
                    mode="mean"
                
                #aggregate according to mode and frequency
                r("my_aggregate<-aggregate(%s,%s,%s)" %(zooName,functions["fagg"],mode) )
                
                #create an empty regular series
                r("tt <- %s" %(functions["fseq"]))
                r('z<-zoo(,tt)')
                
                #merge the regular class with the sampled
                r('%s<-merge(z,my_aggregate,fill=0)' %(opName))
                
                #plot the result
                if p_name:
                    plotname = opName+"_"+p_name+'.png'
                    res['plot'].append(plotname)
                    r.png(plotname,width=p_width,height=p_height)
                    r("plot(%s,type='b',pch=1:length(%s), screen=1, col=1:length(%s))" %(opName,opName,opName))
                    r("title(main='%s',font.main=4)" %(opName) )
                    r("abline(v=time(%s), col='lightgray', lty='dashed')" %(opName) )
                    """
                    axis.POSIXct(1, 1:16, rv.dates, format="%Y-%m-%d")
                    """
                    r("legend('topright', colnames(%s), lty=1, col=1:length(%s))"  %(opName,opName))
                    r('dev.off()')
                
                #write the output
                if f_name:
                    filename = opName+"_"+f_name+'.csv'
                    res['serie'].append(filename)
                    r('write.zoo(%s,file=\'%s\',index.name=\'EventTime\')' %(opName,filename))
                
                #write summary stat
                if stat:
                    res['summary'].append(str(r("summary(%s)" %(opName))))

    if by=='SENSOR': 
        for ob in obs:
            time=None
            data={}
            rain={}
            #--check if ob.procedure has op value
            time = robjects.StrVector(ob.result['time'])
            opList = []
            for op in ob.result['vals'].keys():
                opName = op.split('@')[0]
                if opName=='rainfall':
                    rain[opName] = robjects.FloatVector(ob.result['vals'][op])
                    rainList=op
                    has_rain=True
                else:
                    data[opName] = robjects.FloatVector(ob.result['vals'][op])
                    opList.append(op)
            #============= set R variables ==================
            tName = "time_%s" %(ob.procedure)
            dName = "data_%s" %(ob.procedure)
            zdName = "z_%s" %(dName)
            robjects.globalEnv[tName] = time
            robjects.globalEnv[dName] = r['data.frame'](**data)
            r( "%s <- zoo(%s,as.POSIXct(strptime(%s,'%%FT%%T'),tz='UTC'))" %(zdName,dName,tName) )
            if has_rain:
                rName = "rain_"+ob.procedure
                zrName = "z_%s" %(rName)
                robjects.globalEnv[rName] = r['data.frame'](**rain)
                r( "%s <- zoo(%s,as.POSIXct(strptime(%s,'%%FT%%T'),tz='UTC'))" %(zrName,rName,tName) )  
            #==============                     
            if p_name or f_name or stat:
                #aggregate according to mode and frequency
                adName = "a_"+zdName
                data_f = get_zoo_aggr_fun(zdName,freq,start)
                r("%s<-aggregate(%s,%s,%s)" %(adName,zdName,data_f["fagg"],"mean") )
                if has_rain:
                    arName = "a_"+zrName
                    rain_f = get_zoo_aggr_fun(zrName,freq,start)
                    r("%s<-aggregate(%s,%s,%s)" %(arName,zrName,rain_f["fagg"],"sum") )
                #combine series and get zooName serie
                if has_rain:
                    bind_cmd = "cbind(%s,%s)" %(arName,adName)
                    zooName = "%s_agg" %(ob.procedure)
                    r('%s<-%s'%(zooName,bind_cmd))
                    r("colnames(%s)<-c('%s','%s')" %(zooName,rainList,",".join(opList)))
                else:
                    zooName = adName
                #=================================
                #create an empty regular series
                r("tt <- %s" %(data_f["fseq"]))
                r('z<-zoo(,tt)')
                
                #merge the regular class with the sampled
                r('%s<-merge(z,%s,fill=0)' %(ob.procedure,zooName))
                
                #plot the result
                if p_name:
                    plotname = ob.procedure+"_"+p_name+'.png'
                    res['plot'].append(plotname)
                    r.png(plotname,width=p_width,height=p_height)
                    r("plot(%s,type='b',pch=1:length(%s), col=1:length(%s))" %(ob.procedure,ob.procedure,ob.procedure))
                    r('dev.off()')
                
                #write the output
                if f_name:
                    filename = ob.procedure+"_"+f_name+'.csv'
                    res['serie'].append(filename)
                    r('write.zoo(%s,file=\'%s\',index.name=\'EventTime\')' %(ob.procedure,filename))
                
                #write summary stat
                if stat:
                    res['summary'].append(str(r("summary(%s)" %(ob.procedure))))
       
    return res





