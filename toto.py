import scrapy
import json

class TotoScraper(scrapy.Spider):
    name = "toto"

    def start_requests(self):
        base_url = 'http://www.singaporepools.com.sg/en/product/sr/Pages/toto_results.aspx?'
        urls = self.generate_urls(base_url)
        for url in urls:
            yield scrapy.Request(url=url, callback=self.parse)
    
    def generate_urls(self, base_url):
        urls = []
        filename = 'querylinks.html'
        with open(filename, 'r') as f:
            lines = f.readlines()
            for line in lines:
                if line[5:11] == 'option':
                    urls.append(base_url + line[25: 50])
        return urls
    def parse(self, response):
        page = response.url.split('/')[-2]
        filename = 'toto-%s.txt' % page
        with open(filename, 'a') as f:
            crawler_data = {}
            for content_table in response.css('.divSingleDraw table'):
                if content_table.css('.drawDate::text').get() is not None:
                    crawler_data['Draw date'] = content_table.css('.drawDate::text').get()
                if content_table.css('.drawNumber::text').get() is not None:
                    crawler_data['Draw number'] = content_table.css('.drawNumber::text').get()
                if content_table.css('.win1::text').get() is not None:
                    crawler_data['Winning numbers'] = [
                        content_table.css('.win1::text').get(),
                        content_table.css('.win2::text').get(),
                        content_table.css('.win3::text').get(),
                        content_table.css('.win4::text').get(),
                        content_table.css('.win5::text').get(),
                        content_table.css('.win6::text').get()
                    ]
                if content_table.css('.additional::text').get() is not None:
                    crawler_data['Additional number'] = content_table.css('.additional::text').get()
            for winning_share in response.css('.divSingleDraw table.tableWinningShares tr'):
                prize_group = winning_share.css('td:first-child::text').get()
                if prize_group is not None: 
                    prize_group = prize_group.replace('\r\n', '').strip()
                share_amount = winning_share.css('td:nth-child(2)::text').get()
                if share_amount is not None:
                    share_amount = share_amount.replace('\r\n', '').strip()
                number_of_share = winning_share.css('td:last-child::text').get()
                if number_of_share is not None:
                    number_of_share = number_of_share.replace('\r\n', '').strip()
                if prize_group != '' and prize_group is not None and prize_group != 'Prize Group':
                    crawler_data[prize_group + ' prize'] = {
                        'Price group': prize_group,
                        'Share amount': share_amount,
                        'Number of shares': number_of_share
                    }
            f.write(json.dumps(crawler_data))
            f.write('\n')
            f.close()
        self.log('saved file %s' % filename)