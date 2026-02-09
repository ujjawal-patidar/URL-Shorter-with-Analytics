import geoip2.database
from geoip2.models import City
from pathlib import Path

GEO_DB_PATH = Path("app/db/GeoLite2-City.mmdb")

reader: geoip2.database.Reader | None = None


def init_geoip():
    global reader
    reader = geoip2.database.Reader(GEO_DB_PATH)


def close_geoip():
    global reader
    if reader:
        reader.close()


def get_geo_info_from_ip(ip: str | None) -> City | None:
    if not ip or not reader:
        return None

    try:
        return reader.city(ip)
    except Exception as e:
        print("Exception", e)
        return None
