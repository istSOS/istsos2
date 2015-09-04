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
from filter_utils import parse_and_get_ns

from lib.isodate import parse_duration
from lib.etree import et
import json

import sys


convertToSec = {
    'min': lambda x: x * 60,
    'h': lambda x: x * 3600,
    'd': lambda x: x * 24 * 3600,
    's': lambda x: x,
    'ms': lambda x: x / 1000,
    'us': lambda x: x / 1000000
}


class sosRSfilter(f.sosFilter):
    """filter object for a registerSensor request


    Attributes:
        request (str): the request submitted
        service (str): the name of the service requested
        version (str): the version of the service
        procedure (str): the procedure name
        time_sam_val (int): the sampling time resolution
        time_acq_val (int): the acquisition taime resolution
        systemType (str): the system type
        xmlSensorDescription (obj): the sensor description etree's element
        oprDef (list): ordered list of observed properties definition
        oprDesc (list): ordered list of observed properties description
        oprName (list): ordered list of observed properties name
        foiName (str): feature of interest name
        foiType (str): feature of interest geometry type
        foiSRS (str): feature of interest EPSG code
        foiGML (str): feature of interest GML representation
        parameters (list): ordered list of parameters observed by the sensor
        uoms (list): ordered list of unit of measures (indexed as parameters)
        names (list): ordered list of parameters's names (indexed as parameters)
        descs (list): ordered list of parameters's description (indexed as parameters)
        constr (list): ordered list of parameters's constraints (indexed as parameters)
        partime (list): ordered list 0-1 values identifing the time parameter (1) or not (0) (indexed as parameters)
        beginPosition (str): set to NULL (TODO: CHECK IF REQUIRED!)

    """

    def __init__(self,sosRequest,method,requestObject,sosConfig):
        f.sosFilter.__init__(self,sosRequest,method,requestObject,sosConfig)
        #**************************
        if method == "GET":
            raise sosException.SOSException("NoApplicableCode",None,"registerSensor request support only POST method!")

        if method == "POST":
            from StringIO import StringIO

            tree, ns = parse_and_get_ns(StringIO(requestObject))

            #---SensorDescription
            #----------------------
            SensorDescription = tree.find("{%s}SensorDescription" % ns['sos'] )
            if SensorDescription == None:
                raise sosException.SOSException("MissingParameterValue","SensorDescription","sos:SensorDescription parameter is mandatory with multiplicity 1")

            #---Procedure Name
            name = tree.find("{%s}SensorDescription/{%s}member/{%s}System/{%s}name"
                            %(ns['sos'],ns['sml'],ns['sml'],ns['gml']) )
            self.procedure = name.text

            #---ProcedureDescription
            description = tree.find("{%s}SensorDescription/{%s}member/{%s}System/{%s}description"
                            %(ns['sos'],ns['sml'],ns['sml'],ns['gml']) )
            if not description==None:
                self.proc_desc = description.text
            else:
                self.proc_desc = 'NULL'

            # Add capabilities time to db
            # Convert all to seconds

            #---Capabilities
            capabilities = tree.findall("{%s}SensorDescription/{%s}member/{%s}System/{%s}capabilities/{%s}DataRecord/{%s}field"
                                            % (ns['sos'],ns['sml'],ns['sml'],ns['sml'],ns['swe'],ns['swe']))
            #print >> sys.stderr, "capabilities: ",capabilities

            self.time_sam_val = "0"
            self.time_acq_val = "0"

            for cap in capabilities:

                if cap.attrib.has_key('name') and cap.attrib['name']=='Sampling time resolution':
                    # parse Sampling time resolution
                    tmpSam = int(cap.find("{%s}Quantity/{%s}value"% (ns['swe'],ns['swe'])).text)
                    uom = cap.find("{%s}Quantity/{%s}uom"% (ns['swe'],ns['swe']))
                    if uom.attrib.has_key('code'):
                        uomSam = uom.attrib['code']
                        self.time_sam_val = convertToSec[uomSam](tmpSam) #convertToSec(uomSam,tmpSam)
                    else:
                        raise sosException.SOSException("MissingParameterValue","SensorDescription","sml:capabilities, missing uom for Sampling time resolution")
                elif cap.attrib.has_key('name') and cap.attrib['name']=='Acquisition time resolution':
                    # parse Acquisition time resolution
                    tmpAcq =  int(cap.find("{%s}Quantity/{%s}value"% (ns['swe'],ns['swe'])).text)
                    uom = cap.find("{%s}Quantity/{%s}uom"% (ns['swe'],ns['swe']))
                    if uom.attrib.has_key('code'):
                        uomAcq = uom.attrib['code']
                        self.time_acq_val = convertToSec[uomAcq](tmpAcq) #convertToSec(uomAcq,tmpAcq)
                    else:
                        raise sosException.SOSException("MissingParameterValue","SensorDescription","sml:capabilities, missing uom for Sampling time resolution")

            print >> sys.stderr, self.time_sam_val

           #---System type
            # From istSOS 2.0 the system type became mandatory (insitu-fixed-point, insitu-mobile-point, ...)
            self.systemType = None
            classifiers = tree.findall("{%s}SensorDescription/{%s}member/{%s}System/{%s}classification/{%s}ClassifierList/{%s}classifier"
                            % ( ns['sos'],ns['sml'],ns['sml'],ns['sml'],ns['sml'],ns['sml'] ) )
            for classifier in classifiers:
                if classifier.attrib.has_key('name') and classifier.attrib['name']=='System Type':
                    val = classifier.find("{%s}Term/{%s}value"
                        % ( ns['sml'],ns['sml']) )
                    if val != None:
                        self.systemType = val.text


            member = tree.find("{%s}SensorDescription/{%s}member" %(ns['sos'],ns['sml']) )
            root = et.Element("{%s}SensorML" % ns['sml'])
            root.attrib[ "{%s}schemaLocation" % ns['xsi'] ] = "http://www.opengis.net/sensorML/1.0.1 http://schemas.opengis.net/sensorML/1.0.1/sensorML.xsd"
            root.attrib["version"] = "1.0.1"
            root.append(member)
            self.xmlSensorDescription = root
            """
            from xml.dom.minidom import parseString
            txt = et.tostring(root, encoding="UTF-8")
            self.xmlSensorDescription = parseString(txt).toprettyxml()
            """

            #---ObservationTemplate
            #----------------------
            ObservationTemplate = tree.find("{%s}ObservationTemplate" % ns['sos'] )
            if ObservationTemplate==None:
                raise sosException.SOSException("MissingParameterValue","ObservationTemplate","ObservationTemplate parameter is mandatory with multiplicity 1")

            Observation = ObservationTemplate.find("{%s}Observation" % ns['om'] )
            if Observation==None:
                raise sosException.SOSException("NoApplicableCode",None,"om:Observation tag is mandatory with multiplicity 1")

            #-------procedure
            procedure = Observation.find("{%s}procedure" % ns['om'] )
            self.procedure = procedure.attrib["{%s}href" % ns['xlink']].split(":")[-1]
            if procedure == None:
                raise sosException.SOSException("NoApplicableCode",None,"om:procedure tag is mandatory with multiplicity 1")

            #-------ObservedProperties
            self.oprDef=[]
            self.oprDesc=[]
            self.oprName=[]
            self.beginPosition = 'NULL'

            try:
                name = Observation.find("{%s}observedProperty/{%s}CompositePhenomenon/{%s}name"
                                        %(ns['om'],ns['swe'],ns['gml']) )
            except:
                raise sosException.SOSException("NoApplicableCode",None,
                                "swe:CompositePhenomenon mandatory name element is missing")

            components = Observation.findall("{%s}observedProperty/{%s}CompositePhenomenon/{%s}component"
                                        %(ns['om'],ns['swe'],ns['swe']) )
            if not components == []:
                for comp in components:
                    try:
                        self.oprDef.append(comp.attrib["{%s}href" % ns['xlink']])
                    except:
                        raise sosException.SOSException("NoApplicableCode",None,
                                "om:observedProperty/component attribute missing: 'xlink:href' required")

                        """ NON STANDARD
                        try:
                            desc = comp.find("{%s}description" % ns['gml'])
                            self.oprDesc.append(desc.text)
                        except:
                            self.oprDesc.append("NULL")

                        try:
                            desc = comp.find("{%s}name" % ns['gml'])
                            self.oprName.append(desc.text)
                        except:
                            self.oprName.append("NULL")
                        """


            """ PER COSA È? CASO NON COMPOSITEPHENOMENON?
            else:
                observedProperty = Observation.find("{%s}observedProperty" % ns['om'])
                try:
                    self.oprName.append(observedProperty.attrib["{%s}href" % ns['xlink']])
                except:
                    name = Observation.find("{%s}observedProperty/{%s}name" %(ns['om'],ns['gml']) )
                    try:
                        self.oprName.append(name.txt)
                    except:
                        raise sosException.SOSException(1,
                                "om:observedProperty Name is missing: 'xlink:href' or 'gml:name' required")

                    desc = Observation.find("{%s}observedProperty/{%s}description" %(ns['om'],ns['gml']) )
                    try:
                        self.oprDesc.append(desc.txt)
                    except:
                        self.oprDesc.append("NULL")
            """

            #-------samplingTime
#==============================================================================
#             samplingTime = Observation.find("{%s}samplingTime" % ns['om'] )
#             if samplingTime == None:
#                 raise sosException.SOSException("NoApplicableCode",None,"om:samplingTime tag is mandatory with multiplicity 1")
#             else:
#                 duration = samplingTime.find("{%s}TimePeriod/{%s}TimeLength/{%s}duration"
#                                             %(ns['gml'],ns['gml'],ns['gml'], ) )
#
#                 if not duration==None:
#
#                     strdur = str( parse_duration( duration.text.strip() ) ).split(",")
#                     if len(strdur)>1:
#                         self.time_res_val = strdur[0].split(" ")[0]
#                         self.time_res_unit = strdur[0].split(" ")[1]
#                     elif len(strdur)==1:
#                         time = strdur[0].split(":")
#                         self.time_res_val = parse_duration( duration.text.strip() ).seconds
#                         self.time_res_unit = "sec"
#                 else:
#                     self.time_res_unit = "unknown"
#                     self.time_res_val = "NULL"
#==============================================================================


            #------featureOfInterest
            featureOfInterest = Observation.find("{%s}featureOfInterest" % ns['om'] )
            if featureOfInterest == None:
                raise sosException.SOSException("NoApplicableCode",None,"om:featureOfInterest tag is mandatory with multiplicity 1")
            try:
                self.foiName = featureOfInterest.attrib["{%s}href" % ns['xlink']]
            except:
                raise sosException.SOSException("NoApplicableCode",None,"om:featureOfInterest: attribute 'xlink:href' is required")
                """ NON COMPLIANT
                name = Observation.find("{%s}featureOfInterest/{%s}name" %(ns['om'],ns['gml']) )
                try:
                    self.foiName = name.text
                except:
                    raise sosException.SOSException(1,"om:featureOfInterest name is missing: 'xlink:href' or 'gml:name' is required")
                """


            description = Observation.find("{%s}featureOfInterest/{%s}FeatureCollection/{%s}description" %(ns['om'],ns['gml'],ns['gml']) )
            if not description == None:
                self.foiDesc = description.text
            else:
                self.foiDesc = "NULL"

            #--foiWKZ
            # gml_type = ["gml:Polygon", "gml:LineString", "gml:Point", "gml:Box", "gml:GeometryCollection",
            #            "gml:MultiPoint", "gml:MultiLineString", "gml:MultiPolygon"]
            self.foiType = None
            for geomtype in sosConfig.foiGeometryType:
                geomtype = geomtype.split(":")[1]
                GMLfeature = Observation.find("{%s}featureOfInterest/{%s}FeatureCollection/{%s}location/{%s}%s"
                                                %(ns['om'],ns['gml'],ns['gml'],ns['gml'],geomtype) )

                if not GMLfeature==None:
                    self.foiType = geomtype
                    self.foiSRS = GMLfeature.attrib["srsName"].split(":")[-1]
                    self.foiGML = et.tostring(GMLfeature, encoding="UTF-8").replace("<?xml version='1.0' encoding='UTF-8'?>","")
            if self.foiType == None:
                raise sosException.SOSException("NoApplicableCode",None,"not found valid GML feature, supported: %s "
                                    %(";".join(sosConfig.foiGeometryType)))


            #--result
            result = Observation.find("{%s}result" % ns['om'] )
            self.parameters = []
            self.uoms = []
            self.names = []
            self.descs = []
            self.constr = []
            self.partime = []

            if not result == None:
                sdr = Observation.find("{%s}result/{%s}SimpleDataRecord" %(ns['om'],ns['swe']) )
                da = Observation.find("{%s}result/{%s}DataArray" %(ns['om'],ns['swe']) )

                if sdr!=None and da==None:
                    fields = sdr.findall("{%s}field" % ns['swe'])
                elif da!=None and sdr==None:
                    fields = da.findall("{%s}elementType/{%s}DataRecord/{%s}field" %(ns['swe'],ns['swe'],ns['swe']))
                else:
                    err_txt = "in <swe:result>: <swe:DataRecord> or <swe:DataArray> are mandatory in multiplicity 1"
                    raise sosException.SOSException("NoApplicableCode",None,err_txt)

                timetag = False
                for field in fields:
                    defin = None
                    uom = None
                    self.names.append(field.attrib['name'])
                    tf = field.find("{%s}Time" % ns['swe'])
                    qf = field.find("{%s}Quantity" % ns['swe'])

                    if not tf==None and qf==None:
                        self.partime.append(1)
                        timetag = True
                        self.parameters.append(tf.attrib["definition"])
                        uom = tf.find("{%s}uom" % ns['swe'])
                        self.uoms.append(uom.attrib["code"])
                        desc = tf.find("{%s}description" % ns['swe'])
                        if not desc==None:
                            self.descs.append(desc.text)
                        else:
                            self.descs.append("NULL")
                        #self.constr.append(None)
                        #self.constr.append("NULL")

                    elif not qf==None and tf==None:
                        self.partime.append(0)
                        self.parameters.append(qf.attrib["definition"])
                        uom = qf.find("{%s}uom" % ns['swe'])
                        self.uoms.append(uom.attrib["code"])
                        desc = qf.find("{%s}description" % ns['swe'])
                        if not desc==None:
                            self.descs.append(desc.text)
                        else:
                            self.descs.append("NULL")

                        # look for constraints [min,max,interval,valueList]
                        #===================================================
                        #import sys
                        cc = {}
                        constraints = qf.findall("{%s}constraint" %(ns['swe']))
                        if len(constraints)==0:
                            self.constr.append(None)
                        else:
                            for constraint in constraints:
                                if constraint:
                                    if "{%s}role" % ns["xlink"] in constraint.attrib:
                                        if constraint.attrib[ "{%s}role" % ns["xlink"] ] == "urn:ogc:def:classifiers:x-istsos:1.0:qualityIndex:check:reasonable":
                                            crole = constraint.attrib[ "{%s}role" % ns["xlink"] ]

                                            allow = constraint.find("{%s}AllowedValues" %(ns['swe']))
                                            if allow is None:
                                                err_txt = "in <swe:constraint>: <swe:AllowedValues> is mandatory in multiplicity 1"
                                                raise sosException.SOSException("NoApplicableCode",None,err_txt)
                                            else:

                                                cvals = None
                                                if len(allow)==1:
                                                    ct = allow[0].tag
                                                    if not ct in ["{%s}min" % ns["swe"],"{%s}max" % ns["swe"],"{%s}interval" % ns["swe"],"{%s}valueList" % ns["swe"]]:
                                                        err_txt = "in <swe:constraint>: support only min, max, interval, valueList tag"
                                                        raise sosException.SOSException("NoApplicableCode",None,err_txt)

                                                    xvals = allow[0].text.strip().split(" ")

                                                    if ct == "{%s}min" % ns["swe"]:
                                                        ct = "min"
                                                        if not len(xvals)==1:
                                                            err_txt = "'%s' constraint support/need one values" % ct
                                                            raise sosException.SOSException("NoApplicableCode",None,err_txt)
                                                        try:
                                                            cvals = float(xvals[0])
                                                        except:
                                                            err_txt = "'%s' constraint requires float value" % ct
                                                            raise sosException.SOSException("NoApplicableCode",None,err_txt)

                                                    elif ct == "{%s}max" % ns["swe"]:
                                                        ct = "max"
                                                        if not len(xvals)==1:
                                                            err_txt = "'%s' constraint support/need one values" % ct
                                                            raise sosException.SOSException("NoApplicableCode",None,err_txt)
                                                        try:
                                                            cvals = float(xvals[0])
                                                        except:
                                                            err_txt = "'%s' constraint requires float value" % ct
                                                            raise sosException.SOSException("NoApplicableCode",None,err_txt)

                                                    elif ct == "{%s}interval" % ns["swe"]:
                                                        ct = "interval"
                                                        if not len(xvals)==2:
                                                            err_txt = "'%s' constraint support/need two values" % ct
                                                            raise sosException.SOSException("NoApplicableCode",None,err_txt)
                                                        try:
                                                            cvals = [float(xvals[0]),float(xvals[1])]
                                                        except:
                                                            err_txt = "'%s' constraint requires float value" % ct
                                                            raise sosException.SOSException("NoApplicableCode",None,err_txt)

                                                    elif ct == "{%s}valueList" % ns["swe"]:
                                                        ct = "valueList"
                                                        if not len(xvals)>0:
                                                            err_txt = "'%s' constraint support/need at least one values" % ct
                                                            raise sosException.SOSException("NoApplicableCode",None,err_txt)
                                                        try:
                                                            cvals = [float(a) for a in xvals]
                                                        except:
                                                            err_txt = "'%s' constraint requires float value" % ct
                                                            raise sosException.SOSException("NoApplicableCode",None,err_txt)

                                                    cc["role"] = crole
                                                    cc["%s" % ct] = cvals

                                if not cc=={}:
                                    self.constr.append(json.dumps(cc))
                                else:
                                    self.constr.append(None)


                    else:
                        err_txt = "swe:Time or swe:Quantity is mandatory in multiplicity 1:N"
                        raise sosException.SOSException("NoApplicableCode",None,err_txt)


            else:
                err_txt = "om:result is mandatory in multiplicity 1:N"
                raise sosException.SOSException("NoApplicableCode",None,err_txt)


            #case simple om:result
            """ WAS
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














