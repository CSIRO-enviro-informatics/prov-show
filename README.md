# PROV Show
The purpose of this application is to allow users to make simple visualisations of [RDF](https://www.w3.org/RDF/) graphs, with a focus on [PROV-O](https://www.w3.org/TR/prov-o/), provenance ontology, graphs. It is intended to assist with prototyping PROV visualisations.

It is a small web application written in Python3, using the Flask HTTP framework to handle  its web form and the uploading of RDf data and the Python rdflib module for RDF manipulation.


## Using
A user can:
 
* supply RDF data to an endpoint 
    * either via direct input, file upload, or an HTTP POST
* filter the graph
    * the user can select one of number of strategies to include or exclude display elements
* view the result
    * typically as an interactive node-edge web graphic using the [vis.js](http://visjs.org) JavaScript visualisation toolkit
    * or as a static node-edge image for download
    * or the filtered raw RDF data
  

### Uploading data
You can use the data upload form presented by this application at its homepage to:

* **directly input RDF**
    * copy 'n paste your data into a text box
    * you will need to indicate the RDF format used
* **upload an RDF file**
* **send an HTTP POST** of RDF data    
    * the POST should be sent to the /show endpoint of the application
    * you will need to correctly set the MIME type for your RDF data
    

### Filtering data
This application will supply a number of selectable filtering strategies, any of which you can choose, which will then be applied to uploaded data. The strategies implemented so far are:

* **basic**
    * default
    * aims to represent simple Entity, Activity & Agent classes of object with basic relationships only
* **entities only**
    *  removes everything from uploaded RDF data other than Entities and builds relationships between Entities where it can reason about them from other relationships
    
For full documentation for the strategies, see the /strategies web page delivered by the application or view the [strategies.py](strategies.py) file in this repository.

## Using this repository

## Software requirements
This repository works with Python 3.6 and the packages listed in [requirements.txt](requirements.txt).

## License 
This code is supplied under a Creative Commons 4.0 license. See [LICENSE](LICENSE) for the specifics.

## Citation
If you would like to refer to this repository, please do so using the URI http://promsns.org/repo/prov-show. A standard software repository citation might look like:

> Car, N.J. (2018) PROV Show. Software repository of Python 3.6 Flask/rdflib code Repository using Git version control. Available online at http://promsns.org/repo/prov-show, accessed yyyy-mm-dd.

## Author
**Nicholas Car**  
*Senior Experimental Scientist*  
CSIRO Land & Water  
Dutton Park, Queensland, Australia  
<nicholas.car@csiro.au>  
<http://orcid.org/0000-0002-8742-7730>
