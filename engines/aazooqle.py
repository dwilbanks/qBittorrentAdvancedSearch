#VERSION: 1.0
from engines._x1_common import basePlugin
import traceback
from engines._aazooqlexml import aazooqlexml
from engines._aazooqlehtml import aazooqlehtml


class aazooqle(basePlugin):
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
    keyElementDesc = ".//item"
    cfg_engine ={
        "UseEngine":"html"
    }    

    def download_torrent(self, fullURL):
        try:
            if( self.prop("UseEngine") =="html" ):
                engine = aazooqlehtml()
                
            else:
                engine = aazooqlexml()
            return engine.download_torrent(fullURL)
        except:
            self.log_Fatal(traceback.format_exc())    
            return False

    def search(self, what, cat="all"):
        try:
            if( self.prop("UseEngine") =="html" ):
                engine = aazooqlehtml()
            else:
                engine = aazooqlexml()                
            engine.search(what, cat);
        except:
            self.log_Fatal(traceback.format_exc())    
            return False