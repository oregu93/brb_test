#!/usr/bin/env python
# coding: utf-8

# importing libs

from bs4 import BeautifulSoup
import requests
import re
from re import sub
from decimal import Decimal
import io
from datetime import datetime
import pandas as pd

from selenium import webdriver
from time import sleep
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as EC

from boto.s3.connection import S3Connection         # to get vars from heroku
TOKEN = S3Connection(os.environ['TOKEN'])   # telegram bot token
url_0 = S3Connection(os.environ['URL_0'])   # primary url for scrap


# general bot procedure's code

def bot(vendor_code):
    search = vendor_code
    # search = str(input('--> '))
    # url_0 = 'https://www.intimissimi.com'
    url_0 = str(url_0)                             # convert var into string
    url_search = url_0+'/ru/search/?q='+search
    # print(url_search)
    
    html_text_0 = requests.get(url_search).text
    soup_0 = BeautifulSoup(html_text_0, 'lxml') # search page
    
    
    links_0=[]
    links_0 = soup_0.find_all('a', class_ = 'product-tile js-pdp-link no-hover')
    colors=[]
    for link in links_0:            # проход по ссылкам и сборка всех цветов
        link=link.get('href')
        
        url = url_0 + link
        html_text = requests.get(url).text
        soup = BeautifulSoup(html_text, 'lxml')
        
        color = ' '.join(map(str,[soup.find('span', class_ = 'family-color text-capitalized').text.strip(), soup.find('span', class_ = 'attribute-label text-capitalized').text.strip()]))
        colors.append(color)
    colors = ', '.join(map(str,colors))
    
    
    # colors_0 = soup_0.find_all('div', class_='product')
    # colors=[]
    # for c in colors_0:
    #     c=c.get('data-pid')
    #     colors.append(c)
    # colors = [colors[i].strip() for i in range(len(colors))]
    # colors = ' '.join(map(str,colors))
    
    
    url = url_0 + links_0[0].get('href')
    name = soup.find('h1', class_ = 'h3').text
    size = soup.find_all('div', class_ = 'radio-label')
    color = ' '.join(map(str,[soup.find('span', class_ = 'family-color text-capitalized').text.strip(), soup.find('span', class_ = 'attribute-label text-capitalized').text.strip()]))
    
    discription = soup.find('div', class_ = 'accordion-content').text
    
    sizes = [size[i].text.strip() for i in range(len(size))]
    sizes = ' '.join(map(str,sizes))
    
    
    ##!!! нажатие кнопки размеров и получение инфы о составе (materials)
    # path="C:\\Users\\user\\Documents\\GitHub\\BRB\\env\\bin\\chromedriver.exe"
    #
    # m_dat=''
    # class TestFunc(object):
    #     def __init__(self):
    #         self.driver = webdriver.Chrome(path)
    #         self.driver.get(url)
    #
    #     def but_clck(self):
    # #         sleep(5)
    #         mrk="//label/input[@type='radio']"
    #         button = self.driver.find_element_by_xpath(mrk)
    # #         button.click()
    # #         button = self.driver.find_element_by_xpath("label[@class='boolean-field_swatch-boolean_dark']")
    #         self.driver.execute_script("arguments[0].click();",button)
    #         webdriver.ActionChains(self.driver).move_to_element(button).click(button).perform()
    #         mt="//div[@class='js-composition-info']"
    #         mat_data = self.driver.find_element_by_xpath(mt)
    #         global m_dat
    #         m_dat = mat_data
    #
    #         self.driver.close()
    #         self.driver.quit()
    #
    # TestFunc().but_clck()

    # html_text_M = requests.get(url).text
    # soup_M = BeautifulSoup(html_text_M, 'lxml')
    # material_url = soup_M.find('div', class_='js-composition-info')
    # material_url = soup_M.driver.find_element_by_xpath("//div[@class_='js-composition-info']")
    
    
    res = {'name':name.strip(),'size':sizes,'color':colors,'material':'m_dat','discription':discription.strip()}

    s = f"""
{'-'*5}
# Code: {vendor_code.upper()}
# Name: {res['name']}
# Size: {res['size']}
# Color: {res['color']}
# Material: {res['material']}
# Discription: {res['discription']}
{'-'*5}
    """
        
    return s


# telegram bot code

import logging
from telegram import Update, ForceReply
from telegram.ext import Updater, CommandHandler, MessageHandler, Filters, CallbackContext

# TOKEN = System.getenv['TOKEN']

# Enable logging
logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s', level=logging.INFO
)

logger = logging.getLogger(__name__)


# Define a few command handlers. These usually take the two arguments update and context
def start(update: Update, context: CallbackContext) -> None:
    """Send a message when the command /start is issued."""
    user = update.effective_user
    update.message.reply_markdown_v2(
        fr'Welcome on board, {user.mention_markdown_v2()}\!',
        reply_markup=ForceReply(selective=True),
    )


def help_command(update: Update, context: CallbackContext) -> None:
    """Send a message when the command /help is issued."""
    update.message.reply_text('Help!')


def echo(update: Update, context: CallbackContext) -> None:
    """Echo the user message."""
    vendor_code = update.message.text
    try:
        answer = bot(vendor_code)
    except:
        answer = 'Извините, что-то сломалось :('
      
    update.message.reply_text(answer)



def main() -> None:
    """Start the bot."""
    # Create the Updater and pass it your bot's token.
    updater = Updater(TOKEN, use_context=True)

    # Get the dispatcher to register handlers
    dispatcher = updater.dispatcher

    # on different commands - answer in Telegram
    dispatcher.add_handler(CommandHandler("start", start))
    dispatcher.add_handler(CommandHandler("help", help_command))

    # on non command i.e message - echo the message on Telegram
    dispatcher.add_handler(MessageHandler(Filters.text & ~Filters.command, echo))

    # Start the Bot
    updater.start_polling()

    # Run the bot until you press Ctrl-C or the process receives SIGINT,
    # SIGTERM or SIGABRT. This should be used most of the time, since
    # start_polling() is non-blocking and will stop the bot gracefully.
    updater.idle()


if __name__ == '__main__':
    main()

