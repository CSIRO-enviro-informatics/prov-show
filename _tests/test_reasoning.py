import _config as conf
from os.path import dirname, realpath, join, abspath
import rdflib


grf = rdflib.Graph()
grf.parse(join(conf.APP_DIR, '_config', 'prov-o.ttl'), format='turtle')
print(grf.serialize(format='turtle'))
