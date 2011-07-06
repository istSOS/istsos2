
from xml.dom import minidom

class ObsError(Exception):
    def __init__(self, value):
        self.value = value
    def __str__(self):
        return repr(self.value)

def getElemTxt(node):
    if node.hasChildNodes():
        val = node.firstChild
        if val.nodeType == val.TEXT_NODE:
            return str(val.data)
        else:
            err_txt = "get node text value: \"%s\" is not of type TEXT" %(node.nodeName)
            raise ObsError(err_txt)
    else:
            err_txt = "get node text value: \"%s\" has no child node" %(node.nodeName)
            raise ObsError(err_txt)

def getElemAtt(node,att,mode='p'):
    if att in node.attributes.keys():
        return str(node.getAttribute(att))
    else:
        if mode == 'p':
            return None
        else:
            err_txt = "get node attribute value: \"%s\"has no \"%s\" attribute" %(node.nodeName,att)
            raise ObsError(err_txt)

class measures:
    def __init__(self,name,uom,urn,vals):
        self.name = name
        self.uom = uom
        self.urn = urn
        self.vals = vals

class om_Observation:
    def __init__(self, xml_observation_object):
        self.procedure = None
        self.oprName=[]
        self.samplingTime = None
        self.foiName = None
        self.foiGml = None
        self.result = {
            "time" : [],
            "vals" : {} #{ "prop@uom" : [], "prop2@uom": [], "prop3@uom": [] }
           }
        
        #-------procedure
        proc = xml_observation_object.getElementsByTagName('om:procedure')
        if not len(proc)==1:
            raise ObsError("om:procedure tag is mandatory with multiplicity 1")
        self.procedure = get_name_from_urn(getElemAtt(proc[0],"xlink:href"),"procedure")
        
        #-------ObservedProperties
        self.oprName=[]
        oprs = xml_observation_object.getElementsByTagName('om:observedProperty')
        if not len(oprs)==1:
            raise sosException.SOSException(1,"om:observedProperty tag is mandatory with multiplicity 1")
            cf = oprs[0].getElementsByTagName('swe:CompositPhenomenon')
            if len(cf)==1:
                comp = cf[0].getElementsByTagName('swe:component')
                for co in comp:
                    if "xlink:href" in co.attributes.keys():
                        self.oprName.append(getElemAtt(co,"xlink:href").split(":")[-1])
                    else:
                        name = co.getElementsByTagName('gml:name')
                        if len(name)==1:
                            self.oprName.append(getElemTxt(name[0]))
                        else:
                            raise ObsError("om:observedProperty Name is missing: 'xlink:href' or 'gml:name' required")
            elif len(cf)==0:
                if "xlink:href" in oprs[0].attributes.keys():
                    self.oprName.append(getElemAtt(oprs[0],"xlink:href").split(":")[-1])
                else:
                    name = oprs[0].getElementsByTagName('gml:name')
                    if len(name)==1:
                        self.oprName.append(getElemTxt(name[0]))
                    else:
                        raise ObsError("om:observedProperty Name is missing: 'xlink:href' or 'gml:name' required")
            else:
                raise ObsError("swe:CompositPhenomenon tag is allowed with multiplicity 1")
            
            #-----samplingTime
            st = xml_observation_object.getElementsByTagName('om:samplingTime')
            if len(st)==1:
                tp = st[0].getElementsByTagName('gml:TimePeriod')
                ti = st[0].getElementsByTagName('gml:TimeInstant')
                #get samplingTime from timePeriod
                if len(tp) == 1 and len(ti)==0:
                    bp = tp[0].getElementsByTagName('gml:beginPosition')
                    ep = tp[0].getElementsByTagName('gml:endPosition')
                    if len(bp)==1 and len(ep)==1:
                        self.samplingTime = getElemTxt(bp[0]) + "/" + getElemTxt(ep[0])
                    else:
                        err_txt = "om:TimePeriod is mandatory in multiplicity 1"
                        raise ObsError(err_txt)
                #get samplingTime from timeInstant
                elif len(tp) == 0 and len(ti)==1:
                    tpos = ti[0].getElementsByTagName('gml:timePosition')
                    if len(tpos)==1:
                        self.samplingTime = getElemTxt(tpos[0])
                    else:
                        err_txt = "gml:timePosition is mandatory in multiplicity 1"
                        raise ObsError(err_txt)
                else:
                    err_txt = "om:TimePeriod or om:TimeInstant is mandatory in multiplicity 1"
                    raise ObsError(err_txt)
            else:
                err_txt = "om:samplingTime is mandatory in multiplicity 1"
                raise ObsError(err_txt)
            
            #------featureOfInterest
            foi = xml_observation_object.getElementsByTagName("om:featureOfInterest")
            if not len(foi)==1:
                raise ObsError("om:featureOfInterest tag is mandatory with multiplicity 1")
            #---------------------foiName
            urn = getElemAtt(foi[0],"xlink:href")
            if urn:
                self.foiName = get_name_from_urn(urn,"feature")
            else:
                gml_name = foi[0].getElementsByTagName("gml:name")
                if len(gml_name)==1:
                    self.foiName = getElemTxt(gml_name[0])
                    gml_polygon = foi[0].getElementsByTagName("gml:Polygon")
                    gml_point = foi[0].getElementsByTagName("gml:Point")
                    gml_lineString = foi[0].getElementsByTagName("gml:LineString")
                    gml_box = foi[0].getElementsByTagName("gml:Box")
                    if len(gml_polygon)==1:
                        self.foiGml = gml_polygon.toxml()
                    elif len(gml_point)==1:
                        self.foiGml = gml_point.toxml()
                    elif len(gml_lineString)==1:
                        self.foiGml = gml_lineString.toxml()
                    elif len(gml_box)==1:
                        self.foiGml = gml_box.toxml()
                    else:
                        self.foiGml = None       
                else:
                    raise ObsError("om:featureOfInterest name is missing: 'xlink:href' or 'gml:name' is required")
                        
            #--result
            res = xml_observation_object.getElementsByTagName('om:result')
            
            ##########################################################################################################
            #-----result---
            #return self.data where self.data is a dictionary of "definition" containing dictionary of "uom" and "vals"
            """
            self.result = {
                            "time" : []
                            "vals" : {} #{ "prop1@uom" : [], "prop2@uom": [], "prop3@uom": [] }
                           }
            """
            ##########################################################################################################
            
            if len(res)==1:
                sdr = res[0].getElementsByTagName('swe:SimpleDataRecord')
                da = res[0].getElementsByTagName('swe:DataArray')
                self.data={}
                
                #case SimpleDataRecord
                if len(sdr)==1 and len(da)==0:                           
                    fields = sdr[0].getElementsByTagName('swe:field')
                    for field in fields:
                        defin = None
                        uom = None
                        vals = []
                        times=[]
                        fieldName = getElemAtt(field,"name")
                        tf = field.getElementsByTagName("swe:Time")
                        qf = field.getElementsByTagName("swe:Quantity")
                        
                        if len(tf)==1 and len(qf)==0:
                            defin = getElemAtt(tf[0],"definition").split(":")[-1]
                            times.append(getElemTxt(tf[0].getElementsByTagName('swe:value')[0]))
                        
                        elif len(tf)==0 and len(qf)==1:
                            if getElemAtt(qf[0],"definition"):
                                defin = getElemAtt(qf[0],"definition").split(":")[-1]
                                um = qf[0].getElementsByTagName('swe:uom')
                                if len(um) == 1:
                                    uom = getElemAtt(um[0],"code")
                                v = qf[0].getElementsByTagName('swe:value')
                                if len(v) == 1:
                                    vals.append(getElemTxt(v[0]))
                        else:
                            err_txt = "swe:Time or swe:Quantity is mandatory in multiplicity 1"
                            raise ObsError(err_txt)
                        
                        self.result["time"]=times
                        
                        if uom:
                            self.result["vals"][defin+"@"+uom]=vals
                        else:
                            self.result["vals"][defin]=vals
                        
                        for key in self.result["vals"].keys():
                            if len(self.result["time"])==len(self.result["vals"][key]):
                                raise ObsError("length of values differs from length of time")
                
                #case DataArray
                elif len(sdr)==0 and len(da)==1:
                    dr = da[0].getElementsByTagName('swe:DataRecord')
                    fields = dr[0].getElementsByTagName('swe:field')
                    urnlist=[]
                    for id, field in enumerate(fields):
                        defin = None
                        uom = None
                        vals = []
                        fieldName = getElemAtt(field,"name")
                        swet = field.getElementsByTagName("swe:Time")
                        sweq = field.getElementsByTagName("swe:Quantity")
                        
                        if len(swet)==1 and len(sweq)==0:
                            defin = getElemAtt(swet[0],"definition").split(":")[-1]
                            urnlist.append(defin) 
                        elif len(swet)==0 and len(sweq)==1 :
                            defin = getElemAtt(sweq[0],"definition").split(":")[-1]
                            sweu = sweq[0].getElementsByTagName('swe:uom')
                            if len(sweu)==1:
                                uom = getElemAtt(sweu[0],"code")
                                urnlist.append(defin+"@"+uom)
                            else:
                                urnlist.append(defin)
                        else:
                            err_txt = "swe:Time or swe:Quantity is mandatory in multiplicity 1 %s" %(field.firstChild.nodeName)
                            raise ObsError(err_txt)
                        
                        
                        enc = da[0].getElementsByTagName('swe:encoding')
                        if len(enc)==1:
                            encoding = enc[0].getElementsByTagName('swe:TextBlock')
                        else:
                            err_txt = "XML error: 'swe:TextBlock'"
                            raise ObsError(err_txt)
                        if len(encoding)==1:
                            tokenSeparator = getElemAtt(encoding[0],"tokenSeparator") 
                            blockSeparator = getElemAtt(encoding[0],"blockSeparator") 
                            decimalSeparator = getElemAtt(encoding[0],"decimalSeparator")
                        else:
                            err_txt = "swe:encoding is mandatory in multiplicity 1"
                            raise ObsError(err_txt)
                        
                        values = da[0].getElementsByTagName('swe:values')
                        if len(values)==1:
                            txtvals = getElemTxt(values[0])
                            valsplit=[i.split(tokenSeparator) for i in txtvals.split(blockSeparator)]
                            
                            for index,defi in enumerate(urnlist):
                                if defi=="iso8601":
                                    for line in valsplit:
                                        self.result["time"].append(line[index])
                                else:
                                    for line in valsplit:
                                        self.result["vals"][defi].append(line[index])
                        else:
                            err_txt = "swe:values is mandatory in multiplicity 1"
                            raise ObsError(err_txt)
                        
                        #raise sosException.SOSException(1,"%s" %(self.data) )
                
                #case simple om:result
                elif len(sdr)==0 and len(da)==0:
                    self.data[sosConfig.urn["time"]]=[self.samplingTime]
                    uom = getElemAtt(res[0],"uom")
                    vals = [getElemTxt(res[0])]
                    self.data[sosConfig.urn["phenomena"]+self.oprName+"@"+uom]=vals
            
            else:
                err_txt = "om:SimpleDataRecord in multiplicity N or om:DataArray in multiplicity 1 is mandatory"
                raise ObsError(err_txt) 
        
        #end if len(observation)==0 or >1 rise error
        else:
            err_txt = "om:Observation in multiplicity 1 is mandatory"
            raise ObsError(err_txt) 


        


