import logging, time

import requests

from page_utils import *

def download_with_user_agent(url):
    # We need to send a User-Agent or else Tapas returns a 403
    # Forbidden.
    headers = { 'User-Agent': 'wget/1.19.2' }

    # n.b. [.text] returns the decoded [.content], based on its best
    # guess for the encoding.
    return requests.get(url,headers=headers).text

class PlainUrlPage(object):
    def __init__(self, url):
        self.url = url

    def download(self):
        logging.info({"message"    : "downloading",
                      "type"       : "PlainUrlPage",
                      "needs_login": False,
                      "url"        : self.url})
        return download_with_user_agent(self.url)

    @property
    def name(self):
        return sha256_hexencoded(self.url.encode('utf-8'))

class WebtoonsLoggedInPage(object):
    webtoons_login_url = 'http://m.webtoons.com/member/login/doLoginById'
    
    def __init__(self, url, username, password):
        self.url, self.username, self.password = url, username, password

    def download(self):
        logging.info({"message"    : "downloading",
                      "type"       : "WebtoonsLoggedInPage",
                      "needs_login": True,
                      "login_url"  : self.webtoons_login_url,
                      "username"   : self.username,
                      "url"        : self.url})
        
        from selenium import webdriver

        browser = webdriver.Firefox()
        browser.get(self.webtoons_login_url)

        username_field = browser.find_element_by_id("emailId")
        username_field.send_keys(self.username)

        password_field = browser.find_element_by_id("password")
        password_field.send_keys(self.password)

        time.sleep(5)

        login_button = browser.find_element_by_id("btnLogIn")
        login_button.click()

        logging.info({"message": "Finished attempting login"})                          

        browser.get(self.url)

        logging.info({"message": "Visiting actual page of interest"})
        desired_content = browser.page_source

        browser.close()

        return desired_content

    @property
    def name(self):
        return sha256_hexencoded((self.url + self.username).encode('utf-8'))

