import scrapy
import re

class BooksSpider(scrapy.Spider):
    name = "books"
    allowed_domains = ["www.labirint.ru"]
    start_urls = ["https://www.labirint.ru/search/фантастика/?page=1"]

    def parse(self, response):
        books = response.xpath('//*[@id="rubric-tab"]/div[3]/section/div[@class="search-result"]/div')
        for book in books:
            title = book.xpath(".//a[@class='product-card__name']/@title").get()
            link = book.xpath(".//a[@class='product-card__name']/@href").get()
            if book.xpath(".//descendant::div[contains(@class, 'price-current')]"):
                price = re.sub("[^0-9]", "", book.xpath(".//descendant::div[contains(@class, 'price-current')]/text()").get())
            else:
                price = 'Нет в продаже'
            yield response.follow(url=link, callback=self.parse_books, meta={'title': title, 'price': price})
        
        next_url = response.xpath("//div[@class='pagination-next']/a/@href").get()
        if next_url:
            yield response.follow(url=next_url)  

    def parse_books(self, response):
        info = response.xpath("//*[@id='product-specs']/div[2]")
        for i in info:
            title = response.request.meta['title']
            price = response.request.meta['price']

            authors = i.xpath(".//div[@class='authors'][1]/a")
            authors_list = []
            for author in authors:
                authors_list.append(author.xpath(".//text()").get())

            publisher = i.xpath(".//div[@class='publisher']/a/text()").get()
            year =  re.sub("[^0-9]", "", i.xpath(".//div[@class='publisher']/text()[2]").get())
            yield {
                 'title': title,
                 'price': price,
                 'authors': ', '.join(authors_list),
                 'publisher': publisher,
                 'year': year
             }