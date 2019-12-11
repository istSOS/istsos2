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

import psycopg2
import sys
import json
from os import path

sys.path.insert(0, path.abspath("."))
try:
    import lib.argparse as argparse
except ImportError as e:
    print("""
Error loading internal libs:
 >> did you run the script from the istSOS root folder?\n\n""")
    raise e

conn = psycopg2.connect(
    "dbname=istsos "
    "user=postgres "
    "password=postgres "
    "host=localhost "
    "port=9432"
)


def execute(args, conf=None):
    """
        Example:
        python scripts/applyqi.py
            -s vedeggio
            -p 598_33
            -e 2018-02-09T00:00:00+02
            -sqi 210
    """
    cur = conn.cursor()

    # Activate and print verbose information
    # debug = args['v'] if 'v' in args else False

    # dqi = args['dqi']  # default qi
    cqi = args['cqi']  # correct qi
    sqi = args['sqi']  # statistical qi

    # Procedure name
    procedure = args['procedure']
    # Service name
    service = args['service']

    # Begin date
    begin = args['begin'] if 'begin' in args else "*"
    # End date
    end = args['end'] if 'end' in args else "*"

    try:
        cur.execute("BEGIN;")
        cur.execute("""
            SELECT id_prc, stime_prc, etime_prc
            FROM %s.procedures
            WHERE
                upper(name_prc) = upper(%s);
        """ % (service, '%s'), (procedure,))
        res = cur.fetchone()

        if res is None:
            raise Exception("Procedure %s not found in serivce %s" % (
                procedure, service
            ))

        print(res)
        id_prc = res[0]
        # b = res[1]
        # e = res[2]
        # print('b', b.isoformat(), 'e', e.isoformat())
        # Load Procedure QI
        cur.execute("""
            SELECT
                id_pro, constr_pro, constr_opr
                name_opr, def_opr
            FROM
                %s.proc_obs,
                %s.observed_properties
            WHERE
                id_opr = id_opr_fk
            AND
                id_prc_fk = %s;
        """ % (service, service, '%s'), (id_prc,))
        recs = cur.fetchall()

        for rec in recs:
            print(rec)
            id_pro = rec[0]
            constr_opr = rec[2]  # level 0
            constr_pro = rec[1]  # level 1

            conditions = []
            if begin != '*':
                conditions.append("""
                    time_eti >= '%s'::TIMESTAMP WITH TIME ZONE
                """ % begin)
            if end != '*':
                conditions.append("""
                    time_eti <= '%s'::TIMESTAMP WITH TIME ZONE
                """ % end)
            conditions.append('id_prc_fk = %s' % id_prc)
            conditions.append('id_pro_fk = %s' % id_pro)

            for conf in [[constr_opr, cqi], [constr_pro, sqi]]:
                constraint = conf[0]
                qi = conf[1]
                if constraint is not None and constraint != '':
                    constraint = json.loads(constraint)

                    if 'interval' in constraint:
                        conditions.append("""
                            (
                                val_msr >= %s
                                AND val_msr <= %s
                            )
                        """ % (
                            constraint['interval'][0],
                            constraint['interval'][1]
                        ))
                    sql = """
                        SELECT id_msr
                        FROM
                            %s.measures,
                            %s.event_time
                        WHERE
                            id_eti = id_eti_fk
                        AND
                            %s
                    """ % (
                        service,
                        service,
                        " AND ".join(conditions)
                    )

                    # print("""
                    cur.execute("""
                        UPDATE %s.measures
                        SET id_qi_fk = %s
                        WHERE id_msr in (%s)
                    """ % (
                        service,
                        qi,
                        sql
                    ))

        cur.execute("COMMIT;")

    except Exception as e:
        print(str(e))
        cur.execute("ROLLBACK;")


if __name__ == "__main__":

    parser = argparse.ArgumentParser(
        description='Apply the qi'
    )

    parser.add_argument(
        '-v', '--verbose',
        action='store_true',
        dest='v',
        help='Activate verbose debug'
    )

    parser.add_argument(
        '-p', '--procedure',
        action='store',
        dest='procedure',
        help='Procedure name'
    )

    parser.add_argument(
        '-s', '--service',
        action='store',
        dest='service',
        help='Service name'
    )

    parser.add_argument(
        '-b', '--begin',
        action='store',
        dest='begin',
        default='*',
        metavar='1978-10-08T03:56:00+01:00',
        help='Begin position date of the processing in ISO 8601.'
    )

    parser.add_argument(
        '-e', '--end',
        action='store',
        dest='end',
        default='*',
        metavar='2014-01-27T11:27:00+01:00',
        help='End position date of the processing in ISO 8601.'
    )

    parser.add_argument(
        '-dqi',
        action='store',
        dest='dqi',
        default=100,
        help='Default QI'
    )

    parser.add_argument(
        '-cqi',
        action='store',
        dest='cqi',
        default=110,
        help='Correct QI'
    )

    parser.add_argument(
        '-sqi',
        action='store',
        dest='sqi',
        default=200,
        help='Correct QI'
    )

    args = parser.parse_args()
    execute(args.__dict__)
