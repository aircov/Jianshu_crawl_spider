# -*- coding: utf-8 -*-
import scrapy
from scrapy.linkextractors import LinkExtractor
from scrapy.spiders import CrawlSpider, Rule
from jianshu.items import JianshuItem


class JsSpider(CrawlSpider):
    name = 'js'
    allowed_domains = ['jianshu.com']
    start_urls = ['https://www.jianshu.com/']

    rules = (
        Rule(LinkExtractor(allow=r'.*/p/[0-9a-z]{12}.*'), callback='parse_item', follow=True),
    )

    def parse_item(self, response):
        title = response.xpath("//h1[@class='title']/text()").get()
        content = response.xpath("//div[@class='show-content-free']").get()
        author = response.xpath("//span[@class='name']/a/text()").get()
        avatar = response.xpath("//a[@class='avatar']/img/@src").get()
        pub_time = response.xpath("//span[@class='publish-time']/text()").get().replace("*", "")
        word_count = response.xpath("//span[@class='wordage']/text()").get()

        view_count = response.xpath("//span[@class='views-count']/text()").get()
        comment_count = response.xpath("//span[@class='comments-count']/text()").get()
        like_count = response.xpath("//span[@class='likes-count']/text()").get()

        # https://www.jianshu.com/p/8cac9e79ecd2?utm_campaign=maleskine&utm_content=note&utm_medium=seo_notes&utm_source=recommendation
        # https://www.jianshu.com/p/8cac9e79ecd2
        origin_url = response.url

        # ['https://www.jianshu.com/p/8cac9e79ecd2','utm_campaign=maleskine&utm_content=note&utm_medium=seo_notes&utm_source=recommendation']
        # ['https://www.jianshu.com/p/8cac9e79ecd2']
        url = origin_url.split("?")[0]
        article_id = url.split("/")[-1]

        # Example: '.'.join(['ab', 'pq', 'rs']) -> 'ab.pq.rs'
        subjects = ",".join(response.xpath("//div[@class='include-collection']/a/div/text()").getall())

        item = JianshuItem(
            title=title,
            content=content,
            author=author,
            avatar=avatar,
            pub_time=pub_time,
            word_count=word_count,
            view_count=view_count,
            comment_count=comment_count,
            like_count=like_count,
            origin_url=origin_url,
            article_id=article_id,
            subjects=subjects
        )

        yield item
