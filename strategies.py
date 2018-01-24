import rdflib


def apply_strategy(g, strategy):
    """
    Receives an RDF graph and applies a filtering strategy to it

    :param g: an rdflib Graph to apply the strategy to
    :param strategy: the ID of the strategy applied
    :return: an rdflib Graph (results of input with strategy applied)
    """
    if strategy == 'basic':
        return apply_strategy_basic(g)


def apply_strategy_basic(g):
    # flip any generated to wasGeneratedBy
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

    # TODO: add in more inverses to point backwards here

    # find all Entity subclasses and annotate them as Entity
    u = '''
        PREFIX rdf: <http://www.w3.org/1999/02/22-rdf-syntax-ns#>
        PREFIX rdfs: <http://www.w3.org/2000/01/rdf-schema#>
        PREFIX owl: <http://www.w3.org/2002/07/owl#> 
        PREFIX prov: <http://www.w3.org/ns/prov#>
        INSERT {
            ?e rdf:type prov:Entity .
        }
        WHERE {
            ?e rdf:type/(rdfs:subClassOf|owl:equivalentClass)* prov:Entity .
        }
    '''
    g.update(u)

    # find all Activity subclasses and annotate them as Activity
    u = '''
        PREFIX rdf: <http://www.w3.org/1999/02/22-rdf-syntax-ns#>
        PREFIX rdfs: <http://www.w3.org/2000/01/rdf-schema#>
        PREFIX owl: <http://www.w3.org/2002/07/owl#> 
        PREFIX prov: <http://www.w3.org/ns/prov#>
        INSERT {
            ?e rdf:type prov:Activity .
        }
        WHERE {
            ?e rdf:type/(rdfs:subClassOf|owl:equivalentClass)* prov:Activity .
        }
    '''
    g.update(u)

    # find all Agent subclasses and annotate them as Agent
    u = '''
        PREFIX rdf: <http://www.w3.org/1999/02/22-rdf-syntax-ns#>
        PREFIX rdfs: <http://www.w3.org/2000/01/rdf-schema#>
        PREFIX owl: <http://www.w3.org/2002/07/owl#> 
        PREFIX prov: <http://www.w3.org/ns/prov#>
        INSERT {
            ?e rdf:type prov:Agent .
        }
        WHERE {
            ?e rdf:type/(rdfs:subClassOf|owl:equivalentClass)* prov:Agent .
        }
    '''
    g.update(u)

    # annotate every Entity, Activity & Agent with a label if it doesn't already have one
    u = '''
        PREFIX prov: <http://www.w3.org/ns/prov#>
        PREFIX rdf: <http://www.w3.org/1999/02/22-rdf-syntax-ns#>
        PREFIX rdfs: <http://www.w3.org/2000/01/rdf-schema#>
        INSERT {
            ?n rdfs:label ?str .
        }
        WHERE {
            { ?n a prov:Entity }
            UNION
            { ?n a prov:Activity }
            UNION
            { ?n a prov:Agent }
            FILTER(
                NOT EXISTS{ ?n rdfs:label ?l }
            )
            BIND(STR(?n) AS ?str)
        }
    '''
    g.update(u)
    # for r in g.query(u):
    #     print(r)

    # TODO: snip off the last URI segment after '/' or '#' and make that the label, not the whole URI

    # check to see if we have a valid graph for display
    q = '''
    SELECT (COUNT(?n) AS ?cnt) 
    WHERE {
        { ?n a prov:Entity }
        UNION
        { ?n a prov:Activity }
        UNION
        { ?n a prov:Agent }
    }'''
    for r in g.query(q):
        if int(r[0]) < 1:
            raise ValueError('the RDF you supplied, when filtered, using the basic strategy, did not produce '
                             'at least one Entity, Activity or Agent, Please ensure that class instances in your RDF'
                             'indicate that they are subClassOf either Entity, Activity or Agent or subclasses of '
                             'subclasses of them with the full subclass hierarchy defined.')


def apply_strategy_entity_only(g):
    # find all Entity subclasses and annotate them as Entity
    u = '''
        PREFIX rdf: <http://www.w3.org/1999/02/22-rdf-syntax-ns#>
        PREFIX rdfs: <http://www.w3.org/2000/01/rdf-schema#>
        PREFIX owl: <http://www.w3.org/2002/07/owl#> 
        PREFIX prov: <http://www.w3.org/ns/prov#>
        INSERT {
            ?e rdf:type prov:Entity .
        }
        WHERE {
            ?e rdf:type/(rdfs:subClassOf|owl:equivalentClass)* prov:Entity .
        }
    '''
    g.update(u)

    # find all Activity subclasses and annotate them as Activity
    u = '''
        PREFIX rdf: <http://www.w3.org/1999/02/22-rdf-syntax-ns#>
        PREFIX rdfs: <http://www.w3.org/2000/01/rdf-schema#>
        PREFIX owl: <http://www.w3.org/2002/07/owl#> 
        PREFIX prov: <http://www.w3.org/ns/prov#>
        INSERT {
            ?e rdf:type prov:Activity .
        }
        WHERE {
            ?e rdf:type/(rdfs:subClassOf|owl:equivalentClass)* prov:Activity .
        }
    '''
    g.update(u)

    # find all Agent subclasses and annotate them as Agent
    u = '''
        PREFIX rdf: <http://www.w3.org/1999/02/22-rdf-syntax-ns#>
        PREFIX rdfs: <http://www.w3.org/2000/01/rdf-schema#>
        PREFIX owl: <http://www.w3.org/2002/07/owl#> 
        PREFIX prov: <http://www.w3.org/ns/prov#>
        INSERT {
            ?e rdf:type prov:Agent .
        }
        WHERE {
            ?e rdf:type/(rdfs:subClassOf|owl:equivalentClass)* prov:Agent .
        }
    '''
    g.update(u)

    # replace any Entity <- Activity <- Entity chains with Entity <- Entity direct relationship
    u = '''
        PREFIX prov: <http://www.w3.org/ns/prov#>
        PREFIX rdf: <http://www.w3.org/1999/02/22-rdf-syntax-ns#>
        PREFIX rdfs: <http://www.w3.org/2000/01/rdf-schema#>
        INSERT {
            ?n rdfs:label ?str .
        }
        WHERE {
            ?a  prov:used           ?e1 .
            ?e2 prov:wasGeneratedby ?a  . # gene
        }
    '''
    g.update(u)

    # annotate every Entity with a label if it doesn't already have one
    u = '''
        PREFIX prov: <http://www.w3.org/ns/prov#>
        PREFIX rdf: <http://www.w3.org/1999/02/22-rdf-syntax-ns#>
        PREFIX rdfs: <http://www.w3.org/2000/01/rdf-schema#>
        INSERT {
            ?n rdfs:label ?str .
        }
        WHERE {
            ?n a prov:Entity
            FILTER(
                NOT EXISTS{ ?n rdfs:label ?l }
            )
            BIND(STR(?n) AS ?str)
        }
    '''
    g.update(u)
    # for r in g.query(u):
    #     print(r)

    # TODO: snip off the last URI segment after '/' or '#' and make that the label, not the whole URI

    # check to see if we have a valid graph for display
    q = '''
    SELECT (COUNT(?n) AS ?cnt) 
    WHERE {
        { ?n a prov:Entity }
        UNION
        { ?n a prov:Activity }
        UNION
        { ?n a prov:Agent }
    }'''
    for r in g.query(q):
        if int(r[0]) < 1:
            raise ValueError('the RDF you supplied, when filtered, using the basic strategy, did not produce '
                             'at least one Entity, Activity or Agent, Please ensure that class instances in your RDF'
                             'indicate that they are subClassOf either Entity, Activity or Agent or subclasses of '
                             'subclasses of them with the full subclass hierarchy defined.')

if __name__ == '__main__':
    g = rdflib.Graph().parse('_tests/test_subclasses.ttl', format='turtle')

    apply_strategy_basic(g)
    print(g.serialize(format='turtle').decode('utf-8'))
