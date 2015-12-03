import overpy
op = overpy.Overpass()
result = op.query('(node[operator="Metra"])->.metra;node.metra[railway="station"](40.72644570551446,-89.9176025390625,43.265206318396025,-85.7977294921875);out;')
for node in result.nodes:
    print '%s: %0.3f, %0.3f' % (node.tags.get('name'), node.lat, node.lon)
