#VERSION: 1.0
from engines._x1_common import basePlugin
import traceback
class aaextra(basePlugin):
    url = "http://AA-extra.to"
    name = "AA-Extra"
    baseurl = "https://extra.to/search/?%s"
    supported_categories = {
        'all'       : '0',
        'anime'     : '1',
        'books'     : '2',
        'games'     : '3',
        'movies'    : '4',
        'music'     : '5',
        'pictures'  : '6',
        'software'  : '7',
        'tv'        : '8',
    }
    keyElementDesc = ".//a[@title='Magnet link']"
    cfg_engine ={
        "searchURLsort":"leechers",
    }

    def custom_eltToArray(self, key_element):
        try:
            row = key_element.getparent().getparent()
            desc_Anchor  = row.find("./td[3]/a")
            name = "".join(desc_Anchor.itertext())
            url_desc = "http://extra.to"+ desc_Anchor.get("href")
            url_download = "http://extra.to"+ row.find(".//a[1]").get("href")
            return {
                "name"          :name,
                "size"          :row.find("./td[5]").text,
                "bthash"        :"",
                "leech"         :row.find("./td[7]").text,
                "seeds"         :row.find("./td[6]").text,
                "url_desc"      :url_desc,
                "url_download"  :url_download,
                "url_engine"    :self.url,
                "url_magnet"    :key_element.get("href"),
            }
        except: 
            self.log_Fatal(traceback.format_exc())
            return []
        
    def custom_getURL(self, pageNum):
        try:
            parms = {
                "search":self.search_whatNorm,
                "s_cat":self.search_cat,
                "srt":self.prop("searchURLsort"),
                "pp":"50",
                "order":"desc",
                "page":pageNum,
            }
            return self.baseurl % self.urlencode(parms)
        except: 
            self.log_Fatal(traceback.format_exc())
            return False       
