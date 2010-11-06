from google.appengine.ext import webapp
from google.appengine.ext.webapp.util import run_wsgi_app
import os

class MainPage(webapp.RequestHandler):
    def get(self):
        self.response.headers['Content-Type'] = 'text/html'
        FH = open('static/index.html')
        lines = FH.readlines()
        FH.close()
        for line in lines:
            self.response.out.write(line)

application = webapp.WSGIApplication(
                                     [('/', MainPage)],
                                     debug=True)

def main():
    run_wsgi_app(application)

if __name__ == "__main__":
    main()
