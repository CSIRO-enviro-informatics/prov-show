import _config as conf
from flask import Flask, render_template, request, Response
import rdflib
import strategies

app = Flask(__name__, template_folder=conf.TEMPLATES_DIR, static_folder=conf.STATIC_DIR)


@app.route('/')
def home():
    return render_template(
        'form.html'
    )


@app.route('/show', methods=['POST'])
def show():
    # check for query string args:
    #   result_type: one of ['png', 'svg', 'web', 'rdf'], default: 'web'
    result_type = request.values.get('result_type') if request.values.get('result_type') else 'web'

    #   strategy: one of ['basic'], default: 'basic'
    strategy = request.values.get('strategy') if request.values.get('strategy') else 'basic'

    # get the RDF data
    if 'multipart/form-data' in request.headers.get('Content-Type'):
        # try copy 'n paste data first
        if len(request.form['copy']) > 0:
            # read the RDF data from the POSTed form
            rdf_data = request.form['copy']
            # read the given RDF format
            rdf_format = request.form['copy_format']
        # next try file upload
        elif request.files['file'].filename != '':
            # read the RDF data from the file
            f = request.files['file']
            rdf_data = f.read()
            # guess the RDF encoding: file already limited to one of .ttl, .rdf, .owl, .json by JavaScript
            rdf_format = rdflib.util.guess_format(request.files['file'].filename)
    # check for a known RDF mimetype
    elif request.data is not None:
        rdf_data = request.data
        if 'text/turtle' in request.headers.get('Content-Type'):
            rdf_format = 'turtle'
        elif 'rdf+xml' in request.headers.get('Content-Type'):
            rdf_format = 'xml'
        elif 'application/rdf+json' in request.headers.get('Content-Type'):
            rdf_format = 'json-ld'
        else:
            return Response(
                'If you are POSTing raw RDF data to this service, you must use one of the following RDF mimtypes: '
                'text/turtle (Turtle), application/rdf+xml (RDF/XML) or application/rdf+json (JSON-LD).',
                status=400, mimetype='text/plain')
    # we have a POST error
    else:
        return Response(
            'You must either post raw RDF data, with a correct Content-Type HTTP header or submit an HTML '
            'form to this endpoint with either an RDF file named \'file\' or a textarea input named \'copy\' '
            'containing RDF data',
            status=400, mimetype='text/plain')

    # to get here we must have both an rdf_data and an rdf_format value
    # try and make a graph, returning any errors to client

    try:
        g = rdflib.Graph().parse(data=rdf_data, format=rdf_format)

        # if we are here, we have a valid RDf graph so now we can filter it, using the selected strategy
        strategies.apply_strategy(g, strategy)

        return make_result_type(g, result_type, rdf_format)
    except rdflib.plugins.parsers.notation3.BadSyntax as e:
        return Response(
            'There is an error parsing the RDF data you uploaded. The RDF parser said: ' + str(e),
            status=400,
            mimetype='text/plain'
        )
    except Exception as e:
        return Response(
            'There was an error: ' + str(e),
            status=400,
            mimetype='text/plain'
        )


@app.route('/strategies')
def strategiez():
    return render_template(
        'strategies.html'
    )


def basic_make_nodes_edges(g):
    def basic_make_nodes(g):
        nodes = ''

        q = '''
            PREFIX rdfs: <http://www.w3.org/2000/01/rdf-schema#>
            PREFIX prov: <http://www.w3.org/ns/prov#>
            SELECT *
            WHERE {
                ?s a ?o .
                {?s a prov:Entity .}
                UNION
                {?s a prov:Activity .}
                UNION
                {?s a prov:Agent .}
                ?s rdfs:label ?label .
            }
            '''
        for row in g.query(q):
            if str(row['o']) == 'http://www.w3.org/ns/prov#Entity':
                nodes += '\t{id: "%(node_id)s", label: "%(label)s", shape: "ellipse", ' \
                         'color:{background:"#FFFC87", border:"#808080"}},\n' % {
                    'node_id': row['s'],
                    'label': row['label']
                }
            elif str(row['o']) == 'http://www.w3.org/ns/prov#Activity':
                nodes += '\t{id: "%(node_id)s", label: "%(label)s", shape: "box", ' \
                         'color:{background:"#9FB1FC", border:"blue"}},\n' % {
                    'node_id': row['s'],
                    'label': row['label']
                }
            elif str(row['o']) == 'http://www.w3.org/ns/prov#Agent':
                nodes += '\t{id: "%(node_id)s", label: "%(label)s", image: "/static/img/agent.png", shape: "image"},\n' % {
                    'node_id': row['s'],
                    'label': row['label']
                }

        return nodes

    def basic_make_edges(g):
        edges = ''

        q = '''
            PREFIX rdfs: <http://www.w3.org/2000/01/rdf-schema#>
            PREFIX prov: <http://www.w3.org/ns/prov#>
            SELECT *
            WHERE {
                ?s ?p ?o .
                ?s prov:wasAttributedTo|prov:wasGeneratedBy|prov:used|prov:wasDerivedFrom|prov:wasInformedBy ?o .
            }
            '''
        for row in g.query(q):
            edges += '\t{from: "%(from)s", to: "%(to)s", arrows:"to", font: {align: "bottom"}, ' \
                     'color:{color:"black"}, label: "%(relationship)s"},\n' % {
                'from': row['s'],
                'to': row['o'],
                'relationship': str(row['p']).split('#')[1]
            }

        return edges

    nodes = 'var nodes = new vis.DataSet([\n'
    nodes += basic_make_nodes(g)
    nodes = nodes.rstrip().rstrip(',') + '\n  ]);\n\n'

    edges = 'var edges = new vis.DataSet([\n'
    edges += basic_make_edges(g)
    edges = edges.rstrip().rstrip(',') + '\n  ]);\n\n'

    return {
        'nodes': nodes,
        'edges': edges
    }


def basic_make_javascript(g):
    ne = basic_make_nodes_edges(g)
    ne_str = ne.get('nodes')
    ne_str += '\n\n'
    ne_str += ne.get('edges')
    return ne_str


def make_result_type(g, result_type, rdf_format):
    if result_type == 'rdf':
        return Response(g.serialize(format=rdf_format), mimetype='text/plain')
    elif result_type == 'web' or result_type == 'img' or result_type == 'svg':
        # make the image
        img = ''
        if result_type == 'img':
            return Response(img, mimetype='image/png')
        elif result_type == 'svg':
            return render_template(
                'result-svg.html',
                ne=basic_make_javascript(g),
                prov=g.serialize(format=rdf_format).decode("utf-8"),
                error=None
            )
        else:  # result_type == 'web'
            return render_template(
                'result.html',
                ne=basic_make_javascript(g),
                prov=g.serialize(format=rdf_format).decode("utf-8"),
                error=None
            )


if __name__ == '__main__':
    app.run(debug=conf.DEBUG)
