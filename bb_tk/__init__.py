#!/usr/bin/env python

print "bb_tk/__init__.py!!!"

import blackbird,bb_utilities
import os,sys,webbrowser,traceback

__all__ = ['tree_browser','STYLE']

from Tkinter import *
from ttk import *
import Tkinter as tk
import tkMessageBox

##
## Style & Theme Setup
##

global err_test
err_test = None

#report_callback_exception(self,exc,val,tb)
def show_error(*args,**kwargs):
    #print "####"
    #print "#### SHOW ERROR:"
    #print "#### Number of args: {}".format(len(args))
    #for i,arg in enumerate(args):
    #    print "#### Arg {}:".format(i)
    #    print "####    Type: {!r}".format(arg.__class__.__name__)
    #    print "####     Str: {!r}".format(str(arg))
    exc_type = kwargs.get('exc_type',kwargs.get('type',None))
    exc_value = kwargs.get('exc_value',kwargs.get('value',None))
    exc_trace = kwargs.get('exc_trace',kwargs.get('trace',kwargs.get('tb',None)))
    if len(args):
        for arg in args:
            if type(arg) is type and issubclass(arg,Exception):
                if not exc_type or not (type(exc_type) is type and issubclass(exc_type,Exception)):
                    exc_type = arg
            elif isinstance(arg,Exception):
                if not exc_value or not isinstance(exc_value,Exception):
                    exc_value = arg
            elif isinstance(arg,traceback.types.TracebackType):
                if not exc_trace or not isinstance(exc_trace,traceback.types.TracebackType):
                    exc_trace = arg
    if not exc_type and exc_value and isinstance(exc_value,Exception):
        exc_type = type(exc_value)
    if exc_trace and isinstance(exc_trace,traceback.types.TracebackType):
        exc_trace = traceback.extract_tb(exc_trace)
    else:
        exc_trace = []
    
    titl = 'Exception Raised'
    if exc_type:
        titl = "{} Raised".format(exc_type.__name__)
    messag = str(exc_value)
    body = ""
    
    if exc_trace:
        body+="Traceback:\n"
        for fl,lnnum,fnct,ln in exc_trace:
            body += "{!r}[{}]:".format(fl,lnnum)
            if fnct != '<module>':
                body += " in {!r}:".format(fnct)
            body += "\n"
            if ln:
                body += "  {}\n".format(ln)
    
    try:
        tkMessageBox.showerror(titl,message=messag,detail=body)
    except TclError as e:
        if "bad option" in str(e) or (hasattr(e,'message') and "bad option" in e.message):
            tkMessageBox.showerror(titl,"{}\n{}".format(messag,body))
    return

tk.Tk.report_callback_exception = show_error

_media_dir = os.path.abspath(os.path.join(os.path.dirname(__file__),'media'))

_update_on_Tk_reset = []

__tk_obj_ = None
def _run_on_toplevel(run_funct,*args,**kwargs):
    """Calls  run_funct( {toplevel}, *args, **kwargs ) on a hidden toplevel instance.
    """
    global __tk_obj_
    if not __tk_obj_:
        __tk_obj_ = Tk(); __tk_obj_.withdraw(); __tk_obj_.winfo_toplevel().title(" ")
        for i in _update_on_Tk_reset:
            try:
                i()
            except Exception as e:
                print "ERRORed on updating Tk after reset"
                print e
    if not callable(run_funct):
        return False
    
    retval = None
    try:
        retval = run_funct.__call__(__tk_obj_,*args,**kwargs)
    except:
        return sys.exc_info()[1]
    finally:
        try:
            state = __tk_obj_.state()
            if 'withdrawn' not in state:
                __tk_obj_.withdraw()
        except TclError as e:
            if 'has been destroyed' in e.message:
                __tk_obj_ = None
                _run_on_toplevel(None)
    return retval

_run_on_toplevel(None) #To initialize Tk system

def check_tk():
    x = _run_on_toplevel(lambda t: t.state())
    print type(x)
    print x
    print ""

def _tk_call(*args,**kwargs):
    run_funct = lambda x: x.tk.call(*args,**kwargs)
    return _run_on_toplevel(run_funct)

if not os.path.isdir(_media_dir):
    raise IOError, "Failed to find media subdirectory."

class StyleError(Exception):
    pass

class _icons_cls(object):
    def __init__(self,style_parent):
        object.__init__(self)
        self.parent = style_parent
        self.app_icon = None
        self.all_icon_names = ['assignment','attachment','blankpage','blog', \
                'discussion','document','file','file_link_ti','folder', \
                'grouppages','image','lesson','lessonplan','link','selfpeer', \
                'survey','test','UNKNOWN','wiki','youtube']
        self.__icons_cl = {}
        _update_on_Tk_reset.append(self.__reset_n_update)
    
    def __reset_n_update(self):
        self.app_icon = None
        self.__icons_cl.clear()
        self.__update()
    
    def __update(self):
        x = os.path.join(_media_dir,'icon/TheBlackbird.gif')
        if not isinstance(self.app_icon,Image):
            self.app_icon = Image("photo", file=x)
        elif self.app_icon.cget('file') != x:
            self.app_icon.configure(file=x)
        
        icon_path_gen = lambda icn,thme: os.path.join(_media_dir,'THEME_{}/{}.gif'.format(thme,icn))
        
        for icon_name in self.all_icon_names:
            ipath = icon_path_gen(icon_name,self.parent.theme)
            
            if not os.path.isfile(ipath):
                if icon_name == 'youtube':
                    ipath = os.path.join(_media_dir,'YouTube_constant/YouTube-social-icon_red.26x20.gif')
                else:
                    ipath = icon_path_gen(icon_name,'default')
                
                if not os.path.isfile(ipath):
                    raise Exception, "Fundamental Icon Error: Failed to find icon {!r} in default theme. Probably, the icon class was changed, or the file was moved."
            if not isinstance(self.__icons_cl.get(icon_name),PhotoImage):
                self.__icons_cl[icon_name] = PhotoImage(file=ipath)
            else:
                self.__icons_cl[icon_name].configure(file=ipath)
    
    def __getitem__(self,key):
        if key in self.__icons_cl:
            return self.__icons_cl[key]
        return None

class _style_cls(object):
    __slots__ = ('theme','_style_cls__icons')
    
    def __init__(self):
        self.__icons = _icons_cls(self)
        self.set_theme('default')
    
    def get_all_themes(self):
        themez = []
        for itm in os.listdir(_media_dir):
            itmpath = os.path.join(_media_dir,itm)
            if os.path.isdir(itmpath) and itm.startswith('THEME_'):
                themez.append(itm[6:])
        return themez
    
    def set_theme(self,val):
        if val not in self.get_all_themes():
            raise StyleError, "Theme {!r} could not be found.".format(val)
        object.__setattr__(self,'theme',val)
        self.__icons._icons_cls__reset_n_update()
    
    @property
    def __current_theme_path(self):
        peth = os.path.join(_media_dir,'THEME_{}/'.format(self.theme))
    
    @property
    def windowing_system(self):
        return _tk_call('tk','windowingsystem')
    
    def app_icon_setter(self,widget):
        x = _tk_call('wm','iconphoto',widget.winfo_toplevel()._w,self.__icons.app_icon)
        
        return False if isinstance(x,BaseException) else True
    
    
    def get_icon(self,icon_name,default=''):
        return self.__icons[icon_name] or default


class _config_cls(object):
    
    def __init__(self):
        self._opts = {  'rightclick':   ('<ButtonRelease-3>',),
                        'browser':      None,
                        'defaultdir':   os.path.expanduser('~'),
                        'BinOrDec':     'bin',
                        'pwd_char':     u'\u2022'
                     }
        
        if STYLE.windowing_system == 'aqua':
            self._opts['rightclick'] = ('<ButtonRelease-2>','<Control-ButtonRelease-1>')
        
        if isinstance(self._opts['browser'],basestring) or self._opts['browser'] is None:
            try:
                self._opts['browser'] = webbrowser.get(self._opts['browser'])
            except webbrowser.Error:
                try:
                    self._opts['browser'] = webbrowser.get()
                except webbrowser.Error:
                    self._opts['browser'] = None
        else:
            try:
                self._opts['browser'] = webbrowser.get()
            except webbrowser.Error:
                self._opts['browser'] = None
    
    def getopt(self,opt_str=None,default='ARbiTrARY stRinG'):
        if opt_str is not None:
            if opt_str in self._opts:
                return self._opts[opt_str]
            elif default == 'ARbiTrARY stRinG':
                raise KeyError, "Key {!r} is not a valid config key.".format(opt_str)
            else:
                return default
        return dict(self._opts)
    
    def browser_open(self,url,new=0):
        if not self._opts['browser']:
            return None
        if new not in range(3):
            new = 0
        
        return self._opts['browser'].open(url,new)


STYLE = _style_cls()

CONFIG = _config_cls()
