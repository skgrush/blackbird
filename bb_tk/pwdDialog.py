#!/usr/bin/env python

import bb_tk,niceButton

from Tkinter import *
from ttk import *
import tkSimpleDialog

import numbers

def _validate_or_default(val, default=None, min_length=1, max_length=20, \
                            chop_at_newlines=True, allow_numeric=True, \
                            ellipsis=True):
    """Performs validation of input values.
    
    Order of operations:
        1.  allow_numeric   |   chop_at_newline
        2.  min_length
        3.  max_length
    -
    Operations:
        allow_numeric       If True and a numeric-type value is provided for
                                val, it will be converted to a string. If
                                False and value is numeric, returns default.
        chop_at_newlines    If True: cuts off string at first newline. 
                                Newline defined as '\n', '\v', or '\r\n'.
                                If a newline exists at index 0, returns default.
        min_/max_length     If less than min_, returns default. If longer than
                                max_length and ellipsis is True, cuts to max_
                                and adds an ellipsis; if ellipsis is False,
                                returns default.
                                If max_length is None, any length accepted.
        ellipsis            If True and max_length exceeded, val is chopped
                                and an ellipsis is appended.
    """
    if default is None:
        default = ''
    
    if isinstance(val,numbers.Number):
        if allow_numeric:
            val = str(val)
        else:
            return default
    
    elif isinstance(val,basestring):
        if chop_at_newline:
            nCRLF = val.find('\r\n')
            nLF   = val.find('\n')
            nVT   = val.find('\v')
            if 0 in [nCRLF,nLF,nVT]:
                return default
            nCRLF = 9999 if (nCRLF == -1) else nCRLF
            nLF   = 9999 if (nLF   == -1) else nLF
            nVT   = 9999 if (nVT   == -1) else nVT
            poz = min(nCRLF,nLF,nVT)
            if poz != 9999:
                val = val[:poz]
        
        if len(val) < min_length:
            return default
        elif max_length and len(val) > max_length:
            if ellipsis:
                val = u"{}\u2026".format(val[:max_length])
            else:
                return default
    else:
        return default
    return val

class _PwdDialog(tkSimpleDialog.Dialog):
    
    def __init__(self, parent, title='Enter Credentials', **kwargs):
        
        self.opts = {}
        self.opts['uname_prompt'] = _validate_or_default( kwargs.get('uname_prompt'),'Username',0,30)
        self.opts['pwd_prompt']   = _validate_or_default( kwargs.get('pwd_prompt'  ),'Password',0,30)
        self.opts['submit_label'] = _validate_or_default( kwargs.get('submit_label'),'Login',   1,20)
        self.opts['cancel_label'] = _validate_or_default( kwargs.get('cancel_label'),'Cancel', 1,20)
        t_m = kwargs.get('top_message',None)
        if not t_m or (isinstance(t_m,basestring) and not t_m.strip()):
            t_m = None
        self.opts['top_message'] = t_m
        
        if not parent:
            import Tkinter
            parent = Tkinter._default_root
        
        tkSimpleDialog.Dialog.__init__(self,parent, title)
    
    
    
    
    def body(self, master):
        if self.opts['top_message']:
            self.top_message = Label(master,anchor='center',text=self.opts['top_message'])
            self.top_message.grid(row=0,column=0,columnspan=3,sticky='nesw')
        self.uname_prompt = Label(master,anchor='w',text=self.opts['uname_prompt'])
        self.uname_prompt.grid(row=1,column=0,sticky='nesw')
        self.pwd_prompt = Label(master,anchor='w',text=self.opts['pwd_prompt'])
        self.pwd_prompt.grid(row=2,column=0,sticky='nesw')
        self.__PwdDialog_ = (StringVar(),StringVar())
        uname_input = Entry(master,exportselection=0,textvariable=self.__PwdDialog_[0])
        pwd_input = Entry(master,exportselection=0,show=bb_tk.CONFIG.getopt('pwd_char',u'\u2022'),textvariable=self.__PwdDialog_[1])
        uname_input.grid(row=1,column=2,sticky='nsw')
        pwd_input.grid(row=2,column=2,sticky='nsw')
        
        
        return uname_input
    
    
    def buttonbox(self):
        
        box = niceButton.ButtonGroup(self, binder=self)
        
        box.set_positive_button(self.opts['submit_label'], command=self.ok, \
                                takefocus=True)
        box.set_cancel_button(text=self.opts['cancel_label'], command=self.cancel, \
                                takefocus=True)
        
        self.bind("<Return>", self.ok)
        self.bind("<Escape>", self.cancel)
        
        box.pack(side='bottom',fill='x')
        #box.grid(row=3,column=0,columnspan=3,sticky='nesw')
    
    
    def validate(self):
        u,p = self.__PwdDialog_
        try:
            self.result = u.get(), p.get()
            print self.result
        except:
            print "Failure"
            pass
        return 1
    
    def getresult(self):
        return self.result
        

def getpass(parent, **kwargs):
    
    d = _PwdDialog(parent, **kwargs)
    return d.getresult()
