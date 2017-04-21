# qBittorrentAdvancedSearch
search plugins for qBittorrent

This project started to repair existing engines that were broken.

The baseline examples for for plugin engines are exceptionally convoluted.

The project grew towards isolating the various search engine specific components from the inner workings of a more complicated engine.

Required Propertyies:
  url - Required by qBittorrent, this must be unique
  name - Required by qBittorrent, this must be unique 
  supported_categories - Required by qBittorrent
  cfg_engine - dictionary, describes configuration items about this specific engine
  keyElementDesc - string - either lxml.etree compatible find string, or json base class- Described later

Required Methods:
  def custom_getURL(self, pageNum)
    The base object handles the search method, it filters through the "what" and "cat" then calls the custom_getURL method for you to format the information into the URL to use to get the specific page URL
    
  def custom_eltToArray(self, key_element):
    The base object handles reading the page and getting a collection of elements from the page to parse.
    If the search engine is simple, this will be a table row.   Given that table row, you can then search that row for the information needed to populate a results array.
    
Optional Methods:
  def custom_pageProcess1(self, url, root):
  def custom_pageProcess2(self, url, root):
    These methods are called before and after the itteration of results data and calls to custom_eltToArray
      Default is to return True, the pages can also return False, which indicates that processing should end with this page.
  def custom_download(self)
    This method is called as a part of the download process.  You may need to read additional information like parsing an description page to actually get to the torrent URL
    
    
