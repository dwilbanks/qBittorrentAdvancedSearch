# qBittorrentAdvancedSearch
search plugins for qBittorrent

This project started to repair existing engines that were broken.

The baseline examples for for plugin engines are exceptionally convoluted and parse the HTML manually, I feel this 
is similar to re-inventing the wheel.  Unless you successfully make a better wheel, you have failed.  

The project grew towards isolating the various search engine specific components from the inner workings of a more 
complicated engine.

The project is now a framework for creating new plugins.   Instead of creating the entire plugin, you simpley built 
a couple methods, the framework takes care of the rest. 

###Getting Started:
	There are two main components that may or may not be installed into your python. 

	From the command line issue these two commands.
	
	pip install requests
	pip install lxml
	
	If these commands worked for you, you probably didn't even need to have me tell you what
	the commands were.  You are probably already a python expert, why are you reading this?
	
	In almost all cases, unless you are already a python expert these two commands will fail.
	The reason for this is the makers of python hate you.   If you are not every bit as
	knowlegable as they are about python they detest you.   If you don't use linux they hate
	you even more.
	
	To compensate for the fact that the makers of qBittorrent have chosen python as the
	language for search, and the makers of python hates the target audience qBittorrent, 
	I will have to explain a couple things that are public-secrets.   
	
	Nobody goes out of	their 	way to explain these little details, but, knowing them is 
	essential to using python.
	
	First, you will need to know where your python is installed.  
	
	When you did your install it asked you a bunch of questions.  We don't read, them, 
	we just click next-next-next until it says we are done.
	
	One of those questions was where would you like your python installed.   This is
	important because the contributers to python hate each other more than they hate
	consumers.  Instead of a central place for installing python, everyone suggests a
	different place to install it.  This is because all other people contributing to python
	are wrong, and only the person who built the package you downloaded knows the correct
	location for installing python.
	
	If you don't know where it installed, exit out of qBittorrent, then launch it again.
	Navigate to the execution log, tab and look for the text for where is says:
	"python found in"  
	
	Open a command prompt and change directories, then within that directory change to the
	"scripts" directory.
	
	If your python is installed in "C:\Python27" then your scripts will be in
	"C:\Python27\scripts"
	
	From there you can run the pip commands above.
	If that does not work, then maybe it's better to install a different version of python.
	

###Required Properties:
* url - Required by qBittorrent, this must be unique
* name - Required by qBittorrent, this must be unique 
* supported_categories - Required by qBittorrent
* cfg_engine - dictionary, describes configuration items about this specific engine
* keyElementDesc - string - either lxml.etree compatible find string, or json base class 
			- This will be described more in detail elsewhere

###Required Methods:
	def custom_getURL(self, pageNum)
		The base object handles the search method, it filters through the "what" and "cat" 
		then calls the custom_getURL method for you to format the information into the URL 
		to use to get the specific page URL
    
	def custom_eltToArray(self, key_element):
			The base object handles reading the page and getting a collection of elements from
			the page to parse.  If the search engine is simple, this will be a table row.   
			Given that table row, you can then search that row for the information needed to 
			populate a results array.
			    
###Optional Methods:
	def custom_pageProcess1(self, url, root):
	def custom_pageProcess2(self, url, root):
		These methods are called before and after the itteration of results data and calls 
		to the custom_eltToArray method
		Default is to return True, the pages can also return False, which indicates that 
		processing should end with this page.
	def custom_download(self)
		This method is called as a part of the download process.  You may need to read 
		additional information like parsing an description page to actually get to the torrent URL

		
### examples:

```javascript
function fancyAlert(arg) {
  if(arg) {
    $.facebox({div:'#foo'})
  }
}
```
