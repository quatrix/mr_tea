import tornado.ioloop
import tornado.web
import sys

from elasticsearch import Elasticsearch
from datetime import datetime
from telepot import Bot

es = Elasticsearch()

MINUTE = 60

class MrTeaBot(object):
    def __init__(self, token, uid):
        self.bot = Bot(token)
        self.bot.notifyOnMessage(self.handle_message)

        self.uid = uid
        self.name = None
        self.waiting_for_rank = False

    def ask(self, name, rebrew):
        self.name = name
        self.rebrew = rebrew

        r = ' (rebrewed)' if rebrew else ''

        self.bot.sendMessage(
            self.uid,
            'please rate {}{}'.format(name, r)
        )

        self.waiting_for_rank = True

    def log_rank(self, rank):
        doc = {
            'name': self.name,
            'rebrew': self.rebrew,
            'rank': rank,
            '@timestamp': datetime.utcnow(),
        }

        es.index(index="mr_tea", doc_type='tea_rank', body=doc)

    def get_rank(self, msg):
        rank = int(msg['text'])

        if rank < 1 or rank > 5:
            raise ValueError('rank should be between 1 and 5')

        return rank

    def handle_message(self, msg):
        if not self.waiting_for_rank:
            self.bot.sendMessage(self.uid, 'not waiting for rank')
            return

        try:
            self.log_rank(self.get_rank(msg))
        except Exception as e:
            self.bot.sendMessage(self.uid, 'failed to log rank: {}'.format(e))
            return

        self.bot.sendMessage(
            self.uid,
            'your review of {} tea was logged'.format(self.name)
        )

        self.waiting_for_rank = False


class DoneBrewingHandler(tornado.web.RequestHandler):
    def initialize(self, bot):
        self.bot = bot

    def get(self):
        tornado.ioloop.IOLoop.current().call_later(
            1,
            self.bot.ask,
            self.get_argument('name'),
            bool(int(self.get_argument('rebrew'))),
        )

        self.write('ok') 


class UidToNameHandler(tornado.web.RequestHandler):
    _res = {
        '6d950b6c': 'Tie Guan Yin Imperial,95,{}'.format(6 * MINUTE),
        '1d990b6c': 'Mai Tips SFTGFOP,80,{}'.format(4 * MINUTE),
        'ad0c0b6c': 'Huang Hua Yun Jian,75,{}'.format(4 * MINUTE),
        '4dd20b6c': 'Mao Jian Lu Cha,75,{}'.format(4 * MINUTE),
        '1d470b6c': 'Shimcha Kurasawa 2015,70,{}'.format(2 * MINUTE),
        'cd9a0b6c': 'Dong Ding,95,{}'.format(6 * MINUTE),
        '2dbe0b6c': 'Bourgeus de Yuunan,90,{}'.format(4 * MINUTE),
        'bda10b6c': 'Dong Ding Antique,90,{}'.format(6 * MINUTE),
    }

    _last_brew = ""

    def get(self):
        uid = self.get_argument('uid')

        if uid == 'rebrew':
            uid = self._last_brew

        if uid in self._res:
            self.__class__._last_brew = uid
            self.write(self._res[uid])
        else:
            self.write('unknown')



if __name__ == "__main__":
    bot = MrTeaBot(token=sys.argv[1], uid=sys.argv[2])

    application = tornado.web.Application([
        (r"/uid_to_name", UidToNameHandler),
        (r"/done_brewing", DoneBrewingHandler, {'bot': bot}),
    ])

    application.listen(8888)
    tornado.ioloop.IOLoop.current().start()
