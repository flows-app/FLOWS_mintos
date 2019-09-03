from bs4 import BeautifulSoup
import urllib.request
import http.cookiejar
import json
import datetime
from urllib.request import Request, urlopen
import cfscrape

def handler(event, context):
    username = event['account']['username']
    password = event['account']['password']

    cj = http.cookiejar.CookieJar()
    opener = urllib.request.build_opener(
        urllib.request.HTTPCookieProcessor(cj),
        urllib.request.HTTPRedirectHandler(),
        urllib.request.HTTPHandler())
    opener.addheaders = [('User-agent', "Mozilla/5.0 (Windows NT 5.1) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/28.0.1500.72 Safari/537.36")]
    scraper = cfscrape.create_scraper()
    html = scraper.get("https://www.mintos.com/en/login").content
    soup = BeautifulSoup(html, 'html.parser')
    csrf=soup.find('login-form')['token']
    postdata = urllib.parse.urlencode({"_csrf_token":csrf,
                                       "_username":username,
                                       "_password":password}).encode("utf-8")

    html = scraper.post('https://www.mintos.com/en/login/check',
                data={"_csrf_token":csrf,
                        "_username":username,
                        "_password":password}).content

    html  = scraper.get('https://www.mintos.com/en/overview/').content
    print('overview')
    print(html)
    soup = BeautifulSoup(html, 'html.parser')
    balanceStr = soup.select("ul.m-overview-boxes div.value")[0]
    balance = balanceStr.string
    #clean up value
    balance = float(balance.strip()[2:].replace(" ", ""))
    
    availableStr = soup.select("ul.m-overview-boxes table.data tr td:nth-of-type(2)")[0]
    available = availableStr.string
    #clean up value
    available = float(available.strip()[2:].replace(" ", ""))
    
    investedStr = soup.select("ul.m-overview-boxes table.data tr:nth-of-type(2) td:nth-of-type(2)")[0]
    invested = investedStr.string
    #clean up value
    invested = float(invested.strip()[2:].replace(" ", ""))

    result = {"balance":balance,"available":available,"invested":invested}
    resultStr = json.dumps(result)
    customcontext = context.client_context.custom
    if "lastvalue" in customcontext and resultStr == customcontext['lastvalue']:
      return
    else:
      result['dedupid']=resultStr
      return result