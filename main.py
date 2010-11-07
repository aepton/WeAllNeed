from google.appengine.ext import webapp
from google.appengine.ext.webapp.util import run_wsgi_app
from google.appengine.api import users
from google.appengine.ext import db
from django.utils import simplejson
import datetime
import time
import operator

class QuoteObject(db.Model):
    quote_text = db.StringProperty(multiline=True)
    quote_text_alt = db.StringProperty(multiline=True)
    person_name = db.StringProperty()
    date = db.DateProperty()
    location = db.GeoPtProperty()
    person_age = db.IntegerProperty()
    photo_url = db.LinkProperty()
    tags = db.StringListProperty()
    use_first_question = db.BooleanProperty()


class MainPage(webapp.RequestHandler):
    def get(self):
        self.response.headers['Content-Type'] = 'text/html'
        FH = open('static/index.html')
        lines = FH.readlines()
        FH.close()
        datastore = self.getDataStore()
        quotelist_delimiter = '||quotelist||'
        taglist_delimiter = '||taglist||'
        taglist_all_delimiter = '||taglist_all||'
        map_delimiter = '||map||'
        for line in lines:
            if line.find(quotelist_delimiter) != -1:
                line = line.replace(quotelist_delimiter,
                                    self.generateQuotelist(datastore))
            if line.find(taglist_delimiter) != -1:
                line = line.replace(taglist_delimiter,
                                    self.generateTaglist(datastore, 5))
            if line.find(taglist_all_delimiter) != -1:
                line = line.replace(taglist_all_delimiter,
                                    self.generateTaglist(datastore, -1))
            if line.find(map_delimiter) != -1:
                line = line.replace(map_delimiter, self.generateMap(datastore))
            self.response.out.write(line)

    def getDataStore(self):
        query = QuoteObject.all()
        results = query.fetch(limit=200)
        return results
        
    def generateQuotelist(self, datastore):
        item_template = """
        <article id="quote%d" class="%s">
            %s
            <img src="%s" alt="">
        </article>"""
        quotelist = ''
        counter = 0
        for item in datastore:
            quote = ''
            if item.use_first_question:
                quote = item.quote_text
            else:
                quote = item.quote_text_alt
            if not quote:
                continue
            article = item_template % (counter, '', quote, item.photo_url)
            quotelist = '%s\n%s' % (quotelist, article)
            counter += 1
        return quotelist

    def generateTaglist(self, datastore, limit):
        item_template = '<li><a href="#%s">%s</a></li>\n'
        taglist = {}
        for item in datastore:
            for tag in item.tags:
                if tag in taglist:
                    taglist[tag] += 1
                else:
                    taglist[tag] = 0
        sorted_taglist = sorted(taglist.iteritems(),
                                key=operator.itemgetter(1))
        sorted_taglist.reverse()
        taglist_string = ''
        if limit == -1:
            limit = len(sorted_taglist) + 1
        for tag in sorted_taglist[:limit]:
            tag_string = item_template % (tag[0], tag[0])
            all_string = ''
            if limit == (len(sorted_taglist) + 1):
                all_string = '%s: %d\n' % (tag[0], tag[1])
                tag_string = ''
            taglist_string = '%s%s%s' % (taglist_string, tag_string,
                                         all_string)
        return taglist_string

    def generateMap(self, datastore):
        return ''
            
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
        question_to_use = self.request.get('use_first_question')
        if question_to_use.find('True') != -1:
            quote.use_first_question = True
        else:
            quote.use_first_question = False
        quote.put()
        self.redirect('/data_form')

class GenerateTagsAttribute(webapp.RequestHandler):
    def get(self):
        self.response.headers['Content-Type'] = 'text/html'
        self.response.out.write("""
<html><head><title>Generate Tags</title></head><body>""")
        query = QuoteObject.all()
        results = query.fetch(limit=200)
        banned_words = ['to', 'i', 'the', 'going', 'and', 'my', 'a', 'about',
                        'when', 'that', 'what', 'get', 'want', 'at', 'this',
                        'is', "i'm", 'are', 'right', u'i\u2019m', 'me', 'how',
                        'go', 'so', 'up', 'he', 'way', 'because', 'on', 'come',
                        'now', 'we', 'be', 'got', 'see', 'where', 'like',
                        'around', 'had', u'it\u2019s', 'it', 'have', 'just',
                        'really', 'guess', 'for', 'coming', 'take', 'if',
                        'was', 'thinking', 'know', 'wondering', 'of',
                        u'don\u2019t', 'anything', 'you', 'in', "don't",
                        'more', 'kind', 'some', 'not', 'do', 'but', 'buy',
                        'out', "that's", 'well', u'that\u2019s', 'back', 'or',
                        'stop']
        for result in results:
            text = ''
            if result.use_first_question:
                text = result.quote_text
                result.use_first_question = True
            elif len(result.quote_text_alt):
                text = result.quote_text_alt
                result.use_first_question = False
            else:
                text = result.quote_text
                result.use_first_question = True
            if not text:
                continue
            removals = ['.', '(', ')', '"']
            for removal in removals:
                text = text.replace(removal, '')
            words = text.split()
            taglist = []
            for word in words:
                word = word.lower()
                if word not in taglist and word not in banned_words:
                    taglist.append(word)
            result.tags = taglist
            self.response.out.write(
                '<p>Quote: %s<br>Tags: %s</p>' % (result.quote_text,
                                                  taglist))
            result.put()
        self.response.out.write('</body></html>')

class DataForm(webapp.RequestHandler):
    def get(self):
        self.response.out.write("""
<html><head><title>Add Data Here</title></head><body>
<form action="/add_data" method="post">
<div><p>What are you thinking about right now<textarea name="quote_text" rows="3" cols="60"></textarea></p></div>
<div><p>What do you need<textarea name="quote_text_alt" rows="3" cols="60"></textarea></p></div>
<div><p><input type="radio" name="use_first_question" value="True" checked>Use "What are you thinking about" question</input><br>
<input type="radio" name="use_first_question" value="False">Use "What do you need" question</input></p></div>
<div><p>Name of Quotee<input type="text" name="person_name"></input></p></div>
<div><p>Latitude<input type="text" name="location_lat"></input></p></div>
<div><p>Longitude<input type="text" name="location_long"></input></p></div>
<div><p>Age<input type="text" name="person_age"></input></p></div>
<div><p>Photo URL<input type="text" name="photo_url"></input></p></div>
<div><input type="submit" value="Add Quote"></div>
</form>
<br><br><a href="http://tenderneeds.appspot.com/generate_tags">Regenerate Tags</a>
</body>
</html>""")

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
        output['id'] = model.key().id()
        return output
    def post(self):
        pass

application = webapp.WSGIApplication(
                                     [('/add_data', AddData),
                                     ('/data_form', DataForm),
                                     ('/quotes', JSON),
                                     ('/generate_tags', GenerateTagsAttribute),
                                     ('/', MainPage)])

def main():
    run_wsgi_app(application)

if __name__ == "__main__":
    main()
