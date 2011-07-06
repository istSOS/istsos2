
import urllib
import parse_getObservation as pgo
from xml.dom import minidom

#import rpy2.robjects as robjects
#from rpy2.robjects.packages import importr


#get SOS observation in python
#-- execute request
request = "http://istgeo.ist.supsi.ch/istsos?service=SOS&version=1.0.0&request=GetObservation&offering=meteoIST&procedure=P_BED,P_TRE&eventTime=2010-02-08T11:50+01:00/2010-02-10T11:50+01:00&observedProperty=rainfall&responseFormat=text%2Fxml%3Bsubtype%3D%27sensorML%2F1.0.0%27"

request="http://istgeo.ist.supsi.ch/istsos?service=SOS&version=1.0.0&request=GetObservation&offering=meteoIST&procedure=P_BED,P_TRE,P_CAM&eventTime=2010-02-08T11:50+01:00/2010-02-10T11:50+01:00&observedProperty=rainfall&responseFormat=text%2Fxml%3Bsubtype%3D%27sensorML%2F1.0.0%27"

xml_response = urllib.urlretrieve(request)
xmldoc = minidom.parse(xml_response[0])
requestObject = xmldoc.firstChild
xmlobs = requestObject.getElementsByTagName('om:Observation')
obs = []

for xmlob in xmlobs:
    obs.append(pgo.om_Observation(xmlob))


#define R vars
import rpy2.robjects as robjects
robjects.r.library("zoo")

r = robjects.r
r_strptime = robjects.r['strptime']
r_aspos = robjects.r['as.POSIXct']
r_zoo = robjects.r['zoo']
#"""
time = ['2009-07-31T12:00:00+02:00', '2009-07-31T12:10:00+02:00', '2009-07-31T12:20:00+02:00', '2009-07-31T13:30:00+02:00']
data=dict()
time = robjects.StrVector(time)
data["rain"] = robjects.FloatVector([0.1,0.5,0.3,0.4])
data["temp"] = robjects.FloatVector([22.1,23.7,23.9,24.3])
#"""

observation{
            "procedure": ""
            "uoms" : { "prop@uom" : [prop1,prop2], "prop2@uom2" : [prop3,prop4]}
            "time" : []
            "vals" : { "prop1" : [], "prop2": [], "prop3": [] }
           }

GROUPBY = ["property","procedure"]

array(observation)

array(ts_observation)



zoo={}
for idx,ob in enumerate(obs):
    data = dict()
    for key in ob.data.keys():
        defin = key.split(":")[-1].split("@")
        if len(defin)==2:
            name = defin[0]
            uom =  defin[1]
        elif len(defin)==1:
            name = defin[0]
            uom = None
        else:
            Err = "name error"
        
        if name == "iso8601":
            time = robjects.StrVector(ob.data[key])
        else:
            data[name]   = robjects.FloatVector(ob.data[key])
            
    data_i = r_aspos(r_strptime(time,"%FT%T",tz = "GMT"))
    data_f = r['data.frame'](**data)

    robjects.globalEnv["data_i"] = data_i
    robjects.globalEnv["data_f"] = data_f
    
    zooNames.append("%s" %ob.procedure) 
    r('%s<-zoo(data_f,data_i)'%(ob.procedure))
    
    #----
    
    r.png('plot.png',width=500,height=400)
    txt = str(r('plot(z_1)'))
    r('dev.off()')
    
    #merge time series and get them regular by sampling (sum or ave)
    
    r('tt <- seq(time(z_1)[1], to=as.POSIXct("2009-08-02 13:30:00 GMT"), by=600)')


    
    
        


        
        
data_index = r_aspos(r_strptime(data["time"],"%FT%T",tz = "GMT"))


        
        
        
       
    





z_index_str = robjects.StrVector(a)
z_index = r_aspos(r_strptime(z_index_str,"%FT%T",tz = "GMT"))
z_data = robjects.FloatVector(b)

robjects.globalEnv["z_index"] = z_index
robjects.globalEnv["z_data"] = z_data

r('z<-zoo(z_data,z_index)')

print r('summary(z)')

r('plot(z)')


d = {'value': robjects.IntVector((1,2,3)),
     'letter': robjects.StrVector(('x', 'y', 'z'))
     }
     

data_index = robjects.StrVector(a)


dataFrame = { "eventTime" : 

dataf = r['data.frame'](**d)
print dataf

    
    
    

    r_strptime = robjects.r['strptime']
    r_aspos = robjects.r['as.POSIXct']
    

    
    
    od = rlc.OrdDict(
    
    
    dataf = robjects.DataFrame()
    
    res = robjects.StrVector()
    
    
dataf = robjects.DataFrame()
import rpy2.rlike.container as rlc
od = rlc.OrdDict(




as.POSIXct(strptime(ds[,2],"%m/%d/%y %H:%M:%S"))


od = rlc.OrdDict(c(('value', robjects.IntVector((1,2,3))),
                    ('letter', robjects.StrVector(('x', 'y', 'z')))))
dataf = robjects.DataFrame(od)
print(dataf.colnames)
[1] "letter" "value"    
    
        
        
        


obsData = 
