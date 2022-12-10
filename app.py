from flask import Flask
import re
import sys
import mariadb
import json
app = Flask(__name__)


# Get Cursor

@app.route("/cmdb/<type>/<os>")
def get_cmdb(type, os):
    try:
        conn = mariadb.connect(
        user="root",
        password="root",
        host="localhost",
        port=3306,
        database="eits"

    )
    except mariadb.Error as e:
        print(f"Error connecting to MariaDB Platform: {e}")
        sys.exit(1)
    cur = conn.cursor()
    cur.execute("SELECT * FROM archi_import WHERE type = ? and os = ?", (type, os))
    rows = cur.fetchall()
    json_data = []
    for row in rows:
        json_data.append({
            'sid': row[0],
            'type': row[1],
            'name': row[2],
            'stage': row[3],
            'domain': row[4],
            'tag': row[5],
            'url': row[6],
            'ipv4': row[7],
            'ext_ipv4': row[8],
            'vpc': row[9],
            'os': row[10],
            'build': row[11],
            'vendor': row[12],
            'support': row[13],
            'src': row[14],
            'dst': row[15],
            'doc': row[16],
            'eol': row[17]
        })
    return json.dumps(json_data)



