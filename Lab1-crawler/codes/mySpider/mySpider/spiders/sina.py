import scrapy
from mySpider.items import SinaItem


class SinaSpider(scrapy.Spider):
    name = "sina"
    allowed_domains = ["finance.sina.com.cn"]
    start_urls = [
        "http://vip.stock.finance.sina.com.cn/corp/view/vCB_BulletinGather.php?stock_str=sh600168&page_index=1"
    ]

    url = "http://vip.stock.finance.sina.com.cn/corp/view/vCB_BulletinGather.php?stock_str=sh600168&page_index=%d"
    index = 1

    # 回调函数接受item
    def parse_detail(self, response):
        item = response.meta['item']
        detail_page = response.xpath('//*[@id="content"]//text()').extract()
        detail_page = ''.join(detail_page)
        item['detail_page'] = detail_page

        # print(detail_page)

        yield item

    # 解析首页中的标题名称
    def parse(self, response):
        tbody_list = response.xpath('/html/body/div/div[5]/table/tbody')

        for tbody in tbody_list:
            tr_list = tbody.xpath('./tr')
            for tr in tr_list:
                item = SinaItem()
                title = tr.xpath('./th/a/text()').extract_first()
                item['title'] = title
                # print(title)
                date = tr.xpath('./td[2]/text()').extract_first()
                item['date'] = date
                # print(date)
                type = tr.xpath('./td[1]/text()').extract_first()
                item['type'] = type
                # print(type)
                detail_url = "http://vip.stock.finance.sina.com.cn" + tr.xpath(
                    './th/a/@href').extract_first()  # 链接里的内容
                # print(detail_url)
                yield scrapy.Request(detail_url,
                                     callback=self.parse_detail,
                                     dont_filter=True,
                                     meta={'item': item})

                # 分页操作
                if self.index <= 5:
                    new_url = format(self.url % self.index)
                    self.index += 1

                    yield scrapy.Request(new_url,
                                         callback=self.parse,
                                         dont_filter=True)
