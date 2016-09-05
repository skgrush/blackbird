#!/usr/bin/env python

import Tkinter as tk
import ttk

from sys import platform as _sysplatform

#   Name                    Alignment           Sticky
######################################################################
#1. Left                #|XXX|       1       |# 'nesw'
#2. Right               #|       1       |XXX|# 'nesw'
#3. Left,Right          #|XXX|     1     |XXX|# 'nesw'  'nesw'
#4. Center              #|  1    |XXX|    1  |# 'nesw'  'nesw'
#5. Left,Center         #|XXX|  1  |XXX|  1  |# 'nesw'  'nesw'
#6. Center,Right        #|  1  |XXX|  1  |XXX|# 'nesw'  'nesw'
#7. Left,Center,Right   #|XXX| 1 |XXX| 1 |XXX|# 'nesw'  'nesw'  'nesw'
#8. Justified           #|XXXXXXXXXXXXXXXXXXX|# 'ns'
######################################################################

bLEFT = 1
bRIGHT = 2
bCENTER = 4
bJUSTIFIED = 8


_d_a = bCENTER
_d_s = tuple( [(str(bCENTER),('+','-','c','a','h','m'))] + [(str(k), ()) for k in [bLEFT,bRIGHT,bJUSTIFIED]] )

def _gen_dflt(setting, plat=''):
    """
    
    'setting': alignment|sections|
    """
    

if _sysplatform.lower().startswith('darwin'):
    _d_a = bLEFT|bRIGHT
    _d_s = ( (str(bLEFT), ('h','m'))  ,  (str(bRIGHT), ('-','c','a','+')) )
elif _sysplatform.lower().startswith('win32') or _sysplatform == 'win':
    _d_a = bRIGHT
    _d_s = tuple(  [ (str(bRIGHT), dict(_d_s)[str(bCENTER)]) ] + [(str(k), ()) for k in [bLEFT,bCENTER,bJUSTIFIED]] )



class DuplicateButtonError(RuntimeError):
    pass

class ButtonGroup(ttk.Frame,object):
    
    default_alignment = _d_a
    default_sections = _d_s
    

    def __init__(self, master=None, **kwargs):
        """
        kwargs:
            alignment   
            l|r|c|j     Set the button layout (tuple) for the given section.
            button_padx The distance between each button
            padding     Internal padding of the box (subtracts button_padx 
                        on for left and right).
            binder      Object to bind keypresses to. [Default: None]
        """
        
        self.__sections = {}
        self.__alignment = self.default_alignment
        self.__stretcher = None
        self.__widgets = {'y':None,'n':None,'c':None,'a':None,'h':None,'m':[]}
        self.__widget_opts = {'y':None,'n':None,'c':None,'a':None,'h':None,'m':[]}
        self.__default = None
        self.__binder = None
        self.__pad = (0, 0, '')
        
        new_align = []
        new_sects = {}
        new_pad = [0,0,''] #(button_padx, box_pad)
        new_bwidth = ''
        
        
        my_kwargs = []
        
        for k,v in kwargs.items():
            if k == 'button_padx':
                my_kwargs.append(k)
                self.button_padx = v
            elif k == 'button_pady':
                my_kwargs.append(k)
                self.button_pady = v
            elif k in ['padding','box_pad','box_padding']:
                my_kwargs.append(k)
                self.padding = v
            elif k == 'binder':
                my_kwargs.append(k)
                self.binder = v
            elif k == 'alignment':
                my_kwargs.append(k)
                if isinstance(v,(tuple,list)):
                    new_align = v
                else:
                    new_align = [v]
            elif not k:
                my_kwargs.append(k)
                continue
            elif k in dict(self.__sections):
                my_kwargs.append(k)
                if not isinstance(v,(tuple,list)):
                    continue
                new_sects[k] = v
            elif (len(k) == 1 and k.lower() in 'lrcj') or k.lower() in ['left','right','center','justified']:
                my_kwargs.append(k)
                k = k[0].lower()
                if not isinstance(v,(tuple,list)):
                    continue
                new_sects[k] = v
        
        self.define_layouts(**new_sects or dict(self.default_sections))
        self.set_alignment(*new_align or [self.default_alignment])
        
        ##Prepare for Frame instantiation
        for k in my_kwargs:
            if k in kwargs:
                del kwargs[k]
        
        no_init = False
        if 'no_init' in kwargs:
            no_init = bool(kwargs['no_init'])
            del kwargs['no_init']
        
        if not no_init:
            ttk.Frame.__init__(self,master,**kwargs)
            self.__no_init = False
        else:
            self.master = master
            self.__no_init = True
    
    @property
    def alignment(self):
        return self.__alignment
    
    @property
    def sections(self):
        sects = []
        for k,v in self.__sections.items():
            k = int(k)
            if k&self.__alignment:
                sects.append(  (k, self.__sections[str(k)])  )
        return tuple(sects)
    
    @property
    def default(self):
        """Default button-type that will be highlighted when presented."""
        return self.__default
    
    @default.setter
    def default(self, val):
        if val is None:
            self.__default = None
        verif = self._parse_button_type(val, return_errors=True)
        if isinstance(verif, tuple):
            if verif and isinstance(verif[0],basestring):
                self.__default = verif[0]
                return
            verif = ValueError()
            
        if isinstance(verif, ValueError):
            raise ValueError, "Default should be the button-type that will be default in this group, or None."
        elif isinstance(verif, TypeError):
            raise verif
        elif isinstance(verif, Exception):
            raise RuntimeError, "Unexpected exception raised: {}".format(verif)
    
    @property
    def binder(self):
        """The widget to bind keypresses to."""
        return self.__binder
    
    @binder.setter
    def binder(self, w):
        if w is None:
            self.__binder = None
            return
        if not isinstance(w,tk.Misc):
            raise TypeError, "Binder should be a widget to bind keypresses to, or None."
        try:
            ret = w.bind('<Return>')
            ret2 = w.bind('<Escape>')
        except (AttributeError, TypeError):
            return
        
        if isinstance(ret,basestring) and isinstance(ret,basestring):
            self.__binder = w
    
    @property
    def button_padx(self):
        return self.__pad[0]
    @property
    def button_pady(self):
        return self.__pad[1]
    
    @button_padx.setter
    def button_padx(self, v):
        try:
            v = int(v) if int(v) > 0 else 0
        except:
            raise TypeError, "button_padx must be int-coercible, not {!r}".format(v.__class__.__name__)
        self.__pad = (v, self.__pad[1], self.__pad[2])
    @button_pady.setter
    def button_pady(self, v):
        try:
            v = int(v) if int(v) > 0 else 0
        except:
            raise TypeError, "button_pady must be int-coercible, not {!r}".format(v.__class__.__name__)
        self.__pad = (self.__pad[0], v, self.__pad[2])
    
    @property
    def padding(self):
        return self.__pad[2]
    
    @padding.setter
    def padding(self, v):
        try:
            v = int(v) if int(v) > 0 else 0
        except:
            raise TypeError, "padding must be int-coercible, not {!r}".format(v.__class__.__name__)
        self.__pad = (self.__pad[0], self.__pad[1], v)
    
    def _make_default(self):
        #validate
        self.set_alignment(self.alignment)
        self.define_layouts(**dict(self.sections))
        #set
        ButtonGroup.default_alignment = self.alignment
        ButtonGroup.default_sections = self.sections
    
    
    def set_alignment(self, *align):
        
        names = {'left':bLEFT,'right':bRIGHT,'center':bCENTER,'justified':bJUSTIFIED}
        
        choice = 0
        
        for a in align:
            if isinstance(a,basestring):
                if a.lower() in names:
                    choice |= names[a.lower()]
                else:
                    raise ValueError, "Unknown alignment {!r}".format(a.lower())
            elif isinstance(a,int):
                if 0 < a <= 15: #8 should be highest, but we'll catch that later
                    choice |= a
                elif a <= 0:
                    raise ValueError, "align arguments of set_alignment() must be greater than 0."
                else:
                    raise ValueError, "align arguments of set_alignment() should be 8 or a bitwise-or map of 1, 2, and/or 4; not {}.".format(a)
            else:
                raise TypeError, "align arguments of set_alignment() must be a string or int representing left,right,center, or justified."
        if choice > 8:
            raise ValueError, "The 'justified' alignment cannot be used with other alignments."
        
        self.__alignment = choice
    
    
    def _parse_button_type(self, *buttons, **kwargs):
        """Internal parsing of button-type identifiers.
        
        button-type values to parse should be passed in the 'buttons' 
            parameter. Types are returned in input-order as a tuple.
        -
        KWARGS:
        return_errors   [bool] If True, instead of raising an error when
                        an invalid button-type is detected, the error is
                        returned. [Deflt: False]
        ignore_errors   [bool] If True, invalid button-types will be ignored
                        and skipped. [Deflt: False] (overrides return_errors)
        check_against   [mapping|iterable] If iterable-type, check if buttons
                        passed already exist in the iterable. If mapping-type,
                        check buttons against mapping's iterable values.
                        Additionally checks against other buttons passed.
                        Raises an error if duplicates found, or returns error
                        if return_errors is True. This error cannot be 
                        ignored with ignore_errors.
        """
        #0=silent,1=return-errors,2=raise-'em
        error_handle = 1 if kwargs.get('return_errors') else 2
        error_handle = 0 if kwargs.get('ignore_errors') else error_handle
        check_against = None
        if 'check_against' in kwargs:
            check_against = []
            c_a = kwargs['check_against']
            if isinstance(c_a, dict):
                for v in c_a.values():
                    if hasattr(v,'__iter__'):
                        check_against.extend(v)
            elif hasattr(v,'__iter__'):
                check_against.extend(v)
        
        button_types = '+-chamony'
        convert_types = {'+':'y','-':'n','o':'m'}
        btn_list = []
        
        for b in buttons:
            if not isinstance(b,basestring):
                if error_handle:
                    err = TypeError("button-types must be strings, not {!r}.".format(b.__class__.__name__))
                    if error_handle -1:
                        raise err
                    return err
                continue
            if not b:   continue
            b = b[0].lower()
            if b not in button_types:
                if error_handle:
                    err = ValueError("{!r} is not a valid button-type.".format(b))
                    if error_handle -1:
                        raise err
                    return err
                continue
            b = convert_types.get(b,b)
            if check_against is not None:
                if b in check_against or b in btn_list:
                    err = DuplicateButtonError("button-type {!r} already added to group.".format(b))
                    if error_handle -1:
                        raise err
                    return err
            
            btn_list.append( b )
        
        return tuple(btn_list)
    
    
    def define_layouts(self, **sect_buttons):
        """Define all section layouts through keyword arguments.
        
        Keys are 'left', 'right','center', and 'justified', or just the first 
            letter of each.
        Arguments should be a list of button-types to assign to the relevant
            section.
        """
        sects = {'l':bLEFT,'r':bRIGHT,'c':bCENTER,'j':bJUSTIFIED}
        button_types = '+-chamony'
        
        new_sections = dict( (str(k), []) for k in [bLEFT,bRIGHT,bCENTER,bJUSTIFIED] )
        
        for kee, val in sect_buttons.items():
            if not kee:
                continue
            if kee.isdigit():
                if int(kee) not in sects.values():
                    raise ValueError, "invalid key {!r}".format(kee)
            elif kee[0].lower() in sects:
                kee = str(sects[kee[0].lower()])
            else:
                raise ValueError, "invalid key {!r}".format(kee)
            
            if not isinstance(val,(list,tuple)):
                raise TypeError, "keyword arguments of define_layouts() should be lists or tuples."
            
            #leest = []
            #for b in val:
            #    if not isinstance(b,basestring):
            #        raise TypeError, "button-types must be strings, not {!r}".format(b.__class__.__name__)
            #    if not b:
            #        continue
            #    if val[0].lower() not in button_types:
            #        raise ValueError, "unknown button-type {!r}".format(val[0].lower())
            #    if val[0].lower() == 'o':
            #        val = 'm'
            #    leest.append(val[0].lower())
            new_sections[kee] = self._parse_button_type(*val,check_against=new_sections)
        
        self.__sections = new_sections
    
    
    def define_section_layout(self, section, *buttons):
        
        sects = {'l':bLEFT,'r':bRIGHT,'c':bCENTER,'j':bJUSTIFIED}
        button_types = '+-chamony'
        
        if isinstance(section, int):
            if section not in sects.values():
                raise ValueError, -"section argument of set_layout() should represent an alignment section."
        elif isinstance(section, basestring):
            section = section[0].lower()
            if section not in sects or (section.isdigit() and int(section) in sects.values()):
                raise ValueError, "section argument of set_layout() should represent an alignment section."
            section = sects[section]
        else:
            raise TypeError, "section argument of set_layout() should be a string or int."
        section = str(section)
        #buttonz = []
        #for b in buttons:
        #    if not b:
        #        continue
        #    if not isinstance(b,basestring):
        #        raise TypeError, "buttons arguments of set_layout() should be strings."
        #    b = b[0].lower()
        #    if b not in button_types:
        #        raise ValueError, "Unknown button type {!r}.".format(b)
        #    if b == 'o':
        #        b = 'm'
        #    buttonz.append(b)
        c_a = dict(self.__sections)
        del c_a[section]
        self.__sections[str(section)] = self._parse_button_type(*buttons,check_against=c_a)
    
    
    def __donothing(s,*a,**k):
        pass
    columnconfigure = grid_columnconfigure = rowconfigure = grid_rowconfigure = \
            __donothing
    
    
    def __geometryManage(self, method, args=[], kwargs={}):
        #               Windowz     Mac
        #box margins    11          10-12
        #button spacing 7           12
        
        if self.__no_init:
            return
        if method not in ['grid','pack','place']:
            raise ValueError, "{!r} is not a valid method for ButtonGroup.__geometryManage()".format(method)
        method = ttk.Frame.grid if (method=='grid') else (ttk.Frame.pack if (method=='pack') else ttk.Frame.place)
        
        sects = dict(self.sections)
        
        for btyp,wdgt in self.__widgets.items():
            if btyp == 'm':
                for i in wdgt:
                    try:
                        i.destroy()
                    except: pass
                self.__widgets['m'] = []
            else:
                if wdgt is not None:
                    try:
                        wdgt.destroy()
                    except: pass
                    self.__widgets[btyp] = None
        if self.__stretcher is not None:
            try:
                self.__stretcher.destroy()
            except: pass
            self.__stretcher = None
        
        
        widget_row = 1
        col_itr = -1
        widget_padx = int(self.button_padx/2.0)
        widget_pady = int(self.button_pady/2.0)
        #self.__widget_opts
        #self.__widgets
        if self.alignment&bJUSTIFIED:
            
            if bJUSTIFIED in sects:
                gridopts = {'row':widget_row,'padx':widget_padx,'pady':widget_pady,'sticky':'ns'}
                for btyp in sects[bJUSTIFIED]:
                    
                    if not self.__widget_opts[btyp]:
                        continue
                    if btyp == 'm':
                        for opt in self.__widget_opts[btyp]:
                            col_itr += 1
                            wdgt = ttk.Button(self,**opt)
                            self.__widgets['m'].append(wdgt)
                            wdgt.grid(column=col_itr,**gridopts)
                            ttk.Frame.columnconfigure(self, col_itr, weight=1)
                    else:
                        col_itr += 1
                        wdgt = ttk.Button(self,**self.__widget_opts[btyp])
                        if self.default and self.default == btyp:
                            try:
                                wdgt.config(default=tk.ACTIVE)
                            except: pass
                            if self.binder and self.__widget_opts[btyp].get('command'):
                                try:
                                    self.binder.bind("<Return>",self.__widget_opts[btyp].get('command'))
                                except: pass
                        if btyp == 'c' and self.binder and self.__widget_opts[btyp]:
                            try:
                                self.binder.bind("<Escape>",self.__widget_opts[btyp].get('command'))
                            except: pass
                        
                        self.__widgets[btyp] = wdgt
                        wdgt.grid(column=col_itr,**gridopts)
                        ttk.Frame.columnconfigure(self, col_itr, weight=1)
        
        else:
            gridopts = {'row':widget_row,'padx':widget_padx,'pady':widget_pady,'sticky':'nsew'}
            for section in [bLEFT,bCENTER,bRIGHT]:
                #pre-mapping
                if not self.alignment&section:
                    if section == bLEFT:
                        col_itr += 1
                        ttk.Frame.columnconfigure(self, col_itr, weight=1)
                    continue
                
                #parsing
                for btyp in sects[section]:
                    
                    if not self.__widget_opts[btyp]:
                        continue
                    if btyp == 'm':
                        for opt in self.__widget_opts[btyp]:
                            col_itr += 1
                            wdgt = ttk.Button(self,**opt)
                            self.__widgets['m'].append(wdgt)
                            wdgt.grid(column=col_itr,**gridopts)
                            ttk.Frame.columnconfigure(self, col_itr, weight=0)
                    else:
                        col_itr += 1
                        wdgt = ttk.Button(self,**self.__widget_opts[btyp])
                        if self.default and self.default == btyp:
                            try:
                                wdgt.config(default=tk.ACTIVE)
                            except: pass
                            #if self.binder and self.__widget_opts[btyp].get('command'):
                            #    try:
                            #        self.binder.bind("<Return>",self.__widget_opts[btyp].get('command'))
                            #    except: pass
                        
                        self.__widgets[btyp] = wdgt
                        wdgt.grid(column=col_itr,**gridopts)
                        ttk.Frame.columnconfigure(self, col_itr, weight=0)
                
                #post-mapping
                if section in [bLEFT,bCENTER]:
                    col_itr += 1
                    ttk.Frame.columnconfigure(self,col_itr, weight=1)
                elif section in [bRIGHT]:
                    ttk.Frame.columnconfigure(self, col_itr+1, weight=0)
        
        col_width = col_itr+1
        self.__stretcher = ttk.Separator(self, orient=tk.HORIZONTAL)
        self.__stretcher.grid(row=int(not widget_row),column=0,columnspan=col_width,sticky='nesw')
        
        return method(self, *args, **kwargs)
    
    
    def add_button(self, btype, text, command=None, takefocus=False, underline=None):
        if not btype:
            raise TypeError, "btype parameter of add_button() must be a button-type."
        btype = self._parse_button_type(btype)[0]
        
        opts = {'text':text,'takefocus':bool(takefocus)}
        if underline is not None:
            opts['underline'] = underline
        if command is not None:
            opts['command'] = command
        if btype == 'm':
            self.__widget_opts['m'].append(opts)
        else:
            self.__widget_opts[btype] = opts
    
    #add_button() "aliases"
    def set_positive_button(self, text, **kwargs):
        self.add_button('y', text, **kwargs)
    
    def set_negative_button(self, text, **kwargs):
        self.add_button('n', text, **kwargs)
    
    def set_cancel_button(self, **kwargs):
        kwargs.setdefault('text','Cancel')
        self.add_button('c', **kwargs)
    
    def set_apply_button(self, **kwargs):
        kwargs.setdefault('text','Apply')
        self.add_button('a', **kwargs)
    
    def set_help_button(self, **kwargs):
        kwargs.setdefault('text','Help')
        self.add_button('h', **kwargs)
    
    def add_misc_button(self, text, **kwargs):
        self.add_button('m', text, **kwargs)
    
    #__geometryManage() "aliases"
    def grid_configure(self,**kw):
        return self.__geometryManage('grid',kwargs=kw)
    grid = grid_configure
    
    def place_configure(self,**kw):
        return self.__geometryManage('place',kwargs=kw)
    place = place_configure
    
    def pack_configure(self,**kw):
        return self.__geometryManage('pack',kwargs=kw)
    pack = pack_configure
