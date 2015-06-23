#  -*- coding: utf-8 -*-
# istsos WebAdmin - Istituto Scienze della Terra
# Copyright (C) 2012 Massimiliano Cannata, Milan Antonovic
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

import lib.requests as requests
import time

def getCapabilities(doc):
    
    doc.write('\n\n-----------------getCapabilities----------------------------\n')
    
    service = 'test'
    
    success_get = False
    success_post = False
    combo = False
    
    get = 'http://localhost/istsos/' + service + '?request=getCapabilities&sections=serviceidentification,serviceprovider,operationsmetadata,contents&service=SOS&version=1.0.0'
    
    post = '''<?xml version="1.0" encoding="UTF-8"?>
    <sos:GetCapabilities
        xmlns:xsi="http://www.w3.org/2001/XMLSchema-instance"
        xsi:schemaLocation="http://schemas.opengis.net/sos/1.0.0/sosAll.xsd"
        xmlns:sos="http://www.opengis.net/sos/1.0"
        xmlns:gml="http://www.opengis.net/gml/3.2"
        xmlns:ogc="http://www.opengis.net/ogc"
        xmlns:om="http://www.opengis.net/om/1.0"
        version="1.0.0" service="SOS">'
            <section>serviceidentification</section>
            <section>serviceprovider</section>
            <section>operationsmetadata</section>
            <section>contents</section>
    </sos:GetCapabilities>'''
    
    header = {'Content-Type': 'application/xml'}    
    
    get1 = requests.get(get, prefetch=True)
    time.sleep(1)
    get2 = requests.get(get, prefetch=True)
    
    res1 = requests.post('http://localhost/istsos/' + service, data=post, headers=header, prefetch=True)
    time.sleep(1)
    res2 = requests.post('http://localhost/istsos/' + service, data=post, headers=header, prefetch=True)
    
    if get1.text == get2.text:
        doc.write('GET retrieved the same information')
        success_get = True
    else:
        doc.write('GET didn\'t retrieve the correct information')
        doc.write('\n---------------------GET didn\'t retrieve the correct information--------------------\n')
        doc.write(get2.text)
    
    if res1.text == res2.text:
        doc.write('POST retrieved the same information')
        success_post = True
    else:
        doc.write('POST didn\'t retrieve the correct information')
        doc.write('\n---------------------POST didn\'t retrieve the correct information--------------------\n')
        doc.write(res2.text)
        
    if get2.text == res2.text:
        doc.write('POST and GET retrieved the same information')
        combo = True
    else:
        doc.write('POST and GET didn\'t retrieve the correct information')
        doc.write('\nPOST and GET didn\'t retrieve the correct information\n')
        doc.write('\n---------------------GET--------------------\n\n')
        doc.write(get2.text)
        doc.write('\n\n---------------------POST--------------------\n\n')
        doc.write(res2.text)

    result = {
        'getCapabilities_GET' : success_get,
        'getCapabilities_POST' : success_post,
        'getCapabilities_BOTH' : combo
        }
        
    return result



   
def describeSensor(doc):
    
    doc.write('\n\n-----------------describeSensor-----------------------------\n')
    
    service = 'test'
    procedure = 'test'
    
    success_get = False
    success_post = False
    combo = False
    
    get = 'http://localhost/istsos/' + service + '?request=describeSensor&procedure=' + procedure + '&outputFormat=text/xml%3Bsubtype%3D\'sensorML/1.0.0\'&service=SOS&version=1.0.0'
    
    post = '''<?xml version="1.0" encoding="UTF-8"?>
    <sos:describeSensor
        xmlns:xsi="http://www.w3.org/2001/XMLSchema-instance"
        xsi:schemaLocation="http://schemas.opengis.net/sos/1.0.0/sosAll.xsd"
        xmlns:sos="http://www.opengis.net/sos/1.0"
        xmlns:gml="http://www.opengis.net/gml/3.2"
        xmlns:ogc="http://www.opengis.net/ogc"
        xmlns:om="http://www.opengis.net/om/1.0"
        service="SOS"
        outputFormat="text/xml;subtype=\'sensorML/1.0.0\'">
            <procedure>test</procedure>
    </sos:describeSensor>'''
    
    header = {'Content-Type': 'application/xml'}        
    
    get1 = requests.get(get, prefetch=True)
    time.sleep(1)
    get2 = requests.get(get, prefetch=True)
    
    res1 = requests.post('http://localhost/istsos/' + service, data=post, headers=header, prefetch=True)
    time.sleep(1)
    res2 = requests.post('http://localhost/istsos/' + service, data=post, headers=header, prefetch=True)
    
    if get1.text == get2.text:
        doc.write('GET retrieved the same information')
        success_get = True
    else:
        doc.write('GET didn\'t retrieve the correct information')
        doc.write('\n---------------------GET didn\'t retrieve the correct information--------------------\n')
        doc.write(get2.text)
    
    if res1.text == res2.text:
        doc.write('POST retrieved the same information')
        success_post = True
    else:
        doc.write('POST didn\'t retrieve the correct information')
        doc.write('\n---------------------POST didn\'t retrieve the correct information--------------------\n')
        doc.write(res2.text)
    
    if get2.text == res2.text:
        doc.write('POST and GET retrieved the same information')
        combo = True
    else:
        doc.write('POST and GET didn\'t retrieve the correct information')
        doc.write('\nPOST and GET didn\'t retrieve the correct information\n')
        doc.write('\n---------------------GET--------------------\n\n')
        doc.write(get2.text)
        doc.write('\n\n---------------------POST--------------------\n\n')
        doc.write(res2.text)

    result = {
        'describeSensor_GET' : success_get,
        'describeSensor_POST' : success_post,
        'describeSensor_BOTH' : combo
        }
        
    return result





    
def getObservation(doc):
    
    doc.write('\n\n-----------------getObservation-----------------------------\n')
    
    service = 'test'
    procedure = 'test'
    offering = 'temporary'
    obproperty = 'test'
    
    success_get = False
    success_getB = False
    success_post = False
    combo = False
    
    get = 'http://localhost/istsos/' + service + '?service=SOS&request=GetObservation&offering=' + offering + '&procedure=' + procedure + '&eventTime=2013-01-01T00:00:00+01/2013-01-05T17:00:00+01,2013-01-05T17:30:00+01&observedProperty=' + obproperty + '&responseFormat=text/xml;subtype=\'sensorML/1.0.0\'&service=SOS&version=1.0.0'
    getBBOX = 'http://localhost/istsos/' + service + '?service=SOS&request=GetObservation&offering=' + offering + '&observedProperty='  + obproperty + '&responseFormat=text/xml;subtype=\'sensorML/1.0.0\'&service=SOS&version=1.0.0&featureOfInterest=&BBOX=[713800,89915 713830,89940(,21781)]&service=SOS&version=1.0.0'
    
    post = '''<?xml version="1.0" encoding="UTF-8"?>
    <sos:GetObservation
       xmlns:xsi="http://www.w3.org/2001/XMLSchema-instance"
       xsi:schemaLocation="http://schemas.opengis.net/sos/1.0.0/sosAll.xsd"
       xmlns:sos="http://www.opengis.net/sos/1.0"
       xmlns:gml="http://www.opengis.net/gml/3.2"
       xmlns:ogc="http://www.opengis.net/ogc"
       xmlns:om="http://www.opengis.net/om/1.0" 
       service="SOS" version='1.0.0'>
        <offering>urn:ogc:def:offering:x-istsos:1.0:temporary</offering>
        <procedure>urn:ogc:def:procedure:x-istsos:1.0:test</procedure>
        <eventTime>
            <gml:TimePeriod>
               <gml:beginPosition>2013-01-01T00:00:00+01:00</gml:beginPosition>
               <gml:endPosition>2013-01-05T00:00:00+01:00</gml:endPosition>
            </gml:TimePeriod>
            <gml:TimeInstant>
               <gml:timePosition>2013-01-05T00:00:00+01:00</gml:timePosition>
            </gml:TimeInstant>
        </eventTime>
        <responseFormat>text/xml;subtype='sensorML/1.0.0'</responseFormat>
        <observedProperty>urn:ogc:def:parameter:x-istsos:1.0:test</observedProperty>
    </sos:GetObservation>'''
    
    post2 = '''<?xml version="1.0" encoding="UTF-8"?>
    <sos:GetObservation
       xmlns:xsi="http://www.w3.org/2001/XMLSchema-instance"
       xsi:schemaLocation="http://schemas.opengis.net/sos/1.0.0/sosAll.xsd"
       xmlns:sos="http://www.opengis.net/sos/1.0"
       xmlns:gml="http://www.opengis.net/gml/3.2"
       xmlns:ogc="http://www.opengis.net/ogc"
       xmlns:om="http://www.opengis.net/om/1.0" 
       service="SOS" version='1.0.0'>
        <offering>urn:ogc:def:offering:x-istsos:1.0:temporary</offering>
        <procedure>urn:ogc:def:procedure:x-istsos:1.0:test</procedure>
    
        <eventTime>
            <gml:TimeInstant>
               <gml:timePosition>2013-01-07T00:00:00+01:00</gml:timePosition>
            </gml:TimeInstant>
        </eventTime>
        <responseFormat>text/xml;subtype='sensorML/1.0.0'</responseFormat>
        <srsName>urn:ogc:crs:EPSG:21781</srsName>
        <observedProperty>urn:ogc:def:parameter:x-istsos:1.0:test</observedProperty>
    </sos:GetObservation>'''
    
    post4 = '''<?xml version="1.0" encoding="UTF-8"?>
    <sos:GetObservation
       xmlns:xsi="http://www.w3.org/2001/XMLSchema-instance"
       xsi:schemaLocation="http://schemas.opengis.net/sos/1.0.0/sosAll.xsd"
       xmlns:sos="http://www.opengis.net/sos/1.0"
       xmlns:gml="http://www.opengis.net/gml/3.2"
       xmlns:ogc="http://www.opengis.net/ogc"
       xmlns:om="http://www.opengis.net/om/1.0" 
       service="SOS" version='1.0.0'>
        <offering>urn:ogc:def:offering:x-istsos:1.0:temporary</offering>
        <procedure>urn:ogc:def:procedure:x-istsos:1.0:test</procedure>
        <eventTime>
            <gml:TimeInstant>
               <gml:timePosition>2012-10-26T17:00:00+01</gml:timePosition>
            </gml:TimeInstant>
        </eventTime>
        <responseFormat>text/xml;subtype='sensorML/1.0.0'</responseFormat>
        <observedProperty>urn:ogc:def:parameter:x-istsos:1.0:test</observedProperty>
    </sos:GetObservation>'''
    
    header = {'Content-Type': 'application/xml'}        
    
    get1 = requests.get(get, prefetch=True)
    time.sleep(1)
    get2 = requests.get(get, prefetch=True)
    
    getb1 = requests.get(getBBOX, prefetch=True)
    time.sleep(1)
    getb2 = requests.get(getBBOX, prefetch=True)
    
    res1 = requests.post('http://localhost/istsos/' + service, data=post, headers=header, prefetch=True)
    time.sleep(1)
    res2 = requests.post('http://localhost/istsos/' + service, data=post, headers=header, prefetch=True)
    
    res3 = requests.post('http://localhost/istsos/' + service, data=post2, headers=header, prefetch=True)
    time.sleep(1)
    res4 = requests.post('http://localhost/istsos/' + service, data=post2, headers=header, prefetch=True)

    res5 = requests.post('http://localhost/istsos/' + service, data=post4, headers=header, prefetch=True)
    time.sleep(1)
    res6 = requests.post('http://localhost/istsos/' + service, data=post4, headers=header, prefetch=True)
    
    if get1.text == get2.text:
        doc.write('GET retrieved the same information')
        success_get = True
    else:
        doc.write('GET didn\'t retrieve the correct information')
        doc.write('\n---------------------GET didn\'t retrieve the correct information--------------------\n')
        doc.write(get2.text)
        
    if getb1.text == getb2.text:
        doc.write('GET retrieved the same information')
        success_getB = True
    else:
        doc.write('GETB didn\'t retrieve the correct information')
        doc.write('\n---------------------GETB didn\'t retrieve the correct information--------------------\n')
        doc.write(getb2.text)
    
    if res1.text == res2.text:
        doc.write('POST retrieved the same information')
        success_post = True
    else:
        doc.write('POST didn\'t retrieve the correct information')
        doc.write('\n---------------------POST didn\'t retrieve the correct information--------------------\n')
        doc.write(res2.text)
        
    
    if res3.text == res4.text:
        doc.write('POST2 retrieved the same information')
        success_post = True
    else:
        doc.write('POST2 didn\'t retrieve the correct information')
        doc.write('\n---------------------POST2 didn\'t retrieve the correct information--------------------\n')
        doc.write(res3.text)
    
    if res5.text == res6.text:
        doc.write('POST4 retrieved the same information')
        success_post = True
    else:
        doc.write('POST4 didn\'t retrieve the correct information')
        doc.write('\n---------------------POST4 didn\'t retrieve the correct information--------------------\n')
        doc.write(res5.text)
    
        
    if get2.text == getb2.text:
        doc.write('GET and GETB retrieved the same information')
        combo = True
    else:
        doc.write('GET and GETB didn\'t retrieve the correct information')
        doc.write('\nGET and GETB didn\'t retrieve the correct information\n')
        doc.write('\n---------------------GET--------------------\n\n')
        doc.write(get2.text)
        doc.write('\n\n---------------------GETB--------------------\n\n')
        doc.write(getb2.text)
    
    if get2.text == res2.text:
        doc.write('POST and GET retrieved the same information')
        combo = True
    else:
        doc.write('POST and GET didn\'t retrieve the correct information')
        doc.write('\nPOST and GET didn\'t retrieve the correct information\n')
        doc.write('\n---------------------GET--------------------\n\n')
        doc.write(get2.text)
        doc.write('\n\n---------------------POST--------------------\n\n')
        doc.write(res2.text)
        
    if getb2.text == res2.text:
        doc.write('POST and GETB retrieved the same information')
        combo = True
    else:
        doc.write('POST and GETB didn\'t retrieve the correct information')
        doc.write('\nPOST and GETB didn\'t retrieve the correct information\n')
        doc.write('\n---------------------GETB--------------------\n\n')
        doc.write(getb2.text)
        doc.write('\n\n---------------------POST--------------------\n\n')
        doc.write(res2.text)
            
    if get2.text == res4.text:
        doc.write('POST2 and GET retrieved the same information')
        combo = True
    else:
        doc.write('POST2 and GET didn\'t retrieve the correct information')
        doc.write('\nPOST2 and GET didn\'t retrieve the correct information\n')
        doc.write('\n---------------------GET--------------------\n\n')
        doc.write(get2.text)
        doc.write('\n\n---------------------POST2--------------------\n\n')
        doc.write(res4.text)
            
    if get2.text == res6.text:
        doc.write('POST4 and GET retrieved the same information')
        combo = True
    else:
        doc.write('POST4 and GET didn\'t retrieve the correct information')
        doc.write('\nPOST4 and GET didn\'t retrieve the correct information\n')
        doc.write('\n---------------------GET--------------------\n\n')
        doc.write(get2.text)
        doc.write('\n\n---------------------POST4--------------------\n\n')
        doc.write(res6.text)

    result = {
        'getObservation_GET' : success_get,
        'getObservation_GETB' : success_getB,
        'getObservation_POST' : success_post,
        'getObservation_BOTH' : combo
        }
        
    return result
    
    
    
    
def registerSensor(doc):
    
    doc.write('\n\n-----------------registerSensor-----------------------------\n')
    
    service = 'test'
    
    success_posts = False
    success_postc = False
    
    header = {'Content-Type': 'application/xml'}
    
    post_simple = '''<?xml version="1.0" encoding="UTF-8"?>
    <sos:RegisterSensor 
        service="SOS" 
        version="1.0.0" 
        xmlns:sos="http://www.opengis.net/sos/1.0" 
        xmlns:gml="http://www.opengis.net/gml" 
        xmlns:om="http://www.opengis.net/om" 
        xmlns:sml="http://www.opengis.net/sensorML" 
        xmlns:swe="http://www.opengis.net/swe" 
        xmlns:xlink="http://www.w3.org/1999/xlink" 
        xmlns:xsi="http://www.w3.org/2001/XMLSchema-instance" 
        xsi:schemaLocation="http://schemas.opengis.net/sos/1.0.0/sosRegisterSensor.xsd">
      <sos:SensorDescription>
        <sml:member>
          <sml:System gml:id="H_TREVANO">
            <gml:name>H_TREVANO</gml:name>
            <sml:identification/>
            <sml:classification>
              <sml:ClassifierList>
                <sml:classifier name="System Type">
                  <sml:Term definition="urn:ogc:def:classifier:x-istsos:1.0:systemType">
                    <sml:value>insitu-fixed-point</sml:value>
                  </sml:Term>
                </sml:classifier>
                <sml:classifier name="Sensor Type">
                  <sml:Term definition="urn:ogc:def:classifier:x-istsos:1.0:sensorType">
                    <sml:value>humidity sensor</sml:value>
                  </sml:Term>
                </sml:classifier>
              </sml:ClassifierList>
            </sml:classification>
            <sml:capabilities>
              <swe:DataRecord/>
            </sml:capabilities>
            <gml:location>
              <gml:Point gml:id="trevano" srsName="EPSG:4326">
                <gml:coordinates>8.961435,46.028235,350</gml:coordinates>
              </gml:Point>
            </gml:location>
            <sml:outputs>
              <sml:OutputList>
                <sml:output name="output data">
                  <swe:DataRecord definition="urn:ogc:def:dataType:x-istsos:1.0:timeSeries">
                    <swe:field name="Time">
                      <swe:Time definition="urn:ogc:def:parameter:x-istsos:1.0:time:iso8601" gml:id="1">
                        <swe:uom code="iso8601"/>
                      </swe:Time>
                    </swe:field>
                    <swe:field name="air humidity">
                      <swe:Quantity definition="urn:ogc:def:parameter:x-istsos:1.0:meteo:air:humidity" gml:id="2">
                        <swe:uom code="%"/>
                      </swe:Quantity>
                    </swe:field>
                  </swe:DataRecord>
                </sml:output>
              </sml:OutputList>
            </sml:outputs>
          </sml:System>
        </sml:member>
      </sos:SensorDescription>
      <sos:ObservationTemplate>
        <om:Observation>
          <om:procedure xlink:href="urn:ogc:object:procedure:x-istsos:1.0:H_TREVANO"/>
          <om:samplingTime>
            <gml:TimePeriod>
              <gml:TimeLength/>
            </gml:TimePeriod>
          </om:samplingTime>
          <om:observedProperty>
            <swe:CompositPhenomenon dimension="2">
              <swe:component xlink:href="urn:ogc:def:parameter:x-istsos:1.0:time:iso8601"/>
              <swe:component xlink:href="urn:ogc:def:parameter:x-istsos:1.0:meteo:air:humidity"/>
            </swe:CompositPhenomenon>
          </om:observedProperty>
          <om:featureOfInterest xlink:href="trevano">
            <gml:Point gml:id="trevano" srsName="EPSG:4326">
              <gml:coordinates>8.961435,46.028235,350</gml:coordinates>
            </gml:Point>
          </om:featureOfInterest>
          <om:result>
            <swe:DataArray>
              <swe:elementCount>
                <swe:value>2</swe:value>
              </swe:elementCount>
              <swe:elementType name="SimpleDataArray" xlink:href="urn:ogc:def:dataType:x-istsos:1.0:timeSeriesDataRecord">
                <swe:DataRecord definition="urn:ogc:def:dataType:x-istsos:1.0:timeSeries">
                  <swe:field name="Time">
                    <swe:Time definition="urn:ogc:def:parameter:x-istsos::time:iso8601" gml:id="1">
                      <swe:uom code="iso8601"/>
                    </swe:Time>
                  </swe:field>
                  <swe:field name="air humidity">
                    <swe:Quantity definition="urn:ogc:def:parameter:x-istsos:1.0:meteo:air:humidity" gml:id="2">
                      <swe:uom code="%"/>
                    </swe:Quantity>
                  </swe:field>
                </swe:DataRecord>
              </swe:elementType>
              <swe:encoding>
                <swe:TextBlock blockSeparator="@" decimalSeparator="." tokenSeparator=","/>
              </swe:encoding>
              <swe:values/>
            </swe:DataArray>
          </om:result>
        </om:Observation>
      </sos:ObservationTemplate>
    </sos:RegisterSensor>'''

    post_composite = '''<?xml version="1.0" encoding="UTF-8"?>
    <sos:RegisterSensor 
        service="SOS" 
        version="1.0.0" 
        xmlns:sos="http://www.opengis.net/sos/1.0" 
        xmlns:gml="http://www.opengis.net/gml" 
        xmlns:om="http://www.opengis.net/om" 
        xmlns:sml="http://www.opengis.net/sensorML" 
        xmlns:swe="http://www.opengis.net/swe" 
        xmlns:xlink="http://www.w3.org/1999/xlink" 
        xmlns:xsi="http://www.w3.org/2001/XMLSchema-instance">
      <sos:SensorDescription>
        <sml:member>
          <sml:System gml:id="LL_CERESIO">
            <gml:name>LL_CERESIO</gml:name>
            <sml:identification>
              <sml:IdentifierList>
                <sml:identifier name="Short Name">
                  <sml:Term definition="urn:x-ogc:def:identifier:x-istsos:1.0:shortName">
                    <sml:value>CHS001</sml:value>
                  </sml:Term>
                </sml:identifier>
                <sml:identifier name="Long Name">
                  <sml:Term definition="urn:x-ogc:def:identifier:x-istsos:1.0:longName">
                    <sml:value>Capacitive humidity sensors model 001</sml:value>
                  </sml:Term>
                </sml:identifier>
                <sml:identifier name="Manufacturer Name">
                  <sml:Term definition="urn:x-ogc:def:identifier:x-istsos:1.0:manufacturerName">
                    <sml:value>Technical Department - SUPSI</sml:value>
                  </sml:Term>
                </sml:identifier>
                <sml:identifier name="Model Number">
                  <sml:Term definition="urn:x-ogc:def:identifier:x-istsos:1.0:modelNumber">
                    <sml:value>TDS-001</sml:value>
                  </sml:Term>
                </sml:identifier>
                <sml:identifier name="Serial Number">
                  <sml:Term definition="urn:x-ogc:def:identifier:x-istsos:1.0:serialNumber">
                    <sml:value>EXZU70012987712ABC</sml:value>
                  </sml:Term>
                </sml:identifier>
                <sml:identifier name="Device ID">
                  <sml:Term definition="urn:x-ogc:def:identifier:x-istsos:1.0:deviceID">
                    <sml:value>TDSCHSMWLLUGANO</sml:value>
                  </sml:Term>
                </sml:identifier>
              </sml:IdentifierList>
            </sml:identification>
            <sml:classification>
              <sml:ClassifierList>
                <sml:classifier name="System Type">
                  <sml:Term definition="urn:ogc:def:classifier:x-istsos:1.0:systemType">
                    <sml:value>insitu-fixed-point</sml:value>
                  </sml:Term>
                </sml:classifier>
                <sml:classifier name="Sensor Type">
                  <sml:Term definition="urn:ogc:def:classifier:x-istsos:1.0:sensorType">
                    <sml:value>lake water level</sml:value>
                  </sml:Term>
                </sml:classifier>
              </sml:ClassifierList>
            </sml:classification>
            <sml:characteristics xlink:href="http://192.168.56.101/istsos/admin/"/>
            <sml:capabilities>
              <swe:DataRecord>
                <swe:field name="Memory Capacity">
                  <swe:Quantity definition="urn:x-ogc:def:classifier:x-istsos:1.0:memoryCapacity">
                    <swe:uom code="Byte"/>
                    <swe:value>34359738368</swe:value>
                  </swe:Quantity>
                </swe:field>
                <swe:field name="Battery Current">
                  <swe:Quantity definition="urn:x-ogc:def:phenomenon:x-istsos:1.0:batteryCurrent">
                    <swe:uom code="A.h"/>
                    <swe:value>1420000</swe:value>
                  </swe:Quantity>
                </swe:field>
                <swe:field name="Sampling time resolution">
                  <swe:Quantity definition="urn:x-ogc:def:classifier:x-istsos:1.0:samplingTimeResolution">
                    <swe:uom code="iso8601"/>
                    <swe:value>PT20M</swe:value>
                  </swe:Quantity>
                </swe:field>
                <swe:field name="Acquisition time resolution">
                  <swe:Quantity definition="urn:x-ogc:def:classifier:x-istsos:1.0:acquisitionTimeResolution">
                    <swe:uom code="iso8601"/>
                    <swe:value>PT30M</swe:value>
                  </swe:Quantity>
                </swe:field>
              </swe:DataRecord>
            </sml:capabilities>
            <sml:contact role="urn:x-ogc:def:classifiers:x-istsos:1.0:contactType:owner">
              <sml:ResponsibleParty>
                <sml:individualName>Fausto Gervasoni</sml:individualName>
                <sml:organizationName>Institute of Earth Science - SUPSI</sml:organizationName>
                <sml:contactInfo>
                  <sml:phone>
                    <sml:voice>+41586666200</sml:voice>
                    <sml:facsimile>+41586666209</sml:facsimile>
                  </sml:phone>
                  <sml:address>
                    <sml:deliveryPoint>Campus Trevano</sml:deliveryPoint>
                    <sml:city>Canobbio</sml:city>
                    <sml:administrativeArea>Ticino</sml:administrativeArea>
                    <sml:postalCode>6952</sml:postalCode>
                    <sml:country>Switzerland</sml:country>
                    <sml:electronicMailAddress>ist@supsi.ch</sml:electronicMailAddress>
                  </sml:address>
                  <sml:onlineResource xlink:href="http://www.supsi.ch/ist"/>
                </sml:contactInfo>
              </sml:ResponsibleParty>
            </sml:contact>
            <sml:contact role="urn:x-ogc:def:classifiers:x-istsos:1.0:contactType:manufacturer">
              <sml:ResponsibleParty>
                <sml:individualName>Paolo Rezzonico</sml:individualName>
                <sml:organizationName>Technical Department - SUPSI</sml:organizationName>
                <sml:contactInfo>
                  <sml:phone>
                    <sml:voice>+41586666200</sml:voice>
                    <sml:facsimile>+41586666209</sml:facsimile>
                  </sml:phone>
                  <sml:address>
                    <sml:deliveryPoint>Residence Stella alpina</sml:deliveryPoint>
                    <sml:city>Viganello</sml:city>
                    <sml:administrativeArea>Ticino</sml:administrativeArea>
                    <sml:postalCode>6962</sml:postalCode>
                    <sml:country>Switzerland</sml:country>
                    <sml:electronicMailAddress>ist@supsi.ch</sml:electronicMailAddress>
                  </sml:address>
                  <sml:onlineResource xlink:href="http://www.supsi.ch/ist"/>
                </sml:contactInfo>
              </sml:ResponsibleParty>
            </sml:contact>
            <sml:contact role="urn:x-ogc:def:classifiers:x-istsos:1.0:contactType:operator">
              <sml:ResponsibleParty>
                <sml:individualName>Giacomino Bragaferro</sml:individualName>
                <sml:organizationName>Ufficio Tecnico Augenthaler</sml:organizationName>
                <sml:contactInfo>
                  <sml:phone>
                    <sml:voice>+41586666200</sml:voice>
                    <sml:facsimile>+41586666209</sml:facsimile>
                  </sml:phone>
                  <sml:address>
                    <sml:deliveryPoint>Via delle Vigne 6</sml:deliveryPoint>
                    <sml:city>Bironico</sml:city>
                    <sml:administrativeArea>Ticino</sml:administrativeArea>
                    <sml:postalCode>6804</sml:postalCode>
                    <sml:country>Switzerland</sml:country>
                    <sml:electronicMailAddress>ist@supsi.ch</sml:electronicMailAddress>
                  </sml:address>
                  <sml:onlineResource xlink:href="http://www.supsi.ch/ist"/>
                </sml:contactInfo>
              </sml:ResponsibleParty>
            </sml:contact>
            <sml:documentation>
              <sml:Document>
                <gml:description>User Manual</gml:description>
                <sml:date>01/01/2013</sml:date>
                <sml:format>text/html</sml:format>
                <gml:onlineResource xlink:href="http://goo.gl/0fpAA"/>
              </sml:Document>
            </sml:documentation>
            <gml:location>
              <gml:Point gml:id="ceresio" srsName="EPSG:4326">
                <gml:coordinates>8.962662,46.004809,270</gml:coordinates>
              </gml:Point>
            </gml:location>
            <sml:interfaces>
              <sml:InterfaceList>
                <sml:interface name="Bluetooth4.0/SDP/RFCOMM/L2CAP"/>
                <sml:interface name="USB2.0/Mass Storage"/>
              </sml:InterfaceList>
            </sml:interfaces>
            <sml:outputs>
              <sml:OutputList>
                <sml:output name="output data">
                  <swe:DataRecord definition="urn:ogc:def:dataType:x-istsos:1.0:timeSeries">
                    <swe:field name="Time">
                      <swe:Time definition="urn:ogc:def:parameter:x-istsos:1.0:time:iso8601" gml:id="1">
                        <swe:uom code="iso8601"/>
                      </swe:Time>
                    </swe:field>
                    <swe:field name="lake water level">
                      <swe:Quantity definition="urn:ogc:def:parameter:x-istsos:1.0:lake:water:level" gml:id="2">
                        <swe:uom code="m"/>
                      </swe:Quantity>
                    </swe:field>
                    <swe:field name="lake water temperature">
                      <swe:Quantity definition="urn:ogc:def:parameter:x-istsos:1.0:lake:water:temperature" gml:id="2">
                        <swe:uom code="°C"/>
                      </swe:Quantity>
                    </swe:field>
                  </swe:DataRecord>
                </sml:output>
              </sml:OutputList>
            </sml:outputs>
          </sml:System>
        </sml:member>
      </sos:SensorDescription>
      <sos:ObservationTemplate>
        <om:Observation>
          <om:procedure xlink:href="urn:ogc:object:procedure:x-istsos:1.0:LL_CERESIO"/>
          <om:samplingTime>
            <gml:TimePeriod>
              <gml:TimeLength/>
            </gml:TimePeriod>
          </om:samplingTime>
          <om:observedProperty>
            <swe:CompositPhenomenon dimension="2">
              <swe:component xlink:href="urn:ogc:def:parameter:x-istsos:1.0:time:iso8601"/>
              <swe:component xlink:href="urn:ogc:def:parameter:x-istsos:1.0:lake:water:level"/>
              <swe:component xlink:href="urn:ogc:def:parameter:x-istsos:1.0:lake:water:temperature"/>
            </swe:CompositPhenomenon>
          </om:observedProperty>
          <om:featureOfInterest xlink:href="ceresio">
            <gml:Point gml:id="ceresio" srsName="EPSG:4326">
              <gml:coordinates>8.962662,46.004809,270</gml:coordinates>
            </gml:Point>
          </om:featureOfInterest>
          <om:result>
            <swe:DataArray>
              <swe:elementCount>
                <swe:value>2</swe:value>
              </swe:elementCount>
              <swe:elementType name="SimpleDataArray" xlink:href="urn:ogc:def:dataType:x-istsos:1.0:timeSeriesDataRecord">
                <swe:DataRecord definition="urn:ogc:def:dataType:x-istsos:1.0:timeSeries">
                  <swe:field name="Time">
                    <swe:Time definition="urn:ogc:def:parameter:x-istsos:1.0:time:iso8601" gml:id="1">
                      <swe:uom code="iso8601"/>
                    </swe:Time>
                  </swe:field>
                  <swe:field name="lake water level">
                    <swe:Quantity definition="urn:ogc:def:parameter:x-istsos:1.0:lake:water:level" gml:id="2">
                      <swe:uom code="m"/>
                    </swe:Quantity>
                  </swe:field>
                  <swe:field name="lake water temperature">
                    <swe:Quantity definition="urn:ogc:def:parameter:x-istsos:1.0:lake:water:temperature" gml:id="2">
                      <swe:uom code="°C"/>
                    </swe:Quantity>
                  </swe:field>
                </swe:DataRecord>
              </swe:elementType>
              <swe:encoding>
                <swe:TextBlock blockSeparator="@" decimalSeparator="." tokenSeparator=","/>
              </swe:encoding>
              <swe:values/>
            </swe:DataArray>
          </om:result>
        </om:Observation>
      </sos:ObservationTemplate>
    </sos:RegisterSensor>'''
    
    
    ress1 = requests.post('http://localhost/istsos/' + service, data=post_simple, headers=header, prefetch=True)
    time.sleep(1)
    ress2 = requests.post('http://localhost/istsos/' + service, data=post_simple, headers=header, prefetch=True)
    
    resc1 = requests.post('http://localhost/istsos/' + service, data=post_composite, headers=header, prefetch=True)
    time.sleep(1)
    resc2 = requests.post('http://localhost/istsos/' + service, data=post_composite, headers=header, prefetch=True)
    
    if ress1.text == ress2.text:
        doc.write('POST Simple retrieved the same information')
        success_posts = True
    else:
        doc.write('POST Simple didn\'t retrieve the correct information')
        doc.write('\n---------------------POST Simple didn\'t retrieve the correct information--------------------\n')
        doc.write(ress2.text)    
    
    if resc1.text == resc2.text:
        doc.write('POST Composite retrieved the same information')
        success_postc = True
    else:
        doc.write('POST Composite didn\'t retrieve the correct information')
        doc.write('\n---------------------POST Composite didn\'t retrieve the correct information--------------------\n')
        doc.write(resc2.text)
    
    result = {
        'registerSensor_POSTS' : success_posts,
        'registerSensor_POSTC' : success_postc
        }
        
    return result


def insertObservation(doc):
    
    doc.write('\n\n-----------------insertObservation--------------------------\n')    
    
    service = 'test'
    
    success_posts = False
    success_postc = False
            
    header = {'Content-Type': 'application/xml'}
    
    post_simple = '''<?xml version="1.0" encoding="UTF-8"?>
    <sos:InsertObservation
       xmlns:xsi="http://www.w3.org/2001/XMLSchema-instance"
       xsi:schemaLocation="http://schemas.opengis.net/sos/1.0.0/sosAll.xsd"
       xmlns:sos="http://www.opengis.net/sos/1.0"
       xmlns:xlink="http://www.w3.org/1999/xlink"
       xmlns:sa="http://www.opengis.net/sampling/1.0"
       xmlns:swe="http://www.opengis.net/swe/1.0.1"
       xmlns:gml="http://www.opengis.net/gml/3.2"
       xmlns:ogc="http://www.opengis.net/ogc"
       xmlns:om="http://www.opengis.net/om/1.0" service="SOS" version="1.0.0" >
       <AssignedSensorId>urn:ogc:object:sensor:x-ist::???</AssignedSensorId>
       <om:Observation>
        <om:procedure xlink:href="urn:ogc:object:procedure:x-ist::thermo1"/>
        <om:samplingTime>
          <gml:TimePeriod>
            <gml:beginPosition>2010-01-01T00:10:00+00:00</gml:beginPosition>
            <gml:endPosition>2010-01-01T02:00:00+00:00</gml:endPosition>
          </gml:TimePeriod>
        </om:samplingTime>
        <om:observedProperty>
          <swe:CompositPhenomenon dimension="2">
            <swe:component xlink:href="urn:ogc:def:parameter:x-ist::time:iso8601"/>  
            <swe:component xlink:href="urn:ogc:def:property:x-ist::airtemperature" />      
          </swe:CompositPhenomenon>
        </om:observedProperty>
        <om:featureOfInterest xlink:href="urn:ogc:object:feature:x-ist::station:LUGANO"/>
          <om:result>
            <swe:DataArray>
              <swe:elementCount>
                <swe:Count>
                  <swe:value>2</swe:value>
                </swe:Count>
              </swe:elementCount>
              <swe:elementType name="SimpleDataArray">
                  <swe:DataRecord definition="http://mmiws.org/ont/x/timeSeries">
                    <swe:field name="Time">
                      <swe:Time definition="urn:ogc:def:parameter:x-ist::time:iso8601"/>
                    </swe:field>
                    <swe:field name="airtemperature">
                      <swe:Quantity definition="urn:ogc:def:property:x-ist::airtemperature">
                        <swe:uom code="deg"/>
                      </swe:Quantity>
                    </swe:field>
                  </swe:DataRecord>
              </swe:elementType>
            <swe:encoding>
              <swe:TextBlock tokenSeparator="," blockSeparator="@" decimalSeparator="."/>
            </swe:encoding>
            <swe:values>
                2010-01-01T00:10:00+00:00,9.81@
                2010-01-01T00:20:00+00:00,9.78@
                2010-01-01T00:30:00+00:00,9.74@
                2010-01-01T00:40:00+00:00,9.69@
                2010-01-01T00:50:00+00:00,9.4@
                2010-01-01T01:00:00+00:00,9.1@
                2010-01-01T01:10:00+00:00,8.7@
                2010-01-01T01:20:00+00:00,8.5@
                2010-01-01T01:30:00+00:00,8.4@
                2010-01-01T01:40:00+00:00,8.32@
                2010-01-01T01:50:00+00:00,8.30@
                2010-01-01T02:00:00+00:00,8.27
            </swe:values>
          </swe:DataArray>
        </om:result>
      </om:Observation>
    </sos:InsertObservation>'''

    post_composite = '''<?xml version="1.0" encoding="UTF-8"?>
    <sos:InsertObservation
       xmlns:xsi="http://www.w3.org/2001/XMLSchema-instance"
       xsi:schemaLocation="http://schemas.opengis.net/sos/1.0.0/sosAll.xsd"
       xmlns:sos="http://www.opengis.net/sos/1.0"
       xmlns:xlink="http://www.w3.org/1999/xlink"
       xmlns:sa="http://www.opengis.net/sampling/1.0"
       xmlns:swe="http://www.opengis.net/swe/1.0.1"
       xmlns:gml="http://www.opengis.net/gml/3.2"
       xmlns:ogc="http://www.opengis.net/ogc"
       xmlns:om="http://www.opengis.net/om/1.0" service="SOS" version="1.0.0" >
       <AssignedSensorId>urn:ogc:object:sensor:x-ist::???</AssignedSensorId>
       <om:Observation>
        <om:procedure xlink:href="urn:ogc:object:procedure:x-ist::meteo1"/>
        <om:samplingTime>
          <gml:TimePeriod>
            <gml:beginPosition>2010-02-10T16:10:00+01:00</gml:beginPosition>
            <gml:endPosition>2010-02-10T18:00:00+01:00</gml:endPosition>
          </gml:TimePeriod>
        </om:samplingTime>
        <om:observedProperty>
          <swe:CompositPhenomenon dimension="4">
            <swe:component xlink:href="urn:ogc:def:parameter:x-ist::time:iso8601"/>  
            <swe:component xlink:href="urn:ogc:def:property:x-ist::airtemperature"/> 
            <swe:component xlink:href="urn:ogc:def:property:x-ist::rainfall"/> 
            <swe:component xlink:href="urn:ogc:def:property:x-ist::pressure"/>
          </swe:CompositPhenomenon>
        </om:observedProperty>
        <om:featureOfInterest xlink:href="urn:ogc:object:feature:x-ist::station:LUGANO"/>
          <om:result>
            <swe:DataArray>
              <swe:elementCount>
                <swe:Count>
                  <swe:value>5</swe:value>
                </swe:Count>
              </swe:elementCount>
              <swe:elementType name="SimpleDataArray">
                  <swe:DataRecord definition="http://mmiws.org/ont/x/timeSeries">
                    <swe:field name="Time">
                      <swe:Time definition="urn:ogc:def:parameter:x-ist::time:iso8601"/>
                    </swe:field>
                    <swe:field name="airtemperature">
                      <swe:Quantity definition="urn:ogc:def:property:x-ist::airtemperature">
                        <swe:uom code="deg"/>
                      </swe:Quantity>
                    </swe:field>
                    <swe:field name="rainfall">
                      <swe:Quantity definition="urn:ogc:def:property:x-ist::rainfall">
                        <swe:uom code="mm"/>
                      </swe:Quantity>
                    </swe:field>
                    <swe:field name="pressure">
                      <swe:Quantity definition="urn:ogc:def:property:x-ist::pressure">
                        <swe:uom code="mbar"/>
                      </swe:Quantity>
                    </swe:field>
                  </swe:DataRecord>
              </swe:elementType>
            <swe:encoding>
              <swe:TextBlock tokenSeparator="," blockSeparator="@" decimalSeparator="."/>
            </swe:encoding>
            <swe:values>
                2010-02-10T16:10:00+01:00,12.8,0.2,940@
                2010-02-10T16:20:00+01:00,12.7,0.3,948@
                2010-02-10T16:30:00+01:00,12.5,0.2,949@
                2010-02-10T16:40:00+01:00,12.3,0.3,950@
                2010-02-10T16:50:00+01:00,12.2,0.4,949@
                2010-02-10T17:00:00+01:00,12.1,0.4,947@
                2010-02-10T17:10:00+01:00,11.8,0.5,948@
                2010-02-10T17:20:00+01:00,11.6,0.3,944@
                2010-02-10T17:30:00+01:00,11.7,0.4,943@
                2010-02-10T17:40:00+01:00,11.4,0.4,944@
                2010-02-10T17:50:00+01:00,11.4,0.5,944@
                2010-02-10T18:00:00+01:00,11.3,0.4,945
            </swe:values>
          </swe:DataArray>
        </om:result>
      </om:Observation>
    </sos:InsertObservation>'''
    
    
    ress1 = requests.post('http://localhost/istsos/' + service, data=post_simple, headers=header, prefetch=True)
    time.sleep(1)
    ress2 = requests.post('http://localhost/istsos/' + service, data=post_simple, headers=header, prefetch=True)
    
    resc1 = requests.post('http://localhost/istsos/' + service, data=post_composite, headers=header, prefetch=True)
    time.sleep(1)
    resc2 = requests.post('http://localhost/istsos/' + service, data=post_composite, headers=header, prefetch=True)
    
    if ress1.text == ress2.text:
        doc.write('POST Simple retrieved the same information')
        success_posts = True
    else:
        doc.write('POST Simple didn\'t retrieve the correct information')
        doc.write('\n---------------------POST Simple didn\'t retrieve the correct information--------------------\n')
        doc.write(ress2.text)    
    
    if resc1.text == resc2.text:
        doc.write('POST Composite retrieved the same information')
        success_postc = True
    else:
        doc.write('POST Composite didn\'t retrieve the correct information')
        doc.write('\n---------------------POST Composite didn\'t retrieve the correct information--------------------\n')
        doc.write(resc2.text)
        
    result = {
        'insertObservation_POSTS' : success_posts,
        'insertObservation_POSTC' : success_postc
        }
        
    return result

def getFeatureOfInterest(doc):
    
    doc.write('\n\n-----------------getFeatureOfInterest-----------------------\n')
    
    service = 'test'
    foi = 'test'
    srs = '4326'
    
    success_get = False
    success_post = False
    combo = False
    
    get = 'http://localhost/istsos/' + service + '?request=getFeatureOfInterest&FeatureOfInterestId=' + foi + '&srsName=' + srs + '&service=SOS&version=1.0.0'
        
    post = '''<?xml version="1.0" encoding="UTF-8"?>
    <sos:getfeatureOfinterest
        xmlns:xsi="http://www.w3.org/2001/XMLSchema-instance"
        xsi:schemaLocation="http://schemas.opengis.net/sos/1.0.0/sosAll.xsd"
        xmlns:sos="http://www.opengis.net/sos/1.0"
        xmlns:gml="http://www.opengis.net/gml/3.2"
        xmlns:ogc="http://www.opengis.net/ogc"
        xmlns:om="http://www.opengis.net/om/1.0" service="SOS" outputFormat="text/xml;subtype='sensorML/1.0.0'">
            <FeatureOfInterestId>urn:ogc:def:feature:x-istsos:1.0:Point:test</FeatureOfInterestId>
            <srsName>4326</srsName>    
      </sos:getfeatureOfinterest>'''
    
    header = {'Content-Type': 'application/xml'}    
    
    get1 = requests.get(get, prefetch=True)
    time.sleep(1)
    get2 = requests.get(get, prefetch=True)
    
    res1 = requests.post('http://localhost/istsos/' + service, data=post, headers=header, prefetch=True)
    time.sleep(1)
    res2 = requests.post('http://localhost/istsos/' + service, data=post, headers=header, prefetch=True)
    
    if get1.text == get2.text:
        doc.write('GET retrieved the same information')
        success_get = True
    else:
        doc.write('GET didn\'t retrieve the correct information')
        doc.write('\n---------------------GET didn\'t retrieve the correct information--------------------\n')
        doc.write(get2.text)
    
    if res1.text == res2.text:
        doc.write('POST retrieved the same information')
        success_post = True
    else:
        doc.write('POST didn\'t retrieve the correct information')
        doc.write('\n---------------------POST didn\'t retrieve the correct information--------------------\n')
        doc.write(res2.text)
    
    if get2.text == res2.text:
        doc.write('POST and GET retrieved the same information')
        combo = True
    else:
        doc.write('POST and GET didn\'t retrieve the correct information')
        doc.write('\nPOST and GET didn\'t retrieve the correct information\n')
        doc.write('\n---------------------GET--------------------\n\n')
        doc.write(get2.text)
        doc.write('\n\n---------------------POST--------------------\n\n')
        doc.write(res2.text)
        
    result = {
        'getFeatureOfInterest_GET' : success_get,
        'getFeatureOfInterest_POST' : success_post,
        'getFeatureOfInterest_BOTH' : combo
        }
        
    return result
