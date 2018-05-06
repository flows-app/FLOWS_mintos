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

    req = Request('https://www.mintos.com/en/', headers={'User-Agent': "Mozilla/5.0 (Windows NT 5.1) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/28.0.1500.72 Safari/537.36"})
    html = opener.open(req).read()
    soup = BeautifulSoup(html, 'html.parser')
    csrf=soup.form.input['value']
    postdata = urllib.parse.urlencode({"_csrf_token":csrf,
                                       "_username":username,
                                       "_password":password}).encode("utf-8")

    req = Request('https://www.mintos.com/en/login/check',
                data=postdata,
                method='POST')

    response = opener.open(req)
    html = response.read()
    today = datetime.date.today()
    yesterday = datetime.date.today() - datetime.timedelta(1)
    todaystr = today.strftime("%d.%m.%Y")
    yesterdaystr = yesterday.strftime("%d.%m.%Y")
    print('getting data from '+yesterdaystr+' to '+todaystr)
    postdata2 = urllib.parse.urlencode({'max_results':100}).encode("utf-8")

    req = Request('https://www.mintos.com/en/my-investments/list',
      data=postdata2,
      headers={'origin': 'https://www.mintos.com',
              'authority': 'www.mintos.com',
              'User-Agent': "Mozilla/5.0 (Windows NT 5.1) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/28.0.1500.72 Safari/537.36",
              'x-requested-with': 'XMLHttpRequest',
              'content-type': 'application/x-www-form-urlencoded; charset=UTF-8',
              'referer': 'https://www.mintos.com/en/account-statement/'
              },
      method='POST')

    response = opener.open(req)
    jsondata = response.read()
    tmp = json.loads(jsondata)
    result = []
    for investment in tmp['data']['result']['investments']:
        del investment['button']
        result.append(investment)

    totalCount=tmp['data']['result']['total']
    print("total count "+str(totalCount))
    idx=1
    while totalCount > len(result):
        #crawl next page
        idx += 1
        print("running page "+str(idx))
        postdata2 = urllib.parse.urlencode({'max_results':100,
                            'page':idx}).encode("utf-8")

        req = Request('https://www.mintos.com/en/my-investments/list',
          data=postdata2,
          headers={'origin': 'https://www.mintos.com',
                  'authority': 'www.mintos.com',
                  'User-Agent': "Mozilla/5.0 (Windows NT 5.1) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/28.0.1500.72 Safari/537.36",
                  'x-requested-with': 'XMLHttpRequest',
                  'content-type': 'application/x-www-form-urlencoded; charset=UTF-8',
                  'referer': 'https://www.mintos.com/en/account-statement/'
                  },
          method='POST')

        response = opener.open(req)
        jsondata = response.read()
        tmp = json.loads(jsondata)
        for investment in tmp['data']['result']['investments']:
            del investment['button']
            result.append(investment)

    print(json.dumps(result))
    return result
