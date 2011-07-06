import xml.etree.ElementTree as etree

xsi="http://www.w3.org/2001/XMLSchema-instance/" 
swe="http://www.opengis.net/swe/1.0.1" 
gml="http://www.opengis.net/gml" 
om="http://www.opengis.net/om/1.0" 
xlink="http://www.w3.org/1999/xlink" 
sa="http://www.opengis.net/sampling/1.0"

etree._namespace_map[xsi] = 'xsi'
etree._namespace_map[swe] = 'swe'
etree._namespace_map[gml] = "gml"
etree._namespace_map[om] = "om"
etree._namespace_map[xlink] = "xlink"
etree._namespace_map[sa] = "sa"
etree._namespace_map["http://www.w3.org/2001/XMLSchema/"] = 'xs'

def get_name_from_urn(stringa,urnName):
    a = stringa.split(":")
    name = a[-1]
    urn = sosConfig.urn[urnName].split(":")
    if len(a)>1 and not name=="iso8601":
        for index in range(len(urn)-1):
            if urn[index]==a[index]:
                pass
            else:
                raise sosException.SOSException(1,"Urn \"%s\" is not valid: %s."%(a,urn))
    return name

file = "/home/ist/Desktop/getObservationComposite.xml"
f = open(file,'r') 
xmlstr = f.read()

class om_observation:
    def __init__(self, xmlstr):
        self.procedure = None
        self.oprName=[]
        self.samplingTime = None
        self.foiName = None
        self.foiGml = None
        self.result = {
            "time" : []
            "vals" : {} #{ "prop@uom" : [], "prop2@uom": [], "prop3@uom": [] }
           }
        
        #initialize on_observation
        if xml.__class__.__name__ == "file":
            tree = etree.parse(xmlstr)
        elif xml.__class__.__name__ == "str":
            tree = etree.XML(xmlstr)
        
        root = tree.getroot()
        
        #-------procedure
        proc = root.findall("{%s}member/{%s}Observation/{%s}procedure"%(om,om,om))
        if not len(proc)==1:
            raise ObsError("om:procedure tag is mandatory with multiplicity 1")
        self.procedure = get_name_from_urn(getElemAtt(proc[0].attrib["{%s}href" %xlink],"procedure")
        
        
        



