from flask import Flask
import xml.etree.ElementTree as ET
import sys
import mariadb
import json
app = Flask(__name__)


@app.route("/cmdb/relation/<depth>/<archiid>")
def get_graph(depth, archiid):
    depth = int(depth)
    json_data = []
    json_data = iterate_relations(archiid, 1, depth, json_data)
    cur = db().cur
    deduplicated_data = []
    for item in json_data:
        source = item['source']
        target = item['target']
        cur.execute(
            "SELECT * FROM archi_graph WHERE target = ? AND source = ?", (source, target))
        result = cur.fetchall()
        if result:
            item['source'] = target
            item['target'] = source
            source = item['source']
            target = item['target']

        cur.execute("SELECT name FROM archi_import WHERE sid = ?", (source,))
        result = cur.fetchall()

        item['name'] = result[0][0]
        cur.execute("SELECT name FROM archi_import WHERE sid = ?", (target,))
        result = cur.fetchall()

        item['target_name'] = result[0][0]
        if item not in deduplicated_data:
            deduplicated_data.append(item)

    filtered_json = json.dumps(deduplicated_data)
    return filtered_json


@app.route("/cmdb/<type>/<os>")
def get_cmdb(type, os):
    cur = db().cur
    cur.execute(
        "SELECT * FROM archi_import WHERE type = ? and os = ?", (type, os))
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


def iterate_relations(source, depth, max_depth, json_data):
    if depth > max_depth:
        return

  # Query the database to get the target relations for the given source
    targets = query_database(source)

  # Iterate through the target relations
    for target in targets:
        target = target[0]
        print(source, "->", target)
        json_data.append(
            {
                'source': source,
                'target': target
            }
        )

        iterate_relations(target, depth+1, max_depth, json_data)
    return json_data


def query_database(archiid):
    try:
        cur = db().cur
        conn = db().conn
        cur.execute(
            "SELECT source from archi_graph WHERE target = ?", (archiid,))
        result = cur.fetchall()
        cur.execute(
            "SELECT target from archi_graph WHERE source = ?", (archiid,))
        result2 = cur.fetchall()
        result += result2
        conn.commit()
        return result
    except mariadb.Error as e:
        print(f"Error reading data from MariaDB: {e}")
        conn.commit()
        return 1


class database:
    def __init__(self):
        try:
            self.conn = mariadb.connect(
                user="root",
                password="root",
                host="localhost",
                port=3306,
                database="eits"

            )
        except mariadb.Error as e:
            print(f"Error connecting to MariaDB Platform: {e}")
            sys.exit(1)
        self.cur = self.conn.cursor()


def db():
    return database()
