#VERSION: 1.0
from engines._x1_common import basePlugin
import traceback

class aararbghtml(basePlugin):
    url = 'http://AA-rarbg.to'
    name = 'AA-rarbg'
    baseurl = "https://rarbg.to/torrents.php?%s"
    supported_categories = {
        'all'       : "",
        'games'     : '1;27;28;29;30;31;32;40',
        'music'     : '1;23;24;25;26',
        'tv'        : '1;18;41;49',
        }
    cfg_engine ={       "usemagnet":"never"    }
    keyElementDesc = ".//table[@class='lista2t']//tr[@class='lista2']"
    urls = {}
    
    def custom_eltToArray(self, key_element):
        try:
#  .//table[@class='lista2t']//tr[@class='lista2']/td[2]/a            
            desc_Anchor = key_element.find("./td[2]/a")
            name =desc_Anchor.text 
            url_desc = desc_Anchor.get("href")
            key =url_desc.split("/")[2]
            mouseOver = desc_Anchor.get("onmouseover")
            bthash = mouseOver.split("/over/")[1].split(".")[0]
            url_download = "https://rarbg.to/download.php?id=%s&f=%s.torrent" % (key, bthash)
            return {
                "name"          : name,
                "size"          : key_element.find("./td[4]").text,
                "bthash"        : bthash,
                "leech"         : key_element.find("./td[6]").text,
                "seeds"         : key_element.find("./td[5]/font").text,
                "url_desc"      : url_desc,
                "url_download"  : url_download,
                "url_engine"    : self.url,
                "url_magnet"    : "",
            }
        except: 
            self.log_Fatal(traceback.format_exc())
            return []
        
    def custom_getURL(self, pageNum):
        try:
            if( str( pageNum) in self.urls):
                return self.urls[str( pageNum)]
            parms = {
                "search":self.search_whatNorm,
            }
            return self.baseurl % self.urlencode(parms)
        except: 
            self.log_Fatal(traceback.format_exc())
            return False

    def custom_pageProcess2(self, url, root):
        try:        
            pageLinks = root.findall(".//div[@id='pager_links']/a")
            self.log("Found %d pages" % len(pageLinks ))
            for anchor in pageLinks:
                parms  =anchor.get('href').split("?")[1]
                page = anchor.text
                self.urls[page] = self.baseurl % parms
        except: 
            self.log_Fatal(traceback.format_exc())
    
