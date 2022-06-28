#!/usr/bin/env python3
import scrapy
from scrapy.crawler import CrawlerProcess

    


class MySpider(scrapy.Spider):
    name = "quotes"
    domain = "https://ss.ge"

    def start_requests(self):
        links = [f"https://ss.ge/ka/udzravi-qoneba/l/bina/iyideba?Page={i}&RealEstateTypeId=5&RealEstateDealTypeId=4&MunicipalityId=95&CityIdList=95&subdistr=47" for i in range(1,50)]
        
        for link in links:
            yield scrapy.Request(url=link, callback=self.parse)

    def parse(self, response):
        article_links = []
        articles = response.xpath('//div[@class="list-img-cont"]')
        for article in articles:
            link = article.css('a::attr(href)').get()
            link = self.domain + link
            
            if link not in article_links:
                article_links.append(link)

        for link in self.article_links:
            yield scrapy.Request(url=link, callback=self.parse_article)

    # parsing each article
    def parse_article(self,response):
        pass

process = CrawlerProcess()

process.crawl(MySpider)
process.start() 