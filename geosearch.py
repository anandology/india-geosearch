import web
import json
import os
import sys

urls = (
    "/", "index",
    "/js/(.*)", "javascript",
    "/geosearch", "geosearch_web"
)
app = web.application(urls, globals())
db = web.database(dbn="postgres", db="geosearch")

def geosearch(lat, lon):
    point = 'Point({0} {1})'.format(lon, lat)
    q = "SELECT pc_code, pc_name, st_code, st_name FROM india_pc_2014 WHERE ST_Within(ST_GeomFromText($point, 4326), geom)"
    result = db.query(q, vars={"point": point})
    match = result and result[0] or None
    if match:
        match['key'] = "{}/PC{:02d}".format(match['st_name'], match['pc_code'])
        if match['st_name'] == 'AP':
            match.update(geosearch_ap(match['pc_code'], lat, lon))
        if match['st_name'] == 'KA' and match['pc_code'] in (24, 25, 26):
            match.update(geosearch_bangalore_wards(lat, lon))
        if match['st_name'] in ['KL', 'MP']:
            match.update(geosearch_polling_booth(match['pc_code'], lat, lon))
    return match

def geosearch_ap(pc, lat, lon):
    point = 'Point({0} {1})'.format(lon, lat)
    q = "SELECT ac_id, ac_name FROM ap_ac_2014 WHERE ST_Within(ST_GeomFromText($point, 4326), geom)"
    result = db.query(q, vars={"point": point})
    match = result and result[0] or None
    if match:
        match['ac_key'] = "AP/AC{:03d}".format(match['ac_id'])
    else:
        match = {}
    return match

def get_state_code(num):
    d = {
        11: 'KL',
        12: 'MP'
    }
    return d[num]

def geosearch_polling_booth(pc, lat, lon):
    result = db.query("SELECT ac_code, pb_code FROM booth_coordinates" +
                      " WHERE pc_code=$pc" +
                      " ORDER BY (lat-$lat)*(lat-$lat) + (lon-$lon)*(lon-$lon)" + 
                      " LIMIT 1", vars=locals())
    if result:
        match = result[0]
        state = get_state_code(match['state_code'])
        match['ac_key'] = "{}/AC{:03d}".format(state, match['ac_code'])
        match['pb_key'] = "{}/AC{:03d}/PB{:04d}".format(state, match['ac_code'], match['pb_code'])
    else:
        match = {}
    return match

def geosearch_bangalore_wards(lat, lon):
    point = 'Point({0} {1})'.format(lon, lat)
    q = "SELECT ward_no, ward_name FROM bbmpwards WHERE ST_Within($point, the_geom)"
    result = db.query(q, vars={"point": point})
    match = result and result[0] or {}
    return match

class index:
    def GET(self):
        web.header("content-type", "text/html")
        path = os.path.join(os.path.dirname(__file__), "examples/ex1.html")
        return open(path).read()

class geosearch_web:
    def GET(self):
        i = web.input(lat=None, lon=None)
        web.header("content-type", "application/json")
        web.header("Access-Control-Allow-Origin", "*")
        if not i.lat or not i.lon:
            return '{"error": "Please specify lat and lon parameters"}'
        match = geosearch(i.lat, i.lon)
        response = {
            "query": i,
            "result": match
        }
        return json.dumps(response)

class javascript:
    def GET(self, filename):
        web.header("content-type", "text/javascript")
        path = os.path.join(os.path.dirname(__file__), "js", filename)
        if os.path.exists(path):
            return open(path).read()
        else:
            raise web.notfound()

def debug():
    print "visakhapatnam", geosearch("83.21848150000005", "17.6868159")
    print "muralinagar, visakha", geosearch("83.25996740000005", "17.7471481")
    print "KPHB, hyd", geosearch("78.39204369999993", "17.4785496")
    print "rtnagar, bangalore", geosearch("77.59295399999996", "13.02458")

if __name__ == "__main__":
    if "--debug" in sys.argv:
        debug()
    else:
        app.run()
