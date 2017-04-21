#VERSION: 1.0
from engines._x1_common import basePlugin
import traceback
class aakickass(basePlugin):
    url = 'http://AA-kickasstorrents.to/'
    name = 'AA-KickAssTorrents'
    baseurl = 'https://katcr.co/new/torrents-search.php?%s'
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
    keyElementDesc = ".//tr[@class='t-row']"
    cfg_engine ={
        "search_encodeAscii":True,
        "search_decode":False,
    }

    def custom_eltToArray(self, key_element):
        try:
            name_Anchor = key_element.find(".//div[@class='torrentname']/div/a")
            name = "".join(name_Anchor.itertext())
            download_anchor =key_element.find(".//a[@title='Download torrent file']")
            download_url ="https://katcr.co/new/" + download_anchor.get('href')
            localid = self.util_middle(download_url, "id=", "&")
            url_desc = "https://katcr.co/new/" + name_Anchor.get("href")
            
            bthash = "" 
            if( "&name=" in download_url):
                filename = download_url.split("&name=")[1].split(".")[0].lower()
                if len(filename)==40:
                    isHex = True
                    for eachChar in filename:
                        isHex=isHex and (eachChar in "0123456789abcdef")
                    if( isHex):
                        bthash = filename
            return {
                "name"          :name,
                "size"          :key_element.find("./td[2]").text,
                "bthash"        :bthash,
                "leech"         :key_element.find("./td[5]/font").text,
                "seeds"         :key_element.find("./td[4]/font").text,
                "localid"       :localid,
                "url_desc"      :url_desc,
                "url_download"  :download_url,
                "url_engine"    :self.url,
                "url_magnet"    :"",
            }
        except: 
            self.log_Fatal(traceback.format_exc())
            return []

    def custom_getURL(self, pageNum):
        try:
            parms = {
                "search":self.search_whatNorm,
                "cat":self.search_cat,
                "sort":"seeders",
                "order":"desc",
                "lang":"0",
            }
            if( pageNum>1):
                parms["page"] = pageNum-1
            return self.baseurl % self.urlencode(parms)
        except: 
            self.log_Fatal(traceback.format_exc())
            return False       

    def custom_download(self):
        try:
            root = self.url_to_treeroot(self.curitem.url_desc)
            self.curitem.url_magnet = root.find(".//a[@title='Magnet link']").get("href")
            self.curitem.set_bthash(self.magnetTobthash(self.curitem.url_magnet))
            self.localid_set_bthash()
            return  self.download_torrent_altsites()
        except: 
            self.log_Fatal(traceback.format_exc())
