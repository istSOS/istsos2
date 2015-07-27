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
import sys, traceback
import json
from lib.etree import et
from walib import utils as ut

reurl = r'(http|ftp|https):\/\/[\w\-_]+(\.[\w\-_]+)+([\w\-\.,@?^=%&amp;:/~\+#]*[\w\-\@?^=%&amp;/~\+#])?'

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


class Procedure():
    def __init__(self, serviceconf=None):
        """
        Create the the self.data object representing the istSOS SensorML
        """
        self.data = {}
        self.serviceconf = serviceconf
    
    def loadJSON(self, describeSensorObj):
        """
        Create the the self.data object representing the istSOS SensorML from a json elemet
        
        @param json: a json describeSensor object
        """
        self.data = json.loads(describeSensorObj)

    
    def loadDICT(self, describeSensorObj):
        """
        Create the the self.data object representing the istSOS SensorML from a json elemet
        
        @param json: a json describeSensor object
        """
        self.data = describeSensorObj
        
    def loadXML(self, xml):
        """
        Create the the self.data object representing the istSOS SensorML from an XML elemet
        
        @param json: a json describeSensor object (xml string or xml file full path)
        """
        if type(xml)==type("ciao"):
            from os import path
            if path.isfile(xml):
                tree, ns = parse_and_get_ns(xml)
            else:
                from StringIO import StringIO
                tree, ns = parse_and_get_ns(StringIO(xml))
        else:
            raise TypeError("xml input must be a string representing the XML itself or the path to the file where the XML is stored")
            #tree, ns = parse_and_get_ns(xml)
        
        # Workaround for rare xml parsing bug in etree
        ns = {
            'swe': 'http://www.opengis.net/swe/1.0.1',
            'gml': 'http://www.opengis.net/gml',
            'sml': 'http://www.opengis.net/sensorML/1.0.1',
            'xlink': 'http://www.w3.org/1999/xlink',
            'xsi': 'http://www.w3.org/2001/XMLSchema-instance'
        }
        
        #-----System name/identifier------
        system = tree.find("{%s}member/{%s}System" %(ns['sml'],ns['sml']) )
        try:
            self.data['system_id'] = system.attrib[ "{%s}id" % ns['gml'] ]
        except Exception as e:
            raise SyntaxError("Error in <sml:member>: <sml:System> element or mandatory attribute are missing")
        
        systemname = tree.find("{%s}member/{%s}System/{%s}name" %(ns['sml'],ns['sml'],ns['gml']) )
        try:
            self.data['system'] = systemname.text.strip()
        except:
            raise SyntaxError("Error in <sml:System>: <sml:name> element is missing")
        
        
        #-----System description------
        desc = tree.find("{%s}member/{%s}System/{%s}description" %(ns['sml'],ns['sml'],ns['gml']) )
        try:
            self.data['description'] = desc.text.strip()
        except:
            self.data['description'] = ""
        
        #-----System Search Keywords------
        keys = tree.findall("{%s}member/{%s}System/{%s}keywords/{%s}KeywordList/{%s}keyword" %((ns['sml'],)*5))
        try:
            self.data['keywords'] = ",".join([key.text.strip() for key in keys])
        except:
            self.data['keywords'] = ""
        
        #-----System Classifiers------
        self.data['identification'] = []
        idents = tree.findall("{%s}member/{%s}System/{%s}identification/{%s}IdentifierList/{%s}identifier" %((ns['sml'],)*5))
        for ident in idents:
            try:
                defin = ident.find('{%s}Term' % ns['sml']).attrib['definition']
                item={}
                item["name"] = defin.split(':')[-1]
                item["definition"] = defin
                item["value"] = ident.find('{%s}Term/{%s}value' %(ns['sml'],ns['sml'])).text.strip()
                self.data['identification'].append(item)
            except:
                raise SyntaxError("Error in <swe:identification>: some <sml:identifier> mandatory sub elements or attributes are missing")
        
        #-----System Identifiers------
        self.data["classification"] = []
        man=[False,False]
        classifiers = tree.findall("{%s}member/{%s}System/{%s}classification/{%s}ClassifierList/{%s}classifier" %((ns['sml'],)*5))
        for classifier in classifiers:
            try:
                item={}
                item["name"] = classifier.attrib['name']
                item["definition"] = classifier.find('{%s}Term' % ns['sml']).attrib['definition']
                item["value"] = classifier.find('{%s}Term/{%s}value' %(ns['sml'],ns['sml'])).text.strip()
                self.data['classification'].append(item)
                if item["name"] == "System Type":
                    man[0]=True
                elif item["name"] == "Sensor Type":
                    man[1]=True
            except:
                raise SyntaxError("Error in <swe:classification>: some <sml:classifier> mandatory sub elements or attributes are missing")
        if not man==[True,True]:
            raise SyntaxError("Error in <sml:ClassifierList>: 'System Type' and 'Sensor Type' classifiers are both mandatory")
        
        #-----System Characteristics------
        try:
            self.data["characteristics"] = tree.find("{%s}member/{%s}System/{%s}characteristics" %((ns['sml'],)*3)).attrib[ "{%s}href" % ns['xlink'] ]
        except:
            self.data["characteristics"] = ""
        
        #-----System Capabilities------
        self.data["capabilities"] = []
        fields = tree.findall("{%s}member/{%s}System/{%s}capabilities/{%s}DataRecord/{%s}field" %(ns['sml'],ns['sml'],ns['sml'],ns['swe'],ns['swe']))
        man=[False,False]
        for field in fields:
            try:
                item={}
                item["name"] = field.attrib['name']
                fieldchield = field.find('{%s}Quantity' % ns['swe'])
                if fieldchield == None:
                    fieldchield = field.find('{%s}Category' % ns['swe'])
                item["definition"] = fieldchield.attrib['definition']
                
                uom = fieldchield.find('{%s}uom' % ns['swe'] )
                value = fieldchield.find('{%s}value' % ns['swe'] )
                
                if uom != None and value != None:
                    item["uom"] = uom.attrib['code']
                    item["value"] = value.text.strip()
                
                self.data['capabilities'].append(item)
                if item["name"] == 'Sampling time resolution':
                    man[0]=True
                elif item["name"] == 'Acquisition time resolution':
                    man[1]=True
            except:
                raise SyntaxError("Error in <swe:capabilities>: some <swe:field> mandatory sub elements or attributes are missing")
        #if not man==[True,True]:
        #    raise SyntaxError("Error in <sml:capabilities>: 'Sampling time resolution' and 'Acquisition time resolution' fields are both mandatory")
        
        #-----Relevant Contacts------
        self.data["contacts"] = []
        contacts = tree.findall("{%s}member/{%s}System/{%s}contact" %((ns['sml'],)*3))
        for contact in contacts:
            try:
                item={}
                item["role"] = contact.attrib["{%s}role"  % ns['xlink']]
                cont = contact.find("{%s}ResponsibleParty" % ns['sml'])
                item["organizationName"] = cont.find("{%s}organizationName" % ns['sml']).text.strip()
                try:
                    item["individualName"] = cont.find("{%s}individualName" % ns['sml']).text.strip()
                except:
                    item["individualName"] = ""
                try:
                    item["voice"] = cont.find("{%s}contactInfo/{%s}phone/{%s}voice" %((ns['sml'],)*3)).text.strip()
                except:
                    item["voice"] = ""   
                try:
                    item["fax"] = cont.find("{%s}contactInfo/{%s}phone/{%s}facsimile" %((ns['sml'],)*3)).text.strip()
                except:
                    item["fax"] = "" 
                try:
                    item["deliveryPoint"] = cont.find("{%s}contactInfo/{%s}address/{%s}deliveryPoint" %((ns['sml'],)*3)).text.strip()
                except:
                    item["deliveryPoint"] = ""
                try:
                    item["city"] = cont.find("{%s}contactInfo/{%s}address/{%s}city" %((ns['sml'],)*3)).text.strip()
                except:
                    item["city"] = ""
                try:
                    item["administrativeArea"] = cont.find("{%s}contactInfo/{%s}address/{%s}administrativeArea" %((ns['sml'],)*3)).text.strip()
                except:
                    item["administrativeArea"] = ""
                try:
                    item["postalcode"] = cont.find("{%s}contactInfo/{%s}address/{%s}postalCode" %((ns['sml'],)*3)).text.strip()
                except:
                    item["postalcode"] = ""
                try:
                    item["country"] = cont.find("{%s}contactInfo/{%s}address/{%s}country" %((ns['sml'],)*3)).text.strip()
                except:
                    item["country"] = ""
                try:
                    item["email"] = cont.find("{%s}contactInfo/{%s}address/{%s}electronicMailAddress" %((ns['sml'],)*3)).text.strip()
                except:
                    item["email"] = ""
                try:
                    item["web"] = cont.find("{%s}contactInfo/{%s}onlineResource" %((ns['sml'],)*2)).attrib["{%s}href" % ns['xlink']]
                except:
                    item["web"] = ""
                self.data["contacts"].append(item)
            except Exception as e:
                print "ECCEZIONE: "
                print str(e)
                raise SyntaxError("Error in <swe:contact>: some <swe:contact> mandatory sub elements or attributes are missing")
            
        
        #-----System Documentation------            
        self.data["documentation"] = []
        documents = tree.findall("{%s}member/{%s}System/{%s}documentation/{%s}Document" %((ns['sml'],)*4))
        for doc in documents:
            try:
                item = {}
                item["description"] = doc.find("{%s}description" % ns['gml']).text.strip()
                item["link"] = doc.find("{%s}onlineResource" % ns['sml']).attrib["{%s}href" % ns['xlink'] ]
                try:
                    item["date"] = doc.find("{%s}date" % ns['sml']).text.strip()
                except:
                    item["date"] = ""
                try:
                    item["format"] = doc.find("{%s}format" % ns['sml']).text.strip()
                except:
                    item["format"] = ""
                    
                self.data["documentation"].append(item)
                
            except:
                raise SyntaxError("Error in <swe:documentation>: some <swe:Document> mandatory sub elements or attributes are missing")
                
        #-----System Location------            
        point = tree.find("{%s}member/{%s}System/{%s}location/{%s}Point" %(ns['sml'],ns['sml'],ns['sml'],ns['gml']) )
        coord = tree.find("{%s}member/{%s}System/{%s}location/{%s}Point/{%s}coordinates" %(ns['sml'],ns['sml'],ns['sml'],ns['gml'],ns['gml']))
        
        try:
            coordlist = [ i for i in coord.text.strip().split(",")]
            self.data["location"] = {}
            self.data["location"]["type"] = "Feature"
            self.data["location"]["geometry"] = {}
            self.data["location"]["geometry"]["type"] = "Point"
            self.data["location"]["geometry"]["coordinates"] = coordlist
            self.data["location"]["crs"] = {}
            self.data["location"]["crs"]["type"] = "name"
            self.data["location"]["crs"]["properties"] = {}
            self.data["location"]["crs"]["properties"]["name"] = point.attrib["srsName"]
            self.data["location"]["properties"] = {}
            self.data["location"]["properties"]["name"] = point.attrib["{%s}id" % ns['gml'] ]
        except:
            raise SyntaxError("Error in <swe:location>: some mandatory <gml:Point> sub elements or attributes are missing")
            
        
        #-----System Interfaces------
        interfaces = tree.findall("{%s}member/{%s}System/{%s}interfaces/{%s}InterfaceList/{%s}interface" %((ns['sml'],)*5))
        try:
            self.data["interfaces"] = ",".join([ interface.attrib["name"] for interface in interfaces ])
        except:
            raise SyntaxError("Error in <swe:interfaces>: some mandatory sub elements or attributes are missing")
        
        #-----System Inputs------
        inputs = tree.findall("{%s}member/{%s}System/{%s}inputs/{%s}InputList/{%s}input" %((ns['sml'],)*5))
        self.data["inputs"] = []
        for inp in inputs:
            try:
                item = {}
                item["name"] = inp.attrib["name"]
                item["definition"] = inp.find("{%s}Quantity" % ns['swe']).attrib["definition"]
                try:
                    item["description"] = inp.find("{%s}Quantity/{%s}description" %(ns['swe'],ns['gml'])).text.strip()
                except:
                    item["description"] = ""
                self.data["inputs"].append(item)
            except:
                raise SyntaxError("Error in <swe:inputs>: some <swe:input> mandatory sub elements or attributes are missing")
                
            
        #-----System Outputs------
        outputs = tree.findall("{%s}member/{%s}System/{%s}outputs/{%s}OutputList/{%s}output/{%s}DataRecord/{%s}field" 
                                %( (ns['sml'],)*5 + (ns['swe'],)*2) )
        self.data["outputs"] = []
        time = False
        for out in outputs:
            try:
                item={}
                item["name"] = out.attrib["name"]
                if out.attrib["name"] == "Time":
                    time = True
                    child = out.find("{%s}Time" % ns['swe'] )
                    allow = child.find("{%s}constraint/{%s}AllowedTimes" %(ns['swe'],ns['swe']))
                else:
                    child =  out.find("{%s}Quantity" % ns['swe'] )
                    allow = child.find("{%s}constraint/{%s}AllowedValues" %(ns['swe'],ns['swe']))  
                item["definition"] = child.attrib["definition"]
                try:
                    item["description"] = child.find("{%s}description" % ns['gml']).text.strip()
                except:
                    item["description"] = ""
                    
                try:
                    item["uom"] = child.find("{%s}uom" % ns['swe']).attrib["code"]
                except:
                    item["uom"] = ""
                
                
                if allow:
                
                    item["constraint"] = {}
                     
                    try:
                        item["constraint"]["role"] = child.find("{%s}constraint" % ns['swe']).attrib["{%s}role" % ns['xlink']]
                    except:
                        pass
    
                    try:
                        item["constraint"]["min"] = allow.find("{%s}min" % ns['swe']).text.strip()
                    except:
                        pass #item["constraint"]["min"] = ""
    
                    try:
                        item["constraint"]["max"] = allow.find("{%s}max" % ns['swe']).text.strip()
                    except:
                        pass #item["constraint"]["max"] = ""
    
                    try:
                        item["constraint"]["interval"] = allow.find("{%s}interval" % ns['swe']).text.strip().split(" ")
                    except:
                        pass #item["constraint"]["interval"] = ""
                    
                    try:
                        item["constraint"]["valuelist"] = allow.find("{%s}valueList" % ns['swe']).text.strip().split(" ")
                    except:
                        pass #item["constraint"]["valuelist"] = ""
                
                self.data["outputs"].append(item)
                
            except Exception as ex:
                print >> sys.stderr, traceback.print_exc()
                raise SyntaxError("Error in <sml:outputs>: some <swe:field> mandatory sub elements or attributes are missing")
        if time==False:
            raise SyntaxError("Error in <sml:outputs>: <swe:Time> is mandatory")

        #-----System History------
        events = tree.findall("{%s}member/{%s}System/{%s}history/{%s}EventList/{%s}member" %( (ns['sml'],)*5 ) )
        self.data["history"] = []
        for event in events:
            try:
                item = {}
                item["type"] = event.attrib["name"]
                item["date"] = event.find("{%s}Event/{%s}date" %((ns['sml'],)*2) ).text.strip()
                try:
                    item["description"] = event.find("{%s}Event/{%s}description" %(ns['sml'],ns['gml']) ).text.strip()
                except:
                    item["description"] = ""
                item["reference"] = {}
                item["reference"]["username"] = event.find("{%s}Event/{%s}contact" %((ns['sml'],)*2) ).attrib["{%s}href" % ns['xlink']]
                item["reference"]["role"] = event.find("{%s}Event/{%s}contact" %((ns['sml'],)*2) ).attrib["{%s}arcrole" % ns['xlink']]
                self.data["history"].append(item)
            except:
                raise SyntaxError("Error in <sml:history>: some <sml:member> mandatory sub elements or attributes are missing")
        
        
    def toJSON(self):
        """
        Return the Json that represent the self.data object as L{string}
        """
        return json.dumps(self.data, ensure_ascii=False)
        
    def toXML(self,indent=False):
        """
        Return the SensorML that represent the self.data object as L{string}
        """
        import sys
        ns = {
            'xsi': "http://www.w3.org/2001/XMLSchema-instance" ,
            'sml': "http://www.opengis.net/sensorML/1.0.1", 
            'swe': "http://www.opengis.net/swe/1.0.1", 
            'xlink': "http://www.w3.org/1999/xlink", 
            'gml': 'http://www.opengis.net/gml'            
        }
           
        #---map namespaces---
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
                        print >> sys.stderr, ("Failed to import ElementTree from any known place")
                for key in ns:
                    _namespace_map[ns[key]] = key
        
        root = et.Element("{%s}SensorML" % ns['sml'])
        root.attrib[ "{%s}schemaLocation" % ns['xsi'] ] = "http://www.opengis.net/sensorML/1.0.1 http://schemas.opengis.net/sensorML/1.0.1/sensorML.xsd"
        root.attrib["version"] = "1.0"
                   
        member = et.SubElement(root, "{%s}member" % ns['sml'] )
        
        system = et.SubElement(member, "{%s}System" % ns['sml'] )
        system.attrib["{%s}id" % ns['gml'] ] = self.data["system_id"]

        #--- System Description
        system.append(et.Comment("System Description"))        
        
        if ("keywords" in self.data) and (not self.data["description"]==""):
            desc = et.SubElement(system, "{%s}description" % ns['gml'] )
            desc.text = self.data["description"]
        
        name = et.SubElement(system, "{%s}name" % ns['gml'] )
        name.text = self.data["system"]
        
        #--- System Search Keywords
        if ("keywords" in self.data) and (not self.data["keywords"]==""):
            system.append(et.Comment("System Search Keywords"))
            keys = et.SubElement(system, "{%s}keywords" % ns['sml'] )
            keylist = et.SubElement(keys, "{%s}KeywordList" % ns['sml'] )
            for k in self.data["keywords"].split(","):
                key = et.SubElement(keylist, "{%s}keyword" % ns['sml'] )
                key.text = k
        
        #--- System Identifiers
        if ("identification" in self.data) and (not self.data["identification"]==[]):
            system.append(et.Comment("System Identifiers"))
            identification = et.SubElement(system, "{%s}identification" % ns['sml'] )
            IdentifierList = et.SubElement(identification, "{%s}IdentifierList" % ns['sml'] )
            uniqueidPresent = False
            for i in  self.data["identification"]:
                if i["definition"] == 'urn:ogc:def:identifier:OGC:uniqueID':
                    uniqueidPresent = True
                identifier = et.SubElement(IdentifierList, "{%s}identifier" % ns['sml'] )
                identifier.attrib["name"] = i["name"]
                term = et.SubElement(identifier, "{%s}Term" % ns['sml'] )
                term.attrib["definition"] = i["definition"]
                value = et.SubElement(term, "{%s}value" % ns['sml'])
                value.text = i["value"]
            if not uniqueidPresent:
                raise Exception("self.data['identification']: 'uniqueID' is mandatory")
        
        #--- System Classifiers
        system.append(et.Comment("System Classifiers"))
        classification = et.SubElement(system, "{%s}classification" % ns['sml'] )
        ClassifierList = et.SubElement(classification, "{%s}ClassifierList" % ns['sml'])
        for c in self.data["classification"]:
            classifier = et.SubElement(ClassifierList, "{%s}classifier" % ns['sml'] )
            classifier.attrib["name"] = c["name"]
            term = et.SubElement(classifier, "{%s}Term" % ns['sml'] )
            term.attrib["definition"] = c["definition"]
            value = et.SubElement(term, "{%s}value" % ns['sml'] )
            value.text = c["value"]
            if c["name"]=="System Type":
                systype = True
            elif c["name"]=="Sensor Type":
                senstype = True
        if not systype == True and senstype == True:
            raise Exception("self.data['classification']: 'System Type' and 'Sensor Type' are mandatory")
        
        #--- System Characteristics 
        if ("characteristics" in self.data) and ( not self.data["characteristics"] == ""):
            system.append(et.Comment("System Characteristics"))
            characteristics = et.SubElement(system, "{%s}characteristics" % ns['sml'])
            characteristics.attrib[ "{%s}href" % ns['xlink'] ] = self.data["characteristics"]
        
        #--- System Capabilities 
        system.append(et.Comment("System Capabilities"))
        capabilities = et.SubElement(system, "{%s}capabilities" % ns['sml'])
        DataRecord = et.SubElement(capabilities, "{%s}DataRecord" % ns['swe'])
        stres = False
        atres = False
        for f in self.data["capabilities"]:
            field = et.SubElement(DataRecord, "{%s}field" % ns['swe'])
            field.attrib[ "name" ] =f["name"]
            Quantity = et.SubElement(field, "{%s}Quantity" % ns['swe'])
            Quantity.attrib[ "definition" ] =f["definition"]
            if "uom" in f and "value" in f :
                uom = et.SubElement(Quantity, "{%s}uom" % ns['swe'])
                uom.attrib[ "code" ] =f["uom"]
                value = et.SubElement(Quantity, "{%s}value" % ns['swe'])
                value.text =f["value"]
            if c["name"]=="Sampling time resolution":
                stres = True
            elif c["name"]=="Acquisition time resolution":
                atres = True
        if not stres == True and atres == True:
            raise Exception("self.data['capabilities']: 'Sampling time resolution' and 'Acquisition time resolution' are mandatory")
        
        #--- Relevant Contacts 
        if  ("contacts" in self.data) and (not self.data["contacts"] == []):
            system.append(et.Comment("Relevant Contacts"))
            for c in self.data["contacts"]:
                contact = et.SubElement(system, "{%s}contact" % ns['sml'])
                contact.attrib["{%s}role" % ns['xlink']] = c["role"]
                ResponsibleParty = et.SubElement(contact, "{%s}ResponsibleParty" % ns['sml'])
                if not c["individualName"] == "":
                    individualName = et.SubElement(ResponsibleParty, "{%s}individualName" % ns['sml'])
                    individualName.text = c["individualName"]
                organizationName = et.SubElement(ResponsibleParty, "{%s}organizationName" % ns['sml'])
                organizationName.text = c["organizationName"]
                phonetag = not c["voice"] == c["fax"] == ""
                addresstag = not c["deliveryPoint"] == c["city"] == c["administrativeArea"] == c["postalcode"] == c["country"] == c["email"] == ""
                onlineResourcetag = not c["web"] == ""
                if not phonetag == addresstag == onlineResourcetag == False:
                    contactInfo = et.SubElement(ResponsibleParty, "{%s}contactInfo" % ns['sml'])
                    if not phonetag==False:
                        phone = et.SubElement(contactInfo, "{%s}phone" % ns['sml'])
                        if not c["voice"] == "":
                            voice = et.SubElement(phone, "{%s}voice" % ns['sml'])
                            voice.text = c["voice"]
                        if not c["fax"] == "":
                            facsimile = et.SubElement(phone, "{%s}facsimile" % ns['sml'])
                            facsimile.text = c["fax"]
                    if not addresstag==False:
                        address = et.SubElement(contactInfo, "{%s}address" % ns['sml'])
                        if not c["deliveryPoint"] == "":
                            deliveryPoint = et.SubElement(address, "{%s}deliveryPoint" % ns['sml'])
                            deliveryPoint.text = c["deliveryPoint"]
                        if not c["city"] == "":
                            city = et.SubElement(address, "{%s}city" % ns['sml'])
                            city.text = c["city"]
                        if not c["administrativeArea"] == "":
                            administrativeArea = et.SubElement(address, "{%s}administrativeArea" % ns['sml'])
                            administrativeArea.text = c["administrativeArea"]
                        if not c["postalcode"] == "":
                            postalCode = et.SubElement(address, "{%s}postalCode" % ns['sml'])
                            postalCode.text = c["postalcode"]
                        if not c["country"] == "":
                            country = et.SubElement(address, "{%s}country" % ns['sml'])
                            country.text = c["country"]
                        if not c["email"] == "":
                            electronicMailAddress = et.SubElement(address, "{%s}electronicMailAddress" % ns['sml'])
                            electronicMailAddress.text = c["email"]
                    if not onlineResourcetag==False:
                        onlineResource = et.SubElement(contactInfo, "{%s}onlineResource" % ns['sml'])
                        onlineResource.attrib["{%s}href" % ns['xlink'] ] = c["web"]
                        
        #--- System Documentation 
        if ("documentation" in self.data) and (not self.data["documentation"] == []):
            system.append(et.Comment("System Documentation"))
            for d in self.data["documentation"]:
                documentation = et.SubElement(system, "{%s}documentation" % ns['sml'])
                Document = et.SubElement(documentation, "{%s}Document" % ns['sml'])
                description = et.SubElement(Document, "{%s}description" % ns['gml'])
                description.text = d["description"]
                if not d["date"]=="":
                    date = et.SubElement(Document, "{%s}date" % ns['sml'])
                    date.text = d["date"]
                if not d["format"]=="":
                    format = et.SubElement(Document, "{%s}format" % ns['sml'])
                    format.text = d["format"]    
                onlineResource = et.SubElement(Document, "{%s}onlineResource" % ns['sml'])
                onlineResource.attrib["{%s}href" % ns['xlink'] ] = d["link"]
        
        #--- System Location
        system.append(et.Comment("System Location"))
        location = et.SubElement(system, "{%s}location" % ns['sml'])
        for item in self.data["classification"]:
            if item["name"] == "System Type":
                if item["value"].find("mobile")>0:
                    location.attrib[ "{%s}role" % ns['xlink'] ] = "urn:ogc:def:dataType:x-istsos:1.0:lastPosition"
        Point = et.SubElement(location, "{%s}Point" % ns['gml'])

        if ut.valid_NCName(self.data["location"]["properties"]["name"]):
            Point.attrib[ "{%s}id" % ns['gml'] ] = self.data["location"]["properties"]["name"]
        else:
            raise Exception ("Invalid location name '%s' (gml:id only allows alphanumeric characters)" % self.data["location"]["properties"]["name"])
        Point.attrib[ "srsName" ] = "EPSG:"+str(self.data["location"]["crs"]["properties"]["name"])
        coordinates = et.SubElement(Point, "{%s}coordinates" % ns['gml'])
        coordinates.text = ",".join([ str(a) for a in self.data["location"]["geometry"]["coordinates"] ])
        
        #--- System Interfaces
        if ("interfaces" in self.data) and (not self.data["interfaces"]==""):
            system.append(et.Comment("System Interfaces"))
            interfaces = et.SubElement(system, "{%s}interfaces" % ns['sml'])
            InterfaceList = et.SubElement(interfaces, "{%s}InterfaceList" % ns['sml'])
            for i in self.data["interfaces"].split(","):
                interface = et.SubElement(InterfaceList, "{%s}interface" % ns['sml'])
                interface.attrib["name"] = i
        
        #--- System Inputs # Not yet supported in waAdmin !!
        if ("inputs" in self.data) and (not self.data["inputs"]==[]):
            system.append(et.Comment("System Inputs"))
            inputs = et.SubElement(system, "{%s}inputs" % ns['sml'])
            InputList = et.SubElement(inputs, "{%s}InputList" % ns['sml'])
            for inp in self.data["inputs"]:
                inputml = et.SubElement(InputList, "{%s}input" % ns['sml'])
                inputml.attrib["name"] = inp["name"]
                Quantity = et.SubElement(inputml, "{%s}Quantity" % ns['swe'])
                Quantity.attrib["definition"] = inp["definition"]
                if not inp["description"]=="":
                    description = et.SubElement(Quantity, "{%s}description" % ns['gml'])
                    description.text = inp["description"]
        
        #--- System Outputs
        timetag = False
        system.append(et.Comment("System Outputs"))
        outputs = et.SubElement(system, "{%s}outputs" % ns['sml'])
        OutputList = et.SubElement(outputs, "{%s}OutputList" % ns['sml'])
        output = et.SubElement(OutputList, "{%s}output" % ns['sml'])
        output.attrib["name"] = "output data"
        DataRecord = et.SubElement(output, "{%s}DataRecord" % ns['swe'])
        DataRecord.attrib["definition"] = "urn:ogc:def:dataType:x-istsos:1.0:timeSeries"
        oid = 0
        for o in self.data["outputs"]:
            oid += 1
            field = et.SubElement(DataRecord, "{%s}field" % ns['swe'])
            field.attrib["name"] = o["name"]
            
            if o["name"] == "Time":
                timetag = True
                item = et.SubElement(field, "{%s}Time" % ns['swe'])
                item.attrib["{%s}id" % ns['gml']] = "IDT_" + str(oid)
                item.attrib["definition"] = o["definition"]
                
                if not o["description"]=="":
                    description = et.SubElement(item, "{%s}description" % ns['gml'])
                    description.text = o["description"]
                    
                uom = et.SubElement(item, "{%s}uom" % ns['swe'])
                uom.attrib["code"] = o["uom"]
                
                # The constraint object is not mandatory
                if "constraint" in o and o["constraint"]!={}: # and o["constraint"]["role"]!="" and o["constraint"]["role"]!=None:
                    
                    constraint = et.SubElement(item, "{%s}constraint" % ns['swe'])
                    
                    # Role attribute is not mandatory
                    if "role" in o["constraint"] and o["constraint"]["role"]!="" and o["constraint"]["role"]!=None:
                        constraint.attrib[ "{%s}role" % ns['xlink'] ] = o["constraint"]["role"]
                        
                    AllowedTimes = et.SubElement(constraint, "{%s}AllowedTimes" % ns['swe'])
                    interval = et.SubElement(AllowedTimes, "{%s}interval" % ns['swe'])
                    interval.text = " ".join([ str(a) for a in o["constraint"]["interval"] ])
                    
            else:
                item = et.SubElement(field, "{%s}Quantity" % ns['swe'])
                item.attrib["{%s}id" % ns['gml']] = "IDQ_" + str(oid)
                item.attrib["definition"] = o["definition"]
                
                if not o["description"]=="":
                    description = et.SubElement(item, "{%s}description" % ns['gml'])
                    description.text = o["description"]
                    
                uom = et.SubElement(item, "{%s}uom" % ns['swe'])
                uom.attrib["code"] = o["uom"]
                
                # The constraint object is not mandatory
                if "constraint" in o and o["constraint"]!={}: # and o["constraint"]["role"]!="" and o["constraint"]["role"]!=None:
                    print >> sys.stderr, o['constraint']                    
                    try:
                        ut.validateJsonConstraint(o['constraint'])
                    except Exception as ex:
                        raise Exception("Constraint for observed property '%s' is not valid: %s" % (o["definition"],ex))
                    
                    constraint = et.SubElement(item, "{%s}constraint" % ns['swe'])
                    
                    # Role attribute is not mandatory
                    if "role" in o["constraint"] and o["constraint"]["role"]!="" and o["constraint"]["role"]!=None:
                        constraint.attrib[ "{%s}role" % ns['xlink'] ]= o["constraint"]["role"]
                        
                    AllowedValues = et.SubElement(constraint, "{%s}AllowedValues" % ns['swe'])
                    
                    # Factory on constraint min/max/interval/valuelist
                    if "interval" in o["constraint"]:
                        interval = et.SubElement(AllowedValues, "{%s}interval" % ns['swe'])
                        interval.text = " ".join([ str(a) for a in o["constraint"]["interval"] ])
                        
                        
                    elif "valueList" in o["constraint"]:#.has_key("valueList"):
                        valueList = et.SubElement(AllowedValues, "{%s}valueList" % ns['swe'])
                        valueList.text = " ".join([ str(a) for a in o["constraint"]["valueList"] ])
                        
                    elif "min" in o["constraint"]:#.has_key("min"):
                        amin = et.SubElement(AllowedValues, "{%s}min" % ns['swe'])
                        amin.text = str(o["constraint"]["min"])
                        
                    elif "max" in o["constraint"]:#.has_key("max"):
                        amax = et.SubElement(AllowedValues, "{%s}max" % ns['swe'])
                        amax.text = str(o["constraint"]["max"])
                        
                        
        if timetag == False:
            raise Exception("self.data['outputs']: Time is mandatory")
        
        #--- System History
        if ("history" in self.data) and (not self.data["history"]==[]):
            system.append(et.Comment("System History"))
            history = et.SubElement(system, "{%s}history" % ns['sml'])
            EventList = et.SubElement(history, "{%s}EventList" % ns['sml'])
            for h in self.data["history"]:
                member = et.SubElement(EventList, "{%s}member" % ns['sml'])
                member.attrib["name"] = h["type"]
                Event = et.SubElement(member, "{%s}Event" % ns['sml'])
                date = et.SubElement(Event, "{%s}date" % ns['sml'])
                date.text = h["date"]
                if not h["description"]=="":
                    description = et.SubElement(Event, "{%s}description" % ns['gml'])
                    description.text = h["description"]
                contact = et.SubElement(Event, "{%s}contact" % ns['sml'])
                contact.attrib["{%s}href" % ns['xlink'] ] = h["reference"]["username"]
                contact.attrib["{%s}arcrole" % ns['xlink'] ] = h["reference"]["role"]
        
        return et.tostring(root, encoding="UTF-8")
        
        
    def toRegisterSensorDom(self,indent=False):
        """
        Create a SOS register sensor request DOM element from self.procedure object
        """
        import sys
        ns = {
            'xsi': 'http://www.w3.org/2001/XMLSchema-instance',
            'sml': 'http://www.opengis.net/sensorML/1.0.1', 
            'swe': "http://www.opengis.net/swe/1.0.1", 
            'xlink': "http://www.w3.org/1999/xlink", 
            'gml': 'http://www.opengis.net/gml',           
            'sos': "http://www.opengis.net/sos/1.0",
            'ogc': "http://www.opengis.net/ogc",
            'om': "http://www.opengis.net/om/1.0",
        }
        
        #---map namespaces---
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
                        print >> sys.stderr, ("Failed to import ElementTree from any known place")
                for key in ns:
                    _namespace_map[ns[key]] = key
        
        #---start creating XML ----        
        root = et.Element("{%s}RegisterSensor" % ns['sos'])
        root.attrib[ "{%s}schemaLocation" % ns['xsi'] ] = "http://www.opengis.net/sos/1.0 http://schemas.opengis.net/sos/1.0.0/sosAll.xsd"
        root.attrib["version"] = "1.0.0"
        root.attrib["service"] = "SOS"
        
        SensorDescription = et.SubElement(root, "{%s}SensorDescription" % ns['sos'])
        
        sml = self.toXML()
        #print >> sys.stderr, "SML:%s" % sml
        from StringIO import StringIO
        smltree, smlns = parse_and_get_ns(StringIO(sml))
        member = smltree.find("{%s}member" % ns['sml'] )
        SensorDescription.append(member)
        
        #---         
        ObservationTemplate = et.SubElement(root, "{%s}ObservationTemplate" % ns['sos'])
        Observation = et.SubElement(ObservationTemplate, "{%s}Observation" % ns['om'])
        procedure = et.SubElement(Observation, "{%s}procedure" % ns['om'])
        procedure.attrib["{%s}href" % ns['xlink']] = "urn:ogc:object:procedure:x-istsos:1.0:"+self.data["system"]
        
        samplingTime = et.SubElement(Observation, "{%s}samplingTime" % ns['om'])
        TimePeriod = et.SubElement(samplingTime, "{%s}TimePeriod" % ns['gml'])
        beginPosition = et.SubElement(TimePeriod, "{%s}beginPosition" % ns['gml'])
        endPosition = et.SubElement(TimePeriod, "{%s}endPosition" % ns['gml'])

        observedProperty = et.SubElement(Observation, "{%s}observedProperty" % ns['om'])
        CompositePhenomenon = et.SubElement(observedProperty, "{%s}CompositePhenomenon" % ns['swe'])
        CompositePhenomenon.attrib["{%s}id" % ns['gml']] = str("comp_XXX")
        CompositePhenomenon.attrib["dimension"] = str(len(self.data["outputs"]))
        name = et.SubElement(CompositePhenomenon, "{%s}name" % ns['gml'])
        name.text = "timeSeriesOfObservations"
        for o in self.data["outputs"]:
            component = et.SubElement(CompositePhenomenon, "{%s}component" % ns['swe'])
            component.attrib["{%s}href" % ns['xlink']] = o["definition"]
        
        featureOfInterest = et.SubElement(Observation, "{%s}featureOfInterest" % ns['om'])
        featureOfInterest.attrib["{%s}href" % ns['xlink']] = self.data["location"]["properties"]["name"]
        FeatureCollection = et.SubElement(featureOfInterest, "{%s}FeatureCollection" % ns['gml'])
        #FeatureCollection = et.SubElement(featureOfInterest, "{%s}FeatureCollection" % ns['gml'])
        location = et.SubElement(FeatureCollection, "{%s}location" % ns['gml'])
        Point = et.SubElement(location, "{%s}Point" % ns['gml'])
        Point.attrib[ "{%s}id" % ns['gml'] ] = "gmlfoi_" + self.data["location"]["properties"]["name"]
        Point.attrib[ "srsName" ] = self.data["location"]["crs"]["properties"]["name"] if "EPSG:" in self.data["location"]["crs"]["properties"]["name"] else "EPSG:%s" % self.data["location"]["crs"]["properties"]["name"]
        coordinates = et.SubElement(Point, "{%s}coordinates" % ns['gml'])
        coordinates.text = ",".join([ str(a) for a in self.data["location"]["geometry"]["coordinates"] ])
        
        result = et.SubElement(Observation, "{%s}result" % ns['om'])
        DataArray = et.SubElement(result, "{%s}DataArray" % ns['swe'])
        
        elementCount = et.SubElement(DataArray, "{%s}elementCount" % ns['swe'])
        count = et.SubElement(elementCount, "{%s}count" % ns['swe'])        
        value = et.SubElement(count, "{%s}value" % ns['swe'])
        value.text = str(len(self.data["outputs"]))
        
        elementType = et.SubElement(DataArray, "{%s}elementType" % ns['swe'])
        elementType.attrib["name"] = "SimpleDataArray"
        elementType.attrib["{%s}href" % ns['xlink']] = "urn:ogc:def:dataType:x-istsos:1.0:timeSeriesDataRecord"
        
        DataRecord = smltree.find("{%s}member/{%s}System/{%s}outputs/{%s}OutputList/{%s}output/{%s}DataRecord" 
                            % (ns['sml'],  ns['sml'],  ns['sml'], ns['sml'],    ns['sml'],  ns['swe'] ) )
        
        elementType.append(DataRecord)
        
        encoding = et.SubElement(DataArray, "{%s}encoding" % ns['swe'])
        TextBlock = et.SubElement(encoding, "{%s}TextBlock" % ns['swe'])
        TextBlock.attrib["tokenSeparator"] = "," 
        TextBlock.attrib["blockSeparator"] = "@"
        TextBlock.attrib["decimalSeparator"] = "."
        
        #values = et.SubElement(DataArray, "{%s}values" % ns['swe'])
        
        return root
        
        
    def toRegisterSensor(self,indent=False):
        """
        Create a SOS register sensor request String from self.procedure object
        """
        dom = self.toRegisterSensorDom()
        return et.tostring(dom, encoding="UTF-8")      
        
        
        
        
        
        
        
        
        
        
        
        
        
        
        
        
        
        



    

