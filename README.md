# osmgeojson-python

Python SDK for the **MapLark** OSM GeoJSON API with auto-pagination, bounding box chunking, retry/backoff, pandas/geopandas output, async support, and convenience methods to get common OSM data such as buildings, amenities, bike roads, etc.

```
pip install osmgeojson
pip install "osmgeojson[geo]"   # pandas / geopandas / shapely support
```

## Quick start

```python
from osmgeojson import OSMGeoJSONClient

with OSMGeoJSONClient(api_key="sk-...") as client:
    fc = client.query(bbox="18.06,59.32,18.09,59.34", tags=["building"])
    print(len(fc.features), "buildings found")
```

See the full docs for async support, bbox chunking, CLI usage, and convenience helpers.
