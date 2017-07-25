# coding: utf-8
import json
import sys
from functools import partial

import fiona
import pyproj
import rtree.index

from shapely.geometry import asShape, mapping
from shapely import speedups
from shapely.ops import transform

import logging
log = logging.getLogger(__name__)

logging.basicConfig(level=logging.INFO, format='%(asctime)-15s %(levelname)-8s %(message)s')

def main():
    import optparse
    parser = optparse.OptionParser()
    parser.add_option('--a-file')
    parser.add_option('--b-file')
    parser.add_option('--result-file')

    parser.add_option('--src-srs')

    parser.add_option('--buffer', type=float, default=100)

    opts, args = parser.parse_args()

    if not(all([
        opts.a_file,
        opts.b_file,
        opts.result_file,
        opts.src_srs,
    ])):
        parser.print_help()
        sys.exit(1)

    proj_src_to_wgs = partial(
        pyproj.transform,
        pyproj.Proj(init=opts.src_srs),
        pyproj.Proj(init='epsg:4326'))


    a_fname = opts.a_file
    b_fname = opts.b_file
    result_fname = opts.result_file


    idx = rtree.index.Index()

    # Load file A and insert into index
    geoms = []
    with fiona.open(a_fname) as src:
        for i, feat in enumerate(src):
            geom = asShape(feat['geometry'])
            geoms.append(geom)
            idx.insert(i, geom.bounds)


    # Iterate file B and check with file A geometries
    # Collect geoms only in B in diff_b
    diff_b = []
    with fiona.open(b_fname) as src:
        for i, feat in enumerate(src):
            geom = asShape(feat['geometry'])
            hits = list(idx.intersection(geom.bounds))

            for hit in hits:
                if geoms[hit] and geoms[hit].equals(geom):
                    # Set geom to None if it is equal in A and B
                    geoms[hit] = None
                    break
            else:
                diff_b.append(geom)

    # Geoms only in A
    diff_a = [g for g in geoms if g is not None]

    result_features = []
    for g in diff_a + diff_b:
        # Buffer, simplify and transform to WGS84
        if opts.buffer:
            g = g.buffer(opts.buffer, 1).simplify(opts.buffer/4, preserve_topology=True)
        g = transform(proj_src_to_wgs, g)
        result_features.append({
            'type': 'Feature',
            'properties': {},
            'geometry': mapping(g),
        })

    result = {'type': 'FeatureCollection', 'features': result_features}

    with open(result_fname, 'w') as f:
        json.dump(result, fp=f)

if __name__ == '__main__':
    if speedups.available:
        speedups.enable()
    main()
