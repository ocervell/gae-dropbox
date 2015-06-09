#!/usr/bin/env python
import webapp2
import cgi
import time
import os
import jinja2
import urllib
import cloudstorage as gcs
import urlparse
import threading
import numpy
from datetime import datetime
from google.appengine.ext.webapp import template
from google.appengine.api import users
from google.appengine.api import app_identity
from google.appengine.api import memcache

from google.appengine.ext import blobstore
from google.appengine.ext.webapp import blobstore_handlers
from google.appengine.api import files


############################## GLOBAL PARAMETERS #############################
my_default_retry_params = gcs.RetryParams(initial_delay=0.2,
										  max_delay=5.0,
										  backoff_factor=2,
										  max_retry_period=15)
write_retry_params = gcs.RetryParams(backoff_factor=1.1)
bucket = '/cloudcomputing553'
filesizes = {}
RETRIEVE_TIME = []
REMOVE_TIME = []
sizes = []
nb_threads = 1
num_threads = 1
filenames = []
use_cache = True
############################# FUNCTIONS #################################

#Insert a file in GCS bucket
def insert(key, value):
	try:
		gcs_file = gcs.open(key,
							'w',
		    		        content_type='text/plain',
			    			retry_params=write_retry_params)
		gcs_file.write(value)
		gcs_file.close()
		return True
	except Exception:
		return False
			
#Insert a file in cache (the file stays in cache for 24 hours)
def insertCache(key, value):
	if key is None:
		return False
	if not memcache.set(key, value, 86400):
		return False
	return True

#Check if a file is in GCS bucket
def check(key):
	try:
		gcs.stat(key,
		 	 	 retry_params=write_retry_params)
		return True
	except Exception:
		return False
			
#Check if a file is in memcache
def checkCache(key):
	if memcache.get(key) is None:
		return False
	return True

#Retrieve the content of a file in GCS
def find(key):
	try:
		gcs_file = gcs.open(key,'r')
		data = gcs_file.read()
		gcs_file.close()
		return data
	except Exception:
		return 'Name of file invalid, file does not exist or problem with reading the file'
			
#Get file contents from memcache
def findCache(key):
	if key is None:
		return 'File does not exist'
	value = memcache.get(key)
	return value

#Remove a file from GCS bucket
def remove(key):
	filename = bucket + '/' + key
	try:
		gcs.delete(filename,
				   retry_params=None)
		if checkCache(key): removeCache(key)
		return True
	except Exception:
		return False

#Remove a file from memcache
def removeCache(key):
	if key is None:
		return False
	if memcache.delete(key) != 2:
		return False
	return True

#Remove all files from the cache and GCS bucket
def removeAll():
	#removeAllCache()
	
	content = listing()
	for i in content:
		if not remove(str(i).replace(bucket,"")[1:]): return False
	removeAllCache()
	return True

#Remove all cache
def removeAllCache():	
	if memcache.flush_all():
		return True
	else:
		return False

#List all elements in GCS bucket
def listing():
	listbucket=[]
	bucketContent = gcs.listbucket(bucket,
				 				   marker=None,
				 				   max_keys=None,
				  				   delimiter=None,
				  				   retry_params=None)
	for entry in bucketContent:
		listbucket.append(entry.filename)
	return listbucket

def cacheSizeMB():
	return float(memcache.get_stats()['bytes']) / 1024

def cacheSizeElem():
	return memcache.get_stats()['items']

################################## PAGES #####################################

#This is the main page. It has a dropdown menu where one can choose between
#multiple options.
class MainPage(webapp2.RequestHandler):
	def get(self):
		template_values = {}
		path = os.path.join(os.path.dirname(__file__), "form.html")
		self.response.write(template.render(path,template_values))

#This is the page showed to the user after he picked one of the
#options.For example, if the user chose 'Insert file' he will
#get the menu to look for a file to upload into GCS bucket.
class Landing(webapp2.RequestHandler):
	def post(self):
		global opt
		JINJA_ENVIRONMENT = jinja2.Environment(
    	loader=jinja2.FileSystemLoader(os.path.dirname(__file__)),
    	extensions=['jinja2.ext.autoescape'],
    	autoescape=True)

		opt = cgi.escape(self.request.get('opt'))			
		
		template_values = {
            'option': opt
		}
		
		template = JINJA_ENVIRONMENT.get_template('landing.html.jinja2')
		self.response.write(template.render(template_values))				

#This page will choose among the below classes and execute the
#right function. 
class Process(webapp2.RequestHandler):
	def get(self):
		JINJA_ENVIRONMENT = jinja2.Environment(
    	loader=jinja2.FileSystemLoader(os.path.dirname(__file__)),
    	extensions=['jinja2.ext.autoescape'],
    	autoescape=True)
		
		option = self.request.get('option')
		success = self.request.get('success')
		elements = self.request.get('elements')
		size = self.request.get('size')

		template_values = {
            'option': option,
			'success' : success,
			'elements': elements,
			'size': size
		}

		template = JINJA_ENVIRONMENT.get_template('process.html.jinja2')
		self.response.write(template.render(template_values))


class Insert(webapp2.RequestHandler):
	def post(self):
		key = self.request.params['insert'].filename
		value = self.request.get('insert')
		success = 'yes'
		filename = bucket + '/' + key
		if(len(value)<=100000): #If the size of the file is < 100 kb, we
		#add it to the cache as well
			if not insertCache(key, value) : success = 'no'
		if not insert(filename, value) : success = 'no'

		redirect_url = "process?option=insert&success=%s" % success		
		self.redirect(redirect_url)

		
class Check(webapp2.RequestHandler):
	def post(self):
		key = self.request.get('check')
		success = 'yes'
		filename = bucket + '/' + key
		if not checkCache(key):
			if not check(filename): success = 'no'

		redirect_url = "process?option=check&success=%s" % success		
		self.redirect(redirect_url)

class Find(webapp2.RequestHandler):
	def post(self):
		key = self.request.get('find')
		success = 'yes'
		filename = bucket + '/' + key
		data = findCache(key)
		if (data is None):
			if check(filename):
				data = find(filename)
			else:
				success = 'no'
		self.response.write(data)
		#redirect_url = "process?option=find&success=%s" % success
		#self.redirect(redirect_url)
		

class Remove(webapp2.RequestHandler):
	def post(self):

		key = self.request.get('remove')
		filename = bucket + '/' + key
		success = 'yes'

		if not removeCache(key) and checkCache(key): success = 'no'
		if not remove(key) and check(filename): success = 'no'

		redirect_url = "process?option=remove&success=%s" % success
		self.redirect(redirect_url)

class RemoveAll(webapp2.RequestHandler):
	def get(self):
		success = 'yes'
		if not removeAll(): success = 'no'
		redirect_url = "process?option=removeall&success=%s" % success		
		self.redirect(redirect_url)


class Listing(webapp2.RequestHandler):
	def get(self):
		self.response.write("Listing of elements in bucket <b>%s</b> :<br/>" % bucket[1:])
		listbucket = listing()
		for s in listbucket:
			self.response.write("<br/>")
			self.response.write(str(s).replace(bucket,"")[1:])

class CheckCache(webapp2.RequestHandler):
	def post(self):
		key = self.request.get('checkcache')
		success = 'yes'
		if not checkCache(key): success = 'no'

		redirect_url = "process?option=checkcache&success=%s" % success		
		self.redirect(redirect_url)

class RemoveAllCache(webapp2.RequestHandler):
	def get(self):
		success = 'yes'
		if not removeAllCache(): success = 'no'

		redirect_url = "process?option=removeallcache&success=%s" % success		
		self.redirect(redirect_url)

class CacheSize(webapp2.RequestHandler):
	def get(self):
		success = 'yes'
		size = cacheSizeMB()
		redirect_url = "process?option=cachesize&success=%s&size=%s" % (success, size)
		self.redirect(redirect_url)

class CacheSizeElem(webapp2.RequestHandler):
	def get(self):
		success = 'yes'
		items = cacheSizeElem()
		redirect_url = "process?option=cachesizeelem&success=%s&elements=%s" % (success, items)
		self.redirect(redirect_url)


class Benchmark(webapp2.RequestHandler):
	def get(self):
   		upload_url = blobstore.create_upload_url('/upload', gs_bucket_name = bucket[1:])
		self.response.out.write('<html><body>')
            	self.response.out.write('<form action="%s" method="POST" enctype="multipart/form-data">' % upload_url)
            	self.response.out.write("""
				<b><h2> Benchmark over a dataset </h2></b>
            	</br><b>Select the number of threads :</b> 
           		</br><input type="radio" name="num_threads" value="1">One
           		</br><input type="radio" name="num_threads" value="4">Four
            	<br/></br><b>Use memcache</b>
            	<input type="checkbox" name="use_cache" value="True"  /></br></br><b>
            	<br/><b><label for "files"> Select your dataset </label></b>
           		<input type="file" multiple name="file"><br>
            	<br/><br/><input type="submit" name="submit" value="Submit"> </form></body></html>""")

class Upload(blobstore_handlers.BlobstoreUploadHandler):
	def post(self):
		global num_threads
		global use_cache
		global nb_threads
		num_threads = int(self.request.get('num_threads'))
		use_cache = self.request.get('use_cache')
		nb_threads = num_threads
		#INSERT OPERATION - Can't be multithreaded if using blobstore as get_file_infos recovers everything from the html form and automatically upload it through the upload_url seen earlier.
		upload_files = self.get_file_infos('file')  # 'file' is file upload field in the form
		for file_ in upload_files:
			key = file_.gs_object_name[(4+len(bucket)):] #cutting /gs/bucket_name/ to retrieve only the key
			sizes.append(file_.size)
			filenames.append(key)
			filesizes[key] = file_.size
		self.response.write(" %s blobs stored " % len(upload_files))
		self.redirect('runthreads')

class Runthreads(webapp2.RequestHandler):
	def get(self):
		#Retrieving GCS file names
		Threads     = []
		TestRoutine = {}
			
		#Filling local arrays filenames and contents, filling global dict files with filename as key and content as value.
		#Launching threads with dataset picked by the user through HTML form.
		for i in range(num_threads):
			section_length = len(filenames)/num_threads
			first = section_length*i
			last = first + section_length
	   		if last < len(filenames):
			     if i == num_threads-1:
			         last = len(filenames)+1
			filenames_thread = filenames[first:last]

			TestRoutine[i] = runtest(filenames_thread, use_cache, nb_threads, i)
			Threads.append(TestRoutine[i])
			TestRoutine[i].daemon = True
			TestRoutine[i].start()

		for i in range(num_threads):
			TestRoutine[i].join()
		
		self.redirect("display")

class runtest(threading.Thread):
	def __init__(self, filenames, use_cache, num_threads, id):
		super(runtest,self).__init__()
		self.filenames = filenames
		self.use_cache = use_cache
		self.num_threads = num_threads
		self.id = id

	def run(self):

		#INSERT OPERATION (in cache)
		for name in self.filenames:
			if((filesizes[name]<=100000) and self.use_cache): #If the size of the file is < 100 kb and memcache option is on
			   name_gcs = bucket+'/'+ name.encode()
			   gcs_file = gcs.open(name_gcs, 'r')
			   value = gcs_file.read()
			   insertCache(name, value)
			
		#RETRIEVE OPERATION
		start_retrieve = datetime.now()
		fileaccess = numpy.random.random_integers(0,len(self.filenames)-1,2*len(self.filenames)) #Generating 2 random accesses per file following uniform distribution	
		for i in range(len(fileaccess)):	
			key = self.filenames[fileaccess[i]]
			filename = bucket + '/' + key.encode()
			value = findCache(key)
			if (value is None):
				if check(filename):
					with gcs.open(filename, 'r') as f:
						for line in f:
							value = f.readline()
		RETRIEVE_TIME.append((datetime.now() - start_retrieve).total_seconds())
			
		#REMOVE OPERATION
		start_remove = datetime.now()
		for name in self.filenames:
			remove(name)
		REMOVE_TIME.append((datetime.now() - start_remove).total_seconds())

class Display(webapp2.RequestHandler):
	def get(self):
		#PRINTING NECESSARY INFORMATION ON LANDING PAGE	
		nb_threads = num_threads
		nb_files = len(sizes)
		size = 0.0
		for s in sizes:
			size += s
		units = ["B", "kB", "MB", "GB"]
		i = 0
		size_ = size
		#Adapting size to the right unit (B, kB, MB, GB)
		unit = "B"
		while (size > 1024):
			size = size / 1024
			i = i + 1
			unit = units[i]

		#Display list of inserted file
		self.response.write("<b><h1>Report file</h1></b>")
		self.response.write("<h3>Dataset :</h3><b>Number of files:</b> %d <br/><b>Total size:</b> %.1f %s" %(nb_files,size,unit))
		#for f in filenames:
			#self.response.write("<br/>%s" % f)

		#Calculate and display timings
		total_retrieve = 0
		throughput_retrieve = 0
		for t in RETRIEVE_TIME:
			total_retrieve += t
		total_retrieve /= nb_threads
		avg_retrieve = total_retrieve / (2*nb_files)
		if (total_retrieve != 0):
			throughput_retrieve = (2*size_) / total_retrieve #We generate two access per file so the totalsize processed is 2 * number of files
			throughput_retrieve /= (1024*1024) #conversion Bytes -> MBytes

		total_remove = 0
		throughput_remove = 0
		for t in REMOVE_TIME:
			total_remove += t 
		total_remove /= nb_threads
		avg_remove = (total_remove / nb_files)*1000 #average remove time is in milliseconds
		if (total_remove != 0):
			throughput_remove = size_ / total_remove
			throughput_remove /= (1024*1024) #Conversion Bytes -> MBytes

		
		self.response.write("<br/><br/><h3>Retrieve operation: </h3>")
		self.response.write("<b>Retrieve time: </b> %.1f seconds" % total_retrieve)
		self.response.write("<br/><br/><b>Average retrieve time: </b> %.3f s/file" % avg_retrieve)
		self.response.write("<br/><br/><b>Retrieve throughput: </b> %.1f MB/s" % throughput_retrieve)
	
		self.response.write("<br/><br/><h3>Remove operation: </h3>")
		self.response.write("<b>Remove time: </b> %.2f seconds" % total_remove)
		self.response.write("<br/><br/><b>Average remove time: </b> %.f ms/file" % avg_remove)
		self.response.write("<br/><br/><b>Remove throughput: </b> %.1f MB/s" % throughput_remove)	

		#Reinitializing global variables
		filesizes.clear()
		del RETRIEVE_TIME[:]
		del REMOVE_TIME[:]
		del sizes[:]
		del filenames[:]
		nb_threads = 1
		

app = webapp2.WSGIApplication([
    ('/', MainPage),
	('/land', Landing),
	('/process', Process),
	('/insert', Insert),
	('/check', Check),
	('/find', Find),
	('/remove', Remove),
	('/removeall', RemoveAll),
	('/listing', Listing),
	('/checkcache', CheckCache),
	('/removeallcache', RemoveAllCache),
	('/cachesize', CacheSize),
	('/cachesizeelem', CacheSizeElem),
	('/benchmark',Benchmark),
	('/upload', Upload),
	('/runthreads', Runthreads),
	('/display', Display)
], debug=True)


