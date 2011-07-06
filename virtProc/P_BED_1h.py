
from istSOS.responders.GOresponse import VirtualProcess
import isodate as iso
import  decimal, pytz
from datetime import timedelta,datetime

class istvp(VirtualProcess):
    def __init__(self,filter,pgdb):
        VirtualProcess.__init__(self,filter,pgdb)
        
        self.d = timedelta(hours=1)
        
        #set time filter to get the complete first requested hour
        if self.filter.eventTime:
            if len(self.filter.eventTime) > 1:
                raise Exception("virtual procedures with aggregated values do not support multiple tijme intervals!")
            if len(self.filter.eventTime[0]) == 2:
                self.filter.eventTime[0][0] = iso.datetime_isoformat(iso.parse_datetime(self.filter.eventTime[0][0]).replace(minute=0, second=0, microsecond=0))
            if len(self.filter.eventTime[0]) == 1:
                self.filter.eventTime[0][0] = iso.datetime_isoformat(iso.parse_datetime(self.filter.eventTime[0][0]).replace(minute=0, second=0, microsecond=0)-self.d)
                self.filter.eventTime[0][1] = iso.datetime_isoformat(iso.parse_datetime(self.filter.eventTime[0][0]).replace(minute=0, second=0, microsecond=0))
        
        #SET THE INPUTS      
        (self.pioggia,self.st) = self.setSOSobservationVar("P_BED","rainfall",True)
        
        if not self.filter.eventTime:
            self.filter.eventTime = [[None,None]]
            ot = self.st[1].replace(minute=0, second=0, microsecond=0)
            self.filter.eventTime[0][0] = iso.datetime_isoformat(ot-self.d)
            self.filter.eventTime[0][1] = iso.datetime_isoformat(ot)
            #reset the inputs
            (self.pioggia,self.st) = self.setSOSobservationVar("P_BED","rainfall",True)
        
        self.st[0] = self.st[0].replace(minute=0, second=0, microsecond=0) + self.d
        self.st[1] = self.st[1].replace(minute=0, second=0, microsecond=0)
        
    def execute(self):
        
        data_out=[]
        valdef=0.0
        
        if iso.parse_datetime(self.filter.eventTime[0][0]).tzinfo:
            ts = iso.parse_datetime(self.filter.eventTime[0][0]).astimezone(pytz.utc)
            te = iso.parse_datetime(self.filter.eventTime[0][1]).astimezone(pytz.utc)
        else:
            ts = iso.parse_datetime(self.filter.eventTime[0][0])
            te = iso.parse_datetime(self.filter.eventTime[0][1])
        
        #ensure returned data are in observed period
        te = min([te,self.st[1]])
        ts = max([ts,self.st[0]])
        
        i = 0
        
        while ts <= te-self.d:            
            data_out.append([ts+self.d,valdef])
            while i < len(self.pioggia):
                if self.pioggia[i][0] <= ts+self.d:
                    data_out[-1][1] += float(self.pioggia[i][1])
                    i += 1 
                if i >= len(self.pioggia) or self.pioggia[i][0] > ts+self.d:
                    break
            ts = ts+self.d
        
        return data_out     

    def setsamplingTime(self):
        return self.st
