
def arduinoWns():
    import datetime
    import time
    from pytz import timezone
    from tzlocal import get_localzone
    now = datetime.datetime.now(get_localzone())#.replace(tzinfo=timezone(time.tzname[0]))
    endDate = now.strftime('%Y-%m-%dT%H:%M:%S%z')
    eventTime = now - datetime.timedelta(hours=1)
    startDate = eventTime.strftime('%Y-%m-%dT%H:%M:%S%z')

    rparams = {"service": "SOS",
            "offering": "temporary", 
            "request": "GetObservation",
            "version": "1.0.0",
            "responseFormat": "application/json",
            "observedProperty": "air:heat:index,air:humidity,air:temperature",
            "procedure": "ARDUINO",
            "aggregateInterval": "PT10M",
            "aggregateFunction": "MAX"
    }
    rparams['eventTime'] = str(startDate) + "/" +str(endDate)

    
    print "getObservation from: ", startDate, " to: ", endDate

    import requests
    res = requests.get('http://localhost/istsos/demo', params=rparams)

    result = res.json()['ObservationCollection']['member'][0]


    values = result['result']['DataArray']['values']

    if len(values) == 0:
        print "no data"
        return 

    T = float(values[-1][3])
    RH = float(values[-1][2])
    index = float(values[-1][1])
   

    print T, ' ', RH, ' ', index
    
    if T < 27 or RH < 40 or index <=27:
        print "Not all values"
        print  "temp must be > 27"
        return

    if index <= 32:
        message = "caution " # level 2
    elif index <= 40 and index > 32:
        message = "Extreme caution " # level 3
    elif index  <= 54 and index > 40:
        message = "Danger" # level 4
    elif index > 54:
        message = "Extreme Danger " # level 5

    print message


    import wnslib.notificationScheduler as nS    
    mail_message = "alarm heat wave: " + message + " a Trevano"

    notify = {
        "twitter": {
            "public": mail_message,
            "private": mail_message
        },
        "mail": {
            "subject": "Allarme canicola",
            "message": mail_message
        }
    }

    nS.notify('arduinoWns',notify, False)
