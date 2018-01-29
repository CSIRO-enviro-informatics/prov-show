import rdflib
import pickle
import os
import _config as conf


def get_prov_o_graph():
    # if we have a pickle, use it, if not, parse the text copy of the ont, return that graph and pickle it for future
    prov_o_pickled = os.path.join(conf.APP_DIR, 'prov-o.pickle')
    prov_o_text = os.path.join(conf.APP_DIR, '_config', 'prov-o.ttl')
    if os.path.isfile(prov_o_pickled):
        po = pickle.load(open(prov_o_pickled, 'rb'))
    else:
        po = rdflib.Graph()
        po.load(prov_o_text, format='turtle')
        with open(prov_o_pickled, 'wb') as p:
            pickle.dump(po, p)

    return po


def apply_strategy(grf, strategy):
    """
    Receives an RDF graph and applies a filtering strategy to it

    :param g: an rdflib Graph to apply the strategy to
    :param strategy: the ID of the strategy applied
    :return: an rdflib Graph (results of input with strategy applied)
    """
    if strategy == 'basic':
        return apply_strategy_basic(grf)
    elif strategy == 'entities_only':
        return apply_strategy_entities_only(grf)


def apply_strategy_basic(grf):
    # add PROV-O to the data being processed to allow for PROV-O reasoning
    po = get_prov_o_graph()
    grf = grf + po

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
    grf.update(u)

    # indicate Entity attribution
    u = '''
        PREFIX prov: <http://www.w3.org/ns/prov#>
        INSERT {
            ?e prov:wasAttributedTo ?ag .
        }
        WHERE {
            ?e prov:wasGeneratedBy/prov:wasAssociatedWith ?ag .
        }
    '''
    grf.update(u)

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
    grf.update(u)

    # class anything that got used or wasGeneratedBy as an Entity (duck-typing)
    u = '''
        PREFIX rdf: <http://www.w3.org/1999/02/22-rdf-syntax-ns#>
        PREFIX rdfs: <http://www.w3.org/2000/01/rdf-schema#>
        PREFIX owl: <http://www.w3.org/2002/07/owl#> 
        PREFIX prov: <http://www.w3.org/ns/prov#>
        INSERT {
            ?x a prov:Entity .
            ?y a prov:Entity .
        }
        WHERE {
            ?a prov:used ?x .
            ?y prov:wasGeneratedBy ?a2 .
        }
    '''
    grf.update(u)

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
    grf.update(u)

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
    grf.update(u)

    # ensure all things that are used/generated are understood to be Entities
    u = '''
        PREFIX rdf: <http://www.w3.org/1999/02/22-rdf-syntax-ns#>
        PREFIX rdfs: <http://www.w3.org/2000/01/rdf-schema#>
        PREFIX owl: <http://www.w3.org/2002/07/owl#> 
        PREFIX prov: <http://www.w3.org/ns/prov#>
        INSERT {
            ?e rdf:type prov:Entity .
        }
        WHERE {
            {?a prov:used ?e .}
            UNION
            {?a prov:generated e .}
        }
    '''
    grf.update(u)

    # ensure all things that used or that generated are understood to be Activities
    u = '''
        PREFIX rdf: <http://www.w3.org/1999/02/22-rdf-syntax-ns#>
        PREFIX rdfs: <http://www.w3.org/2000/01/rdf-schema#>
        PREFIX owl: <http://www.w3.org/2002/07/owl#> 
        PREFIX prov: <http://www.w3.org/ns/prov#>
        INSERT {
            ?a rdf:type prov:Activity .
        }
        WHERE {
            {?a prov:used ?e .}
            UNION
            {?a prov:generated e .}
        }
    '''
    grf.update(u)

    # annotate every Entity, Activity & Agent with a label if it doesn't already have one
    # TODO: snip off the last URI segment after '/' or '#' and make that the label, not the whole URI
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
    grf.update(u)

    # replace all qualified associations with simple relationships
    u = '''
        PREFIX prov: <http://www.w3.org/ns/prov#>
        PREFIX rdf: <http://www.w3.org/1999/02/22-rdf-syntax-ns#>
        PREFIX rdfs: <http://www.w3.org/2000/01/rdf-schema#>
        DELETE {
            ?s ?p ?qa .
            ?qa ?p2 ?o2 .
        }
        INSERT {
            ?a prov:wasAssociatedWith ?ag .
        }
        WHERE {
            ?s ?p ?qa .
            ?qa ?p2 ?o2 .
            ?a prov:qualifiedAssociation ?qa .
            ?qa prov:agent ?ag .
        }
    '''
    grf.update(u)

    # remove all the non-Entities/Activities/Agents and their properties
    u = '''
        PREFIX prov: <http://www.w3.org/ns/prov#>
        PREFIX rdf: <http://www.w3.org/1999/02/22-rdf-syntax-ns#>
        PREFIX rdfs: <http://www.w3.org/2000/01/rdf-schema#>
        DELETE {
            ?s ?p ?o .
            ?o ?p2 ?o2 .
        }
        WHERE {
            ?s ?p ?o .
            MINUS {
                {?s a prov:Entity .}
                UNION
                {?s a prov:Activity .}
                UNION
                {?s a prov:Agent .}
            }
        }
    '''
    grf.update(u)

    # remove the polluting PROV-O triples to get back just the data with enhancements
    grf = grf - po

    # check to see if we have a valid graph for display
    q = '''
    PREFIX prov: <http://www.w3.org/ns/prov#>
    SELECT (COUNT(?n) AS ?cnt) 
    WHERE {
        { ?n a prov:Entity }
        UNION
        { ?n a prov:Activity }
        UNION
        { ?n a prov:Agent }
    }'''
    for r in grf.query(q):
        if int(r[0]) < 1:
            raise ValueError('the RDF you supplied, when filtered, using the basic strategy, did not produce '
                             'at least one Entity, Activity or Agent, Please ensure that class instances in your RDF'
                             'indicate that they are subClassOf either Entity, Activity or Agent or subclasses of '
                             'subclasses of them with the full subclass hierarchy defined.')

    return grf


def apply_strategy_entities_only(grf):
    # add PROV-O to the data being processed to allow for PROV-O reasoning
    po = get_prov_o_graph()
    grf = grf + po

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
    grf.update(u)

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
    grf.update(u)

    # class anything that got used or wasGeneratedBy as an Entity (duck-typing)
    u = '''
        PREFIX rdf: <http://www.w3.org/1999/02/22-rdf-syntax-ns#>
        PREFIX rdfs: <http://www.w3.org/2000/01/rdf-schema#>
        PREFIX owl: <http://www.w3.org/2002/07/owl#> 
        PREFIX prov: <http://www.w3.org/ns/prov#>
        INSERT {
            ?x a prov:Entity .
            ?y a prov:Entity .
        }
        WHERE {
            ?a prov:used ?x .
            ?y prov:wasGeneratedBy ?a2 .
        }
    '''
    grf.update(u)

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
    grf.update(u)

    # replace any Entity <- Activity <- Entity chains with Entity <- Entity direct relationship
    u = '''
        PREFIX prov: <http://www.w3.org/ns/prov#>
        PREFIX rdf: <http://www.w3.org/1999/02/22-rdf-syntax-ns#>
        PREFIX rdfs: <http://www.w3.org/2000/01/rdf-schema#>
        INSERT {
            ?e2     prov:wasDerivedFrom ?e1 .
        }
        WHERE {
            ?a      prov:used           ?e1 .
            {?e2    prov:wasGeneratedby ?a  .}
            UNION
            {?a     prov:generated      ?e2 .}
        }
    '''
    grf.update(u)

    # TODO: add in other PROV-equivalent relationships for other qualified things like Associations

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
    grf.update(u)

    # TODO: snip off the last URI segment after '/' or '#' and make that the label, not the whole URI

    # remove all Activities & Agents and references to them
    # (need to remove references to them (i.e. Activity & Agent as object) before removing them else
    # we can't find them)
    u = '''
        PREFIX prov: <http://www.w3.org/ns/prov#>
        PREFIX rdf: <http://www.w3.org/1999/02/22-rdf-syntax-ns#>
        PREFIX rdfs: <http://www.w3.org/2000/01/rdf-schema#>
        DELETE {
            ?x ?y ?s .
        }
        WHERE {
            {?s a prov:Activity .}
            UNION
            {?s a prov:Agent .}
            ?x ?y ?s .
        }
    '''
    grf.update(u)

    # remove all the non-Entities and their properties
    u = '''
        PREFIX prov: <http://www.w3.org/ns/prov#>
        PREFIX rdf: <http://www.w3.org/1999/02/22-rdf-syntax-ns#>
        PREFIX rdfs: <http://www.w3.org/2000/01/rdf-schema#>
        DELETE {
            ?s ?p ?o .
            ?o ?p2 ?o2 .
        }
        WHERE {
            ?s ?p ?o .
            MINUS {
                ?s a prov:Entity .
            }
        }
    '''
    grf.update(u)

    # remove the polluting PROV-O triples to get back just the data with enhancements
    grf = grf - po

    # check to see if we have a valid graph for display
    q = '''
    PREFIX prov: <http://www.w3.org/ns/prov#>
    SELECT (COUNT(?n) AS ?cnt) 
    WHERE {
        ?n a prov:Entity
    }'''
    for r in grf.query(q):
        if int(r[0]) < 1:
            raise ValueError('the RDF you supplied, when filtered, using the basic strategy, did not produce '
                             'at least one Entity, Activity or Agent, Please ensure that class instances in your RDF'
                             'indicate that they are subClassOf either Entity, Activity or Agent or subclasses of '
                             'subclasses of them with the full subclass hierarchy defined.')

    return grf


if __name__ == '__main__':
    # run tests
    # make a graph of PROV-O, pickle it to emulate Flask app

    # Basic
    grf = rdflib.Graph()
    grf.parse('_tests/test_entities_only.ttl', format='turtle')
    strategy = 'entities_only'

    print(apply_strategy(grf, strategy).serialize(format='turtle').decode('utf-8'))

    # # Entities only
    # g2 = rdflib.Graph().parse('_tests/test_entities_only.ttl', format='turtle')
    # apply_strategy_entities_only(g2)
    # print(g2.serialize(format='turtle').decode('utf-8'))

