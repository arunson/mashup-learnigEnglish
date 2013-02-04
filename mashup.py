import webapp2
import urllib2
import json
import jinja2
import os
from xml.dom import minidom

template_dir = os.path.join(os.path.dirname(__file__),'templates')
jinja_env = jinja2.Environment(loader = jinja2.FileSystemLoader(template_dir), autoescape = True)


class MashupHandler(webapp2.RequestHandler):
	def write(self, *a, **kw):
		self.response.out.write(*a,**kw)
	def render_str(self,template,**params):
		t = jinja_env.get_template(template)
		return t.render(params)
	def render(self, template,**kw):
		self.write(self.render_str(template,**kw))

def getTweets(keyword):
	search = urllib2.urlopen("http://search.twitter.com/search.json?q=" + keyword)
	response = search.read()
	data = json.loads(response)
	results = data['results']
	return [i['text'] for i in results]

#https://developers.google.com/image-search/v1/jsondevguide
def getImages(keyword):
	url = ('https://ajax.googleapis.com/ajax/services/search/images?' + 'v=1.0&q=%s&rsz=8&imgsz=medium' %keyword)
	response = urllib2.urlopen(url).read()
	data = json.loads(response)
	results = data['responseData']['results']
	return [i['url'] for i in results]

class Item:
	sound="http://media.merriam-webster.com/soundc11/h/"
	ew=""
	pr=""
	fl=""


#http://www.dictionaryapi.com/products/api-collegiate-dictionary.htm
def getDic(keyword):
	url = 'http://www.dictionaryapi.com/api/v1/references/collegiate/xml/%s?key=yourkey' %keyword
	response = urllib2.urlopen(url).read()
	dom = minidom.parseString(response)
	entries = dom.getElementsByTagName('entry')
	items = []
	for entry in entries:
		item = Item()
		if len(entry.getElementsByTagName('ew'))>0:
			item.ew = entry.getElementsByTagName('ew')[0].firstChild.nodeValue
		if len(entry.getElementsByTagName('fl'))>0:
			item.fl = entry.getElementsByTagName('fl')[0].firstChild.nodeValue
		if len(entry.getElementsByTagName('pr'))>0:
			item.pr = entry.getElementsByTagName('pr')[0].firstChild.nodeValue
		if len(entry.getElementsByTagName('sound'))>0:
			item.sound=entry.getElementsByTagName('sound')[0].getElementsByTagName('wav')[0].firstChild.nodeValue
		defs = entry.getElementsByTagName('def')[0]
		dts = defs.getElementsByTagName('dt')
		item.defs = []
		for dt in dts:
			#sentence = dt.firstChild.nodeValue
			#for node in dt.childNodes:
			#	if node.nodeName == 'sx':
			#		sentence += (',' + node.firstChild.nodeValue)
			#	elif node.nodeName == 'vi':
			#		sentence += (',' + node.firstChild.nodeValue)
			#item.defs.append(sentence)
			item.defs.append(dt.toxml())
		items.append(item)
	return items

class MainPage(MashupHandler):
	def get(self):
		self.render('base.html')

	def post(self):
		keyword=self.request.get('query')
		keyword = keyword.replace(' ','%20')
		#twitter data
		tweets = getTweets(keyword)
		#dictionary data
		dicItems = getDic(keyword)
		#image data
		images = getImages(keyword)
		#self.render('base.html')
		self.render('base.html', tweets = tweets, images=images, dicItems=dicItems)


app = webapp2.WSGIApplication([('/learningenglish',MainPage),],debug=True)