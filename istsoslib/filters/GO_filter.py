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
from istsoslib import sosException, sosUtils
from lib import isodate as iso
from filter_utils import get_name_from_urn
import sys

class sosGOfilter(f.sosFilter):
    """filter object for a GetObservations request

    Attributes:
        request (str): the request submitted
        service (str): the name of the service requested
        version (str): the version of the service
        sosConfig (obj): the configuration preference of istSOS instance
        offering (str): the requeste offering name
        observedProperty (list): the list of observed properties names as string
        responseFormat (str): the name of the desired output format
        srsName (str): the EPSG code of the desired reference system
        eventTime (list): list of time intervals (list of two isodate) and/or time instants (list of one isodate), for example: *[ [2014-10-11T12:00:00+02:00, 2014-11-11T12:00:00+02:00], [2014-13-11T12:00:00+02:00] ]*
        procedure (list): list of procedure names as string
        featureOfInterest (list): list of feature of interest names as string
        featureOfInterestSpatial (str): the SQL WHERE clause to apply the OGC filter expression in XML format specified in the request
        result (str): the SQL WHERE clause to apply the OGC property operator in XML format specified in the request
        resultModel (str): the model to represent the result (*om:Observation*)
        responseMode (str): the response mode (*inline*)
        aggregate_interval (str): the aggregation interval in ISO 8601 duration
        aggregate_function (str): the function to use for aggregation (one of: "AVG","COUNT","MAX","MIN","SUM")
        aggregate_nodata_qi (str): the quality index value to use for representing no data in aggregated time serie
        qualityIndex (bool): if the quality index shall be returned (*True*) or not (*False*)
        qualityFilter (str): CQL-like filter on quality index (>200 returns all the records with all QI greater then 200)

    """
    def __init__(self,sosRequest,method,requestObject,sosConfig):
        f.sosFilter.__init__(self,sosRequest,method,requestObject,sosConfig)
        # @TODO Declare attribute first!
        # self.offering = None
        # etc..

        #**************************
        if method == "GET":
            #---------- THE OFFERING
            if requestObject.has_key("offering"):
                try:
                    self.offering = get_name_from_urn(requestObject["offering"],"offering",sosConfig)
                except Exception as e:
                    raise sosException.SOSException("InvalidParameterValue","offering","%s" % e)
            else:
                raise sosException.SOSException("MissingParameterValue","offering","Parameter \"offering\" is mandatory with multiplicity 1")

            #---------- THE OBSERVED PROPERTY
            if requestObject.has_key("observedproperty"):
                self.observedProperty = []
                oprs = requestObject["observedproperty"].split(",")
                for opr in oprs:
                    # get_name_from_urn limit the ability to ask for an observedProperty with LIKE:
                    # eg: ask "water" to get all the water related data, "water:discharge", "water:temperature" ...
                    #oprName = get_name_from_urn(opr,"property")
                    oprName = opr
                    self.observedProperty.append(oprName) # one-many ID
            else:
                raise sosException.SOSException("MissingParameterValue","observedProperty","Parameter \"observedProperty\" is mandatory with multiplicity N")

            #---------- RESPONSE FORMAT
            if requestObject.has_key("responseformat"):
                if not requestObject["responseformat"] in sosConfig.parameters["GO_responseFormat"]:
                    raise sosException.SOSException("InvalidParameterValue","responseFormat","Parameter \"responseFormat\" sent with invalid value : use one of %s" % "; ".join(sosConfig.parameters["GO_responseFormat"]))
                else:
                    self.responseFormat = requestObject["responseformat"]
            else:
                raise sosException.SOSException("MissingParameterValue","responseFormat","Parameter \"responseFormat\" is mandatory with multiplicity 1") #one

            #OPTIONAL request parameters
            #---------- SRS FILTER
            if requestObject.has_key("srsname"):
                try:
                    self.srsName = get_name_from_urn(requestObject["srsname"],"refsystem",sosConfig)
                except Exception as e:
                    raise sosException.SOSException("InvalidParameterValue","srsname","%s" % e)

                if not self.srsName in sosConfig.parameters["GO_srs"]:
                    raise sosException.SOSException("InvalidParameterValue","srsName","srsName \"%s\" not supported, use one of: %s" %(self.srsName,",".join(sosConfig.parameters["GO_srs"])))
            else:
                self.srsName = sosConfig.parameters["GO_srs"][0]

            #---------- TIME FILTER
            if requestObject.has_key('eventtime'):
                self.eventTime = []
                for i in requestObject["eventtime"].replace(" ","+").split(","):
                    if len(i.split("/")) < 3:
                        self.eventTime.append(i.split("/"))
                    else:
                        raise sosException.SOSException("InvalidParameterValue","eventTime","Parameter \"eventTime\" bad formatted")

                # Checking if some event limitation is reached
                #if sosConfig["maxGoPeriod"]:
                tp=[]
                for t in self.eventTime:
                    if len(t) == 2:
                        tp.append(iso.parse_datetime(t[0]))
                        tp.append(iso.parse_datetime(t[1]))
                    if len(t)==1:
                        tp.append(iso.parse_datetime(t[0]))
                if int(sosConfig.maxGoPeriod) > 0:
                    from datetime import timedelta
                    d = timedelta(hours=int(sosConfig.maxGoPeriod))
                    userPeriod = max(tp)-min(tp)
                    if d < userPeriod:
                        raise sosException.SOSException("InvalidParameterValue","eventTime","You are requesting data for a period of [%s hours], but you are not permitted to ask for a period longer than: %s hours" % (userPeriod,d))

            else:
                self.eventTime = None

            #---------- PROCEDURES FILTER
            if requestObject.has_key("procedure"):
                self.procedure = []
                prcs = requestObject["procedure"].split(",")
                for prc in prcs:
                    try:
                        prcName = get_name_from_urn(prc,"procedure",sosConfig)
                    except Exception as e:
                        raise sosException.SOSException("InvalidParameterValue","procedure","%s" % e)

                    self.procedure.append(prcName)
            else:
                self.procedure = None

            #---------- FEATURES OF INTEREST FILTER
            self.featureOfInterest = None
            self.featureOfInterestSpatial = None
            if requestObject.has_key("featureofinterest"):
                foi = requestObject["featureofinterest"]
                if foi.find("<ogc:")>=0 and foi.find("<gml:")>=0:
                    #raise sosException.SOSException(3,"FOI SPATIAL: %s" %(foi))
                    self.featureOfInterestSpatial = sosUtils.ogcSpatCons2PostgisSql(foi,'geom_foi',sosConfig.istsosepsg)
                else:
                    try:
                        self.featureOfInterest = get_name_from_urn(foi,"feature",sosConfig)
                    except Exception as e:
                        raise sosException.SOSException("InvalidParameterValue","featureofinterest","%s" % e)

                #fois = requestObject["featureOfInterest"].split(",")
                #for foi in fois:
                #    foiName = get_name_from_urn(foi,"feature")
                #    self.featureOfInterest.append(foiName)

            #---------- FILTERS FOR QUERY NOT SUPPORTED YET
            if requestObject.has_key("result"):
                #raise sosException.SOSException(3,"Parameter \"result\" not yet supported")
                self.result = sosUtils.ogcCompCons2PostgisSql(requestObject["result"])
            else:
                self.result = None #zero-one optional

            #---------- RESULT MODEL
            if requestObject.has_key("resultmodel"):
                if requestObject["resultmodel"] in sosConfig.parameters["GO_resultModel"]:
                    self.resultModel = requestObject["resultmodel"]
                else:
                    raise sosException.SOSException("InvalidParameterValue","resultModel","Parameter \"resultModel\" sent with invalid value: supported values are: %s" %",".join(sosConfig.parameters["GO_resultModel"]))
            else:
                self.resultModel = sosConfig.parameters["GO_resultModel"][0]

            #---------- RESPONSE MODE
            if requestObject.has_key("responsemode"):
                if requestObject["responsemode"] in sosConfig.parameters["GO_responseMode"]:
                    self.responseMode = requestObject["responsemode"]
                else:
                    raise sosException.SOSException("InvalidParameterValue","responseMode","Parameter \"responseMode\" sent with invalid value, supported values are: %s" %(",".join(sosConfig.parameters["GO_responseMode"])))

            else:
                self.responseMode = sosConfig.parameters["GO_responseMode"][0]

            ###########################
            # NON STANDARD PARAMETERS #
            ###########################
            #---------- AGGREGATE INTERVAL
            # In ISO 8601 duration format
            if requestObject.has_key("aggregateinterval"):
                # Check on the eventTime parameter: it must be only one interval: 2010-01-01T00:00:00+00/2011-01-01T00:00:01+00
                exeMsg = "Using aggregate functions, the event time must exist with an interval composed by a begin and an end date (ISO8601)"
                if self.eventTime == None or len(self.eventTime)!=1 or len(self.eventTime[0])!=2:
                    raise sosException.SOSException("InvalidParameterValue","aggregateInterval",exeMsg)
                self.aggregate_interval = requestObject["aggregateinterval"]
                try:
                    iso.parse_duration(self.aggregate_interval)
                except Exception as ex:
                    raise sosException.SOSException("InvalidParameterValue","aggregateInterval","Parameter \"aggregate_interval\" sent with invalid format (check ISO8601 duration spec): %s" % ex)
            else:
                self.aggregate_interval = None

            #---------- AGGREGATE FUNCTION
            # sum,avg,max,min
            if requestObject.has_key("aggregatefunction"):
                if self.aggregate_interval==None:
                    raise sosException.SOSException("InvalidParameterValue","aggregateFunction","Using aggregate functions parameters \"aggregateInterval\" and \"aggregateFunction\" are both mandatory")
                self.aggregate_function = requestObject["aggregatefunction"]
                if not (self.aggregate_function.upper() in ["AVG","COUNT","MAX","MIN","SUM"]):
                    raise sosException.SOSException("InvalidParameterValue","aggregateFunction","Available aggregation functions: avg, count, max, min, sum.")
            else:
                self.aggregate_function = None

            #---------- AGGREGATE NODATA
            if requestObject.has_key("aggregatenodata"):
                if self.aggregate_interval==None or self.aggregate_function==None:
                    raise sosException.SOSException("InvalidParameterValue","aggregateNodata","Using aggregateNodata parameter requires both \"aggregateInterval\" and \"aggregateFunction\"")
                self.aggregate_nodata = requestObject["aggregatenodata"]
            else:
                self.aggregate_nodata = sosConfig.aggregate_nodata

            #---------- AGGREGATE NODATA QUALITY INDEX
            if requestObject.has_key("aggregatenodataqi"):
                if self.aggregate_interval==None or self.aggregate_function==None:
                    raise sosException.SOSException("InvalidParameterValue","aggregateNodataQi","Using aggregateNodataQi parameter requires both \"aggregateInterval\" and \"aggregateFunction\"")
                self.aggregate_nodata_qi = requestObject["aggregatenodataqi"]
            else:
                self.aggregate_nodata_qi = sosConfig.aggregate_nodata_qi

            #------------ QUALITY INDEX
            self.qualityIndex=False
            if requestObject.has_key("qualityindex"):
                if requestObject["qualityindex"].upper() == "TRUE":
                    self.qualityIndex = True
                elif requestObject["qualityindex"].upper() == "FALSE":
                    self.qualityIndex = False
                else:
                    raise sosException.SOSException("InvalidParameterValue","qualityIndex","qualityIndex can only be True or False!")
                #    self.qualityIndex = sosUtils.CQLvalueFilter2PostgisSql("id_qi_fk",requestObject["qualityIndex"])

            #------------ QUALITY INDEX FILTERING
            self.qualityFilter=False
            #import sys
            #print >> sys.stderr, "**************************"
            #print >> sys.stderr, requestObject
            if requestObject.has_key("qualityfilter"):
                #print >> sys.stderr, " > qualityFilter is set"
                if len(requestObject["qualityfilter"])>=2:
                    try:
                        if requestObject["qualityfilter"][0:2]=='<=' or requestObject["qualityfilter"][0:2]=='>=':
                            self.qualityFilter = (requestObject["qualityfilter"][0:2],float(requestObject["qualityfilter"][2:]))
                        elif (requestObject["qualityfilter"][0]=='>' or
                                requestObject["qualityfilter"][0]=='=' or
                                requestObject["qualityfilter"][0]=='<'):
                            self.qualityFilter = (requestObject["qualityfilter"][0],float(requestObject["qualityfilter"][1:]))

                        # If qualityFilter is defined qualityIndex are automatically returned
                        self.qualityIndex=True
                        #print >> sys.stderr, self.qualityFilter
                    except ValueError as ve:
                        raise sosException.SOSException("InvalidParameterValue","qualityFilter","invalid quality index value in qualityFilter")
                else:
                    raise sosException.SOSException("InvalidParameterValue","qualityFilter","qualityFilter operator can only be in ['<','>','<=','>=','=']")



        #**********************
        if method == "POST":

            from xml.dom import minidom
            #---------- THE OFFERING
            offs = requestObject.getElementsByTagName('offering')
            if len(offs) == 1:
                val = offs[0].firstChild
                if val.nodeType == val.TEXT_NODE:
                    try:
                        self.offering = get_name_from_urn(str(val.data),"offering",sosConfig)
                    except Exception as e:
                        raise sosException.SOSException("InvalidParameterValue","offering","%s" % e)
                else:
                    err_txt = "XML parsing error (get value: offering)"
                    raise sosException.SOSException("NoApplicableCode",None,err_txt)
            else:
                err_txt = "Parameter \"offering\" is mandatory with multiplicity 1"
                raise sosException.SOSException("MissingParameterValue","offering",err_txt)


            #---------- THE OBSERVED PROPERTY
            obsProps = requestObject.getElementsByTagName('observedProperty')
            self.observedProperty = []
            if len(obsProps) > 0:
                for obsProp in obsProps:
                    val = obsProp.firstChild
                    if val.nodeType == val.TEXT_NODE:
                        # get_name_from_urn limit the ability to ask for an observedProperty with LIKE:
                        # eg: ask "water" to get all the water related data, "water:discharge", "water:temperature" ...
                        #self.observedProperty.append(get_name_from_urn(str(val.data),"property"))
                        self.observedProperty.append(str(val.data))
                    else:
                        err_txt = "XML parsing error (get value: observedProperty)"
                        raise sosException.SOSException("NoApplicableCode",None,err_txt)
            else:
                err_txt = "Parameter \"observedProperty\" is mandatory with multiplicity N"
                raise sosException.SOSException("MissingParameterValue","observedProperty",err_txt)

            #---------- RESPONSE FORMAT
            respF = requestObject.getElementsByTagName('responseFormat')
            if len(respF) == 1:
                val = respF[0].firstChild
                if val.nodeType == val.TEXT_NODE:
                    self.responseFormat = str(val.data)
                    if self.responseFormat not in sosConfig.parameters["GO_responseFormat"]:
                        raise sosException.SOSException("InvalidParameterValue","responseFormat","Parameter \"responseFormat\" sent with invalid value: use one of %s" % "; ".join(sosConfig.parameters["GO_responseFormat"]))
                else:
                    err_txt = "XML parsing error (get value: responseFormat)"
                    raise sosException.SOSException("NoApplicableCode",None,err_txt)
            else:
                err_txt = "Parameter \"responseFormat\" is mandatory with multiplicity 1"
                raise sosException.SOSException("MissingParameterValue","responseFormat",err_txt)

            #OPTIONAL request parameters
            #---------- SRS OF RETURNED GML FEATURES
            srs = requestObject.getAttributeNode('srsName')
            if srs:
                self.srsName = srs.nodeValue
                if not self.srsName in sosConfig.parameters["GO_srs"]:
                    raise sosException.SOSException("InvalidParameterValue","srsName","srsName \"%s\" not supported, use one of: %s" %(self.srsName,",".join(sosConfig.parameters["GO_srs"])))
            else:
                self.srsName = sosConfig.parameters["GO_srs"][0]
            """
            srss = requestObject.getElementsByTagName('srsName')
            if len(srss) > 0:
                if len(srss) < 2:
                    val = srss[0].firstChild
                    if val.nodeType == val.TEXT_NODE:
                        self.srsName = get_name_from_urn(str(val.data),"refsystem",sosConfig)
                    else:
                        err_txt = "XML parsing error (get value: srsName)"
                        raise sosException.SOSException("NoApplicableCode",None,err_txt)
                else:
                    err_txt = "Allowed only ONE parameter \"srsName\""
                    raise sosException.SOSException("NoApplicableCode",None,err_txt)
            else:
                self.srsName = sosConfig.parameters["GO_srs"][0]
            """
            #---------- TIME FILTER
            evtms = requestObject.getElementsByTagName('eventTime')
            self.eventTime = []
            if len(evtms) > 0:
                for evtm in evtms:
                    tps = evtm.getElementsByTagName('gml:TimePeriod')
                    for tp in tps:
                        begin = tp.getElementsByTagName('gml:beginPosition')
                        end = tp.getElementsByTagName('gml:endPosition')
                        if len(begin)==1 and len(end)==1:
                            Bval = begin[0].firstChild
                            Eval = end[0].firstChild
                            #raise sosException.SOSException(1,end[0].toprettyxml())
                            if Bval.nodeType == Bval.TEXT_NODE and Eval.nodeType == Eval.TEXT_NODE:
                                self.eventTime.append([str(Bval.data).replace(" ","+"),str(Eval.data).replace(" ","+")])
                                #raise sosException.SOSException(1,str(self.eventTime))
                            else:
                                err_txt = "XML parsing error (get value: TimePeriod)"
                                raise sosException.SOSException("NoApplicableCode",None,err_txt)

                    tis = evtm.getElementsByTagName('gml:TimeInstant')
                    for ti in tis:
                        instant = ti.getElementsByTagName('gml:timePosition')
                        if len(instant)>0 and len(instant)<2:
                            Ival = instant[0].firstChild
                            if Ival.nodeType == Ival.TEXT_NODE:
                                self.eventTime.append([str(Ival.data).replace(" ","+")])
                            else:
                                err_txt = "XML parsing error (get value: Timeinstant)"
                                raise sosException.SOSException("NoApplicableCode",None,err_txt)
            else:
                self.eventTime = None

            #---------- PROCEDURES FILTER
            procs = requestObject.getElementsByTagName('procedure')
            if len(procs) > 0:
                self.procedure=[]
                for proc in procs:
                    if "xlink:href" in proc.attributes.keys():
                        self.procedure.append(str(proc.getAttribute("xlink:href")))
                    elif proc.hasChildNodes():
                        val = proc.firstChild
                        if val.nodeType == val.TEXT_NODE:
                            try:
                                self.procedure.append(get_name_from_urn(str(val.data),"procedure",sosConfig))
                            except Exception as e:
                                raise sosException.SOSException("InvalidParameterValue","procedure","%s" % e)
                    else:
                        err_txt = "XML parsing error (get value: procedure)"
                        raise sosException.SOSException("NoApplicableCode",None,err_txt)
            else:
                self.procedure = None

            #---------- FEATURES OF INTEREST FILTER
            fets = requestObject.getElementsByTagName('featureOfInterest')
            self.featureOfInterest = None
            self.featureOfInterestSpatial = None
            # get sub-elements of FOI
            if fets:
                elements = [e for e in fets[0].childNodes if e.nodeType == e.ELEMENT_NODE]
#            else:
#               import sys
#               print >> sys.stderr, "\n\nELE: %s" % len(elements)
#                err_txt = "Parameter \"featureOfInterest\" is mandatory"
#                raise sosException.SOSException("MissingParameterValue","featureOfInterest",err_txt)

                if len(elements)==0:
                    err_txt = "ObjectID or ogc:spatialOps elements in parameter \"featureOfInterest\" are mandatory"
                    raise sosException.SOSException("NoApplicableCode",None,err_txt)
                # only one sub element
                elif len(elements)==1 and elements[0].tagName!="ObjectID" :
                    self.featureOfInterestSpatial = sosUtils.ogcSpatCons2PostgisSql(elements[0],'geom_foi',sosConfig.istsosepsg)
                else:
                    tempfois=[]
                    for e in elements:
                        if not e.tagName=="ObjectID":
                            err_txt = "Allowed only ObjectID or ogc:spatialOps elements in parameter \"featureOfInterest\""
                            raise sosException.SOSException("NoApplicableCode",None,err_txt)
                        try:
                            val = e.firstChild
                            import sys
                            print >> sys.stderr, "\n\nVAL: %s\n\n" % (val.data)
                            if val.nodeType == val.TEXT_NODE:
                                try:
                                    tempfois.append( get_name_from_urn(str(val.data),"feature",sosConfig) )
                                except Exception as e:
                                     raise sosException.SOSException("InvalidParameterValue","featureOfInterest","%s" % e)
                        except Exception as e:
                            raise e

                    self.featureOfInterest = ",".join(tempfois)


            #---------- FILTERS FOR QUERY NOT SUPPORTED YET
            ress = requestObject.getElementsByTagName('result')
            if len(ress)>0:
                raise sosException.SOSException("NoApplicableCode",None,"Parameter \"result\" not yet supported")
            else:
                self.result = None #zero-one optional

            #---------- RESULT MODEL
            mods = requestObject.getElementsByTagName('resultModel')
            if len(mods)>0:
                if len(mods)<2:
                    val = mods[0].firstChild
                    if val.nodeType == val.TEXT_NODE:
                        self.resultModel = str(val.data)
                        if self.resultModel not in sosConfig.parameters["GO_resultModel"]:
                            raise sosException.SOSException("InvalidParameterValue","resultModel","Parameter \"resultModel\" sent with invalid value")
                    else:
                        err_txt = "XML parsing error (get value: resultModel)"
                        raise sosException.SOSException("NoApplicableCode",None,err_txt)
                else:
                    err_txt = "Allowed only ONE parameter \"resultModel\""
                    raise sosException.SOSException("NoApplicableCode",None,err_txt)
            else:
                self.resultModel = None

            #---------- RESPONSE MODE
            rsmods = requestObject.getElementsByTagName('responseMode')
            if len(rsmods)>0:
                if len(rsmods)<2:
                    val = rsmods[0].firstChild
                    if val.nodeType == val.TEXT_NODE:
                        self.responseMode = str(val.data)
                        if self.responseMode not in sosConfig.parameters["GO_responseMode"]:
                            raise sosException.SOSException("InvalidParameterValue","responseMode","Parameter \"responseMode\" sent with invalid value")
                    else:
                        err_txt = "XML parsing error (get value: responseMode)"
                        raise sosException.SOSException("NoApplicableCode",None,err_txt)
                else:
                    err_txt = "Allowed only ONE parameter \"responseMode\""
                    raise sosException.SOSException("NoApplicableCode",None,err_txt)
            else:
                self.responseMode = sosConfig.parameters["GO_responseMode"][0]


            #-------------- AGGREGATE INTERVAL & FUNCTION
            self.aggregate_interval = None
            self.aggregate_function = None
            self.aggregate_nodata = None
            self.aggregate_nodata_qi = None

            aggint = requestObject.getElementsByTagName('aggregateInterval')
            aggfun = requestObject.getElementsByTagName('aggregateFunction')
            aggnodata = requestObject.getElementsByTagName('aggregateNodata')

            if len(aggint)==1 and len(aggfun)==1:
                #-----------------------
                # -- aggregate_interval
                #-----------------------
                # Check on the eventTime parameter: it must be only one interval: 2010-01-01T00:00:00+00/2011-01-01T00:00:01+00
                exeMsg = "Using aggregate functions, the event time must exist with an interval composed by a begin and an end date (ISO8601)"
                if self.eventTime == None or len(self.eventTime)!=1 or len(self.eventTime[0])!=2:
                    raise sosException.SOSException("NoApplicableCode",None,exeMsg)
                val = aggint[0].firstChild
                if val.nodeType == val.TEXT_NODE:
                    self.aggregate_interval = str(val.data)
                    try:
                        iso.parse_duration(self.aggregate_interval)
                    except Exception as ex:
                        raise sosException.SOSException("InvalidParameterValue","aggregateInterval","Parameter \"aggregate_interval\" sent with invalid format (check ISO8601 duration spec): %s" % ex)
                else:
                    err_txt = "cannot get ISO8601 duration value in \"aggregateInterval\""
                    raise sosException.SOSException("InvalidParameterValue","aggregateInterval",err_txt)
                #-----------------------
                # -- aggregate_function
                #-----------------------
                val = aggfun[0].firstChild
                if val.nodeType == val.TEXT_NODE:
                    self.aggregate_function = str(val.data)
                    if not (self.aggregate_function.upper() in ["AVG","COUNT","MAX","MIN","SUM"]):
                        raise sosException.SOSException("InvalidParameterValue","aggregateFunction","Available aggregation functions: avg, count, max, min, sum.")


                #-----------------------------------
                # -- aggregate_no_data default value
                #-----------------------------------
                if len(aggnodata)==1:
                    val = aggnodata[0].firstChild
                    self.aggregate_nodata = str(val.data)
                else:
                    self.aggregate_nodata = sosConfig.aggregate_nodata

           #================================
           #MISSING AGGREGATE QUALITY INDEX
           #================================

            elif len(aggint)==0 and len(aggfun)==0:
                pass
            else:
                err_txt = "\"aggregateInterval\" and \"aggregate_function\" are both required with multiplicity 1"
                raise sosException.SOSException("NoApplicableCode",None,err_txt)

            #------------ QUALITY INDEX
            self.qualityIndex=False
            qidx = requestObject.getElementsByTagName('qualityIndex')

            if len(qidx)>0:
                if len(qidx)<2:
                    val = qidx[0].firstChild
                    if val.nodeType == val.TEXT_NODE:
                        self.qualityIndex = str(val.data)
                        if self.qualityIndex.upper() == "TRUE":
                            self.qualityIndex=True
                        elif self.qualityIndex.upper() == "FALSE":
                            pass
                        else:
                            raise sosException.SOSException("InvalidParameterValue","qualityIndex","qualityIndex can only be \'True\' or \'False\'")
            elif len(qidx)==0:
                pass
            else:
                err_txt = "\"qualityIndex\" is allowed with multiplicity 1 only"
                raise sosException.SOSException("NoApplicableCode",None,err_txt)

            self.qualityFilter=False
