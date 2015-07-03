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
import ConfigParser
import os 
import os.path

class waServiceConfig():
    """
    base service configuration object to handle configuration files
    
    >>> Class structure:
        self.defaultcfgpath --> path of the default configuration file
        self.servicecfgpath --> path of the service configuration file
        self.sections = --> list of available sections
        self.* = {} --> dictionary of the options for the * section
    
    @note: Each section is an attribute of the waServiceConfig object and is a dictionary of option names (key) and value.
    Additionally each section dictionary has a special key "default" that is a boolean variable indicating if the section 
    is set in the default or specific service configuration file.
    
    >>> Example of section attribute
        myconfig = waServiceConfig("/services","/services/myservice")
        print myconfig.serviceurl
        {'default': True, 'post': 'http://localhost:8099', 'get': 'http://localhost:8099'}
    """
    
    def __init__(self, defaultcfgpath, servicecfgpath=None):
        """
        initialize the configuration object with default configuration file and
        service specific configuration file
        
        @param defaultcfgpath: path of default configuration file
        @type defaultcfgpath: C{string}
        @param servicecfgpath: path of service configuration file
        @type servicecfgpath: C{string}
        """
        self.defaultcfgpath = defaultcfgpath
        self.servicecfgpath = servicecfgpath
        
        #read config from server
        defaultconf = ConfigParser.RawConfigParser()
        defaultconf.optionxform = str
        defaultconf.read(defaultcfgpath)
        self.sections = defaultconf.sections()
        
        #read config from service
        serviceconf = ConfigParser.RawConfigParser()
        serviceconf.optionxform = str
        if not servicecfgpath == None:
            serviceconf.read(servicecfgpath)
        
        for section in self.sections:
            val = {}
            if serviceconf.has_section(section):
                val["default"] = False
                for option in serviceconf.options(section):
                    val[option] = serviceconf.get(section, option)
            else:
                val["default"] = True
                for option in defaultconf.options(section):
                    val[option] = defaultconf.get(section, option)
            setattr(self, section, val) 
    
    def get(self,section):
        """
        returns the requested section as a dictionary
        
        @param section: configuration section
        @type section: C{string}
        """
        try:
            return getattr(self,"%s" % section)
        except Exception:
            raise Exception("Section %s does not exists" % section)
    
    def put(self,section,option,value):
        """
        put new value to given option in given section
        
        @param section: configuration section
        @type section: C{string}
        @param option: configuration option
        @type option: C{string}
        @param value: configuration value
        @type section: C{value}
        """
        tmpsection = getattr(self,"%s" % section)
        if option in tmpsection:
            if not self.servicecfgpath==None:
                tmpsection["default"] = False 
            tmpsection[option]=value
            setattr(self,section,tmpsection)
        else:
            raise Exception("section <%s> has not option <%s>" %(section,option) )
    
    
    def delete(self,section):
        """
        returns the requested section as a dictionary
        
        @param section: configuration section
        @type section: C{string}
        """
        if self.get(section)['default'] == True:
            raise Exception("Cannot remove sections from default configuration")
        self.sections.remove(section)
    
    def save(self):
        """
        save current configuration to appropriate files
        """
        if not self.servicecfgpath==None:
            serviceconf = ConfigParser.RawConfigParser()
            serviceconf.optionxform = str
            
            for sectionname in self.sections:
                section = getattr(self,"%s" % sectionname)
                if section["default"]==False:
                    serviceconf.add_section(sectionname)
                    for option in section.keys():
                        if not option=="default":
                            serviceconf.set(sectionname, option, section[option])
                        
            cfgfile = open(self.servicecfgpath,'w')
            serviceconf.write(cfgfile)
            cfgfile.close()
            
        else:
            defaultconf = ConfigParser.RawConfigParser()
            defaultconf.optionxform = str
            
            for sectionname in self.sections:
                section = getattr(self,"%s" % sectionname)
                defaultconf.add_section(sectionname)
                for option in section.keys():
                    if not option=="default":
                        defaultconf.set(sectionname, option, section[option])
                        
            cfgfile = open(self.defaultcfgpath,'w')
            defaultconf.write(cfgfile)
            cfgfile.close()     
        
    
