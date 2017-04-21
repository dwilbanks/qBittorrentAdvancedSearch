#VERSION: 1.0
from engines._x1_common import basePlugin
import traceback
class aazooqlexml(basePlugin):
    url = "http://AA-zooqle.com"
    name = "AA-Zooqle"
    baseurl = "https://zooqle.com/search?%s"
    supported_categories = {
        'all'       : 'all',
        'anime'     : 'Anime',
        'books'     : 'Books',
        'games'     : 'Games',
        'movies'    : 'Movies',
        'music'     : 'Music',
#       'pictures'  : '',
        'software'  : 'Apps',
        'tv'        : 'TV',
    }
    keyElementDesc = ".//item"
    cfg_engine ={
         "search_dataType":"xml",
         "search_UseText":False,
         "ignoreZeroByte":True,
         "search_decode":False,
    }
    def custom_eltToArray(self, key_element):
        try:
            name = key_element.find("title").text
            bthash = key_element.find("{https://zooqle.com/xmlns/0.1/index.xmlns}infoHash").text
            return {
                "name"          :name,
                "size"          :key_element.find("enclosure").get("length"),
                "bthash"        :bthash,
                "leech"         :key_element.find("{https://zooqle.com/xmlns/0.1/index.xmlns}peers").text,
                "seeds"         :key_element.find("{https://zooqle.com/xmlns/0.1/index.xmlns}seeds").text,
                "url_desc"      :key_element.find("link").text,
                "url_download"  :key_element.find("enclosure").get('url'),
                "url_engine"    :self.url,
                "url_magnet"    :"",
            }
        except:
            self.log_Fatal(traceback.format_exc())    
            return []

    def custom_getURL(self, pageNum):
        try:
            newWhat = self.search_whatNorm
            if( self.search_cat !="all"):
                newWhat += "+category:"+self.search_cat
            parms = {"q":newWhat,
                     "fmt":"rss"}
            if( pageNum!=1):
                parms ['pg'] = pageNum
            return self.baseurl % self.urlencode(parms) 
        except: 
            self.log_Fatal(traceback.format_exc())
            return False
        
    def custom_pageProcess2(self, url, root):
        channel = root.find("channel")            
        totalResults = channel.find("{http://a9.com/-/spec/opensearch/1.1/}totalResults").text
        startIndex = channel.find("{http://a9.com/-/spec/opensearch/1.1/}startIndex").text
        itemsPerPage = channel.find("{http://a9.com/-/spec/opensearch/1.1/}itemsPerPage").text
        totalResults  = int(totalResults)
        startIndex = int(startIndex)
        itemsPerPage = int(itemsPerPage)
        self.log('reading remote Page %s total resuls %d startindex = %d itemsPerPage = %d' % (url, totalResults, startIndex, itemsPerPage))
        if(  startIndex  + itemsPerPage > totalResults ):
            return False
        return True
