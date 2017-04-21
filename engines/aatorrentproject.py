#VERSION: 1.0
from engines._x1_common import basePlugin
import traceback
class aatorrentproject(basePlugin):
    url = "http://AA-torrentproject.se/"
    name = "AA-Torrentproj"
    baseurl = "http://torrentproject.se/?%s"
    supported_categories = {
        'all'       : '',
#        'anime'     : '',
#        'books'     : '',
#        'games'     : '',
#        'movies'    : '',
#        'music'     : '',
#        'pictures'  : '',
#        'software'  : '',
#        'tv'        : ''
    }
    keyElementDesc = ".//div[@id='similarfiles']/div/span[5]/.."
    cfg_engine ={
        "searchURLsort":"seeders",
    }
    
    def custom_eltToArray(self, key_element):
        try:
            url_desc = key_element.find(".//a[1]").get('href');
            url_desc = url_desc.replace("\\\'","")
            bthash = url_desc.split("/")[1]
            url_desc =  "http://torrentproject.se"+url_desc
            name = key_element.find(".//a[1]").text
            url_download = "http://torrentproject.se/torrent/%s.torrent" % bthash.upper()  
            url_magnet = "magnet:?xt=urn:btih:{}&dn={}".format( bthash ,name)
            return {
                "name"          : name,
                "size"          : key_element.find("./span[5]").text,
                "bthash"        : bthash,
                "leech"         : key_element.find("./span[3]").text ,
                "seeds"         : key_element.find("./span[2]").text,
                "url_desc"      : url_desc,
                "url_download"  : url_download,
                "url_engine"    : self.url,
                "url_magnet"    : url_magnet,
            }
        except:
            self.log_Fatal(traceback.format_exc())    
            return []        
                
    def custom_getURL(self, pageNum):
        try:
            parms = {
                "t":self.search_whatNorm,
                "orderby":self.prop("searchURLsort"),
                "safe":"off",
                }
            if( pageNum>1):
                parms["p"] = pageNum+1
            return self.baseurl % self.urlencode(parms)
        except:
            self.log_Fatal(traceback.format_exc())    
            return False
