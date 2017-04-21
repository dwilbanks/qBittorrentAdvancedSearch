#VERSION: 1.0
from engines._x1_common import basePlugin
import traceback
class aademonoid(basePlugin):
    url = "http://AA-demonoid.pw"
    name = "AA-Demonoid"
    baseurl = "https://www.demonoid.pw/files/?%s"
    supported_categories = {
        'all'       : '0',
        'anime'     : '9',
        'books'     : '11',
        'games'     : '4',
        'movies'    : '1',
        'music'     : '2',
#        'pictures'  : '',
        'software'  : '5',
        'tv'        : '3'
    }
    keyElementDesc = ".//img[@title='Download as torrent']/../../.."
    
    cfg_engine ={
        "searchURLseeded":"2",
        "searchURLexternal":"2",
        "searchURLsubcategory":"All",
        "searchURLquality":"All",
        "searchURLsort":"",
    }
    
    def custom_eltToArray(self, key_element):
        try:
            FirstRow = key_element.getprevious()
            if( FirstRow==None):
                self.log("FAIL")
                return False
            magnet_anchor = key_element.find(".td[3]//img[@title='Download as magnet']/..")
            download_anchor= key_element.find("./td[3]/a[1]")
            desc_anchor = FirstRow.find("td[2]/a")
            return {
                "name"          : FirstRow.find("td[2]/a").text,
                "size"          : key_element.find("./td[4]").text,
                "bthash"        :"",
                "leech"         : key_element.find("./td[8]/font").text,
                "seeds"         : key_element.find("./td[7]/font").text,
                "url_desc"      : desc_anchor.get("href"),
                "url_download"  : download_anchor.get("href"),
                "url_engine"    : self.url,
                "url_magnet"    : magnet_anchor.get("href"),
            }
        except:
            self.log_Fatal(traceback.format_exc())    
            return []
        
    def custom_getURL(self, pageNum):
        try:
            parms = {
                "category":self.search_cat,
                "subcategory":self.prop("searchURLsubcategory"),
                "quality" :self.prop("searchURLquality"),
                "seeded" : self.prop("searchURLseeded"),
                "external" : self.prop("searchURLexternal"),
                "query" : self.search_whatNorm,
                "uid":0,
                "sort" :self.prop("searchURLsort"),
            }
            if( pageNum>1):
                parms["page"] = pageNum
            return self.baseurl % self.urlencode(parms)
        except:
            self.log_Fatal(traceback.format_exc())    
            return False
