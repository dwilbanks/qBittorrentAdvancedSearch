import traceback
import os.path
import requests
import json
import time 
import uuid
import tempfile
import io
import sys
import base64
import sqlite3
# import logging

from engines._x1_bdecode import Bdecode
from engines._x1_filelock import FileLock ,FileLockException
from engines._x1_v1k45QBClient import v1k45LoginRequired, v1k45Client
from novaprinter import prettyPrinter, anySizeToBytes
try:
    from urllib.parse import unquote, quote, urlencode
except ImportError:
    from urllib import unquote, quote, urlencode


try:
    from lxml import etree    
except ImportError:    
    from lxml import etree

class Logger():
    pass

logHistory = []

class torrentFile():
    engine = None
    isValid = False
    fileHandle = None
    path = None
    torContents = None
    logText = ""
    url_magnet = None
    bthash = None
    log_mode = 0
    readURLS = []
    redirBlackListURLS=[
        "https://www.limetorrents.cc"
        ]
    redirBlackListParts=[]
    def __init__(self, engine):
        self.engine = engine

    def log(self, value):
        self.engine.log(value)

    def _setDefaults(self):
        self.isValid = False
        self.fileHandle = None
        self.path = None
        self.torContents = None
        self.logText = ""
        self.url_magnet = None
        
    def url_to_torrent(self, url):
        self._setDefaults()
        
        if( url==None):
            return self.isValid
        if( url==""):
            return self.isValid
        
        redirCount = 0
        while redirCount < 3:
            if url in self.readURLS:
                self.log( "Already read " + url)                
                return self.isValid
            if url in self.redirBlackListURLS:
                self.log( "Blacklisted URL " + url)                
                return self.isValid
            for blacklistPart in self.redirBlackListParts:
                if blacklistPart in url:
                    self.log( "Blacklisted URL '%s' contains '%s'", url,blacklistPart)                
                    return self.isValid

            self.log( "reading url " + url)
            req = requests.get(url, allow_redirects=False)
            self.readURLS.append(url)
            
            self.log("req.status_code")
            self.log(req.status_code )
            if req.status_code == 302:
                newURL = req.headers['location']
                self.log( "redirect url is (%s) " % newURL)
                if newURL.startswith("magnet:"):
                    self.url_magnet = newURL
                    return False
                url = newURL
                redirCount = redirCount +1
            elif req.status_code == 200:
                torr = Bdecode()
                try:
                    torr.read_contents( req.content)
                    self.bthash = torr.info_hash.lower()
                    self.isValid = True
                    self.torContents = req.content
                except ValueError:
                    pass
                return self.isValid
            else:
                self.log("req.status_code")
                self.log(req.status_code )
                return self.isValid

    def getFileName(self):
        if not self.isValid:
            return ""
        if  self.path == None:
            osfileHandle, self.path = tempfile.mkstemp(".torrent")
            fileHandle = os.fdopen(osfileHandle, "wb")
            fileHandle.write(self.torContents)
            fileHandle.close()
        return self.path
        
    
    
    def getInfohash(self):
        torr = Bdecode()
        try:
            torr.read_filename(self.path)
            return torr.info_hash.lower()
        except ValueError:
            return ""            
        
        
        
class util(object):
    def unquote(self, string, encoding='utf-8', errors='replace'):
        return unquote(string, encoding, errors) 
    
    def quote(self, string, safe='/', encoding=None, errors=None):
        return quote(string, safe, encoding, errors)           
    
    def urlencode(self, query, doseq=False, safe='', encoding=None, errors=None):
        return urlencode(query, doseq, safe, encoding, errors)

    def util_middle(self, haystack, start, end):
        if not start in haystack:
            return ""
        return haystack.split(start)[1].split(end)[0]

class basePlugin(util):
    cfg = {
        "Connection.Proxy.IP":"127.0.0.1",
        "Connection.Proxy.Password":"",
        "FileLogger.Path":"""D:\qbittorrent\Logs""",
        "WebUI.Enabled":True,
        "WebUI.HTTPS.Enabled":False,
        "WebUI.LocalHostAuth":True,
        "WebUI.Password":"admin",
        "WebUI.Port":"8080",
        "WebUI.Username":"admin",
    }
    cfg_types = {
        "searchHave":["ignore","mark","norm"],
        "searchzerobytes":["norm","ignore"],
        "usemagnet":["never","norm","always"],
        "download_alt_1" : str,
        "download_alt_2" : str,
        "download_alt_3" : str,
        "download_alt_4" : str,
        "download_alt_5" : str,
        "download_alt_6" : str,
        "download_alt_7" : str,
        "download_alt_8" : str,
        "download_alt_9" : str,
        "searchResultsMax":int,
        "searchPageStart":int,
        "searchPageEnd":int,
        "autodownload":bool,
        "search_dataType":["json","xml","html"],
        "search_decode":bool,
        "search_encodeAscii":bool,
        "search_UseText":bool,
        "search_logToFile":bool,
        "logmode":["norm","verbose"],
        "archive_action":["norm","ignore","mark"],
        "action":["console","search","download"],
        "search_sortby":["leachers","seeders","size","age"],        
    }
    
           
    
    cfg_base = {
        "action":"console",
        "autodownload":False,
        "archive_action":"ignore",
        "archive_dir":"D:/tor/files",
        "download_alt_1" : "http://itorrents.org/torrent/%s.torrent",
        "download_alt_2" : "https://torrentproject.se/torrent/%s.torrent",
        "download_alt_3" : "http://torrasave.site/torrent/%s.torrent",

        "logmode":"norm",
        "minimum_leachers":0,
        "minimum_seeders":0,
        "minimum_size":0,
        "maxium_size":-1,
        "searchResultsMax":300,
        "searchPageStart":1,
        "searchPageEnd":10,
        "searchHave":"ignore",
        "searchMarkHave":"HAVE: %s",
        "archive_marktemplate":"BLACKLIST: %s",
        "searchzerobytes":"norm",
        "search_dataType":"html",
        "search_decode":True,
        "search_encodeAscii":False,
        "search_UseText":True,
        "search_logToFile":False,
        "search_sortby":"leachers",
        "usemagnet":"norm",
    }
    supportedSorts={
        "leachers":"leachers",
        "seeders":"seeders",
        "size":"size",        
        "age":"age",        
    }
    cfg_engine= {}
    engineDir = None;
    torrentIHave = None
    logText = ""
    log_messageCount = 0
    shortname = None
    webUI = None
    logFile = None
    
    loaded = {}
    resultCount = 0
    baseurl = None
    search_whatNorm = None
    search_whatQuote = None
    search_cat = None
    url = None
    curitem = None
    sqlConnection = None
    trackers_list = ['udp://tracker.coppersurfer.tk:6969/announce',
                    'udp://tracker.opentrackr.org:1337/announce',
                    'udp://tracker.zer0day.to:1337/announce',
                    'udp://tracker.leechers-paradise.org:6969/announce',
                    'udp://9.rarbg.com:2710/announce',
                    'udp://explodie.org:6969/announce']

    def _realInit(self):
        if self.engineDir != None:
            return
        try:
            self.engineDir = os.path.dirname(os.path.realpath(__file__))
            self.shortname = self.__class__.__name__.lower()
            self.prop_readConfig()
            self.DL = torrentFile(self)
            self.DL.log_mode =1 
#             logging.basicConfig(level=logging.CRITICAL)          
#             logging.basicConfig(
#                     level=logging.DEBUG,
#                     format='%(asctime)s %(message)s',
#                     datefmt='%m/%d/%Y %I:%M:%S',
#                     filename='/temp/myapp.log',
#                     filemode='a')
        except: 
            self.log_Fatal(traceback.format_exc())      

    def __init__(self):
        pass

    def __del__(self):
        if self.logFile != None:
            self.logFile.close()
        if self.sqlConnection != None:
            self.sqlConnection.close()
            
    def database_init(self):
        if self.sqlConnection != None:
            return
        fileLogger = self.prop("FileLogger.Path")
        path=os.path.join(fileLogger,"Database")
        if not os.path.exists(path):
            os.makedirs(path)
        dbfile = os.path.join( path, self.shortname+'.db' )
        self.sqlConnection = sqlite3.connect(dbfile)
        c = self.sqlConnection.cursor()
        checkTableSQL = "SELECT name FROM sqlite_master WHERE type='table' AND name=?;"
        c.execute(checkTableSQL, ("localids",))
        if c.fetchone()==None:
            c.execute("CREATE TABLE localids (localid text, bthash text)")
            self.sqlConnection.commit()
        c.execute(checkTableSQL, ("history",))
        if c.fetchone()==None:
            c.execute("CREATE TABLE history (url text, timestamp integer, data text)")
            self.sqlConnection.commit()
                
    def localid_checkbthash(self):
        if self.curitem.localid == "":
            return
        if not self.curitem.hashIsValid():
            return
        lu_bthash = self.localid_getbthash()
        if( lu_bthash==""):
            self.localid_set_bthash()
        
    def localid_set_bthash(self, localid= None, bthash=None):
        self.database_init()
        if localid== None:
            localid =self.curitem.localid
        if bthash== None:
            bthash =self.curitem.get_bthash()
        bthash = bthash.lower()
        c = self.sqlConnection.cursor()
        c.execute("INSERT INTO localids VALUES (?,?)",(localid, bthash,))
        self.sqlConnection.commit()

    def localid_getbthash(self, localid = None):
        self.database_init()
        if localid== None:
            localid =self.curitem.localid
        if localid== "":
            return ""
        c = self.sqlConnection.cursor()
        c.execute('SELECT * FROM localids WHERE localid=?', (localid,))
        result= c.fetchone()
        if( result==None):
            return ""
        bthash = result[1].lower()
        if( "0000000000" in bthash):
            return ""
        return bthash
    
    def localid_dump(self):
        print ("dumping")
        self.database_init()
        c = self.sqlConnection.cursor()
        for row in c.execute('SELECT * FROM localids ORDER BY localid'):
            print (row)

    def getelt(self, what, pageNum=1, eltNum = 0):
        self._realInit()
        self.search_filterWhat(what,"all")
        url = self.custom_getURL(pageNum)
        self.log(url)
        root = self.url_to_treeroot(url)
        keyElementsArr = root.findall(self.keyElementDesc)
        return keyElementsArr[eltNum]     
    
    def custom_pageProcess1(self, url, root):
        return True

    def custom_pageProcess2(self, url, root):
        return True

    def download_torrent_url(self ,url):
        self.log( "Inside download_torrent_url-- url='%s' " % url)
        self.DL.url_to_torrent(url)
        if self.DL.isValid:
            return self.DL.isValid
        
        if not self.DL.url_magnet == None:
            self.DL.bthash = self.magnetTobthash(self.DL.url_magnet )
        
        if self.DL.bthash == None:
            return self.DL.isValid
        if self.DL.bthash == self.curitem.get_bthash():
            return self.DL.isValid
        
        if( not self.curitem.hashIsValid()):
            self.log("** The current bthash is empty, we have a new one")
            self.curitem.set_bthash(self.DL.bthash)
            self.localid_checkbthash()                   
            self.download_torrent_altsites()
        return self.DL.isValid
                    
    def download_torrent_tryall(self):
        self.log( "Inside download_torrent_tryall2")
        self.download_torrent_url(self.curitem.url_download)
        if self.DL.isValid:
            return
        self.custom_download()
        if self.DL.isValid:
            return 
        self.download_torrent_altsites()
        return 
    
    def download_listing(self):
        try:
            self.log( "Inside download_listing")
            self.download_torrent_tryall()
            if not self.DL.isValid:
                self.log("DOWNLOAD IS NOT VALID")
                self.curitem.get_url_magnet()
                self.log("url_magent  = '%s'" % self.curitem.url_magnet)
                if len(self.curitem.url_magnet)>0:
                    self.webAPI_download_from_link(self.curitem.url_magnet)
                return
            if self.curitem.localid !="":
                self.log("LocalID found "+str(self.curitem.localid))
                if not self.curitem.hashIsValid():
                    self.curitem.set_bthash(self.DL.bthash)
                    self.localid_checkbthash()
            if not self.prop("WebUI.Enabled"):
                self.log("webui is not enabled")
            self.log("UPLOADING "+self.DL.bthash)
            path = self.DL.getFileName()
            fileHandle = open( path, 'rb')
            if not self.webAPI_download_from_file(fileHandle):
                self.log( "filename was " +path )
            fileHandle.close()
            return
            
            
        except: # catch *all* exceptions
            self.log_Fatal(traceback.format_exc())
            
        
    def download_torrent(self, ExtendedURL):
        self._realInit()
        self.prop_set("action","download")
        self.log( "inside  download_torrent",2)
        self.log( "inside  ExtendedURL = %s" % ExtendedURL,2)
        try:
            
            self.curitem = torrentListing( self)
            ExtendedURL = ExtendedURL.split("|")[0]
            self.curitem.initfromExtendedURL( ExtendedURL)
            self.download_listing()
            filename = self.DL.getFileName()
            returnValue = filename +" "+ExtendedURL
            print (returnValue)
        except: # catch *all* exceptions
            self.log_Fatal(traceback.format_exc())

    def download_torrent_altsites(self, bthash= None):
        self.log( "inside  download_torrent_altsites",2)
        if bthash== None:
            bthash= self.curitem.get_bthash()
        if( len(bthash)==0):
            return
                
        if( len(bthash)!=40):
            self.log( "bthash is not 40 Char Long: Exiting %s" % bthash )
            return 
        count =1
        while count < 10:
            nextURL =self.prop("download_alt_%d" % count )
            if "%s" in str(nextURL):
                self.download_torrent_url(nextURL % bthash)
                if self.DL.isValid:
                    return
            count = count+1
        self.log( "After altsites",2)
        return

    def custom_download(self):
        return

    def download_torrent_normal(self,url, btHash=""):
        filename = self.download_torrent_url(url)
        if(len(filename)==0):
            filename = self.download_torrent_altsites(btHash)
        if(len(filename)>0):
            return filename +" "+url;


    def download_torrent_webUI(self, url, btHash=""):
        self.webAPI_download_from_link(url)
        time.sleep(2)
        torinfo = self.webAPI_get_torrent(btHash)
        if( len(torinfo)==0):
            self.webAPI_download_from_link(url)
        return

    def download_torrent_withLock(self,url,bthash):
        lockName = self.shortname + '_download.lock';
        lockName = os.path.join(self.engineDir,lockName)
        lock = FileLock(lockName,120,.5)
        try:
            with lock:
                result = self.download_torrent_normal( url)
                if( len(result)>0 ):
                    return result
        except FileLockException:
            self.log("Timeout")

    def log(self ,logText, level=0):
        if( not level==0):
            return 
        if( type(logText) != str):
            logText = str( logText)

        
        if self.prop("action")== "console":
            print(logText)
        elif self.prop("action")== "download":
            print(logText)            
            
        lineNum = '{:04d}'.format(self.log_messageCount)             
            
        thisLine = time.strftime("%H:%M:%S", time.gmtime())
        thisLine += " " + lineNum 
        thisLine += " " + logText + "\n"
        if self.prop("logmode") =="norm":
            self.logText = self.logText + thisLine
        else:
            self.log_open();
            self.logFile.write(thisLine)
            for eachLine in logText.split("\n"):
                self.log_toSearchRestult(eachLine)
    
    def log_dumpToFile(self):
        if( self.prop("logmode") =="norm" and self.prop("action") =="search"):
            multiLineArr = self.logText.split("\n")
            for eachLine in multiLineArr:
                self.log_toSearchRestult(eachLine)
        self.log_open();
        self.logFile.write("-------");
        self.logFile.write(self.logText);
        self.logFile.write("-------");
        
    def log_raw(self,rawtext):
        self.log_open();
        self.logFile.write( rawtext )

    def log_Fatal(self,tbText):
        self.log_raw("\n")
        self.log_raw("=================\n")
        self.log_raw("===== FATAL ERROR\n")
        self.log(str("FATAL ERROR:"+tbText))
        self.log_raw("=================\n")
        self.log_dumpToFile()

    def log_open(self):
        if( self.logFile  != None):
            return
        fileLogger = self.prop("FileLogger.Path")
        if( self.shortname==None):
            self.shortname = "Error"
        path=os.path.join(fileLogger,self.shortname)
        if not os.path.exists(path):
            os.makedirs(path)

        if( self.prop("logmode") =="verbose"):
            logName = str(uuid.uuid4()) + '.log';
        else:
            logName = self.shortname + '.log';
        
        logName = os.path.join(path,logName)        
        self.logFile = open( logName, 'a')

    def log_toSearchRestult(self, outputText):
        if self.prop("action")!= "search":
            return

        self.log_messageCount = self.log_messageCount +1
        lineNum = '{:04d}'.format(self.log_messageCount) 
        logtext = self.name + " LOG " + lineNum + " "+ outputText
        result = {
            "engine_url" : self.url,
            "link" : self.url,
            "desc_link" : "about:blank#" +outputText,
            "name" : logtext,
            "size" : "",
            "leech" : "",
            "seeds" : ""
        }
        try:
            prettyPrinter(result)
        except:
            
            result["name"] = "****** ERROR Printing"
            exit()
            prettyPrinter(result)
        
        

    def magnetTobthash(self,url_magnet):
        bthash = url_magnet.split(":btih:")[1].split("&")[0]
        if( len(bthash)==40):
            return bthash.lower()
        try:
            return base64.b32decode(bthash).hex()
        except:
            return ""
        

    def prop(self,name):
        if (name in self.cfg):
            return self.cfg[name]
        return False
     
    def prop_set(self, propName, propValue):
        propName.replace("\\",".")
        if not propName in self.cfg:
            return False
        if( type(self.cfg[propName]) == str):
            self.cfg[propName] = propValue
            return
        if( type(self.cfg[propName]) == int):
            self.cfg[propName] = self.prop_val_int(propValue)
            return
        if( type(self.cfg[propName]) == bool):
            self.cfg[propName] = self.prop_val_bool(propName, propValue)
            return 

    def prop_val_bool(self,propName, value):
        if( type(value)==bool):
            return value
        value = str(value).lower( )
        if( value=='true'):
            return True
        if( value=='yes'):
            return True
        if( value=='no'):
            return False
        if value=='false':
            return False
        if value =='0':
            return False
        if propName in self.cfg_engine:
            return not self.cfg_engine[propName]
        if propName in self.cfg_base:
            return not self.cfg_base[propName]
        if propName in self.cfg:
            return not self.cfg[propName]
        return True

    def prop_val_int(self,value):
        #todo Error Checking
        if( type(value)==int):
            return value
        return int(value)

    def prop_readConfig(self):
        for key in self.cfg_base:
            self.cfg[ key] = self.cfg_base[key] 
        for key in self.cfg_engine:
            self.cfg[ key] = self.cfg_engine[key] 
        appData = os.getenv('APPDATA')
        if( appData == None):
            iniName = "~/.config/qBittorrent/qBittorrent.conf"
        else:
            iniName = os.path.join(os.getenv('APPDATA'),"qBittorrent","qBittorrent.ini")
        if os.path.isfile(iniName):
            self.prop_readFile(iniName)
        else:
            self.log( "failed to read qBittorrent configuration")
        cfgName = self.shortname+ '.cfg';
        cfgName = os.path.join(self.engineDir,cfgName)
        if not os.path.isfile(cfgName):
#             cfgFile = open( cfgName, 'w')
#             for propName in self.cfg:
#                 cfgFile.write(propName+ "=" + str( self.cfg[propName]) +"\n");
#             cfgFile.close()
            return
#         self.prop_readFile(cfgName)
        return

    def prop_readFile(self,fileName):
        cfgFile = open( fileName, 'r')
        content =cfgFile.read()
        cfgFile.close() 
        linesArr = content.split( "\n")
        for eachLine in linesArr:
            EachLineContent =eachLine.split("=")
            if( len(EachLineContent)==2):
                self.prop_set(EachLineContent[0], EachLineContent[1])

    def webAPI_init(self):
        if self.webUI == False:
            return False
        
        if self.webUI != None:
            return True
        
        if( self.prop("WebUI.HTTPS.Enabled")):
            server = 'https://localhost:' + self.prop("WebUI.Port") +  '/'
        else:
            server = 'http://localhost:' + self.prop("WebUI.Port") +  '/'
        self.log('reading local web server '+server)
        try:
            self.webUI = v1k45Client(server)
        except:
            self.webUI = False
            self.log("CONNECTION REFUSED")
            return False
        if( not(self.prop("WebUI.LocalHostAuth"))):
            logintext = self.webUI.login(self.prop("WebUI.Username"), self.prop("WebUI.Password"))
            if( type(logintext) == str):
                self.log("Failed to login Server response:" + logintext )
                return False
            else:
                self.log("login success")
        else:
            self.log('no login is required')
        return True
    
        
    def webAPI_readList(self):
        if self.torrentIHave != None:
            return
        self.torrentIHave = {}
        
        if self.prop("searchHave") == "norm":
            self.log( "webAPI_readList Not Needed" )
            return
        
        if not self.prop("WebUI.Enabled"):
            self.log( "webAPI_readList Not Web enabled" )
            return
        if not self.webAPI_init():
            self.log( "webAPI_readList web init failed" )
            return
        self.log( "webAPI_readList Not Web enabled" )        
        try:
            torrents = self.webUI.torrents()
        except v1k45LoginRequired:
            self.log_toSearchRestult("************ Login to your local web server failed")
            return False
        self.log("found " +str(len(torrents) ) + " torrents on your local server")
        
        for eachTorrent in torrents:
            bthash = eachTorrent['hash']
            size = eachTorrent['size']
            self.torrentIHave[bthash] = size
    
    def webAPI_download_from_link(self, link, **kwargs):
        if not self.webAPI_init():
            return
        self.log("UPLOADING %s " % link)
        return self.webUI.download_from_link(link, **kwargs)
        
    def webAPI_download_from_file(self, file_buffer, **kwargs):
        if not self.webAPI_init():
            return False
        try:            
            self.webUI.download_from_file(file_buffer, **kwargs)
            return True
        except:
            self.log("upload failed once")
            self.log_Fatal(traceback.format_exc())
        try:            
            self.webUI.download_from_file(file_buffer, **kwargs)
            return True
        except:
            self.log("Upload failed twice")
            self.log_Fatal(traceback.format_exc())
        return False
    
        
    def webAPI_get_torrent(self, infohash):
        if not self.webAPI_init():
            return
        return self.webUI.get_torrent(infohash)
        
    def url_to_json(self,url):
        data = self.url_to_str(url)
        if data=="":
            return []
        return json.loads(data)
        
    def url_to_str(self,url):
        session = requests.Session()
        try:
            request = session.get(url)
        except:
            return ""
        if( self.prop("search_UseText")):    
            result = request.text
        else:
            result = request.content         
        if( self.prop("search_encodeAscii")):
            result = result.encode('ascii', errors='backslashreplace').decode('ascii')
        if( self.prop("search_decode")):
            result = str(result.encode(sys.stdout.encoding, errors='replace'))
        if( self.prop("search_logToFile")):
            self.log_raw(result)
            self.log_raw("\n")
        return result
    
    def url_to_treeroot(self , url):
        try:
            data = self.url_to_str(url)
            if data =="":
                data = "<html></html>"
            if (self.prop("search_dataType") =="xml"):
                root = etree.fromstring( data)
            else:
                parser = etree.HTMLParser()
                tree   = etree.parse(io.StringIO( data), parser)
                root = tree.getroot();
            return root
        except: # catch *all* exceptions
            self.log_Fatal(traceback.format_exc())
            return False

    def searchAction_cmd(self, cmdstr):
        if cmdstr == "showlog":
            cmdstr = "logmode=verbose"
        if cmdstr.lower() == "dumpconfig" or cmdstr.lower() == "dumpcfg":
            self.searchAction_DumpConfig()
            return
        if cmdstr == "help":
            self.searchAction_Help()
            return
            
        if "=" in cmdstr:
            action = cmdstr.split("=")[0]
            parm =  cmdstr.split(action+"=")[1]
        else:
            action = cmdstr
            parm = ""
        if ":" in action:
            objectstr = action.split(":")[0]
            found = False
            for engineName in objectstr.split(","):
                if self.shortname == engineName:
                    found = True
            if not found:
                return
            action =  action.split(objectstr+":")[1]
        if action in self.cfg:
            self.prop_set(action,parm)
            return

    def searchAction_DumpConfig_out(self, outputText):
        if self.prop("action")=="seach":
            self.log_toSearchRestult(outputText)
        else:
            self.log(outputText)
             
    def searchAction_DumpConfig_cat(self, title, data):
        self.searchAction_DumpConfig_out("-------")
        self.searchAction_DumpConfig_out(title)
        for key in data:
            outputText = "== " + key  +" = " +  str( self.cfg[key])
            self.searchAction_DumpConfig_out(outputText)
            if key in self.cfg_types:
                if type(self.cfg_types[key])==list:
                    valueList = ",".join(self.cfg_types[key])
                    outputText = "       Possible values are " +valueList 
                    self.searchAction_DumpConfig_out(outputText)
        self.searchAction_DumpConfig_out("-------")                    
        
    def searchAction_DumpConfig(self):
        cfgByCat = {
            "base":[],
            "engine":[],
            "ini":[]
        }
        for key in self.cfg:
            if( key in self.cfg_base):   
                where = "base"
            elif( key in self.cfg_engine):   
                where = "engine"
            else:
                where = "ini"
            cfgByCat[where].append(key)
        self.searchAction_DumpConfig_cat("INI Values", sorted(cfgByCat["ini"]))
        self.searchAction_DumpConfig_cat("Common Values", sorted(cfgByCat["base"]))
        self.searchAction_DumpConfig_cat("engine Values", sorted(cfgByCat["engine"]))





    def searchAction_Help(self):
        self.log_toSearchRestult("Help :Help: - this page")            
        self.log_toSearchRestult("Help :ShowLog: - Detailed log of what the search engine is doing")
        self.log_toSearchRestult("Help :DumpConfig: - Show Config")
        self.log_toSearchRestult("Help :SetConfig Name Value: - Incomplete")

    def search(self, what, cat="all"):
        self._realInit()
        self.prop_set("action","search")
        self.search_Main(what, cat)

    def search_console(self, what, cat="all"):
        self._realInit()
        self.search_Main(what, cat)

        
    def search_Main(self, what, cat="all"):
        try:
            
            what = self.search_filterWhat(what, cat)
            if len( what )==0:
                self.log( "Nothing to search for")
                return
            pageNum = self.prop("searchPageStart")
            while pageNum <= self.prop("searchPageEnd"):
                url = self.custom_getURL(pageNum)
                if len(url) ==0:
                    self.log( "SEARH:Page %d does not have a valid URL" % pageNum)
                    return
                if( not (self.search_process_page(url))):
                    self.log( "SEARH:Page returned false")                    
                    return
                pageNum += 1
            self.log( "SEARH:Page End")                
            return
        except: # catch *all* exceptions
            self.log_Fatal(traceback.format_exc())
                 
    def search_getURL(self,pageNum, whatNorm, cat="all"):
        self.search_filterWhat(whatNorm,cat)
        return self.custom_getURL( pageNum) 
        
    def search_filterWhat(self,what,cat="all"):
        realWhat = unquote(what);
        rtnWhat = ""
        for word in realWhat.split(" "):
            if word.startswith("--"):
                self.searchAction_cmd(word[2:])
            else:
                rtnWhat += word +" "
        self.search_whatNorm = rtnWhat.strip()
        self.search_whatQuote =quote( self.search_whatNorm)
        self.search_cat = self.supported_categories[cat]
        self.log("Searching for '%s' in '%s'" % (self.search_whatNorm , cat) )                                
        return self.search_whatQuote

    def search_process_page(self, url):
        try:
            returnVal = True
            resultsArr = self.search_DB_get(url)
            if resultsArr== False:
                self.log( "PAGE NOT IN DB " + url )
                root, keyElementsArr = self.search_page_getElements(url)
                if keyElementsArr == False:
                    return
                if not self.custom_pageProcess1(url, root):
                    returnVal = False
                resultsArr = [];
                for key_element in keyElementsArr:
                    result = self.custom_eltToArray(key_element);
                    if len(result )>0:
                        resultsArr.append(result)
                if not self.custom_pageProcess2(url, root):
                    returnVal = False
                self.search_DB_set( url,resultsArr )
                self.log( "PAGE HAS BEEN SAVED TO DB " + url )
            else:
                self.log( "PAGE Data from DB " + url )
            for result in resultsArr:
                self.returnResults( result )
                if( self.resultCount >= self.prop("searchResultsMax")):
                    return False
            return returnVal    
        except: 
            self.log_Fatal(traceback.format_exc())
            return False
        
    def search_DB_get(self, url):
        self.database_init()
        c = self.sqlConnection.cursor()
        c.execute('SELECT data,timestamp FROM history WHERE url=?', (url,))
        result = c.fetchone()
        if( result==None):
            return False
        data,timestamp =result
        if timestamp==0:
            self.log("never zero")
        return json.loads(data)

    def search_DB_set(self, url, resultsArr):
        self.database_init()
        c = self.sqlConnection.cursor()
        timestamp = int(time.time())
        data = json.dumps( resultsArr)
        c.execute("INSERT INTO history VALUES (?,?,?)",(url, timestamp,data))
        self.sqlConnection.commit()

        
        
#         history (url text, timestamp integer, data text
        return False
    
    
    def search_page_getElements(self, url): 
        try:
            if (self.prop("search_dataType") =="json"):
                root = self.url_to_json(url)
                if not self.keyElementDesc in root:
                    return (False,False)
                keyElementsArr = root[self.keyElementDesc] 
            else:
                root = self.url_to_treeroot(url)
                keyElementsArr = root.findall(self.keyElementDesc)    
        except:
            self.log("failed to download page" + url)
            return (False,False)
        
        if( len(keyElementsArr) ==0):
            self.log("No keyElements found")
            return (False,False)
        return (root, keyElementsArr)



    def returnResults_CheckAlreadySent(self,bthash):
        if bthash in self.loaded:
            return True
        self.loaded[bthash] = True
        return False
    
    def returnResults_CheckHaveIt(self,bthash):
        if self.prop("searchHave") =="norm":
            return False
        self.webAPI_readList()
        if not bthash in self.torrentIHave:
            return False
        self.curitem.on_Downloads = True
        
        if self.prop("searchHave") =="mark":
            pattern = self.prop("searchMarkHave")
            if not "%s" in pattern:
                pattern = "HAVE: %s"
            self.curitem.name = pattern % self.curitem.name
            return False
        if self.prop("searchHave") =="ignore":
            self.log( "%s is already on the download list" % self.curitem.logdesc() )
            return True
        return False        

    def returnResults_archive(self):
        archive_action = self.prop("archive_action")
        if archive_action=="norm":
            return False
        if len(self.prop("archive_dir")) == 0:
            return False            
        archive_dir = self.prop("archive_dir")
        filename = self.curitem.get_bthash()+'.torrent'
        archiveFileName = os.path.join(archive_dir,filename)
        if not os.path.isfile(archiveFileName):
            return False      
        self.curitem.in_archive = True              
        if archive_action=="ignore":
            self.log( "Ignoring archive torrent "+self.curitem.logdesc(),2)
            return True
        pattern = self.prop("archive_marktemplate")
        if not "%s" in pattern:
            pattern = "BLACKLIST: %s"
        self.curitem.name = pattern % self.curitem.name 
        return False        
        
        
    def returnResults_evallocalid(self):
        if self.curitem.localid =="":
            return
        cur_localid =self.curitem.localid 
        cur_bthash = self.curitem.get_bthash()
        LU_bthash = self.localid_getbthash(cur_localid);
        if LU_bthash == "":
            if cur_bthash =="":
                return
            self.localid_set_bthash(cur_localid, cur_bthash);
            return
        if cur_bthash=="":
            self.curitem.set_bthash(LU_bthash) 
            return
        if cur_bthash==LU_bthash:
            return
        message = "ERROR bthash missmatch localid %s scrape = %s database = %s"
        self.log(message %(cur_localid,cur_bthash ,LU_bthash) )
        
    def returnResults(self, result):
        if len(result)==0:
            return
        self.curitem = torrentListing( self)
        self.curitem.processResults(result)
        self.curitem.updateValues()
        self.returnResults_evallocalid()
#         self.log( "evaluating item for consideration:" + self.curitem.logdesc() )
#         self.log( "   localid=" + self.curitem.localid )
#         self.log( "   bthash=" + self.curitem.get_bthash() )
        
        if( "0000000000" in self.curitem.bthash):
            self.curitem.set_bthash("");
            self.curitem.url_magnet = ""
        
        if self.curitem.hashIsValid():
            if self.returnResults_CheckAlreadySent(self.curitem.get_bthash()):
                self.log( "Ignoring already sent "+self.curitem.logdesc())
                return
            if self.returnResults_CheckHaveIt(self.curitem.get_bthash()):
                return
            
            if self.returnResults_archive():
                return                
        else:
            self.curitem.set_bthash("");
        if self.curitem.size == "0" or self.curitem.size == "":
            if self.prop("searchzerobytes") == "ingore":
                self.log( "Ignoring zero byte "+self.curitem.logdesc())
                return

        if self.prop("usemagnet")=="never":
            link = self.curitem.neverMagnet()
        elif  self.prop("usemagnet") =="always":
            link = self.curitem.get_url_magnet()
        elif len( self.curitem.url_download)>0:
            link = self.curitem.getExtendedURL(self.curitem.url_download)
        else:
            link = self.curitem.getExtendedURL(self.url)
        if( len(link)==0):
            self.log( "Ignoring no valid link"+self.curitem.logdesc(),2)
            return
        printObj = {
            "size"          :self.curitem.size,
            "link"          :link,
            "name"          :self.curitem.name,
            "seeds"         :self.curitem.seeds,
            "leech"         :self.curitem.leech,
            "desc_link"     :self.curitem.url_desc,
            'engine_url'    :self.url}
        self.resultCount = self.resultCount + 1
        self.log("incremented counter")
#         self.curitem.dump()
        if self.prop("autodownload"):
            if not self.curitem.on_Downloads:
                self.download_listing()
        prettyPrinter(printObj)

class torrentListing(util):
    baseurl = None
    url = None
    engine = None
    bthash= None
    name = None
    url_magnet = None
    url_download = None
    url_desc = None
    size = None
    seeds  = None
    leech = None
    localid = None
    on_Downloads = False
    in_archive = False
    
    def __init__(self, engine):
        self.engine = engine
        self.baseurl = engine.baseurl
        self.url = engine.url

    def processResults(self, result):
        self.set_bthash(result["bthash"])
        if result['name'] != None:
            self.name = result['name'].strip()
        else:
            self.name ="ZZERROR - unnamed"
        self.url_magnet = result['url_magnet'].strip()
        self.size = self.format_size(result["size"])
        self.seeds = self.format_num( result['seeds'])
        self.leech = self.format_num(result['leech'])
        self.url_download = self.format_url(result['url_download'])
        self.url_desc = self.format_url(result['url_desc'])
        if( "localid" in result):
            self.localid = result["localid"]
        else:
            self.localid = ""
    
    def get_bthash(self):
        if( "0000000000" in self.bthash):
            self.bthash = ""
        return self.bthash

    def get_url_magnet(self):
        if( "0000000000" in self.url_magnet):
            return ""
        if( len(self.url_magnet ) >0):
            return self.url_magnet
        if(len(self.bthash) ==0):
            return ""
        self.url_magnet ="magnet:?xt=urn:btih:{}&dn={}".format( self.bthash ,self.name) 
        return self.url_magnet 
            
    def set_bthash(self, newval):
        newval = newval.lower().strip()
        if( "0000000000" in newval):
            self.bthash = ""
        if len(newval)!=40:
            self.bthash = ""
        else:
            self.bthash = newval

    def initfromExtendedURL(self, fullURL):
        self.url_download = fullURL.split("#")[0]
        if self.url_download == self.baseurl:
            self.url_download = ""
        self.bthash = self.util_middle(fullURL, "#bthash=","#")
        self.localid = self.util_middle(fullURL, "#localid=","#")
        self.localid = unquote(self.localid)
        self.url_magnet = self.util_middle(fullURL, "#url_magnet=","#")
        self.url_magnet = unquote(self.url_magnet)
        self.url_desc = self.util_middle(fullURL, "#url_desc=","#")
        self.url_desc = unquote(self.url_desc)
        self.name = self.util_middle(fullURL, "#name=","#")
        self.name = unquote(self.name)
        
    def hashIsValid(self):
        return len(self.bthash) ==40
    
    def logdesc(self):
        returnVal = self.name
        returnVal = returnVal.encode('ascii', errors='backslashreplace').decode('ascii')
        if self.bthash != None:
            returnVal += " hash(" +self.bthash +")" 
        
        if self.localid != None:
            returnVal += " localid(" +self.localid +")" 
        return returnVal
        
        
            
            
    
    def updateValues(self):
        if len( self.bthash ) == 0 and len(self.url_magnet ) > 0:
            self.bthash = self.magnetTobthash(self.url_magnet)
        
    
        
    def format_size(self,value):
        if type(value ) == int:
            return str( value)
        if value.isdigit():
            return value
        value = value.replace(",","")
        try:
            value =str(anySizeToBytes(value))
        except:
            self.log("BAD VALUE:" + value)
        return value 

    def format_num(self, value):
        if value == None:
            return ''
        value = str(value).replace(",","").strip()
        if not value.isdigit():
            return ''
        return value

    def format_url(self, value):
        value= value.strip()
        if( value==""):
            return ""
        if(":" in value):
            return value
        parts = self.baseurl.split("/")
        return parts[0] +"//" + parts[2] + value

    def magnetTobthash(self,url_magnet):
        bthash = url_magnet.split(":btih:")[1].split("&")[0]
        if( len(bthash)<40):
            bthash = base64.b32decode(bthash).hex()
        return bthash.lower()
    
    def getExtendedURL(self, baseurl):
        url = baseurl 
        url += "#bthash=" + self.bthash
        url += "#url_magnet=" +quote(self.get_url_magnet()) 
        url += "#localid=" +quote(self.localid)
        url += "#url_desc=" +quote(self.url_desc)
        url += "#name=" +quote(self.name)
        url += "#"
        return url
    
    def dump(self):
        result = []
        result.append ("baseurl     ="+str(self.baseurl     )) 
        result.append ("url         ="+str(self.url         ))
        result.append ("bthash      ="+str(self.bthash      ))
        result.append ("logdesc     ="+str(self.logdesc()   ))
        result.append ("name        ="+str(self.name        ))
        result.append ("url_magnet  ="+str(self.url_magnet  ))
        result.append ("url_download="+str(self.url_download))
        result.append ("url_desc    ="+str(self.url_desc    ))
        result.append ("size        ="+str(self.size        ))
        result.append ("seeds       ="+str(self.seeds       ))
        result.append ("leech       ="+str(self.leech       ))
        result.append ("localid     ="+str(self.localid     ))
        result.append ("in_archive  ="+str(self.in_archive))
        result.append ("on_Downloads="+str(self.on_Downloads))
        return result
        
        
    def neverMagnet(self):
        if self.url_download.startswith("magnet"):
            if( len( self.bthash)== 0):
                self.bthash = self.magnetTobthash(self.url_download)
            self.url_download = ""
        if( len(self.bthash)==0):
            return ""
        if( len(self.url_download)>0):
            return self.getExtendedURL(self.url_download)
        else:
            return self.getExtendedURL(self.url)
