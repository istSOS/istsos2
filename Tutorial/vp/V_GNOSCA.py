from istsoslib.responders.GOresponse import VirtualProcessHQ
class istvp(VirtualProcessHQ):
    procedures = {
        "RH_GNOSCA": "urn:ogc:def:parameter:x-istsos:1.0:river:water:height"
    }
