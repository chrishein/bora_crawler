# -*- coding: utf-8 -*-
import datetime
import json
import re
import urllib
import copy

import scrapy

from scrapy.selector import Selector
from datetime import date
from bora_crawler.items import BoraItem


class BoraSpider(scrapy.Spider):
    name = "bora"
    allowed_domains = ["boletinoficial.gob.ar"]
    start_urls = ()

    def __init__(self, start_date=None, end_date=None, *args, **kwargs):
        super(BoraSpider, self).__init__(*args, **kwargs)
        if start_date is not None:
            self.start_date = datetime.datetime.strptime(start_date, "%Y-%m-%d").date()
        else:
            self.start_date = date(2011, 1, 1)

        if end_date is not None:
            self.end_date = datetime.datetime.strptime(end_date, "%Y-%m-%d").date()
        else:
            self.end_date = date.today()

    def start_requests(self):
        current_date = copy.copy(self.start_date)
        delta = datetime.timedelta(days=1)
        url = 'https://www.boletinoficial.gob.ar/secciones/secciones.json'
        while current_date <= self.end_date:
            payload = {'nombreSeccion': 'segunda', 'subCat': 'all',
                       'offset': 1, 'itemsPerPage': 500,
                       'fecha': current_date.strftime("%Y%m%d")}

            yield scrapy.Request(url=url, callback=self.parse_date_publication,
                                 method="POST",
                                 headers={'X-Requested-With': 'XMLHttpRequest',
                                          'Referer':'https://www.boletinoficial.gob.ar/',
                                          'Accept': 'application/json, text/javascript, */*; q=0.01',
                                          'Content-Type': 'application/x-www-form-urlencoded; charset=UTF-8'
                                          },
                                 body=urllib.urlencode(payload)
                                 )

            current_date += delta

    def parse_date_publication(self, response):
        data = json.loads(response.body)
        url = 'https://www.boletinoficial.gob.ar/norma/detalleSegunda'

        for edict in data['dataList'][0]:
            if edict['rubro'] in ('CONSTITUCION SA', 'REFORMA SA', 'CONTRATO SRL', 'MODIFICACIONES SRL'):
                payload = {'id': edict['id']}
                yield scrapy.Request(url=url, callback=self.parse_edict,
                                     method="POST",
                                     headers={'X-Requested-With': 'XMLHttpRequest',
                                              'Referer':'https://www.boletinoficial.gob.ar/',
                                              'Accept': 'application/json, text/javascript, */*; q=0.01',
                                              'Content-Type': 'application/x-www-form-urlencoded; charset=UTF-8'
                                              },
                                     body=urllib.urlencode(payload))

    def parse_edict(self, response):
        data = json.loads(response.body)['dataList']
        selector = Selector(text=data['textoCompleto'])

        item = BoraItem()
        item['id'] = data['idTramite']
        item['type'] = data['rubroDescripcion']
        item['company'] = selector.xpath('//h3/text()').extract_first().strip()
        item['date'] = datetime.datetime.strptime(data['fechaPublicacion'], "%Y%m%d").date()
        item['content'] = selector.xpath('//p/text()').extract_first().strip()

        yield item
