# gae-dropbox
A dropbox web application for Google App Engine

Getting Started
---------------
To deploy the app on your own Google App Engine project, you need to :

- put the project folder dropbox in the Google App Engine SDK folder.
- to run it locally, from the GAE folder: ./dev_appserver.py dropbox
  Note: If you run it locally, you should have Numpy library for Python installed on your machine

- to deploy the application:
•	Put your project name on the first line of the app.yaml file.
•	Change the variable bucket and put your own bucket name.
•	./appcfg update dropbox
•	./appcfg backends update dropbox backend
Note: This last line will launch a backend to be able to process the entire dataset without timeouts.

- to generate the dataset: report to section ‘Dataset generator’

Usage
---------------
The web application can be accessed at 
cloudcomputing553.appspot.com

To upload the whole benchmark, we needed to get rid of the HTTP 60 seconds time out which is present on default instances. 
To do that, we added a backend that can support long requests. 
It is accessible at:
backend.cloudcomputing553.appspot.com

Operations
---------------
At the homepage, you can select one of the following operations from the drop down button and then click Submit.

•	Insert File - upload a file to GCS. If the file size is less than 100KB it is also stored in cache. 
•	Check File - check if a file is on GCS
•	Find File - retrieve file from cache or GCS and prints its content on the web page.
•	Remove File - remove a file from GCS and cache.
•	List all Files - list all files stored in GCS.
•	Check file in cache - check if a file is on cache.
•	Remove all files from cache
•	Remove all files - remove all files from GCS and cache.
•	Show cache usage (MB)
•	Show total files in cache
•	Run Benchmark

Note: for the basic operations, a file bigger than 32 MB will produce an HTTP timeout.
This issue was solved but used only in the ‘run benchmark’ option (see previous paragraph ‘The 32 MB problem’).

At the “Run Benchmark” option it is possible to choose the number of threads to run the tests, the use of memcache and the dataset files to be used for benchmarking. Here you can upload a dataset of any size without a time-out error.

