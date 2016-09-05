#!/usr/bin/env python

_bs4_file = 'bs4_4.2.1_vitals.zip'




import sys,os

class BlackbirdConfigError(EnvironmentError):
    pass

def _path_maker(argpath):
    x = os.path.join(os.path.dirname(__file__),argpath)
    x = os.path.abspath(x)
    return x

def get_bs4(globells=None,ret_bs4=False):
    bzz4 = None
    try:
        bzz4 = __import__('bs4')
    except ImportError:
        peth = _path_maker(_bs4_file)
        sys.path.insert(0,peth)
        try:
            bzz4 = __import__('bs4')
        except ImportError:
            raise BlackbirdConfigError, "Failed to find BeautifulSoup module " \
                    "'bs4' both natively and locally."
        finally:
            sys.path.pop(0)
    
    if type(globells) is type(globals):
        raise TypeError, "get_bs4() argument should be an OPENED global dictionary"
        
    elif isinstance(globells,dict):
        globells['bs4'] = bzz4
    if ret_bs4:
        return bzz4

#
#let    environ = os.environ

# WINDOWS XP|Vista|7:
#   environ['USERNAME']     # username
#   environ['USERPROFILE']  # user home directory, e.g. "%HOMEDRIVE%:\\Users\\%USERNAME%"
#   environ['APPDATA']      # user-specific domain-wide program data, == "%USERPROFILE%\\[[Application Data | AppData\\Roaming]]"
#
# WINDOWS Vista|7:
#   environ



