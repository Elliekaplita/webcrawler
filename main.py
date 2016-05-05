#!/usr/bin/python

from flask import Flask, render_template, request, url_for, redirect
from celery import Celery
#from nltk.corpus import wordnet as wn
#from wikimarkup import parse
from time import sleep
import json
import re
import urllib2
import urllib
import lxml.html

app = Flask(__name__, static_url_path='')
app.debug = True
app.config['CELERY_BROKER_URL'] = 'redis://localhost:6379/0'
app.config['CELERY_RESULT_BACKEND'] = 'redis://localhost:6379/0'

celery = Celery(app.name, broker=app.config['CELERY_BROKER_URL'])
celery.conf.update(app.config)

@app.route('/')
def index():
#    return app.send_static_file('index.html')
     return render_template("index.html")

@app.route('/make', methods=['POST'])
def make():
	webpageid = request.form["webpageid"]
	task = processwebpage.delay(webpageid)
	#return 'Job ID ' + task.id, 302, {'Location': url_for('progresspage', task_id = task.id)}
#	return "Original: \n\n" + wp.content + "\n\nNew: \n\n" + content + "\n\nChanged words: " + str(replacecount) + "\n\nLog:\n" + output
	return render_template('wait.html', taskid = task.id)

@app.route('/result/<task_id>')
def result(task_id):
	task = processwebpage.AsyncResult(task_id)
	if task.state == 'SUCCESS':
		links = task.result['links']
		return render_template("result.html", links = links)
	else:
		return "Be more patient!"

@app.route('/status/<task_id>')
def progress(task_id):
	task = processwebpage.AsyncResult(task_id)
	stat = ""
	curr = 0
	total = 100
	if task.state == 'PENDING':
		stat = "Job queued..."
	elif task.state == 'PROCESSING':
		stat = task.info['status']
		curr = task.info['current']
		total = task.info['total']
	elif task.state == 'SUCCESS':
		stat = task.info['status']
		return json.dumps({'progress': curr, 'status': stat, 'links': task.result['links'], 'complete': 1})
	else:
		stat = 'An error occurred.'
	#return render_template("wait.html", status = stat, current = curr, total = total)
	return json.dumps({'percent': curr, 'status': stat, 'total': total, 'complete': 0})

@celery.task(bind=True)
def processwebpage(self, webpageid):
	# webpageid (URL of the page to crawl)
	# --> links fetch webpage download webpage to python as string get links out of it and list them
	links = ""
	webpage = urllib.urlopen('http://' + webpageid) 	
	dom =  lxml.html.fromstring(webpage.read())

	for link in dom.xpath('//a/@href'): # select the url in href for all links
	    links += "\n" + link


	self.update_state(state='PROCESSING', meta={'current': 5, 'total': 100, 'status': 'Downloading webpage...'})
	# ---

	# ---
	return {'current': 100, 'total': 100, 'status': 'Processing complete!', 'links': links}
	
	

def checkword(word):
	if len(word) < 5:
		return False
	if word[0].isupper():
		return False
	if word[-1] == 's':
		return False
	return True

def checksyn(word):
	if "_" in word:
		return False
	if word[0].isupper():
		return False
	return True


if __name__ == '__main__':
    app.run(host='0.0.0.0')
