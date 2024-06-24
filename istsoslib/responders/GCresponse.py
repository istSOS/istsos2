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

import os
import sys
import importlib
from istsoslib.filters import DS_filter
from ..utils import escape

class ServiceIdentification:
    """Service identification of the GetCapabilities responseFormat

    Attributes:
        title (str): service name
        abstract (str): service abstract
        keywords (str): service keywords
        serviceTypeCode (str): service type code
        serviceTypeValue (str): service type value
        serviceTypeVersion (str): service type version
        fees (str): service fees
        accessconstrains (str): service access constrains
    """
    def __init__(self,sosConfig):
        self.title=sosConfig.serviceIdentification["title"]
        self.abstract=sosConfig.serviceIdentification["abstract"]
        self.keywords=sosConfig.serviceIdentification["keywords"]
        self.serviceTypeCode=sosConfig.serviceType["codespace"]
        self.serviceTypeValue=sosConfig.serviceType["value"]
        self.serviceTypeVersion=sosConfig.serviceType["version"]
        self.fees=sosConfig.serviceIdentification["fees"]
        self.accessconstrains=sosConfig.serviceIdentification["accessConstrains"]

class ServiceProvider:
    """Service provider of the GetCapabilities responseFormat

    Attributes:
        providerName (str): provider name
        providerSite (str): provider site
        individualName (str): individual name
        positionName (str): position name
        contactVoice (str): contact voice number
        contactFax (str): contact fax number
        contactDelivery (str): contact delivery address
        contactCity (str): contact city
        contactArea (str): contact area
        contactPostCode (str): contact post code
        contactCountry (str): contact country
        contactMail (str): contact email

    """

    def __init__(self,sosConfig):
        self.providerName=sosConfig.serviceProvider["providerName"]
        self.providerSite=sosConfig.serviceProvider["providerSite"]
        self.individualName=sosConfig.serviceProvider["serviceContact"]["individualName"]
        self.positionName=sosConfig.serviceProvider["serviceContact"]["positionName"]
        self.contactVoice=sosConfig.serviceProvider["serviceContact"]["contactInfo"]["voice"]
        self.contactFax=sosConfig.serviceProvider["serviceContact"]["contactInfo"]["fax"]
        self.contactDelivery=sosConfig.serviceProvider["serviceContact"]["contactInfo"]["deliveryPoint"]
        self.contactCity=sosConfig.serviceProvider["serviceContact"]["contactInfo"]["city"]
        self.contactArea=sosConfig.serviceProvider["serviceContact"]["contactInfo"]["administrativeArea"]
        self.contactPostCode=sosConfig.serviceProvider["serviceContact"]["contactInfo"]["postalCode"]
        self.contactCountry=sosConfig.serviceProvider["serviceContact"]["contactInfo"]["country"]
        self.contactMail=sosConfig.serviceProvider["serviceContact"]["contactInfo"]["email"]

class Parameter:
    """Parameter object

    Attributes:
        name (str): attribute name
        use (str): attribute use
        allowedValues (list): allowed values
        range (list): ranges
    """
    def __init__(self, name, use = "optional", allowedValues=[],range=[], referenceSystem=False):
        self.name=name
        self.use=use
        self.allowedValues=allowedValues
        self.range=range
        self.referenceSystem=referenceSystem

class Operation:
    """Operation object

    Attributes:
        name (str): operation name
        get (str): address for get request
        post (str): address for post request
        parameters (list): list of parameter objects *istsoslib.responders.GCresponse.Parameter*

    """
    def __init__(self,name,get="",post=""):
        self.name=name
        self.get=get
        self.post=post
        self.parameters=[]
    def addParameter(self,name,use = "optional",allowedValues=[],range=[], referenceSystem=False):
        self.parameters.append(Parameter(name,use,allowedValues,range,referenceSystem))

def BuildSensorIdList(pgdb,sosConfig):
    """Generate the sensor list

    Args:
        pgdb (obj): the database object *istsoslib.sosDatabase.PgDB*
        sosCOnfig (obj): the istsos configuration object

    Returns:
        sensorList (list): the list of sensor names
    """
    list=[]
    sql = "SELECT name_prc FROM %s.procedures ORDER BY name_prc" %(sosConfig.schema)
    try:
        rows=pgdb.select(sql)
    except:
        raise Exception("sql: %s" %(pgdb.mogrify(sql)))
    for row in rows:
        list.append(sosConfig.urn["procedure"] + row["name_prc"])
    return list

def BuildOfferingList(pgdb,sosConfig):
    """Generate the offering list

    Args:
        pgdb (obj): the database object *istsoslib.sosDatabase.PgDB*
        sosCOnfig (obj): the istsos configuration object

    Returns:
        offeringList (list): the list of offering names
    """
    list=[]
    sql = "SELECT distinct(name_off) FROM %s.procedures, %s.off_proc, %s.offerings" %(sosConfig.schema,sosConfig.schema,sosConfig.schema)
    sql += " WHERE id_prc=id_prc_fk AND id_off_fk=id_off ORDER BY name_off"
    try:
        rows=pgdb.select(sql)
    except:
        raise Exception("sql: %s" %(pgdb.mogrify(sql)))
    #rows=pgdb.select(sql)
    for row in rows:
        list.append(sosConfig.urn["offering"] + row["name_off"])
    return list


def BuildOfferingList_2_0_0(pgdb,sosConfig):
    """Generate the sensor list

    Args:
        pgdb (obj): the database object *istsoslib.sosDatabase.PgDB*
        sosCOnfig (obj): the istsos configuration object

    Returns:
        sensorList (list): the list of sensor names
    """
    list=[]
    sql = "SELECT name_prc FROM %s.procedures ORDER BY name_prc" % (sosConfig.schema)
    try:
        rows=pgdb.select(sql)
    except:
        raise Exception("sql: %s" %(pgdb.mogrify(sql)))
    for row in rows:
        list.append(sosConfig.urn["offering"] + row["name_prc"])
    return list
    
def BuildEventTimeRange(pgdb,sosConfig):
    """Generate observation time interval

    Args:
        pgdb (obj): the database object *istsoslib.sosDatabase.PgDB*
        sosCOnfig (obj): the istsos configuration object

    Returns:
        eventime (list): a two element list with begin and end position of sensor observations
    """
    sql = "SELECT min(stime_prc) as b, max(etime_prc) as e FROM %s.procedures" %(sosConfig.schema)
    #sql = "SELECT min(time_eti) as b, max(time_eti) as e FROM %s.event_time" %(sosConfig.schema)
    try:
        rows=pgdb.select(sql)
    except:
        raise Exception("sql: %s" %(pgdb.mogrify(sql)))
    #check if not observation?!?!?!?
    return [rows[0]["b"],rows[0]["e"]]

def BuildEnvelopeMinMax(pgdb,sosConfig):
    sosEpsgList = [sosConfig.istsosepsg,]*2
    sosSchemaList = [sosConfig.schema,]*3
    sqlParamsList = sosEpsgList+sosSchemaList+[sosConfig.istsosepsg, sosConfig.schema]
    sql = """
        SELECT 
            st_XMin(envelope) as mix,
            st_YMin(envelope) as miy,
            st_XMax(envelope) as max,
            st_YMax(envelope) as may
        FROM
        (
        	select ST_ENVELOPE(ST_Collect(ST_Transform(envelope,%s))) as envelope 
        	from (
        			select 
        			  ST_ENVELOPE(ST_Collect(ST_Transform(geom_pos,%s))) as envelope 
        			FROM 
        			  %s.positions, %s.event_time, %s.procedures
        			WHERE 
        			  id_prc = id_prc_fk
        			AND
        			  id_eti = id_eti_fk
        		union
        			select 
        			  ST_ENVELOPE(ST_Collect(ST_Transform(geom_foi,%s))) as envelope 
        			FROM 
        			  %s.foi
        	) as g
        ) as s
    """ % (tuple(sqlParamsList))
    result = [0,0,0,0]
    rows=pgdb.select(sql)
    if len(rows) == 1:
        result = ["%s %s" % (rows[0]['mix'], rows[0]['miy']), "%s %s" % (rows[0]['max'], rows[0]['may'])]
    return result
    
def BuildobservedPropertyList(pgdb,sosConfig):
    """Generate observed properties

    Args:
        pgdb (obj): the database object *istsoslib.sosDatabase.PgDB*
        sosCOnfig (obj): the istsos configuration object

    Returns:
        obsprop (list): a list of unique observed properties definitions
    """
    list=[]
    sql = "SELECT distinct(def_opr) as nopr FROM %s.procedures,%s.proc_obs,%s.observed_properties" %(sosConfig.schema,sosConfig.schema,sosConfig.schema)
    sql += " WHERE id_prc_fk=id_prc AND id_opr_fk=id_opr ORDER BY nopr"
    rows=pgdb.select(sql)
    for row in rows:
        #list.append(sosConfig.urn["phenomena"] + row["nopr"])
        list.append(row["nopr"])
    return list

def BuildfeatureOfInterestList(pgdb,sosConfig):
    """Generate feature of interests

    Args:
        pgdb (obj): the database object *istsoslib.sosDatabase.PgDB*
        sosCOnfig (obj): the istsos configuration object

    Returns:
        fois (list): a list of unique feature of interests
    """
    list=[]
    sql = "SELECT distinct(name_fty||':'||name_foi) as nfoi FROM %s.foi, %s.feature_type" %(sosConfig.schema,sosConfig.schema)
    sql += " WHERE id_fty=id_fty_fk ORDER BY nfoi"
    try:
        rows=pgdb.select(sql)
    except:
        raise Exception("sql: %s" %(pgdb.mogrify(sql)))
    for row in rows:
        if row["nfoi"]:
            list.append(sosConfig.urn["feature"] + row["nfoi"])
    return list

def BuildOffEnvelope(pgdb,id,sosConfig):
    """Generate offering envelope

    Args:
        pgdb (obj): the database object *istsoslib.sosDatabase.PgDB*
        sosCOnfig (obj): the istsos configuration object

    Returns:
        envel (str): gml representation of offering bounding box as gml:envelope
    """
    sql = "SELECT ST_asgml(Box2D(u.geom)) as ext FROM"
    sql += " ("
    #----case obs_type = fix
    sql += " SELECT ST_Transform(geom_foi,%s) as geom FROM %s.off_proc," %(sosConfig.istsosepsg,sosConfig.schema)
    sql += " %s.procedures, %s.foi" %(sosConfig.schema,sosConfig.schema)
    sql += " WHERE id_prc_fk=id_prc AND id_foi_fk=id_foi AND id_off_fk=%s"
    #---------------
    sql += " UNION"
    #----case obs_type = mobile
    sql += " SELECT ST_Transform(geom_pos,%s) as geom FROM %s.positions, %s.event_time e," %(sosConfig.istsosepsg,sosConfig.schema,sosConfig.schema)
    sql += " %s.procedures, %s.off_proc o" %(sosConfig.schema,sosConfig.schema)
    sql += " WHERE id_eti=id_eti_fk AND id_prc=e.id_prc_fk AND id_prc=o.id_prc_fk AND id_off_fk=%s"
    #----------------
    sql += " ) u"
    params=(id,id)

    # TODO:
    #  igrac specified
    sql = "SELECT ST_asgml(Box2D(location)) as ext FROM mv_well"
    params=None
    try:
        rows=pgdb.select(sql,params)
    except:
        raise Exception("sql: %s" %(pgdb.mogrify(sql,params)))

    # Retrieve any of the gml:* elements below to go inside the gml:Envelope tag.
    # Unfortunately, xml.etree.ElementTree.fromstring cannot parse xml elements with
    # an unknown prefix, so I have to revert to string manipulation.
    result = "<gml:Null>Not Applicable</gml:Null>"
    if rows:
        gml = rows[0]["ext"]
        # TODO: a better solution would be to parse these from the schema definition.
        for element in ['gml:coordinates','gml:lowerCorner', 'gml:coord', 'gml:pos']:
            open_tag = '<%s>' % element
            close_tag = '</%s>' % element
            pos = gml.find(open_tag)
            if pos:
                gml = gml[pos:]
                pos = gml.find(close_tag)
                result = gml[:pos+len(close_tag)]
                break
    return result


def BuildOffTimePeriod(pgdb,id,sosConfig):
    """Generate offering time interval

    Args:
        pgdb (obj): the database object *istsoslib.sosDatabase.PgDB*
        id (int): the offering id
        sosCOnfig (obj): the istsos configuration object

    Returns:
        eventime (list): a two element list with begin and end position of the given offering id
    """
    sql = "SELECT max(etime_prc) as e, min(stime_prc) as b"
    sql += " from %s.procedures, %s.off_proc o" %(sosConfig.schema,sosConfig.schema)
    sql += " WHERE o.id_prc_fk=id_prc and id_off_fk=%s"
    params = (id,)
    try:
        rows=pgdb.select(sql,params)
    except Exception as err:
        raise Exception("SQL2: %s - %s" %(pgdb.mogrify(sql,params), err))

    return [rows[0]["b"],rows[0]["e"]]

def BuildOffProcList(pgdb,id,sosConfig):
    """Generate the list of procedures for a given offering

    Args:
        pgdb (obj): the database object *istsoslib.sosDatabase.PgDB*
        id (int): the offering id
        sosCOnfig (obj): the istsos configuration object

    Returns:
        procedures (list): the list of procedured belonging to the given offering id
    """
    list=[]
    sql = "SELECT distinct(name_prc)"
    sql += " FROM %s.off_proc, %s.procedures,%s.offerings" %(sosConfig.schema,sosConfig.schema,sosConfig.schema)
    sql += " WHERE id_off=id_off_fk AND id_prc_fk=id_prc AND id_off=%s"
    sql += " ORDER BY name_prc"
    params = (id,)
    try:
        rows=pgdb.select(sql,params)
    except:
        raise Exception("sql: %s" %(pgdb.mogrify(sql,params)))
    for row in rows:
        #list.append(sosConfig.urn["procedure"] + row["name_prc"])
        list.append(escape(row["name_prc"]))
    return list

def BuildOffObsPrList(pgdb,id,sosConfig):
    """Generate the list of properties for a given offering

    Args:
        pgdb (obj): the database object *istsoslib.sosDatabase.PgDB*
        id (int): the offering id
        sosCOnfig (obj): the istsos configuration object

    Returns:
        properties (list): the list of properties associated to the given offering id
    """
    list=[]
    sql = "SELECT distinct(def_opr)"
    sql += " FROM %s.offerings, %s.off_proc o, %s.procedures," %(sosConfig.schema,sosConfig.schema,sosConfig.schema)
    sql += " %s.proc_obs p, %s.observed_properties" %(sosConfig.schema,sosConfig.schema)
    sql += " WHERE id_off=id_off_fk AND o.id_prc_fk=id_prc AND p.id_prc_fk=id_prc"
    sql += " AND id_opr_fk=id_opr AND id_off=%s" %(id)
    sql += " ORDER BY def_opr"
    params = (id,)
    try:
        rows=pgdb.select(sql,params)
    except:
        raise Exception("sql: %s"%(pgdb.mogrify(sql,params)))
    for row in rows:
        list.append(row["def_opr"])
    return list

def BuildOffFoiList(pgdb,id,sosConfig):
    """Generate the list of feture of interest for a given offering

    Args:
        pgdb (obj): the database object *istsoslib.sosDatabase.PgDB*
        id (int): the offering id
        sosCOnfig (obj): the istsos configuration object

    Returns:
        fois (list): the list of feture of interest associated to the given offering id
    """
    list=[]

    sql = "SELECT distinct(name_fty || ':' || name_foi) as fois"

    sql += " FROM %s.off_proc, %s.procedures,%s.foi,%s.feature_type"  %(sosConfig.schema,sosConfig.schema,sosConfig.schema,sosConfig.schema)
    sql += " WHERE id_prc_fk=id_prc AND id_off_fk=%s"
    sql += " AND id_foi_fk=id_foi AND id_fty_fk=id_fty"
    sql += " ORDER BY fois"
    params = (id,)
    try:
        rows=pgdb.select(sql,params)
    except:
        raise Exception("sql: %s" %(pgdb.mogrify(sql,params)))
    for row in rows:
        if row["fois"]:
            list.append(sosConfig.urn["feature"] + escape(row["fois"]))
    return list

def BuildSensorList(pgdb,sosConfig):
    """Generate the list of sensors

    Args:
        pgdb (obj): the database object *istsoslib.sosDatabase.PgDB*
        sosCOnfig (obj): the istsos configuration object

    Returns:
        sensors (list): the list of sensors
    """
    sql = "SELECT assignedid_prc as id from %s.procedures" %(sosConfig.schema)
    try:
        rows=pgdb.select(sql)
    except:
        raise Exception("sql: %s" %(pgdb.mogrify(sql)))
    return [ sosConfig.urn["sensor"]+str(sid["id"]) for sid in rows ]

class OperationsMetadata:
    """The GetCapabilities Metadata section object

    Attributes:
        OP (list): list of offered requests

            .. note::
                Each request is a list of operation objects (*istsoslib.responders.GCresponse.Operation*) with specific parameters
    """
    def __init__(self,pgdb,sosConfig):
        self.OP=[]
        srslist=[sosConfig.urn["refsystem"]+i for i in sosConfig.parameters["GO_srs"]]

        """ GetCapabilities """
        GetCapabilities=Operation(name="GetCapabilities",get=sosConfig.serviceUrl["get"],post=sosConfig.serviceUrl["post"])
        GetCapabilities.addParameter(name="service",use = "required",allowedValues=sosConfig.parameters["service"])
        GetCapabilities.addParameter(name="acceptversions", use = "required", allowedValues=sosConfig.parameters["version"])
        GetCapabilities.addParameter(name="section",use = "optional",allowedValues=sosConfig.parameters["GC_Section"])
        self.OP.append(GetCapabilities)

        #DescribeSensor
        DescribeSensor=Operation(name="DescribeSensor",get=sosConfig.serviceUrl["get"],post=sosConfig.serviceUrl["post"])
        DescribeSensor.addParameter(name="service",use = "required",allowedValues=sosConfig.parameters["service"])
        DescribeSensor.addParameter(name="version",use = "required",allowedValues=sosConfig.parameters["version"])
        DescribeSensor.addParameter(name="procedure",use = "required",allowedValues=BuildSensorIdList(pgdb,sosConfig))
        DescribeSensor.addParameter(name="outputFormat",use = "required",allowedValues=sosConfig.parameters["DS_outputFormats"])
        self.OP.append(DescribeSensor)

        #GetObservation
        GetObservation=Operation(name="GetObservation",get=sosConfig.serviceUrl["get"],post=sosConfig.serviceUrl["post"])
        GetObservation.addParameter(name="service",use = "required",allowedValues=sosConfig.parameters["service"])
        GetObservation.addParameter(name="version",use = "required",allowedValues=sosConfig.parameters["version"])
        GetObservation.addParameter(name="srsName",use = "optional",allowedValues=srslist)
        GetObservation.addParameter(name="offering",use = "required",allowedValues=BuildOfferingList(pgdb,sosConfig))
        GetObservation.addParameter(name="eventTime",use = "optional",allowedValues=[],range=BuildEventTimeRange(pgdb,sosConfig))
        GetObservation.addParameter(name="procedure",use = "optional",allowedValues=BuildSensorIdList(pgdb,sosConfig))
        GetObservation.addParameter(name="observedProperty",use = "optional",allowedValues=BuildobservedPropertyList(pgdb,sosConfig))
        GetObservation.addParameter(name="featureOfInterest",use = "optional",allowedValues=BuildfeatureOfInterestList(pgdb,sosConfig))

        #GetObservation.addParameter(name="result",use = "optional",allowedValues=[sosConfig.parameters["result"]])
        GetObservation.addParameter(name="responseFormat",use = "required",allowedValues=sosConfig.parameters["GO_responseFormat"])
        GetObservation.addParameter(name="resultModel",use = "optional",allowedValues=sosConfig.parameters["GO_resultModel"])
        GetObservation.addParameter(name="responseMode",use = "optional",allowedValues=sosConfig.parameters["GO_responseMode"])
        self.OP.append(GetObservation)

        #GetFeatureOfInterest
        GetFeatureOfInterest=Operation(name="GetFeatureOfInterest",get=sosConfig.serviceUrl["get"],post=sosConfig.serviceUrl["post"])
        GetFeatureOfInterest.addParameter(name="service",use = "required",allowedValues=sosConfig.parameters["service"])
        GetFeatureOfInterest.addParameter(name="version",use = "required",allowedValues=sosConfig.parameters["version"])
        GetFeatureOfInterest.addParameter(name="featureOfInterest",use = "required",allowedValues=BuildfeatureOfInterestList(pgdb,sosConfig))
        GetFeatureOfInterest.addParameter(name="srsName",use = "optional",allowedValues=srslist)
        self.OP.append(GetFeatureOfInterest)

        #RegisterSensor
        RegisterSensor=Operation(name="RegisterSensor",get=None,post=sosConfig.serviceUrl["post"])
        RegisterSensor.addParameter(name="service",use = "required",allowedValues=sosConfig.parameters["service"])
        RegisterSensor.addParameter(name="version",use = "required",allowedValues=sosConfig.parameters["version"])
        RegisterSensor.addParameter(name="SensorDescription",use = "required",allowedValues=["Any SensorML"])
        RegisterSensor.addParameter(name="ObservationTemplate",use = "required",allowedValues=["Any om:Observation"])
        self.OP.append(RegisterSensor)

        #--InsertObservation
        InsertObservation=Operation(name="InsertObservation",get=None,post=sosConfig.serviceUrl["post"])
        InsertObservation.addParameter(name="service",use = "required",allowedValues=sosConfig.parameters["service"])
        InsertObservation.addParameter(name="version",use = "required",allowedValues=sosConfig.parameters["version"])
        InsertObservation.addParameter(name="AssignedSensorId",use = "required",allowedValues=["Any registered sensorID"])
        InsertObservation.addParameter(name="Observation",use = "optional",allowedValues=["Any om:Observation"])
        self.OP.append(InsertObservation)

        """ optional parameters are:
        result ogc:comparisonOps Zero or one (Optional)
        responseFormat (e.g.: text/xml;schema="ioos/0.6.1" TML, O&M, native format, or MPEG stream out-of-band). (MIME content type) One (mandatory)
        resultModel QName Zero or one (Optional)
        responseMode (inline, out-of-band, attached, resultTemplate) Zero or one (Optional)
        """

class OperationsMetadata_2_0_0:
    """The GetCapabilities Metadata section object for SOS 2.0.0

    Attributes:
        OP (list): list of offered requests

            .. note::
                Each request is a list of operation objects (*istsoslib.responders.GCresponse.Operation*) with specific parameters
    """
    def __init__(self,pgdb,sosConfig):
        self.OP=[]

        # GetCapabilities
        GetCapabilities=Operation(name="GetCapabilities", get=sosConfig.serviceUrl["get"])
        GetCapabilities.addParameter(name="acceptformats", use = "optional", allowedValues=['application/xml']) 
        GetCapabilities.addParameter(name="acceptversions", use = "required", allowedValues=sosConfig.parameters["version"])
        GetCapabilities.addParameter(name="sections", use = "optional", allowedValues=sosConfig.parameters["GC_Section_2_0_0"])
        self.OP.append(GetCapabilities)
        
        # DescribeSensor
        DescribeSensor = Operation(name="DescribeSensor", get=sosConfig.serviceUrl["get"])
        DescribeSensor.addParameter(name="procedure", use = "required", allowedValues=BuildSensorIdList(pgdb,sosConfig))
        DescribeSensor.addParameter(name="procedureDescriptionFormat", use = "required", allowedValues=sosConfig.parameters["DS_outputFormats_2_0_0"])
        self.OP.append(DescribeSensor)
        
        # GetObservation
        GetObservation=Operation(name="GetObservation", get = sosConfig.serviceUrl["get"])
        GetObservation.addParameter(name="offering", use = "required", allowedValues = BuildOfferingList_2_0_0(pgdb,sosConfig))
        GetObservation.addParameter(name="temporalFilter", use = "optional", allowedValues = [], range=BuildEventTimeRange(pgdb,sosConfig))
        GetObservation.addParameter(name="spatialFilter", use = "optional", allowedValues = [], range=BuildEnvelopeMinMax(pgdb,sosConfig), referenceSystem="http://www.opengis.net/def/crs/EPSG/0/"+sosConfig.istsosepsg)
        GetObservation.addParameter(name="procedure", use = "optional", allowedValues = BuildSensorIdList(pgdb,sosConfig))
        GetObservation.addParameter(name="observedProperty", use = "optional", allowedValues = BuildobservedPropertyList(pgdb,sosConfig))
        GetObservation.addParameter(name="featureOfInterest", use = "optional", allowedValues = BuildfeatureOfInterestList(pgdb,sosConfig))
        GetObservation.addParameter(name="responseFormat", use = "required", allowedValues = sosConfig.parameters["GO_responseFormat_2_0_0"])
        self.OP.append(GetObservation)
        
        # GlobalOperations (GLOBAL PARAMETERS VAALID FOR ALL REQUESTS)
        GlobalOperations = Operation(name="GlobalOperations", get=sosConfig.serviceUrl["get"])
        GlobalOperations.addParameter(name="service", use = "required", allowedValues=sosConfig.parameters["service"])
        GlobalOperations.addParameter(name="version", use = "required", allowedValues=sosConfig.parameters["version"])
        GlobalOperations.addParameter(name="crs", use = "optional", allowedValues=[sosConfig.urn["refsystem"]+i for i in sosConfig.parameters["GO_srs"]])
        self.OP.append(GlobalOperations)


class Offering:
    """The Offering object

    Attributes:
        id (str): offering id
        name (str): offering name
        desc (str): offering description
        boundedBy (str): offering bounding box
        beginPosition (str): offering starting time of observation
        endPosition (str): offering end time of observation
        procedures (list): procedures list
        obsProp (list): observed properties list
        fois (list): feature of interest list
    """
    def __init__(self):
        self.id = None
        self.name = None
        self.desc = None
        self.boundedBy = None
        self.beginPosition = None
        self.endPosition = None
        self.procedures=[]
        self.obsProp=[]
        self.fois=[]
        

class Offering_2_0_0:
    """The Offering object for SOS 2.0.0

    Attributes:
        id (str): offering id
        name (str): offering name
        desc (str): offering description
        boundedBy (str): offering bounding box
        beginPosition (str): offering starting time of observation
        endPosition (str): offering end time of observation
        procedures (list): procedures list
        obsProp (list): observed properties list
        fois (list): feature of interest list
    """
    def __init__(self):
        self.id = None
        self.description = None
        self.identifier = None
        self.procedure = None
        self.observedArea = None
        self.beginPosition = None
        self.endPosition = None
        self.observableProperties=[]
        self.systemType=None
        self.featurename=None
        self.lowerX = None
        self.lowerY = None
        self.upperX = None
        self.upperY = None

class ObservationOfferingList:
    """Observation offering list object

    Attributes:
        offerings (list): list of offerings objects (*istsoslib.responders.GCresponse.Offering*)
        responseFormat (str): response format
        resultModel (str): result model
        responseMode (str): response mode

    """
    #def __init__(self,filter, pgdb):
    def __init__(self, pgdb, sosConfig):
        self.offerings=[]
        self.responseFormat = sosConfig.parameters["GO_responseFormat"]
        self.resultModel = sosConfig.parameters["GO_resultModel"]
        self.responseMode = sosConfig.parameters["GO_responseMode"]

        #get offering list
        sql = "SELECT id_off,name_off,desc_off from %s.offerings where active_off != false ORDER BY name_off" %(sosConfig.schema)
        rows=pgdb.select(sql)
        for row in rows:
            off = Offering()
            off.id = row["name_off"]
            off.name = sosConfig.urn["offering"] + row["name_off"]
            off.desc = row["desc_off"]
            off.boundedBy = BuildOffEnvelope(pgdb,row["id_off"],sosConfig)
            timelag = BuildOffTimePeriod(pgdb,row["id_off"],sosConfig)
            off.beginPosition = timelag[0]
            off.endPosition = timelag[1]
            off.procedures = BuildOffProcList(pgdb,row["id_off"],sosConfig)
            off.obsProp = BuildOffObsPrList(pgdb,row["id_off"],sosConfig)
            off.fois = BuildOffFoiList(pgdb,row["id_off"],sosConfig)
            self.offerings.append(off)
            

class ObservationOfferingList_2_0_0:
    """Observation offering list object

    Attributes:
        offerings (list): list of offerings objects (*istsoslib.responders.GCresponse.Offering*)
        responseFormat (str): response format
        resultModel (str): result model
        responseMode (str): response mode

    """
    #def __init__(self,filter, pgdb):
    def __init__(self, pgdb, sosConfig):
        self.offerings=[]
        self.responseFormat = sosConfig.parameters["GO_responseFormat"]
        self.resultModel = sosConfig.parameters["GO_resultModel"]
        self.responseMode = sosConfig.parameters["GO_responseMode"]        
        
        sql = """
            SELECT 
              procedures.id_prc, 
              procedures.assignedid_prc, 
              procedures.name_prc, 
              procedures.desc_prc, 
              procedures.stime_prc, 
              procedures.etime_prc, 
              procedures.time_res_prc, 
              procedures.time_acq_prc, 
              foi.id_foi, 
              foi.name_foi, 
              foi.geom_foi, 
              feature_type.name_fty, 
              obs_type.name_oty
            FROM 
              %s.procedures, 
              %s.foi, 
              %s.feature_type,
              %s.obs_type
            WHERE 
              procedures.id_foi_fk = foi.id_foi 
            AND 
              feature_type.id_fty = foi.id_fty_fk
            AND 
              obs_type.id_oty = procedures.id_oty_fk
            ORDER BY name_prc;
            
        """ % (
            (sosConfig.schema,)*4)
        rows=pgdb.select(sql)
        
        for row in rows:
            off = Offering_2_0_0()
            self.offerings.append(off)
            
            off.description = row["desc_prc"]
            off.identifier = sosConfig.urn["offering"] + row["name_prc"]
            off.procedure = sosConfig.urn["procedure"] + row["name_prc"]
            
            off.systemType = row["name_oty"]
            
            #print >> sys.stderr, "systemType: %s" % off.systemType
            if off.systemType == 'virtual':
                
                vpFolder = os.path.join(sosConfig.virtual_processes_folder, off.identifier)
                try:
                    sys.path.append(vpFolder)
                    
                except:
                    raise Exception("Error in loading virtual procedure path")
                    
                # check if python file exist
                if os.path.isfile("%s/%s.py" % (vpFolder, off.identifier)):
                    
                    #import procedure process
                    # exec("import %s as vproc" % off.procedure)
                    vproc = importlib.import_module(off.procedure)
                    
                    # Initialization of virtual procedure will load the source data
                    vp = vproc.istvp()
                    vp._configure(
                        DS_filter.get_fake_ds(off.procedure, sosConfig), pgdb
                    )
                    off.beginPosition, off.endPosition = vp.getSampligTime()
                    
                else:
                    off.beginPosition = off.endPosition = None
                    
            else:
                off.beginPosition = row["stime_prc"]
                off.endPosition = row["etime_prc"]
                
            off.featurename = row["name_foi"]
            off.id = row["id_prc"]
            
            # Calculating the observedArea
            if off.systemType == 'insitu-mobile-point':
                sql = """
                    SELECT 
                      st_XMax(envelope) as max,
                      st_YMax(envelope) as may,
                      st_XMin(envelope) as mix,
                      st_YMin(envelope) as miy
                    from (
                    	select 
                          ST_ENVELOPE(ST_Collect(ST_Transform(geom_pos,%s))) as envelope 
                      FROM 
                          %s.positions, %s.event_time, %s.procedures
                      WHERE 
                          id_prc = id_prc_fk
                      AND
                          id_eti = id_eti_fk
                      AND
                          id_prc = %s
                    ) as s
                """ % (
                    sosConfig.istsosepsg, sosConfig.schema, sosConfig.schema, 
                    sosConfig.schema, off.id
                )
                res = pgdb.select(sql)
                if len(res) == 1:
                    off.lowerX = res[0]['mix']
                    off.lowerY = res[0]['miy']
                    off.upperX = res[0]['max']
                    off.upperY = res[0]['may']
                
            else:
                sql = """
                    SELECT 
                        st_x(ST_Transform(geom_foi,%s)) as x, 
                        st_y(ST_Transform(geom_foi,%s)) as y 
                    FROM %s.foi
                    WHERE id_foi = %s;
                """ % (
                    sosConfig.istsosepsg, sosConfig.istsosepsg, sosConfig.schema, row["id_foi"])
                res = pgdb.select(sql)
                if len(res) == 1:
                    off.lowerX = off.upperX = res[0]['x']
                    off.lowerY = off.upperY = res[0]['y']
            
            # Loading observableProperties
            sql = """
                SELECT 
                  observed_properties.name_opr, 
                  observed_properties.def_opr, 
                  observed_properties.desc_opr, 
                  observed_properties.constr_opr, 
                  uoms.name_uom, 
                  uoms.desc_uom 
                FROM 
                  %s.observed_properties, 
                  %s.proc_obs, 
                  %s.uoms 
                WHERE 
                  proc_obs.id_opr_fk = observed_properties.id_opr 
                AND 
                  proc_obs.id_uom_fk = uoms.id_uom 
                AND 
                  id_prc_fk = %s;
            """ % (
                sosConfig.schema, sosConfig.schema, sosConfig.schema, off.id)
            
            res = pgdb.select(sql)
            
            for obs in res:
                off.observableProperties.append({
                    'definition': obs['def_opr'],
                    'description': obs['desc_opr'],
                    'constraint': obs['constr_opr'],
                    'name': obs['name_opr'],
                    'uom': obs['name_uom'],
                    'uom_name': obs['desc_uom']
                })
            


class GetCapabilitiesResponse():
    """The GetCapabilitiesResponse object

    Attributes:
        ServiceIdentifier (list): list of ServiceIdentifier objects (*istsoslib.responders.GCresponse.ServiceIdentifier*)
        ServiceProvider (list): list of ServiceProvider objects (*istsoslib.responders.GCresponse.ServiceProvider*)
        OperationsMetadata (list): list of OperationsMetadata objects (*istsoslib.responders.GCresponse.OperationsMetadata*)
        ObservationOfferingList (list): list of ObservationOfferingList objects (*istsoslib.responders.GCresponse.ObservationOfferingList*)

        .. note::
            Attributes may vary depending of sections argument values
    """
    def __init__(self,fil,pgdb):
        
        self.version = fil.version


        if "all" in fil.sections:

            if self.version == '2.0.0':
                self.ObservationOfferingList = ObservationOfferingList_2_0_0(pgdb,fil.sosConfig)
                
            else:
                self.ObservationOfferingList = ObservationOfferingList(pgdb,fil.sosConfig)
                
            self.ServiceIdentifier = ServiceIdentification(fil.sosConfig)
            self.ServiceIdentifier.serviceTypeVersion = fil.version
            self.ServiceProvider = ServiceProvider(fil.sosConfig)
            if self.version == '2.0.0':
                self.OperationsMetadata = OperationsMetadata_2_0_0(pgdb,fil.sosConfig)
                
            else:
                self.OperationsMetadata = OperationsMetadata(pgdb,fil.sosConfig)
            self.FilterCapabilities = True
                
        else:

            if "contents" in fil.sections:
                if self.version == '2.0.0':
                    self.ObservationOfferingList = ObservationOfferingList_2_0_0(pgdb,fil.sosConfig)
                    
                else:
                    self.ObservationOfferingList = ObservationOfferingList(pgdb,fil.sosConfig)
            else:
                self.ObservationOfferingList = []
                    
            if "serviceidentification" in fil.sections:
                self.ServiceIdentifier = ServiceIdentification(fil.sosConfig)
                self.ServiceIdentifier.serviceTypeVersion = fil.version
                
            else:
                self.ServiceIdentifier = []
                
            if "serviceprovider" in fil.sections:
                self.ServiceProvider = ServiceProvider(fil.sosConfig)
                
            else:
                self.ServiceProvider = []
                
            if "operationsmetadata" in fil.sections:
                if self.version == '2.0.0':
                    self.OperationsMetadata = OperationsMetadata_2_0_0(pgdb,fil.sosConfig)
                    
                else:
                    self.OperationsMetadata = OperationsMetadata(pgdb,fil.sosConfig)
                
            else:
                self.OperationsMetadata = []

            if "filtercapabilities" in fil.sections:
                self.FilterCapabilities = True
                
            else:
                self.FilterCapabilities = False



