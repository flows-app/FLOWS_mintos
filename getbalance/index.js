const { parse } = require('node-html-parser');

exports.handler = async (event, context,callback) => {
  let CLOUDSCRAPER = require('cloudscraper');

  //remove credentials from event structure
  let username = event.account.username;
  let password = event.account.password;
  event.account.username='***';
  event.account.password='***';

  console.log("event");
  console.log(JSON.stringify(event,null,2));

  let html = await CLOUDSCRAPER.get("https://www.mintos.com/en/login");
  let doc = parse(html);
  let el = doc.querySelector('login-form');
  if(!el ){
    console.log('error happened');
    console.log(html);
    throw new Error("no login");
  }
  let csrf = el.attributes.token;
  let options = {
    uri: 'https://www.mintos.com/en/login/check',
    formData: {"_csrf_token":csrf,
    "_username":username,
    "_password":password}
  };

  html = await CLOUDSCRAPER.post(options);

  html  = await CLOUDSCRAPER.get('https://www.mintos.com/en/overview/');
  doc = parse(html);
  el = doc.querySelector('ul.m-overview-boxes div.value');
  let str = el.text;
  let balance = Number(str.trim().substring(2).replace(/ /g,''));

  el = doc.querySelectorAll('ul.m-overview-boxes table.data tr td')[1];
  str = el.text;
  let available = Number(str.trim().substring(2).replace(/ /g,''));

  el = doc.querySelectorAll('ul.m-overview-boxes table.data tr')[1].querySelectorAll('td')[1];
  str = el.text;
  let invested = Number(str.trim().substring(2).replace(/ /g,''));

  let result = {"balance":balance,"available":available,"invested":invested};

  return result;
}