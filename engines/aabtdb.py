#VERSION: 1.0
from engines._x1_common import basePlugin
import traceback
class aabtdb(basePlugin):
    url = 'https://AA-btdb.in'
    name = 'AA-BTDB'
    baseurl = 'https://btdb.in/q/'
    supported_categories = {
        'all'       : '0',
        'anime'     : '1',
        'books'     : '2',
        'games'     : '3',
        'movies'    : '4',
        'music'     : '5',
        'pictures'  : '6',
        'software'  : '7',
        'tv'        : '8'
    }
    keyElementDesc = ".//h2[@class='item-title']/.."
    cfg_engine ={
        "search_encodeAscii":True,
        "search_decode":False,
    }

    def custom_eltToArray(self, key_element):
        try:
            name_Anchor = key_element.find(".//h2[@class='item-title']/a")
            magnet_Acnchor = key_element.find(".//a[@class='magnet']")
            size_div = key_element.find("./div/span[1]")
            if name_Anchor == None:
                return
            if name_Anchor == None:
                return []
            if name_Anchor == None:
                return []
            
            
             
            name = "".join(name_Anchor.itertext())
            return {
                "name"          :name,
                "size"          :size_div.text,
                "bthash"        :"",
                "leech"         :"",
                "seeds"         :"",
                "localid"       :"",
                "url_desc"      :name_Anchor.get("href"),
                "url_download"  :"",
                "url_engine"    :self.url,
                "url_magnet"    :magnet_Acnchor.get("href"),
            }
        except: 
            self.log_Fatal(traceback.format_exc())
            return []

    def custom_getURL(self, pageNum):
        try:
            url =self.baseurl + self.search_whatQuote
            if( pageNum>1):
                url += "/" + str(pageNum) 
            return url
        except: 
            self.log_Fatal(traceback.format_exc())
            return False       

