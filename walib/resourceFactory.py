# -*- coding: utf-8 -*-
# ===============================================================================
#
# Authors: Massimiliano Cannata, Milan Antonovic
#
# Copyright (c) 2015 IST-SUPSI (www.supsi.ch/ist)
#
# This program is free software; you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation; either version 2 of the License, or (at your option)
# any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program; if not, write to the Free Software
# Foundation, Inc., 51 Franklin Street, Fifth Floor, Boston, MA  02110-1301  USA
#
# ===============================================================================
import sys, re
import copy
def initResource(waEnviron):
    path = waEnviron['path']
    # ---------------
    # Entering istsos
    # ---------------
    pathinfo = copy.deepcopy(waEnviron['pathinfo'])
    resource = pathinfo.pop(0)
    #print >> sys.stderr, resource

    if resource == "istsos":

        '''if 'user' in waEnviron and not waEnviron['user'].isAdmin():
            from walib import users
            return users.waUserUnauthorized(waEnviron)'''

        resource = pathinfo.pop(0)

        # --------------------------
        # Entering istsos.operations
        # --------------------------
        if resource == "operations":
            resource = pathinfo.pop(0)

            if resource == "status":
                from walib.istsos import istsos
                return istsos.waStatus(waEnviron)
            elif resource == "log":
                from walib.istsos import istsos
                return istsos.waLog(waEnviron)
            elif resource == "about":
                from walib.istsos import istsos
                return istsos.waAbout(waEnviron)
            elif resource == "validatedb":
                from walib.istsos import istsos
                return istsos.waValidatedb(waEnviron)
            ''' checking if not need any more
            elif resource == "initialization":
                from walib.istsos import istsos
                return istsos.waInitialization(waEnviron)'''

        # --------------------------
        # Entering istsos.services
        # --------------------------
        elif resource == "services":
            #print >> sys.stderr, resource

            if len(pathinfo) <= 1:
                from walib.istsos.services import services
                return services.waServices(waEnviron)
            else:
                pathinfo.pop(0)
                resource = pathinfo.pop(0)

                # Entering istsos.services.configsections
                if resource == "configsections":
                    #print >> sys.stderr, resource

                    if len(pathinfo) == 0:
                        from walib.istsos.services.configsections import configsections
                        return configsections.waConfigsections(waEnviron)
                    else:
                        resource = pathinfo.pop(0)
                        #print >> sys.stderr, resource
                        if resource == "connection":
                            if len(pathinfo)==0:
                                from walib.istsos.services.configsections import connection
                                return connection.waConnection(waEnviron)
                            else:
                                resource = pathinfo.pop(0)
                                #print >> sys.stderr, resource
                                if resource == "operations":
                                    resource = pathinfo.pop(0)
                                    #print >> sys.stderr, resource
                                    if resource == "validatedb":
                                        from walib.istsos.services.configsections import connection
                                        return connection.waValidatedb(waEnviron)

                        elif resource == "getobservation":
                            from walib.istsos.services.configsections import getobservation
                            return getobservation.waGetobservation(waEnviron)
                        elif resource == "paths":
                            from walib.istsos.services.configsections import paths
                            return paths.waPaths(waEnviron)
                        elif resource == "authority":
                            from walib.istsos.services.configsections import authority
                            return authority.waAuthority(waEnviron)
                        elif resource == "identification":
                            from walib.istsos.services.configsections import identification
                            return identification.waIdentification(waEnviron)
                        elif resource == "geo":
                            from walib.istsos.services.configsections import geo
                            return geo.waGeo(waEnviron)
                        elif resource == "serviceurl":
                            from walib.istsos.services.configsections import serviceurl
                            return serviceurl.waServiceurl(waEnviron)
                        elif resource == "provider":
                            from walib.istsos.services.configsections import provider
                            return provider.waProvider(waEnviron)
                        elif resource == "urn":
                            from walib.istsos.services.configsections import urn
                            return urn.waUrn(waEnviron)
                        elif resource == "mqtt":
                            from walib.istsos.services.configsections import mqtt
                            return mqtt.waMqtt(waEnviron)

                # ---------------------------------------
                # Entering istsos.services.dataqualities
                # ---------------------------------------
                elif resource == "dataqualities":
                    #print >> sys.stderr, resource
                    from walib.istsos.services.dataqualities import dataqualities
                    return dataqualities.waDataqualities(waEnviron)

                # ---------------------------------------
                # Entering istsos.services.procedures
                # ---------------------------------------
                elif resource == "procedures":
                    #print >> sys.stderr, resource

                    if len(pathinfo) <= 1:
                        from walib.istsos.services.procedures import procedures
                        return procedures.waProcedures(waEnviron)

                    else:

                        resource = pathinfo.pop(0)
                        #print >> sys.stderr, resource

                        if resource == 'operations':
                            resource = pathinfo.pop(0)
                            #print >> sys.stderr, resource

                            if resource == "getlist":
                                from walib.istsos.services.procedures import procedures
                                return procedures.waGetlist(waEnviron)

                            elif resource == "geojson":
                                from walib.istsos.services.procedures import procedures
                                return procedures.waGetGeoJson(waEnviron)

                # ---------------------------------------
                # Entering istsos.services.virtualprocedures
                # ---------------------------------------
                elif resource == "virtualprocedures":
                    #print >> sys.stderr, resource

                    if len(pathinfo)<=1:
                        from walib.istsos.services.virtualprocedures import virtualprocedures
                        return virtualprocedures.waVirtualProcedures(waEnviron)

                    else:
                        resource = pathinfo.pop(0)
                        #print >> sys.stderr, resource

                        if resource == "operations":
                            #print >> sys.stderr, resource
                            resource = pathinfo.pop(0)
                            if resource == "getlist":
                                #print >> sys.stderr, resource
                                from walib.istsos.services.virtualprocedures import virtualprocedures
                                return virtualprocedures.waGetlist(waEnviron)

                        resource = pathinfo.pop(0)
                        #print >> sys.stderr, resource

                        if resource == 'code':
                            #print >> sys.stderr, resource
                            from walib.istsos.services.virtualprocedures import code
                            return code.waCode(waEnviron)

                        elif resource == 'ratingcurve':
                            #print >> sys.stderr, resource
                            from walib.istsos.services.virtualprocedures import ratingcurve
                            return ratingcurve.waRatingcurves(waEnviron)

                # ---------------------------------------
                # Entering istsos.services.observedproperties
                # ---------------------------------------
                elif resource == "observedproperties":
                    #print >> sys.stderr, resource
                    from walib.istsos.services.observedproperties import observedproperties
                    return observedproperties.waObservedproperties(waEnviron)

                # ---------------------------------------
                # Entering istsos.services.uoms
                # ---------------------------------------
                elif resource == "uoms":
                    #print >> sys.stderr, resource
                    from walib.istsos.services.uoms import uoms
                    return uoms.waUoms(waEnviron)

                # ---------------------------------------
                # Entering istsos.services.epsgs
                # ---------------------------------------
                elif resource == "epsgs":
                    #print >> sys.stderr, resource
                    from walib.istsos.services.epsgs import epsgs
                    return epsgs.waEpsgs(waEnviron)

                # ---------------------------------------
                # Entering istsos.services.epsgs
                # ---------------------------------------
                elif resource == "systemtypes":
                    #print >> sys.stderr, resource
                    from walib.istsos.services.systemtypes import systemtypes
                    return systemtypes.waSystemTypes(waEnviron)


                # ---------------------------------------
                # Entering istsos.services.offerings
                # ---------------------------------------
                elif resource == "offerings":
                    #print >> sys.stderr, resource

                    if len(pathinfo)<=1:
                        from walib.istsos.services.offerings import offerings
                        return offerings.waOfferings(waEnviron)
                    else:
                        resource = pathinfo.pop(0) # remove offering name
                        #print >> sys.stderr, resource

                        if resource == "operations":
                            resource = pathinfo.pop(0)
                            if resource == "getlist":
                                #print >> sys.stderr, resource
                                from walib.istsos.services.offerings import offerings
                                return offerings.waGetlist(waEnviron)
                        else:
                            resource = pathinfo.pop(0)
                            if resource == "procedures":
                                if len(pathinfo)<=1:
                                    from walib.istsos.services.offerings.procedures import procedures
                                    return procedures.waProcedures(waEnviron)
                                else:
                                    resource = pathinfo.pop(0)
                                    if resource == "operations":
                                        #print >> sys.stderr, resource
                                        resource = pathinfo.pop(0)
                                        if resource == "memberslist":
                                            from walib.istsos.services.offerings.procedures import procedures
                                            return procedures.waMemberslist(waEnviron)
                                        elif resource == "nonmemberslist":
                                            from walib.istsos.services.offerings.procedures import procedures
                                            return procedures.waNonmemberslist(waEnviron)

                # ---------------------------------------
                # Entering istsos.services.operations
                # ---------------------------------------
                elif resource == "operations":
                    #print >> sys.stderr, resource
                    resource = pathinfo.pop(0)
                    if resource == "getobservation":
                        #print >> sys.stderr, resource
                        from walib.istsos.services import services
                        return services.waGetobservation(waEnviron)
                    elif resource == "insertobservation":
                        #print >> sys.stderr, resource
                        from walib.istsos.services import services
                        return services.waInsertobservation(waEnviron)
                    elif resource == "fastinsert":
                        print >> sys.stderr, resource
                        from walib.istsos.services import services
                        return services.waFastInsert(waEnviron)

                # ---------------------------------------
                # Entering istsos.services.logs
                # ---------------------------------------
                elif resource == "logs":
                    from walib.istsos.services.logs import logs
                    return logs.waLogs(waEnviron)

                # ---------------------------------------
                # Entering istsos.services.status
                # ---------------------------------------
                elif resource == "status":
                    from walib.istsos.services.status import status
                    return status.waStatus(waEnviron)

    elif resource == "user":
        from walib import users
        return users.waUsers(waEnviron)

    raise Exception("Resource is not identified, check the URL")
