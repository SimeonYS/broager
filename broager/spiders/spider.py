import re
import scrapy
from scrapy.loader import ItemLoader
from ..items import BroagerItem
from itemloaders.processors import TakeFirst

pattern = r'(\xa0)?'

class BroagerSpider(scrapy.Spider):
	name = 'broager'
	start_urls = ['https://www.broagersparekasse.dk/nyheder-overblik']

	def parse(self, response):
		post_links = response.xpath('//a[@class="a-arrow-link a-arrow-link "]/@href').getall() + response.xpath('//div[@class="accordion__content rich-text"]//a/@href').getall()
		yield from response.follow_all(post_links, self.parse_post)

	def parse_post(self, response):
		date = response.xpath('//time/text()').get()
		title = response.xpath('//h2[@class="article-top-a__title"]/text()').get()
		content = response.xpath('//div[@class="frame__cell-item"]/p//text() | //div[@class="text-module-b__content"]//text() |//div[@class="rich-text"]/p//text() | (//div[@class="frame__cell-item"])[position() = 3]//text()').getall()
		content = [p.strip() for p in content if p.strip()]
		content = re.sub(pattern, "",' '.join(content))

		item = ItemLoader(item=BroagerItem(), response=response)
		item.default_output_processor = TakeFirst()

		item.add_value('title', title)
		item.add_value('link', response.url)
		item.add_value('content', content)
		item.add_value('date', date)

		yield item.load_item()
