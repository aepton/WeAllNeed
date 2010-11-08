from google.appengine.ext import webapp
from google.appengine.ext.webapp.util import run_wsgi_app
from google.appengine.api import users
from google.appengine.ext import db
from django.utils import simplejson
import datetime
import time
import operator
from google.appengine.api import urlfetch
import urllib
import sys

class QuoteObject(db.Model):
    quote_text = db.StringProperty(multiline=True)
    quote_text_alt = db.StringProperty(multiline=True)
    person_name = db.StringProperty()
    date = db.DateProperty()
    location = db.GeoPtProperty()
    person_age = db.IntegerProperty()
    photo_url = db.LinkProperty()
    audio_url = db.LinkProperty()
    tags = db.StringListProperty()
    use_first_question = db.BooleanProperty()
    audio_embed = db.StringProperty(multiline=True)


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
        if self.request.get('item_id'):
            quote = QuoteObject.get_by_id(int(self.request.get('item_id')))
        else:
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
        quote.audio_url = self.request.get('audio_url')
        question_to_use = self.request.get('use_first_question')
        if question_to_use.find('True') != -1:
            quote.use_first_question = True
        else:
            quote.use_first_question = False
        quote.put()
        self.redirect('/data_form')

class GenerateAudioEmbed(webapp.RequestHandler):
    def get(self):
        query = QuoteObject.all()
        results = query.fetch(limit=200)
        self.response.headers['Content-Type'] = 'text/plain'
        soundcloud_url = 'http://api.soundcloud.com/oembed?url='
        for result in results:
            try:
                fetchresult = urlfetch.fetch(str(soundcloud_url+result.audio_url+'&format=json'))
                #result.audio_embed = urllib.decode(fetchresult.content['html'])
                #result.put()
                #self.response.out.write(urllib.decode(fetchresult.content['html']))
                self.response.out.write('---\n')
                self.response.out.write(fetchresult.content.keys())
            except:
                self.response.out.write('No - %s! %s' % (sys.exc_info()[0],
                                                         result.person_name))
#           result.audio_embed
#           result.put()

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

class ViewData(webapp.RequestHandler):
    def get(self):
        self.response.headers['Content-Type'] = 'text/html'
        query = QuoteObject.all()
        results = query.fetch(limit=200)
        link = 'http://tenderneeds.appspot.com/data_form?id='
        self.response.out.write('<html><head><title>All entries</title>')
        self.response.out.write('</head><body>')
        for result in results:
            self.response.out.write('<a href=%s%d>%d - %s</a><br>' % (
                link, result.key().id(), result.key().id(), result.person_name))
        self.response.out.write('</body></html>')

class DataForm(webapp.RequestHandler):
    def get(self):
        item_id = self.request.get('id')
        item_strs = {'quote_text': '', 'quote_text_alt': '',
                     'use_first_q_true': '', 'use_first_q_false': '',
                     'name': '', 'location_lat': '', 'location_long': '',
                     'age': '', 'photo_url': '', 'mp3_url': '',
                     'update_item': ''}
        if item_id:
            quote = QuoteObject.get_by_id(int(item_id))
            item_strs['quote_text'] = quote.quote_text
            item_strs['quote_text_alt'] = quote.quote_text_alt
            item_strs['use_first_q_true'] = 'checked' if quote.use_first_question else ''
            item_strs['use_first_q_false'] = 'checked' if not quote.use_first_question else ''
            item_strs['name'] = quote.person_name
            location_string = str(quote.location)
            item_strs['location_lat'] = location_string.split(',')[0]
            item_strs['location_long'] = location_string.split(',')[1]
            item_strs['age'] = quote.person_age
            item_strs['photo_url'] = quote.photo_url
            item_strs['mp3_url'] = quote.audio_url
            item_strs['update_item'] = ('<input type="hidden" name="item_id"'
                                        'value="%s">' % item_id)
        else:
            item_strs['use_first_q_true'] = 'checked'
        self.response.out.write("""
<html><head><title>Add Data Here</title></head><body>
<form action="/add_data" method="post">
<div><p>What are you thinking about right now<textarea name="quote_text" rows="3" cols="60">%s</textarea></p></div>
<div><p>What do you need<textarea name="quote_text_alt" rows="3" cols="60">%s</textarea></p></div>
<div><p><input type="radio" name="use_first_question" value="True" %s>Use "What are you thinking about" question</input><br>
<input type="radio" name="use_first_question" value="False" %s>Use "What do you need" question</input></p></div>
<div><p>Name of Quotee<input type="text" name="person_name" value=%s></input></p></div>
<div><p>Latitude<input type="text" name="location_lat" value=%s></input></p></div>
<div><p>Longitude<input type="text" name="location_long" value=%s></input></p></div>
<div><p>Age<input type="text" name="person_age" value=%s></input></p></div>
<div><p>Photo URL<input type="text" name="photo_url" value=%s></input></p></div>
<div><p>MP3 URL<input type="text" name="audio_url" value=%s></input></p></div>
%s
<div><input type="submit" value="Add Quote"></div>
</form>
<br><br><a href="http://tenderneeds.appspot.com/generate_tags">Regenerate Tags</a>
</body>
</html>""" % (item_strs['quote_text'], item_strs['quote_text_alt'],
              item_strs['use_first_q_true'], item_strs['use_first_q_false'],
              item_strs['name'], item_strs['location_lat'],
              item_strs['location_long'], item_strs['age'],
              item_strs['photo_url'], item_strs['mp3_url'],
              item_strs['update_item']))

class JSON (webapp.RequestHandler):
    def get(self):
        self.response.headers['Content-Type'] = 'text/plain'
        query = QuoteObject.all()
        results = query.fetch(limit=200)
        json_out = []
        if self.request.get("callback"):
            self.response.out.write(self.request.get("callback")+"(")
        for result in results:
            json_out.append(self.to_dict(result))
        resp = simplejson.dumps(json_out, separators=(',',':'))
        self.response.out.write(resp)
#        self.response.out.write('[')
#        for out in json_out[:-1]:
#            self.response.out.write('{\n')
#            for key in out.keys():
#                if isinstance(out[key], basestring):
#                    out[key] = '"%s"' % out[key]
#                self.response.out.write('\t%s: %s,\n' % (key, out[key]))
#            self.response.out.write('},\n')
#        self.response.out.write('{\n')
#        out = json_out[-1]
#        for key in out.keys():
#            if isinstance(out[key], basestring):
#                out[key] = '"%s"' % out[key]
#            self.response.out.write('\t%s: %s,\n' % (key, out[key]))
#        self.response.out.write('}]\n')
        if self.request.get("callback"):
            self.response.out.write(");")
        
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
                                     ('/view_data', ViewData),
                                     ('/generate_audio_embed', GenerateAudioEmbed),
                                     ('/', MainPage)])

def main():
    run_wsgi_app(application)

if __name__ == "__main__":
    main()
