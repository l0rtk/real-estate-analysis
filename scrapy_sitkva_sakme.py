#!/usr/bin/env python3
import scrapy
from scrapy.crawler import CrawlerProcess
from scrapy import signals
from scrapy.signalmanager import dispatcher
import pandas as pd
from datetime import datetime 

import logging

logging.getLogger('scrapy').setLevel(logging.WARNING)
logging.getLogger('scrapy').propagate = False


class SitkvaSakmeArticle():
    
    def get_price(self,response):
        """ 
        args:
            response: scrapy response
    
        returns price_dict: dictionary
        """
    
        price_dict = {}

        price = response.xpath('//div[@class="article_right_price price "]/text()').get().strip()
        price = "".join(price.split())
        price = int(price)

        currencies = response.xpath('//div[@class="switch"]')
        currencies = currencies[0]
        active_curr = currencies.css('label.switch-label-on::text').get()

        price_dict['price'] = price
        price_dict['currency'] = active_curr

        return price_dict
    
    def get_params(self,response):
    
        """
        args:
            response: scrapy response
    
        returns params: dictionary
        """
        
        params = {}

        top_params = response.xpath('//div[has-class("ParamsDetTop")]')
        top_names = top_params.xpath('//div[@class="ParamsBotBlk"]/text()').getall()
        top_values = top_params.xpath('//text/text()').getall()

        for i in range(len(top_names)):
            params[top_names[i].strip()] = top_values[i].strip()

        
        bottom_params = response.xpath('//div[has-class("ParamsbotProj")]')
        bottom_names = bottom_params.xpath('//span[@class="TitleEachparbt"]/text()').getall()
        bottom_values = bottom_params.xpath('//span[@class="PRojeachBlack"]/text()').getall()

        for i in range(len(bottom_names)):
            params[bottom_names[i].strip()] = bottom_values[i].strip()

        return params

    
    
    def get_additional_info(self,response):
        """
        args:
            response: scrapy response
    
            returns additional_info: dictionary
        """
    
        additional_info = {}

        info_div = response.xpath('//div[@class="AditionalInfoBlocksBody"]')
        infos = info_div.xpath('//div[has-class("parameteres_item_each")]')

        for info in infos:
            name = info.css('::text').get().strip()
            isChecked = info.css('span').xpath("@class").extract()[0].strip()
            if isChecked == "CheckedParam":
                additional_info[name] = 1
            if isChecked == "UnCheckedParam":
                additional_info[name] = 0

        return additional_info    
    

    def get_article_data(self,response):
        """
        args:
            response: scrapy response
    
        returns article_data: dictionary
        """
        article_data = {}
    
        id_div = response.xpath('//div[@class="article_item_id"]')
        id_text = id_div.css('span::text').get().strip()
        article_data['id'] = id_text

        date = response.xpath('//div[has-class("add_date_block")]/text()').get().strip()

        article_data['date'] = date
        article_data['link'] = response.url

        return article_data
    
    
    def get_author(self,response):
        """ 
        args:
            response: scrapy response
        returns author: dictionary
        """
        author = {}

        name = response.xpath('//div[has-class("author_type")]/text()').get().strip().split('\r')[0]
        number = response.xpath('//span[has-class("EAchPHonenumber")]/text()').get()

    
        author['name'] = name
        author['number'] = number
    
        return author
        
    
    def get_location(self,response):
        """ 
        args:
            response: scrapy response
        returns street: string
        """
        loc = {}

        location_div = response.xpath('//div[has-class("StreeTaddressList")]')
        location = location_div.css('a::text').get().strip()
        loc['location'] = location

        return loc
        
    

    def get_article_all_data(self,response):
        """
        args:
            response: scrapy response

        returns data: dictionary | all info on the page
        """
        price = self.get_price(response)
        params = self.get_params(response)
        add_info = self.get_additional_info(response)
        article_data = self.get_article_data(response)
        author = self.get_author(response)
        location = self.get_location(response)

        res = {**price,**params,**add_info,**article_data,**author ,**location} 
        
        return res



class SitkvaSakmeSpider(scrapy.Spider):
    name = "quotes"
    domain = "https://ss.ge"
    ss_article = SitkvaSakmeArticle()
    pages = 0

    def __init__(self,links):
        self.links = links

    def start_requests(self):
        for link in self.links:
            self.pages += 1
            print('page: ',str(self.pages))
            yield scrapy.Request(url=link, callback=self.parse)

    def parse(self, response):
        article_links = []
        articles = response.xpath('//div[@class="list-img-cont"]')
        for article in articles:
            link = article.css('a::attr(href)').get()
            link = self.domain + link
            
            if link not in article_links:
                article_links.append(link)

        for link in article_links:
            yield scrapy.Request(url=link, callback=self.parse_article)


    # parsing each article
    def parse_article(self,response):
        all_data = self.ss_article.get_article_all_data(response)
        return all_data


def spider_results(links):
    results = []

    def crawler_results(signal, sender, item, response, spider):
        results.append(item)

    dispatcher.connect(crawler_results, signal=signals.item_scraped)

    process = CrawlerProcess()
    process.crawl(SitkvaSakmeSpider,links = links)
    process.start()  # the script will block here until the crawling is finished
    return results






def result_to_dataframe(results):
    res_dict = {}

    # fill with all fields
    for res in results:
        for k,v in res.items():
            res_dict[k] = []

    for res in results:
        for key in res_dict.keys():
            try:
                res_dict[key].append(res[key])
            except KeyError:
                res_dict[key].append('NaN')

    df = pd.DataFrame(res_dict)

    return df



if __name__ == "__main__":

    pages = 3
    links = [f"https://ss.ge/ka/udzravi-qoneba/l/bina/iyideba?Page={i}&RealEstateTypeId=5&RealEstateDealTypeId=4&BaseUrl=/ka/udzravi-qoneba/l&CurrentUserId=&Query=&MunicipalityId=95&CityIdList=95&IsMap=false&subdistr=32,33,34,35,36,37,53,38,39,40,41,42,43&stId=&PrcSource=1&RealEstateStatus=&CommercialRealEstateType=&QuantityFrom=&QuantityTo=&PriceType=false&CurrencyId=1&PriceFrom=&PriceTo=&Context.Request.Query[Query]=&FloorType=&Balcony_Loggia=&Toilet=&Project=&Other=&State=&HouseWillHaveToLive=&BedroomsFrom=&BedroomsTo=&KitchenAreaFrom=&KitchenAreaTo=&FloorsFrom=&FloorsTo=&AdditionalInformation=&ConstructionAgencyId=&AgencyId=&VipStatus=&PageSize=20&Sort.SortExpression=%221%22&WIth360Image=false&IsConstruction=false&WithImageOnly=false&IndividualEntityOnly=false&IsPetFriendly=false&IsForUkraine=false" for i in range(0,pages)] 
    results = spider_results(links)

    now = datetime.now().strftime('%m-%d %H:%M')
    pd.DataFrame(results).to_csv(f'./data/{now}-data.csv')
