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
import isodate as iso
from lxml import etree as et
#import sosConfig

def render(GF,sosConfig):
    r = ""
    if GF.type.lower()=="station" or GF.type.lower()=="point":
        r += "<sa:SamplingPoint \n"
    elif GF.type=="surface":
        r += "<sa:SamplingSurface \n"
    else:
        r += "<sa:SamplingPoint \n"
    r += "gml:id=\"" + GF.name + "\" \n"
    r += "xmlns:sa=\"http://www.opengis.net/sampling/1.0\" \n"
    r += "xmlns:swe=\"http://www.opengis.net/swe/1.0.1\" \n"
    r += "xmlns:xsi=\"http://www.w3.org/2001/XMLSchema-instance\" \n"
    r += "xmlns:xlink=\"http://www.w3.org/1999/xlink\" \n"
    r += "xmlns:gml=\"http://www.opengis.net/gml\" \n"
    r += "xmlns:om=\"http://www.opengis.net/om/1.0\" \n"
    r += "xsi:schemaLocation=\"http://www.opengis.net/sampling/1.0 http://schemas.opengis.net/sampling/1.0.0/sampling.xsd\">\n"

    if GF.desc:
        r += "  <gml:description>" + GF.desc + "</gml:description>\n"
    r += "  <gml:name>" + GF.name + "</gml:name> \n"
    r += "  <sa:sampledFeature/>\n"
    
    for i in range(len(GF.procedures)):
        r += "  <sa:relatedObservation>\n"
        r += "    <om:Observation>\n"
        
        # Sampling time
        for a in range(len(GF.samplingTime[i])):
            if len(GF.samplingTime[i][a])==2: 
                r += "    <om:samplingTime>\n"
                r += "      <gml:TimePeriod>\n"
                r += "        <gml:beginPosition>" + iso.datetime_isoformat(GF.samplingTime[i][a][0]) + "</gml:beginPosition>\n"
                r += "        <gml:endPosition>" + iso.datetime_isoformat(GF.samplingTime[i][a][1]) + "</gml:endPosition>\n"
                r += "        <gml:duration>"  + iso.duration_isoformat(GF.samplingTime[i][a][1]-GF.samplingTime[i][a][0]) + "</gml:duration>\n"
                '''
                r += "        <gml:TimeLength>\n"
                r += "          <gml:duration>"  + iso.duration_isoformat(a[1]-a[0]) + "</gml:duration>\n"
                r += "          <gml:timeInterval unit=\"" + str(ob.timeResUnit) + "\">" + str(ob.timeResVal) + "</gml:timeInterval>\n"            
                r += "        </gml:TimeLength>\n"
                '''
                r += "      </gml:TimePeriod>\n"
                r += "    </om:samplingTime>\n"
                
        # Procedure
        r += "      <om:procedure xlink:href=\"" + GF.procedures[i] + "\"/>\n"
        
        # ObservationProperty
        r += "      <om:observedProperty>\n"
        if GF.obsType[i] == "insitu-mobile-point":
            ii=4
        else:
            ii=1
        r += "      <swe:CompositePhenomenon gml:id=\"comp_" + str(GF.idPrc[i]) + "\" dimension=\"" + str(len(GF.properties[i])+ii) + "\">\n"
        r += "      <gml:name/>\n"
        r += "        <swe:component xlink:href=\"" + sosConfig.urn["parameter"] + "time:iso8601" + " \" />\n" 
        #if ob.procedureType == "insitu-fixed-point":
            
        if GF.obsType[i]=="insitu-mobile-point":          
            r += "        <swe:component xlink:href=\"" + sosConfig.urn["refsystem"] + ":x-position\" />\n"
            r += "        <swe:component xlink:href=\"" + sosConfig.urn["refsystem"] + ":y-position\" />\n"
            r += "        <swe:component xlink:href=\"" + sosConfig.urn["refsystem"] + ":z-position\" />\n"
        
        for c in range(len(GF.properties[i])):
            r += "        <swe:component xlink:href=\"" + sosConfig.urn["parameter"] + GF.properties[i][c] + "\"/>\n"
            
        r += "      </swe:CompositePhenomenon>\n"
        r += "      </om:observedProperty>\n"
        
        #FEATURE OF INTEREST
        r += "    <om:featureOfInterest xlink:href=\"" + sosConfig.urn["feature"] + GF.type + ":" + GF.name + "\"/>\n"
            
        #RESULT EMPTY (?)
        r += "      <om:result/>\n"
        
        r += "    </om:Observation>\n"
        r += "  </sa:relatedObservation>\n"
    
    r += "  <sa:position> \n"
    if GF.geom:
        r += "    " + GF.geom + "\n"
    r += "  </sa:position>\n"
    if GF.type.lower()=="station" or GF.type.lower()=="point":
        r += "</sa:SamplingPoint> \n"
    elif GF.type=="surface":
        r += "</sa:SamplingSurface> \n"
    else:
        r += "</sa:SamplingPoint> \n"
    tree = et.ElementTree(et.fromstring(r))
    root = tree.getroot()
    return b'<?xml version="1.0" encoding="UTF-8"?>' + et.tostring(root)
