# -*- coding: utf-8 -*-
# =============================================================================
#
# Authors: Massimiliano Cannata, Milan Antonovic
#
# Copyright (c) 2016 IST-SUPSI (www.supsi.ch/ist)
#
# This program is free software; you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation; either version 2 of the License, or (at your
# option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program; if not, write to the Free Software
# Foundation, Inc., 51 Franklin Street, Fifth Floor, Boston, MA  02110-1301 USA
#
# =============================================================================

__author__ = 'Milan Antonovic'
__copyright__ = 'Copyright (c) 2016 IST-SUPSI (www.supsi.ch/ist)'
__credits__ = []
__license__ = 'GPL2'
__version__ = '1.0'
__maintainer__ = 'Massimiliano Cannata, Milan Antonovic'
__email__ = 'milan.antonovic@gmail.com'

from istsoslib.filters import filter as f
from istsoslib import sosException
from lib.etree import et
import traceback
import sys
from filter_utils import parse_and_get_ns


class sosIOfilter(f.sosFilter):
    """Filter object for a InsertObservation request

    Attributes:
        request (str): the request submitted
        service (str): the name of the service requested
        version (str): the version of the service
        assignedSensorId (str): the requested sensor id
        forceInsert (bool): if True overrides existing observations falling in
                            the interval
        procedure (str): the name of the procedure
        oprName (list): the names of thr observed properties
        samplingTime (str): the time period of the observations to be inserted
        foiName (str): the name of the feature of featureOfInterest
        parameters (list): the ordered list of unit of the parameters
        uom (list): the ordered list of unit of minutes associated with
                    the parameters
        data (dict): a dictionary of parameter's dictionaries with unit of
                     minutes and values, e.g.:

        .. code::

            data = {
                "urn:ist:parameter:time:iso8601":
                    {
                        "uom":"sec",
                        "vals":["2009-07-31T12:00:00+02:00",
                                "2009-07-31T12:10:00+02:00",
                                "2009-07-31T12:20:00+02:00"]
                    },
                "urn:ist:def:phenomenon:rainfall":
                    {
                        "uom":"mm",
                        "vals":[0.1,0.2,0.3,0.4]
                    }
            }
    """
    def __init__(self, sosRequest, method, requestObject, sosConfig):
        f.sosFilter.__init__(self, sosRequest,
                             method, requestObject, sosConfig)
        if method == "GET":
            raise sosException.SOSException(
                "NoApplicableCode", None, "insertObservation request support "
                "only POST method!")

        if method == "POST":
            from StringIO import StringIO
            tree, ns = parse_and_get_ns(StringIO(requestObject))

            # Workaround for rare xml parsing bug in etree
            ns = {
                'gml': 'http://www.opengis.net/gml',
                'swe': 'http://www.opengis.net/swe',
                'om': 'http://www.opengis.net/om/1.0',
                'sos': 'http://www.opengis.net/sos/1.0',
                'xlink': 'http://www.w3.org/1999/xlink',
                'xsi': 'http://www.w3.org/2001/XMLSchema-instance'
            }

            if not 'swe' in ns:
                ns['swe'] = 'http://www.opengis.net/swe/1.0.1'

            # assignedSensorId
            AssignedSensorId = tree.find("{%s}AssignedSensorId" % ns['sos'])
            if AssignedSensorId is None:
                raise sosException.SOSException(
                    "MissingParameterValue",
                    "AssignedSensorId",
                    "sos:AssignedSensorId parameter is mandatory "
                    "with multiplicity 1")

            else:
                self.assignedSensorId = AssignedSensorId.text.split(":")[-1]

            # forceInsert
            ForceInsert = tree.find("{%s}ForceInsert" % ns['sos'])
            if not ForceInsert is None:
                if ForceInsert.text == 'true' or ForceInsert.text == "":
                    self.forceInsert = True

                elif ForceInsert.text == 'false':
                    self.forceInsert = False

                else:
                    err_txt = ("parameter \"ForceInsert\" can only be: "
                               "'true' or 'false'")
                    raise sosException.SOSException(
                        "InvalidParameterValue", "ForceInsert", err_txt)

            else:
                self.forceInsert = False

            # om:observation
            Observation = tree.find("{%s}Observation" % ns['om'])
            if Observation is None:
                raise sosException.SOSException(
                    "MissingParameterValue", "Observation",
                    "om:Observation tag is mandatory with multiplicity 1")

            # procedure
            procedure = Observation.find("{%s}procedure" % ns['om'])
            if procedure is None:
                raise sosException.SOSException(
                    "NoApplicableCode", None,
                    "om:procedure tag is mandatory with multiplicity 1")

            self.procedure = procedure.attrib[
                "{%s}href" % ns['xlink']].split(":")[-1]

            # ObservedProperties
            self.oprName = []
            observedProperty = Observation.find(
                "{%s}observedProperty" % ns['om'])
            if observedProperty is None:
                raise sosException.SOSException(
                    "NoApplicableCode", None,
                    "om:observedProperty tag is mandatory with multiplicity 1")

            CompositPhenomenon = observedProperty.find(
                "{%s}CompositePhenomenon" % ns['swe'])

            if not CompositPhenomenon is None:
                components = CompositPhenomenon.findall(
                    "{%s}component" % ns['swe'])
                for co in components:
                    try:
                        self.oprName.append(
                            co.attrib["{%s}href" % ns['xlink']])

                    except:
                        try:
                            name = co.find("{%s}name" % ns['gml'])
                            self.oprName.append(name.text)

                        except:
                            raise sosException.SOSException(
                                "NoApplicableCode", None,
                                "om:observedProperty Name is missing: "
                                "'xlink:href' or 'gml:name' required")

            else:
                try:
                    self.oprName.append(
                        observedProperty.attrib["{%s}href" % ns['xlink']])

                except:
                    try:
                        name = co.find("{%s}name" % ns['gml'])
                        self.oprName.append(name.text)

                    except:
                        print >> sys.stderr, "XML: %s" % requestObject
                        raise sosException.SOSException(
                            "NoApplicableCode", None,
                            "om:observedProperty Name is missing: "
                            "'xlink:href' or 'gml:name' required")

            # samplingTime
            samplingTime = Observation.find("{%s}samplingTime" % ns['om'])
            if samplingTime is None:
                raise sosException.SOSException(
                    "NoApplicableCode", None,
                    "om:samplingTime is mandatory in multiplicity 1")

            TimePeriod = samplingTime.find("{%s}TimePeriod" % ns['gml'])
            if not TimePeriod is None:
                bp = TimePeriod.find("{%s}beginPosition" % ns['gml'])
                ep = TimePeriod.find("{%s}endPosition" % ns['gml'])
                if bp is None or ep is None:
                    raise sosException.SOSException(
                        "NoApplicableCode", None,
                        "gml:TimePeriod is mandatory in multiplicity 1")
                self.samplingTime = bp.text + "/" + ep.text

            else:
                TimeInstant = samplingTime.find("{%s}TimeInstant" % ns['gml'])
                if not TimeInstant is None:
                    tpos = TimeInstant.find("{%s}timePosition" % ns['gml'])
                    self.samplingTime = tpos.text

                else:
                    raise sosException.SOSException(
                        "NoApplicableCode", None,
                        "one of gml:TimePeriod or gml:TimeInstant "
                        "is mandatory in multiplicity 1")

            # featureOfInterest
            featureOfInterest = Observation.find(
                "{%s}featureOfInterest" % ns['om'])
            if featureOfInterest is None:
                raise sosException.SOSException(
                    "NoApplicableCode", None,
                    "om:featureOfInterest tag is mandatory with "
                    "multiplicity 1")
            try:
                self.foiName = featureOfInterest.attrib[
                    "{%s}href" % ns['xlink']].split(":")[-1]

            except:
                try:
                    gml_name = featureOfInterest.find(
                        "{%s}name" % ns['gml']).split(":")[-1]
                    self.foiName = gml_name.text

                except:
                    raise sosException.SOSException(
                        "NoApplicableCode", None,
                        "om:featureOfInterest name is missing: 'xlink:href' "
                        "or 'gml:name' is required")

            # result
            if Observation.find("{%s}result" % ns['om']) is None:
                raise sosException.SOSException(
                    "NoApplicableCode", None,
                    "om:result tag is required")

            SimpleDataRecord = Observation.find(
                "{%s}result/{%s}SimpleDataRecord" % (ns['om'], ns['swe']))
            DataArray = Observation.find(
                "{%s}result/{%s}DataArray" % (ns['om'], ns['swe']))

            ###################################################################
            # RESULT
            # return self.data where self.data is a dictionary of "definition"
            # containing dictionary of "uom" and "vals"
            #""" e.g.:
            #self.data = {
            #            "urn:ist:parameter:time:iso8601":
            #                {
            #                "uom":"sec",
            #                "vals":[
            #                   "2009-07-31T12:00:00+02:00",
            #                   "2009-07-31T12:10:00+02:00",
            #                   "2009-07-31T12:20:00+02:00"]
            #                },
            #            "urn:ist:def:phenomenon:rainfall":
            #                {
            #                "uom":"mm",
            #                "vals":[0.1,0.2,0.3,0.4]
            #                }
            #            }
            #
            ###################################################################

            self.parameters = []
            self.uoms = []
            self.data = {}

            #case SimpleDataRecord
            if not SimpleDataRecord is None and DataArray is None:
                fields = SimpleDataRecord.findall("{%s}field" % ns['swe'])
                for field in fields:
                    defin = None
                    uom = None
                    vals = []
                    fieldName = field.attrib["name"]
                    if not field.find("{%s}Time" % ns['swe']) is None:
                        tf = field.find("{%s}Time" % ns['swe'])
                        defin = tf.attrib["definition"]
                        vals.append(tf.find("{%s}value" % ns['swe']).text)

                    elif not field.find("{%s}Quantity" % ns['swe']) is None:
                        qf = field.find("{%s}Quantity" % ns['swe'])
                        defin = qf.attrib["definition"]
                        uom = qf.find("{%s}uom" % ns['swe']).attrib["code"]
                        vals.append(qf.find("{%s}value" % ns['swe']).text)

                    else:
                        raise sosException.SOSException(
                            "NoApplicableCode", None,
                            "swe:Time or swe:Quantity is mandatory in "
                            "multiplicity 1")

                    self.data[defin] = {
                        "uom": uom,
                        "vals": vals
                    }

            # Case DataArray
            elif SimpleDataRecord is None and not DataArray is None:
                DataRecord = DataArray.find(
                    "{%s}elementType/{%s}DataRecord" % (ns['swe'], ns['swe']))
                fields = DataRecord.findall("{%s}field" % ns['swe'])
                urnlist = []
                for id, field in enumerate(fields):
                    defin = None
                    uom = None
                    vals = []
                    #fieldName = field.attrib["name"]
                    if not field.find("{%s}Time" % ns['swe']) is None:
                        swet = field.find("{%s}Time" % ns['swe'])
                        defin = swet.attrib["definition"]
                        urnlist.append(swet.attrib["definition"])

                    elif not field.find("{%s}Quantity" % ns['swe']) is None:
                        sweq = field.find("{%s}Quantity" % ns['swe'])
                        defin = sweq.attrib["definition"]
                        urnlist.append(sweq.attrib["definition"])
                        if not sweq.find("{%s}uom" % ns['swe']) is None:
                            uom = sweq.find(
                                "{%s}uom" % ns['swe']).attrib["code"]

                    else:
                        raise sosException.SOSException(
                            "NoApplicableCode", None,
                            "swe:Time or swe:Quantity is mandatory in "
                            "multiplicity 1")

                    self.data[defin] = {
                        "uom": uom,
                        "vals": vals
                    }

                # encoding
                encodingTxtBlock = Observation.find(
                    "{%s}result/{%s}DataArray/{%s}encoding/{%s}TextBlock" % (
                        ns['om'], ns['swe'], ns['swe'], ns['swe']))
                if encodingTxtBlock is None:
                    raise sosException.SOSException(
                        "NoApplicableCode", None,
                        "swe:encoding is mandatory in multiplicity 1")

                tokenSeparator = encodingTxtBlock.attrib["tokenSeparator"]
                blockSeparator = encodingTxtBlock.attrib["blockSeparator"]

                values = Observation.find(
                    "{%s}result/{%s}DataArray/{%s}values" % (
                        ns['om'], ns['swe'], ns['swe']))

                if values is None:
                    raise sosException.SOSException(
                        "NoApplicableCode", None,
                        "swe:values is mandatory in multiplicity 1")

                self.dataArray = []
                if values.text:
                    valsplit = [
                        i.split(tokenSeparator) for i in values.text.split(
                            blockSeparator)]
                    self.dataArray = valsplit
                    for index, c in enumerate(urnlist):
                        col = []
                        for l in valsplit:
                            col.append(l[index])
                        self.data[c]["vals"] = col

            # case simple om:result
            elif SimpleDataRecord is None and DataArray is None:
                self.data[sosConfig.urn["time"]] = {
                    "uom": None,
                    "vals": [self.samplingTime]
                }
                result = Observation.find("{%s}result" % (ns['om']))
                uom = result.attrib["uom"]
                vals = result.text
                self.data[sosConfig.urn["phenomena"]+self.oprName] = {
                    "uom": uom,
                    "vals": vals
                }
                self.dataArray = [
                    [self.samplingTime, vals]
                ]

            # error
            else:
                raise sosException.SOSException(
                    "NoApplicableCode", None,
                    "om:SimpleDataRecord in multiplicity N or om:DataArray "
                    "in multiplicity 1 is mandatory")
