#VERSION: 1.0
from engines._x1_common import basePlugin
import traceback
class aapiratebay(basePlugin):
    url = "http://AA-thepiratebay.org"
    name = "AA-The Pirate Bay"
    baseurl = "https://thepiratebay.org/search/%s/%s/%s/%s"
    supported_categories = {
        'all'       : '0',
#       'anime'     : '',
#       'books'     : '',
        'games'     :'400',
        'movies'    :'200',
        'music'     :'100',
        'software'  :'300'
#       'tv'        : '',
    }
    keyElementDesc = ".//table[@id='searchResult']/tr"
    cfg_engine ={

    }
    
    def custom_eltToArray(self, key_element):
        try:
            desc_anchor = key_element.find(".//div/a")
            magnet_Anchor = key_element.find(".//a[@title='Download this torrent using magnet']")
            sizeRawText = key_element.find(".//font[@class='detDesc']").text
            size = sizeRawText.split("Size ")[1].split(",")[0]
            size = size.replace("iB","B")
            return {
                "name"          :desc_anchor.text,
                "size"          :size,
                "bthash"        :"",
                "leech"         :key_element.find("./td[4]").text,
                "seeds"         :key_element.find("./td[3]").text,
                "url_desc"      :desc_anchor.get('href'),
                "url_download"  :"",
                "url_engine"    :self.url,
                "url_magnet"    :magnet_Anchor.get('href')
            }
        except:
            self.log_Fatal(traceback.format_exc())    
            return []
        
    def custom_getURL(self, pageNum):
        try:
            search = self.search_whatQuote
            pageNum = pageNum -1
            order = "7"
            return self.baseurl % (search,pageNum,order, self.search_cat)  
        except: 
            self.log_Fatal(traceback.format_exc())
            return False
