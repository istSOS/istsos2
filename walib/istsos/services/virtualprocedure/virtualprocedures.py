# -*- coding: utf-8 -*-

from walib import procedure, databaseManager
import lib.requests as requests
from walib.resource import waResourceService
import os
import sys
import shutil


class waVirtualProcedures(waResourceService):
    
    def __init__(self,waEnviron):
        waResourceService.__init__(self,waEnviron)
        self.servicename = self.pathinfo[2]
        if not self.pathinfo[-1]=="virtualprocedures" and len(self.pathinfo)>4:
            self.procedurename = self.pathinfo[4]
        else:
            self.procedurename = None
            
    def executePost(self):
        """self.json >>>servicecfgpath
        {"script" : 
            {
                "code" : "def execute(self):...",
                "init" : "from|to|low_val|up_val|A|B|C|K"        
            },
        "observed_property" :
            {
                "definition": "urn:ogc:def:parameter:x-istsos:1.0:hydro:river:water:discharge",
                "constraint": {
                    "role": "urn:x-ogc:def:classifiers:x-istsos:1.0:qualityIndexCheck:level0",
                    "min": "0"
                },
                "name": "river-discharge",
                "uom": "m3/s",
                "description": ""
            },
        "original_proc" : "nameOfProcedure"
        }"""

        
        k = self.pathinfo.index("services")
        service = self.pathinfo[k+1]
        k = self.pathinfo.index("virtualprocedures")
        name = self.pathinfo[k+1]
        
        address = 'http://localhost/istsos/wa/istsos/services/' + service
        
        
        jproc = requests.get(address + '/procedures/' + self.json['original_proc'], prefetch=True).json['data']
        
        jproc["capabilities"] = []
        jproc["contacts"] = []
        jproc["documentation"] = []
        jproc["history"] = []
        jproc["identification"] = []
        jproc["inputs"] = []
        jproc["interfaces"] = ""
        jproc["keywords"] = ""
        jproc["characteristics"] = ""
      
        jproc["description"] = "Virtual procedure based on " + jproc['system']
        jproc["system"] = name
        jproc["system_id"] = name
        jproc["classification"][0]["value"] = "insitu-fixed-point"
        jproc["classification"][1]["value"] = "virtual"
        #jproc["location"] remains the same
    
        for el in jproc['outputs']:
            if el['name'] != 'Time':
                jproc['outputs'].remove(el)
            else:
                el["constraint"]["role"] = "urn:x-ogc:def:classifiers:x-istsos:1.0:qualityIndexCheck:level0"
                
        jproc['outputs'].append(self.json['observed_property'])

#        res = requests.post(
#            address + '/virtualprocedures',
#            data=json.dumps(jproc),
#            prefetch=True
#        )

        os.umask(0000)

        proc = procedure.Procedure(self.serviceconf)
        proc.loadDICT(jproc)
        smlstring = proc.toRegisterSensor(indent=False)
        
        res = requests.post(
            self.serviceconf.serviceurl["url"], 
            data=smlstring,
            headers={"Content-type": "text/xml"}, 
            prefetch=True
        )
        
        
        servicedb = databaseManager.PgDB(
            self.serviceconf.connection['user'],
            self.serviceconf.connection['password'],
            self.serviceconf.connection['dbname'],
            self.serviceconf.connection['host'],
            self.serviceconf.connection['port']
        )
        sql  = "UPDATE %s.procedures " %(self.service)
        sql  += " SET id_oty_fk = 3 WHERE name_prc = '%s'" %(self.procedurename)
        print >> sys.stderr, "sql: %s" %(sql)
        servicedb.execute(sql)
                 
        try:
            res.raise_for_status() # raise exception if som comunication error occured    
        except Exception as e:
            print str(e)
            
            
        if self.json['script'] == '': #HQ procedure
            init = """
from istsoslib.responders.GOresponse import VirtualProcess

class istvp(VirtualProcess):
    def __init__(self,filter,pgdb):
        #INIT Virtual Process
        VirtualProcess.__init__(self,filter,pgdb)
        #LOAD THE DATA
        self.data = self.setSOSobservationVar('""" + name + """','urn:ogc:def:parameter:x-istsos:1.0:hydro:river:water:discharge')
        self.hqCurves = self.setDischargeCurves('""" + name + """_HQ.dat')"""        
            
            exScript = """
    def execute(self):
        import datetime, decimal
        if self.filter.qualityIndex == True:
            data_out=[]
            for rec in self.data:
                for o in range(len(self.hqCurves['from'])):
                    if (self.hqCurves['from'][o] < rec[0] <= self.hqCurves['to'][o]) and (self.hqCurves['low'][o] < float(rec[1]) <= self.hqCurves['up'][o]):
                        data_out.append([ rec[0], "%.3f" %(self.hqCurves['K'][o] + self.hqCurves['A'][o]*((float(rec[1])-self.hqCurves['B'][o])**self.hqCurves['C'][o])), rec[2] ])
                        break
        else:
            data_out=[]
            for rec in self.data:
                for o in range(len(self.hqCurves['from'])):
                    if (self.hqCurves['from'][o] < rec[0] <= self.hqCurves['to'][o]) and (self.hqCurves['low'][o] < float(rec[1]) <= self.hqCurves['up'][o]):
                        data_out.append([ rec[0], "%.3f" %(self.hqCurves['K'][o] + self.hqCurves['A'][o]*((float(rec[1])-self.hqCurves['B'][o])**self.hqCurves['C'][o])) ])
                        break
        return data_out"""    
            
            
            j = self.serviceconf.servicecfgpath.index("services")            
            self.RCpath = self.serviceconf.servicecfgpath[1:j+8] + "/" + service + "/virtual/"
            self.RCfilename = self.RCpath + "/" + name + ".py"
            if not os.path.exists(self.RCpath):
                os.makedirs(self.RCpath)
            pyfile = open(self.RCfilename, 'a') #come recuperare il percorso? il file si chiama name.py
            pyfile.write(init + '\n\n' + exScript)
            pyfile.close()
                
            self.RCpath = self.serviceconf.discharges["virtual_HQ_folder"]
            self.RCfilename = self.RCpath + "/" + name + "_HQ.dat"
            if not os.path.exists(self.RCpath):
                os.makedirs(self.RCpath)
            pyfile = open(self.RCfilename, 'a') #come recuperare il percorso? il file si chiama name_HQ.py
            pyfile.write('from|to|low_val|up_val|A|B|C|K\n')
            pyfile.close()
            
        else: #new procedure
            init = """
from istsoslib.responders.GOresponse import VirtualProcess

class istvp(VirtualProcess):
    def __init__(self,filter,pgdb):
        #INIT Virtual Process
        VirtualProcess.__init__(self,filter,pgdb)
        #LOAD THE DATA
        self.data = self.setSOSobservationVar('""" + name + """','urn:ogc:def:parameter:x-istsos:1.0:hydro:river:water:discharge')
        self.hqCurves = self.setDischargeCurves('""" + name + """.dat')"""
            
            
            j = self.serviceconf.servicecfgpath.index("services")            
            self.RCpath = self.serviceconf.servicecfgpath[1:j+8] + "/" + service + "/virtual"
            self.RCfilename = self.RCpath + "/" + name + ".py"
            if not os.path.exists(self.RCpath):
                os.makedirs(self.RCpath)
            pyfile = open(self.RCfilename, 'a')
            pyfile.write(init + '\n\n' + self.json['script']['code'])
            pyfile.close()
            
            self.RCpath = self.serviceconf.servicecfgpath[1:j+8] + "/" + service + "/virtual/" + name
            self.RCfilename = self.RCpath + "/" + name + ".dat"
            if not os.path.exists(self.RCpath):
                os.makedirs(self.RCpath)
            pyfile = open(self.RCfilename, 'a')
            pyfile.write(self.json['script']['init'] + '\n')
            pyfile.close()
            
    def executeGet(self):
        import lib.requests as requests
        res = requests.get(
            self.serviceconf.serviceurl["url"], 
            params={
                "request": "DescribeSensor",
                "procedure": self.procedurename,
                "outputFormat": "text/xml;subtype='sensorML/1.0.0'",
                "service": "SOS",
                "version": "1.0.0"
            }
        )
        
        smlobj = procedure.Procedure()
        smlobj.loadXML(res.content)
        
        # Searching for the assignedSensorId from the database
        servicedb = databaseManager.PgDB(
            self.serviceconf.connection['user'],
            self.serviceconf.connection['password'],
            self.serviceconf.connection['dbname'],
            self.serviceconf.connection['host'],
            self.serviceconf.connection['port']
        )
        sql  = "SELECT assignedid_prc FROM %s.procedures " %((self.service,))
        sql  += " WHERE name_prc = %s and id_oty_fk = 3"
        rows = servicedb.select(sql,(self.procedurename,))
        if rows:
            ret = {
                'assignedSensorId': rows[0]["assignedid_prc"]
            }
            ret.update(smlobj.data) # merging dictionaries
            self.setData(ret)
            self.setMessage("Sensor Description secessfully loaded")
        else:
                self.setException("Unable to find the procedure's assignedSensorId")
                
    def executeDelete(self):
        if self.procedurename==None:
            raise Exception("DELETE action without url procedure name not supported")
        
        try:
            servicedb = databaseManager.PgDB(self.serviceconf.connection['user'],
                                            self.serviceconf.connection['password'],
                                            self.serviceconf.connection['dbname'],
                                            self.serviceconf.connection['host'],
                                            self.serviceconf.connection['port']
            )
            
            #DELETE from database in transaction
            sql  = "DELETE from %s.procedures" % self.service
            sql += " WHERE name_prc = %s"
            params = (self.procedurename,)
            servicedb.executeInTransaction(sql,params)
            
            #DELETE sensorML, file .py, content file
            
            k = self.pathinfo.index("services")
            service = self.pathinfo[k+1]
            k = self.pathinfo.index("virtualprocedures")
            name = self.pathinfo[k+1]            
            
            procedureMLpath = os.path.join(self.sensormlpath,self.procedurename+".xml")
            os.remove(procedureMLpath)
            
            j = self.serviceconf.servicecfgpath.index("services")            
            self.RCpath = self.serviceconf.servicecfgpath[1:j+8] + "/" + service + "/virtual/"
            self.RCfilename = self.RCpath + "/" + name + ".py"
            procedureMLpath = os.path.join(self.RCfilename) #file name.py
            os.remove(procedureMLpath)
            
            self.RCpath = self.serviceconf.servicecfgpath[1:j+8] + "/" + service + "/virtual/" + name
            shutil.rmtree(self.RCpath)
            
            #COMMIT transaction
            servicedb.commitTransaction()
            self.setMessage("Procedure '%s' successfully deleted" % self.procedurename)
        except Exception as e:
            self.setException("%s" %e)