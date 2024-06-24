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
import sys
import isodate as iso

from ..utils import escape

def render(GC,sosConfig):
    r = '''<?xml version="1.0" encoding="UTF-8"?>
    <Capabilities
      xmlns:gml="http://www.opengis.net/gml"
      xmlns:xlink="http://www.w3.org/1999/xlink"
      xmlns:swe="http://www.opengis.net/swe/1.0.1"
      xmlns:om="http://www.opengis.net/om/1.0"
      xmlns="http://www.opengis.net/sos/1.0"
      xmlns:sos="http://www.opengis.net/sos/1.0"
      xmlns:ows="http://www.opengis.net/ows/1.1"
      xmlns:ogc="http://www.opengis.net/ogc"
      xmlns:tml="http://www.opengis.net/tml"
      xmlns:sml="http://www.opengis.net/sensorML/1.0.1"
      xmlns:xsi="http://www.w3.org/2001/XMLSchema-instance"
      xsi:schemaLocation="http://www.opengis.net/sos/1.0 http://schemas.opengis.net/sos/1.0.0/sosGetCapabilities.xsd"
      version="1.0.0">\n'''
    
    if not GC.ServiceIdentifier==[]:
        '''r += "  <!--~~~~~~~~~~~~~~~~~~~~~~~~-->\n"
        r += "  <!-- Service Identification -->\n"
        r += "  <!--~~~~~~~~~~~~~~~~~~~~~~~~-->\n"'''
        r += "  <ows:ServiceIdentification>\n"
        r += "    <ows:Title>" + GC.ServiceIdentifier.title  + "</ows:Title>\n"
        r += "    <ows:Abstract>" + GC.ServiceIdentifier.abstract +"</ows:Abstract>\n"
        r += "    <ows:Keywords>\n"
        for k in GC.ServiceIdentifier.keywords:
            r += "      <ows:Keyword>"+ k +"</ows:Keyword>\n"
        r += "    </ows:Keywords>\n"
        r += "    <ows:ServiceType codeSpace=\"" + GC.ServiceIdentifier.serviceTypeCode + "\">"
        r +=  GC.ServiceIdentifier.serviceTypeValue + "</ows:ServiceType>\n"
        r += "    <ows:ServiceTypeVersion>" + GC.ServiceIdentifier.serviceTypeVersion + "</ows:ServiceTypeVersion>\n"
        r += "    <ows:Fees>" + GC.ServiceIdentifier.fees + "</ows:Fees>\n"
        r += "    <ows:AccessConstraints>" + GC.ServiceIdentifier.accessconstrains + "</ows:AccessConstraints>\n"
        r += "  </ows:ServiceIdentification>\n"

    if not GC.ServiceProvider==[]:
        '''r += "  <!--~~~~~~~~~~~~~~~~~~~~~~-->\n"
        r += "  <!-- Provider Description -->\n"
        r += "  <!--~~~~~~~~~~~~~~~~~~~~~~-->\n"'''
        r += "  <ows:ServiceProvider>\n"
        r += "    <ows:ProviderName>" + GC.ServiceProvider.providerName + "</ows:ProviderName>\n"
        r += "    <ows:ProviderSite xlink:href=\"" + GC.ServiceProvider.providerSite + "\"/>\n"
        r += "    <ows:ServiceContact>\n"
        r += "      <ows:IndividualName>" + GC.ServiceProvider.individualName + "</ows:IndividualName>\n"
        r += "      <ows:PositionName>" + GC.ServiceProvider.positionName + "</ows:PositionName>\n"
        r += "      <ows:ContactInfo>\n"
        r += "        <ows:Phone>\n"
        r += "          <ows:Voice>" + GC.ServiceProvider.contactVoice + "</ows:Voice>\n"
        r += "          <ows:Facsimile>" + GC.ServiceProvider.contactFax + "</ows:Facsimile>\n"
        r += "        </ows:Phone>\n"
        r += "        <ows:Address>\n"
        r += "          <ows:DeliveryPoint>" + GC.ServiceProvider.contactDelivery + "</ows:DeliveryPoint>\n"
        r += "          <ows:City>" + GC.ServiceProvider.contactCity + "</ows:City>\n"
        r += "          <ows:AdministrativeArea>" + GC.ServiceProvider.contactArea + "</ows:AdministrativeArea>\n"
        r += "          <ows:PostalCode>" + GC.ServiceProvider.contactPostCode + "</ows:PostalCode>\n"
        r += "          <ows:Country>" + GC.ServiceProvider.contactCountry + "</ows:Country>\n"
        r += "          <ows:ElectronicMailAddress>" + GC.ServiceProvider.contactMail + "</ows:ElectronicMailAddress>\n"        
        r += "        </ows:Address>\n"
        r += "      </ows:ContactInfo>\n"
        r += "    </ows:ServiceContact>\n"
        r += "  </ows:ServiceProvider>\n"

    if GC.OperationsMetadata:
        r += "  <ows:OperationsMetadata>\n"
        for o in GC.OperationsMetadata.OP:
            r += "    <ows:Operation name=\"" + o.name + "\">\n"
            r += "      <ows:DCP>\n"
            r += "        <ows:HTTP>\n"
            if o.get:
                r += "          <ows:Get xlink:href=\"" + o.get + "\"/>\n"
            if o.post:
                r += "          <ows:Post xlink:href=\"" + o.post + "\"/>\n"
            r += "        </ows:HTTP>\n"
            r += "      </ows:DCP>\n"
            for p in o.parameters:
                # r += "    <ows:Parameter name=\"" + p.name + "\" use=\"" + p.use + "\">\n"
                r += "    <ows:Parameter name=\"" + p.name + "\">\n"
                r += "      <ows:AllowedValues>\n"
                if len(p.allowedValues)>0:
                    for a in p.allowedValues:
                        r += "        <ows:Value>" + escape(a) + "</ows:Value>\n"
                if len(p.range)>0:
                    r += "        <ows:Range>\n"
                    r += "          <ows:MinimumValue>"  
                    if str(type(p.range[0]))== "<type 'datetime.datetime'>":
                        r += iso.datetime_isoformat(p.range[0])
                    else:
                        r += str(p.range[0])
                    r += "</ows:MinimumValue>\n"
                    r += "          <ows:MaximumValue>"
                    if str(type(p.range[1]))== "<type 'datetime.datetime'>":
                        r += iso.datetime_isoformat(p.range[1])
                    else:
                        r += str(p.range[1])
                    r += "</ows:MaximumValue>\n"
                    r += "        </ows:Range>\n"
                r += "      </ows:AllowedValues>\n"
                r += "    </ows:Parameter>\n"
            r += "    </ows:Operation>\n"
        r += "  </ows:OperationsMetadata>\n"
        
    if not GC.ObservationOfferingList==[]:
        r += "  <Contents>\n"
        r += "    <ObservationOfferingList>\n"
        for ofl in GC.ObservationOfferingList.offerings:
            r += "      <ObservationOffering gml:id=\"" + str(ofl.id) + "\">\n"
            r += "        <gml:description>" + ofl.desc + "</gml:description>\n"
            r += "        <gml:name>" + ofl.name + "</gml:name>\n"

            if ofl.boundedBy:
                r += "        <gml:boundedBy>\n"
                r += "          <gml:Envelope>\n"
                r += "            " + str(ofl.boundedBy) + "\n"
                r += "          </gml:Envelope>\n"
                r += "        </gml:boundedBy>\n"

            
            if ofl.beginPosition and ofl.endPosition :
                r += "        <time>\n"
                r += "          <gml:TimePeriod>\n"
                r += "            <gml:beginPosition>" + iso.datetime_isoformat(ofl.beginPosition) + "</gml:beginPosition>\n"
                r += "            <gml:endPosition>" + iso.datetime_isoformat(ofl.endPosition) + "</gml:endPosition>\n"
                r += "          </gml:TimePeriod>\n"
                r += "        </time>\n"
            else:
                r += "        <sos:time />\n"
                
            for pr in ofl.procedures:
                r += "        <sos:procedure xlink:href=\"" + sosConfig.urn["procedure"] + pr + "\" />\n"
            
            for op in ofl.obsProp:
                r += "        <sos:observedProperty xlink:href=\"" + op + "\" />\n"
            
            for fo in ofl.fois:
                r += "        <sos:featureOfInterest xlink:href=\"" + fo + "\" />\n"
            
            
            for ef in GC.ObservationOfferingList.responseFormat:
                r += "        <sos:responseFormat>" + ef + "</sos:responseFormat>\n"
                
            for rmd in GC.ObservationOfferingList.resultModel:
                r += "        <sos:resultModel>" + rmd + "</sos:resultModel>\n"
                
            for rm in GC.ObservationOfferingList.responseMode:
                r += "        <sos:responseMode>" + rm + "</sos:responseMode>\n"

            r += "        </ObservationOffering>\n"
        
        r += "      </ObservationOfferingList>\n"
        r += "      </Contents>\n"
    r += "    </Capabilities>"
    return r.encode()
    

def render_2_0_0(GC,sosConfig):
    r = '''<?xml version="1.0" encoding="UTF-8"?>
    <sos:Capabilities
      xsi:schemaLocation="http://www.opengis.net/sos/2.0 http://schemas.opengis.net/sos/2.0/sos.xsd" 
      xmlns:xsi="http://www.w3.org/2001/XMLSchema-instance" 
      xmlns:wsa="http://www.w3.org/2005/08/addressing" 
      xmlns:swe="http://www.opengis.net/swe/2.0" 
      xmlns:swes="http://www.opengis.net/swes/2.0" 
      xmlns:ows="http://www.opengis.net/ows/1.1" 
      xmlns:sos="http://www.opengis.net/sos/2.0" 
      xmlns:fes="http://www.opengis.net/fes/2.0" 
      xmlns:gml="http://www.opengis.net/gml/3.2" 
      xmlns:ogc="http://www.opengis.net/ogc" 
      xmlns:xlink="http://www.w3.org/1999/xlink"
      version="2.0.0">\n'''
    
    if not GC.ServiceIdentifier==[]:
        r += "  <ows:ServiceIdentification>\n"
        r += "    <ows:Title>" + GC.ServiceIdentifier.title  + "</ows:Title>\n"
        r += "    <ows:Abstract>" + GC.ServiceIdentifier.abstract +"</ows:Abstract>\n"
        r += "    <ows:Keywords>\n"
        for k in GC.ServiceIdentifier.keywords:
            r += "      <ows:Keyword>"+ k +"</ows:Keyword>\n"
        r += "    </ows:Keywords>\n"
        r += "    <ows:ServiceType codeSpace=\"http://opengeospatial.net\">OGC:SOS</ows:ServiceType>\n"
        r += "    <ows:ServiceTypeVersion>2.0.0</ows:ServiceTypeVersion>\n"
        r += "    <ows:Profile>http://www.opengis.net/spec/OMXML/2.0/conf/observation</ows:Profile>\n"
        r += "    <ows:Profile>http://www.opengis.net/spec/OMXML/2.0/conf/geometryObservation</ows:Profile>\n"
        r += "    <ows:Profile>http://www.opengis.net/spec/OMXML/2.0/conf/samplingPoint</ows:Profile>\n"
        #r += "    <ows:Profile>http://www.opengis.net/spec/OMXML/2.0/conf/specimen</ows:Profile>\n"
        #r += "    <ows:Profile>http://www.opengis.net/spec/OMXML/2.0/req/SWEArrayObservation</ows:Profile>\n"
        r += "    <ows:Profile>http://www.opengis.net/spec/SOS/1.0/conf/core</ows:Profile>\n"
        r += "    <ows:Profile>http://www.opengis.net/spec/SOS/1.0/conf/enhanced</ows:Profile>\n"
        r += "    <ows:Profile>http://www.opengis.net/spec/SOS/2.0/conf/core</ows:Profile>\n"
        r += "    <ows:Profile>http://www.opengis.net/spec/SOS/2.0/conf/kvp-core</ows:Profile>\n"
        r += "    <ows:Profile>http://www.opengis.net/spec/SOS/2.0/conf/spatialFilteringProfile</ows:Profile>\n"
        r += "    <ows:Fees>" + GC.ServiceIdentifier.fees + "</ows:Fees>\n"
        r += "    <ows:AccessConstraints>" + GC.ServiceIdentifier.accessconstrains + "</ows:AccessConstraints>\n"
        r += "  </ows:ServiceIdentification>\n"

    if not GC.ServiceProvider==[]:
        '''r += "  <!--~~~~~~~~~~~~~~~~~~~~~~-->\n"
        r += "  <!-- Provider Description -->\n"
        r += "  <!--~~~~~~~~~~~~~~~~~~~~~~-->\n"'''
        r += "  <ows:ServiceProvider>\n"
        r += "    <ows:ProviderName>" + GC.ServiceProvider.providerName + "</ows:ProviderName>\n"
        r += "    <ows:ProviderSite xlink:href=\"" + GC.ServiceProvider.providerSite + "\"/>\n"
        r += "    <ows:ServiceContact>\n"
        r += "      <ows:IndividualName>" + GC.ServiceProvider.individualName + "</ows:IndividualName>\n"
        r += "      <ows:PositionName>" + GC.ServiceProvider.positionName + "</ows:PositionName>\n"
        r += "      <ows:ContactInfo>\n"
        r += "        <ows:Phone>\n"
        r += "          <ows:Voice>" + GC.ServiceProvider.contactVoice + "</ows:Voice>\n"
        r += "          <ows:Facsimile>" + GC.ServiceProvider.contactFax + "</ows:Facsimile>\n"
        r += "        </ows:Phone>\n"
        r += "        <ows:Address>\n"
        r += "          <ows:DeliveryPoint>" + GC.ServiceProvider.contactDelivery + "</ows:DeliveryPoint>\n"
        r += "          <ows:City>" + GC.ServiceProvider.contactCity + "</ows:City>\n"
        r += "          <ows:AdministrativeArea>" + GC.ServiceProvider.contactArea + "</ows:AdministrativeArea>\n"
        r += "          <ows:PostalCode>" + GC.ServiceProvider.contactPostCode + "</ows:PostalCode>\n"
        r += "          <ows:Country>" + GC.ServiceProvider.contactCountry + "</ows:Country>\n"
        r += "          <ows:ElectronicMailAddress>" + GC.ServiceProvider.contactMail + "</ows:ElectronicMailAddress>\n"        
        r += "        </ows:Address>\n"
        r += "      </ows:ContactInfo>\n"
        r += "      <ows:Role/>\n"
        r += "    </ows:ServiceContact>\n"
        r += "  </ows:ServiceProvider>\n"
        
    
    if GC.OperationsMetadata:
        r += "  <ows:OperationsMetadata>\n"
        for o in GC.OperationsMetadata.OP:
            if o.name != 'GlobalOperations':
                r += "    <ows:Operation name=\"" + o.name + "\">\n"
                r += "      <ows:DCP>\n"
                r += "        <ows:HTTP>\n"
                if o.get:
                    r += "          <ows:Get xlink:href=\"" + o.get + "\">\n"
                    r += "            <ows:Constraint name=\"Content-Type\">\n"
                    r += "              <ows:AllowedValues>\n"
                    r += "                <ows:Value>application/x-kvp</ows:Value>\n"
                    r += "              </ows:AllowedValues>\n"
                    r += "            </ows:Constraint>\n"
                    r += "          </ows:Get>\n"
                    
                r += "        </ows:HTTP>\n"
                r += "      </ows:DCP>\n"
                
            for p in o.parameters:
                r += "    <ows:Parameter name=\"" + p.name + "\">\n"
                r += "      <ows:AllowedValues>\n"
                if len(p.allowedValues)>0:
                    for a in p.allowedValues:
                        r += "        <ows:Value>" + str(a) + "</ows:Value>\n"
                        
                if len(p.range)>0:
                    r += "        <ows:Range>\n"
                    r += "          <ows:MinimumValue>"  
                    if str(type(p.range[0]))== "<type 'datetime.datetime'>":
                        r += iso.datetime_isoformat(p.range[0])
                        
                    else:
                        r += str(p.range[0])
                        
                    r += "</ows:MinimumValue>\n"
                    r += "          <ows:MaximumValue>"
                    if str(type(p.range[1]))== "<type 'datetime.datetime'>":
                        r += iso.datetime_isoformat(p.range[1])
                        
                    else:
                        r += str(p.range[1])
                        
                    r += "</ows:MaximumValue>\n"
                    r += "        </ows:Range>\n"
                    
                r += "      </ows:AllowedValues>\n"
                # add ReferenceSystem tag
                if p.referenceSystem:
                    r += "      <ows:ReferenceSystem ows:reference='" + str(p.referenceSystem) + "' />\n"
                r += "    </ows:Parameter>\n"
                
            if o.name != 'GlobalOperations':
                r += "    </ows:Operation>\n"
                
            
            #r += "      <ows:Parameter name=\"validTime\">\n"
            #r += "        <ows:AnyValue/>\n"
            #r += "      </ows:Parameter>\n"
        
        # GLOBAL PARAMETERS VAALID FOR ALL REQUESTS
        
        r += "  </ows:OperationsMetadata>\n"
        
    if GC.FilterCapabilities:
        r += "      <sos:extension/>"
        r += "      <sos:filterCapabilities>"
        r += "          <fes:Filter_Capabilities>"
        r += "            <fes:Conformance>"
        r += "              <fes:Constraint name=\"ImplementsQuery\">"
        r += "                <ows:NoValues/>"
        r += "                <ows:DefaultValue>false</ows:DefaultValue>"
        r += "              </fes:Constraint>"
        r += "              <fes:Constraint name=\"ImplementsAdHocQuery\">"
        r += "                <ows:NoValues/>"
        r += "                <ows:DefaultValue>false</ows:DefaultValue>"
        r += "              </fes:Constraint>"
        r += "              <fes:Constraint name=\"ImplementsFunctions\">"
        r += "                <ows:NoValues/>"
        r += "                <ows:DefaultValue>false</ows:DefaultValue>"
        r += "              </fes:Constraint>"
        r += "              <fes:Constraint name=\"ImplementsMinStandardFilter\">"
        r += "                <ows:NoValues/>"
        r += "                <ows:DefaultValue>false</ows:DefaultValue>"
        r += "              </fes:Constraint>"
        r += "              <fes:Constraint name=\"ImplementsStandardFilter\">"
        r += "                <ows:NoValues/>"
        r += "                <ows:DefaultValue>false</ows:DefaultValue>"
        r += "              </fes:Constraint>"
        r += "              <fes:Constraint name=\"ImplementsMinSpatialFilter\">"
        r += "                <ows:NoValues/>"
        r += "                <ows:DefaultValue>true</ows:DefaultValue>"
        r += "              </fes:Constraint>"
        r += "              <fes:Constraint name=\"ImplementsSpatialFilter\">"
        r += "                <ows:NoValues/>"
        r += "                <ows:DefaultValue>true</ows:DefaultValue>"
        r += "              </fes:Constraint>"
        r += "              <fes:Constraint name=\"ImplementsMinTemporalFilter\">"
        r += "                <ows:NoValues/>"
        r += "                <ows:DefaultValue>true</ows:DefaultValue>"
        r += "              </fes:Constraint>"
        r += "              <fes:Constraint name=\"ImplementsTemporalFilter\">"
        r += "                <ows:NoValues/>"
        r += "                <ows:DefaultValue>true</ows:DefaultValue>"
        r += "              </fes:Constraint>"
        r += "              <fes:Constraint name=\"ImplementsVersionNav\">"
        r += "                <ows:NoValues/>"
        r += "                <ows:DefaultValue>false</ows:DefaultValue>"
        r += "              </fes:Constraint>"
        r += "              <fes:Constraint name=\"ImplementsSorting\">"
        r += "                <ows:NoValues/>"
        r += "                <ows:DefaultValue>false</ows:DefaultValue>"
        r += "              </fes:Constraint>"
        r += "              <fes:Constraint name=\"ImplementsExtendedOperators\">"
        r += "                <ows:NoValues/>"
        r += "                <ows:DefaultValue>false</ows:DefaultValue>"
        r += "              </fes:Constraint>"
        r += "            </fes:Conformance>"
        r += "            <fes:Spatial_Capabilities>"
        r += "              <fes:GeometryOperands>"
        r += "                <fes:GeometryOperand name=\"gml:Point\"/>"
        r += "                <fes:GeometryOperand name=\"gml:Polygon\"/>"
        r += "              </fes:GeometryOperands>"
        r += "              <fes:SpatialOperators>"
        r += "                <fes:SpatialOperator name=\"BBOX\"/>"
        #r += "                <fes:SpatialOperator name=\"Intersects\"/>"
        #r += "                <fes:SpatialOperator name=\"Within\"/>"
        r += "              </fes:SpatialOperators>"
        r += "            </fes:Spatial_Capabilities>"
        r += "            <fes:Temporal_Capabilities>"
        r += "              <fes:TemporalOperands>"
        r += "                <fes:TemporalOperand name=\"gml:TimePeriod\"/>"
        r += "                <fes:TemporalOperand name=\"gml:TimeInstant\"/>"
        r += "              </fes:TemporalOperands>"
        r += "              <fes:TemporalOperators>"
        r += "                <fes:TemporalOperator name=\"During\"/>"
        #r += "                <fes:TemporalOperator name=\"After\"/>"
        r += "                <fes:TemporalOperator name=\"TEquals\"/>"
        r += "              </fes:TemporalOperators>"
        r += "            </fes:Temporal_Capabilities>"
        r += "          </fes:Filter_Capabilities>"
        r += "        </sos:filterCapabilities>"

    if not GC.ObservationOfferingList==[]:
        r += "  <sos:contents>\n"
        r += "    <sos:Contents>\n"
        
        for offering in GC.ObservationOfferingList.offerings:
            r += "      <swes:offering>\n"
            r += "        <sos:ObservationOffering xmlns:ns=\"http://www.opengis.net/sos/2.0\">\n"
            r += "          <swes:description>%s</swes:description>\n" % (offering.description)
            r += "          <swes:identifier>%s</swes:identifier>\n" % (offering.identifier)
            r += "          <swes:procedure>%s</swes:procedure>\n" % (offering.procedure)
            r += "          <swes:procedureDescriptionFormat>http://www.opengis.net/sensorML/1.0.1</swes:procedureDescriptionFormat>\n"
            #r += "          <swes:procedureDescriptionFormat>http://www.opengis.net/waterml/2.0/observationProcess</swes:procedureDescriptionFormat>\n"
            
            for observableProperty in offering.observableProperties:            
                r += "          <swes:observableProperty>%s</swes:observableProperty>\n" % (observableProperty['definition'])
                
            r += "          <sos:observedArea>\n"
            r += "            <gml:Envelope srsName=\"http://www.opengis.net/def/crs/EPSG/0/%s\">\n" % sosConfig.istsosepsg
            r += "              <gml:lowerCorner>%s %s</gml:lowerCorner>\n" % (offering.lowerX ,offering.lowerY )
            r += "              <gml:upperCorner>%s %s</gml:upperCorner>\n" % (offering.upperX ,offering.upperY )
            r += "            </gml:Envelope>\n"
            r += "          </sos:observedArea>\n"
            
            r += "          <sos:phenomenonTime>\n"
            r += "            <gml:TimePeriod gml:id=\"phenomenonTime_%s\">\n" % offering.id
            r += "              <gml:beginPosition>%s</gml:beginPosition>\n" % (iso.datetime_isoformat(offering.beginPosition) if offering.beginPosition!=None else '')
            r += "              <gml:endPosition>%s</gml:endPosition>\n" % (iso.datetime_isoformat(offering.endPosition) if offering.endPosition!=None else '')
            r += "            </gml:TimePeriod>\n"
            r += "          </sos:phenomenonTime>\n"
            
            # This shall be modified to handle specimen
            for rf in sosConfig.parameters['GO_responseFormat_2_0_0']:
                r += "        <sos:responseFormat>" + rf + "</sos:responseFormat>\n"
            r += "          <sos:observationType>http://www.opengis.net/def/observationType/OGC-OM/2.0/OM_Measurement</sos:observationType>  \n"   
            r += "          <sos:featureOfInterestType>http://www.opengis.net/def/samplingFeatureType/OGC-OM/2.0/SF_SamplingPoint</sos:featureOfInterestType>\n"
            r += "        </sos:ObservationOffering>\n"
            r += "      </swes:offering>\n"
        
        r += "      </sos:Contents>\n"
        r += "    </sos:contents>\n" 
        
    r += "    </sos:Capabilities>"
    return r.encode()
