"""Graph-building helpers used by the routing and accessibility example tests.

These utilities convert a list of GeoJSON LineString features from the MapLark
API into an undirected weighted ``networkx.Graph`` suitable for Dijkstra /
BFS traversal.

Import in your test or app code::

    from tests.example_apps.graph_utils import build_nx_graph
"""

from haversine import Unit, haversine
import networkx as nx


def feature_layer(tags: dict) -> int:
    """Return the effective vertical layer for an OSM way.

    Uses the explicit ``layer`` tag when present; falls back to +1 for bridges
    and -1 for tunnels so that grade-separated crossings are not falsely joined
    to at-grade ways that happen to share the same coordinate.
    """
    if "layer" in tags:
        try:
            return int(tags["layer"])
        except ValueError:
            pass
    if tags.get("bridge") not in (None, "no"):
        return 1
    if tags.get("tunnel") not in (None, "no"):
        return -1
    return 0


def build_nx_graph(features: list) -> nx.Graph:
    """Build an undirected weighted networkx Graph from GeoJSON LineString features.

    Nodes  : ``(lon, lat, layer)`` tuples where ``layer`` is the effective
             vertical level derived from the feature's OSM bridge/tunnel/layer
             tags.  Including the layer prevents grade-separated crossings
             (bridges, tunnels) from being falsely joined to at-grade ways that
             share the same coordinate - a known hazard when topology is inferred
             from geometry alone without original OSM node IDs.

    Weights: haversine distance in metres between adjacent nodes (edge attr
             ``'weight'``).

    Endpoints (first and last vertex of each way) are placed at layer 0 so that
    bridge/tunnel ways connect to the at-grade network at their terminations.
    Interior nodes carry the way's effective layer so that grade-separated
    crossings mid-span are not joined to crossing at-grade ways.
    """
    G = nx.Graph()

    for f in features:
        geom = f["geometry"]
        if geom["type"] != "LineString":
            continue
        tags = f.tags
        layer = feature_layer(tags)
        coords = geom["coordinates"]
        n = len(coords)
        for i in range(n - 1):
            la = 0 if i == 0 else layer
            lb = 0 if i + 1 == n - 1 else layer
            a = (coords[i][0], coords[i][1], la)
            b = (coords[i + 1][0], coords[i + 1][1], lb)
            d = haversine((a[1], a[0]), (b[1], b[0]), unit=Unit.METERS)
            if G.has_edge(a, b):
                if d < G[a][b]["weight"]:
                    G[a][b]["weight"] = d
            else:
                G.add_edge(a, b, weight=d)

    return G
