# -*- coding: utf-8 -*-
# ===============================================================================
#
# Authors: Massimiliano Cannata, Milan Antonovic
#
# Copyright (c) 2015 IST-SUPSI (www.supsi.ch/ist)
#
# This program is free software; you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation; either version 2 of the License, or (at your option)
# any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program; if not, write to the Free Software
# Foundation, Inc., 51 Franklin Street, Fifth Floor, Boston, MA  02110-1301  USA
#
# ===============================================================================
from istsoslib.filters import filter as f
from istsoslib import sosException
from lib.etree import et

def parse_and_get_ns(file):
    events = "start", "start-ns"
    root = None
    ns = {}
    for event, elem in et.iterparse(file, events):
        if event == "start-ns":
            if elem[0] in ns and ns[elem[0]] != elem[1]:
                # NOTE: It is perfectly valid to have the same prefix refer
                #   to different URI namespaces in different parts of the
                #   document. This exception serves as a reminder that this
                #   solution is not robust.  Use at your own peril.
                raise KeyError("Duplicate prefix with different URI found.")
            ns[elem[0]] = "%s" % elem[1]
        elif event == "start":
            if root is None:
                root = elem 
    return et.ElementTree(root), ns

class sosIOfilter(f.sosFilter):
    "filter object for a InsertObservation request"
    #self.sensorId
    #self.samplingTime
    #self.procedure
    #self.observedProperty
    #self.featureOfInterest
    #self.data {def:string {"uom":string,"vals":[]}
    def __init__(self,sosRequest,method,requestObject,sosConfig):
        f.sosFilter.__init__(self,sosRequest,method,requestObject,sosConfig)
        #**************************
        if method == "GET":
            raise sosException.SOSException("NoApplicableCode",None,"insertObservation request support only POST method!")
        
        if method == "POST":
            from StringIO import StringIO
            
            tree, ns = parse_and_get_ns(StringIO(requestObject))
            
            # Workaround for rare xml parsing bug in etree
            ns = {
                'gml': 'http://www.opengis.net/gml',
                'swe': 'http://www.opengis.net/swe',
                'om': 'http://www.opengis.net/om/1.0',
                'sos': 'http://www.opengis.net/sos/1.0',
                'xlink': 'http://www.w3.org/1999/xlink',
                'xsi': 'http://www.w3.org/2001/XMLSchema-instance',
                
            }
            
            if not 'swe' in ns:
                ns['swe'] = 'http://www.opengis.net/swe/1.0.1'
            
            #---assignedSensorId
            #----------------------
            AssignedSensorId = tree.find("{%s}AssignedSensorId" % ns['sos'] )
            if AssignedSensorId == None:
                raise sosException.SOSException("MissingParameterValue","AssignedSensorId","sos:AssignedSensorId parameter is mandatory with multiplicity 1")
            else:
                self.assignedSensorId = AssignedSensorId.text.split(":")[-1]
            
            #---forceInsert
            ForceInsert = tree.find("{%s}ForceInsert" % ns['sos'] )
            if not ForceInsert==None:
                if ForceInsert.text == 'true' or ForceInsert.text == "":
                    self.forceInsert = True 
                elif ForceInsert.text == 'false':
                    self.forceInsert = False
                else:
                    err_txt = "parameter \"ForceInsert\" can only be: 'true' or 'false'"
                    raise sosException.SOSException("InvalidParameterValue","ForceInsert",err_txt)
            else:
                self.forceInsert = False
                
            #---om:observation
            Observation = tree.find("{%s}Observation" % ns['om'] )
            if Observation == None:
                raise sosException.SOSException("MissingParameterValue","Observation","om:Observation tag is mandatory with multiplicity 1")
            
            #-------procedure
            procedure = Observation.find("{%s}procedure" % ns['om'] )
            if procedure == None:
                raise sosException.SOSException("NoApplicableCode",None,"om:procedure tag is mandatory with multiplicity 1")
            self.procedure = procedure.attrib[ "{%s}href" % ns['xlink'] ].split(":")[-1]

            #-------ObservedProperties
            self.oprName=[]
            observedProperty = Observation.find("{%s}observedProperty" % ns['om'] )
            if observedProperty == None:
                raise sosException.SOSException("NoApplicableCode",None,"om:observedProperty tag is mandatory with multiplicity 1")
            
            
            CompositPhenomenon = observedProperty.find("{%s}CompositePhenomenon" % ns['swe'] )
            import traceback, sys
            
            if not CompositPhenomenon == None:
                components = CompositPhenomenon.findall("{%s}component" % ns['swe'] )
                for co in components:
                    try:
                        self.oprName.append(co.attrib[ "{%s}href" % ns['xlink'] ] )
                    except:
                        try:
                            name = co.find("{%s}name" % ns['gml'] )
                            self.oprName.append(name.text)
                        except:
                            raise sosException.SOSException("NoApplicableCode",None,"om:observedProperty Name is missing: 'xlink:href' or 'gml:name' required")
            else:
                try:
                    self.oprName.append(observedProperty.attrib[ "{%s}href" % ns['xlink'] ])
                except:
                    try:
                        name = co.find( "{%s}name" % ns['gml'] )
                        self.oprName.append(name.text)
                    except:
                        print >> sys.stderr, "XML: %s" % requestObject
                        raise sosException.SOSException("NoApplicableCode",None,"om:observedProperty Name is missing: 'xlink:href' or 'gml:name' required")
                    
            #-----samplingTime
            samplingTime = Observation.find("{%s}samplingTime" % ns['om'] )
            if samplingTime==None:
                err_txt = "om:samplingTime is mandatory in multiplicity 1"
                raise sosException.SOSException("NoApplicableCode",None,err_txt)
            
            TimePeriod = samplingTime.find("{%s}TimePeriod" % ns['gml'] )
            if not TimePeriod == None:
                bp = TimePeriod.find("{%s}beginPosition" % ns['gml'] )
                ep = TimePeriod.find("{%s}endPosition" % ns['gml'] )
                if bp==None or ep==None:
                    err_txt = "gml:TimePeriod is mandatory in multiplicity 1"
                    raise sosException.SOSException("NoApplicableCode",None,err_txt)
                self.samplingTime = bp.text + "/" + ep.text

            else:
                TimeInstant = samplingTime.find("{%s}TimeInstant" % ns['gml'] )
                if not TimeInstant==None:
                    tpos = TimeInstant.find("{%s}timePosition" % ns['gml'] )
                    self.samplingTime = tpos.text
                else:
                    err_txt = "one of gml:TimePeriod or gml:TimeInstant is mandatory in multiplicity 1"
                    raise sosException.SOSException("NoApplicableCode",None,err_txt)
            
            #------featureOfInterest
            featureOfInterest = Observation.find("{%s}featureOfInterest" % ns['om'] )
            if featureOfInterest == None:
                raise sosException.SOSException("NoApplicableCode",None,"om:featureOfInterest tag is mandatory with multiplicity 1")
            try:
                self.foiName = featureOfInterest.attrib[ "{%s}href" % ns['xlink'] ].split(":")[-1]
            except:
                try:
                    gml_name = featureOfInterest.find("{%s}name" % ns['gml'] ).split(":")[-1]
                    self.foiName = gml_name.text
                except:
                    raise sosException.SOSException("NoApplicableCode",None,"om:featureOfInterest name is missing: 'xlink:href' or 'gml:name' is required")
            
            #--result
            if Observation.find("{%s}result" % ns['om'] ) == None:
                raise sosException.SOSException("NoApplicableCode",None,"om:result tag is required")
            
            SimpleDataRecord = Observation.find("{%s}result/{%s}SimpleDataRecord" %(ns['om'],ns['swe']) )
            DataArray = Observation.find("{%s}result/{%s}DataArray" %(ns['om'],ns['swe']) )
            
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
            
            self.parameters = []
            self.uoms = []
            self.data = {}
            
            #case SimpleDataRecord 
            if not SimpleDataRecord==None and DataArray==None:
                fields = SimpleDataRecord.findall("{%s}field" % ns['swe'] )
                for field in fields:
                    defin = None
                    uom = None
                    vals = []
                    fieldName = field.attrib["name"]
                    if not field.find("{%s}Time" % ns['swe']) == None:
                        tf = field.find("{%s}Time" % ns['swe'])
                        defin = tf.attrib["definition"]
                        vals.append( tf.find("{%s}value" % ns['swe']).text )
                    elif not field.find("{%s}Quantity" % ns['swe']) == None:
                        qf = field.find("{%s}Quantity" % ns['swe'])
                        defin = qf.attrib["definition"]
                        uom = qf.find("{%s}uom" % ns['swe']).attrib["code"]
                        vals.append( qf.find("{%s}value" % ns['swe']).text )
                    else:
                        err_txt = "swe:Time or swe:Quantity is mandatory in multiplicity 1"
                        raise sosException.SOSException("NoApplicableCode",None,err_txt)
                    self.data[defin]={"uom":uom,"vals":vals}
            
            #Case DataArray
            elif SimpleDataRecord==None and not DataArray==None:
                DataRecord = DataArray.find("{%s}elementType/{%s}DataRecord" % (ns['swe'],ns['swe']))
                fields = DataRecord.findall("{%s}field" % ns['swe'] )
                urnlist=[]
                for id, field in enumerate(fields):
                    defin = None
                    uom = None
                    vals = []
                    #fieldName = field.attrib["name"]
                    if not field.find("{%s}Time" % ns['swe']) == None:
                        swet = field.find("{%s}Time" % ns['swe'])
                        defin = swet.attrib["definition"]
                        urnlist.append(swet.attrib["definition"])
                    elif not field.find("{%s}Quantity" % ns['swe']) == None:
                        sweq = field.find("{%s}Quantity" % ns['swe'])
                        defin = sweq.attrib["definition"]
                        urnlist.append( sweq.attrib["definition"])
                        if not sweq.find("{%s}uom" % ns['swe']) == None:
                           uom = sweq.find("{%s}uom" % ns['swe']).attrib["code"]
                    else:
                        err_txt = "swe:Time or swe:Quantity is mandatory in multiplicity 1"
                        raise sosException.SOSException("NoApplicableCode",None,err_txt)
                    self.data[defin]={"uom":uom,"vals":vals}
                #encoding
                encodingTxtBlock = Observation.find("{%s}result/{%s}DataArray/{%s}encoding/{%s}TextBlock" 
                                            %(ns['om'],ns['swe'],ns['swe'],ns['swe']) )
                if encodingTxtBlock == None:
                    err_txt = "swe:encoding is mandatory in multiplicity 1"
                    raise sosException.SOSException("NoApplicableCode",None,err_txt)
                tokenSeparator = encodingTxtBlock.attrib["tokenSeparator"]
                blockSeparator = encodingTxtBlock.attrib["blockSeparator"]
                #decimalSeparator = encodingTxtBlock.attrib["decimalSeparator"]
                #values
                values = Observation.find("{%s}result/{%s}DataArray/{%s}values" %(ns['om'],ns['swe'],ns['swe']) )
                if values == None:
                    err_txt = "swe:values is mandatory in multiplicity 1"
                    raise sosException.SOSException("NoApplicableCode",None,err_txt)
                
                if values.text:
                    valsplit=[i.split(tokenSeparator) for i in values.text.split(blockSeparator)]
                    for index,c in enumerate(urnlist):
                        col = []
                        for l in valsplit:
                            col.append(l[index])
                        self.data[c]["vals"] = col
                
            
            #case simple om:result
            elif SimpleDataRecord==None and DataArray==None:
                self.data[sosConfig.urn["time"]] = {"uom":None,"vals":[self.samplingTime]}
                result = Observation.find("{%s}result" %(ns['om']) )
                uom = result.attrib["uom"]
                vals = result.text
                self.data[sosConfig.urn["phenomena"]+self.oprName]={"uom":uom,"vals":vals}
                
            #error
            else:
                err_txt = "om:SimpleDataRecord in multiplicity N or om:DataArray in multiplicity 1 is mandatory"
                raise sosException.SOSException("NoApplicableCode",None,err_txt) 
             
        
                        
