import psycopg2
import sys
import json
import csv
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

"""
input file:

name_prc,name_foi,st_x,st_y,st_z,st_srid
A_AETCAN_AIR,AET,691140,153780,1140,21781
A_BOL_PTC,PortoCeresio ,712688,84295,290,21781

"""

if len(sys.argv) != 4:
    raise Exception("SOS instance name or CSV file not given.")


def red(message):
    return(f"\033[91m{message}\033[0m")

# Check if there is a name_foi with more the one coordinates

print("# Starting to check file inconsistencies:")

print(" > Searching for name_foi duplicates:")

fois = {}
procedures = {}
schema = sys.argv[1]
xml_folder = sys.argv[3]

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
            'cnt': 1,
            'procedures': [name_prc]
        }

    # If exists check for duplicate
    elif fois[name_foi]['coords'] != coords:
        # Create a new FOI
        name_foi = f"{name_foi}_{fois[name_foi]['cnt']+1}"
        # Check recursivly
        name_foi = check_foi(name_prc, name_foi, st_x, st_y, st_z, st_srid)

    else:
        fois[name_foi]['cnt'] += 1
        fois[name_foi]['procedures'].append(name_prc)
        
    return name_foi

with open(sys.argv[2], newline='') as csvfile:

    reader = csv.reader(csvfile, delimiter=',')
    for row in reader:
        # Map the procedure with the new FOI
        procedures[row[0]] = check_foi(*row)


for foi in sorted(fois.keys()):
    print(f"{foi}: {json.dumps(fois[foi], indent=4)}")
    
    for procedure in fois[foi]['procedures']:
        print(f" - {procedure}: {procedures[procedure]}")

#print(json.dumps(procedures, indent=4))
#print(sorted(procedures.values()))

conn = psycopg2.connect(
    "dbname=istsos "
    "user=postgres "
    "password=postgres "
    "host=localhost "
    "port=5432"
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
        cur.execute(f"""
            SELECT
                id_foi
            FROM
                {schema}.foi
            WHERE
                name_foi = %s;
        """, (name_foi,))

        foi_rec = cur.fetchone()

        if foi_rec is None:
            print(f'Inserting "{name_foi}" new foi..')

            cur.execute(f"""
                INSERT INTO {schema}.foi(
                    id_fty_fk, name_foi, geom_foi
                )
                VALUES (
                    1, %s, ST_SetSRID(ST_MakePoint(%s, %s, %s), 21781)
                ) RETURNING id_foi;
            """, (
                name_foi,    
                foi['coords'][0],
                foi['coords'][1],
                foi['coords'][2]
            ))
            id_foi = cur.fetchone()[0]

        else:
            print(f'Updating "{name_foi}" coordinates..')
            
            id_foi = foi_rec[0]
            
            # Unlink foi related procedures 
            cur.execute(f"""
                UPDATE
                    {schema}.procedures
                SET
                    id_foi_fk = NULL
                WHERE
                    id_foi_fk = %s;
            """, (id_foi,))

            # Update foi's coordinates
            cur.execute(f"""
                UPDATE
                    {schema}.foi
	            SET
	                geom_foi = ST_SetSRID(ST_MakePoint(%s, %s, %s), 21781)
	            WHERE
	                id_foi = %s;
            """, (
                foi['coords'][0],
                foi['coords'][1],
                foi['coords'][2],
                id_foi
            ))

        for procedure in foi['procedures']:

            cur.execute(f"""
                SELECT
                    id_prc
                FROM
                    {schema}.procedures
                WHERE
                    name_prc = %s;
            """, (procedure,))

            res = cur.fetchone()

            if res is None:
#                raise Exception(f'Procedure {procedure} not found in db.')
                print(f'Procedure {procedure} not found in db.')
                continue

            id_prc = res[0]

            cur.execute(f"""
                UPDATE
                    {schema}.procedures
                SET
                    id_foi_fk = %s
                WHERE
                    id_prc = %s;
            """, (id_foi, id_prc))

            # Update XML
            f = path.join(xml_folder, schema, 'sml', f'{procedure}.xml')
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

                f = path.join(xml_folder, schema, 'sml', f'{procedure}.xml')
                sml.write(f)

            else:
                print(f"Warning: SML not found ({f})")

    # Check work in the database
    for procedure in sorted(procedures.keys()):

        cur.execute(f"""
            SELECT
                id_prc,
                id_foi,
                name_foi,
                st_x(geom_foi) as x,
                st_y(geom_foi) as y,
                st_z(geom_foi) as z
            FROM
                {schema}.procedures
            INNER JOIN
                {schema}.foi
            ON
                id_foi_fk = id_foi
            WHERE
                name_prc = %s;
        """, (procedure,))

        res = cur.fetchone()

        if res is None:
            print(f"skipping procedure {procedure} not in db")
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
                print(f"{procedure} foi not updated from {db_name_foi} to {name_foi}")

            if db_coords != coords:
                print(f"{procedure} coords not updated from {db_coords} to {coords}")

        else:
            print(f"{procedure} update correctly")

#    cur.execute("ROLLBACK;")
    cur.execute("COMMIT;")
    
    # Update SML
    

except Exception as e:
    print(str(e))
    cur.execute("ROLLBACK;")

