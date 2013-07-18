#!/usr/bin/env python

# Run this with
# PYTHONPATH=. DJANGO_SETTINGS_MODULE=testsite.settings testsite/tornado_main.py
# Serves by default at
# http://localhost:8080/hello-tornado and
# http://localhost:8080/hello-django

from tornado.options import options, define, parse_command_line
import django.core.handlers.wsgi
import tornado.httpserver
import tornado.ioloop
import tornado.web
import tornado.wsgi
import app

define('port', type=int, default=80)

class HelloHandler(tornado.web.RequestHandler):
    def get(self):
        self.write('Hello from tornado')

def main():
    wsgi_app = tornado.wsgi.WSGIContainer(
    django.core.handlers.wsgi.WSGIHandler())

    #tornado_app = tornado.web.Application(default_host='404cn\.org',
    #  handlers=[
    #    ('.*',app.towww),
    #    (r"/static/(.*)", tornado.web.StaticFileHandler, {"path": "./static"}),
    #    )])

    #tornado_app.add_handlers(r"wwww\.404cn\.org", [
    #('.*', tornado.web.FallbackHandler, dict(fallback=wsgi_app)),
    #])

    tornado_app = tornado.web.Application(default_host="oucena\.com",
      handlers=[
    	(r"/", app.weixin),
    	(r"/static/(.*)", tornado.web.StaticFileHandler, {"path": "./static"}),
    	    ])

    tornado_app.add_handlers(r'www\.404cn\.org', [
        ('.*', tornado.web.FallbackHandler, dict(fallback=wsgi_app)),
    ])

    tornado_app.add_handlers(r"www\.oucena\.com", [
    (r"/", app.weixin),
    (r"/static/(.*)", tornado.web.StaticFileHandler, {"path": "./static"}),
    ])

    tornado_app.add_handlers(r"www\.tufuli\.com", [
    (r"/root.txt", app.tufuli),
    (r"/", app.www),
    (r"/static/(.*)", tornado.web.StaticFileHandler, {"path": "./static"}),
    ])

    tornado_app.add_handlers(r"heregoo\.com", [
    (r"/root.txt", app.tufuli),
    (r"/top/([0-9]+)/", app.heregoo),
    (r"/static/(.*)", tornado.web.StaticFileHandler, {"path": "./static"}),
    ])

    server = tornado.httpserver.HTTPServer(tornado_app)
    server.listen(options.port)
    tornado.ioloop.IOLoop.instance().start()

if __name__ == '__main__':
    main()
