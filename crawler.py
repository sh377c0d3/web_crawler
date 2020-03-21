import os
import threading
import time
from queue import Queue
from urllib.parse import urlparse
from html.parser import HTMLParser
from urllib import parse
from urllib.request import urlopen

class LinkFinder(HTMLParser):

    def __init__(self, base_url, page_url):
        super().__init__()
        self.base_url = base_url
        self.page_url = page_url
        self.links = set()

    def handle_starttag(self, tag, attrs):
        if tag == 'a':
            for (attribute, value) in attrs:
                if attribute == 'href':
                    url = parse.urljoin(self.base_url, value)
                    self.links.add(url)

    def page_links(self):
        return self.links

    def error(self, message):
        pass

class Spider:

    project_name = ''
    base_url = ''
    domian_name = ''
    queue_file = ''
    crawled_file = ''
    queue =set()
    crawled = set()

    def __init__(self, project_name, base_url, domian_name):
        
        Spider.project_name = project_name
        Spider.base_url = base_url
        Spider.domain_name = domian_name
        Spider.queue_file = Spider.project_name + '/queue.txt'
        Spider.crawled_file = Spider.project_name + '/crawled.txt'
        self.boot()
        self.crawl_page(' First Spider ', Spider.base_url)

    @staticmethod
    def boot():
        create_project_dir(Spider.project_name)
        create_data_files(Spider.project_name, Spider.base_url)
        Spider.Queue = file_to_set(Spider.queue_file)
        Spider.crawled = file_to_set(Spider.crawled_file)

    @staticmethod
    def crawl_page(thread_name, page_url):
        if page_url not in Spider.crawled:
            print(thread_name + ' number thread is unused ' + page_url )
            print (t() + ' Queue : ' + str(len(Spider.queue)) + ' | Crawled : ' + str(len(Spider.crawled)))
            Spider.add_links_to_queue(Spider.gather_links(page_url))
            Spider.queue.remove(page_url)
            Spider.crawled.add(page_url)
            Spider.update_files()

    @staticmethod
    def gather_links(page_url):
        html_string = ''
        try:
            response = urlopen(page_url)
            if 'text/html' in response.getheader('Content-Type'):
                html_bytes = response.read()
                html_string = html_bytes.decode("utf-8")
            finder = LinkFinder(Spider.base_url, page_url)
            finder.feed(html_string)
        except Exception as e:
            print(str(e))
            return set()
        return finder.page_links()

    @staticmethod
    def add_links_to_queue(links):
        for url in links:
            if (url in Spider.queue) or (url in Spider.crawled):
                continue
            if Spider.domain_name != get_domain_name(url):
                continue
            Spider.queue.add(url)

    @staticmethod
    def update_files():
        set_to_file(Spider.queue, Spider.queue_file)
        set_to_file(Spider.crawled, Spider.crawled_file)

def get_domain_name(url):
    try:
        results = get_sub_domain_name(url).split('.')
        return results[-2] + '.' + results[-1]
    except:
        return ''

def get_sub_domain_name(url):
    try:
        return urlprase(url).netloc
    except:
        return ''

def create_project_dir(directory):
    if not os.path.exists(directory):
        print("Wait Directory is being created" + directory)
        os.makedirs(directory)

def create_data_files(project_name, base_url):
    queue = os.path.join(project_name,'queue.txt')
    crawled = os.path.join(project_name,'crawled.txt')
    if not os.path.isfile(queue):
        write_file(queue,base_url)
    if not os.path.isfile(crawled):
        write_file(crawled,'')

def write_file(path,data):
    with open(path,'w') as f:
        f.write(data)

def append_to_file(path,data):
    with open(path,'a') as file:
        file.write(data + '\n')

def delete_file_contents(path):
    open(path,'w').close()

def file_to_set(file_name):
    results = set()
    with open(file_name,'rt') as f:
        for line in f:
            results.add(line.replace('\n',''))
    return results

def set_to_file(links, file_name):
    with open(file_name,'w') as f:
        for l in sorted(links):
            f.write(l+"\n")
            
def t():
    current_time = time.localtime()
    ctime = time.strftime('%H:%M:%S', current_time)
    return '[' + ctime + ']'
        
def logo():
    os.system("clear")
    print( """
      ________       __            ______                     __            
     |  |  |  .-----|  |--.       |      .----.---.-.--.--.--|  .-----.----.
     |  |  |  |  -__|  _  |  ---  |   ---|   _|  _  |  |  |  |  |  -__|   _|
     |________|_____|_____|       |______|__| |___._|________|__|_____|__|  
                                                                    
    """)
    
if __name__ == '__main__':
    
    logo()
    PROJECT_NAME = str(input("Enter Name For Your Project : "))
    HOMEPAGE = str(input("Enter Url to Crawl : "))
    NUMBER_OF_THREADS = int(input("Enter the number of threads to use : "))
    DOMAIN_NAME = get_domain_name(HOMEPAGE)
    QUEUE_FILE = PROJECT_NAME + '/queue.txt'
    CRAWLED_FILE = PROJECT_NAME + '/crawled.txt'
    queue = Queue()
    Spider(PROJECT_NAME, HOMEPAGE, DOMAIN_NAME)

    def create_workers():
        for _ in range(NUMBER_OF_THREADS):
            t = threading.Thread(target=work)
            t.daemon = True
            t.start()

    def work():
        while True: 
            url = queue.get()
            Spider.crawl_page(threading.current_thread().name, url)
            queue.task_done()

    def create_jobs():
        for link in file_to_set(QUEUE_FILE):
            queue.put(link)
        queue.join()
        crawl()

    def crawl():
        queued_links = file_to_set(QUEUE_FILE)
        if len(queued_links) > 0:
            print(str(len(queued_links)) + 'links in the queue')
            create_jobs()

    create_workers()
    crawl()
