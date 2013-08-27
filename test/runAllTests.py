# -*- coding: utf-8 -*-

import istsos.services.configsections as conf
import istsos.services.dataqualities as data
import istsos.services.epsgs as eps
import istsos.services.observedproperties as obsprop
import istsos.services.offerings as offer
import istsos.services.operations as oper
import istsos.services.procedures as proc
import istsos.services.services as ser
import istsos.services.systemtypes as syst
import istsos.services.uoms as uom
import istsos.services.sosRequests as sos
import lib.argparse as argparse

def run_tests(arg):
    
    verb = arg['v']
    
    if verb:
        f = open('/home/priska/Desktop/log.txt', 'w')
    else:
        f = None
        
    print '\n-----------------getCapabilities----------------------------\n'
    getCapabilities = sos.getCapabilities(f, verb)
    print '\n-----------------describeSensor-----------------------------\n'
    describeSensor = sos.describeSensor(f, verb)
    print '\n-----------------getObservation-----------------------------\n'
    getObservation = sos.getObservation(f, verb)
    print '\n-----------------registerSensor-----------------------------\n'
    registerSensor = sos.registerSensor(f, verb)
    print '\n-----------------insertObservation--------------------------\n'
    insertObservation = sos.insertObservation(f, verb)
    print '\n-----------------getFeatureOfInterest-----------------------\n'
    featureofInterest = sos.getFeatureOfInterest(f, verb)
    
    
    dataqualities = data.test_dataqualities(f, verb)
    epsgs = eps.test_epsgs(f, verb)
    observedproperties = obsprop.test_observedproperties(f, verb)
    offerings = offer.test_offerings(f, verb)
    operations = oper.test_operations(f, verb)
    procedures = proc.test_procedures(f, verb)
    services = ser.test_services(f, verb)
    systemtypes = syst.test_systemtypes(f, verb)
    uoms = uom.test_uoms(f, verb)
#    configsections = conf.test_configsections(f, verb)


    if verb:
        f.close()
    
    print '\n#############################################################'
    print '------------------------Failed tests:------------------------'
    print '#############################################################'
    
#    print '\nConfigsections:'
#    for el in configsections:
#        if not configsections[el]:
#            print el
#        
    print '\nDataqualities:'
    for el in dataqualities:
        if not dataqualities[el]:
            print el
        
    print '\nEpsgs:'
    for el in epsgs:
        if not epsgs[el]:
            print el
      
    print '\nObservedproperties:'
    for el in observedproperties:
        if not observedproperties[el]:
            print el
        
    print '\nOfferings:'
    for el in offerings:
        if not offerings[el]:
            print el
        
    print '\nOperations:'
    for el in operations:
        if not operations[el]:
            print el
        
    print '\nProcedures:'
    for el in procedures:
        if not procedures[el]:
            print el
        
    print '\nServices:'
    for el in services:
        if not services[el]:
            print el
      
    print '\nSystemtypes:'
    print 'services/name/systemtypes non é implementato'
#    for el in systemtypes:
#        if not systemtypes[el]:
#            print el
        
    print '\nUoms:'
    for el in uoms:
        if not uoms[el]:
            print el

    print '\ngetCapabilities:'
    for el in getCapabilities:
        if not getCapabilities[el]:
            print el

    print '\ndescribeSensor:'
    for el in describeSensor:
        if not describeSensor[el]:
            print el

    print '\ngetObservation:'
    for el in getObservation:
        if not getObservation[el]:
            print el

    print '\nregisterSensor:'
    for el in registerSensor:
        if not registerSensor[el]:
            print el

    print '\ninsertObservation:'
    for el in insertObservation:
        if not insertObservation[el]:
            print el

    print '\ngetFeatureOfInterest:'
    for el in featureofInterest:
        if not featureofInterest[el]:
            print el
            


if __name__ == "__main__":

    parser = argparse.ArgumentParser(
        description='Import data from a csv file.')
    
    parser.add_argument('-v','--verbose',
        action = 'store_true',
        dest   = 'v',
        help   = 'Activate verbose debug')
        
    args = parser.parse_args()
    run_tests(args.__dict__)