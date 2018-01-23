# PROV Show
The purpose of this application is to allow users to make simple visualisations of [RDF](https://www.w3.org/RDF/) graphs, with a focus on [PROV-O](https://www.w3.org/TR/prov-o/), provenance ontology, graphs.

It is a small web application written in Python3, using the Flask HTTP framework, and to allow for RDF graph visualisations a user can:
 
* supply RDf data to an endpoint 
    * either via direct input, file upload or HTTP POST
* filter the graph
    * the user can select one of number of strategies to include or exclude display elements
* view the result
    * typically as an interactive node-edge web graphic using the [vis.js](http://visjs.org/) JavaScript visualisation toolkit
    * or as a static node-edge image for download
    * or the raw filtered RDF data
  
## Using this
### Uploading data
You can use the data upload form presented by this application at its homepage to:

* **directly input RDF** - copy 'n paste your data in
* **upload an RDF file**

You can also POST, that is send an HTTP POST request, of RDF data directly to the show endpoint (/show)

### Filtering data
This application will supply a number of selectable filtering strategies, any of which you can choose, which will then be applied to uploaded data. The strategies implemented so far are:

* **basic**
    * 

## Using this repository

## Software requirements
This repository works with Python 3.6 and the packages listed in [requirements.txt](requirements.txt).

## License 
This code is supplied under a Creative Commons 4.0 license. See [LICENSE](LICENSE) for the specifics.

## Citation
If you would like to refer to this repository, please do so using the URI http://promsns.org/repo/prov-show. A standard software repository citation might look like:

> Car, N.J. (2017) PROV SVG. Python 3.6 Flask code Repository using Git version control. Available online at http://promsns.org/repo/prov-svg, accessed yyyy-mm-dd.

## Author
**Nicholas Car**  
*Senior Experimental Scientist*  
<nicholas.car@csiro.au>  
<http://orcid.org/0000-0002-8742-7730>
