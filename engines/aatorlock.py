#VERSION: 1.0
from engines._x1_common import basePlugin
import traceback

class aatorlock(basePlugin):
    url = 'http://AA-torlock.com'
    name = 'AA-Torlock'
    baseurl = 'https://www.torlock.com/%s/torrents/%s.html?%s'
    supported_categories = {
        'all'       : 'all',
        'anime'     : 'anime',
        'books'     : 'ebooks',
        'games'     : 'game',
        'movies'    : 'movie',
        'music'     : 'music',
#       'pictures'  : '',        
        'software'  : 'software',
        'tv'        : 'television',
    }
    keyElementDesc = ".//div[@class='panel panel-default']//tr"
    cfg_engine ={
        "searchURLsort":"seeds",
    }

    def custom_eltToArray(self, key_element):
        try:
            desc_anchor = key_element.find(".//a[1]")
            name = "".join(desc_anchor.itertext())
            url_desc = desc_anchor.get("href")
            localid = url_desc.split("/")[2]
            url_download = "https://www.torlock.com/tor/%s.torrent" % ( localid) 
            return {
                "name"          :name,
                "size"          :key_element.find("td[@class='ts']").text,
                "bthash"        :"",
                "leech"         :key_element.find("td[@class='tdl']").text,
                "seeds"         :key_element.find("td[@class='tul']").text,
                "localid"       :localid,
                "url_desc"      :url_desc,
                "url_download"  :url_download,
                "url_engine"    :self.url,
                "url_magnet"    :"",
            }
        except: 
            self.log_Fatal(traceback.format_exc())
            return []

    def custom_getURL(self, pageNum):
        try:
            searchwhat = self.search_whatNorm.lower()
            searchwhat = searchwhat.replace(" ", "-")
            searchwhat = searchwhat.replace("%20", "-")
            parms = {
                "sort":self.prop("searchURLsort"),
            }
            if( pageNum>1):
                parms["page"] = pageNum
            url = self.baseurl %  (self.search_cat,searchwhat,self.urlencode(parms))
            return url
        except: 
            self.log_Fatal(traceback.format_exc())
            return False        
