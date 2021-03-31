import json
import re

import scrapy

from scrapy.loader import ItemLoader

from ..items import ValleyItem
from itemloaders.processors import TakeFirst
import requests

url = "https://www.valley.com/siteAPI/ArticleListing/GetArticles"

payload="{\"CategoryID\":39,\"Lat\":null,\"Lng\":null}"
headers = {
  'Connection': 'keep-alive',
  'Pragma': 'no-cache',
  'Cache-Control': 'no-cache',
  'sec-ch-ua': '"Google Chrome";v="89", "Chromium";v="89", ";Not A Brand";v="99"',
  'Accept': 'application/json, text/plain, */*',
  'sec-ch-ua-mobile': '?0',
  'User-Agent': 'Mozilla/5.0 (Windows NT 6.1; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/89.0.4389.90 Safari/537.36',
  'Content-Type': 'application/json;charset=UTF-8',
  'Origin': 'https://www.valley.com',
  'Sec-Fetch-Site': 'same-origin',
  'Sec-Fetch-Mode': 'cors',
  'Sec-Fetch-Dest': 'empty',
  'Referer': 'https://www.valley.com/why-valley/company-information/investor-relations-press-and-news/newsroom',
  'Accept-Language': 'en-US,en;q=0.9,bg;q=0.8',
  'Cookie': 'CMSPreferredCulture=en-US; CMSCsrfCookie=+quptQLuexbrMs0PQi4muG5i0utoP/accJ1L+ZqS; _gcl_au=1.1.1931494150.1617095845; nmstat=da02cf1d-b625-532c-49d1-147421b7cc22; _ga=GA1.2.1191882706.1617095847; _gid=GA1.2.785268680.1617095847; __ncuid=ffbea4ad-7b65-45fb-af28-d3624789c8b4; _hjTLDTest=1; _hjid=ac4d3cc6-f8ef-474c-a3b2-d1092094e62f; _fbp=fb.1.1617095848100.235864909; visitor_id519011=403135669; visitor_id519011-hash=4213e7d134d2016eac4cb5a711f6a13928d220229f46cba7c423a3e532332373b4f1608adc152111091683cebfb23fc813582871; ASP.NET_SessionId=tvsztblbmtpak2ywhiw5so2l; TS01104954=01b4209fcc60aaa52f00bfd21743d3c1bb01cf52258fe4843baa635b69d1a5d107695c61f399fb97c0bd29d235d789d804bfda93795ac2142645d06eaaa8dffff5985840f93b7faa8ee5325d7d0c44db29152d9cb2; _gat_UA-126475673-1=1; _hjIncludedInPageviewSample=1; _hjAbsoluteSessionInProgress=0; _hjIncludedInSessionSample=1; _gat_ncAudienceInsightsGa=1; BE_CLA3=p_id%3D68A462NJALR4RP84J46A8428RAAAAAAAAH%26bf%3Dfe77763951e079ad8f9a2779c36cf7fe%26bn%3D5%26bv%3D3.43%26s_expire%3D1617186840559%26s_id%3D68A462NJALR4RR86PRPA8428RAAAAAAAAH'
}


class ValleySpider(scrapy.Spider):
	name = 'valley'
	start_urls = ['https://www.valley.com/why-valley/company-information/investor-relations-press-and-news/newsroom']

	def parse(self, response):
		data = requests.request("POST", url, headers=headers, data=payload)
		data = data.text
		post_links = re.findall(r'LinkPath\\":\\"(.*?)\\",\\"ArticleCategoryName', data, re.DOTALL)
		yield from response.follow_all(post_links, self.parse_post)

	def parse_post(self, response):
		title = response.xpath('//h1/text()').get()
		description = response.xpath('//div[@class="main-content"]//p//text()[normalize-space()]|(//div[@class="columns medium-10 contentwrapper--section"])[2]//text()[normalize-space()]').getall()
		description = [p.strip() for p in description]
		description = ' '.join(description).strip()
		date = response.xpath('//div[@class="mb-20 mt-20"]/h5/text()').get()
		try:
			date = re.findall(r'\d{1,2}/\d{1,2}/\d{4}', date)[0]
		except:
			date = ''

		item = ItemLoader(item=ValleyItem(), response=response)
		item.default_output_processor = TakeFirst()
		item.add_value('title', title)
		item.add_value('description', description)
		item.add_value('date', date)

		return item.load_item()
