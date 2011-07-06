
class VirtualProcess():
    def execute():
        raise Exception("function execute must be overridden")
        
    def setSOSobservation(self,proc,prop):
        "method for setting a real observation input"
        self.filter.procedure = [proc]
        self.filter.observedProperty = [prop]
        
        #CRETE OBSERVATION OBJECT
        #=================================================
        ob = observation()
        
        #BUILD BASE INFOS FOR REQUIRED PROCEDURE
        #=================================================
        sqlSel = "SELECT DISTINCT"
        sqlSel += " id_prc, name_prc, name_oty, stime_prc, etime_prc, time_res_prc, name_tru"
        
        sqlFrom = "FROM %s.procedures, %s.proc_obs p, %s.observed_properties, %s.uoms, %s.time_res_unit," %(sosConfig.schema,sosConfig.schema,sosConfig.schema,sosConfig.schema,sosConfig.schema)
        sqlFrom += " %s.off_proc o, %s.offerings, %s.obs_type" %(sosConfig.schema,sosConfig.schema,sosConfig.schema)
        
        sqlWhere = "WHERE id_prc=p.id_prc_fk AND id_opr_fk=id_opr AND o.id_prc_fk=id_prc AND id_off_fk=id_off AND id_uom=id_uom_fk AND id_tru=id_tru_fk AND id_oty=id_oty_fk"
        sqlWhere += " AND name_off='%s' AND name_prc='%s' AND name_opr='%s'" %(myfilter.offering,myfilter.procedure,myfilter.observedProperty)
        try:
            o = pgdb.select(sqlSel + " " + sqlFrom + " " + sqlWhere)[0]
        except:
            raise sosException.SOSException(3,"SQL: %s"%(sqlSel + " " + sqlFrom + " " + sqlWhere))    
        
        ob.baseInfo(pgdb,o)
        
        #GET DATA FROM PROCEDURE ACCORDING TO THE FILTERS
        #=================================================
        ob.setData(pgdb,o,myfilter)
        
        return ob.data 
        
    def setDischargeTables(self,hqConfigFile):
        "method for setting h-q tranformation tables/curves"
        
        
        
        
        filter.eventTime
        
        
        
