# -*- coding: utf-8 -*-
import scrapy


class BoraItem(scrapy.Item):
    company = scrapy.Field()
    date = scrapy.Field()
    url = scrapy.Field()
    content = scrapy.Field()
    id = scrapy.Field()
    type = scrapy.Field()
