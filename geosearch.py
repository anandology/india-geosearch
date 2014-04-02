import web
import json

urls = (
    "/geosearch", "geosearch"
)
app = web.application(urls, globals())
db = web.database(dbn="postgres", db="geosearch")

class geosearch:
    def GET(self):
        i = web.input(lat=None, lon=None)
        web.header("content-type", "application/json")
        web.header("Access-Control-Allow-Origin", "*")
        if not i.lat or not i.lon:
            return '{"error": "Please specify lat and lon parameters"}'

        point = 'Point({0} {1})'.format(i.lat, i.lon)
        q = "SELECT pc_no, pc_name FROM pc WHERE ST_Within(ST_GeomFromText($point, 4326), geom)"
        result = db.query(q, vars={"point": point})
        match = result and result[0] or None
        return json.dumps(match)

if __name__ == "__main__":
    app.run()
