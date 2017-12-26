#!/usr/bin/env python

#//*[@id="emailId"]
#//*[@id="password"]


import requests
from lxml import html

USERNAME = "julie.y.chien@gmail.com"
PASSWORD = "<PASSWORD>"

LOGIN_URL = "http://www.webtoons.com/member/login/doLoginById#"
URL = "http://www.webtoons.com/challenge/titleStat?titleNo=81223"

def main():
    session_requests = requests.session()

    # Get login csrf token
    result = session_requests.get(LOGIN_URL)
    tree = html.fromstring(result.text)
    # authenticity_token = list(set(tree.xpath("//input[@name='csrfmiddlewaretoken']/@value")))[0]

    # Create payload
    payload = {
        "emailId": USERNAME, 
        "password": PASSWORD, 
    }

    # Perform login
    result = session_requests.post(LOGIN_URL, data = payload, headers = dict(referer = LOGIN_URL))

    # Scrape url
    result = session_requests.get(URL, headers = dict(referer = URL))
    #tree = html.fromstring(result.content)
    #bucket_names = tree.xpath("//div[@class='repo-list--repo']/a/text()")

    print(result.content)

if __name__ == '__main__':
    main()
