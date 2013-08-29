# -*- coding: utf-8 -*-
# istSOS WebAdmin - Istituto Scienze della Terra
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

from walib.resource import waResourceService
import sys, os

# istsos/services/test/virtualprocedures/Q_TEST/ratingcurves
class waRatingcurve(waResourceService):
    """
    class to handle SOS rating curve for virtual procedure of type HQ
    called with a request to istsos/services/{serviceName}/virtualprocedures/{procedurename}/ratingcurve
    
    list of ordered dictionary of rating-curve parameters:
        [ 
         {
          "A": "5.781",
          "B": "0.25",
          "C": "1.358",
          "K": "0",
          "from": "1982-01-01T00:00+00:00",
          "low_val": "0",
          "to": "1983-01-01T00:00+00:00",
          "up_val": "1000"
         }, 
         {...},{...},...
        ]
    """
    
    def __init__(self,waEnviron):
        waResourceService.__init__(self,waEnviron)
        self.servicename = self.pathinfo[2]
        self.procedurename =  self.pathinfo[4]
        self.procedureFolder = os.path.join(self.servicepath, "/virtual/", self.procedurename)
        self.RCfilename = os.path.join(self.procedureFolder, self.procedurename + ".dat")
        
    def executeGet(self):
        #filename = self.RCpath + "/" + self.RCprocedure + ".dat"
        if not os.path.exists(self.procedureFolder):
            os.makedirs(self.procedureFolder) 
        RClist = RCload(self.RCfilename)
        self.setData(RClist)
        self.setMessage("Rating-curve parameters of procedure <%s> successfully retrived" % self.RCprocedure)        
            
    def executePost(self):
        """
        Method for executing a POST requests that create a new SOS observed property
                  
        """
        if RCsave(self.json,self.RCfilename):
            self.setMessage("Rating-curve parameters of procedure <%s> successfully saved" % self.RCprocedure)               
            
        
        
def RCload(filename):
    #load HQ virtual procedure conf file to a list of dictionaries
    cvlist=[]
    with open(filename) as f:
        lines = f.readlines()
        items = [ i.strip().split("|") for i in lines ]
        fields = items[0]
        for i in range(1,len(items)):
            cvdict = {}
            for f, field in enumerate(fields):
                cvdict[field]= items[i][f]
            cvlist.append(cvdict)
    return cvlist

def RCsave(cvlist,filename):

    print >> sys.stderr, "==================save=============="    
    print >> sys.stderr, cvlist
    print >> sys.stderr, filename
    print >> sys.stderr, "==================save=============="
    lines = []
    header = ['from','to','low_val','up_val','A','B','C','K']
    #check cvlist validity and save to HQ virtual procedure conf file
    for item in cvlist:
        try:
            if not item["from"] < item["to"]:
                raise Exception, 'Error: <from> %s not before of <to> %s' %(item["from"],item["to"])
            line = [ item[h] for h in header ]
            lines.append(line)
        except Exception as e:
            raise Exception("Error: invalid HQ parameter list; %s" % str(e) )
    
    

    lines.sort()
    for i in range(1,len(lines)):
        if not lines[i][0]==lines[i-1][1]:
            raise Exception, 'Error: series of HQ curve not continue; check <from> %s' %(lines[i][0])
    
    with open (filename, 'w') as f:
        f.write("|".join(header) + "\n")
        for line in lines:
            f.write ("|".join(line) + "\n")
    
    return True
        

"""    
from|to|low_val|up_val|A|B|C|K
1982-
"""
