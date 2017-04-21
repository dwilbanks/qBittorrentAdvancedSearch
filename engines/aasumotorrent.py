#VERSION: 1.0
from engines._x1_common import basePlugin
import traceback
class aasumotorrent(basePlugin):
    url = 'http://AA-sumotorrent.sx'
    name = 'AA-Sumotorrent'
    baseurl = 'http://www.sumotorrent.sx/en/search/'
    supported_categories = {
        'all'       : '',
        'anime'     : '8',
#       'books'     : '',
        'games'     : '2',
        'movies'    : '4',
        'music'     : '0',
#       'pictures'  : '',
        'software'  : '1',
        'tv'        : '9',
    }
    keyElementDesc = ".//td[@class='trow']/font[@color='#008000']/../.."
    cfg_engine ={}
    
    def custom_eltToArray(self, key_element):
        try:
            detail_anchor = key_element.find("./td[3]//a")
            name = "".join(detail_anchor.itertext())
            download_anchor = key_element.find("./td[5]//a")
            size = key_element.find("./td[6]").text
            size = size.replace("\\n","").replace("\\t","")
            
            
            dowloadParts = download_anchor.get("href").split("/");
            localid =dowloadParts[-3] 
            strdate = dowloadParts[-2]
            fileName = self.quote(dowloadParts[-1]).replace('%20', '+')
            
            url_dowload = 'http://torrents.sumotorrent.sx/torrent_download/%s/%s/%s'
            url_dowload = url_dowload % ( localid ,strdate ,fileName)
            
            url_desc = detail_anchor.get('href')
            url_desc = url_desc.replace("XXX/","")
            return {
                "name"          :name,
                "size"          :size,
                "bthash"        :"",
                "localid"       :download_anchor.get("href").split("/")[4],
                "leech"         :key_element.find("./td[8]/font").text,
                "seeds"         :key_element.find("./td[7]/font").text,
                "url_desc"      :url_desc,
                "url_download"  :url_dowload,
                "url_engine"    :self.url,
                "url_magnet"    :""
            }
        except:
            self.log_Fatal(traceback.format_exc())    
            return []

    def custom_getURL(self, pageNum):
        try:
            newWhat = self.search_whatNorm.lower()
            newWhat = newWhat.replace(" ","-")
            url  = self.baseurl + newWhat 
            if( pageNum!=1):
                url += "?start=" + str(pageNum-1)
            return url   
        except: 
            self.log_Fatal(traceback.format_exc())
            return False

    def custom_download(self):
        try:
            if self.curitem.hashIsValid():
                return 
            self.log("Reading description" +self.curitem.url_desc)
            root = self.url_to_treeroot(self.curitem.url_desc)
            try:
                self.curitem.magnet_url = root.find(".//img[@src='/img/ico_magnet.jpg']/..").get('href')
                self.curitem.set_bthash(self.magnetTobthash( self.curitem.magnet_url))
            except:
                pass
            if not self.curitem.hashIsValid():            
                self.log("No bthash in magnet")
                try:
                    newBTHash = root.xpath(".//table[@id='bits']/tbody/tr/td[.='Hash']")[0].getnext().text
                    self.curitem.set_bthash(newBTHash)
                except:
                    pass
            if not self.curitem.hashIsValid():
                return 
            self.localid_checkbthash()
            return self.download_torrent_altsites()
        except:
            return
