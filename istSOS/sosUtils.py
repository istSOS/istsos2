from xml.dom import minidom
from osgeo import ogr
from istSOS import sosException

def childElementNodes(xmlnode):
    elements = [e for e in xmlnode.childNodes if e.nodeType == e.ELEMENT_NODE]
    return elements

def ogcSpatCons2PostgisSql(ogcSpatialOperator,geomField,epsgField):
    """parse an ogc spatial operator element and convert it to a PostGIS SQL spatial WHERE clause"""
    ogcSupportedSpatialOperators = {'ogc:Disjoint':'ST_Disjoint',
                        'ogc:Equals':'ST_Equals',
                        'ogc:Intersect':'ST_Intersects',
                        'ogc:Touches':'ST_Touches',
                        'ogc:Crosses':'ST_Crosses',
                        'ogc:Within':'ST_Within',
                        'ogc:Contains':'ST_Contains',
                        'ogc:Overlaps':'ST_Overlaps',                        
                    }
                        
    ogcSupportedDistanceBufferType = [ 'ogc:DWithin' ] 
    ogcBBOXType = ['ogc:BBOX']
    ogcUnsupportedSpatialOperators = ['ogc:Beyond']
    
    if ogcSpatialOperator.__class__.__name__ in ["str","StringField"]:
        xmlString = """<?xml version="1.0" encoding="UTF-8"?><sos:featureOfInterest 
        xmlns:xsi="http://www.w3.org/2001/XMLSchema-instance" 
        xsi:schemaLocation="http://schemas.opengis.net/sos/1.0.0/sosAll.xsd"
        xmlns:sos="http://www.opengis.net/sos/1.0"
        xmlns:gml="http://www.opengis.net/gml/3.2"
        xmlns:ogc="http://www.opengis.net/ogc"
        xmlns:om="http://www.opengis.net/om/1.0" 
        service="SOS" version='1.0.0'>
        """
        xmlString += ogcSpatialOperator + "</sos:featureOfInterest>"
        xmlObject = minidom.parseString(xmlString)
        foi = xmlObject.getElementsByTagName("sos:featureOfInterest")[0]
        ogcSpatialOperator = childElementNodes(foi)[0]
    
    try:
        ogcOperator = ogcSpatialOperator.nodeName.encode()
    except:
        raise sosException.SOSException(1,"ogcSpatCons2PostgisSql: argunment must be an ''XML object'' or a valid ''XML string''")
    
    prop = ''
    sql=''

    #---------------------------
    # PARSE OPTIONS
    #---------------------------
    if ogcOperator in ogcSupportedSpatialOperators.keys():
        childs = childElementNodes(ogcSpatialOperator)
        propertyName = childs[0].firstChild.data.encode()
        geometry = childs[1]
        try:
            epsg = geometry.attributes['srsName'].value.split(":")[-1]
        except:
            epsg = None
        if not epsg.isdigit() and not epsg == None:
            raise sosException.SOSException(1,"Error: srsName '%s' must be numeric!" %(epsg))
        WKTgeom = ogr.CreateGeometryFromGML(str(geometry.toxml()))
        
        if epsgField == epsg or epsg == None:
            sql = "%s(%s,ST_GeomFromText('%s',%s))" %(ogcSupportedSpatialOperators[ogcOperator],geomField,WKTgeom.ExportToWkt(),epsgField)
        else:
            sql = "%s(%s,ST_Transform(ST_GeomFromText('%s',%s),%s))" %(ogcSupportedSpatialOperators[ogcOperator],geomField,WKTgeom.ExportToWkt(),epsg,epsgField)
        return sql
    
    elif ogcOperator == 'ogc:BBOX':
        childs = childElementNodes(ogcSpatialOperator)
        propertyName = childs[0].firstChild.data.encode()
        geometry = childs[1]
        try:
            epsg = geometry.attributes['srsName'].value.split(":")[-1]
        except:
            epsg = None
        if not epsg.isdigit() and not epsg == None:
            raise sosException.SOSException(1,"Error: srsName '%s' must be numeric!" %(epsg))            
        WKTgeom = ogr.CreateGeometryFromGML(str(geometry.toxml()))
        if epsgField == epsg or epsg == None:
            sql = "%s && ST_GeomFromText('%s',%s)" %(geomField,WKTgeom.ExportToWkt(),epsgField)
        else:
            sql = "%s && ST_Transform(ST_GeomFromText('%s',%s),%s)"  %(geomField,WKTgeom.ExportToWkt(),epsg,epsgField)
        return sql
    
    elif ogcOperator == 'ogc:DWithin':
        childs = childElementNodes(ogcSpatialOperator)
        propertyName = childs[0].firstChild.data.encode()
        geometry = childs[1]
        distance = childs[2].firstChild.data.encode()
        try:
            epsg = geometry.attributes['srsName'].value.split(":")[-1]
        except:
            epsg = None        
        if not epsg.isdigit() and not epsg == None:
            raise sosException.SOSException(1,"Error: srsName '%s' must be numeric!" %(epsg))
        WKTgeom = ogr.CreateGeometryFromGML(str(geometry.toxml()))
        if epsgField == epsg or epsg == None:
            sql = "ST_DWithin(%s,ST_GeomFromText('%s',%s),%s)" %(geomField,WKTgeom.ExportToWkt(),epsgField,distance)
        else:
            sql = "ST_DWithin(%s,ST_Transform(ST_GeomFromText('%s',%s),%s),%s)" %(geomField,WKTgeom.ExportToWkt(),epsg,epsgField,distance)
        return sql
    
    elif ogcOperator in ogcUnsupportedSpatialOperators:
        raise sosException.SOSException(1,"Spatial Operator nor supported. Available methods are: %s" %(",".join(ogcSupportedSpatialOperators.keys())))
    
    else:
        raise sosException.SOSException(1,"ogcSpatialOperator format ERROR")
        

def ogcCompCons2PostgisSql(ogcComparisonOperator):
    """parse an ogc spatial operator element and convert it to a PostGIS SQL spatial WHERE clause"""
    ogcSupportedCompOperators = {'ogc:PropertyIsEqualTo':'=',
                        'ogc:PropertyIsNotEqualTo':'!=',
                        'ogc:PropertyIsLessThan':'<',
                        'ogc:PropertyIsGreaterThan':'>',
                        'ogc:PropertyIsLessThanOrEqualTo':'<=',
                        'ogc:PropertyIsGreaterThanOrEqualTo':'>=',
                    }
    """
    'ogc:PropertyIsBetween':'BETWEEN'
    'ogc:PropertyIsLike':'LIKE',
    'ogc:PropertyIsNull':'= NULL'
    """
    
    if ogcComparisonOperator.__class__.__name__ in ["str","StringField"]:
        xmlString = """<?xml version="1.0" encoding="UTF-8"?><sos:result 
        xmlns:xsi="http://www.w3.org/2001/XMLSchema-instance" 
        xsi:schemaLocation="http://schemas.opengis.net/sos/1.0.0/sosAll.xsd"
        xmlns:sos="http://www.opengis.net/sos/1.0"
        xmlns:gml="http://www.opengis.net/gml/3.2"
        xmlns:ogc="http://www.opengis.net/ogc"
        xmlns:om="http://www.opengis.net/om/1.0" 
        service="SOS" version='1.0.0'>
        """
        xmlString += ogcComparisonOperator + "</sos:result>"
        xmlObject = minidom.parseString(xmlString)
        res = xmlObject.getElementsByTagName("sos:result")[0]
        ogcComparisonOperator = childElementNodes(res)[0]
    
    try:
        ogcOperator = ogcComparisonOperator.nodeName.encode()
    except:
        raise sosException.SOSException(1,"ogcCompCons2PostgisSql: argunment must be an ''XML object'' or a valid ''XML string''")
    
    
    prop = ''
    sql=''

    #---------------------------
    # PARSE OPTIONS
    #---------------------------
    if ogcOperator in ogcSupportedCompOperators.keys():
        childs = childElementNodes(ogcComparisonOperator)
        propertyNameObj = ogcComparisonOperator.getElementsByTagName("ogc:PropertyName")
        literalObj = ogcComparisonOperator.getElementsByTagName("ogc:Literal")
        matchCase = True
        if len(propertyNameObj)==1 and len(literalObj)==1:
            #raise sosException.SOSException(1,"XML %s" %(propertyNameObj[0].data))
            propertyName = propertyNameObj[0].firstChild.data.encode().strip()
            """ -- unsupported because only digits are valid --
            if propertyNameObj[0].value.upper()=="FALSE": 
                matchCase = False
            """
            literal = literalObj[0].firstChild.data.encode().strip()
            if not literal.isdigit() and not literal == None:
                raise sosException.SOSException(1,"Sorry istSOS support only numeric constraints, provided: \'%s\'" %(literal))
        else:
            raise sosException.SOSException(2,"ogcCompCons2PostgisSql: ogc:comparisonOps allow only two expression")
        
        return ("%s" %(propertyName),"%s %s" %(ogcSupportedCompOperators[ogcOperator],literal))
    else:
        raise sosException.SOSException(2,"ogcCompCons2PostgisSql: ogc:comparisonOps not jet supported")
        
def CQLvalueFilter2PostgisSql(fildName,CQLfilter):
    """parse a CQL filter and returen an SQL filter"""
    CQLsupportedOperators = ("<","<=",">",">=","=")
    
    if CQLfilter.__class__.__name__ in ["str","StringField"]:
        if CQLfilter[0] in ["<",">","="]:
            if CQLfilter[1] in ["="]:
                if not CQLfilter[2:].isdigit():
                    raise sosException.SOSException(2,"CQLvalueFilter2PostgisSql: only numeric comparison supported")
            else:
                if not CQLfilter[1:].isdigit():
                    raise sosException.SOSException(2,"CQLvalueFilter2PostgisSql: only numeric comparison supported")
        else:
            raise sosException.SOSException(2,"CQLvalueFilter2PostgisSql: only filter by comparing values is supported")
    else:
        raise sosException.SOSException(2,"CQLvalueFilter2PostgisSql: input must be a string")
    return "%s %s" %(fildName,CQLfilter)
    
    
    
    
    
    
    
    
    
    
        
