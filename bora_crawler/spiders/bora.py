# -*- coding: utf-8 -*-
import datetime
import json
import re
import urllib

import scrapy

from bs4 import BeautifulSoup
from datetime import date
from bora_crawler.items import BoraItem


class BoraSpider(scrapy.Spider):
    name = "bora"
    allowed_domains = ["boletinoficial.gob.ar"]
    start_urls = ()

    def start_requests(self):
        start_date = date(2011, 1, 1)
        # end_date = date.today() - timedelta(1)
        # end_date = date(2015, 12, 31)
        end_date = date(2011, 02, 15)
        current_date = start_date
        delta = datetime.timedelta(days=1)
        url = 'https://www.boletinoficial.gob.ar/secciones/secciones.json'
        while current_date <= end_date:
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
            if edict['rubro'] in ('CONSTITUCION SA', 'REFORMA SA'):
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
        soup = BeautifulSoup(data['textoCompleto'], 'lxml')

        item = BoraItem()
        item['id'] = data['idTramite']
        item['company'] = soup.h3.string
        item['date'] = datetime.datetime.strptime(data['fechaPublicacion'], "%Y%m%d").date()
        item['content'] = soup.p.string

        yield item
