from walib.resource import waResourceService
from walib import databaseManager

class waLogs(waResourceService):
    
    def __init__(self,waEnviron):
        waResourceService.__init__(self,waEnviron)
        self.setData("")
        
    def executeGet(self):
        """
        Method for executing a GET requests        
        
        Request:
            (...)/istsos/wa/istsos/<service name>/logs/?message=TypeError
                                                        &element=T_TREVANO
                                                        &stime=2013-01-01T00:08:00.000000%2B0100
                                                        &etime=2013-01-01T00:11:00.000000%2B0100
                                                        &process=acquisition
        The response is:
        {
                 [
                    {
                        "process": "acquisition",
                        "element": "T_TREVANO",
                        "datetime": "2013-01-01T00:10:00.000000+0100",
                        "message": "TypeError",
                        "details": "Error parsing line 200",
                        "status": "pending"
                    },
                    {
                        "process": "...",
                        "element": "...",
                        "datetime": "...",
                        "message": "...",
                        "details": "...",
                        "status": "verified"
                    }
                ] 
            }
                
        """
        if self.service == "default":
            raise Exception("logs operation can not be done for default service instance.")
        
        servicedb = databaseManager.PgDB(
            self.serviceconf.connection['user'],
            self.serviceconf.connection['password'],
            self.serviceconf.connection['dbname'],
            self.serviceconf.connection['host'],
            self.serviceconf.connection['port']) 
       
        params = self.waEnviron['parameters']
        par = ()  
        
        sql = """SELECT datetime_clo, * FROM %s.cron_log, %s.procedures """ % (self.service, self.service)
        sql += " WHERE id_prc_fk = id_prc "
        
        # where
        if not params == None:
            keyList = params.keys()
            
            if 'message' in keyList:
                sql += " AND ( message_clo = %s) "
                par += (params['message'][0],)
                
                            
            if 'stime' in keyList:
                sql += " AND  (datetime_clo > %s::timestamptz)"
                par += (params['stime'][0],)
                
            if 'etime' in keyList:
                sql += " AND  (datetime_clo < %s::timestamptz)"
                par += (params['etime'][0],)  
            
            if 'process' in keyList:
                sql += " AND  (process_clo = %s )"
                par += (params['process'][0],)
                    
            if 'element' in keyList:
                sql += " AND  (element_clo = %s )"          
                par += (params['element'][0],)
            
            if 'status' in keyList:                
                if params['status'][0] in ('verified','pending'):
                    sql+= " AND (status_clo = %s)"
                    par += (params['status'][0],)
                else:  
                    raise Exception("Status %s not supported." % params['status'][0])
        
        # Sort by date            
        sql += " ORDER BY datetime_clo DESC;"     
        
        exceptions = servicedb.select(sql,par)
        
        data = []           
        for exc in exceptions:
            data.append(
                    {
                        "process" : exc['process_clo'],
                        "element" : exc['element_clo'],
                        "datetime": str(exc['datetime_clo']),
                        "message" : exc['message_clo'],
                        "details" : exc['details_clo'],
                        "status"  : exc['status_clo'],
                        "id"      : exc['id_clo']
                    }
            )
        
        self.setMessage("logs result")
        self.setData(data)                
            
     
    def executePost(self):
        """
        Method for executing a POST requests that insert a new exception       
         {
                "process": "acquisition",
                "element": "T_TREVANO",
                "datetime": "2013-01-01T00:10:00.000000+0100",
                "message": "TypeError",
                "details": "Error parsing line 200"                       
        }
        """
      
                
        if self.service == "default":
            raise Exception("Logs operation can not be done for default service instance.")
        
        servicedb = databaseManager.PgDB(
            self.serviceconf.connection['user'],
            self.serviceconf.connection['password'],
            self.serviceconf.connection['dbname'],
            self.serviceconf.connection['host'],
            self.serviceconf.connection['port'])  
            
        #TODO: Add a error code to the table? 
        #check if exception exist   
            
            
        # Get procedure id
        sql = "SELECT id_prc FROM %s.procedures WHERE " % self.service
        sql += "name_prc = %s;"
        par = (self.json['element'],)

        procId = servicedb.execute(sql,par)

        if(len(procId) != 1):
            raise Exception("Procedure %s not found." % (self.json['element'])) 
        
        sql = "INSERT INTO %s.cron_log(process_clo, element_clo, datetime_clo,message_clo,details_clo,id_prc_fk, status_clo)" % self.service
        sql += " VALUES (%s, %s, %s, %s, %s, %s, %s);"
        par = (self.json['process'], self.json['element'],self.json['datetime'],self.json['message'],self.json['details'], procId[0][0],'pending')
        servicedb.execute(sql,par)
        self.setMessage("Added exception")   
        
        
    def executePut(self):
        """
            Method for executing a PUT requests that update the status of a  exception  
            Update a exception status
            
            {
                "id" : 1,
                "newstatus" : "verified"                       
            }
        """        
        if self.service == "default":
            raise Exception("Logs operation can not be done for default service instance.")    
        
        servicedb = databaseManager.PgDB(
            self.serviceconf.connection['user'],
            self.serviceconf.connection['password'],
            self.serviceconf.connection['dbname'],
            self.serviceconf.connection['host'],
            self.serviceconf.connection['port'])  
            
            
        if(self.json['newstatus'] == None or self.json['id'] == None):
            raise Exception("Not params.") 
            
        
        sql = "UPDATE %s.cron_log SET" % self.service
        sql += " status_clo = %s WHERE id_clo = %s"
        par = (self.json['newstatus'],self.json['id'])
        servicedb.execute(sql,par)
        self.setMessage("Status changed")   
        
        
    def executeDelete(self):
        """
             Method for executing a DELETE requests that remove a exception  
            (...)/istsos/wa/istsos/<service name>/logs?id=1
        """        
        if self.service == "default":
            raise Exception("Logs operation can not be done for default service instance.")    
        
        servicedb = databaseManager.PgDB(
            self.serviceconf.connection['user'],
            self.serviceconf.connection['password'],
            self.serviceconf.connection['dbname'],
            self.serviceconf.connection['host'],
            self.serviceconf.connection['port'])  
            
        idexc = self.waEnviron['parameters']['id'][0]    
        
        if(idexc == None):
            raise Exception("No exception id specified")
            
        sql = "DELETE FROM %s.cron_log" % self.service
        sql += " WHERE id_clo = %s"
        par = (idexc,)
        servicedb.execute(sql,par)
        self.setMessage("Exception removed")   