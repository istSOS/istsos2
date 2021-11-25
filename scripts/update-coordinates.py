import traceback
import psycopg2
import sys
import json
import csv
import yaml
import xml.etree.ElementTree as et
from os import path

"""
Given a CSV file like this:
--
A_AETCAN_AIR,AET,691140,153780,1140,21781
A_BOL_PTC,PortoCeresio ,712688,84295,290,21781
A_BOL_PTC_LAM,Porto Ceresio (Italia) ,712560,83610,290,21781
A_BOL_R_PTC,PortoCeresio,712688,84295,290,21781
A_BON_QUA,Quartino,713525,113128,201,21781
A_CAL_AIR,Batola,692060,152560,1100,21781
--

And a yaml file like this:

--
database:
    host: localhost
    port: 5432
    user: postgres
    password: postgres
    dbname: istsos
    schema: sos

folders:
    services: /services
    csv: /data/locations.csv
--

Update all the foi coordinates:

Example:

python update-coordinates.py INSTANCE_NAME CSV_FULL_PATH ISTSOS_SERVICES_FOLDER_PATH

python update-coordinates.py sos ~/Desktop/locations.csv ~/workspace/istsos/istsos2/services/
"""

ns = {
    'swe': 'http://www.opengis.net/swe/1.0.1',
    'gml': 'http://www.opengis.net/gml',
    'sml': 'http://www.opengis.net/sensorML/1.0.1',
    'xlink': 'http://www.w3.org/1999/xlink',
    'xsi': 'http://www.w3.org/2001/XMLSchema-instance'
}

if len(sys.argv) != 2:
    raise Exception("yaml config file not given.")

config = None
with open(sys.argv[1], 'r') as file:
    config = yaml.load(file, Loader=yaml.FullLoader)
    print(config)

def red(message):
    return("\033[91m%s\033[0m" % message)

# Check if there is a name_foi with more the one coordinates

print("# Starting to check file inconsistencies:")

print(" > Searching for name_foi duplicates:")

fois = {}
procedures = {}
schema = config['database']['schema']
xml_folder = config['folders']['services']
csvfile_path = config['folders']['csv']

def check_foi(name_prc, name_foi, st_x, st_y, st_z, st_srid):

    name_foi = name_foi.strip()

    st_x = float(st_x)
    st_y = float(st_y)
    st_z = float(st_z)
    st_srid = int(st_srid)

    coords = [st_x, st_y, st_z]

    # Check if not exists
    if name_foi not in fois:
        fois[name_foi] = {
            'coords': coords,
            'srid': st_srid,
            'cnt': 1,
            'procedures': [name_prc]
        }

    # If exists check for duplicate
    elif fois[name_foi]['coords'] != coords:
        # Create a new FOI
        name_foi = "%s_%s" % (name_foi, fois[name_foi]['cnt']+1)
        # Check recursivly
        name_foi = check_foi(name_prc, name_foi, st_x, st_y, st_z, st_srid)

    else:
        fois[name_foi]['cnt'] += 1
        fois[name_foi]['procedures'].append(name_prc)
        
    return name_foi

with open(csvfile_path) as csvfile:

    reader = csv.reader(csvfile, delimiter=',')
    for row in reader:
        # Map the procedure with the new FOI
        procedures[row[0]] = check_foi(*row)


for foi in sorted(fois.keys()):
    print("%s: %s" % (foi, json.dumps(fois[foi], indent=4)))
    
    for procedure in fois[foi]['procedures']:
        print(" - %s: %s" % (procedure, procedures[procedure]))

#print(json.dumps(procedures, indent=4))
#print(sorted(procedures.values()))

conn = psycopg2.connect(
    "dbname=%s user=%s password=%s host=%s port=%s" % (
        config['database']['dbname'],
        config['database']['user'],
        config['database']['password'],
        config['database']['host'],
        config['database']['port']
    )
)

cur = conn.cursor()

nxp = []
nxf = []
dff = []
cgd = 0
ncgd = 0

try:
    cur.execute("BEGIN;")
    
    for name_foi in sorted(fois.keys()):
    
        foi = fois[name_foi]
        
        # Check if foi exists
        cur.execute("""
            SELECT
                id_foi
            FROM
                """ + schema + """.foi
            WHERE
                name_foi = %s;
        """, (name_foi,))

        foi_rec = cur.fetchone()

        if foi_rec is None:
            print('Inserting "%s" new foi..' % name_foi)

            cur.execute("""
                INSERT INTO """ + schema + """.foi(
                    id_fty_fk, name_foi, geom_foi
                )
                VALUES (
                    1, %s, ST_SetSRID(ST_MakePoint(%s, %s, %s), %s)
                ) RETURNING id_foi;
            """, (
                name_foi,    
                foi['coords'][0],
                foi['coords'][1],
                foi['coords'][2],
                foi['srid']
            ))
            id_foi = cur.fetchone()[0]

        else:
            print('Updating "%s" coordinates..' % name_foi)
            
            id_foi = foi_rec[0]
            
            # Unlink foi related procedures 
            cur.execute("""
                UPDATE
                    """ + schema + """.procedures
                SET
                    id_foi_fk = NULL
                WHERE
                    id_foi_fk = %s;
            """, (id_foi,))

            # Update foi's coordinates
            cur.execute("""
                UPDATE
                    """ + schema + """.foi
	            SET
	                geom_foi = ST_SetSRID(ST_MakePoint(%s, %s, %s), %s)
	            WHERE
	                id_foi = %s;
            """, (
                foi['coords'][0],
                foi['coords'][1],
                foi['coords'][2],
                foi['srid'],
                id_foi
            ))

        for procedure in foi['procedures']:

            cur.execute("""
                SELECT
                    id_prc
                FROM
                    """ + schema + """.procedures
                WHERE
                    name_prc = %s;
            """, (procedure,))

            res = cur.fetchone()

            if res is None:
                print('Procedure %s not found in db.' % procedure)
                continue

            id_prc = res[0]

            cur.execute("""
                UPDATE
                    """ + schema + """.procedures
                SET
                    id_foi_fk = %s
                WHERE
                    id_prc = %s;
            """, (id_foi, id_prc))

            # Update XML
            f = path.join(xml_folder, schema, 'sml', '%s.xml' % procedure)
            if path.isfile(f):
                sml = et.parse(f)
                root = sml.getroot()  # et.Element("{%s}SensorML" % ns['sml'])
                point = root.find(
                    'sml:member/sml:System/sml:location/gml:Point',
                    ns
                )
                coordinates = root.find(
                    "sml:member/sml:System/sml:location/gml:Point/gml:coordinates",
                    ns
                )
                point.attrib["{%s}id" % ns['gml']] = name_foi
                coordinates.text = ','.join([ str(a) for a in foi['coords']])

#                print(et.tostring(point, encoding='utf8', method='xml'))

                f = path.join(xml_folder, schema, 'sml', '%s.xml' % procedure)
                sml.write(f)

            else:
                print("Warning: SML not found (%s)" % f)

    # Check work in the database
    for procedure in sorted(procedures.keys()):

        cur.execute("""
            SELECT
                id_prc,
                id_foi,
                name_foi,
                st_x(geom_foi) as x,
                st_y(geom_foi) as y,
                st_z(geom_foi) as z
            FROM
                """ + schema + """.procedures
            INNER JOIN
                """ + schema + """.foi
            ON
                id_foi_fk = id_foi
            WHERE
                name_prc = %s;
        """, (procedure,))

        res = cur.fetchone()

        if res is None:
            print("skipping procedure %s not in db" % procedure)
            continue

        id_prc = res[0]
        id_foi = res[1]
        db_name_foi = res[2]
        db_coords = [res[3], res[4], res[5]]

        # Get foi name from CSV
        name_foi = procedures[procedure]
        foi = fois[name_foi]
        coords = foi['coords']

        if (
            db_name_foi != name_foi
            or db_coords != coords
        ):

            if db_name_foi != name_foi:
                print("%s foi not updated from %s to %s" % (
                    procedure, db_name_foi, name_foi
                ))

            if db_coords != coords:
                print("%s coords not updated from %s to %s" % (
                    procedure, db_coords, coords
                ))

        else:
            print("%s update correctly" % procedure)

#    cur.execute("ROLLBACK;")
    cur.execute("COMMIT;")
    
    # Update SML
    

except Exception as e:
    print(traceback.print_exc())
    cur.execute("ROLLBACK;")

