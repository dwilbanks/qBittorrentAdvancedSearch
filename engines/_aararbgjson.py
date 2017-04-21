#VERSION: 1.0
from engines._x1_common import basePlugin
import traceback

class aararbgjson(basePlugin):
    url = 'http://AA-rarbg.to'
    name = 'AA-rarbg'
    baseurl = "https://torrentapi.org/pubapi_v2.php?%s"
    token = None
    supported_categories = {
        'all'       : "1;4;14;15;16;17;21;22;42;18;19;41;27;28;29;30;31;32;40;23;24;25;26;33;34;43;44;45;46;47;48",
        'games'     : '1;27;28;29;30;31;32;40',
        'music'     : '1;23;24;25;26',
        'tv'        : '1;18;41;49',
        }
    keyElementDesc ="torrent_results"
    cfg_engine ={
        "search_decode":False,
        "search_dataType":"json",
        "searchPageEnd":1,
    }
    def getToken(self):
        try:
            if self.token == None:
                params = self.urlencode({'get_token': 'get_token'})
                jsonData = self.url_to_json(self.baseurl % params)
                if 'token' in jsonData:
                    self.token = jsonData['token']
                else:
                    self.token = False
            return self.token
        except: 
            self.log_Fatal(traceback.format_exc())        
                
    def custom_pageProcess2(self,url, root):
        if( len(root[self.keyElementDesc]) < 100):
            return False
        return True
        
    def custom_eltToArray(self, key_element):
        try:
            bthash = self.magnetTobthash(key_element['download'])
            name = key_element['title']
            return {
                "name"          :name,
                "size"          :str(key_element['size']),
                "bthash"        :bthash,
                "leech"         :key_element['leechers'],
                "seeds"         :key_element['seeders'],
                "url_desc"      :key_element['info_page'],
                "url_download"  :"",
                "url_engine"    :self.url,
                "url_magnet"    :key_element['download'],
            }
        except: 
            self.log_Fatal(traceback.format_exc())
            return []
                    
    def custom_getURL(self, pageNum):
        try:            
            token = self.getToken();
            if token == False:
                return ""
            parms = {
                'mode': 'search',
                'search_string': self.search_whatNorm,
                'ranked': 0,
                'category': self.search_cat,
                'limit': 100,
                'sort': 'seeders',
                'format': 'json_extended',
                'token': self.getToken()
            }
            if pageNum==1:
                parms['sort'] = 'seeders'
            elif pageNum==2:
                pageNum['sort'] = "last"
            elif pageNum==3:
                pageNum['sort'] = "leechers"
            else:
                return "";    
            return self.baseurl % self.urlencode(parms)

        except: 
            self.log_Fatal(traceback.format_exc())
