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
'''
This script register new procedures importing data from a csv file in this format:

nome procedura;Descrizione;Keywords;SystemType;SensorType;foi name;epsg;x;y;z;name,definition,uom@name,definition,uom@name,definition,uom
nome procedura;Descrizione;Keywords;SystemType;SensorType;foi name;epsg;x;y;z;name,definition,uom@name,definition,uom@name,definition,uom
nome procedura;Descrizione;Keywords;SystemType;SensorType;foi name;epsg;x;y;z;name,definition,uom@name,definition,uom@name,definition,uom
nome procedura;Descrizione;Keywords;SystemType;SensorType;foi name;epsg;x;y;z;name,definition,uom@name,definition,uom@name,definition,uom
nome procedura;Descrizione;Keywords;SystemType;SensorType;foi name;epsg;x;y;z;name,definition,uom@name,definition,uom@name,definition,uom
nome procedura;Descrizione;Keywords;SystemType;SensorType;foi name;epsg;x;y;z;name,definition,uom@name,definition,uom@name,definition,uom


'''

import sys
import os
from os import path
import traceback
import json
import pprint
import glob
from datetime import datetime

#print path.abspath(".")
#print path.normpath("%s/../" % path.abspath("."))
    
sys.path.insert(0, path.abspath("."))
try:
    import lib.argparse as argparse
    from scripts import istsosutils as iu

except ImportError as e:
    print "\nError loading internal libs:\n >> did you run the script from the istSOS root folder?\n\n"
    raise e



def execute (args, logger=None):

    try:
        # Service instance name
        csv = args['csv']
        
        # Initializing URLs
        service = iu.Service(args['u'],args['s'])
        
        file = open(csv, 'rU')
                    
        # loop lines
        lines = file.readlines()
        
        # loop lines (skipping header)
        for i in range(0, len(lines)):
            line = lines[i].strip(' \t\n\r').split(";")
            
            proc = iu.Procedure(line[0])
            proc.setDescription(line[1])
            proc.setKeywords(line[2])
            proc.setSystemType(line[3])
            proc.setSensorType(line[4])
            proc.setFoi(line[5],line[6],line[7],line[8],line[9])
            
            for op in line[10].split("@"):
                op = op.split(",")
                proc.addObservedProperty(op[0], op[1], op[2])
                        
            print line
            
            service.registerProcedure(proc)
            
            
    except Exception as e:    
        print "ERROR: %s\n\n" % e
        traceback.print_exc()
        
        
if __name__ == "__main__":

    parser = argparse.ArgumentParser(
        description='Registers new sensor from a csv file.')
        
    parser.add_argument('-csv', 
        action='store',
        required=True,
        dest='csv',
        metavar='csv file',
        help='The csv file containing the procedures metadata')
    
    parser.add_argument('-u',
        action = 'store',
        dest   = 'u',
        metavar= 'url',
        default= 'http://localhost:80/istsos',
        help   = 'IstSOS Server address IP (or domain name) used for all request. (default: %(default)s).')
    
    parser.add_argument('-s',
        action = 'store',
        required=True,
        dest   = 's',
        metavar= 'service',
        help   = 'The name of the service instance.')

    args = parser.parse_args()
    #print args.__dict__
    execute(args.__dict__)
    
