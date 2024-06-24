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
from lxml import etree as et
import json
from io import StringIO, BytesIO
from os import path
from parse_and_get import parse_and_get_ns

reurl = r'(http|ftp|https):\/\/[\w\-_]+(\.[\w\-_]+)+([\w\-\.,@?^=%&amp;:/~\+#]*[\w\-\@?^=%&amp;/~\+#])?'


def render(DS,sosConfig):
    # Returning content of the SensorML

    try:
        #---parse xml
        tree, ns = parse_and_get_ns(DS.smlFile)
    except Exception as ex:
        raise Exception("sensorML description for procedure '%s' not found or corrupted! [%s]"%(DS.smlFile,ex))

    #---map namespaces---
    try:
        register_namespace = et.register_namespace
        
        for key in ns:
            if not key in ns:
                register_namespace(key,ns[key])
    except AttributeError:
        try:
            et._namespace_map.update(ns)
            for key in ns:
                et._namespace_map[ns[key]] = key
        except AttributeError:
            try:
                from xml.etree.ElementTree import _namespace_map
            except ImportError:
                try:
                    from elementtree.ElementTree import _namespace_map
                except ImportError:
                    print(("Failed to import ElementTree from any known place"), file=sys.stderr)
            for key in ns:
                _namespace_map[ns[key]] = key

    mns = {
            'xsi': "http://www.w3.org/2001/XMLSchema-instance" ,
            'sml': "http://www.opengis.net/sensorML/1.0.1",
            'swe': "http://www.opengis.net/swe/1.0.1",
            'xlink': "http://www.w3.org/1999/xlink",
            'gml': 'http://www.opengis.net/gml'
        }

    for n in list(mns.keys()):
        try:
            ns[n]
        except:
            ns[n] = mns[n]


    #--- CREEATE FIELDS ACCORDING TO DATABASE OBSERVED_PROPERTIES
    # datarecord = tree.xpath("sml:member/sml:System/sml:outputs/sml:OutputList/sml:output/swe:DataRecord", 
    #                         namespaces= ns)

    datarecord = tree.find("{%s}member/{%s}System/{%s}outputs/{%s}OutputList/{%s}output/{%s}DataRecord"
                        %(ns['sml'],ns['sml'],ns['sml'],ns['sml'],ns['sml'],ns['swe']) )

    datarecord.clear()
    datarecord.attrib["definition"] = "%stimeSeries" % (sosConfig.urn['dataType'])
    fieldT = et.SubElement(datarecord,"{%s}field" % ns["swe"])
    fieldT.attrib["name"] = "Time"
    time = et.SubElement(fieldT,"{%s}Time" % ns["swe"])
    time.attrib["definition"] = sosConfig.urn["time"]

    # Adding constraint for current allowed times
    if (not DS.stime == None) and (not DS.etime == None):
        constraint =  et.SubElement(time, "{%s}constraint" % ns['swe'])
        allowedTimes =  et.SubElement(constraint, "{%s}AllowedTimes" % ns['swe'])
        interval = et.SubElement(allowedTimes, "{%s}interval" % ns['swe'])
        begin = et.SubElement(interval, "{%s}begin" % ns['swe'])
        begin.text = DS.stime.strftime("%Y-%m-%dT%H:%M:%S.%fZ")
        end = et.SubElement(interval, "{%s}end" % ns['swe'])
        end.text = DS.etime.strftime("%Y-%m-%dT%H:%M:%S.%fZ")

    if DS.procedureType=="insitu-mobile-point": # Adding 3d coordinates observation

        cord = et.SubElement(datarecord,"{%s}field" % ns["swe"])
        cord.attrib["name"] = "x"
        quantity = et.SubElement(cord,"{%s}Quantity" % ns["swe"])
        quantity.attrib["definition"] = sosConfig.urn["refsystem"] + sosConfig.istsosepsg + ":x-position"

        cord = et.SubElement(datarecord,"{%s}field" % ns["swe"])
        cord.attrib["name"] = "y"
        quantity = et.SubElement(cord,"{%s}Quantity" % ns["swe"])
        quantity.attrib["definition"] = sosConfig.urn["refsystem"] + sosConfig.istsosepsg + ":y-position"

        cord = et.SubElement(datarecord,"{%s}field" % ns["swe"])
        cord.attrib["name"] = "z"
        quantity = et.SubElement(cord,"{%s}Quantity" % ns["swe"])
        quantity.attrib["definition"] = sosConfig.urn["refsystem"] + sosConfig.istsosepsg + ":z-position"


    for index, field in enumerate(DS.observedProperties):

        fieldQ = et.SubElement(datarecord,"{%s}field" % ns["swe"])
        fieldQ.attrib["name"] = field["name_opr"]
        quantity = et.SubElement(fieldQ,"{%s}Quantity" % ns["swe"])
        quantity.attrib["definition"] = field["def_opr"]

        if not (field["name_uom"]=="" or field["name_uom"]==None or field["name_uom"]=="NULL"):
            uom = et.SubElement(quantity,"{%s}uom" % ns["swe"])
            uom.attrib["code"] = field["name_uom"]

        interval = et.SubElement(quantity, "{%s}interval" % ns['swe'])
        begin = et.SubElement(interval, "{%s}begin" % ns['swe'])
        begin.text = field['stime_prc'].strftime("%Y-%m-%dT%H:%M:%S.%fZ")
        end = et.SubElement(interval, "{%s}end" % ns['swe'])
        end.text = field['etime_prc'].strftime("%Y-%m-%dT%H:%M:%S.%fZ")
        """
        if not (field["desc_opr"]=="" or field["desc_opr"]==None or field["desc_opr"]=="NULL"):
            description = et.SubElement(quantity,"{%s}description" % ns["swe"])
            description.text = field["desc_opr"]
        """

        """
        # Handling constraint
        Permitted conigurations:
            {"role":"urn:ogc:def:classifiers:x-istsos:1.0:qualityIndex:check:reasonable","min":"10"}
            {"role":"urn:ogc:def:classifiers:x-istsos:1.0:qualityIndex:check:reasonable","max":"10"}
            {"role":"urn:ogc:def:classifiers:x-istsos:1.0:qualityIndex:check:reasonable","interval":["-10","10"]}
            {"role":"urn:ogc:def:classifiers:x-istsos:1.0:qualityIndex:check:reasonable","valueList":["1","2","3","4","5","6"]}
        """
        if not (field["constr_pro"]=="" or field["constr_pro"]==None):
            try:
                constraintObj = json.loads(field["constr_pro"])

                constraint = et.SubElement(quantity,"{%s}constraint" % ns["swe"])

                # Role attribute is not mandatory
                if "role" in constraintObj and constraintObj["role"]!="" and constraintObj["role"]!=None:
                    constraint.attrib[ "{%s}role" % ns['xlink'] ]= constraintObj["role"]

                AllowedValues = et.SubElement(constraint, "{%s}AllowedValues" % ns['swe'])

                # Factory on constraint min/max/interval/valuelist
                if "interval" in constraintObj:
                    interval = et.SubElement(AllowedValues, "{%s}interval" % ns['swe'])
                    interval.text = " ".join([ str(a) for a in constraintObj["interval"] ])
                    #interval.text = " ".join(constraintObj["interval"])

                elif "valueList" in constraintObj:#.has_key("valueList"):
                    valueList = et.SubElement(AllowedValues, "{%s}valueList" % ns['swe'])
                    valueList.text = ", ".join([ str(a) for a in constraintObj["valueList"] ])
                    #valueList.text = " ".join(constraintObj["valueList"])

                elif "min" in constraintObj:#.has_key("min"):
                    amin = et.SubElement(AllowedValues, "{%s}min" % ns['swe'])
                    amin.text = str(constraintObj["min"])

                elif "max" in constraintObj:#.has_key("max"):
                    amax = et.SubElement(AllowedValues, "{%s}max" % ns['swe'])
                    amax.text = str(constraintObj["max"])

            except Exception:
                raise Exception("Constraint definition invalid in the database for %s" % field["def_opr"])

    #verify that gml_id does not contain blanks
    #(workaround to be corrected in future name sensor registration)
#    ------------------------------------------
#    NCName stands for "non-colonized name".
#    NCName can be defined as an XML Schema regular expression [\i-[:]][\c-[:]]*
#
#    So in plain English it would mean "any initial character, but not :".
#    The whole regular expression reads as "One initial XML name character,
#    but not a colon, followed by zero or more XML name characters, but not a colon."
#
#    The practical restrictions of NCName are that it cannot contain several symbol characters
#    ------------------------------------------

    not_allowed_NCName = [' ', '!','"', '#', '$', '%', '&', '\'',
                          '(', ')', '*', '+', ',', '/', ':', ';',
                          '<', '=', '>', '?', '@', '[', '\\', ']',
                          '^', '`', '{', '|', '}', '~']

    location = tree.find("{%s}member/{%s}System/{%s}location" % (
        ns['sml'],
        ns['sml'],
        ns['sml']))

    for feature in location:
        for ch in not_allowed_NCName:
            if ch in feature.attrib['{%s}id' % ns['gml']]:
                feature.attrib['{%s}id' % ns['gml']] = feature.attrib['{%s}id' %ns['gml']].replace(ch,"_")

        # An underscore is added to be OGC compliant
        #   -> WALIB remove this underscore !!
        #   @TODO: think something better
        if not sosConfig.urn["feature"] in feature.attrib['{%s}id' % ns['gml']]:
            feature.attrib['{%s}id' % ns['gml']] = "loc_%s" % (
                feature.attrib['{%s}id' % ns['gml']])

    # The unique identifier in the response document matches the procedure specified in the request
    system = tree.find("{%s}member/{%s}System" %(ns['sml'],ns['sml']))
    identification = tree.find("{%s}member/{%s}System/{%s}identification" %(ns['sml'],ns['sml'],ns['sml']))

    if identification is None:
        identification = et.Element("{%s}identification" % ns["sml"])
        identifierList = et.SubElement(identification, "{%s}IdentifierList" % ns["sml"])
        identifier = et.SubElement(identifierList, "{%s}identifier" % ns["sml"])
        term = et.SubElement(identifier, "{%s}Term" % ns["sml"])
        term.attrib['definition'] = "urn:ogc:def:identifier:OGC:uniqueID"
        value = et.SubElement(term, "{%s}value" % ns["sml"])
        value.text = system.attrib['{%s}id' % ns['gml']]
        system.insert(1, identification)

    else:
        identifierList = identification.find("{%s}IdentifierList" % ns["sml"])
        if identifierList is None:
            identifierList = et.SubElement(identification, "{%s}IdentifierList" % ns["sml"])
            identifier = et.SubElement(identifierList, "{%s}identifier" % ns["sml"])
            term = et.SubElement(identifier, "{%s}Term" % ns["sml"])
            term.attrib['definition'] = "urn:ogc:def:identifier:OGC:uniqueID"
            value = et.SubElement(term, "{%s}value" % ns["sml"])
            value.text = system.attrib['{%s}id' % ns['gml']]

        else:
            identifiers = identifierList.findall("{%s}identifier" % ns["sml"])
            unique = False
            for identifier in identifiers:
                if identifier.find("{%s}Term" % ns["sml"]).attrib['definition'] == "urn:ogc:def:identifier:OGC:uniqueID":
                    unique = True
                    break

            if not unique:
                identifier = et.SubElement(identifierList,"{%s}identifier" % ns["sml"])
                term = et.SubElement(identifier,"{%s}Term" % ns["sml"])
                term.attrib['definition'] = "urn:ogc:def:identifier:OGC:uniqueID"
                value = et.SubElement(term,"{%s}value" % ns["sml"])
                value.text = system.attrib['{%s}id' %ns['gml']]

    root = tree.getroot()
    root.attrib["xmlns"]="http://www.opengis.net/sensorML/1.0.1"
    root.attrib["version"]="1.0.1"

    # TODO:
    #  Specifically for IGRAC
    #--- Update well information ---#
    for index, field in enumerate(DS.sensorProperties):
        name = tree.find("{%s}member/{%s}System/{%s}name" % (ns['sml'], ns['sml'], ns['gml']))
        name.text = field['name']

        photo = et.Element("{%s}photo" % ns["gml"])
        if field["photo"]:
            photo.text = field["photo"]
        name.addnext(photo)

        org = et.Element("{%s}OriginatingOrganization" % ns["gml"])
        if field["manager"]:
            org.text = field["manager"]
        photo.addnext(org)

        # Hydrogeology
        hydrogeology = et.Element("{%s}Hydrogeology" % ns["gml"])
        aquifer = et.SubElement(hydrogeology, "{%s}Aquifer" % ns["gml"])
        aquifer_name = et.SubElement(aquifer, "{%s}AquiferName" % ns["gml"])
        if field["aquifer_name"]:
            aquifer_name.text = field["aquifer_name"]
        aquifer_material = et.SubElement(aquifer, "{%s}AquiferMaterial" % ns["gml"])
        if field["aquifer_material"]:
            aquifer_material.text = field["aquifer_material"]
        aquifer_type = et.SubElement(aquifer, "{%s}AquiferType" % ns["gml"])
        if field["aquifer_type"]:
            aquifer_type.text = field["aquifer_type"]
        aquifer_thickness = et.SubElement(aquifer, "{%s}AquiferThickness" % ns["gml"])
        if field["aquifer_thickness"]:
            aquifer_thickness.text = field["aquifer_thickness"]
        confinement = et.SubElement(aquifer, "{%s}Confinement" % ns["gml"])
        if field["confinement"]:
            confinement.text = field["confinement"]
        org.addnext(hydrogeology)

        id = tree.find("{%s}member/{%s}System/{%s}identification/{%s}IdentifierList/{%s}identifier/{%s}Term/{%s}value" % (ns['sml'], ns['sml'], ns['sml'], ns['sml'], ns['sml'], ns['sml'], ns['sml']))
        id.text = field['ggis_uid']
        point = tree.find("{%s}member/{%s}System/{%s}location/{%s}Point" % (ns['sml'], ns['sml'], ns['sml'], ns['gml']))
        point.attrib["{%s}id" % ns['gml']] = field['original_id']
        location = tree.find("{%s}member/{%s}System/{%s}location" % (ns['sml'], ns['sml'], ns['sml']))
        if field['country']:
            country = et.SubElement(location, "{%s}country" % ns["gml"])
            country.text = f"{field['country']}"

        coordinates = tree.find("{%s}member/{%s}System/{%s}location/{%s}Point/{%s}coordinates" % (ns['sml'], ns['sml'], ns['sml'], ns['gml'], ns['gml']))
        # if field['elevation_value']:
        #     coordinates.text = f"{field['longitude']},{field['latitude']},{field['elevation_value']}"
        # else:
        #     coordinates.text = f"{field['longitude']},{field['latitude']}"
        #
        # # TODO: WE COMMENT THIS TO ASK FIRST
        latitude = et.SubElement(coordinates, "{%s}latitude" % ns["gml"])
        latitude.text = f"{field['latitude']}"
        longitude = et.SubElement(coordinates, "{%s}longitude" % ns["gml"])
        longitude.text = f"{field['longitude']}"
        elevation = et.SubElement(coordinates, "{%s}elevation" % ns["gml"])
        value = et.SubElement(elevation, "{%s}value" % ns["gml"])
        value.text = f"{field['elevation_value'] if field['elevation_value'] else ''}"
        unit = et.SubElement(elevation, "{%s}unit" % ns["gml"])
        unit.text = f"{field['elevation_unit'] if field['elevation_unit'] else ''}"

        license = tree.find("{%s}member/{%s}System/{%s}License" % (ns['sml'], ns['sml'], ns['gml']))
        if 'license' in field and field['license']:
            if 'summary' in field and field['summary']:
                el = et.SubElement(license, "{%s}summary" % ns["gml"])
                el.text = f"{field['summary']}"
            el = et.SubElement(license, "{%s}name" % ns["gml"])
            el.text = f"{field['license']}"
            el = et.SubElement(license, "{%s}description" % ns["gml"])
            el.text = f"{field['license_desc']}"

        restriction = tree.find("{%s}member/{%s}System/{%s}Restriction" % (ns['sml'], ns['sml'], ns['gml']))
        if 'restriction_code_type_desc' in field and field['restriction_code_type_desc']:
            el = et.SubElement(restriction, "{%s}description" % ns["gml"])
            el.text = f"{field['restriction_code_type_desc']}"
            el = et.SubElement(restriction, "{%s}other" % ns["gml"])
            el.text = f"{field['constraints_other']}"


    return b'<?xml version="1.0" encoding="UTF-8"?>' + et.tostring(root)


def render_2_0_0(DS,sosConfig):
    # Returning content of the SensorML

    try:
        #---parse xml
        tree, ns = parse_and_get_ns(DS.smlFile)

        # swes:validTime is not mandatory and istSOS does not manage sensor description changes in time

        swes = et.XML("""<?xml version="1.0" encoding="UTF-8"?>
<swes:DescribeSensorResponse xmlns:swes="http://www.opengis.net/swes/2.0" xmlns:xsi="http://www.w3.org/2001/XMLSchema-instance" xmlns:gml="http://www.opengis.net/gml/3.2" xmlns:gml1="http://www.opengis.net/gml" xmlns:swe="http://www.opengis.net/swe/1.0.1" xmlns:xlink="http://www.w3.org/1999/xlink" xsi:schemaLocation="http://www.opengis.net/swes/2.0 http://schemas.opengis.net/swes/2.0/swesDescribeSensor.xsd http://www.opengis.net/gml/3.2 http://schemas.opengis.net/gml/3.2.1/gml.xsd http://www.opengis.net/gml http://schemas.opengis.net/gml/3.1.1/base/gml.xsd http://www.opengis.net/sensorML/1.0.1 http://schemas.opengis.net/sensorML/1.0.1/sensorML.xsd http://www.opengis.net/swe/1.0.1 http://schemas.opengis.net/sweCommon/1.0.1/swe.xsd">
  <swes:procedureDescriptionFormat>http://www.opengis.net/sensorML/1.0.1</swes:procedureDescriptionFormat>
  <swes:description>
    <swes:SensorDescription>
      <swes:data></swes:data>
    </swes:SensorDescription>
  </swes:description>
</swes:DescribeSensorResponse>""")
    except Exception as ex:
        raise Exception("sensorML description for procedure '%s' not found or corrupted! [%s]"%(DS.smlFile,ex))

    mns = {
        'xsi': "http://www.w3.org/2001/XMLSchema-instance" ,
        'sml': "http://www.opengis.net/sensorML/1.0.1",
        'swe': "http://www.opengis.net/swe/1.0.1",
        'xlink': "http://www.w3.org/1999/xlink",
        'gml1':  'http://www.opengis.net/gml',
        'gml':'http://www.opengis.net/gml/3.2',
        'swes': 'http://www.opengis.net/swes/2.0'
    }

    for n in list(mns.keys()):
        try:
            ns[n] = mns[n]
        except:
            ns[n] = mns[n]

    # map namespaces
    try:
        register_namespace = et.register_namespace
        for key in ns:
            register_namespace(key,ns[key])
    except AttributeError:
        try:
            et._namespace_map.update(ns)
            for key in ns:
                et._namespace_map[ns[key]] = key
        except AttributeError:
            try:
                from xml.etree.ElementTree import _namespace_map
            except ImportError:
                try:
                    from elementtree.ElementTree import _namespace_map
                except ImportError:
                    print(("Failed to import ElementTree from any known place"), file=sys.stderr)
            for key in ns:
                _namespace_map[ns[key]] = key

    # CREATE FIELDS ACCORDING TO DATABASE OBSERVED_PROPERTIES
    datarecord = tree.find("{%s}member/{%s}System/{%s}outputs/{%s}OutputList/{%s}output/{%s}DataRecord"
                        %(ns['sml'],ns['sml'],ns['sml'],ns['sml'],ns['sml'],ns['swe']) )


    datarecord.clear()
    datarecord.attrib["definition"] = "%stimeSeries" % (sosConfig.urn['dataType'])
    fieldT = et.SubElement(datarecord,"{%s}field" % ns["swe"])
    fieldT.attrib["name"] = "Time"
    time = et.SubElement(fieldT,"{%s}Time" % ns["swe"])
    time.attrib["definition"] = sosConfig.urn["time"]

    # Adding constraint for current allowed times
    if (not DS.stime == None) and (not DS.etime == None):
        constraint =  et.SubElement(time, "{%s}constraint" % ns['swe'])
        allowedTimes =  et.SubElement(constraint, "{%s}AllowedTimes" % ns['swe'])
        interval = et.SubElement(allowedTimes, "{%s}interval" % ns['swe'])
        interval.text = "%s %s" %(DS.stime.strftime("%Y-%m-%dT%H:%M:%S.%fZ"), DS.etime.strftime("%Y-%m-%dT%H:%M:%S.%fZ"))

    if DS.procedureType=="insitu-mobile-point": # Adding 3d coordinates observation

        cord = et.SubElement(datarecord,"{%s}field" % ns["swe"])
        cord.attrib["name"] = "x"
        quantity = et.SubElement(cord,"{%s}Quantity" % ns["swe"])
        quantity.attrib["definition"] = sosConfig.urn["refsystem"] + sosConfig.istsosepsg + ":x-position"

        cord = et.SubElement(datarecord,"{%s}field" % ns["swe"])
        cord.attrib["name"] = "y"
        quantity = et.SubElement(cord,"{%s}Quantity" % ns["swe"])
        quantity.attrib["definition"] = sosConfig.urn["refsystem"] + sosConfig.istsosepsg + ":y-position"

        cord = et.SubElement(datarecord,"{%s}field" % ns["swe"])
        cord.attrib["name"] = "z"
        quantity = et.SubElement(cord,"{%s}Quantity" % ns["swe"])
        quantity.attrib["definition"] = sosConfig.urn["refsystem"] + sosConfig.istsosepsg + ":z-position"


    for index, field in enumerate(DS.observedProperties):

        fieldQ = et.SubElement(datarecord,"{%s}field" % ns["swe"])
        fieldQ.attrib["name"] = field["name_opr"]
        quantity = et.SubElement(fieldQ,"{%s}Quantity" % ns["swe"])
        quantity.attrib["definition"] = field["def_opr"]

        if not (field["name_uom"]=="" or field["name_uom"]==None or field["name_uom"]=="NULL"):
            uom = et.SubElement(quantity,"{%s}uom" % ns["swe"])
            uom.attrib["code"] = field["name_uom"]
        """
        if not (field["desc_opr"]=="" or field["desc_opr"]==None or field["desc_opr"]=="NULL"):
            description = et.SubElement(quantity,"{%s}description" % ns["swe"])
            description.text = field["desc_opr"]
        """

        """
        # Handling constraint
        Permitted conigurations:
            {"role":"urn:ogc:def:classifiers:x-istsos:1.0:qualityIndex:check:reasonable","min":"10"}
            {"role":"urn:ogc:def:classifiers:x-istsos:1.0:qualityIndex:check:reasonable","max":"10"}
            {"role":"urn:ogc:def:classifiers:x-istsos:1.0:qualityIndex:check:reasonable","interval":["-10","10"]}
            {"role":"urn:ogc:def:classifiers:x-istsos:1.0:qualityIndex:check:reasonable","valueList":["1","2","3","4","5","6"]}
        """
        if not (field["constr_pro"]=="" or field["constr_pro"]==None):
            try:
                constraintObj = json.loads(field["constr_pro"])

                constraint = et.SubElement(quantity,"{%s}constraint" % ns["swe"])

                # Role attribute is not mandatory
                if "role" in constraintObj and constraintObj["role"]!="" and constraintObj["role"]!=None:
                    constraint.attrib[ "{%s}role" % ns['xlink'] ]= constraintObj["role"]

                AllowedValues = et.SubElement(constraint, "{%s}AllowedValues" % ns['swe'])

                # Factory on constraint min/max/interval/valuelist
                if "interval" in constraintObj:
                    interval = et.SubElement(AllowedValues, "{%s}interval" % ns['swe'])
                    interval.text = " ".join([ str(a) for a in constraintObj["interval"] ])
                    #interval.text = " ".join(constraintObj["interval"])

                elif "valueList" in constraintObj:#.has_key("valueList"):
                    valueList = et.SubElement(AllowedValues, "{%s}valueList" % ns['swe'])
                    valueList.text = ", ".join([ str(a) for a in constraintObj["valueList"] ])
                    #valueList.text = " ".join(constraintObj["valueList"])

                elif "min" in constraintObj:#.has_key("min"):
                    amin = et.SubElement(AllowedValues, "{%s}min" % ns['swe'])
                    amin.text = str(constraintObj["min"])

                elif "max" in constraintObj:#.has_key("max"):
                    amax = et.SubElement(AllowedValues, "{%s}max" % ns['swe'])
                    amax.text = str(constraintObj["max"])

            except Exception:
                raise Exception("Constraint definition invalid in the database for %s" % field["def_opr"])

    #verify that gml_id does not contain blanks
    #(workaround to be corrected in future name sensor registration)
    #    ------------------------------------------
    #    NCName stands for "non-colonized name".
    #    NCName can be defined as an XML Schema regular expression [\i-[:]][\c-[:]]*
    #
    #    So in plain English it would mean "any initial character, but not :".
    #    The whole regular expression reads as "One initial XML name character,
    #    but not a colon, followed by zero or more XML name characters, but not a colon."
    #
    #    The practical restrictions of NCName are that it cannot contain several symbol characters
    #    ------------------------------------------

    not_allowed_NCName = [' ', '!','"', '#', '$', '%', '&', '\'',
                          '(', ')', '*', '+', ',', '/', ':', ';',
                          '<', '=', '>', '?', '@', '[', '\\', ']',
                          '^', '`', '{', '|', '}', '~']

    location = tree.find("{%s}member/{%s}System/{%s}location" % (ns['sml'], ns['sml'], ns['sml']) )

    for feature in location:
        for ch in not_allowed_NCName:
            if ch in feature.attrib['{%s}id' %ns['gml1']]:
                feature.attrib['{%s}id' %ns['gml1']] = feature.attrib['{%s}id' %ns['gml1']].replace(ch,"_")

    # The unique identifier in the response document matches the procedure specified in the request
    system = tree.find("{%s}member/{%s}System" %(ns['sml'],ns['sml']))
    identification = tree.find("{%s}member/{%s}System/{%s}identification" %(ns['sml'],ns['sml'],ns['sml']))

    if not identification:
        identification = et.Element("{%s}identification" % ns["sml"])
        identifierList = et.SubElement(identification,"{%s}IdentifierList" % ns["sml"])
        identifier = et.SubElement(identifierList,"{%s}identifier" % ns["sml"])
        term = et.SubElement(identifier,"{%s}Term" % ns["sml"])
        term.attrib['definition'] = "urn:ogc:def:identifier:OGC:uniqueID"
        value = et.SubElement(term,"{%s}value" % ns["sml"])
        value.text = sosConfig.urn["procedure"]+system.attrib['{%s}id' %ns['gml1']]
        system.insert(1,identification)
    else:
        identifierList = identification.find("{%s}IdentifierList" % ns["sml"])
        if not identifierList:
            identifierList = et.SubElement(identification,"{%s}IdentifierList" % ns["sml"])
            identifier = et.SubElement(identifierList,"{%s}identifier" % ns["sml"])
            term = et.SubElement(identifier,"{%s}Term" % ns["sml"])
            term.attrib['definition'] = "urn:ogc:def:identifier:OGC:uniqueID"
            value = et.SubElement(term,"{%s}value" % ns["sml"])
            value.text = sosConfig.urn["procedure"]+system.attrib['{%s}id' %ns['gml1']]
#            system.insert(1,identification)
        else:
            identifiers = identifierList.findall("{%s}identifier" % ns["sml"])
            unique = False
            for identifier in identifiers:
                if identifier.find("{%s}Term" % ns["sml"]).attrib['definition'] == "urn:ogc:def:identifier:OGC:uniqueID":
                    unique = True
                    break
            if not unique:
                identifier = et.SubElement(identifierList,"{%s}identifier" % ns["sml"])
                term = et.SubElement(identifier,"{%s}Term" % ns["sml"])
                term.attrib['definition'] = "urn:ogc:def:identifier:OGC:uniqueID"
                value = et.SubElement(term,"{%s}value" % ns["sml"])
                value.text = sosConfig.urn["procedure"]+system.attrib['{%s}id' %ns['gml1']]
#                system.insert(1,identification)

    root = tree.getroot()

    data = swes.find("{%s}description/{%s}SensorDescription/{%s}data" % (ns['swes'], ns['swes'], ns['swes']) )
    data.append(root)

    #swes.attrib["xmlns"]="http://www.opengis.net/swes/2.0"
    return b'<?xml version="1.0" encoding="UTF-8"?>' + et.tostring(swes)
