from bs4 import BeautifulSoup
import urllib.request
import http.cookiejar
import json
import datetime
from urllib.request import Request, urlopen

def handler(event, context):
    username = event['account']['username']
    password = event['account']['password']

    cj = http.cookiejar.CookieJar()
    opener = urllib.request.build_opener(
        urllib.request.HTTPCookieProcessor(cj),
        urllib.request.HTTPRedirectHandler(),
        urllib.request.HTTPHandler())
    opener.addheaders = [('User-agent', "Mozilla/5.0 (Windows NT 5.1) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/28.0.1500.72 Safari/537.36")]

    req = Request('https://www.mintos.com/en/login', headers={'User-Agent': "Mozilla/5.0 (Windows NT 5.1) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/28.0.1500.72 Safari/537.36"})
    html = opener.open(req).read()
    soup = BeautifulSoup(html, 'html.parser')
    csrf=soup.find('login-form')['token']
    postdata = urllib.parse.urlencode({"_csrf_token":csrf,
                                       "_username":username,
                                       "_password":password}).encode("utf-8")

    req = Request('https://www.mintos.com/en/login/check',
                data=postdata,
                method='POST')

    response = opener.open(req)
    html = response.read()

    req = Request('https://www.mintos.com/en/overview/',
      headers={'origin': 'https://www.mintos.com',
              'authority': 'www.mintos.com',
              'User-Agent': "Mozilla/5.0 (Windows NT 5.1) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/28.0.1500.72 Safari/537.36",
              'x-requested-with': 'XMLHttpRequest',
              'content-type': 'application/x-www-form-urlencoded; charset=UTF-8',
              'referer': 'https://www.mintos.com/en/overview/'
              },
      method='GET')

    html = opener.open(req).read()
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
