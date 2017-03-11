from rdflib import Graph


def preconstruct_prov_relationships(g):
    u = '''
        PREFIX prov: <http://www.w3.org/ns/prov#>
        DELETE {
            ?a prov:generated ?e .
        }
        INSERT {
            ?e prov:wasGeneratedBy ?a .
        }
        WHERE {
            ?a prov:generated ?e .
        }
    '''
    g.update(u)

    # u4 = '''
    #     PREFIX prov: <http://www.w3.org/ns/prov#>
    #     INSERT {
    #         ?e prov:wasDerivedFrom ?e_up .
    #     }
    #     WHERE {
    #         ?e prov:wasGeneratedBy/prov:used ?e_up .
    #     }
    # '''
    # g.update(u4)
    #
    # u2 = '''
    #     PREFIX prov: <http://www.w3.org/ns/prov#>
    #     INSERT {
    #         ?a prov:wasInformedBy ?a2 .
    #     }
    #     WHERE {
    #         ?a prov:used/prov:wasGeneratedBy ?a2 .
    #     }
    # '''
    # g.update(u2)
    #
    # u3 = '''
    #     PREFIX prov: <http://www.w3.org/ns/prov#>
    #     INSERT {
    #         ?e prov:wasAttributedTo ?ag .
    #     }
    #     WHERE {
    #         ?e prov:wasGeneratedBy/prov:wasAssociatedWith ?ag .
    #     }
    # '''
    # g.update(u3)


def make_nodes(g):
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
            nodes += '\t{id: "%(node_id)s", label: "%(label)s", shape: "ellipse", color:{background:"#FFFC87", border:"#808080"}},\n' % {
                      'node_id': row['s'],
                      'label': row['label']
            }
        elif str(row['o']) == 'http://www.w3.org/ns/prov#Activity':
            nodes += '\t{id: "%(node_id)s", label: "%(label)s", shape: "box", color:{background:"#9FB1FC", border:"blue"}},\n' % {
                      'node_id': row['s'],
                      'label': row['label']
            }
        elif str(row['o']) == 'http://www.w3.org/ns/prov#Agent':
            nodes += '\t{id: "%(node_id)s", label: "%(label)s", image: "/static/agent.png", shape: "image"},\n' % {
                      'node_id': row['s'],
                      'label': row['label']
            }

    return nodes


def make_edges(g):
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
        edges += '\t{from: "%(from)s", to: "%(to)s", arrows:"to", font: {align: "bottom"}, color:{color:"black"}, label: "%(relationship)s"},\n' % {
            'from': row['s'],
            'to': row['o'],
            'relationship': str(row['p']).split('#')[1]
        }

    return edges


def make_nodes_edges(g):
    preconstruct_prov_relationships(g)

    nodes = 'var nodes = new vis.DataSet([\n'
    nodes += make_nodes(g)
    nodes = nodes.rstrip().rstrip(',') + '\n  ]);\n\n'

    edges = 'var edges = new vis.DataSet([\n'
    edges += make_edges(g)
    edges = edges.rstrip().rstrip(',') + '\n  ]);\n\n'

    return {
        'nodes': nodes,
        'edges': edges
    }


def make_nodes_edges_javascript(g):
    ne = make_nodes_edges(g)
    ne_str = ne.get('nodes')
    ne_str += '\n\n'
    ne_str += ne.get('edges')
    return ne_str


if __name__ == '__main__':
    g = Graph().parse('c:/work/proms-viz/data/test_prune_11.ttl', format='turtle')
    preconstruct_prov_relationships(g)
    nodes = 'var nodes = new vis.DataSet([\n'
    nodes += make_nodes(g)
    nodes = nodes.rstrip().rstrip(',') + '\n  ]);\n\n'

    edges = 'var edges = new vis.DataSet([\n'
    edges += make_edges(g)
    edges = edges.rstrip().rstrip(',') + '\n  ]);\n\n'