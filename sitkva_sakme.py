#!/usr/bin/env python3

import requests
from bs4 import BeautifulSoup
from pprint import pprint


class SitkvaSakme:
    
    domain = "https://ss.ge"
    
    def __init__(self,page_links):
        self.page_links = page_links


    def get_article_links(self):
        """
        args:
            page_links: list
        returns list of the links
    
        links: list
        """
    
    
        article_links = []
        for link in self.page_links:
            res = requests.get(link)
            soup = BeautifulSoup(res.text, 'html.parser')
            
            articles = soup.find_all('div', class_='list-img-cont')
    
            for article in articles:
                href = article.get('href')
                ancher = article.find('a')
                article_link = ancher.get('href')
                article_links.append(self.domain+article_link)
    
    
        return article_links


class SitkvaSakmeArticle():
    
    def get_price(self,soup):
        """ 
        args:
            soup: BeautifulSoup object
    
        returns price_dict: dictionary
        """
    
        price_dict = {}
    
        price = soup.find('div', class_='article_right_price').get_text().strip()
        price = "".join(price.split())
        price = int(price) 
        
        currencies = soup.find('div',class_='switch')
        currency = currencies.find('label','switch-label-on').text
        
        price_dict['price'] = price
        price_dict['currency'] = currency
    
    
        return price_dict
    
    
    def get_params(self,soup):
    
        """
        args:
            soup: BeautifulSoup object
    
        returns params: dictionary
        """
        
        params = {}
    
        top_params = soup.find_all('div',class_='EAchParamsBlocks')
    
        for param in top_params:
            pname = param.find('div',class_='ParamsBotBlk').text.strip()
            pvalue = param.find('div',class_='ParamsHdBlk').text.strip()
            params[pname] = pvalue
        
        bottom_params = soup.find_all('div',class_='ProjBotEach')
    
        for param in bottom_params:
            pname = param.find('span',class_='TitleEachparbt').text.strip()
            pvalue = param.find('span',class_='PRojeachBlack').text.strip()
            params[pname] = pvalue
    
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


if __name__ == '__main__':
    link = 'https://ss.ge/ka/udzravi-qoneba/qiravdeba-dghiurad-2-otaxiani-bina-saburtaloze-3780440'
    res = requests.get(link)
    soup = BeautifulSoup(res.text,'html.parser')
    
    ss_article = SitkvaSakmeArticle()
    res = ss_article.get_article_all_data(soup)
    pprint(res)
