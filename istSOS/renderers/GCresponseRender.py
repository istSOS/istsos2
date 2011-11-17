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

import isodate as iso

def render(GC):
    r = "<?xml version=\"1.0\" encoding=\"UTF-8\"?>\n"
    r += "<Capabilities\n"
    r += "  xmlns:gml=\"http://www.opengis.net/gml\"\n" 
    r += "  xmlns:xlink=\"http://www.w3.org/1999/xlink\"\n"
    r += "  xmlns:swe=\"http://www.opengis.net/swe/1.0.1\"\n" 
    r += "  xmlns:om=\"http://www.opengis.net/om/1.0\"\n" 
    r += "  xmlns=\"http://www.opengis.net/sos/1.0\"\n" 
    r += "  xmlns:sos=\"http://www.opengis.net/sos/1.0\"\n" 
    r += "  xmlns:ows=\"http://www.opengis.net/ows/1.1\"\n"
    r += "  xmlns:ogc=\"http://www.opengis.net/ogc\"\n"
    r += "  xmlns:tml=\"http://www.opengis.net/tml\"\n"
    r += "  xmlns:sml=\"http://www.opengis.net/sensorML/1.0.1\"\n"
    r += "  xmlns:xsi=\"http://www.w3.org/2001/XMLSchema-instance\"\n"
    r += "  xsi:schemaLocation=\"http://www.opengis.net/sos/1.0 http://schemas.opengis.net/sos/1.0.0/sosGetCapabilities.xsd\"\n"
    r += "  version=\"1.0.0\">\n"
    
    if not GC.ServiceIdentifier==[]:
        r += "  <!--~~~~~~~~~~~~~~~~~~~~~~~~-->\n"
        r += "  <!-- Service Identification -->\n"
        r += "  <!--~~~~~~~~~~~~~~~~~~~~~~~~-->\n"
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
        r += "  <!--~~~~~~~~~~~~~~~~~~~~~~-->\n"
        r += "  <!-- Provider Description -->\n"
        r += "  <!--~~~~~~~~~~~~~~~~~~~~~~-->\n"
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
        r += "  <!--~~~~~~~~~~~~~~~~~~~~~~~~~~~~~-->\n"
        r += "  <!-- operations Metadata Section -->\n"
        r += "  <!--~~~~~~~~~~~~~~~~~~~~~~~~~~~~~-->\n"
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
                r += "    </ows:Parameter>\n"
            r += "    </ows:Operation>\n"
        r += "  </ows:OperationsMetadata>\n"
        
    if not GC.ObservationOfferingList==[]:
        r += "  <!--~~~~~~~~~~~~~~~~~~-->\n"
        r += "  <!-- Contents Section -->\n"
        r += "  <!--~~~~~~~~~~~~~~~~~~-->\n"
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
                r += "        <sos:procedure xlink:href=\"" + pr + "\" />\n"
            
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
    r += "    </Capabilities>\n"
    return r
    




