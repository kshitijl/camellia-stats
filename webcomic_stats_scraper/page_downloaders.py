import logging, time

import requests

from page_utils import *

def download_with_user_agent(url):
    # We need to send a User-Agent or else Tapas returns a 403
    # Forbidden.
    headers = {
        'User-Agent': 'Mozilla/5.0 (Macintosh; \
        Intel Mac OS X 10_11_5) AppleWebKit/537.36 \
        (KHTML, lik} Gecko) Chrome/50.0.2661.102 Safari/537.36'}

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
        return sha256_hexencoded(self.url)

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
        
        from splinter import Browser

        with Browser('chrome', headless=True) as browser:
            browser.visit(self.webtoons_login_url)

            username_field = browser.find_by_id("emailId")[0]
            username_field.fill(self.username)

            password_field = browser.find_by_id("password")[0]
            password_field.fill(self.password)

            time.sleep(5)
            
            login_button = browser.find_by_id("btnLogIn")[0]
            login_button.click()

            logging.info({"message": "Finished attempting login"})                          

            browser.visit(self.url)

            logging.info({"message": "Visiting actual page of interest"})
            desired_content = browser.html

        return desired_content

    @property
    def name(self):
        return sha256_hexencoded(self.url + self.username)
    
