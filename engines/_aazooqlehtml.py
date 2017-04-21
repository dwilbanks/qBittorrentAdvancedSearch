#VERSION: 1.0
from engines._x1_common import basePlugin
import traceback
class aazooqlehtml(basePlugin):
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
    keyElementDesc = ".//table[@class='table table-condensed table-torrents vmiddle']/tr/td/a/../.."
    cfg_engine ={
         "ignoreZeroByte":True,
    }
    def custom_eltToArray(self, key_element):
        try:
            desc_Anchor = key_element.find("td[2]/a");
            name = "".join(desc_Anchor.itertext())
            
            magnet_anchor = key_element.find("td[3]//i[@class='spr dl-magnet']/..")
            if  magnet_anchor==None:
                url_magnet = ""
            else:
                url_magnet = magnet_anchor.get("href") 
            download_anchor = key_element.find("td[3]//i[@class='spr dl-generate']/..")
            if download_anchor==None:
                url_download = ""
            else:
                url_download = download_anchor.get("href")
                
                
            size_div = key_element.find("td[4]/div/div")
            if size_div==None:
                size = ""
            else:
                size = size_div.text
                size = size[:-1]
                
            leech_div =key_element.find("td[6]/div/div[2]")
            if leech_div == None:
                leach = ""
            else:
                leach = leech_div.text
            seeds_div =key_element.find("td[6]/div/div[1]")
            if seeds_div == None:
                seeds = ""
            else:
                seeds = seeds_div.text
            return {
                "name"          :name,
                "size"          :size,
                "bthash"        :self.magnetTobthash(url_magnet),
                "leech"         :leach,
                "seeds"         :seeds,
                "url_desc"      :desc_Anchor.get('href'),
                "url_download"  :url_download,
                "url_engine"    :self.url,
                "url_magnet"    :url_magnet,
            }
        except:
            self.log_Fatal(traceback.format_exc())    
            return []

    def custom_getURL(self, pageNum):
        try:
            newWhat = self.search_whatNorm
            if( self.search_cat !="all"):
                newWhat += "+category:"+self.search_cat
            parms = {"q":newWhat}
            if( pageNum!=1):
                parms ['pg'] = pageNum
            return self.baseurl % self.urlencode(parms) 
        except: 
            self.log_Fatal(traceback.format_exc())
            return False
   
