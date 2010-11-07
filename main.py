from google.appengine.ext import webapp
from google.appengine.ext.webapp.util import run_wsgi_app
from google.appengine.api import users
from google.appengine.ext import db
from django.utils import simplejson
import datetime
import time

class QuoteObject(db.Model):
    quote_text = db.StringProperty(multiline=True)
    quote_text_alt = db.StringProperty(multiline=True)
    person_name = db.StringProperty()
    date = db.DateProperty()
    location = db.GeoPtProperty()
    person_age = db.IntegerProperty()
    photo_url = db.LinkProperty()


class MainPage(webapp.RequestHandler):
    def get(self):
        self.response.headers['Content-Type'] = 'text/html'
        FH = open('static/index.html')
        lines = FH.readlines()
        FH.close()
        for line in lines:
            self.response.out.write(line)

class ViewData(webapp.RequestHandler):
    def get(self):
        self.response.headers['Content-Type'] = 'text/html'
        query = QuoteObject.all()
        results = query.fetch(limit=200)
        for result in results:
	        self.response.out.write("<div><img src='img?img_id=%s'></img>" % result.key())
	        
class AddData(webapp.RequestHandler):
    def post(self):
        quote = QuoteObject()
        quote.quote_text = self.request.get('quote_text')
        quote.quote_text_alt = self.request.get('quote_text_alt')
        quote.person_name = self.request.get('person_name')
        quote.date = datetime.date.today()
        lat = self.request.get('location_lat')
        longi = self.request.get('location_long')
        quote.location = db.GeoPt(float(lat), float(longi))
        quote.person_age = int(self.request.get('person_age'))
        quote.photo_url = self.request.get('photo_url')
        quote.put()
        self.redirect('/data_form')

class DataForm(webapp.RequestHandler):
    def get(self):
        self.response.out.write("""
<html><head><title>Add Data Here</title></head><body>
<form action="/add_data" method="post">
<div><p>What are you thinking about right now<textarea name="quote_text" rows="3" cols="60"></textarea></p></div>
<div><p>What do you need<textarea name="quote_text_alt" rows="3" cols="60"></textarea></p></div>
<div><p>Name of Quotee<input type="text" name="person_name"></input></p></div>
<div><p>Latitude<input type="text" name="location_lat"></input></p></div>
<div><p>Longitude<input type="text" name="location_long"></input></p></div>
<div><p>Age<input type="text" name="person_age"></input></p></div>
<div><p>Photo URL<input type="text" name="photo_url"></input></p></div>
<div><input type="submit" value="Add Quote"></div>
</form>
</body>
</html>""")

class Image (webapp.RequestHandler):
    def get(self):
      greeting = db.get(self.request.get("img_id"))
      if greeting.photo:
          self.response.headers['Content-Type'] = "image/png"
          self.response.out.write(greeting.photo)
      else:
          self.error(404)

class JSON (webapp.RequestHandler):
    def get(self):
        self.response.headers['Content-Type'] = 'text/plain'
        query = QuoteObject.all()
        results = query.fetch(limit=200)
        json_out = []
        for result in results:
            json_out.append(self.to_dict(result))
        self.response.out.write('[')
        for out in json_out[:-1]:
            self.response.out.write('{\n')
            self.response.out.write('\tid: ')
            for key in out.keys():
                if isinstance(out[key], basestring):
                    out[key] = '"%s"' % out[key]
                self.response.out.write('\t%s: %s,\n' % (key, out[key]))
            self.response.out.write('},\n')
        self.response.out.write('{\n')
        out = json_out[-1]
        for key in out.keys():
            if isinstance(out[key], basestring):
                out[key] = '"%s"' % out[key]
            self.response.out.write('\t%s: %s,\n' % (key, out[key]))
        self.response.out.write('},]\n')
    def get2(self):
        self.response.headers['Content-Type'] = 'text/plain'
        query = QuoteObject.all()
        results = query.fetch(limit=200)
        json_out = []
        for result in results:
            json_out.append(self.to_dict(result))
        self.response.out.write('[')
        for out in json_out:
            self.response.out.write('{\n')
            for key in out.keys():
                if isinstance(out[key], basestring):
                    out[key] = '"%s"' % out[key]
                self.response.out.write('\t%s: %s,\n' % (key, out[key]))
            self.response.out.write('},\n')
        self.response.out.write(']')
    def to_dict(self, model):
        output = {}
        SIMPLE_TYPES = (int, long, float, bool, dict, basestring, list)
        for key, prop in model.properties().iteritems():
            value = getattr(model, key)
            if value is None or isinstance(value, SIMPLE_TYPES):
                output[key] = value
            elif isinstance(value, datetime.date):
                ms = time.mktime(value.timetuple()) * 1000
                ms += getattr(value, 'microseconds', 0) / 1000
                output[key] = int(ms)
            elif isinstance(value, db.Model):
                output[key] = to_dict(value)
            elif isinstance(value, db.GeoPt):
                output['lat'] = float(str(value).split(',')[0])
                output['long'] = float(str(value).split(',')[1])
            else:
                raise ValueError('cannot encode ' + repr(prop))
        return output
    def post(self):
        pass

application = webapp.WSGIApplication(
                                     [('/view_data', ViewData),
                                     ('/add_data', AddData),
                                     ('/data_form', DataForm),
                                     ('/img', Image),
                                     ('/quotes', JSON),
                                     ('/', MainPage)])

def main():
    run_wsgi_app(application)

if __name__ == "__main__":
    main()
