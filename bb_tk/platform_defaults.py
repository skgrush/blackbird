#!/usr/bin/env python

import Tkinter as tk
import sys

_OPTS = {'windowingsystem':''}


_w = tk.Tk()
try:
    _OPTS['windowingsystem'] = _w.tk.call('tk','windowingsystem')
except:
    pass
finally:
    _w.destroy()
    del _w


def _get_plat(plat=''):
    if plat == '':
        if 'os' in _OPTS:
            return _OPTS['os']
        else:
            i = None
            if len(sys.platform) > 0:
                i = _get_plat(sys.platform)
            _OPTS['os'] = i
            return i
    
    elif isinstance(plat,basestring):
        plat = plat.lower().strip()
        for i in ['win32','windows','cygwin']:
            if plat.startswith(i):
                return 'windows'        #
        if pat == 'win':
            return 'windows'
        for i in ['darwin','osx','os x','mac']:
            if plat.startswith(i):
                return 'osx'            #
        if pat.startswith('linux'):
            return 'linux'              #
    
    return None

_d_a = 4
_d_s = tuple( [('4',('y','n','c','a','h','m'))] + [(k, ()) for k in ['1','2','8']] )

bLEFT = 1
bRIGHT = 2
bCENTER = 4
bJUSTIFIED = 8

def _gen_dflt(setting, plat=''):
    """
    
    'setting':  alignment|sections|
    'plat':     
        ''              will use the pre-determined platform value [default]
        None            use the fallback value for this setting
        (some string)   interpreted as a platform value. If not accepted,
                        the fallback is used.
    """
    bLEFT,bRIGHT,bCENTER,bJUSTIFIED = 1,2,4,8
    parsed_plat = _get_plat(plat)
    
    ret = NotImplemented
    setit = False
    setting = setting.lower()
    
    if plat == '' or parsed_plat == _OPTS['os']:
        if setting in _OPTS:
            return _OPTS['setting']
        setit=True
    
    
    if setting == 'alignment':
        
        if parsed_plat == 'windows':
            ret = bRIGHT
        
        elif parsed_plat == 'osx':
            ret = bLEFT|bRIGHT
        
        elif parsed_plat == 'linux':
            ret = bLEFT|bRIGHT #GNOME and KDE
        
        else:#default
            ret = bCENTER
    
    elif setting == 'section':
        
        win= ('y','n','c','a','h','m')
        bLEFT,bRIGHT,bCENTER,bJUSTIFIED = map(str,[bLEFT,bRIGHT,bCENTER,bJUSTIFIED])
        
        if parsed_plat == 'windows':
            ret = ( (bLEFT,()) , (bRIGHT,win) , (bCENTER,()) , (bJUSTIFIED,()) )
        
        elif parsed_plat == 'osx':
            ret = ( (bLEFT,('h','m')) , (bRIGHT,('n','c','a','y')) , (bCENTER,()) , (bJUSTIFIED,()) )
        
        elif parsed_plat == 'linux':
            #GNOME
            ret = ( (bLEFT,('h')) , (bRIGHT,('m','n','a','c','y')) , (bCENTER,()) , (bJUSTIFIED,()) )
            #KDE
            ret = ( (bLEFT,('h','m')) , (bRIGHT,('y','a','n','c')) , (bCENTER,()) , (bJUSTIFIED,()) )
        
        else:
            ret = ( (bLEFT,()) , (bRIGHT,()) , (bCENTER,win) , (bJUSTIFIED,()) )
    
    else:
        raise ValueError, "{!r} is not an accepted type.".format(plat)
    
    
    #done parsing
    if setit:
        _OPTS[setting] = ret
    return ret
    



if _sysplatform.lower().startswith('darwin'):
    _d_a = bLEFT|bRIGHT
    _d_s = ( (str(bLEFT), ('h','m'))  ,  (str(bRIGHT), ('-','c','a','+')) )
elif _sysplatform.lower().startswith('win32') or _sysplatform == 'win':
    _d_a = bRIGHT
    _d_s = tuple(  [ (str(bRIGHT), dict(_d_s)[str(bCENTER)]) ] + [(str(k), ()) for k in [bLEFT,bCENTER,bJUSTIFIED]] )
