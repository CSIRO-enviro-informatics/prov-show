import _config as conf
from flask import Flask, render_template, request, Response
import rdflib

app = Flask(__name__, template_folder=conf.TEMPLATES_DIR, static_folder=conf.STATIC_DIR)


@app.route('/', methods=['GET', 'POST'])
def index():
    return render_template(
        'index.html'
    )


@app.route('/show', methods=['POST'])
def show():
    # try to work out what to do based on any Content-Type headers
    if 'multipart/form-data' in request.headers.get('Content-Type'):
        # try copy 'n paste data first
        if len(request.form['copy']) > 0:
            print('c')
            # read the RDF data from the POSTed form
            rdf_data = request.form['copy']
            # read the given RDF format
            rdf_format = request.form['copy_format']
            return Response('copy', mimetype='text/plain')
        # next try file upload
        elif request.files['file'].filename != '':
            print('f')
            # read the RDF data from the file
            f = request.files['file']
            rdf_data = f.read()
            # guess the RDF encoding: the file extension is limited to must be one of .ttl, .rdf, .owl, .json by JavaScript
            rdf_format = rdflib.util.guess_format(request.files['file'].filename)
            print(rdf_format)
            print(rdf_data)
            return Response('file', mimetype='text/plain')
    # check for a known RDF mimetype
    elif request.data is not None:
        if 'text/turtle' in request.headers.get('Content-Type'):
            rdf_format = 'turtle'
        elif 'rdf+xml' in request.headers.get('Content-Type'):
            rdf_format = 'xml'
        elif 'application/rdf+json' in request.headers.get('Content-Type'):
            rdf_format = 'json-ld'
        else:
            return Response(
                'If you are POSTing raw RDF dat to this service, you must use one of the following RDF mimtypes:'
                'text/turtle (Turtle), application/rdf+xml (RDF/XML) or application/rdf+json (JSON-LD).',
                status=400, mimetype='text/plain')
        return Response('data', mimetype='text/plain')
    # we have a POST error
    else:
        print('e')
        return Response(
            'You must either post raw RDF data, with a correct Content-Type HTTP header or submit an HTML '
            'form to this endpoint with either an RDF file named \'file\' or a textarea input named \'copy\' '
            'containing RDF data',
            status=400, mimetype='text/plain')

    # try and make a graph, returning any errors to client


if __name__ == '__main__':
    app.run(debug=conf.DEBUG)
