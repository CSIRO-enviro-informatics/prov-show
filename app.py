from flask import Flask, render_template
from rdflib import Graph
import provsvg

app = Flask(__name__)


@app.route('/')
def index():
    # parse the RDF file into a Graph
    g = Graph().parse('data/test_prune_11.ttl', format='turtle')
    # create vis.js JavaScript
    nodes_edges_javascript = provsvg.make_nodes_edges_javascript(g)

    return render_template(
        'index.html',
        ne=nodes_edges_javascript,
        prov=g.serialize(format='turtle').decode("utf-8")
    )


if __name__ == '__main__':
    app.run()
