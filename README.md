# gae-dropbox
## A dropbox web application for Google App Engine using GCS and memcache.

Description
-----------
* This web application developed on Google App Engine has the purpose of offering a **web interface for adding, finding, removing, checking existence of files in a GCS bucket**. 
* It uses memcache for small files (<100 kB) and GCS for bigger files.
* The web application also allows to **list all files in GCS (or memcache, or both)**, **check cache usage (MB)**, and **benchmark** (w/ and w/o memcache enabled) the speed of the operations for a dataset. The operations measured by the benchmarking option are **insert**, **check**, **remove**, **find**.
* A shell script to **generate a dataset** of any size is also provided in **dataset_gen.sh**. 

Getting Started
---------------
To deploy the app on your own Google App Engine project, you need to :

* put the project folder **dropbox** in the Google App Engine (GAE) SDK folder.

* to run it locally:
  * from the GAE folder: **./dev_appserver.py dropbox**
  * *Note:* If you run it locally, you should have Numpy library for Python installed on your machine

* to run it remotely:
  * Put your project name on the first line of the *app.yaml* file.
  * Change the variable bucket and put your own bucket name.
  * **./appcfg update dropbox**
  * **./appcfg backends update dropbox backend**
    *Note:* This last line will launch a backend server, necessary to process the entire dataset without timeouts.

* to generate the dataset:
  * To generate x files of size y, run: **python random_gen.py x y**
  * To run the dataset generator, run the command line: **bash dataset_gen.sh**. *Note:* This will create a folder named *dataset* containing all generated files.
The dataset contains 411 files spanning 311MB of data, according to the following rules:
      * 100 files of 1KB (100KB total)
      * 100 files of 10KB (1MB total)
      * 100 files of 100KB (10MB total)
      * 100 files of 1MB (100MB total)
      * 10 files of 10MB (100MB total)
      * 1 files of 100MB (100MB total)

Usage
-----
The web application can be accessed at 
**cloudcomputing553.appspot.com**

To upload the whole benchmark, we needed to get rid of the HTTP 60 seconds time out which is present on GAE default instances. 
To do that, we added a backend that can support long requests. 
It is accessible at:
**backend.cloudcomputing553.appspot.com**

Operations
---------------
At the homepage, you can select one of the following operations from the drop down button and then click Submit.

* **Insert File** - upload a file to GCS. If the file size is less than 100KB it is also stored in cache. 
* **Check File** - check if a file is on GCS
* **Find File** - retrieve file from cache or GCS and prints its content on the web page.
* **Remove File** - remove a file from GCS and cache.
* **List all Files** - list all files stored in GCS.
* **Check file in cache** - check if a file is on cache.
* **Remove all files from cache**
* **Remove all files** - remove all files from GCS and cache.
* **Show cache usage (MB)**
* **Show total number of files in cache**
* **Run Benchmark** - Run the benchmark (performance test) with the dataset

*Note:* for the basic operations, a file bigger than 32 MB will produce an HTTP timeout (except for *Run Benchmark* which can accept bigger datasets/files).

At the “Run Benchmark” option it is possible to choose the number of threads to run the tests, the use of memcache and the dataset files to be used for benchmarking. Here you can upload a dataset of any size without a time-out error.

