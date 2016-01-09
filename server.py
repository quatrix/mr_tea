import tornado.ioloop
import tornado.web

MINUTE = 60

class MainHandler(tornado.web.RequestHandler):
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
        print(uid)

        if uid == 'rebrew':
            uid = self._last_brew

        if uid in self._res:
            self.__class__._last_brew = uid
            self.write(self._res[uid])
        else:
            self.write('unknown')


application = tornado.web.Application([
    (r"/tea", MainHandler),
])


if __name__ == "__main__":
    application.listen(8888)
    tornado.ioloop.IOLoop.current().start()
