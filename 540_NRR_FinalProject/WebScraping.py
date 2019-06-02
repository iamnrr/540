# -*- coding: utf-8 -*-
"""
Author: Nanduri Raghu Raman

Date: May 22 2019

Execution: This code can be executed by entering one of the following commands
    > python WebScrapping.py
    > python WebScrapping.py laptops
    > python WebScrapping.py TVs
    
    The expected output for the code is list of all the products for the searched symbol from the Samsclub website (only)
    The output is delivered as csv and placed in /data sub-directory.

"""


# Importing required modules
from urllib import request
import pandas as pd
import numpy as np
from collections import OrderedDict
from bs4 import BeautifulSoup

import re
import os
import sys
import logging
import configparser
from datetime import datetime



def get_config():
    '''
    function to fetch configuration parameters (log dir, output dir, URLS etc.)
    '''
    config = configparser.ConfigParser()
    config.read(['config/config.cfg'])
    return config


def substr(text, startfrom, till):    
    '''
    Function that takes text and returns substring of the text 
    Args:
     startfrom : string that specifies the starting position.
     till:       string that specifies the ending position 
    '''
    typ1 = text.find(startfrom) #re.search(startfrom, text).start()
    typ2 = text.find(till)
    return text[typ1+5:typ2-1]

def start_logger():
    '''
    function that configures the basic logger
    '''
    config = get_config()

    logdir = config.get('folders', 'logdir') 
    print(logdir)

    logging.basicConfig(filename= logdir + '/webscrapping_%s.log' %
                        datetime.strftime(datetime.now(), '%m%d%Y_%H%M%S'),
                        level=logging.DEBUG,
                        format='%(asctime)s %(message)s',
                        datefmt='%m-%d %H:%M:%S')


def run(url, symbol):
    
    #content = urllib.request.urlopen(url+symbol).read()
    content = request.urlopen(url+symbol).read()
    
    #pass the HTML to Beautifulsoup.
    soup = BeautifulSoup(content,'html.parser')
    
    #get the HTML of the table called site Table where all the links are displayed
    main_table = soup.find("div",attrs={'id':'panel-all-id'})
    
    #Now we go into main_table and get every a element in it which has a class "title" 
    links = main_table.find_all("li") #,class_="title")
    
    links_text = []
    
    for link in links:    
        links_text.append(link)
    
    # defining list variables to hold the field values
    
    product_ids = []
    product_name = []
    Average_rating = []
    Reviews = []
    product_price = []
    product_channel = []
    product_promotion = []
    product_href = []
    Product_image = []
    
    for i in range(len(links_text)):        
        
        text = links_text[i] 
        # converting into string for manipulation
        string = str(text)
             
        # Get product id and append it to product id list
        pr_id = substr(string," id=", "><a" )    
        print("product id is :" , pr_id)    
        product_ids.append(pr_id)
        
        # Get product name and append it to product name list
        try:
            productnm = text.find('span').text
            print("Product Name : ", productnm)
        except Exception as e:
            break; # break the loop if there is no product name
            productnm = ''
            
        product_name.append(productnm)
           
        # Get average rating for the product and append it to average rating list
        # Average rating:<span class="seo-avg-rating">4.5962
        avgrating = text.find('span', class_ ="seo-avg-rating").text
        print("Average Rating : ", avgrating)
        Average_rating.append(avgrating)
        
        # Get number of reviews and appends it to Reviews list
        num_rev = text.find('span', class_ ="seo-review-count").text
        print("Number of Reviews : ", num_rev)
        Reviews.append(num_rev)
        
        # Get price of the product using try and exception and append it to price list
        #<span aria-hidden="true" class="Price-characteristic">1,699</span>
        try:
            price = text.find('span', class_ ="Price-characteristic").text
            print("Price :", price)        
        except Exception as e:
            price = ''
            
        product_price.append(price)
        
        # Get product channel and append it to the product channel list
        #<span><div class="sc-channel-label">Online</div><div class="sc-channel-stock"><div class="sc-channel-stock-status sc-channel-stock-out-of-stock">Out of stock</div></div><div class="sc-shipping-availability-small" id="prod22550050-ship"></div></span>
        try:
            channel = text.find('', class_ ="sc-channel-label").text
            print("Channel : ", channel)
        except Exception as e:
            channel = ''
        product_channel.append(channel)
        
        # Get product promotional offers if exists (using try and exception) and append to promotions list
        # <div class="sc-promo-message-primary sc-promo-message-single">New Lower Price</div>
        try:
            promo = text.find('', class_ ="sc-promo-message-single").text
            print("Promo : ", promo)
        except Exception as e:
            promo = ''
        product_promotion.append(promo)
    
        # Get product image and append it to product image list
        #data-src="https://scene7.samsclub.com/is/image/samsclub/0019254542797_A?wid=280&amp;hei=280" src=""
        try:
            src = text.find(text = "src=" )#.text
            print("Source : ", src)
        except Exception as e:
            src = ''
        Product_image.append(src)
        
        # Get product href link and append it to product href link
        try:
            href = text.find('a').get("href")
            print("Href : ", href)
        except Exception as e:
            href = ''
        product_href.append(href)
        
    
    
        print("\n")
        # break the loop before i = 48, as there are only 48 elements in list
        if i == 47:
            break;
        
    
    # create a dictionary of all product variables
    product_dict = {
            'Product Id' : product_ids,
            'Product Name' : product_name,
            'Product Price' : product_price,
            'Average Rating' : Average_rating,
            'Number of Reviews' : Reviews,
            'Product Channel' : product_channel,
            'Product Promotions' : product_promotion,
            'product Href' : product_href,
            'Product Image' : Product_image
            }
    
    
    #print(product_dict)
    
    # convert dictionary to pandas data frame for easy processing
    Product_df = pd.DataFrame(product_dict)
    
    #print(Product_df)
    # read configuration file for fetching output directory to place the data
    config = get_config()
    dataoutdir = config.get('folders', 'dataoutdir') 
    # define output file
    #o_filename = r'C:\Users\nrrvlkp\Documents\M\540\540_Project\540_NRR_FinalProject\data\Product_'+symbol+'.csv'
    o_filename = dataoutdir+symbol+'.csv'
    
    # save data frame as csv
    Product_df.to_csv(o_filename, sep = ',')
    print("Exported list to csv")
    return True



def main():
    '''
    Main function to interpret command line request
    and peform search of the given symbol on samsclub website
    '''
    
    start_logger()
    logging.debug("Let us extract results from sams club web page for the given search symbol")
    
    # Get the configuraton settings to read URLs and symbols
    config = get_config()
    # if argument is passed search using that otherwise use default parameter in config file
    if len(sys.argv) > 1:
        symbol = sys.argv[1]
    else: 
        symbol = config.get('Symbols', 'symbol')
        print(symbol)     
    
        
    # read urls from either from config file
    url1 = config.get('URLS', 'url')    
    # 'https://www.samsclub.com/sams/search/searchResults.jsp?searchCategoryId=all&searchTerm='
    logging.info('INFO: Being web scrapping from website {}  for searching {} '.format(url1, symbol))
    #logging.info('INFO: Being web scrapping from website {}'.format(url1))
    
    # call the run function to extract the product information
    run(url1, symbol)

if __name__ == "__main__":
    main()
