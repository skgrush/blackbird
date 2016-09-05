#!/usr/bin/env python

import hashlib,string
from numbers import Number
from base64 import standard_b64encode,standard_b64decode
import filehash

try:
    import warnings
except ImportError:
    warnings = None
try:
    import json
except ImportError:
    json = None

#######CONSTANTS#######
_PRINTABLE = ''.join(map(chr,range(0x09,0x0E))+map(chr,range(0x20,0x7F)))
_IDENT_CHARS = 'abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789-_'


def _wrn(*args):
    if warnings:
        x=''
        for i in args:
            x+="{}".format(i)
        warnings.warn(x,UserWarning)

#
#
# Manifest files are placed (programatically) in each directory holding relevant files. 
# Each file in the directory should hold AT MOST one user.
# 
# ENCODING:           b74cb12d
#             b   7   4   c   b   1   2   d  
#   Magic:  '\x62\x37\x34\x63\x62\x31\x32\x64'
#             0   1   2   3   4   5   6   7  
#   Header:
#       Starts at the first '\x01'.
#       Header parts are started with '\x01' and followed by an ascii character
#           representing their particular function.
#           Manifest identifier:    '\x01N'+ IDENT(see Misc. below)
#           ....
#           Manifest Version #:     '\x01V'+ IDENT
#           Manifest Extension:     '\x01X'+ IDENT
#           Manifest Hash:          '\x01H'+ md5-hash (hex) of concat(02F,02D)
#           Attributes:             '\x01A'+IDENT+'\x1E'+ DATA(see Misc. below)
#           End of header:          '\x01E'
#
#   Sections:
#       Non-header sections start with '\x02' and followed by an ascii character
#           representing their particular function.
#       '\x02F' : Section for the list of files relevant in this directory.
#           List entities are separated by '\x1C'.
#           Each entity is of the form   base64(fname) +'\x1E'+ base64(username) +'\x1E'+ md5_hex
#           (username is 'none' if not relevant)
#           (md5_hex is '0'*32 if hash cannot be taken)
#       '\x02D' : Section for the list of subdirectories (with manifests) in this directory.
#           List entities are separated by '\x1D'.
#           Each entity is of the form   base64(dirname) +'\x1E'+ manifest-hash(of dir's mfst)
#       '\x02E' : End of Sections
#
#   End of Manifest:
#       The end of manifest-related data is marked by '\x04', aka EOT.
#
#   Misc.:
#       strings:    '\x90'+'content here'+'\x9C'
#                                   only allows characters in _PRINTABLE
#       IDENT:      identifier of the form "[A-Za-z0-9_-]+"
#       DATA:       The first byte determines the type of value. 
#                       '\x90' for a string (tailed by '\x9C', as above)
#                       'I' for an int/float (in ASCII, not hex/binary)
#                       'L' for an iterable containing either/both of the above two, each preceded by '\x1F'.
#       
# C0/C1 Meanings
#
# \x01  Start of Heading
# \x02  Start of text
# \x90  Device Control String
# \x9C  String Terminator
# \x1D  Group Separator
# \x1E  Record Seperator
# \x1F  Unit Seperator

'''    _  ___  ___
|\  | / \  |  |           WHEN USING THE FUNCTIONS BELOW, DO   
| \ | | |  |  |--- *           NOT PRE-FORMAT ANY DATA.        
|  \| \_/  |  |___ *   ALL FORMATTING IS HANDLED BY THE MODULE.
'''
'''[(Above) NOTE: WHEN USING THE FUNCTIONS BELOW, DO NOT PRE-FORMAT ANY DATA. ALL FORMATTING IS HANDLED BY THE MODULE.]'''

class manifest(object):
    def __init__(self,mode,**kwargs):
        """Initialization for a file manifest.
        
        POSITIONALS:
            mode            Mode that this initialization is to use. 
                                0 / 'create'
                                1 / 'open'
        -
        CREATE-MODE KEYWORD ARGS:
            path            The current path to the new manifest file's 
                            directory. This value is not written to the 
                            manifest, it is only used for its creation.
            identifier      Unique identifier for this manifest and it's dir.
            attribs         [optional] dictionary of information that can be
                            used to identify manifests.
            overwrite       [optional] Boolean; if True and file exists, 
                            overwrites the file. Otherwise, raises an Exception.
                            If file doesn't exist, does nothing.
        """
        
        self.mode = {0:0,1:1,'create':0,'open':1}.get(mode,None)
        if self.mode is None:
            raise TypeError, "manifest parameter `mode' only accepts 0, 1, " \
                             "'create', and 'open'"
        
        self.__attribs = {}
        self.__parser = manifest._parser(self)
        
        self.__identifier = None
        
        self.__build_data = {} 
        
        if self.mode is 0:
            self.__create_init_(**kwargs)
        elif self.mode is 1:
            self.__open_init_(**kwargs)
        
        
    
    
    def __create_init_(self,*args,**kwargs):
        path = kwargs.get('path',None)
        if path is None:
            raise TypeError, "manifest [create-mode] expects 'path' as a " \
                            "keyword argument."
        
        if os.path.isfile(path) or not os.path.exists(path):
            raise Exception, "'path' keyword argument must be an existing" \
                                " directory in which the new manifest will" \
                                " be created."
        
        self.path = path
        
        ovrwrt = bool(kwargs.get('overwrite',False))
        attribs = kwargs.get('attribs',{})
        
        for kee,val in attribs.items():
            n_kee = self.__parser.mk_IDENT(kee)
            n_val = self.__parser.mk_DATA(val)
            self.__attribs[n_kee] = n_val
        
        
        identifier = kwargs.get('identifier',kwargs.get('id',None))
        if identifier is None:
            raise TypeError, "manifest [create-mode] expects 'identifier' as " \
                            "a keyword argument."
        
        
        
        
        

class _parser(object):
    def __init__(self,parent):
        self.parent = parent if isinstance(parent,manifest) else None
        
        self.magic = trnz('\x62\x37\x34\x63\x62\x31\x32\x64')
        self.version = self.mk_IDENT('development')
        self.ext = self.mk_IDENT('.mfst')
        self.manifest_names = '00{}'.format(self.ext)
    
    #leading
    def pack(self):
        #first must build sections (02F and 02D)
        #second make manifest hash for header
        #third build header
        
    
    
    def get_DATA(self,data):
        if type(data) is not bytearray:
            raise TypeError, "Invalid type for get_DATA function; expected bytearray."
        if data[0] not in [0x90,0x49,0x4C]:
            err = str(data[0:10])
            if len(data) > 10:
                err += '[...]'
            raise ValueError, "Identifying byte not at expected location.\nArgument: {!r}".format(str(err))
        
        if data[0] is 0x90:
            #string
            fnd = data.find('\x9C')
            nxtfnd1,nxtfnd2,nxtfnd3 = data.find('\x1F'),data.find('\x01'),data.find('\x02')
            if fnd < 0:
                raise ValueError, "Failed to find matching String Terminator in DATA."
            for nxtchr in ['\x1F','\x01','\x02','\x1E','\x1D']:
                if 0 < data.find(nxtchr) < fnd:
                    raise ValueError, "Found next entity before matching String Terminator in DATA."
            data_string,sep,remains = data[1:].partition('\x9C')
            if remains:
                _wrn("Remainder left after String Terminator: {!r}".format(str(remains)))
            return str(data_string)
        
        if data[0] is 0x49:
            #numeric
            data = data[1:]
            zEnd=len(data) #first non-[0-9\.] character position
            dec = -1
            for pos,val in enumerate(data):
                if val == 0x2E and dec < 0:
                    #if dec (decimal point) has 
                    #been found already, go to elif and break
                    dec = pos
                    
                elif not (0x30<=val<=0x39):
                    zEnd = pos
                    break
            
            if not zEnd:
                raise ValueError, "Zero-length 'I' DATA value."
            if zEnd < len(data):
                remains = data[zEnd:]
                if len(remains) > 10: remains = remains[:10]+"[...]"
                _wrn("Remainder left after end of 'I' DATA value: {!r}".format(remains)
            ret = float(data[:zEnd])
            if ret.is_integer():
                return int(ret)
            return ret
        #data[0] is 0x4C
        data = data[1:]
        nxtparts = []
        for fndnxt in ['\x01','\x02','\x1D','\x1E']:
            nxtparts.append(data.find(fndnxt))
        if min(nxtparts) >= 0:
            _wrn("Found next entity's identifying byte in DATA value, {} byte(s) after the '\\x4C' identifying byte.".format(min(nxtparts)+1))
            data = data[:min(nxtparts)]
        data_seq = data.split('\x1F')
        if not data_seq:
            raise ValueError, "Found no data in 'L' DATA value."
        iter_count=0
        ret = []
        while True:
            if iter_count >= len(data_seq):
                break
            if not data_seq[iter_count]:
                data_seq.pop(iter_count)
                continue
            if data_seq[iter_count][0] == 0x4C:
                raise ValueError, 'Cannot parse iterables of iterables...'
            if data_seq[iter_count][0] not in [0x90,0x49]:
                raise ValueError, 'Unexpected identifying byte: {!r}'.format(chr(data_seq[iter_count][0]))
            ret.append( self.get_DATA(data_seq[iter_count]) )
        return ret
    
    def mk_DATA(self,value,no_iterables=False):
        ret = bytearray()
        
        if isinstance(value,basestring):
            good='',bad=''
            for i in value:
                if i in _PRINTABLE:
                    good+=i
                else: bad+=i
            if bad:
                _wrn('Invalid characters stripped from IDENT: {}'.format(bad))
            ret=self.trnz('\x90'+good+'\x9C')
        elif isinstance(value,Number):
            if int(value) == value:
                ret=self.trnz('I'+str(int(value)))
            elif float(value) == value:
                if 'e' not in str(float(value)).lower():
                    ret=self.trnz('I'+str(float(value)))
                else:
                    raise OverflowError,'Values cannot be stored exponentially'
            else:
                raise TypeError,'Cannot store numbers that cannot be represented as an integer or real.'
        elif hasattr(value,'__iter__'):
            if no_iterables:
                raise ValueError,'Manifests not fit to hold multi-dimentional iterables.'
            ret = 'L'
            for subvalue in value:
                ret+='\x1F'+self.mk_DATA(subvalue,True)
        else:
            raise TypeError, 'Invalid type for mk_DATA: {}'.format(type(value).__name__)
    
    def mk_IDENT(self,value):
        bad,good='',''
        if not isinstance(value,basestring):
            value = str(value)
        for i in value:
            if i in _IDENT_CHARS:
                good+=i
            else:
                bad+=i
        if bad:
            _wrn('Stripped invalid characters from IDENT: {!r}'.format(','.join(set(bad))))
        return trnz(good)
    
    def trnz(self,ins):
        return bytearray(map(ord,str(ins)))
    
    def parent_attr(self,attr,_set='SoMethINgOthEr'):
        pcls = self.parent.__class__.__name__
        if attr.endswith('__'):
            pass
        elif attr.startswith('__'):
            attr = '_{}{}'.format(pcls.lstrip('_'),attr)
        if _set != 'SoMethINgOthEr':
            return setattr(self.parent,attr,_set)
        return getattr(self.parent,attr)
    
    def __build(self,w):
        if 'header' in w:
            ######
        elif 'section' in w:
            contents = os.listdir(self.parent.path)
            contents.sort(key=str.lower)
            list_fl = []
            list_dr = []
            for itm in contents:
                itmpath = os.path.join(self.path,itm)
                if os.path.islink(itmpath) or itm[0] == '.' or 
                        os.path.splitext(itm)[1] == self.ext:
                    continue
                if os.path.isfile(itmpath):
                    list_fl.append(itm)
                elif os.path.isdir(itmpath):
                    list_dr.append(itm)
            
            #SECTION 02F
            sectF = self.trnz('\x02F')
            newlst = []
            for fl in list_fl:
                flpath = os.path.join(self.parent.path,fl)
                fnm = standard_b64encode(fl)
                user = 'NONE'
                if fl.lower().endswith('.json') and json:
                    dec = json.JSONDecoder()
                    decoded = None
                    try:
                        with open(flpath) as openfl:
                            decoded = dec.decode(openfl.read())
                    except ValueError:
                        pass
                    if decoded:
                        try:
                            for prt in decoded.values()[0]:
                                if 'gradebook' in prt.get('type','').lower():
                                    user = prt.get('user',user)
                                    break
                        except:
                            pass
                try:
                    hsh = filehash.md5(flpath,16)
                except IOError:
                    hsh = filehash.md5_default
                user = standard_b64encode(user)
                i = self.trnz('{}\x1E{}\x1E{}'.format(fnm,user,hsh))
                newlst.append(i)
            sectF+= self.trnz('\x1C').join(newlst)
            self.parent_attr('__builddata')['\x02F'] = sectF
            
            #SECTION 02D
            sectD = self.trnz('\x02D')
            newlst = []
            for dr in list_dr:
                drpath = os.path.join(self.parent.path,dr)
                dr_manifestpath = os.path.join(drpath,self.manifest_names)
                if os.path.exists(dr_manifestpath):
                    mfst_contents = bytearray()
                    srch = self.trnz('\x01E')
                    with open(dr_manifestpath,'rb') as ofile:
                        mfst_contents.append(ofile.read(8))
                        if self.magic not in mfst_contents:
                            continue
                        for chunk in iter(lambda: ofile.read(10), ''):
                            mfst_contents += chunk
                            if srch in mfst_contents:
                                break
                    if bytearray('\x01H') not in mfst_contents:
                        continue
                    mfst_contents = mfst_contents.split('\x01H',1)[1].split('\x01',1)[0]
                    
                    mfst_hash = str(mfst_contents)
                    drnm = standard_b64encode(dr)
                    newlst.append(self.trnz('{}\x1E{}'.format(drnm,mfst_hash)))
            sectD+= self.trnz('\x1C').join(newlst)
            self.parent_attr('__builddata')['\x02D'] = sectD
            
