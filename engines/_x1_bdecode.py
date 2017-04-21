import io
import hashlib
#https://github.com/d33tah/bdecode

class Bdecode(object):
    def read_filename(self, file_name, capture_for_infohash=None ):
        fileHandle = open( file_name, 'rb')
        self.read_filehandle(fileHandle)
        fileHandle.close()
    
    def read_contents(self,contents, capture_for_infohash=None ):
        fileHandle = io.BytesIO(contents)
        self.read_filehandle(fileHandle,capture_for_infohash=None )
        fileHandle.close()

    def read_filehandle(self, input_file, capture_for_infohash=None ):
        """
        Args:
            input_file (file): a file to read from. Only f.read(n) will be
                used
            capture_for_infohash (bool): set this to False if you want to
                disable the calculation of info_hash - this might speed up
                parsing a bit
        """
        self._input_file = input_file
        if capture_for_infohash is None:
            self._capturing_for_infohash = False
            self._infohash_obj = hashlib.sha1()
            self.info_hash = None
        else:
            self._capturing_for_infohash = None
        self.read_value()    

    def _read_bytes(self, n):
        ret = self._input_file.read(n)
        if self._capturing_for_infohash:
            self._infohash_obj.update(ret)
        return ret

    def _read_number_until(self, c):
        # Reads a number given character, then returns it as a string.

        ret = ""
        while True:
            v = self._read_bytes(1).decode('ascii')
            if v.isdigit() or v == '-':
                # I know that string appending is slow, but how large can
                # those numbers really be?
                ret += v
            else:
                if v != c:
                    errmsg = "ERROR: Expected '%s', got '%s'." % (c, v)
                    raise ValueError(errmsg)
                return ret

    def _read_dict(self):
        # Dictionary starts with "d", contains a stream of key-value pairs
        # and ends with "e".
        #
        # This one is the most complex read function because we also calculate
        # info_hash (comment out all is_info code and it gets tiny).
        ret = {}
        is_info = False
        while True:
            key = self.read_value()
            if key == b'info' and self._capturing_for_infohash is not None:
                # we're about to read value used for calculating info_hash.
                is_info = self._capturing_for_infohash = True
            if key is None:
                return ret
            value = self.read_value()
            if is_info:
                # we've read value for info_hash, stop growing the StringIO
                is_info = self._capturing_for_infohash = False
                self.info_hash = self._infohash_obj.hexdigest().upper()
            ret[key] = value

    def _read_list(self):
        # List starts with l, contains a stream of elements and ends with e.
        ret = []
        while True:
            v = self.read_value()
            if v is not None:
                ret += [v]
            else:
                return ret

    def _read_string(self, data_so_far):
        # A string is encoded as a number which means its length, followed by
        # a colon (":")
        t = data_so_far + self._read_number_until(":")
        ret = self._read_bytes(int(t))
        return ret

    def read_value(self):
        """Returns next bencoded object in the file. Note that typical torrent
        files contain one nested bencoded object."""
        t = self._read_bytes(1).decode('ascii')
        if t == 'e':
            return None
        elif t == 'd':
            return self._read_dict()
        elif t.isdigit():
            return self._read_string(data_so_far=t)
        elif t == 'l':
            return self._read_list()
        elif t == 'i':
            return self._read_number_until('e')
        else:
            raise ValueError("Unexpected type: %s" % t)
