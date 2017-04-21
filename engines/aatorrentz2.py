#VERSION: 1.0
from engines._x1_common import basePlugin
import traceback
class aatorrentz2(basePlugin):
    url = 'http://AA-torrentz2.eu'
    name = 'AA-Torrentz2'
    baseurl = 'https://torrentz2.eu/search?%s'
    supported_categories = {
        'all'       : '',
#        'anime'     : '',
#        'books'     : '',
#        'games'     : '',
#        'movies'    : '',
#        'music'     : '',
#        'pictures'  : '',
#        'software'  : '',
#        'tv'        : '',
    }
    keyElementDesc = ".//div[@class='results']/dl"
    cfg_engine ={

    }
    

    def custom_eltToArray(self, key_element):
        try:
            desc_Anchor = key_element.find(".//a[1]")
            url_desc = desc_Anchor.get('href')
            bthash = url_desc[1:]
            return {
                "name"          :key_element.find(".//a[1]").text,
                "size"          :key_element.find("./dd/span[3]").text,
                "bthash"        :bthash,
                "leech"         :key_element.find("./dd/span[4]").text,
                "seeds"         :key_element.find("./dd/span[5]").text,
                "url_desc"      :url_desc,
                "url_download"  :"",
                "url_engine"    :self.url,
                "url_magnet"    :""
            }
        except:
            self.log_Fatal(traceback.format_exc())    
            return []
             
    def custom_getURL(self, pageNum):
        try:
            parms = {
                "f":self.search_whatNorm,
                "p":pageNum, 
            }
            return self.baseurl % self.urlencode(parms)   
        except: 
            self.log_Fatal(traceback.format_exc())
            return False
