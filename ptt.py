import re
import json

import requests
from pyquery import PyQuery as pq


def init_session():
    s = requests.Session()
    s.post(
        "{}{}".format('https://www.ptt.cc', "/ask/over18?from=%2Fbbs%2FGossiping%2Findex.html"),
        verify=False,
        data={"from": 'https://www.ptt.cc', "yes": "yes"}
    )
    return s


class PttPage:
    site_url = 'https://www.ptt.cc'
    url = None
    html = None
    is_last = None

    def __init__(self, boardname, number=None, session: requests.Session =None, lazy=False):
        self.number = number
        self.boardname = boardname
        self.session = session
        if session is None:
            self.session = requests.Session()
            self.session.post(
                "{}{}".format(self.site_url, "/ask/over18?from=%2Fbbs%2FGossiping%2Findex.html"),
                verify=False,
                data={"from": self.site_url, "yes": "yes"}
            )

        if not lazy:
            self.get(self.number)

    @classmethod
    def get_page(cls, boardname=None, number=None):
        if not boardname:
            raise Exception

        page = cls(boardname)
        page.get(number)
        return page


    def get(self, number=None):
        partial_url = '{}/bbs/{}'.format(self.site_url, self.boardname)
        if number is None:
            if self.number is None:
                url = "{}/index.html".format(partial_url)
            else:
                url = '{}/index{}.html'.format(partial_url, self.number)
        else:
            self.number = number
            url = '{}/index{}.html'.format(partial_url, number)

        resp = self.session.get(url, verify=False)
        if resp.ok:
            self.html = resp.text
            self.url = url

            root = pq(self.html)
            page_bar = root('.btn-group.btn-group-paging a')

            self.is_last = True if page_bar[2].get("href") is None else False
            if number is None and self.number is None:
                page_url_before = page_bar[1].get("href")
                self.number = int(re.search(r"\d+", page_url_before).group(0)) + 1

            return self

    @property
    def info(self):
        if self.html is None:
            self.get()
        if self.number is None:
            root = pq(self.html)
            page_bar = root('.btn-group.btn-group-paging a')
            page_url_before = page_bar[1].get("href")
            self.number = int(re.search(r"\d+", page_url_before).group(0)) + 1

        return {
            "board": self.boardname,
            "page_number": self.number,
            "url": self.url,
            "is_last": self.is_last,
            "posts": self.posts
        }

    @property
    def posts(self):
        if self.html is None:
            raise Exception

        posts_elements = pq(self.html)('.r-ent')
        return [self._parse_posts(ele) for ele in posts_elements]

    def _parse_posts(self, post):
        d = pq(post)
        url = d('.title a').attr('href')
        timestamp = url.split('.')[1]
        id = url.split('/')[-1][:-5]

        return {
            "url": d('.title a').attr('href'),
            "post_id": id,
            "timestamp": timestamp,
            "title": d('.title').text(),
            "nrec": d('.nrec span').text(),
            "author": d('.author').text(),
            "mark": d('.mark').text()
        }


class PttPost:
    site_url = 'https://www.ptt.cc'
    html = None
    root = None
    is_404 = None

    def __init__(self, url, session=None, lazy=False):
        self.url = url
        if "https://" not in self.url:
            self.url = self.site_url + self.url

        self.id = url.split('/')[-1][:-5]
        self.timestamp = self.id.split(".")[1]
        self.session = session
        if self.session is None:
            self.session = init_session()

        if not lazy:
            self.get()


    def get(self):
        try:
            resp = self.session.get(self.url, verify=False)
        except Exception as e:
            raise e

        self.html = resp.text
        self.root = pq(self.html)

        if self.root("#main-content > .article-metaline") is None:
            self.is_404 = True

        return self


    @property
    def user_ip(self):
        """Get user's last IP address"""

        text_list = self.root('.f2').map(lambda i, e: e.text)[::-1]
        for text in text_list:
            ip_match = re.search(r"\b\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3}\b", text)
            if ip_match:
                return ip_match.group(0)

    @property
    def snapshot(self):
        return self.root("#main-content").html()

    @property
    def content(self):
        return self.root("#main-content")[0].xpath("./text()")[0].strip()
    
    @property
    def title(self):
        return self.root("#main-content > .article-metaline span")[3].text

    @property
    def author(self):
        s = self.root("#main-content > .article-metaline span")[1].text
        author = s.split('(')[0].strip()
        return author

    @property
    def board(self):
        return self.root('#main-content > .article-metaline-right span')[1].text



    @property
    def pushs(self):
        return [self._get_push(push) for push in self.root('.push')]

    @staticmethod
    def _get_push(push):
        push = pq(push)
        return {
            "push_tag": push('.push-tag').text(),
            "push_userid": push('.push-userid').text().strip(),
            "push_content": push('.push-content').text()[2:],
            "push_ipdatetime": push('.push-ipdatetime').text().strip()
        }

    def calculate_messages(self):
        push = 0
        neutral = 0
        boo = 0
        msg_type = {
            "push": "推",
            "neutral": '→',
            "boo": "噓"
        }
        for msg in self.pushs:
            if msg['push_tag'] == "推":
                push += 1
            elif msg['push_tag'] == '→':
                neutral += 1
            elif msg['push_tag'] == "噓":
                boo += 1

        return {
            "all": push + neutral + boo,
            "boo": boo,
            "count": push - boo,
            "neutral": neutral,
            "push": push,
        }

    def to_dict(self):
        if self.is_404 is True:
            return {
                "article_id": self.id,
                "article_title": "",
                "author": "",
                "board": "",
                "content": "",
                "timestamp": self.timestamp,
                "ip": "",
                "message_count": "",
                "messages": "",
                "url": self.url,
                "is_404": True
            }
        return {
            # "post_snapshot": self.snapshot,
            "article_id": self.id,
            "article_title": self.title,
            "author": self.author,
            "board": self.board,
            "content": self.content,
            "timestamp": self.timestamp,
            "ip": self.user_ip,
            "message_count": self.calculate_messages(),
            "messages": self.pushs,
            "url": self.url,
        }

    def to_json(self):
        return json.dumps(self.to_dict(), ensure_ascii=False)


def get_posts(boardname, number=None, session=None):
    if not session:
        session = init_session()
    p = PttPage(boardname, number=number, session=session)
    posts = [ PttPost(p['url'], session) for p in p.posts ]
    return [ p.to_dict() for p in posts]
