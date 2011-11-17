# istSOS Istituto Scienze della Terra Sensor Observation Service
# Copyright (C) 2010 Massimiliano Cannata
#
# This program is free software; you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation; either version 2 of the License.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program; if not, write to the Free Software
# Foundation, Inc., 51 Franklin Street, Fifth Floor, Boston, MA  02110-1301  USA

import sosConfig
from istSOS.filters import filter as f
from istSOS import sosException

import logging
from datetime import datetime
"""
#=============================
# set LOG FILE
#=============================
logPath = "/var/log/istsos/"
now = datetime.now()
#=============================
log = logging.getLogger('insertObservation')
hdlr = logging.FileHandler(logPath+'insertObservation.log')
formatter = logging.Formatter('%(asctime)s [%(levelname)s] > %(message)s')
hdlr.setFormatter(formatter)
log.addHandler(hdlr)
log.setLevel(logging.INFO)
"""


def getElemTxt(node):
    if node.hasChildNodes():
        val = node.firstChild
        if val.nodeType == val.TEXT_NODE:
            return (val.data).encode('utf-8')
        else:
            err_txt = "get node text value: \"%s\" is not of type TEXT" %(node.nodeName)
            raise sosException.SOSException(1,err_txt)
    else:
            err_txt = "get node text value: \"%s\" has no child node" %(node.nodeName)
            raise sosException.SOSException(1,err_txt)
        
def getElemAtt(node,att):
    if att in node.attributes.keys():
        return (node.getAttribute(att)).encode('utf-8')
    else:
        None
        #err_txt = "get node attribute value: \"%s\"has no \"%s\" attribute" %(node.nodeName,att)
        #raise sosException.SOSException(1,err_txt)

def get_name_from_urn(stringa,urnName):
    a = stringa.split(":")
    name = a[-1]
    urn = sosConfig.urn[urnName].split(":")
    if len(a)>1:
        for index in range(len(urn)-1):
            if urn[index]==a[index]:
                pass
            else:
                raise sosException.SOSException(1,"Urn \"%s\" is not valid: %s."%(a,urn))
    return name 

class sosIOfilter(f.sosFilter):
    "filter object for a InsertObservation request"
    #self.sensorId
    #self.samplingTime
    #self.procedure
    #self.observedProperty
    #self.featureOfInterest
    #self.data {def:string {"uom":string,"vals":[]}
    def __init__(self,sosRequest,method,requestObject):
        f.sosFilter.__init__(self,sosRequest,method,requestObject)

        logTxt = ""
        #**************************
        if method == "GET":
            raise sosException.SOSException(2,"insertObservation request support only POST method!")
        
        if method == "POST":
            
            #---assignedSensorId
            asid = requestObject.getElementsByTagName('AssignedSensorId')
            if len(asid)==1:
                    self.assignedSensorId = getElemTxt(asid[0])
            else:
                err_txt = "parameter \"AssignedSensorId\" is mandatory with multiplicity 1"
                raise sosException.SOSException(1,err_txt)
            
            logTxt += "\n AssignedSensorId: %s" % self.assignedSensorId

            #---forceInsert !!! NOT STANDARD PARAMETER !!!
            force = requestObject.getElementsByTagName('ForceInsert')
            self.forceInsert = False
            if len(force)==1:
                    force_str = getElemTxt(force[0]).lower()
                    if force_str == 'true' or force_str == "":
                        self.forceInsert = True 
                    elif force_str == 'false':
                        self.forceInsert = False
                    else:
                        err_txt = "parameter \"ForceInsert\" can only be: 'true' or 'false'"
                        raise sosException.SOSException(1,err_txt)

            logTxt += "\n ForceInsert: %s" % self.forceInsert
                
            #---om:observation
            obs = requestObject.getElementsByTagName('om:Observation')
            if not len(obs)==1:
                raise sosException.SOSException(1,"om:Observation tag is mandatory with multiplicity 1")
            
            #-------procedure
            proc = obs[0].getElementsByTagName('om:procedure')
            if not len(proc)==1:
                raise sosException.SOSException(1,"om:procedure tag is mandatory with multiplicity 1")
            self.procedure = get_name_from_urn(getElemAtt(proc[0],"xlink:href"),"procedure")

            logTxt += "\n Procedure: %s" % self.procedure

            #-------ObservedProperties
            self.oprName=[]
            oprs = obs[0].getElementsByTagName('om:observedProperty')
            if not len(oprs)==1:
                raise sosException.SOSException(1,"om:observedProperty tag is mandatory with multiplicity 1")
            cf = oprs[0].getElementsByTagName('swe:CompositePhenomenon')
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
                            raise sosException.SOSException(1,"om:observedProperty Name is missing: 'xlink:href' or 'gml:name' required")
            elif len(cf)==0:
                if "xlink:href" in oprs[0].attributes.keys():
                    self.oprName.append(getElemAtt(oprs[0],"xlink:href").split(":")[-1])
                else:
                    name = oprs[0].getElementsByTagName('gml:name')
                    if len(name)==1:
                        self.oprName.append(getElemTxt(name[0]))
                    else:
                        raise sosException.SOSException(1,"om:observedProperty Name is missing: 'xlink:href' or 'gml:name' required")
            else:
                raise sosException.SOSException(1,"swe:CompositePhenomenon tag is allowed with multiplicity 1")

            logTxt += "\n observedProperty: %s" % self.oprName
            
            #-----samplingTime
            st = obs[0].getElementsByTagName('om:samplingTime')
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
                        err_txt = "gml:TimePeriod is mandatory in multiplicity 1"
                        raise sosException.SOSException(1,err_txt)
                #get samplingTime from timeInstant
                elif len(tp) == 0 and len(ti)==1:
                    tpos = ti[0].getElementsByTagName('gml:timePosition')
                    if len(tpos)==1:
                        self.samplingTime = getElemTxt(tpos[0])
                    else:
                        err_txt = "gml:timePosition is mandatory in multiplicity 1"
                        raise sosException.SOSException(1,err_txt)
                else:
                    err_txt = "om:TimePeriod or om:TimeInstant is mandatory in multiplicity 1"
                    raise sosException.SOSException(1,err_txt)
            else:
                err_txt = "om:samplingTime is mandatory in multiplicity 1"
                raise sosException.SOSException(1,err_txt)

            logTxt += "\n samplingTime: %s" % self.samplingTime

            #------featureOfInterest
            foi = obs[0].getElementsByTagName("om:featureOfInterest")
            if not len(foi)==1:
                raise sosException.SOSException(1,"om:featureOfInterest tag is mandatory with multiplicity 1")
            #--foiName
            urn = getElemAtt(foi[0],"xlink:href")
            if urn:
                self.foiName = get_name_from_urn(urn,"feature")
            else:
                gml_name = foi[0].getElementsByTagName("gml:name")
                if len(gml_name)==1:
                    self.foiName = getElemTxt(gml_name[0])
                else:
                    raise sosException.SOSException(1,"om:featureOfInterest name is missing: 'xlink:href' or 'gml:name' is required")

            logTxt += "\n foiName: %s" % self.foiName

            """
            #--foiWKZ
            gml_type = ["gml:Polygon", "gml:LineString", "gml:Point", "gml:Box", "gml:GeometryCollection", "gml:MultiPoint", "gml:MultiLineString", "gml:MultiPolygon"]
            for node in foi[0].childNodes:
                if node.nodeName in gml_type and not node.nodeType == node.TEXT_NODE:
                    GMLfeature = node
                    break
            self.foiSRS = getElemAtt(GMLfeature,"srsName").split(":")[-1]
            a=GMLfeature.toxml()
            geomFoi = ogr.CreateGeometryFromGML(a.encode('ascii','ignore'))
            self.foiWKT = geomFoi.ExportToWkt()
            """
            #--result
            res = obs[0].getElementsByTagName('om:result')
            
            self.parameters = []
            self.uoms = []
            self.data = {}
            ##########################################################################################################
            #-----result---
            #return self.data where self.data is a dictionary of "definition" containing dictionary of "uom" and "vals"
            """ e.g.:
            self.data = {   
                        "urn:ist:parameter:time:iso8601": 
                            {
                            "uom":"sec", 
                            "vals":["2009-07-31T12:00:00+02:00","2009-07-31T12:10:00+02:00","2009-07-31T12:20:00+02:00"]
                            },
                        "urn:ist:def:phenomenon:rainfall": 
                            {
                            "uom":"mm", 
                            "vals":[0.1,0.2,0.3,0.4]
                            }
                        }
            """
            ##########################################################################################################
            if len(res)==1:
                sdr = res[0].getElementsByTagName('swe:SimpleDataRecord')
                da = res[0].getElementsByTagName('swe:DataArray')
                self.data={}
                
                #case SimpleDataRecord
                if len(sdr)==1 and len(da)==0:

                    logTxt += "\n SimpleDataRecord:"

                    fields = sdr[0].getElementsByTagName('swe:field')
                    for field in fields:
                        defin = None
                        uom = None
                        vals = []
                        fieldName = getElemAtt(field,"name")
                        tf = field.getElementsByTagName("swe:Time")
                        qf = field.getElementsByTagName("swe:Quantity")
                        
                        if len(tf)==1 and len(qf)==0:
                            defin = getElemAtt(tf[0],"definition")
                            vals.append(getElemTxt(tf[0].getElementsByTagName('swe:value')[0]))
                        
                        elif len(tf)==0 and len(qf)==1:
                            if getElemAtt(qf[0],"definition"):
                                defin = getElemAtt(qf[0],"definition")
                                um = qf[0].getElementsByTagName('swe:uom')
                                if len(um) == 1:
                                    uom = getElemAtt(um[0],"code")
                                v = qf[0].getElementsByTagName('swe:value')
                                if len(v) == 1:
                                    vals.append(getElemTxt(v[0]))
                        else:
                            err_txt = "swe:Time or swe:Quantity is mandatory in multiplicity 1"
                            raise sosException.SOSException(1,err_txt)
                        self.data[defin]={"uom":uom,"vals":vals}
                        
                #case DataArray
                elif len(sdr)==0 and len(da)==1:

                    logTxt += "\n DataArray:"

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
                            defin = getElemAtt(swet[0],"definition")
                            urnlist.append(defin) 
                        elif len(swet)==0 and len(sweq)==1 :
                            defin = getElemAtt(sweq[0],"definition")
                            urnlist.append(defin)
                            sweu = sweq[0].getElementsByTagName('swe:uom')
                            if len(sweu)==1:
                                uom = getElemAtt(sweu[0],"code")
                            
                            #oppure uom = getElemAtt(field.getElementsByTagName('swe:uom')[0],"code")
                        else:
                            err_txt = "swe:Time or swe:Quantity is mandatory in multiplicity 1 %s" %(field.firstChild.nodeName)
                            raise sosException.SOSException(1,err_txt)
                        self.data[defin]={"uom":uom,"vals":vals}
                        logTxt += "\n > data[%s] = %s:" %(defin,self.data[defin])
                    
                        enc = da[0].getElementsByTagName('swe:encoding')
                        if len(enc)==1:
                            encoding = enc[0].getElementsByTagName('swe:TextBlock')
                        else:
                            err_txt = "XML error: 'swe:TextBlock'"
                            raise sosException.SOSException(1,err_txt)
                        if len(encoding)==1:
                            tokenSeparator = getElemAtt(encoding[0],"tokenSeparator") 
                            blockSeparator = getElemAtt(encoding[0],"blockSeparator") 
                            decimalSeparator = getElemAtt(encoding[0],"decimalSeparator")
                        else:
                            err_txt = "swe:encoding is mandatory in multiplicity 1"
                            raise sosException.SOSException(1,err_txt)
                        
                        values = da[0].getElementsByTagName('swe:values')
                        if len(values)==1:
                            if values[0].hasChildNodes():
                                txtvals = getElemTxt(values[0])
                                valsplit=[i.split(tokenSeparator) for i in txtvals.split(blockSeparator)]
                                #log.info("%s\n\n" % valsplit)
                                for index,c in enumerate(urnlist):
                                    col = []
                                    for l in valsplit:
                                        col.append(l[index])
                                    self.data[c]["vals"] = col
                        else:
                            err_txt = "swe:values is mandatory in multiplicity 1"
                            raise sosException.SOSException(1,err_txt)
                    
                        #raise sosException.SOSException(1,"%s" %(self.data) )
                    
                #case simple om:result
                elif len(sdr)==0 and len(da)==0:
                    self.data[sosConfig.urn["time"]]={"uom":None,"vals":[self.samplingTime]}
                    uom = getElemAtt(res[0],"uom")
                    vals = [getElemTxt(res[0])]
                    self.data[sosConfig.urn["phenomena"]+self.oprName]={"uom":uom,"vals":vals}

            else:
                err_txt = "om:SimpleDataRecord in multiplicity N or om:DataArray in multiplicity 1 is mandatory"
                raise sosException.SOSException(1,err_txt) 
             
        #end if len(observation)==0 or >1 rise error
        else:
            err_txt = "om:Observation in multiplicity 1 is mandatory"
            raise sosException.SOSException(1,err_txt) 

        logTxt += "\n data: %s" % self.data
        #log.info("%s\n\n" % logTxt)
        
        #print filter for debug
        """
        err_txt  = "sensorId: %s\n" %(self.assignedSensorId)
        err_txt += "samplingTime: %s\n" %(self.samplingTime)
        err_txt += "procedure: %s\n" %(self.procedure)
        err_txt += "observedProperty: %s\n" %(self.oprName)
        err_txt += "featureOfInterest: %s\n" %(self.foiName)
        err_txt += "data: %s\n" %(self.data)
        raise sosException.SOSException(1,err_txt)
        """
                        
