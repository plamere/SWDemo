import os 
import sys
import cherrypy
import ConfigParser
import urllib2
import webtools


cache = {}


class Server(object):
    def __init__(self, config):
        self.production_mode = config.getboolean('settings', 'production')


    def call(self, q='',  callback='', _=''):
        if callback:
            cherrypy.response.headers['Content-Type']= 'text/javascript'
        else:
            cherrypy.response.headers['Content-Type']= 'application/json'

        results = fetch_url(q)
        results = callback + "(" + results + ")"
        return results
    call.exposed = True


def fetch_url(url):

    if url in cache:
        print 'cache hit for', url
        js = cache[url]
    else:
        req = urllib2.Request(url)
        req.add_header('Accept', 'application/json');
        f = urllib2.urlopen(req)
        js = f.read()
        print url, js
        f.close()
        cache[url] = js
    return js

if __name__ == '__main__':
    urllib2.install_opener(urllib2.build_opener())
    conf_path = os.path.abspath('web.conf')
    print 'reading config from', conf_path
    cherrypy.config.update(conf_path)

    config = ConfigParser.ConfigParser()
    config.read(conf_path)
    production_mode = config.getboolean('settings', 'production')

    current_dir = os.path.dirname(os.path.abspath(__file__))
    # Set up site-wide config first so we get a log if errors occur.

    if production_mode:
        print "Starting in production mode"
        cherrypy.config.update({'environment': 'production',
                                'log.error_file': 'simdemo.log',
                                'log.screen': True})
    else:
        print "Starting in development mode"
        cherrypy.config.update({'noenvironment': 'production',
                                'log.error_file': 'site.log',
                                'log.screen': True})

    conf = webtools.get_export_map_for_directory("static")
    cherrypy.quickstart(Server(config), '/SWServer', config=conf)

