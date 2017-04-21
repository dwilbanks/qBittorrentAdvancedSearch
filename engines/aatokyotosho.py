#VERSION: 1.0
from engines._x1_common import basePlugin
import traceback
class aatokyotosho(basePlugin):
    url = "http://AA-tokyotosho.info"
    name = "AA-Tokyotosho"
    baseurl = "http://tokyotosho.info/search.php?%s"
    supported_categories = {
        'all'       : '0',
        'anime'     : '1',
#       'books'     : '',
        'games'     : '14',
#       'movies'    : '',
        'music'     : '2',
#       'pictures'  : '',
#       'software'  : '',
#       'tv'        : ''
    }
    keyElementDesc = ".//td[@class='desc-top']/.."
    cfg_engine ={

    }
    urls = {}
        
    def custom_eltToArray(self, key_element):
        try:
            firstRow = key_element;
            secondRow =firstRow.getnext()
            desc_anchor = firstRow.find(".td[2]/a[2]")
            url_magnet = firstRow.find(".td[2]//a[1]").get('href');
            name = "".join(desc_anchor.itertext())
            url_download =desc_anchor.get('href')        
            sizeContainer =secondRow.find("./td[@class='desc-bot']")
            sizeOuterText = "".join(sizeContainer.itertext())
            size = sizeOuterText.split("Size: ")[1].split(" |")[0]
            size = size.replace("MB"," MB")
            size = size.replace("GB"," GB")
            size = size.replace("KB"," KB")
            size = size.replace("TB"," TB")
            url_desc = firstRow.find(".//td[@class='web']/a[@rel='nofollow']").get('href')
            url_desc = "http://tokyotosho.info/" + url_desc 
            url_magnet = url_magnet + "&dn=" +name
            return {
                "name"          : name,
                "size"          : size,
                "bthash"        : "",
                "leech"         : secondRow.find("./td[2]/span[2]").text,
                "seeds"         : secondRow.find("./td[2]/span[1]").text,
                "url_desc"      : url_desc,
                "url_download"  : url_download,
                "url_engine"    : self.url,
                "url_magnet"    : url_magnet,
            }
            
        except:
            self.log_Fatal(traceback.format_exc())
            return []       

    def custom_getURL(self, pageNum):
        try:
            if( str( pageNum) in self.urls):
                return self.urls[str( pageNum)]
            parms = {
                "terms":self.search_whatNorm,
                "type":self.search_cat, 
                "size_min":"",
                "size_max":"",
                "username":"",
            }
            return self.baseurl % self.urlencode(parms)            
        except:
            self.log_Fatal(traceback.format_exc())    
            return False
        
    def custom_pageProcess2(self, url, root):
        pagexpath = ".//p[@style='text-align: center; font-size: 18pt']/a"
        pageLinks = root.findall(pagexpath)
        self.log("Found %d pages" % len(pageLinks ))
        for anchor in pageLinks:
            parms  =anchor.get('href').split("?")[1]
            page = anchor.text
            self.urls[page] = self.baseurl % parms   
        return True

