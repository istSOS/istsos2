from istsoslib.responders.GOresponse import VirtualProcess
import FAO56

class istvp(VirtualProcess):
    procedures = {
        "GRABOW": [
            "urn:ogc:def:parameter:x-istsos:1.0:meteo:air:temperature",
            "urn:ogc:def:parameter:x-istsos:1.0:meteo:air:humidity:relative",
            "urn:ogc:def:parameter:x-istsos:1.0:meteo:air:wind:velocity",
            "urn:ogc:def:parameter:x-istsos:1.0:meteo:solar:radiation"
        ]
    }
    def execute(self):
        data = self.getData("GRABOW")
        data_out = []
        for rec in data:
            if self.filter.qualityIndex == True:
                # rec is a list:
                # [0]=time, [1]=T,[2]=Tqi, [3]=RH,[4]=RHqi,
                # [5]=u2,[6]=u2qi, [7]=Rs,[8]=Rsqi
                etp = FAO56.ET0(isodate = str(rec[0]),
                T=float(rec[1]),
                RH=float(rec[3]),
                u2=float(rec[5]),
                Rs=float(rec[7])*0.0036, # W/m2 to MJ/(m2*h)
                lat=22.67,
                lon=51.25,
                z=177)
                data_out.append([rec[0], etp, min([rec[2],rec[4],rec[6],rec[8]])])
            else:
                # rec is a list: [0]=time,[1]=T,[2]=RH,[3]=u2,[4]=Rs
                etp = FAO56.ET0(isodate = str(rec[0]),
                T=float(rec[1]),
                RH=float(rec[2]),
                u2=float(rec[3]),
                Rs=float(rec[4])*0.0036,
                lat=22.67,
                lon=51.25,
                z=177)
                data_out.append([rec[0], etp])
        return data_out
