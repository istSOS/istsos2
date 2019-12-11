import configparser
config = configparser.RawConfigParser()

import os
import fnmatch

configFiles = [
    os.path.join(dirpath, f)
    for dirpath, dirnames, files in os.walk('services/')
    for f in fnmatch.filter(files, '*.cfg')]

config = configparser.RawConfigParser()


def add_config_options(options):
    """
    options = [
        ['section_1', 'option_1'],
        ['section_1', 'option_2'],
        ['section_2', 'option_1']
    ]
    """
    for configFile in configFiles:
        print("Working on %s" % configFile)
        config.read(configFile)
        for option in options:
            if config.has_section(option[0]) and not config.has_option(
                    option[0], option[1]):
                print(" > Setting option '%s'" % option[1])
                config.set(option[0], option[1])


for configFile in configFiles:
    print("Working on %s" % configFile)
    config.read(configFile)

    try:
        config.get('serviceType', 'default_version')
    except configparser.NoOptionError:
        config.set('serviceType', 'default_version', '1.0.0')
    except configparser.NoSectionError:
        pass

    try:
        config.get('getobservation', 'strictOGC')
    except configparser.NoOptionError:
        config.set('getobservation', 'strictOGC', False)
    except configparser.NoSectionError:
        pass

    try:
        config.get('parameters', 'DS_outputFormats_2_0_0')
    except configparser.NoOptionError:
        config.set(
            'parameters', 'DS_outputFormats_2_0_0',
            'http://www.opengis.net/sensorML/1.0.1')
    except configparser.NoSectionError:
        pass

    try:
        config.get('parameters', 'GC_Section_2_0_0')
    except configparser.NoOptionError:
        config.set(
            'parameters', 'GC_Section_2_0_0',
            'serviceidentification,serviceprovider,'
            'operationsmetadata,contents,filtercapabilities,all')
    except configparser.NoSectionError:
        pass

    try:
        config.get('parameters', 'GO_responseFormat_2_0_0')
    except configparser.NoOptionError:
        config.set(
            'parameters', 'GO_responseFormat_2_0_0',
            'http://www.opengis.net/om/2.0,text/plain')
    except configparser.NoSectionError:
        pass

    try:
        config.get('parameters', 'GO_responseFormat_2_0_0')
    except configparser.NoOptionError:
        config.set(
            'parameters', 'GO_responseFormat_2_0_0',
            'http://www.opengis.net/om/2.0,text/plain')
    except configparser.NoSectionError:
        pass

    with open(configFile, 'wb') as theFile:
        config.write(theFile)
