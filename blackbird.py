#!/usr/bin/env python


#Constants
from bbconsts import *
BB_DATE_FORMAT = '%b %d, %Y %I:%M %p'

import warnings,os,sys,urllib,urllib2,getpass,cookielib,urlparse,datetime,re,numbers,logging,weakref

import bbcompat
bs4 = bbcompat.get_bs4(ret_bs4=True)

##REPLACED BY bbcompat MODULE
#
#sys.path.insert(0,
#        os.path.abspath(os.path.join(os.path.dirname(__file__),'bs4_4.2.1_vitals.zip')))
#try:
#    import bs4
#except ImportError:
#    raise ImportError, "Encountered ImportError while importing 'bs4', the BeautifulSoup4 module."



central_logger = logging.getLogger("blackbird")


LOG_debug = central_logger.debug
LOG_info = central_logger.info
LOG_warning = central_logger.warning
LOG_error = central_logger.error
LOG_critical = central_logger.critical
LOG_exception = central_logger.exception



#def chrange(*ranges):
#    """Return computed character ranges and/or strings
#    
#    ARGUMENTS:
#        'ranges' represents one of two options:
#            1) if 'ranges' is a single argument, it should be a string 
#                formatted similarly to a RegEx string with quoted text
#                and/or character ranges. Character ranges are of the 
#                format "x-y", where all ascii characters between 'x' and 'y'
#                will be returned; quoted texted is simply a substring with
#                characters between matching quotes.
#                NOTE 1: Matching double-quotes are found first, so long as 
#                they are not escaped; then matching single-quotes, then
#                other escaped characters, then character ranges.
#                NOTE 2: Escaped quotes should be double-escaped, e.g. "\\'a\\\""
#                EXAMPLE: "A-Cq-r1-36\-8" will return 
#                                  ['A','B','C','q','r','1','2','3','6','-','8']
#            2) if multiple arguments are passed, each pair of arguments (in
#                the sense of arg0 and arg1, arg2 and arg3) is interpretted as
#                a character range. If an odd number of arguments are passed,
#                the odd-character-out is added by itself.
#    """
#    theStr=[]
#    if len(ranges)==1 and type(ranges[0]) in [str,unicode]:
#        parseme=ranges[0]
#        ###Quoted-Text grabbing
#        for quot in ['"',"'"]:
#            c=parseme.count(quot)
#            c-=parseme.count('\\'+quot)
#            for it in range(c/2):
#                ind = parseme.index(quot)
#                while parseme[ind-1]=='\\':
#                    ind=parseme.find(quot,ind+1)
#                ind2= parseme.find(quot,ind+1)
#                while parseme[ind2-1]=='\\':
#                    ind2=parseme.find(quot,ind2+1)
#                theStr.append(parseme[ind+1:ind2])
#                parseme=parseme[:ind]+parseme[ind2+1:]
#                if ('\\'+quot) in theStr[-1]:
#                    c2=theStr[-1].count('\\'+quot)
#                    for it2 in range(c2):
#                        ind = theStr[-1].index('\\'+quot)
#                        theStr[-1]=theStr[-1][:ind]+theStr[-1][ind+1:]
#        ###Backslashed-character grabbing
#        c=parseme.count('\\')
#        for it in range(c):
#            ind=parseme.index('\\')
#            if ind+1==len(parseme):
#                theStr.append(parseme[ind])
#                parseme=parseme[:-1]
#            else:
#                if parseme[ind+1] != '\\': 
#                    theStr.append(parseme[ind+1])
#                parseme=parseme[:ind]+parseme[ind+2:]
#        ###character-range grabbing
#        c=parseme.count('-')
#        for it in range(c):
#            ind=parseme.index('-')
#            if ind+1==len(parseme):
#                theStr.append(parseme[ind])
#                parseme=parseme[:-1]
#            elif ind==0:
#                theStr.append(parseme[0])
#                parseme=parseme[1:]
#            else:
#                ext = chrange(parseme[ind-1],parseme[ind+1])
#                if ext: theStr.extend(ext)
#                parseme=parseme[:ind-1]+parseme[ind+2:]
#        if parseme: theStr.extend(parseme)
#    else:
#        for i in range(0,len(ranges)-1,2):
#            theStr += map(chr,(range(ord(str(ranges[i])[0]),1+ord(str(ranges[i+1])[0]))))
#        if len(ranges)%2==1:
#            theStr += [ranges[-1][0]]
#    if not theStr: theStr=None
#    return theStr

#def process_uri(str_arg,part):
#    """Processing of parts of a uri
#    
#    str_arg     The uri-part string to process
#    part        Which part is it? 0=protocol/scheme, 1=[subdomain+]domain, 2=path
#    """
#    noncountry_TLDs=['aero','asia','biz','cat','com','coop','info','int','jobs',
#        'museum','name','net','org','post','pro','tel','travel','xxx','edu',
#        'gov','mil','mobi']
#    scheme_chars = chrange('a-z0-9.-')
#    if type(str_arg) not in [str,unicode]:
#        raise ValueError('\'process_uri\' function passed non-string type \'%s\' for str_arg'%type(str_arg).__name)
#    str_arg.strip('/')
#    if part==0:
#        str_arg=str_arg.strip(':')
#        for i in str_arg:
#            if i not in scheme_chars:
#                raise ValueError('Unexpected character \'%s\' in argument to process_uri'%i)
#    elif part==1:
#        theTLD=str_arg.split('.')[-1]
#        if '.' not in str_arg or theTLD not in noncountry_TLDs and len(theTLD)!=2:
#            raise ValueError('Invalid syntax in domain passed to process_uri')
#    return str_arg



class web_img(object):
    def __init__(self,soup_Tag):
        if not isinstance(soup_Tag,bs4.Tag):
            raise TypeError, "web_img argument must be a bs4.Tag type, not {!r}".format(soup_Tag.__class__)
        object.__init__(self)
        self.Tag_name = soup_Tag.name
        self.Tag_attrs = soup_Tag.attrs
        self.title = soup_Tag.get('title',None)
        self.src = soup_Tag.get('src',None)
    
    def __repr__(self):
        return "<Image{1} src={0!r}>".format(self.src," title={!r}".format(self.title) if self.title else "")

_num_re = re.compile('^\D*?(?P<num>(?P<integ>\-?\d+)(?P<dec>\.\d+)?)(?P<pcnt>\%)?')

class Percentage(numbers.Rational):
    """
    
    ARGUMENTS:
      - 'numerator','denominator'   If numerator is rational, the Percentage
        will be (numerator/denominator). If numerator is a string, it
        is assumed to be a percent value and denominator will be ignored.
        
      - 'real_precision'    If not None, this determines the number of 
        decimal places within the Percentage, e.g. '54.32%' has 2 places.
        
      - 'rep_precision'     Similar to real_precision, but is ONLY for
        the precision when the Percentage is represented as a str. This
        allows for a Percentage to have a large precision but still
        be nicely representable.
    """
    
    __slots__ = ('_numerator','_denominator','_real_precision','_rep_precision')
    
    def __new__(cls,numerator=0,denominator=100,real_precision=None,rep_precision=2):
        self = super(Percentage, cls).__new__(cls)
        
        if isinstance(real_precision,numbers.Number):
            real_precision = int(real_precision)
        elif real_precision is not None:
            raise TypeError, "real_precision argument should be an integer or None, not {!r}".format(real_precision.__class__)
        else:
            real_precision = sys.maxint
        
        if isinstance(rep_precision,numbers.Number):
            rep_precision = int(rep_precision)
        else:
            raise TypeError, "rep_precision argument should be an integer, not {!r}".format(rep_precision.__class__)
        
        if isinstance(numerator,basestring):
            metch = _num_re.match(numerator)
            if not metch or not metch.group('num'):
                raise ValueError, 'Could not parse numbers from {!r}'.format(numerator)
            numerator = float(metch.group('num'))
            if numerator.is_integer():
                numerator = int(numerator)
            denominator = 100
        if not isinstance(numerator,numbers.Rational):
            if isinstance(numerator,float) or hasattr(numerator,'__float__'):
                numerator = float(numerator)
            else:
                raise TypeError, "numerator should be rational or rationalizable."
        if isinstance(denominator,float) or hasattr(denominator,'__float__'):
            denominator = float(denominator)
        else:
            raise TypeError, "denominator should be rational or rationalizable."
        
        if denominator == 0:
            raise ZeroDivisionError, "Denominator cannot be zero"
        
        n_sign = 1 if numerator   >= 0 else -1
        d_sign = 1 if denominator >= 0 else -1
        n_sign*=d_sign
        
        self._numerator,self._denominator  = n_sign*abs(numerator) , abs(denominator)
        self._real_precision,self._rep_precision = real_precision,rep_precision
        return self
    
    @classmethod
    def from_float(cls, f):
        if isinstance(f,float):
            if str(float(f)).lower() in ['nan','inf','-inf']:
                raise TypeError, "Cannot convert {} to {}".format(f,cls.__name__)
            return cls(f,1.0)
        raise TypeError, "{}.from_float() only takes floats".format(cls.__name__)
    
    @property
    def real_precision(i):
        return i._real_precision
    
    @property
    def rep_precision(i):
        return i._rep_precision
    
    @property
    def numerator(i):
        return round(i._numerator,i.real_precision)
    
    @property
    def denominator(i):
        return round(i._denominator,i.real_precision)
    
    def display(self):
        return "Percent({} / {}, rep_precision={}{})".format(self.numerator,self.denominator,self.rep_precision,",real_precision={}".format(self.real_precision) if self.real_precision is not None else "")
    
    def __str__(self):
        return '{0:.{1}f}%'.format(100*float(self.numerator) / self.denominator,self.rep_precision)
    
    def __repr__(self):
        return self.__str__()
    
    def __float__(self):
        return round(float(self.numerator)/self.denominator, self.real_precision+2)
    
    def pfloor(s):
        x = 100.0*s.numerator//s.denominator
        return Percentage(x,self.denominator,self.real_precision+2,self.rep_precision+2)
    
    
    
    def __abs__(s):
        return Percentage(abs(self.numerator),self.denominator)
    
    def __add__(s,o):
        num = s.numerator + s.denominator*o
        return Percentage(num,s.denominator,s.real_precision,s.rep_precision)
    
    def __div__(s,o):
        num = s.numerator/o
        return Percentage(num,s.denominator,s.real_precision,s.rep_precision)
    
    def __eq__(s,o):
        #Relies on '__float__'
        try:
            return (float(s) == round(o,s.real_precision+2) or (float(self) == float(o)))
        except TypeError:
            return False
    
    def __floordiv__(s,o):
        #Relies on '__div__' and 'self.pfloor()'
        return (s/o).pfloor()
    
    def __le__(s,o):
        #Relies on '__lt__' and '__eq__' and '__float__'
        return (s < o or s == o)
    
    def __lt__(s,o):
        #Relies on '__float__'
        return (float(s) < o)
    
    def __mod__(s,o):
        #Relies on '__float__'
        num = (float(s) % o) * s.denominator
        return Percentage(num,s.denominator,s.real_precision,s.rep_precision)
    
    def __mul__(s,o):
        return Percentage(s.numerator*o,s.denominator,s.real_precision,s.rep_precision)
    
    def __neg__(s):
        return Percentage(-1*s.numerator,s.denominator,s.real_precision,s.rep_precision)
    
    def __pos__(s):
        return Percentage(s.numerator,s.denominator,s.rep_precision,s.rep_precision)
    
    def __pow__(s,o):
        return Percentage(s.numerator**o,s.denominator**o,s.real_precision,s.rep_precision)
    
    def __sub__(s,o):
        num = s.numerator - s.denominator*o
        return Percentage(num,s.denominator,s.real_precision,s.rep_precision)
    
    def __truediv__(s,o):
        num = s.numerator.__truediv__(o)
        return Percentage(num,s.denominator,s.real_precision,s.rep_precision)
    
    def __trunc__(s):
        #Not sure if this is actually correct....
        return s.pfloor()
    
    
    def __radd__(s,o):
        return o + float(s)
    def __rdiv__(s,o):
        return o / float(s)
    def __rfloordiv__(s,o):
        return o // float(s)
    def __rmod__(s,o):
        return o % float(s)
    def __rmul__(s,o):
        return s*o
    def __rpow__(s,o):
        return o**float(s)
    def  __rsub__(s,o):
        return o - float(s)
    def __rtruediv__(s,o):
        return o.__truediv__(float(s))

def number_finder(val,typ=0,else_orig=False,rem_commas=True):
    """Converts 'val' argument to desired numeric type.
    
    'val' can be a string-type or a numeric (sub-)type.
    'typ' is a bitmap of accepted output types.
        0   Unknown/any. Will return val as the most accurate acceptable type.
        1   Int. 
        2   Float.
        4   Percentage. Returns a Percentage class instance.
    'else_orig' is a boolean [def: False]. If True and 'val' cannot be parsed
        for a meaningful value, 'val' is returned instead of None.
    """
    if typ is int:
        typ = 1
    elif typ is float:
        typ = 2
    elif typ is Percentage:
        typ = 4
    try:
        typ = int(typ)
    except TypeError:
        raise TypeError, "typ argument must be an integer or be coercible to int"
    
    fail_val = None
    if else_orig:
        fail_val = val
    
    if isinstance(val,basestring):
        if else_orig:
            fail_val = fail_val.strip()
        if rem_commas:
            val = val.replace(',','')
        
        
        re_dict = _num_re.match(val)
        if not re_dict:
            return fail_val
        
        re_dict = re_dict.groupdict()
        
        if typ == 0:
            if re_dict['pcnt']:
                return Percentage(re_dict['num']+'%')
            elif re_dict['dec']:
                return float(re_dict['num'])
            return int(re_dict['integ'])
        
        if typ&4:
            if re_dict['pcnt'] is not None or not typ&3:
                return Percentage(re_dict['num']+'%')
        if typ&2:
            if re_dict['dec'] is not None or not typ&1:
                return float(re_dict['num'])
        if typ&1:
            return int(re_dict['integ'])
    elif isinstance(val,numbers.Number):
        if typ == 0 and not typ&4:
            if val%1:
                return float(val)
            return int(val)
        if typ&2 and (not typ&1 or val%1):
            return float(val)
        if typ&1:
            return int(val)
        if typ&4:
            return Percentage(val)
    
    return fail_val

def parse_cdata(cdata_obj):
    if not isinstance(cdata_obj,bs4.element.PageElement):
        raise TypeError, "parse_cdata() argument should be a CData element, but must at least contain one"
    if not isinstance(cdata_obj,bs4.element.CData):
        new_obj = None
        try:
            all_texts = cdata_obj.find_all(text=True)
            for a_text in all_texts:
                if isinstance(a_text,bs4.element.CData):
                    new_obj = a_text
                    break
        except AttributeError:
            pass
        if new_obj is None:
            raise TypeError, "parse_cdata() argument should be a CData element, but must at least contain one"
        cdata_obj = new_obj
    soup = bs4.BeautifulSoup(cdata_obj.string)
    return soup

def try_import(*args):
    imp_list = []
    for arg in args:
        try:
            imp_list.append(__import__(arg,globals()))
        except ImportError as e:
            imp_list.append(e)
    
    if len(imp_list) == 1:
        return imp_list[0]
    elif len(imp_list) > 1:
        return tuple(imp_list)

def default_passwd_in(auths_denied=False):
    if sys.stdin.isatty():
        try:
            if auths_denied:
                sys.stdout.write("\nCredentials not accepted.\n\n")
            usernm = raw_input("Enter Username: ")
            sys.stdout.write("Enter Password: ")
            return usernm,getpass.getpass('')
        except KeyboardInterrupt:
            sys.stdout.write("^C")
        except EOFError:
            sys.stdout.write("^D")
            exit(0)
        finally:
            sys.stdout.write("\n")
    return False

def parse_url(arg_url):
    """Takes in a URL and returns a ParseResult object and a dictionary of its query"""
    parsed = urlparse.urlparse(arg_url)
    qry = urlparse.parse_qs(parsed.query)
    return (parsed, dict( [ (k,qry[k][0]if qry[k] else None) for k in qry.keys()] ))

def _pcn_helper(val,part):
    if part in ['loc','sect']:
        return val
    if part == 'corsnum':
        if not val.isdigit():
            x = number_finder(val,1)
            if x and val.startswith(str(x)):
                return x
            return val
        else:
            return int(val)
    if part == 'clsnum':
        if not val.isdigit():
            return None
        return int(val)
    if part == 'term':
        if 4 <= len(val) <= 6:
            if val[-4:].isdigit() and int(term[-4:]) > 2000:
                return (val,int(term[-4:]))
            return (val,None)
        

def parse_course_name(name_str,part=4|2|1):
    """
    
    Basic syntax of course identifier and name:
        {LOC}-{DEPT}-{###}-{SECT}-{CATLG_ID}-{TERM}: {DEPT} {###}: {NAME} ({CC} {SECT}) {TERM}
                                                    |---Dept ID---|--------Common Name--------|
        |-----------Blackboard Course ID------------|----------------Full Name----------------|
    -
    Full Blackboard Course Name Syntax:
        COMBINED_ID     ::= BB_COURSE_ID ": " FULL_NAME
        BB_COURSE_ID    ::= LOC "-" DEPARTMENT "-" COURSE_NUMBER "-" SECTION "-" CLASS_NUMBER "-" TERM
        FULL_NAME       ::= DEPT_ID ": " COMMON_NAME
        DEPT_ID         ::= DEPARTMENT " " COURSE_NUMBER
        COMMON_NAME     ::= NAME " (" CC " " SECTION ") " TERM
        NAME            ::= <non-parenthesis character>+
        CC              ::= <letter>+
        LOC             ::= <letter>{3}
        DEPARTMENT      ::= (<letter> | "_")+
        COURSE_NUMBER   ::= <number>{3} ["H"]
        SECTION         ::= <number> <letter>+ <number>{0,3} | "ALL"
        CLASS_NUMBER    ::= <number>{7}
        TERM            ::= SEMESTER YEAR
        SEMESTER        ::= "SS" | "FS" | "SP"
        YEAR            ::= "20" <number>{2}
    -
    The 'part' parameter is a bitmap that determines what's being
    passed to the function (and thus what is to be parsed).
    -
    1 = COMMON_NAME
    2 = DEPT_ID
    4 = BB_COURSE_ID
    -
    Therefore if you pass "EXT-CONTED-001-1A-11011-FS2012", you would pass
        part=4 as well.
    If you pass "MATH 001: INTRO TO SUBTRACTION (LAB 2E) SP1938", you would
        pass part=3.
    """
    blackboard_course_id_re = re.compile(r'(?P<course_id>(?P<loc>[A-Z]{3})-(?P<dept>[A-Z_]+)-(?P<corsnum>[0-9]{3})H?-(?P<sect>[0-9][A-Z]+[0-9]{0,3}|ALL)-(?P<clsnum>[0-9]+)-(?P<term>(?P<sem>[FS][SP])(?P<year>20[01][0-9])))',re.I)
    dept_id_re = re.compile(r'(?P<dept_id>(?P<dept>[A-Z_]+)\ (?P<corsnum>[0-9]{3}))',re.I)
    common_name_re = re.compile(r'(?P<common_name>(?P<name>[^(]+)(\ \((?P<sect>[^)]+)\))?(?P<term>\ (?P<sem>[FS][SP])(?P<year>[0-9]{4})))',re.I)
    cc_sect_re = re.compile(r'(?P<cc>[A-Z_]+)\ (?P<sect>.*)',re.I)
    sect_re = re.compile(r'[0-9][A-Z]+[0-9]{0,3}|ALL',re.I)
    #Section examples: "1A42" "3A1" "ALL"
    #Course  examples: "247H"
    part_list = name_str.split(': ')
    dept_id = None
    
    result_dct = {}
    
    if part&4 and name_str:
        reggy = blackboard_course_id_re.search(name_str)
        if reggy:
            result_dct['bb_course_id'] = reggy.group('course_id')
            result_dct['loc'] = reggy.group('loc')
            result_dct['department'] = reggy.group('dept')
            result_dct['course_num'] = int(reggy.group('corsnum'))
            result_dct['section'] = reggy.group('sect')
            result_dct['class_num'] = int(reggy.group('clsnum'))
            result_dct['term'] = reggy.group('term')
            result_dct['semester'] = reggy.group('sem')
            result_dct['year'] = int(reggy.group('year'))
    
    if part&2 and name_str:
        reggy = dept_id_re.search(name_str)
        if reggy:
            dept_id = reggy.group('dept_id')
            dept = reggy.group('dept')
            corsnum = reggy.group('corsnum')
            if 'course_num' not in result_dct or result_dct['course_num'] is None:
                result_dct['course_num'] = int(corsnum)
            if 'department' not in result_dct or result_dct['department'] is None:
                result_dct['department'] = dept
    if part&1 and name_str:
        srch = name_str
        if dept_id:
            srch = srch.split(dept_id)[1]
        reggy = common_name_re.search(srch)
        
        if reggy:
            nem = reggy.group('name')
            if nem[0] == ':':
                nem = nem[1:]
            nem = nem.strip()
            result_dct['name'] = nem
            if result_dct.get('term',None) is None:
                result_dct['term'] = reggy.group('term').strip()
                result_dct['year'] = int(reggy.group('year'))
                result_dct['semester'] = reggy.group('sem')
            if reggy.groupdict()['sect']:
                x = reggy.group('sect')
                cc_sect = cc_sect_re.match(x)
                if 'all' in x.lower():
                    result_dct['section']='ALL'
                elif cc_sect:
                    if result_dct.get('component',None) is None:
                        result_dct['component'] = cc_sect.group('cc')
                    sect = cc_sect.group('sect')
                    sects = sect_re.findall(sect)
                    if len(sects) > 1:
                        result_dct['section'] = sects
                    elif sects and result_dct.get('section',None) is None:
                        result_dct['section'] = sects[0]
    return result_dct                
    
    

def byte_prefix(value,**kwargs):
    """Convert byte values.... in style.
    
    'value' parameter should be a string containing an int and suffix. The
        value will be literally parsed from the suffix, depending on kwargs.
    kwargs:
        value_bin       If True, value is evaluated as binary. (Overrides 
                            suffix base) [DEFAULT: False]
        value_dec       If True, value is evaluated as decimal. (Overrides
                            suffix base and 'value_bin') [DEFAULT: False]
        return_power    If 0: base; 1-9: 1024^n|1000^n; >1000: the value
                            [DEFAULT: 0]
        return_bin      If True, returns binary value. [DEFAULT: True]
        return_dec      If True, returns decimal value. [DEFAULT: False]
    -
    RETURNS:
        Returns a tuple with the converted value (three decimals places, if
        applicable) and the new prefix.
        Ex: byte_prefix('50kB',return_power=1) == (48.828, 'KiB')
        -
        Returns False if it could not be parsed.
    """
    value = value.replace(',','')
    byte_parse = re.compile('\s*(?P<val>[0-9,]*\.?[0-9]*)\s*(?P<suff>[A-Za-z]+)?\s*')
    value_re = byte_parse.match(value)
    if not value_re: return False
    value_re = value_re.groupdict()
    suffix = value_re['suff']
    value = value_re['val']
    value_dec = kwargs.get('value_dec',False)
    value_bin = kwargs.get('value_bin',False)
    return_power = kwargs.get('return_power',0)
    return_bin = not kwargs.get('return_dec',not kwargs.get('return_bin',True))
    suffix_is_bin=True
    bytez=1.0
    base=1024
    powr=0
    if value_dec:
        suffix_is_bin=False
    elif value_bin:
        pass
    else:
        if not suffix:
            pass
        elif len(suffix)>1 and suffix[1].lower()=='i':
            suffix_is_bin=True
        elif suffix[0]=='k':
            if len(suffix)>1:
                suffix_is_bin=False
    if suffix and len(suffix)>1 and suffix[-1]=='b':
        bytez=1.0/8
    if suffix:
        powr={None:0,'k':1,'m':2,'g':3,'t':4,'p':5}.get(suffix[0].lower(),0)
    byte_value = value
    if not suffix_is_bin:
        base=1000
    byte_value = float(value) * bytez * (base ** powr) 
    return_base = [1000,1024][return_bin]
    if isinstance(return_power,int) and return_power > 0:
        if 1000 <= return_power < 1024 and return_base == 1024:
            return_power = 1
        elif return_power >= 1000:
            return_power//=return_base
    else:
        return_power = 0
    rett = byte_value / (return_base ** return_power)
    rnd = 3 if return_power else 0
    rett = round(rett,rnd)
    if rett.is_integer():
        rett = int(rett)
    rett_suff = ''
    if return_power == 1:
        rett_suff = ['k','K'][return_bin]
    else:
        rett_suff = ['','','M','G','T','P','E','Z','Y'][return_power]
    rett_suff += ['B','iB'][bool(return_bin and return_power)]
    if not bytez:
        rett_suff = rett_suff[:-1]+'b'
    return (rett,rett_suff)

class _beaut_soup_custom:
    def __init__(self):
        self.void_elements = set(['base','br','hr','img','input','keygen','link','meta'])
        try:
            self.BSlxml = _beaut_soup_custom.BSlxml
            self.BShtml5lib = _beaut_soup_custom.BShtml5lib
        except AttributeError:
            bs4
            tr_lxml,tr_html5l = try_import('lxml','html5lib')
            hexver = sys.hexversion//0x100
            _beaut_soup_custom.BScompatVer = (hexver >= 0x30202 or 0x30000 > hexver >= 0x20703)
            if isinstance(tr_lxml,ImportError):
                tr_lxml = None
                if isinstance(tr_html5l,ImportError):
                    tr_html5l = None
                    if not _beaut_soup_custom.BScompatVer:
                        curV = "%s.%s.%s"%(sys.version_info.major,sys.version_info.minor,sys.version_info.micro)
                        recV = ['2.7.3','3.2.2'][sys.version_info.major==3]
                        recV2= ['2.7.3','3.2.2'][sys.version_info.major==2]
                        wrn = 'Could not find modules html5lib and lxml.\nBeautifulSoup 4 can be unstable without one of these at your Python version (%s).\nUsing Python %s or later is more supported, as well as Python %s or later (for Python %s).'%(curV,recV,recV2,recV2[0])
                        LOG_warning(wrn)
                    else:
                        wrn = 'Could not find modules html5lib and lxml for BeautifulSoup 4, which works even better with either, especially lxml.'
                        LOG_warning(wrn)
            self.BShtml5lib = _beaut_soup_custom.BShtml5lib = tr_html5l
            self.BSlxml = _beaut_soup_custom.BSlxml = tr_lxml
        self.BScompatVer = _beaut_soup_custom.BScompatVer
        self.BSarg = None
        if self.BSlxml:
            self.BSarg = 'lxml'
        elif self.BShtml5lib:
            self.BSarg = 'html5lib'
        elif self.BScompatVer:
            self.BSarg = 'html.parser'
        LOG_info("Pages will be parsed using {}".format(self.BSarg if self.BSarg else "bs4's parser choice"))
    
    def get_soup(self,fileObject=None,content=None,parser='useBSarg'):
        toPass = None
        fl_length = -1
        
        if not fileObject and content:
            if not isinstance(content,basestring) and hasattr(content,'read'):
                fileObject = content
                content = None
        
        if fileObject and (isinstance(fileObject,file) or \
                    hasattr(fileObject,'read')):
            
            content = fileObject.read()
            fileObject = None
            toPass = content
            fl_length = len(content)
            
        elif content:
            fileObject = None
            toPass = content
            fl_length = len(content)
        else: 
            return False
        
        if parser=='useBSarg':
            parser = self.BSarg
        elif isinstance(parser,list) and len(parser) == 1:
            parser = parser[0]
        
        if parser:
            
            if parser.startswith('_COMPAT_'):
                parser = parser[8:]
            elif parser == 'html.parser':
                return self.compat_soup(toPass,parser)
            elif parser == 'lxml' and fl_length > 0xBE00:
                return self.compat_soup(toPass,parser)
            
            try:
                return bs4.BeautifulSoup(toPass,parser)
            except bs4.FeatureNotFound:
                LOG_exception("BeautifulSoup raised a FeatureNotFound exception; switching to default parser")
                if fileObject:
                    return self.get_soup(fileObject=fileObject,parser=None)
                return self.get_soup(content=content,parser=None)
        
        else:
            return bs4.BeautifulSoup(toPass)
    
    def __compat_soup_helper(self,matchobj):
        tname = matchobj.group('tagname')
        if tname and tname.lower() in self.void_elements:
            if not (matchobj.group('isendtag') or matchobj.group('isselfclose') or matchobj.group('endtag')):
                #needs to be closed
                return matchobj.group(0)[:-1]+'/>'
        return matchobj.group(0)
    
    def compat_soup(self,toPass,parser):
        
        if isinstance(toPass,file) or hasattr(toPass,'read'):
            toPass = toPass.read()
        
        reggy = re.compile("""<(?P<isendtag>/)?(?P<tagname>[A-Z0-9]+)((\s+[^"'>/=\x00]+(\s*=\s*(?:"[^"]*"|'.*?'|[^'">\s]+))?)+\s*|\s*)(?P<isselfclose>/)?>(?P<endtag>\s*</\s*(?P=tagname)\s*>)?""",re.I)
        
        if parser == 'html.parser':
            LOG_info("Running compat_soup: html.parser")
            #void_elements = set(['base','br','hr','img','input','keygen','link','meta'])
            #fmt_repl = "(?P<target>\<{} ([^>\"/]+|\"[^>\"]*\")+\>)"
            #fmt_with = "\g<target></{}>"
            
            
            #for targ in void_elements:
            #    targ_repl = fmt_repl.format(targ)
            #    targ_with = fmt_with.format(targ)
            #    
            #    toPass = re.sub(targ_repl,targ_with,toPass,flags=re.I)
            toPass = reggy.sub(self.__compat_soup_helper,toPass)
        
        elif parser == 'lxml':
            fl_length = len(toPass)
            LOG_info("Running compat_soup: lxml; file length={}".format(fl_length))
            return self.compat_soup(toPass,parser='html.parser')
        
        return self.get_soup(content=toPass,parser='_COMPAT_{}'.format(parser))

class BlackboardError(RuntimeError):
        def __init__(self,value,soup=None,code=None,code_was_soft=False,errorid=None,url=None):
            self.value = value
            self.soup = soup
            self.code_was_soft=code_was_soft
            if code is None:
                code = -1
            if errorid is None:
                errorid = ""
            self.errorid=errorid
            self.code = code
            self.url=url
        
        def __str__(self):
            return repr(self.value)

class BlackboardPage:
    def __init__(self,BBinstance,addinfourl_obj,soup=None):
        if not isinstance(BBinstance,Blackboard):
            raise TypError('BlackboardPage instance passed invalid type for' \
                           ' parameter \'BBinstance\'.')
        if not isinstance(addinfourl_obj,urllib.addinfourl):
            raise TypeError('BlackboardPage instance passed invalid type for' \
                            ' parameter \'addinfourl_obj\'.')
        self.code = addinfourl_obj.code
        self.url = addinfourl_obj.url
        self.headers = addinfourl_obj.headers
        self.parent = BBinstance
        self.soup = soup
        if soup.__class__.__name__ != 'BeautifulSoup':
            self.soup = self.parent.html_parser.get_soup(fileObject=addinfourl_obj)
    
    def __str__(self):
        return repr(self.soup)


class course_object(object):
    def __init__(self,blackboard,**kwargs):
        object.__init__(self)
        self.value_dict = { 'bb_course_id':None,'full_name':None,'name':None,
                        'department':None,'component':None,'term':None,
                        'class_num':None,'section':None,'semester':None,
                        'year':None,'days':None,'times':None,'instructor':None,
                        'course_num':None, 'loc':None }
        for arg in kwargs:
            if arg in self.value_dict:
                self.value_dict[arg] = kwargs[arg]
        self.bb_inst = blackboard
        self.bb_id = kwargs.get('bb_id',kwargs.get('blackboard_id',None))
        self.content_dict = kwargs.get('content',{})#PageName: content_id
        self.visible_tools = kwargs.get('visible_tools',{})
    
    def _key_frmt(self,key):
        if not isinstance(key,basestring):
            return key
        key = key.lower()
        repl_dict = {'number':'num',' ':'_','location':'loc','campus':'loc'}
        for i in repl_dict:
            if i in key:
                key = key.replace(i,repl_dict[i])
        return key
    
    def __getitem__(self,key):
        key = self._key_frmt(key)
        if key in self.value_dict:
            return self.value_dict[key]
        else:
            err = 'key \'%s\' not in course_object value_dict.'%key
            raise KeyError(err)
    
    def __repr__(self):
        return "<blackbird.course_object(bb_id={},department={!r},course_num={},name={!r})>".format(self.bb_id,self['department'],self['course_num'],self['name'])
    
    def has_contentitem(self,key,extend=False):
        updt_cc = False
        for val in self.content_dict:
            if not isinstance(val,content_object):
                if extend:
                    updt_cc = True
                break
            if val.content_id == key or val.has_contentitem(key,extend=extend):
                return True
        
        if not updt_cc:
            return False
        else:
            x = self.bb_inst.update_course_content(self)
            if x is False:
                return False
            else:
                return self.has_contentitem(self,key)
    
    def get_contentitem(self,key,extend=False):
        updt_cc = False
        for val in self.content_dict.values():
            if not isinstance(val,content_object):
                if extend:
                    updt_cc = True
                break
            if val.content_id == key:
                return val
            x = val.get_contentitem(key,extend=extend)
            if x:
                return x
        
        if not updt_cc:
            return None
        else:
            y = self.bb_inst.update_course_content(self)
            if y is False:
                return False
            else:
                return self.get_contentitem(key)
    
    def __contains__(self,item):
        item = self._key_frmt(item)
        if item in self.value_dict:
            return True
        return False
    
    def iterkeys(self):
        return self.value_dict.iterkeys()
    def iteritems(self):
        return self.value_dict.itemitems()
    def itervalue_dict(self):
        return self.value_dict.itervalue_dict()
    def keys(self):
        return self.value_dict.keys()
    def items(self):
        return self.value_dict.items()
    def value(self):
        return self.value_dict.value_dict()
    def __iter__(self):
        return self.iteritems()

def parse_webdav_url(daurl,getinfo=False,bb_inst=None):
    """Utility function for page_parsing()
    
    Takes in a '/bbcswebdav' url and retrieves information from it.
    Returns (content_id, attach_id) or (None,None)
    -
    If getinfo is True and bb_inst is a Blackboard instance, asks 
    Blackboard for file information.
    Returns:
        NOT_LOGGED_IN   If such is the case.
        None            If Blackboard returns an error pertaining to the
                            file not existing.
        (None, None)    If the url is invalid.
        (content_id, attach_id, file_name, mimetype, (byte_sz, 'B'))
                        If the data is found.
        False           If you don't have permission (returned after checking login)
        -
        THIS FUNCTION DOES NOT DOWNLOAD DATA (BESIDES HEADERS).
    """
    if not (getinfo and isinstance(bb_inst, Blackboard)):
        getinfo = False
    if '.edu/' in daurl:
        daurl = daurl.split('.edu',1)[1]
    daurl = daurl.strip().strip('/')
    if not daurl.startswith('bbcswebdav'):
        LOG_debug("Argument URL doesn't start with 'bbcswebdav'")
        return (None,None) # Invalid input
    daurl = daurl.split('#')[0].split('?')[0]
    url_parts = daurl.split('/')
    #if len(url_parts) < 3:
    #    return (None,None) #invalid input
    
    second_part_re = re.compile('pid-(?P<content_id>[0-9]{5,7})-dt-content-rid-(?P<attach_id>[0-9]{3,7})(_1)?')
    #third_part_re  = re.compile('(?:xid-(?P<attach_id2>[0-9]{3,7})(_1)?|(?P<courseword>course))')
    secon = second_part_re.match(url_parts[1])
    #thir = third_part_re.match(url_parts[2])
    
    if not secon:   
        LOG_debug("Second URL portion did not match RegEx.")
        return (None,None)
    daurl = "bbcswebdav/pid-{0[content_id]}-dt-content-rid-{0[attach_id]}_1/xid-{0[attach_id]}_1".format(secon.groupdict())
    
    if getinfo:
        LOG_debug("Getting file information...")
        linst = bb_inst._Blackboard__LOGIN_INST
        url = "{}/{}".format(linst.url_gen('domain'),daurl)
        
        pg_code,pg_url,pg_headers = linst.open(url,method='HEAD')
        pg_url_parsed = parse_url(pg_url)[0]
        url_parts = pg_url_parsed.path.strip('/').split('/')
        fname = None#
        fsz = None  #
        
        secon = second_part_re.match(url_parts[1])
        if not secon:
            LOG_debug("The new url_parts does not match RegEx; {!r}".format(url_parts[1]))
            return (None, None) #invalid input
        secon = secon.groupdict()
        content_id = int(secon['content_id'])
        attach_id  = int(secon['attach_id'])
        
        if len(url_parts) >= 5 and not url_parts[4].startswith('xid-{}'.format(attach_id)):
            fname = urllib.unquote(url_parts[4])
        tmp_sz = pg_headers.get('content-length')
        if isinstance(tmp_sz,basestring) and tmp_sz.isdigit() and int(tmp_sz) > 0:
                fsz = int(tmp_sz)
        mimetype = pg_headers.get('content-type')
        
        
        if pg_headers.get('location','').startswith(linst.url_gen('domain','webapps','login')):
                LOG_warning("NOT_LOGGED_IN")
                return NOT_LOGGED_IN  # ...not logged in
        if '/bbcswebdav' in pg_headers.get('location',''):
            LOG_debug("Reparsing...")
            return parse_webdav_url(pg_headers['location'],getinfo,bb_inst) #retry with the redirected page
        
        #BAD_URL, code=1; invalid URL syntax for bbcswebdav
        ERR_BAD_URL =        1*(pg_code == 500)
        #NO_SUCH_FILE, code=2; the file requested does not exist (at least at the requested URL)
        ERR_NO_SUCH_FILE =   2*(not fname and not ERR_BAD_URL)
        #NOT_LOGGED_IN, code=4; you're not logged in. This is only called if the requested file DOES exist
        ERR_NOT_LOGGED_IN =  4*(not (ERR_NO_SUCH_FILE or ERR_BAD_URL) and bool(pg_headers.get('www-authenticate')))
        #NOT_AUTHORIZED, code=8; you ARE logged in and the file exists, but you don't have permission to dl it.
        ERR_NOT_AUTHORIZED = 8*(not (ERR_NOT_LOGGED_IN or ERR_NO_SUCH_FILE) and pg_code == 404)
        
        ERR = ERR_BAD_URL | ERR_NO_SUCH_FILE | ERR_NOT_LOGGED_IN | ERR_NOT_AUTHORIZED
        
        if ERR or pg_code != 200:
            LOG_info("An error occured. :(")
        if not ERR and pg_code == 200:
            LOG_info("Success!")
            return (content_id,fname,attach_id,mimetype,(fsz,'B')) #All correct!!
        elif ERR_BAD_URL:
            return (None, None)
        elif ERR_NO_SUCH_FILE:
            return None
        elif ERR_NOT_LOGGED_IN:
            return NOT_LOGGED_IN
        elif ERR_NOT_AUTHORIZED:
            return False
        
        
        #no error detected, but code was NOT 200.
        
        from httplib import responses
        if pg_code // 100 == 3:
            if pg_headers.get('location','').startswith(linst.url_gen('webapps','login')):
                    return NOT_LOGGED_IN  # ...not logged in
            elif '/bbcswebdav' in pg_headers.get('location',''):
                return parse_webdav_url(pg_headers['location'],getinfo,bb_inst) #retry with the redirected page
            else:
                if pg_headers.get('location'):
                    raise BlackboardError("Blackboard returned a {!r} ({}) redirect to the location {!r}, which was not an expected value.".format(pg_code,responses.get(pg_code,"An error code you don't support..?"),pg_headers.get('location')),url=pg_url)
                elif pg_code in [301,302,303,304,307,308]:
                    raise BlackboardError("Blackboard returned a {!r} ({}) redirect, but did not provide a redirect location. That's just stupid.".format(pg_code,responses.get(pg_code,"An error code you don't support..?")),url=pg_url)
                else:
                    raise BlackboardError("Blackboard returned a redirect code that I cannot or will not follow ({}: {}).".format(pg_code,responses.get(pg_code,"(invalid code)")),url=pg_url)
        elif pg_code // 100 == 4:
            if pg_code in [401,423]: #DENIED!
                return NOT_LOGGED_IN
            elif pg_code in [400,405,406,409,417,422]: #request was invalid
                return (None,None)
            elif pg_code in [404,410]: #doesn't exist
                return None
            elif pg_code in [403]: #don't have permission
                return False
            elif pg_code in [402,407,413,451]: #WTF
                raise BlackboardError("Blackboard returned status code {}: {}. Yeahh...".format(pg_code,responses.get(pg_code,"(invalid code)")),url=pg_url)
            elif pg_code == 418:
                raise BlackboardError("Blackboard returned status code 418, and is currently a teapot.",code=418,url=pg_url)
            else: #other, e.g. 408,411,412,414,415,416,419, etc.
                raise BlackboardError("Status Code {} returned. Either Blackboard screwed something up, or there was a connection issue.".format(pg_code),url=pg_url)
        elif pg_code // 100 == 5:
            raise BlackboardError("Blackboard returned status code {}: {}.".format(pg_code,responses.get(pg_code,"(invalid code)")),url=pg_url)
        else:
            raise BlackboardError("Blackboard returned unexpected status code {}: {}.".format(pg_code,responses.get(pg_code,"(invalid code)")),url=pg_url)
    
    content_id = int(secon.group('content_id'))
    attach_id = int(secon.group('attach_id'))
    return (content_id,attach_id)

class content_object(object):
    
    __slots__ =('type','name','disabled','content_id','course_id','attachments','content_mdb_id',
                'assign_group_id','yt_id','yt_title','_bb_inst','_contents','ext_link','chainlink','_content_object__refs','_content_object__chlink')
    
    def __init__(self,bb_inst,**kwargs):
        self._contents = None
        self.__refs = ()
        self.__chlink = None
        self.attachments = ()
        self.type = kwargs.get('type',None)
        self.disabled = kwargs.get('disabled',None)
        self.course_id = kwargs.get('course_id',None)
        self.content_id = kwargs.get('content_id',None)
        self.name = kwargs.get('name',None)
        self.content_mdb_id = kwargs.get('content_mdb_id',None)
        self.assign_group_id = kwargs.get('assign_group_id',None)
        self.yt_id = kwargs.get('yt_id',None)
        self.yt_title = kwargs.get('yt_title',None)
        self._bb_inst = bb_inst
        self.ext_link = kwargs.get('ext_link',None)
        #chainlink means that the content is a link to other content,
        #   and just about anything on BB is possible to link to.
        #(Type): set to None if it is not a chainlink; if its value is
        #   True then it is waiting to be evaluated; otherwise, this
        #   attribute will be a link either to the appropriate content_object,
        #   or it will be an entirely new content_object.
        self.chainlink = kwargs.get('chainlink',kwargs.get('chain',None))
    
    def __repr__(self):
        return "<blackbird.content_object(type={},name={!r},course_id={},content_id={})>".format(self.type,self.name,self.course_id,self.content_id)
    
    
    ##ATTACHMENT STRUCTURE
    ## (filename, id, mime, size)
    #############################
    ## filename:    the BASENAME of the attachment  [REQUIRED]
    ##       id:    the webdav id of the attachment [REQUIRED]
    ##     mime:    the mimetype of the attachment
    ##     size:    a tuple; (bytes, suffix). (None,None) if unknown. 
    
    ### ATTACHMENT FUNCTIONS
    
    def add_attachment(self,*args):
        #args = [ (proper-file-name, attach_id, mimetype, size_tuple) , ... ]
        attchmnts = list(self.attachments)
        for arg in args:
            if type(arg) not in [tuple,list]:
                raise ValueError, "add_attachment must be passed a tuple or list of four items, not {!r}".format(type(arg))
            if len(arg) != 4:
                raise ValueError, "add_attachment must be of length 4, not {}".format(len(arg))
            nem, _id, mmtyp, sz = arg
            
            if not isinstance(nem,basestring):  raise ValueError, "add_attachment {}[0] must be a string".format(arg)
            if not isinstance(_id,int):         raise ValueError, "add_attachment {}[1] must be an int".format(arg)
            if not isinstance(mmtyp,basestring):raise ValueError, "add_attachment {}[2] must be a string".format(arg)
            if not isinstance(sz,tuple):        raise ValueError, "add_attachment {}[3] must be a tuple".format(arg)
            
            attchmnts.append(arg)
        
        object.__setattr__(self,'attachments',tuple(attchmnts))
    
    def get_attachment(self, filename_or_id):
        spos = 0
        if not isinstance(filename_or_id,basestring):
            if not isinstance(filename_or_id,int):
                raise TypeError, "get_attachment argument should be a string or int"
            spos = 1
        
        for attch in self.attachments:
            if attch[spos] == filename_or_id:
                return attch
        return None
    
    def download_attachment(self, filename_or_id):
        try:
            y = self.get_attachment(filename_or_id)
            if not y:
                return None
        except TypeError, msg:
            raise TypeError, msg.replace('get_','download_',1)
        
        fullname, attach_id, mimetyp, size_tuple = y
        linst = self._bb_inst._Blackboard__LOGIN_INST
        url = linst.url_gen('domain')+'/bbcswebdav/pid-{0}-dt-content-rid-{1}_1/xid-{1}_1'.format(self.content_id,attach_id)
        x = self._bb_inst.login()
        if x:
            return self._bb_inst._Blackboard__LOGIN_INST.open(url,file_download=True)
        return NOT_LOGGED_IN
    
    def get_ids(self):
        return [x[1] for x in self.attachments]
    
    
    #If type == 'folder' and _bb_inst is defined, recurses through folders
    #   and generates their _contents attributes
    def walk_contents(self,recurse_limit=3):
        
        if recurse_limit <= 0:
            return StopIteration
        
        if not self._bb_inst:
            raise Exception, "'_bb_inst' must be set before using any active " \
                             "parsing functions."
        
        if self.type != "folder":
            return NA
        
        if not self.course_id or not self.content_id:
            return None
        
        lgn_inst = self._bb_inst._Blackboard__LOGIN_INST
        opnr = lgn_inst.open
        
        req_fmt = lgn_inst.url_gen('domain','webapps') + "/blackboard/content/listContent.jsp?course_id={}&content_id={}"
        
        my_bb_pg = opnr(req_fmt.format(self.course_id, self.content_id), retry_login = 1)
        if my_bb_pg is NOT_LOGGED_IN:
            return NOT_LOGGED_IN
        my_parsed = page_parsing(my_bb_pg.soup,self._bb_inst,'bb_list_content')
        
        if 'content' in my_parsed:
            x = tuple(my_parsed['content'])
            object.__setattr__(self,'_contents',x)
            object.__setattr__(self,'_content_object__refs', tuple(clazz.content_id for clazz in x if clazz.content_id ))
        else:
            return False
        
        
        foldrz = [x for x in self._contents if x.is_folder]
        otherz = list(set(self._contents) - set(foldrz))
        out_list = []
        
        for other in otherz:
            if other._bb_inst is None:
                other._bb_inst = self._bb_inst
        
        for foldr in foldrz:
            
            if foldr._bb_inst is None:
                foldr._bb_inst = self._bb_inst
            
            x = foldr.walk_contents(recurse_limit-1)
            if x is StopIteration:
                break
        
        return True
    
    
    ## ACCESSORS AND MUTATORS
    
    @property
    def chainlink(self):
        if self.__chlink is None:
            return None
        return self.__chlink
    
    @property
    def is_folder(self):
        if self.type == 'folder':
            return True
        return False
    
    @property
    def all_set_attrs(self):
        ret = []
        for attr in self.__slots__:
            x = getattr(self,attr)
            if x is None or x == ():
                continue
            ret.append(attr)
        return ret
    
    def has_contentitem(self,key,specific=False,extend=False):
        if not self._contents:
            if self._contents is None and extend:
                self.walk_contents()
                return self.has_contentitem(key,specific)
            return False
        if specific or key in self.__refs:
            return (key in self.__refs)
        for v in self._contents:
            if v.has_contentitem(key):
                return True
        return False
    
    def get_contentitem(self,key,specific=False,extend=False):
        if not self._contents:
            if self._contents is None and extend:
                self.walk_contents()
                return self.get_contentitem(key,specific)
            return None
        if specific or key in self.__refs:
            x = (key in self.__refs) or None
            if x:
                for v in self._contents:
                    if v.content_id == key:
                        x = v
                        break
            return x
        for v in self._contents:
            x = v.get_contentitem(key)
            if x:
                return x
        return None
    
    def _get_accepted_types(self):
        return ('assignment','blog','document','file','folder','lesson',
                        'lessonplan','link','SafeAssign','selfpeer',
                        'survey','test','youtube','UNKNOWN')
    
    def _generate_bb_url(self):
        
        #if not correct content-type
        #    return
        urlgen = self._bb_inst._Blackboard__LOGIN_INST.url_gen
        dapath='/webapps'
        STANDARD = "course_id={}&content_id={}".format(self.course_id,self.content_id)
        if self.type == 'folder':
            dapath += '/blackboard/content/listContent.jsp?{}'
        elif self.type == 'SafeAssign' and self.content_mdb_id:
            dapath += '/mdb-sa-bb_bb60/submitPaper?{}&content_mdb_id={}'.format('{}',self.content_mdb_id)
        elif self.type == 'blog':
            dapath += '/blackboard/content/launchLink.jsp?{}&mode=view'
        elif self.type == 'selfpeer':
            dapath += '/bb-selfpeer-bb_bb60/contentType/view.jsp?{}'
        elif self.type == 'assignment':
            assgn_g_id = self.assign_group_id or ''
            dapath += '/blackboard/execute/uploadAssignment?{}&assign_group_id={}&mode=view'.format('{}',assgn_g_id)
        elif self.type == 'lesson':
            dapath += '/webapps/blackboard/execute/displayLearningUnit?{}'
        elif self.type == 'lessonplan':
            dapath += '/webapps/blackboard/execute/manageLessonPlan?dispatch=view&{}'
        else:
            return None
        
        if '{}' in dapath:
            dapath = dapath.format(STANDARD)
        
        return urlgen('domain','webapps','login')+'/?new_loc='+urllib.quote(dapath)
        
    
    def __setattr__(self,name,val):
        name_classes = {'type':basestring,'disabled':None,'content_id':int,
                      'name':basestring,'content_mdb_id':int,'yt_id':basestring,
                      'assign_group_id':None,'yt_title':basestring,'course_id':int,
                      '_bb_inst':Blackboard,'ext_link':basestring}
        type_values  = self._get_accepted_types()
        
        if name == 'chainlink':
            return
        
        if name[:17] == '_content_object__' and name in content_object.__slots__:
            inter_nem = name[17:]
            
            if inter_nem in ['chlink']:
                pass
            
            else:
                try:
                    _ = getattr(self,name)
                except: pass
                else:
                    raise AttributeError, "'content_object' already has a *__{} attribute".format(inter_nem)
            object.__setattr__(self,name,val)
            return
        
        if name == '_contents':
            try:
                _ = self._contents
            except: pass
            else:
                raise AttributeError, "'content_object' already has a _contents attribute"
            object.__setattr__(self,name,val)
            return
        
        if name == '_bb_inst':
            try:
                _ = self._bb_inst
            except:
                pass
            else:
                if type(self._bb_inst) is Blackboard:
                    raise AttributeError, "'content_object' already has a parent Blackboard instance"
            
            if type(val) is not Blackboard and val is not None:
                raise TypeError, "'_bb_inst' attribute of 'content_object' must be a Blackboard instance"
            object.__setattr__(self,'_bb_inst',val)
            return
        
        if name == 'attachments':
            try:
                _ = self.attachments
            except Exception:
                object.__setattr__(self,'attachments',val)
                return
            raise AttributeError, "Cannot set 'attachments' attribute"
        
        if name not in name_classes:
            raise AttributeError, "'content_object' object has no attribute {!r}".format(name)
        if not (val is None or name_classes[name] is None or \
                issubclass(val.__class__,name_classes[name])):
            nemz = name_classes[name]
            if type(nemz) is tuple:
                nemz = ' or '.join([x.__name__ for x in nemz])
            raise TypeError, "{!r} attribute must be of type {}, not {!r}".format(name,nemz,type(val))
        
        if name == 'type':
            if val not in type_values and val is not None:
                LOG_warning("Found unpredicted content_object type value {!r}".format(val))
        elif name == 'disabled':
            val = bool(val)
        
        #Specifics
        if name == 'ext_link' and val:
            val = val.strip()
            if '://' in val[:13]:
                pass
            elif val.startswith('javascript:'):
                return
            elif val.startswith('/bbcswebdav'):
                ret = parse_webdav_url(val,True,self._bb_inst)
                if ret is NOT_LOGGED_IN:
                    return #This really isn't expected at all, seeing as ext_link is set by the parser
                if ret is None or (None, None): 
                    return #awesome! File doesn't exist or invalid url
                if ret is False: 
                    return #You... don't have access to that page??
                self.add_attachment( ret[1:] )
                return
            else:
                val = 'http://{}'.format(val)
            
            parse_res,qry = parse_url(val)
            if parse_res.netloc.lower() == 'youtube.com':
                i = qry.get('v')
                if i:
                    self.yt_id = i
                    return
            elif parse_res.netloc.lower() == 'youtu.be':
                i = parse_res.path.strip('/')
                if i:
                    self.yt_id = i
                    return
        
        object.__setattr__(self,name,val)
    
    def __getitem__(self,key):
        if key in self.__slots__ and key[0] != '_':
            return getattr(self,key)
        if key == 'contents' or key == 'content':
            return self._contents
        raise KeyError, "'content_object' object has no attribute {!r} acces" \
                        "sible via __getitem__. [content_object uses __getit" \
                        "em__ for accessing attributes that describe the con" \
                        "tent, e.g. 'attachments' and 'content_id'".format(key)
    

def page_parsing(soup,bb_inst,*page_type):
    """Attempts to parse template-type pages and collect relevant information.
    
    PARAMETERS:
        soup        a BeautifulSoup object for the page to be parsed
        page_type   IF the type of page is know, it is provided and parsed.
                    IF the type is unknown (no page_type provided), attempts to
                        parse it to determine type and if successful returns
                        relevant information.
    -
    SUPPORTED PAGE-TYPES:
        bb_error_page     bb_list_content   bb_stream
    -
    RETURN VALUES:
        None                An error occurred during parsing, e.g. unparsable 
                                soup.
        False               No meaningful information was found. Hopefully this
                                is rare.
        [Premade Object]    Returns information about the page. See the section
                                below.
    -
    PREMADE RETURN OBJECTS:
        When a page is found/confirmed to be a certain page_type, a mapping
            object is returned with AT LEAST a key 'page_type' that is  the 
            page's type. Other keys will depend on the page type.
    """
    
    if type(soup).__name__ != 'BeautifulSoup': raise TypeError('Invalid type ' \
            'argument passed to page_parsing function.')
    if len(soup) is 0: return None
    tenttv_title = soup.title
    plchldr = soup.find('li',class_="placeholder")
    tenttv_title =  "Title: {!r}".format(tenttv_title.get_text(strip=True) if tenttv_title else None)
    plchldr =  "Placeholder-text: {!r}".format(plchldr.get_text(strip=True)) if plchldr else ""
    LOG_debug("Begin Parsing Page:  {}, {}".format(tenttv_title,plchldr))
    
    page_type_list = ['bb_error_page','bb_list_content','bb_stream']
    real_page_types = []
    
    Returner = {}
    
    comment_finder = lambda text: isinstance(text,bs4.Comment)
    
    for arg in page_type:
        if not isinstance(arg,basestring): continue
        arg = arg.lower().replace(' ','_').replace('-','_')
        if arg in page_type_list:
            real_page_types.append(arg)
    
    def err_comment_path(elem):
        #\web\course\noContentError.jsp
        comment_excluders = ["checkguest=","copyright blackboard"]
        ele = elem.lower()
        if any([True for excldr in comment_excluders if excldr in ele]):
            return None
        comm = soup.contents[i].strip()
        _bgn_comment = {'errorfile':None,'full':None,'file':None}
        fl = os.path.basename(comm)
        _bgn_comment['full'] = comm
        _bgn_comment['file'] = fl
        if re.match(r'.*([1-5][0-9]{0,2}|error|noStream|noContentError)\.jsp',fl):
            _bgn_comment['errorfile']=fl
        return _bgn_comment
    
    #bgn_comment_re = re.compile(r'\s*(?P<full>.*[/\\]?(?P<file>(?P<errorfile>[1-5][0-9]{2}|error|noStream)?.*?)?\.jsp)\s*',re.I)
    bgn_comment = None
    for i in range(5):
        if len(soup.contents)<(i+1):
            break
        if type(soup.contents[i]).__name__ == 'Comment':
            x = err_comment_path(soup.contents[i])
            if x:
                bgn_comment = x
                break
            #bgn_comment = bgn_comment_re.match(soup.contents[i]).groupdict()
    
    discov_isError = discov_isStream = discov_isListContent = False
    
    ##new error comment
    body_bgn_comment = soup.body.find(text=comment_finder)
    if body_bgn_comment:
        x = err_comment_path(body_bgn_comment)
        if not x:
            body_bgn_comment = None
        else:
            body_bgn_comment = x
            
    
    if bgn_comment:
        if bgn_comment['errorfile']:
            discov_isError = bgn_comment['errorfile']
            if 'stream' in bgn_comment['full'].lower():
                Returner['error_type']='stream'
            #TODO: Other error types
        else:
            if 'stream' in bgn_comment['full'].lower():
                discov_isStream = bgn_comment['full']
                Returner['page_type']='bb_stream'
                if 'grade' in bgn_comment['file']:
                    Returner['stream_type']='grade'
                #TODO: other stream types
            
            
            if 'listContent' in bgn_comment['full']:
                discov_isListContent=True
                Returner['page_type']='listContent'
    elif body_bgn_comment:
        if body_bgn_comment['errorfile']:
            discov_isError = body_bgn_comment['errorfile']
    
    
    
    elif soup.body and len(soup.body) > 0 and len(soup.body.find_all(True)) \
                                                                        == 0:
        discov_isError = True
        Returner['error_type']='generic'
    
    pageTitleText = soup.find(id='pageTitleText')
    contentPanel_error = soup.find(id='contentPanel',class_='error')
    grades_stream_div = soup.find(id='streamDetail')
    error_paletteTitleHeading = soup.find(id='error_paletteTitleHeading')
    general_stream_div = soup.find(class_='stream_full')
    
    if pageTitleText and 'error' in pageTitleText.get_text(strip=True).lower():
        discov_isError = True
        if 'error_type' not in Returner:
            Returner['error_type']='generic'
    
    if discov_isError or 'bb_error_page' in real_page_types or \
                                                        contentPanel_error:
        Returner['page_type']='bb_error_page'
        RET_error_title = ''
        RET_error_msg = ''
        RET_error_errorid = ''
        
        if contentPanel_error:
            error_title = contentPanel_error.find('span',id='pageTitleText')
            
            if error_title:
                
                if error_title.find(attrs={'style':'color:;'}):
                    RET_error_title = error_title.find(attrs={ \
                                                    'style':'color:;'}).string
                
                elif error_title.find('span') and \
                            len(error_title.find('span')) ==1:
                    RET_error_title = error_title.find('span').string
                    
            receiptTag = contentPanel_error.find(id='bbNG.receiptTag.content')
            
            if receiptTag:
                
                if len(receiptTag) == 1:
                    RET_error_msg = receiptTag.string
                elif len(receiptTag) > 1:
                    
                    for i in receiptTag.contents:
                        
                        if type(i).__name__ == 'Tag' and i.name not in \
                                                                    ['br','p']:
                            if i.name == 'strong':
                                RET_error_msg += i.string+': '
                        
                        if type(i).__name__ == 'NavigableString' and \
                                    len(i.split()):
                            RET_error_msg += i
                captnTxt = receiptTag.find(class_='captionText')
                
                if captnTxt:
                    RET_error_errorid = captnTxt.string. \
                            partition('Error ID is ')[2][:-1]
        
        elif soup.body and len(soup.body) > 0 and \
                        len(soup.body.find_all(True)) == 0:
            RET_error_msg = soup.body.string.strip()
        
        elif soup.find(class_='warnFont'):
            RET_error_msg = soup.find(class_='warnFont')
            RET_error_title = pageTitleText.string.strip()
        
        elif error_paletteTitleHeading:
            error_part = error_paletteTitleHeading.find(id="error_link")
            
            if error_part:
                RET_error_title = error_link.get_text(strip=True)
            error_part = error_paletteTitleHeading.find_next_sibling(id="error_contents")
            
            if error_part:
                x = error_part.find(class_="bad")
                
                if x:
                    RET_error_msg = x.stripped_strings.next()
                    x = x.find(class_="captionText")
                    if x:
                        x = x.get_text(strip=True)
                        if 'Error ID' in x:
                            x = x.rsplit(None,1)[-1]
                            if x[-1] == '.':
                                x = x[:-1]
                            RET_error_errorid = x
        
        Returner['error_title']=RET_error_title
        Returner['error_msg']=RET_error_msg
        Returner['errorid']=RET_error_errorid
        Returner[NotImplemented]=NotImplemented
    
    else:
        url_js_re = re.compile(".*?\(\'(?P<lnk>.+?)\'\).*")
        
        if discov_isStream or 'bb_stream' in real_page_types or \
                    grades_stream_div or general_stream_div:
            #is a stream
            
            if grades_stream_div or Returner['stream_type'] == 'grades':
                #is a grade_stream
                
                hasstats = soup.find('div',class_="has-stats")
                if hasstats:
                    gr_dct = {} # 
                    itr = hasstats.h3
                    curr_sect = itr.string.strip()
                    #gr_dct[curr_sect] = {}
                    
                    for part in itr.next_siblings:
                        if type(part).__name__ != 'Tag':
                            continue
                        
                        if part.name == 'h3':
                            curr_sect = part.string
                            #if curr_sect not in gr_dct: gr_dct[curr_sect] = {}
                        
                        elif part.name == 'div' and 'grade-item' in part.get('class',[]):
                            this_gr = {'timestamp':None,'grades':{},'description':None,'grading criteria':None}
                            focus_div = part.find('div',class_='name',recursive=False)
                            
                            if not focus_div:
                                raise EnvironmentError, "Grade found without 'name' attribute while parsing mygrade page"
                            
                            if focus_div.a:
                                if focus_div.a['href'] == '#' and focus_div.a.has_attr('onclick'):
                                    lnk = url_js_re.match(focus_div.a['onclick'])
                                    if lnk:
                                        this_gr['link'] = lnk.group('lnk')
                                elif focus_div.a['href'] != '#':
                                    this_gr['link'] = focus_div.a['href']
                            this_gr['name'] = focus_div.get_text(strip=True)
                            
                            focus_div = part.find('div',class_='info',recursive=False)
                            if focus_div and focus_div.span:
                                tstmp = focus_div.get_text(strip=True)
                                try:
                                    this_gr['timestamp'] = datetime.datetime.strptime(tstmp,BB_DATE_FORMAT)
                                except ValueError:
                                    LOG_exception('Failed to parse timestamp of grade named {!r}'.format(this_gr['name']))
                            
                            focus_div = part.find('table',class_='gradeTable',recursive=False)
                            if focus_div and focus_div.tr:
                                for td in focus_div.tr.find_all('td',recursive=False):
                                    score = td.contents[2]
                                    if td.div:
                                        score = td.div.contents[0]
                                    
                                    if td.img:
                                        score = web_img(td.img)
                                    else:
                                        score = number_finder(score,0,True)
                                        if score == '-':
                                            score = None
                                    label = td.find('span',class_='grade-label').string
                                    if isinstance(label,basestring):
                                        label = label.strip().lower()
                                    this_gr['grades'][label] = score
                                    
                                    outof = td.find('span',class_='outof')
                                    if outof:
                                        #outof = outof.string.strip().strip('/')
                                        outof = number_finder(outof.string,1|2)
                                        this_gr['grades']['outof'] = outof
                            
                            focus_div = part.find('div',class_='eval-links')
                            if focus_div:
                                for inpt in focus_div.find_all('input'):
                                    if not inpt.has_attr('value'):
                                        continue
                                    valu = inpt['value'].lower()
                                    comment = inpt.find_previous_sibling('div')
                                    if comment and comment.get_text(strip=True):
                                        this_gr[str(valu)] = comment.get_text(strip=True)
                            
                            this_gr['section'] = curr_sect
                            if part.has_attr('id') and 'external' in part['id']:
                                gr_dct['TOTAL'] = this_gr
                            else:
                                gr_dct[this_gr['name']] = this_gr
                    
                    submitted_grades = hasstats.find_next_sibling('div',class_="submitted-grades")
                    
                    if submitted_grades and submitted_grades.h3:
                        itr = submitted_grades.h3
                        curr_sect = itr.string.strip()
                        
                        for part in itr.next_siblings:
                            if type(part).__name__ != 'Tag':
                                continue
                            
                            if part.name == 'h3':
                                curr_sect = part.string.strip()
                            
                            elif part.name == 'div' and 'grade-item' in part.get('class',[]):
                                this_gr = {'grades':{}, 'section': curr_sect, 'description':None, 'grading criteria':None}
                                focus_div = part.find('div',class_='name',recursive=False)
                                
                                if focus_div.a:
                                    if focus_div.a['href'] == '#' and focus_div.a.has_attr('onclick'):
                                        lnk = url_js_re.match(focus_div.a['onclick'])
                                        if lnk:
                                            this_gr['link'] = lnk.group('lnk')
                                    elif focus_div.a['href'] != '#':
                                        this_gr['link'] = focus_div.a['href']
                                this_gr['name'] = focus_div.get_text(strip=True)
                                
                                focus_div = part.find('div',class_='info',recursive=False)
                                
                                if focus_div and focus_div.span:
                                    tstmp = focus_div.get_text(strip=True)
                                    try:
                                        this_gr['timestamp'] = datetime.datetime.strptime(tstmp,BB_DATE_FORMAT)
                                    except ValueError:
                                        LOG_exception('Failed to parse timestamp of grade named {!r}'.format(this_gr['name']))
                                
                                focus_div = part.find('div',class_='eval-links')
                                if focus_div:
                                    for inpt in focus_div.find_all('input'):
                                        if not inpt.has_attr('value'):
                                            continue
                                        valu = inpt['value'].lower()
                                        comment = inpt.find_previous_sibling('div')
                                        if comment and comment.get_text(strip=True):
                                            this_gr[valu] = comment.get_text(strip=True)
                                
                                gr_dct[this_gr['name']] = this_gr
                    
                    
                    upcoming_grades = hasstats.find_next_sibling('div',class_="upcoming-grades")
                    
                    if upcoming_grades and upcoming_grades.h3:
                        itr = upcoming_grades.h3
                        curr_sect = itr.string.strip()
                        #if curr_sect not in gr_dct:     gr_dct[curr_sect] = {}
                        
                        for part in itr.next_siblings:
                            if type(part).__name__ != 'Tag':
                                continue
                            
                            if part.name == 'h3':
                                curr_sect = part.string.strip()
                            
                            elif part.name == 'div' and 'grade-item' in part.get('class',[]):
                                this_gr = {'grades':{}, 'timestamp':None, 'section': curr_sect, 'description':None, 'grading criteria':None}
                                focus_div = part.find('div',class_='upcoming',recursive=False)
                                
                                if focus_div:
                                    outof = focus_div.find('span',class_='outof')
                                    if outof:
                                        #outof = outof.string.strip().strip('/')
                                        outof = number_finder(outof.string,1|2)
                                        this_gr['grades']['outof'] = outof
                                
                                focus_div = part.find('div',class_='name')
                                
                                if not focus_div:
                                    raise EnvironmentError, "Upcoming Grade found without 'name' attribute while parsing mygrade page"
                                this_gr['name'] = focus_div.get_text(strip=True)
                                
                                focus_div = part.find('div',class_='info')
                                if focus_div:
                                    tstmp = focus_div.find('span',class_='timestamp')
                                    if tstmp:
                                        tstmp = tstmp.get_text(strip=True)
                                        if tstmp.startswith('Due:'):
                                            tstmp = tstmp[4:].strip()
                                        try:
                                            this_gr['timestamp'] = datetime.datetime.strptime(tstmp,BB_DATE_FORMAT)
                                        except ValueError:
                                            LOG_exception('Failed to parse timestamp of grade named {!r}'.format(this_gr['name']))
                                
                                focus_div = part.find('div',class_='eval-links')
                                if focus_div:
                                    for inpt in focus_div.find_all('input'):
                                        if not inpt.has_attr('value'):
                                            continue
                                        valu = inpt['value'].lower()
                                        comment = inpt.find_previous_sibling('div')
                                        if comment and comment.get_text(strip=True):
                                            this_gr[valu] = comment.get_text(strip=True)
                                
                                gr_dct[this_gr['name']] = this_gr
                    
                    Returner['grades'] = gr_dct
                
                else:
                    Returner['grades'] = gr_dct
            
            else:
                Returner[NotImplemented]=NotImplemented
            
        elif discov_isListContent or 'bb_list_content' in real_page_types:
            
            
            contentForm = soup.find('form',attrs={'name':'contentForm','method':'POST'})
            course_id,content_id = None,None
            if contentForm and contentForm.has_attr('action') and 'course_id' in contentForm['action']:
                contentForm_dct = parse_url(contentForm['action'])[1]
                course_id = number_finder(contentForm_dct['course_id'],1)
                if 'content_id' in contentForm_dct:
                    content_id = number_finder(contentForm_dct['content_id'],1)
            Returner['course_id'] = course_id
            Returner['content_id'] = content_id
            
            listTitle = soup.find('span',id='pageTitleText')
            if listTitle:
                Returner['title']=listTitle.get_text(strip=True)
            
            #contentListItemRegex = re.compile('^contentListItem\:\_(?P<c_id>[0-9]+)\_1$')
            
            listContentDiv = soup.find(id='content_listContainer')
            listContentItems = []
            item_list = []
            if listContentDiv:
                listContentItems = listContentDiv.find_all('li',recursive=False)
            else:
                noItems = soup.find('div',id='containerdiv')
                if not (noItems and noItems.find('div',class_="noItems")):
                    LOG_error("Failed to find either 'content_listContainer' or 'noItems' divs while parsing listContent page.")
            
            for itm in listContentItems:
                item_dict = {}
                
                item_obj = content_object(bb_inst,course_id=course_id)
                
                icon = itm.find('img',class_='item_icon',recursive=False)
                item_div = itm.find('div',class_='item',recursive=False)
                details = itm.find(class_='details',recursive=False)
                
                if not item_div:
                    LOG_warning("Found content li with no <div class=\"item...> element (crs_id:{},cntnt_page_id:{}). Skipping this content.".format(course_id,content_id))
                    continue
                elif item_div.has_attr('id'):
                    x = number_finder(item_div['id'],1)
                    if x:
                        item_obj.content_id=x
                
                if icon and icon.has_attr('src'):
                    icon_src = icon['src'].strip()
                    icon_base = icon_src.rsplit('/',1)[1].split('.')[0]
                    if icon_base.endswith('_on'):
                        item_obj.type = icon_base[:-3]
                    elif icon_base.endswith('_non'):
                        item_obj.type = icon_base[:-4]
                        item_obj.disabled = True
                    
                    elif 'bb_bb60' in icon_src:
                        for typ in ['youtube','SafeAssign','selfpeer','wiki']:
                            if typ in icon_src:
                                item_obj.type = typ
                                break
                elif not icon:
                    LOG_warning("Found content li with no <img class=\"item_icon...> element. (crs_id:{},cntnt_page_id:{}). Hopefully we'll figure out the type later.".format(course_id,content_id))
                else:
                    LOG_warning("Found content li whose item_icon has no 'src' attribute. (crs_id:{},cntnt_page_id:{},cntnt_id:{}). Hopefully we'll figure out the type later.".format(course_id,content_id,item_obj.content_id))
                
                if item_obj.type is None:
                    item_obj.type = 'UNKNOWN'
                
                if item_div and item_div.has_attr('id'):
                    
                    if item_div.h3:
                        cntnts = item_div.h3.find_all(True,recursive=False)
                        if cntnts and len(cntnts) >= 2:
                            nem = cntnts[1]
                            
                            if nem.name == 'img' and nem.get('title') == 'linked item':
                                item_obj.chainlink = True
                                nem = cntnts[2]
                            
                            item_obj.name = nem.get_text(strip=True)
                            
                            LOG_debug("item_obj.name = {!r}".format(item_obj.name))
                            
                            if nem.name == 'a' and nem.has_attr('href'):
                                
                                prs_res,nem_qry = parse_url(nem['href'].strip())
                                
                                
                                if item_obj.type == 'UNKNOWN':
                                    if 'listContent' in prs_res.path:
                                        item_obj.type = 'folder'
                                    elif prs_res.path.endswith('submitPaper'):
                                        item_obj.type = 'SafeAssign'
                                    elif 'selfpeer' in prs_res.path:
                                        item_obj.type = 'selfpeer'
                                    elif 'uploadAssignment' in prs_res.path:
                                        item_obj.type = 'assignment'
                                    elif 'bbcswebdav' in prs_res.path:
                                        item_obj.type = 'file'
                                    elif 'acxiom' in prs_res.path:      #/webapps/bbgs-acxiom-bb_bb60/execute/acxiomGateway?course_id=%&content_id=%&mode=view
                                        item_obj.type = 'test'
                                
                                if item_obj.type == 'SafeAssign':
                                    item_obj.content_mdb_id = number_finder(nem_qry.get('content_mdb_id',item_dict['content_id']),1)
                                elif item_obj.type == 'assignment':
                                    x = nem_qry.get('assign_group_id',None)
                                    if x:
                                        item_obj.assign_group_id = number_finder(x,1,True)
                                elif item_obj.type == 'file' and 'bbcswebdav' in prs_res.path:
                                    retval = parse_webdav_url(prs_res.path,True,bb_inst)
                                    LOG_info("Found 'file' type; parse_wedav_url returned {!r}".format(retval))
                                    if retval and retval != (None,None):
                                        item_obj.add_attachment( retval[1:] )
                                elif item_obj.type == 'link':
                                    item_obj.ext_link = nem['href'].strip()
                        else:
                            LOG_info("###LOG: Found content div with an h3 element of less than two divs (ids:{},{})".format(course_id,content_id))
                
                if item_obj.content_id is None:
                    x = itm.find('div',class_="moduleSample",recursive=False)
                    item_obj.content_id = number_finder(x['id'],1)
                
                if details:
                    attchmnts = details.find('ul',class_='attachments')
                    vtbegen = details.find('div',class_='vtbegenerated')
                    
                    if attchmnts:
                        #attach_list = []
                        
                        for attch in attchmnts.find_all('li',recursive=False):
                            a_lnk = attch.find('a',recursive=False)
                            if not (a_lnk and a_lnk.has_attr('href')):
                                continue
                            link = a_lnk['href']
                            file_nem = a_lnk.get_text(strip=True)
                            
                            
                            retval = parse_webdav_url(link,True,bb_inst)
                            LOG_info("Found attachment; parse_wedav_url returned {!r}".format(retval))
                            if retval and retval != (None,None):
                                item_obj.add_attachment( retval[1:] )
                            
                            #file_sz = a_lnk.find_next_sibling('span')
                            #if file_sz and file_sz.get('id','').endswith('fileSize'):
                            #    file_sz = byte_prefix(file_sz.get_text(strip=True),value_bin=True,return_power=0)
                            #else:
                            #    file_sz = (None,None)
                            #item_obj.add_attachment( (file_nem,file_id,file_sz) )
                    
                    if vtbegen:
                        yt = vtbegen.find('a',class_="lb")
                        
                        if yt and yt.has_attr('title'):
                            href = parse_url(yt['href'].strip())
                            title = yt['title'].strip()
                            yt_id = None
                            if 'youtu.be' in href[0].netloc:
                                yt_id = href[0].path.split('/',2)[1]
                            else:
                                yt_id = href[1].get('v')
                            
                            item_obj.yt_id = yt_id
                            item_obj.yt_title = title
                        
                item_list.append(item_obj)
            
            Returner['content']=item_list
    return Returner


class downloadable_file(object):
    
    def __init__(self, fileobj):
        attr = {}
        
        if isinstance(fileobj,urllib2.HTTPError):
            fileobj.fp = fileobj.fp.fp
        if not isinstance(fileobj,urllib.addinfourl):
            raise TypeError, "Argument of downloadable_file should be an addinfourl object"
        
        attr['code'] = fileobj.code or -1
        attr['url'] = fileobj.url
        attr['name'] = urllib.unquote(os.path.basename(attr['url']))
        attr['msg'] = fileobj.msg or ''
        attr['headers'] = fileobj.headers.dict
        tmp_len = attr['headers'].get('content-length')
        tmp_len = int(tmp_len) if tmp_len else None
        attr['total_length'] = tmp_len
        attr['length_remaining'] = tmp_len
        
        if not fileobj.fp or not isinstance(fileobj.fp,urllib2.socket._fileobject):
            raise TypeError, "Argument of downloadable_file has a closed or unexpected-type socket fileobject."
        attr['fp'] = fileobj.fp
        attr['bufsize'] = fileobj.fp.bufsize
        
        def _priv_get(nem):
            if nem == 'closed':
                if attr['fp'] and attr['fp'].closed:
                    return True
                if not attr['fp']:
                    return True
                return False
            if nem == 'fp':
                raise KeyError, "downloadable_file object has no public attribute 'fp'"
            elif nem == 'headers':
                return attr['headers'].copy()
            elif nem in attr:
                return attr[nem]
            raise KeyError, "downloadable_file object has no attribute {!r}".format(nem)
        self.__priv_get = _priv_get
        
        def read(sz=None):
            if attr['fp'].closed:
                raise ValueError, "Cannot read from a closed file"
            if not isinstance(sz,int) or sz < 0:
                sz = attr['length_remaining']
            
            len_rem = attr['length_remaining']
            
            readout = ''
            try:
                readout = attr['fp'].read(sz)
                if len_rem is not None:
                    if not readout:
                        len_rem = 0
                    if len(readout) >= len_rem:
                        len_rem = 0
                    else:
                        len_rem -= len(readout)
                    attr['length_remaining'] = len_rem
                return readout
            finally:
                if attr['length_remaining'] is not None and attr['length_remaining'] <= 0:
                    attr['fp'].close()
        self.read = read
        
        def read_to(file_target,**kwargs):
            """Reads data directly into a file. This is the recommended method.
            
            file_target should be either:
                1. a file-like object, including 'write' and 'close' methods.
                2. a string, representing a filepath. If the path exists and
                    is a file, it WILL be overwritten; if it is a directory,
                    the file will be written to the directory. If it does
                    not exist, an IOError will be raised.
            -
            kwargs:
            
            'noclose'   a bool that is only respected if file_target is a
                        file-like object. If True, file_target will not 
                        be closed.
            'progress_funct'    a callable object with one argument. It
                        will be passed a number representing the percent
                        compeletion of the download.
            'progress_prec'     an int/float specifying how often 
                        progress_funct will be called; for example, if its
                        value is 1, progress_funct will not be called unless
                        1% of progress has been made since the last call.
                        [Default: 1]
            -
            NOTE: If attempting to use the progress_* keywords, make sure
                to check that the 'total_length' attribute is not None.
                If None, the filesize is indeterminate, and progress_funct
                will not be called.
            """
            noclose = kwargs.get('noclose',False)
            progress_funct = kwargs.get('progress_funct',kwargs.get('progress_function',None))
            progress_prec = kwargs.get('progress_prec',kwargs.get('progress_precision',1))
            if progress_funct and not callable(progress_funct):
                raise TypeError, "progress_funct keyword argument must be callable"
            elif progress_funct:
                if not isinstance(progress_prec,(int,float)):
                    raise TypeError, "progress_prec keyword argument must be an int/float"
                if progress_prec < 0.1:
                    progress_prec = 0.1
            
            
            if isinstance(file_target,basestring):
                noclose = False
                if os.path.exists(file_target):
                    if os.path.isdir(file_target):
                        file_target = os.path.join(file_target,attr['name'])
                else:
                    if not os.path.exists(os.path.dirname(file_target)):
                        raise IOError, "Path supplied to read_to() does not exist, or is inaccessible."
                file_target = open(file_target, 'wb')
            elif not hasattr(file_target,'write'):
                raise TypeError, "Argument of read_to() should be a file-like object, or at least have a 'write' method"
            elif not (noclose or hasattr(file_target,'close')):
                raise TypeError, "Argument of read_to() has no close method"
            if hasattr(file_target,'method') and os.name == 'nt' and 'b' not in file_target.method:
                LOG_warning("File-like object passed to read_to() is not in binary mode, which can corrupt non-text files on Windows.")
            
            curr_prog = 0
            next_step = (progress_prec*0.01*attr['total_length']) if attr['total_length'] else float('inf')
            progress_prec = next_step
            
            try:
                if progress_funct:
                    progress_funct(0.0)
                for chunk in iter(lambda: attr['fp'].read(attr['bufsize']), ''):
                    file_target.write(chunk)
                    curr_prog+=len(chunk)
                    if progress_funct and curr_prog >= next_step:
                        next_step += progress_prec
                        if curr_prog > attr['total_length']:
                            curr_prog = attr['total_length']
                        progress_funct(curr_prog)
                return True
            except Exception as e:
                LOG_exception("Exception raised during file writing from stream.")
                curr_prog = None
                return False
            finally:
                if not noclose:
                    file_target.close()
                attr['fp'].close()
                attr['length_remaining'] = 0
        self.read_to = read_to
        
        def close():
            if attr['fp']:
                attr['fp'].close()
        self.close = close
    
    @property
    def code(self):
        return self.__priv_get('code')
    @property
    def url(self):
        return self.__priv_get('url')
    @property
    def name(self):
        return self.__priv_get('name')
    @property
    def msg(self):
        return self.__priv_get('msg')
    @property
    def headers(self):
        return self.__priv_get('headers')
    @property
    def total_length(self):
        return self.__priv_get('total_length')
    @property
    def length_remaining(self):
        return self.__priv_get('length_remaining')
    @property
    def closed(self):
        return self.__priv_get('closed')


class login_instance:
    """Handles current login-related processes and data.
    
    INIT PARAMETERS:
        BBinstance      Parent instance of Blackboard class.
    INIT KEYWORD PARAMS:
        CookiePolicy    'cookielib.[Default]CookiePolicy' object to use
    """
    def __init__(self,BBinstance,CookiePolicy='Default. Should be ' \
            'CookiePolicy class.',**kwargs):
        if not isinstance(BBinstance,Blackboard):
            try:
                del self
            finally:
                raise TypeError('Invalid Blackboard instance passed to '\
                                '\'login_instance\'')
            return
        if CookiePolicy == 'Default. Should be CookiePolicy class.': \
                CookiePolicy = cookielib.DefaultCookiePolicy( \
                allowed_domains=[BBinstance.uri['domain']])
        if not CookiePolicy or CookiePolicy.__class__ not in \
                [cookielib.CookiePolicy,cookielib.DefaultCookiePolicy]:
            try:
                del self
            finally:
                raise TypeError('type of CookiePolicy passed to \'login_ins' \
                                'tance\' instance is not of an accepted type')
            return
        self.__BBinst = BBinstance
        self.uri_dict = self.__BBinst.uri
        self.__SEIKOOC = urllib2.HTTPCookieProcessor( \
                    cookielib.CookieJar(CookiePolicy))#has variable .cookiejar
        self.__CREDENTIALS = urllib2.HTTPPasswordMgrWithDefaultRealm()
        self.__login_url = "%s://%s/"%(self.uri_dict['protocol'], \
                                       self.uri_dict['domain'])        
        self.__authuri = '/'
        self.__opener = urllib2.build_opener(self.__SEIKOOC)
        self.__SEITREPORP = {'user_agent':  self.__opener.addheaders[0][1],
                             'output':      sys.stdout.write,
                             'passwd_in':   default_passwd_in
                            }
        self.__MLAER = "NotNone"
        self.properties(user_agent='Mozilla/5.0 (X11; Ubuntu; Linux x86_64;' \
                                   'rv:25.0) Gecko/20100101 Firefox/25.0')
        self.html_parser = self.__BBinst.html_parser
        
        
    
    def __get_creds(self,again=False):
        if not callable(self.__SEITREPORP['passwd_in']):
            raise RuntimeError('The property \'passwd_in\' of \'login_instance'
                + '\' could not be called.')
            return
        c=self.__SEITREPORP['passwd_in'](again)
        if c is False: return
        if isinstance(c[0],basestring) and isinstance(c[1],basestring):
            LOG_info("Adding credentials...")
            self.__CREDENTIALS.add_password(self.__MLAER,self.__authuri, \
                c[0],c[1])
    
    def header_additions(self,funct=None):
        header_list =   [   ("Accept","text/html,application/xhtml+xml," \
                                "application/xml;q=0.9,*/*;q=0.8"),
                            ("Connection","keep-alive"),
                            ("DNT","1"),
                            ("Host",self.uri_dict['domain']),
                            ("Accept-Language","en-US,en;q=0.5")
                        ]
        if funct:
            for i,j in header_list:
                funct(i,j)
            return True
        return header_list
    
    def error_handler(self,soup,url,code,definitelyError=False):
        status_code_groupings = {1:'Informational',2:'Success', \
                                 3:'Redirection',4:'Client Error', \
                                 5:'Server Error'}
        status_code_types = {1:'internal',2:'status',3:'redirect',4:'error', \
                             5:'error'}
        code_is_soft=False
        real_type=""
        if not definitelyError:
            if code//100 in [4,5]:
                pass
            elif soup.__class__.__name__ == 'BeautifulSoup' and len(soup.contents)>1:
                if type(soup.contents[0]).__name__ == 'Doctype':
                    if type(soup.contents[1]).__name__ == 'Comment':
                        comnt = soup.contents[1].string.strip()
                        if re.match('.*/([4-5][0-9]{2}|error)\.jsp',comnt):
                            code_is_soft=True
                            real_type_check = re.match('.*/([4-5][0-9]{2}|error)\.jsp',comnt)
                            if real_type_check != 'error':
                                real_type = real_type_check
                if (soup.title and 'error' in soup.title.string.lower()) or soup.find('div','error'):
                    code_is_soft=True
            
            doc_loc_rep_re = re.compile(r".*?document\.location\.replace\('(?P<url>[^']*)'\).*",re.S)
            if not code_is_soft:
                scripts = soup.find_all('script',limit=3)
                for script in scripts:
                    script = script.get_text()
                    metch = doc_loc_rep_re.match(script)
                    if metch and metch.groupdict()['url']:
                        return metch.group('url')
                
            
            if not code_is_soft and code//100 not in [4,5]:
                return False
        
        errorid=None
        error_text=""
        error_div=soup.find('div','error',id='contentPanel')
        if error_div:
            y=error_div.find(id='bbNG.receiptTag.content')
            if y:
                if type(y.contents[0]).__name__ == 'NavigableString':
                    error_text+=y.contents[0]
                errorid_str=y.find(class_='captionText')
                if errorid_str and 'Error ID ' in errorid_str:
                    errorid = errorid_str.string.partition('Error ID is ')[2][:-1]
                    
        if 'not contain' in error_text or 'not found' in error_text:
            if real_type and '4xx' not in real_type:
                real_type += ' or 4xx-type'
            elif not real_type:
                real_type = '4xx-type'
        
        bb_err_val="Blackboard responded with a %s HTTP %s code" \
                   %(code,status_code_types.get(code//100,'invalid'))
        if code_is_soft:
            bb_err_val+=", but presented a%s error page."%['n',' %s'%real_type][bool(real_type)]
        else:
            bb_err_val+="."
        if errorid:
            bb_err_val+=" The provided internal Error ID is %s"%errorid 
        
        return BlackboardError(bb_err_val,soup,code,code_is_soft,errorid,url)


    def __cookies(self,action=None):
        action_dict = { 'clear':self.__SEIKOOC.cookiejar.clear
                    }
        if action in action_dict:
            action_dict[action]()
        return
    
    ##BASICALLY DUPLICATES 'open(...,method=*)' FUNCTIONALITY
    #def validate_link(self,url,data=None,**kwargs):
    #    """Check a url using an independent opener, but optionally use the 
    #    normal cookies.
    #    
    #    kwargs:
    #        cookies     If True, an attempt will be made to open the url with
    #                    your Blackboard cookies.
    #        method      HEAD|GET|POST|PUT|OPTIONS|TRACE
    #    -
    #    Returns a dict 
    #    """
    #    import httplib
    #    req = urllib2.Request(url,data)
    #    if kwargs.get('method') and kwargs['method'].upper() in ['HEAD','GET','POST','PUT','OPTIONS','TRACE']:
    #        req.get_method = lambda : kwargs['method'].upper()
    #        print "Setting Method to {!r}".format(kwargs['method'].upper())
    #    else:
    #        print "Method kept at default"
    #    if kwargs.get('cookies'):
    #        req = self.__SEIKOOC.http_request(req)
    #        print "Adding cookies to request..."
    #    else:
    #        print "Request will be cookie-free"
    #    
    #    dadict = {}
    #    
    #    ret = None
    #    try:
    #        ret = urllib2.urlopen(req)
    #    except urllib2.HTTPError as e:
    #        ret = e
    #    finally:
    #        if ret:
    #            ret.close() #just to be safe
    #    
    #    dadict['status-code'] = ret.code
    #    dadict['status-msg'] = ret.msg
    #    dadict['url'] = ret.url
    #    dadict['headers'] = ret.headers.dict.copy()
    #    dadict['standard-status-msg'] = httplib.responses.get(ret.code)
    #    
    #    return dadict
    
    def open(self,fullurl,data=None,timeout=None,retry_login=0,parser='useBSarg',**kwargs):
        #TODO: write docs for this function...
        #if kwargs['method'] == 'HEAD', a tuple is returned: (status-code, url, header-dict)
        #if kwargs['file_download'] == True, the url will be opened and the
        #   function will return (status-code, url, headers, file-object).
        method = kwargs.get('method',None)
        file_download = bool(kwargs.get('file_download',False))
        
        req = None
        if not data or isinstance(data,basestring):
            pass
        elif isinstance(data,dict) or (isinstance(data,list) and (len(data)<1 \
                or isinstance(data[0],tuple))):
            data = urllib.urlencode(data)
        else:
            err = 'login_instace.open passed invalid argument for parameter ' \
                  '\'data\', of type %s; only sequences of tuples, mapping ' \
                  'objects, and string types are accepted.' \
                  %(data.__class__.__name__)
            raise TypeError(err)
        
        if isinstance(fullurl, basestring):
            req = urllib2.Request(fullurl,data)
        elif isinstance(fullurl, urllib2.Request):
            req = fullurl
            if data:
                req.add_data(data)
        else:
            err = 'login_instance.open passed invalid argument for parameter' \
                  ' \'fullurl\', of type %s; only Request and string types ' \
                  'accepted.'%(fullurl.__class__.__name__)
            raise TypeError(err)
        if method is None or method not in ['GET','HEAD','POST','TRACE','OPTIONS']:
            method = req.get_method()
        elif req.get_method() != method:
            req.get_method = lambda : method
        #Request built
        
        
        if retry_login is None:
            retry_login = 0
        if not isinstance(retry_login,numbers.Real):
            raise TypeError,'open() argument \'retry_login\' should be an integer'
        else:
            retry_login = int(retry_login) if retry_login > 0 else 0
        
        self.header_additions(req.add_header)
        
        resp = None
        try:
            if timeout:
                resp = self.__opener.open(req,timeout)
            else:
                resp = self.__opener.open(req)
        except urllib2.HTTPError as e:
            code = e.code
            url = e.url
            if method == 'HEAD':
                hdrz = e.headers.dict
                e.close()
                return (code, url, hdrz)
            if file_download:
                return downloadable_file(e)
                
            soup=self.html_parser.get_soup(fileObject=e,parser=parser)
            bb_err = self.error_handler(soup,url,code,True)
            LOG_warning("Error url: {!r}; code: {}".format(url,code))
            raise bb_err
        except urllib2.URLError as e:
            reason = e.reason
            if isinstance(reason,urllib2.socket.error):
                raise IOError, "A low-level socket exception was raised. This " \
                        "is most likely the result of a DNS error."
            raise #i.e. pass it on
        
        if method == 'HEAD':
            code,url = resp.code,resp.url
            hdrz = resp.headers.dict
            resp.close()
            return (code,url,hdrz)
        elif file_download:
            return downloadable_file(resp)
        
        soup=self.html_parser.get_soup(fileObject=resp,parser=parser)
        LOG_debug("Returned url: {!r}; code: {}".format(resp.url,resp.code))
        
        err_hndlr_resp = self.error_handler(soup,resp.url,resp.code)
        hndlr_url = ''
        if isinstance(err_hndlr_resp,BlackboardError):
            raise err_hndlr_resp
        elif isinstance(err_hndlr_resp,basestring):
            hndlr_url = err_hndlr_resp
        
        loginScary = self.url_gen('domain','webapps','login')
        scary_checker = lambda checkurl: checkurl.startswith(loginScary)
        
        if ( scary_checker(resp.url) or scary_checker(hndlr_url)) and \
                not scary_checker(req.get_full_url()):
            
            LOG_debug("\"Scary\" url! Blackboard sent us to the login page")
            
            if retry_login:
                LOG_debug("'retry_login' is {}; attempting login...".format(retry_login))
                _ = self.login()
                return self.open(req,None,timeout,retry_login-1)
            return NOT_LOGGED_IN
        
        bbpage = BlackboardPage(self.__BBinst,resp,soup)
        return bbpage
    
    
    def class_parser2(self,update=False):
        courses_is_set = bool(self.__BBinst.courses)
        if courses_is_set and not update:
            LOG_debug("Blackboard.courses is already set, and parameter 'update' is False; returning current courses.")
            return self.__BBinst.courses
        else:
            p1 = "Blackboard.courses is {}set, ".format('' if courses_is_set else 'NOT ')
            p2 = "but" if (courses_is_set and update) else "and"
            p1p2p3 = "{}{} 'update' parameter is {}; continuing class parsing.".format(p1,p2,bool(update))
            LOG_debug(p1p2p3)
        
        
        req_url = self.url_gen('domain','webapps','portal')+'/portal_jsp/layout/display_module.jsp'
        req_data = { 'module_id': 27, 'tabId': 1 }
        bb_page = self.open(req_url,req_data,retry_login=1)
        
        if bb_page is NOT_LOGGED_IN:
            return NOT_LOGGED_IN
        clss_listing = bb_page.soup.find('ul',class_='courseListing')
        courses = []
        
        if not clss_listing:
            clss_listing = []
            LOG_warning("Couldn't find classes in page returned by 'open()'; clss_listing={!r}".format(clss_listing))
        else:
            clss_listing = clss_listing.find_all('li',recursive=False)
            if clss_listing:
                LOG_debug("Found {} classes in 'clss_listing' page.".format(len(clss_listing)))
        for li_course in clss_listing:
            a_ent = li_course.find('a',recursive=False)
            if not a_ent:
                LOG_info("entry has no link, probably old. Skipping...")
                continue
            qry = a_ent['href'] #parse_url(a_ent['href'])[1].get('url')
            
            c_id = None
            if qry:
                qryqry = parse_url(qry)[1]
                c_id = qryqry.get('id')
                if c_id:
                    c_id = number_finder(c_id,1)
            name = a_ent.get_text(strip=True)
            dct = parse_course_name(name)
            if not dct:
                LOG_info("Could not parse course name with function...")
                if ': ' in name:
                    LOG_info("Splitting 'name' for course name")
                    name_lst = name.split(': ',1)
                    dct['bb_course_id'] = name_lst[0]
                    dct['full_name'] = dct['name'] = name_lst[1]
            
            course_information = li_course.find('div',class_="courseInformation")
            if course_information:
                LOG_debug("Found course_information")
                instr_list = course_information.find_all('span',class_="name")
                name_list = []
                for instr in instr_list:
                    x = instr.get_text(strip=True).strip(';')
                    if x:
                        name_list.append(x)
                if len(name_list) == 1:
                    name_list = name_list[0]
                    LOG_debug("Found 1 instructor")
                elif len(name_list) == 0:
                    name_list = None
                    LOG_debug("No instructors found.")
                else:
                    LOG_debug("Found {} instructors.".format(len(name_list)))
                dct['instructor'] = name_list
            
            dct['bb_id'] = c_id
            LOG_debug("Creating course_object...")
            courses.append(course_object(self.__BBinst,**dct))
        LOG_info("Returning {} parsed course_objects".format(len(courses)))
        self.__BBinst.courses = courses
        return courses
    
    def class_parser(self,update=False):
        LOG_warning("class_parser is deprecated in favor of class_parser2")
        if self.__BBinst.courses and not update:
            LOG_debug("<Blackboard>.courses is already set, and parameter 'update' is False")
            return self.__BBinst.courses
        xml_url = self.url_gen('domain','webapps','portal','execute')+'/tabs/tabAction?action=refreshAjaxModule&modId=_4_1&tabId=_1_1'
        bbpage = self.open(xml_url)
        if bbpage is NOT_LOGGED_IN:
            x = self.login()
            if not x:
                return NOT_LOGGED_IN
            bbpage = self.open(xml_url)
            if bbpage is NOT_LOGGED_IN:
                return NOT_LOGGED_IN
        clss_listing = bbpage.soup.find_all('a')
        courses = []
        if not clss_listing:
            LOG_warning("Found no parsable classes when searching.")
            #global parsable_classes
            #parsable_classes = bbpage
            soup = bbpage.soup.find('contents')
            if soup and len(soup):
                soup = soup.contents[0]
                if isinstance(soup,bs4.element.CData):
                    LOG_warning("Found problematic CData element (could contain missing classes)")
                    x = parse_cdata(soup)
                    clss_listing = x.find_all('a')
                    if not clss_listing:
                        clss_listing = []
                    else:
                        LOG_warning("Parsable classes found! Yay! Do you have lxml installed? It's great with CData objects.")
        for x in clss_listing:
            #tmp_url = urllib.unquote(x['href'].split('url=',1)[1])
            tmp_url = parse_url(x['href'])[1]['url']
            blkbd_id = number_finder(parse_url(tmp_url)[1]['id'],1)
            full_nm = x.contents[0]
            courses.append(course_object(self.__BBinst,full_name=full_nm,bb_id=blkbd_id))
        self.__BBinst.courses = courses
        return courses
    
    #https://blackboard.mst.edu/webapps/bb-mygrades-bb_bb60/myGrades?course_id=_282821_1&stream_name=mygrades
    def grade_getter(self,course_id=None,course_obj=None):
        if course_obj is not None:
            if course_obj.bb_id is None:
                raise ValueError, "grade_getter was passed a course_object with a 'bb_id' of None"
            course_id = course_obj.bb_id
        
        if course_id is not None:
            err = "'course_id' argument to grade_getter must be an integer or coercible to an integer"
            if isinstance(course_id,int):
                pass
            elif isinstance(course_id,float):
                course_id = int(course_id)
            elif isinstance(course_id,basestring):
                course_id = course_id.strip()
                if len(course_id) < 5:
                    raise ValueError, err
                if course_id[-2:] == '_1':
                    course_id = course_id[:-2]
                if '_' in course_id:
                    course_id = course_id.strip('_')
                if not course_id.isdigit():
                    raise ValueError, err
                course_id = int(course_id)
        else:
            raise ValueError, "grade_getter must be passed either a course_id or course_obj as a respective argument"
        
        url = "{}/myGrades?course_id={}&stream_name=mygrades".format(self.url_gen('domain','webapps','bb-mygrades'),course_id)
        bb_page = self.open(url)
        
        if bb_page == NOT_LOGGED_IN:
            return NOT_LOGGED_IN
        
        return page_parsing(bb_page.soup,self.__BBinst)
        
    
    def stream_getter(self,streamName):
        #alerts:        /webapps/streamViewer/streamViewer  'cmd':'loadStream','streamName':'alerts','providers':'{}','forOverview':'false'
        #Due Dates All: /webapps/streamViewer/streamViewer  'cmd':'loadStream','streamName':'todo','providers':'{}','forOverview':'false'
        pass
    
    def url_gen(self,*parts):
        retStr = ''
        if 'domain' in parts[:2]:
            if parts[0] == 'protocol':
                parts = parts[2:]
            else:
                parts = parts[1:]
            retStr = '{}://{}'.format(self.uri_dict['protocol'],self.uri_dict['domain'])
        for i in parts:
            if i in self.uri_dict:
                retStr+='/%s'%self.uri_dict[i]
        return retStr
    
    
    def logout(self):
        LOG_info("Logging out...")
        logootUrl = self.url_gen('domain')
        req = urllib2.Request(logootUrl,urllib.urlencode({'action':'logout'}))
        self.header_additions(req.add_header)
        resp = self.__opener.open(req)
        LOG_info("Blackboard returned login page; (probable) success.")
        LOG_info("Clearing Cookies...")
        self.__cookies('clear')
        LOG_info("Clearing saved credentials...")
        self.__CREDENTIALS.passwd.clear()
        return NOT_LOGGED_IN
    
    

    def login(self,secondrun=False):
        u,n=self.__CREDENTIALS.find_user_password(self.__MLAER,self.__authuri)
        if u and n:
            
            #As this function is used from within the normal open() method, it
            #   SHOULD NOT call open(), instead handling login independently
            req = urllib2.Request(self.__login_url,urllib.urlencode({'user_id':u,'password':n,'login':'Login','action':'login','new_loc':''}))
            self.header_additions(req.add_header)
            self.__opener.addheaders = [('User-agent', self.__SEITREPORP['user_agent'])]
            resp = self.__opener.open(req)
            bbpage = BlackboardPage(self.__BBinst,resp)
            x=bbpage.soup.find(id='loginErrorMessage')
            if bbpage.url.startswith(self.url_gen('domain','webapps','login')) or x:
                self.__CREDENTIALS.passwd = {}
                self.__cookies('clear')
                return NOT_LOGGED_IN
            else:
                return True
            
        elif not u and not n:
            LOG_info("Credentials not set")
            LOG_info("Getting credentials %s"%["","(again)"][secondrun])
            self.__get_creds(secondrun)
            return self.login(True)
    
    def properties(self,get=None,**set_prop):
        """Get or set public properties of login instance
        
        To get a property, call the function with the property in a string,
            e.g. `li_instance.properties('user_agent')`
        To set a property, call the function with the keyword-value pair,
            e.g. `li_instance.properties(user_agent='Firefax')`
        Both get and set will return the NotImplemented object if the property
            does not exist.
        -
        TABLE O' PROPERTIES:
        ====================
        PROPERTY    TYPE            MEANING
        user_agent  str|unicode     Standard user-agent string for browsers.
        output      ????            function to call for information output;
                                        should take a string as an argument.
        passwd_in   function        function to call that returns a tuple
                                        containing username and password;
                                        should take an argument that, if True,
                                        means that the auths were not accepted.
                                        (return False to cancel login)
        """
        if get:
            return self.__SEITREPORP.get(get,NotImplemented)
        elif set_prop:
            key=set_prop.keys()[0]
            if key in self.__SEITREPORP:
                self.__SEITREPORP[key]=set_prop[key]
                return True
        return NotImplemented
    
    

class Blackboard(object):
    def __init__(self,uri_parts=None,log=False,log_level=logging.WARNING, \
                    log_to='blackbird.log'):
        
        
        self.uri =  {   'protocol':     'https',
                        'domain':       'blackboard.mst.edu',
                        'webapps':      'webapps',
                            #webapps
                            'portal':       'portal',
                                'frameset':     'frameset.jsp',
                                'execute':      'execute',
                            'login':        'login',
                            'bb-mygrades':      'bb-mygrades-bb_bb60'
                    }
        object.__init__(self)
        if uri_parts:
            not_in=[]
            for x in self.uri:
                if x in uri_parts:
                    self.uri[x] = uri_parts[x]
        
        self.__logging = {'enabled':False,'log_to':'blackbird.log',
                            'level':logging.WARNING,
                            'format':logging.Formatter('%(asctime)s %(module)s.%(funcName)s[%(lineno)04d]: <%(levelname)s> %(message)s')}
        
        self.logging(log,level=log_level,log_to=log_to)
        
        
        self.html_parser = _beaut_soup_custom()
        
        self.__LOGIN_INST = login_instance(self)
        
        self.courses = None
        
        self.tool = None
        
        self.course_directory = './course_contents'
        
        self.course_name_format = re.compile(r'^(?P<department>\w+)\s(?P<class_num>[0-9]+)\:\s(?P<name>[^(]+)((\((?P<section>[^)]+)\))?\s(?P<semester>\w+))?')
    
    def login(self):
        return self.__LOGIN_INST.login()
    
    def logout(self):
        return self.__LOGIN_INST.logout()
    
    
    def logging(self,enabled=None,**kwargs):
        
        #'enabled' Sets the message threshold to 1000 (no messages shown)
        #'log_to'   Determines the logging destination; if it is a string, it is
        #           interpretted as a filename (and thus a FileHandler is used)
        #           If it is a file-like object, it is assumed to be a stream
        #'level'   Minimum logging level to log the message.
        #'format'  The format passed to a logging.Formatter object.
        
        if enabled is not None:
            kwargs['enabled'] = bool(enabled)
        
        refresh_handler = 'handler' not in self.__logging or \
            (isinstance(self.__logging['log_to'],basestring) ^ isinstance(self.__logging['handler'],logging.FileHandler))
        
        if not (kwargs or refresh_handler):  return
        
        if 'enabled' in kwargs:
            self.__logging['enabled'] = bool(kwargs['enabled'])
        if 'log_to' in kwargs:
            self.__logging['log_to'] = kwargs['log_to']
            refresh_handler = True
        if 'level' in kwargs:
            x = kwargs['level']
            if isinstance(x,int):
                self.__logging['level'] = kwargs['level']
        if 'format' in kwargs:
            self.__logging['format'] = logging.Formatter(kwargs['format'])
        
        
        if 'handler' not in self.__logging or refresh_handler:
            if central_logger.handlers:
                central_logger.removeHandler(central_logger.handlers[0])
            log_to = self.__logging['log_to']
            fmt = self.__logging['format']
            if isinstance(log_to,basestring):
                self.__logging['handler'] = logging.FileHandler(log_to,encoding='utf8',delay=True)
            elif isinstance(log_to,file):
                self.__logging['handler'] = logging.StreamHandler(log_to)
            else:
                raise TypeError, "Blackboard.logging() kwarg 'log_to' must be a string (for FileHandler) or a file-like object (for StreamHandler)"
            central_logger.addHandler(self.__logging['handler'])
        
        central_logger.setLevel( [ 1000 , self.__logging['level'] ][self.__logging['enabled']] )
        self.__logging['handler'].setFormatter(self.__logging['format'])
        
        if self.__logging['enabled']:
            central_logger.log(100,"LOGGING ENABLED")
    
    
    def update_courses(self):
        clprsr_ret = self.__LOGIN_INST.class_parser2(True)
        LOG_info("class_parser2 returned {}".format(clprsr_ret if type(clprsr_ret) not in [list,tuple] else str(len(clprsr_ret))+" items"))
        if clprsr_ret is NOT_LOGGED_IN:
            return NOT_LOGGED_IN
        course_menu = self.__LOGIN_INST.url_gen('domain','webapps')+ \
            '/blackboard/content/courseMenu.jsp?course_id={}&newWindow=false'
        if not self.courses:
            LOG_info("Blackboard.courses is {}; returning False".format(self.courses))
            return False
        for clss in self.courses:
            cmenu = self.__LOGIN_INST.open(course_menu.format(clss.bb_id))
            if cmenu is NOT_LOGGED_IN:
                return NOT_LOGGED_IN
            clinks = cmenu.soup.find(id='courseMenuPalette_contents').find_all('li')
            
            for li in clinks:
                x=li.find('a')
                c_url,qry = parse_url(x['href'])
                
                if c_url.path.endswith('listContent.jsp'):
                    #is content link
                    cont_id = number_finder(qry['content_id'],1)
                    
                    if x.span:
                        clss.content_dict[x.span.string]=cont_id
                
                elif c_url.path.endswith('launchLink.jsp') and 'tool_id' in qry:
                    #is a non-content tool link
                    tool_id = number_finder(qry['tool_id'],1)
                    
                    if tool_id not in clss.visible_tools:
                        clss.visible_tools[x.span.string]=tool_id
            
            #if clss['full name']:
            #    reg_res = self.course_name_format.match(clss['full name'])
            #    if reg_res:
            #        regdict = reg_res.groupdict()
            #        for attr in ['department','semester','section','course_num','name']:
            #            if regdict[attr] and not clss[attr]:
            #                regdict[attr]=regdict[attr].strip()
            #                if regdict[attr].isdigit():
            #                    regdict[attr]=int(regdict[attr])
            #                clss.value_dict[attr] = regdict[attr]
            #        if regdict['semester'] and not clss['year']:
            #            reg_yr = re.match('^.*?([0-9]+)',regdict['semester'])
            #            if reg_yr and reg_yr.groups():
            #                clss.value_dict['year']=reg_yr.group(1)
    
    def update_course_content(self,bb_course):
        if not isinstance(bb_course,course_object):
            raise TypeError, "update_course_content() argument 'bb_course' must be a course_object"
        
        if not bb_course.content_dict:
            return False
        
        content_dict = bb_course.content_dict.copy()
        bb_id = bb_course.bb_id
        
        for k,v in content_dict.items():
            if v is None:
                continue
            elif isinstance(v,content_object):
                v = v.content_id
            
            if isinstance(v,int):
                contnt_obj = content_object(self,type='folder',course_id=bb_id,content_id=v,name=k,_bb_inst=self)
                
                x = contnt_obj.walk_contents()
                
                bb_course.content_dict[k] = contnt_obj
            
        return True
    
    #EXPERIMENTAL
    #def get_course_content(self,bb_course,content_id=None,save_path='Default'):
    #    
    #    #if content_id is True, gets all content
    #    LOG_warning("##WARNING: Experimental Function")
    #    listContent = self.__LOGIN_INST.url_gen('domain','webapps')+ \
    #        '/blackboard/content/listContent.jsp?course_id={}&content_id={}'
    #    if save_path is 'Default':
    #        #if 
    #        save_path = self.course_directory+'/'
    #    
    #    if not bb_course.content_dict or not bb_course.bb_id:
    #        return False
    #    if content_id is True:
    #        pass#for contnt
    #    if content_id is None:
    #        print "\n\n#CHOOSE: ",
    #        for i in bb_course.content_dict:
    #            print i,' ',
    #        print ''
    #        choiz = raw_input()
    #        if choiz.title() not in bb_course.content_dict:
    #            print "Invalid choice."
    #            return
    #        content_id = bb_course.content_dict[choiz.title()]
    #    course_id = bb_course.bb_id
    #    cont_page = self.__LOGIN_INST.open(listContent.format(course_id,content_id))
    #    parsed_out = page_parsing(cont_page.soup,'bb_list_content')
    #    if 'page_type' in parsed_out and parsed_out['page_type'] == 'listContent':
    #        print "{} items found on page '{}'.".format(len(parsed_out['content']),parsed_out['title'])
            
    
    def grade_getter(self,course_id=None,course_obj=None):
        x = self.__LOGIN_INST.grade_getter(course_id,course_obj)
        if isinstance(x,dict) and 'grades' in x:
            return x['grades']
    
    def check_for_announcement(self):
        """Checks the Blackboard landing page for announcements and returns any.
        
        If an announcement is found, returns a tuple of the format
                (Header, Title, Date-posted, Message)
        If no announcement is found, returns None
        If an error occurs, returns False
        -
        Success Example:
            ("System Announ...", "BLACKBOARD MAINT...", "Wed, Febr...", "...")
        -
        NOTE: A successful announcement check may still have None values in
            the tuple!
        """
        try:
            page = urllib2.urlopen(self.__LOGIN_INST.url_gen('domain','webapps','login'))
            soup = self.html_parser.get_soup(fileObject=page)
        except Exception:
            LOG_exception("Error while checking for announcements...")
            return False
        
        loginAnn = soup.find('div',id="loginAnnouncements")
        if not loginAnn:
            return None
        
        headr = loginAnn.find('h3',recursive=False)     ###
        if headr:
            headr = headr.get_text(strip=True)
        
        if not loginAnn.li:
            return None
        
        title = loginAnn.li.find('strong',recursive=False)
        posted = loginAnn.li.find('em',recursive=False)
        
        if title:
            title = title.get_text(strip=True)
        if posted:
            posted = posted.get_text(strip=True).strip('()')
        
        vtbegenerated = loginAnn.li.find('div',class_='vtbegenerated',recursive=False)
        
        message = None
        if vtbegenerated:
            items = vtbegenerated.find_all('p')
            if items:
                message = '\n'.join( [' '.join( \
                                list(itm.stripped_strings) ) for itm in items ] )
        
        return (headr, title, posted, message)
    
