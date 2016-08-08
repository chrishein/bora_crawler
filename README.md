# BORA Crawler

[BORA](https://www.boletinoficial.gob.ar) (Bolet&iacute;n Oficial de la Republica Argentina) Crawler implemented using [Scrapy](http://scrapy.org/).

[BORA](https://www.boletinoficial.gob.ar) is the [Official Gazette](https://en.wikipedia.org/wiki/Government_gazette) for Argentina, where the government publishes public or legal notices, including companies incorporation or modifications in their structure and share holders.

This crawler saves the following information for each notice:
* id: Notice ID in the BORA website
* company: Name of the company
* date: Date of publication
* content: Text of publication

The content of the publication contains unstructured text and must be further processed in order to extract data.

## Running the Spider

To run the spider and save the crawled items in JSON use:

```bash
scrapy crawl bora -o items_bora.json
```
