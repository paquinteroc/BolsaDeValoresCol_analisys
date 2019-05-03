import pytrends
from pytrends.request import TrendReq

pytrend = TrendReq()


google_username = "paquinteroc@bt.unal.edu.co"
google_password = "jesusislord"

pytrend = TrendReq(google_username, google_password)


connector = pyGTrends(google_username, google_password)


pytrend.request_report(keys, date="today 90-d", geo="US")

print(" HOLA ")


pytrends = TrendReq(hl='en-US', tz=360)

pytrend = TrendReq()

pytrends = TrendReq(hl='en-US', tz=360, proxies = {'https': 'https://34.203.233.13:80'})

kw_list = ["Blockchain"]
pytrends.build_payload(kw_list, cat=0, timeframe='today 5-y', geo='', gprop='')



