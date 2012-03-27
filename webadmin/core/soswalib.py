# istSOS Istituto Scienze della Terra Sensor Observation Service
# Copyright (C) 2012 Massimiliano Cannata / Milan Antonovic
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


class istSOSservice:
    def __init__(self,configfile,authority=None,version=None,identification=None,
                    provider=None,database=None,qualityIndexes=None,config=None,coords=None):
        self.authority = authority
        self.version = version
        self.identification = identification
        self.provider = provider # provider object 
        self.database = database # database parameters
        self.qualityIndexes = qualityIndexes # qualityIndexes object lists
        self.config = config # config object with required paths
        self.coords = coords # coord object with epsg,e,n,z and allowed epsgs
        
    def get():
        
    def set():
        

        

class provider:
    def __init__(self,name,site,contact):
        self.name = name
        self.site = site
        self.contact = contact # contact object 
        
        
class contact:
    def __init__(self,name,position,email,
                            voice=None,fax=None,deliverypoint=None,
                            city=None,state=None,postcode=None,country=None):
        self.name = name
        self.position = position
        self.voice = voice
        self.fax = fax
        self.email = email
        self.deliverypoint = deliverypoint
        self.city = city
        self.state = state
        self.postcode = postcode
        self.country = country

        
class databse:
    def __init__(self,user,password,host,dbname,schema,port=5432):
        self.user = user
        self.password = password
        self.host = host
        self.dbname = dbname
        self.port = port
        self.schema = schema
    
    
class qualityIndexe:
    def __init__(self,code,desc):
        self.code = code
        self.desc = desc    
    
    
class config:
    def __init__(self,servUrlGet,servUrlPost,sensorMlPath,vertualProcPath,istsoslibPath):
        self.servUrlGet = servUrlGet
        self.servUrlPost = servUrlPost
        self.sensorMlPath = sensorMlPath
        self.vertualProcPath = vertualProcPath
        self.istsoslibPath = istsoslibPath
        
class coords:
    def __init__(self,sosEpsg,x_axis,y_axis,z_axis,allowedEpsg=[]):
        istSOSepsg = sosEpsg
        x_axis = x_axis
        y_axis = y_axis
        z_axis = z_axis
        sos_allowedEPSG = allowedEPSG
    
    
                
        
