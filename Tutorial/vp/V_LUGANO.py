from istsoslib.responders.GOresponse import VirtualProcess

class istvp(VirtualProcess):

    procedures = {
        "T_LUGANO": "urn:ogc:def:parameter:x-istsos:1.0:meteo:air:temperature"
    }
    
    def execute(self):
        data = self.getData("T_LUGANO")
        out=[]
        for idx in range(len(data)):
            rec = data[idx]
            if self.filter.qualityIndex == True:
                out.append([rec[0], self.convert(rec[1]), rec[2]])
            else:
                out.append([rec[0], self.convert(rec[1])])
      	return out
    
    def convert(self, celsius):
        if celsius is None:
            return -999.9
        return (float(celsius) *1.8 + 32)
