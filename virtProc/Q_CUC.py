
from istSOS.responders.GOresponse import VirtualProcess

class istvp(VirtualProcess):
    def __init__(self,filter,pgdb):
        VirtualProcess.__init__(self,filter,pgdb)
        
        #SET THE INPUTS      
        self.altezza = self.setSOSobservationVar("A_CUC","riverheight")
        
        self.hqCurves = self.setDischargeCurves("A_CUC_HQ.dat")
        
        
            
        
    
    def execute(self):
        import datetime, decimal
        
        data_out=[]
        
        stri=""
        
        for rec in self.altezza:
            for o in range(len(self.hqCurves['from'])):                
                if (self.hqCurves['from'][o] < rec[0] <= self.hqCurves['to'][o]) and (self.hqCurves['low'][o] < float(rec[1]) <= self.hqCurves['up'][o]):
                    data_out.append([ rec[0], "%.3f" %(self.hqCurves['K'][o] + self.hqCurves['A'][o]*((float(rec[1])-self.hqCurves['B'][o])**self.hqCurves['C'][o])) ])
                    break
        
        return data_out     

