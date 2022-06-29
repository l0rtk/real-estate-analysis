#!/usr/bin/env python3
import scrapy
from scrapy.crawler import CrawlerProcess
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

    
    
    def get_additional_info(self,soup):
        """
        args:
            soup: BeautifulSoup object
    
            returns additional_info: dictionary
        """
    
        additional_info = {}
    
        info_div = soup.find('div',class_='AditionalInfoBlocksBody')
        infos = info_div.find_all('div',class_='parameteres_item_each')
    
        for info in infos:
            is_checked = info.find('span',class_='CheckedParam')
            
            if is_checked:
                additional_info[info.text.strip()] = True
            else:
                additional_info[info.text.strip()] = False
    
        return additional_info
    
    
    def get_article_data(self,soup):
        """
        args:
            soup: BeautifulSoup object
    
        returns article_data: dictionary
        """
        article_data = {}
    
        id_div = soup.find('div',class_='article_item_id')
        id_text = id_div.find('span').text.strip()
    
        date = soup.find('div',class_='add_date_block').text.strip()
        
        article_data['id'] = id_text
        article_data['date'] = date
    
        return article_data
    
    
    def get_author(self,soup):
        """ 
        args:
            soup: BeautifulSoup object
        returns author: dictionary
        """
        author = {}
        
        name = soup.find('div',class_='author_type').text.strip().split('\r')[0]
        number = soup.find('span',class_='EAchPHonenumber').text
    
        author['name'] = name
        author['number'] = number
    
        return author
        
    

    def get_article_all_data(self,soup):
        """
        args:
            soup: BeautifulSoup object

        returns data: dictionary | all info on the page
        """
        price = self.get_price(soup)
        params = self.get_params(soup)
        add_info = self.get_additional_info(soup)
        article_data = self.get_article_data(soup)
        author = self.get_author(soup)


        res = {**price,**params,**add_info,**article_data,**author } 
        
        return res


ss_article = SitkvaSakmeArticle()

class MySpider(scrapy.Spider):
    name = "quotes"
    domain = "https://ss.ge"

    def start_requests(self):
        links = [f"https://ss.ge/ka/udzravi-qoneba/l/bina/iyideba?Page={i}&RealEstateTypeId=5&RealEstateDealTypeId=4&MunicipalityId=95&CityIdList=95&subdistr=47" for i in range(1,5)]
        
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

        for link in article_links:
            yield scrapy.Request(url=link, callback=self.parse_article)




    # parsing each article
    def parse_article(self,response):
        price = ss_article.get_params(response)
        print('\n',price,'\n')

process = CrawlerProcess()

process.crawl(MySpider)
process.start() 
