#VERSION: 1.0
from engines._x1_common import basePlugin
import traceback
from engines._aararbgjson import aararbgjson
from engines._aararbghtml import aararbghtml


class aararbg(basePlugin):
    url = 'http://AA-rarbg.to'
    name = 'AA-Rarbg'
    supported_categories = {
        'all'       :  '',
#        'anime'     : 'Anime',
#        'books'     : 'Books',
        'games'     : '1;27;28;29;30;31;32;40',
#       'movies'    : '',
        'music'     : '1;23;24;25;26',
#       'pictures'  : '',
#       'software'  : '',
        'tv'        : '1;18;41;49',
    }
    cfg_engine ={
        "UseJSONEngine":True
    }    

    def download_torrent(self, fullURL):
        try:
            if( self.prop("UseJSONEngine") ):
                engine = aararbgjson()
            else:
                engine = aararbghtml()
            return engine.download_torrent(fullURL)
        except:
            self.log_Fatal(traceback.format_exc())    
            return False

    def search(self, what, cat="all"):
        try:
            if( self.prop("UseJSONEngine") ):
                engine = aararbgjson()
            else:
                engine = aararbghtml()
            engine.search(what, cat);
        except:
            self.log_Fatal(traceback.format_exc())    
            return False