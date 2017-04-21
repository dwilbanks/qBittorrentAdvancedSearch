# qBittorrentAdvancedSearch
search plugins for qBittorrent

This project started to repair existing engines that were broken.

The baseline examples for for plugin engines are exceptionally convoluted and parse the HTML manually, I feel this 
is similar to re-inventing the wheel.  Unless you successfully make a better wheel, you have failed.  

The project grew towards isolating the various search engine specific components from the inner workings of a more 
complicated engine.

The project is now a framework for creating new plugins.   Instead of creating the entire plugin, you simpley built 
a couple methods, the framework takes care of the rest. 

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
