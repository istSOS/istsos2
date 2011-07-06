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
from osgeo import ogr

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

class sosRSfilter(f.sosFilter): 
    "filter object for a registerSensor request"
    """
    self.xmlSensorDescription = None
    self.procedure = None
    self.observedProperties = []
    self.uom = []
    self.featureOfInterestUrn = None
    self.featureOfInterestSRS = None
    self.featureOfInterestWKT = None
    """
    
    #self.procedure
    #self.observedProperty
    #self.featureOfInterest
    #self.data {def:string {"uom":string,"vals":[]}
    def __init__(self,sosRequest,method,requestObject):
        f.sosFilter.__init__(self,sosRequest,method,requestObject)
        #**************************
        if method == "GET":
            raise sosException.SOSException(2,"registerSensor request support only POST method!")
        if method == "POST":
            
            #---SensorDescription
            #----------------------            
            sd = requestObject.getElementsByTagName('SensorDescription')
            if len(sd)==1:
                #self.xmlSensorDescription = sd[0].childNodes[0]

                cNodes = sd[0].childNodes
                self.xmlSensorDescription = None
                for c in cNodes:
                    if c.nodeType == c.ELEMENT_NODE:
                        self.xmlSensorDescription = c
                        break
                        
                if not self.xmlSensorDescription:
                    raise sosException.SOSException(1,"a SensorDescription child element is mandatory with multiplicity 1")

                #self.xmlSensorDescription = sd[0].nextSiblingfirstChild
            else:
                raise sosException.SOSException(1,"SensorDescription parameter is mandatory with multiplicity 1")

            #---ProcedureDescription
            try:
                self.proc_desc = getElemTxt(sd[0].getElementsByTagName('gml:description')[0])
            except:
                self.proc_desc = 'NULL'
                
            #---ObservationTemplate
            #----------------------
            ot = requestObject.getElementsByTagName('ObservationTemplate')
            if not len(ot)==1:
                raise sosException.SOSException(1,"ObservationTemplate parameter is mandatory with multiplicity 1")
            
            obs = ot[0].getElementsByTagName('om:Observation')
            if not len(obs)==1:
                raise sosException.SOSException(1,"om:Observation tag is mandatory with multiplicity 1")
            
            #-------procedure
            proc = obs[0].getElementsByTagName('om:procedure')
            if not len(proc)==1:
                raise sosException.SOSException(1,"om:procedure tag is mandatory with multiplicity 1")
            self.procedure = get_name_from_urn(getElemAtt(proc[0],"xlink:href"),"procedure")
            
            #-------ObservedProperties
            self.oprName=[]
            self.oprDesc=[]
            oprs = obs[0].getElementsByTagName('om:observedProperty')
            if not len(oprs)==1:
                raise sosException.SOSException(1,"om:observedProperty tag is mandatory with multiplicity 1")
            
            #-------BeginPosition
            try:
                self.beginPosition = getElemTxt(obs[0].getElementsByTagName('gml:beginPosition')[0])
            except:
                self.beginPosition = 'NULL'


            cf = oprs[0].getElementsByTagName('swe:CompositPhenomenon')
            
            if len(cf)==1:
                comp = cf[0].getElementsByTagName('swe:component')
                for co in comp:
                    if "xlink:href" in co.attributes.keys():
                        #self.oprName.append(getElemAtt(co,"xlink:href").split(":")[-1])
                        self.oprName.append(getElemAtt(co,"xlink:href"))
                        self.oprDesc.append("NULL")
                    else:
                        name = co.getElementsByTagName('gml:name')
                        if len(name)==1:
                            self.oprName.append(getElemTxt(name[0]))
                        else:
                            raise sosException.SOSException(1,"om:observedProperty Name is missing: 'xlink:href' or 'gml:name' required")
                        desc = co.getElementsByTagName('gml:description')
                        if len(desc)==1:
                            self.oprDesc.append(getElemTxt(desc[0]))
                        else:
                            self.oprDesc.append("NULL")
                        
            elif len(cf)==0:
                if "xlink:href" in oprs[0].attributes.keys():
                    #self.oprName.append(getElemAtt(oprs[0],"xlink:href").split(":")[-1])
                    self.oprName.append(getElemAtt(oprs[0],"xlink:href"))
                else:
                    name = oprs[0].getElementsByTagName('gml:name')
                    if len(name)==1:
                        self.oprName.append(getElemTxt(name[0]))
                    else:
                        raise sosException.SOSException(1,"om:observedProperty Name is missing: 'xlink:href' or 'gml:name' required")
                    desc = oprs[0].getElementsByTagName('gml:description')
                    if len(desc)==1:
                        self.oprDesc.append(getElemTxt(desc[0]))
                    else:
                        self.oprDesc.append("NULL")
            else:
                raise sosException.SOSException(1,"swe:CompositPhenomenon tag is allowed with multiplicity 1")
            
            #-------samplingTime
            samplT = obs[0].getElementsByTagName("om:samplingTime")
            if not len(samplT)==1:
                raise sosException.SOSException(1,"om:samplingTime tag is mandatory with multiplicity 1")
            else:
                timeInterval = samplT[0].getElementsByTagName("gml:timeInterval")
                if len(timeInterval)==1:
                    self.time_res_unit = getElemAtt(timeInterval[0],"unit")
                    self.time_res_val = getElemTxt(timeInterval[0])
                else:
                    self.time_res_unit = "unknown"
                    self.time_res_val = "NULL"
            
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
            
            #--foiDesc
            desc = foi[0].getElementsByTagName("gml:description")
            if len(desc)==1:
                self.foiDesc = getElemTxt(desc[0])
            else:
                self.foiDesc = "NULL"
            
            #--foiWKZ
            # gml_type = ["gml:Polygon", "gml:LineString", "gml:Point", "gml:Box", "gml:GeometryCollection", "gml:MultiPoint", "gml:MultiLineString", "gml:MultiPolygon"]
            GMLfeature = None
            for node in foi[0].childNodes:
                if not node.nodeType == node.TEXT_NODE: #node.nodeName in gml_type:  and not node.nodeType == node.TEXT_NODE:
                    if node.nodeName in sosConfig.foiGeometryType.keys():
                        GMLfeature = node
                        self.foiType = sosConfig.foiGeometryType[node.nodeName]
                    """
                    for kej, vej in sosConfig.foiGeometryType.iteritems():
                        if kej == node.nodeName:
                            GMLfeature = node
                            self.foiType = vej
                            break
                    break
                    """
            if not GMLfeature:
                raise sosException.SOSException(1,"not found GML object in <%s> childs, supported: %s, found: %s" %(foi[0].nodeName,";".join(sosConfig.foiGeometryType),";".join([e.nodeName for e in foi[0].childNodes if e.nodeType == e.ELEMENT_NODE])))
            self.foiSRS = getElemAtt(GMLfeature,"srsName").split(":")[-1]
            a=GMLfeature.toxml()
            geomFoi = ogr.CreateGeometryFromGML(a.encode('ascii','ignore'))
            self.foiWKT = geomFoi.ExportToWkt()
            
            #--result
            res = obs[0].getElementsByTagName('om:result')
            
            self.parameters = []
            self.uoms = []
            ################################33            
            if len(res)==1:
                sdr = res[0].getElementsByTagName('swe:SimpleDataRecord')
                da = res[0].getElementsByTagName('swe:DataArray')
                
                if len(sdr)==1 or len(da)==1:
                    if len(sdr)==1 and len(da)==0:                           
                        fields = sdr[0].getElementsByTagName('swe:field')
                    if len(sdr)==0 and len(da)==1:
                        fields = da[0].getElementsByTagName('swe:field')
                        
                    for field in fields:
                        defin = None
                        uom = None
                        fieldName = getElemAtt(field,"name")
                        tf = field.getElementsByTagName("swe:Time")
                        qf = field.getElementsByTagName("swe:Quantity")
                        
                        if len(tf)==1 and len(qf)==0:
                            #self.parameters.append(getElemAtt(tf[0],"definition").split(":")[-1])
                            self.parameters.append(getElemAtt(tf[0],"definition"))
                            self.uoms.append(uom)
                    
                        elif len(tf)==0 and len(qf)==1:
                            if getElemAtt(qf[0],"definition"):
                                #self.parameters.append(getElemAtt(qf[0],"definition").split(":")[-1])
                                self.parameters.append(getElemAtt(qf[0],"definition"))
                                um = qf[0].getElementsByTagName('swe:uom')
                                if len(um) == 1:
                                    uom = getElemAtt(um[0],"code")
                                self.uoms.append(uom)
                        else:
                            err_txt = "swe:Time or swe:Quantity is mandatory in multiplicity 1:N"
                            raise sosException.SOSException(1,err_txt)

                
                #case simple om:result
                elif len(sdr)==0 and len(da)==0:
                    if len(observedProperties)==1:
                        self.parameters.append(observedProperties[0])
                        self.uoms.append(getElemAtt(res[0],"uom"))
                    else:
                        raise sosException.SOSException(1,"om:observedProperty is mandatory with multiplicity 1")
                        

                else:
                    err_txt = "om:observation ERROR"
                    raise sosException.SOSException(1,err_txt) 
                """
                #####################################################################
                # DEBUG
                #####################################################################
                err_txt = "xmlSensorDescription = %s @" %(self.xmlSensorDescription)
                err_txt += "procedure = %s  @" %(self.procedure)
                err_txt += "observedProperties = %s @" %(self.observedProperties)
                err_txt += "uoms = %s @" %(self.uoms)
                err_txt += "featureOfInterestUrn = %s @" %(self.featureOfInterestUrn)
                err_txt += "featureOfInterestSRS = %s @" %(self.featureOfInterestSRS)
                err_txt += "featureOfInterestWKT = %s @" %(self.featureOfInterestWKT)                
                raise sosException.SOSException(1,err_txt)
                #####################################################################
                """
            
            
            
            
           
            
        








