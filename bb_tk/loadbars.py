#!/usr/bin/env python

import bb_tk

import Tkinter as tk #Pretty sure this is the third method for importing
                     #  Tkinter that I've used now...
import ttk


import math

#class _loadbar_box(ttk.Frame):
#    
#    dimensions = {'loadbar_box':}
#    
#    def __init__(self, master, *args, **kwargs):
#        ttk.Frame.__init__(self,master,*args,**kwargs)
        

#global _order_base
_order_base = 1024

_prfxs = [['','k','M','G','T'],['','Ki','Mi','Gi','Ti']]

def _quick_prefx(input_amt,dec_places=2):
    magntd = 0
    if input_amt > 0 and (0 < _order_base and _order_base != 1):
        magntd = int(math.floor(math.log(input_amt,_order_base)))
    if magntd >= len(_prfxs[0]):
        magntd = len(_prfxs[0])-1
    new_val = input_amt*1.0 / (_order_base**magntd)
    return "{0:.0{1}f} {2}B".format(new_val,int(min(dec_places,magntd*3)),_prfxs[_order_base==1024][magntd])

class loadbar_window(tk.Toplevel):
    
    cmd_strt = {'window_config':{'pady':5,'padx':5},
                'minsize':(400,110),
                'resizable':(True,False),
                'maxsize':(10000,110),
                'rowconfig':{0:{'weight':1},1:{'weight':1},2:{'weight':1},
                             3:{'weight':1},4:{'weight':1}},
                'colconfig':{0:{'minsize':18},1:{'weight':1},2:{'minsize':72}}
    }
    cmd_cnfg = {'LabelFile':{'anchor':'w','font':'TkHeadingFont'},
                'LabelRecv':{'anchor':'w','font':'TkTextFont'},
                'LabelOf':{'anchor':'center','font':'TkSmallCaptionFont'},
                'LabelTotal':{'anchor':'w','font':'TkTextFont'},
                'LabelCountr':{'anchor':'center'},
                'LabelPercnt':{'anchor':'center','font':'TkCaptionFont'},
                'Progress':{'length':140}
    }
    cmd_grid = {'LabelFile':{'column':0,'columnspan':2,'row':2,'sticky':'w'},
                'LabelRecv':{'column':1,'row':3,'sticky':'w'},
                'LabelOf':{'column':0,'row':4,'sticky':'ew'},
                'LabelTotal':{'column':1,'row':4,'sticky':'w'},
                'LabelCountr':{'column':2,'row':2,'sticky':'nesw'},
                'LabelPercnt':{'column':2,'row':3,'rowspan':2,'sticky':'nesw'},
                'Progress':{'column':0,'row':1,'columnspan':3,'sticky':'nesw'}
    }
    fmts = {'Total':"{0} ({1:,.0f} B) Total",'Percnt':"{0:.02%}",
            'Recv':"{0} ({1:,.0f} B) Received"}
    
    def __init__(self,master=None):
        tk.Toplevel.__init__(self,master)
        
        self.transient(self.master)
        global _order_base
        if bb_tk.CONFIG.getopt('BinOrDec','bin').lower().startswith('bin') ^ _order_base == 1024:
            cfg = bb_tk.CONFIG.getopt('BinOrDec','bin').lower()
            if cfg.startswith('bin') and _order_base == 1000:
                _order_base = 1024
            elif cfg.startswith('dec') and _order_base == 1024:
                _order_base = 1000
        
        self.__labels = dict(  [(nem[5:],None) for nem in self.cmd_cnfg if nem.startswith('Label')]  )
        #self.__labels = {'File':None,'Recv':None,'Of':None,'Total':None,'Percnt':None}
        self.__vars = dict(  [(nem,tk.StringVar()) for nem in self.__labels]  )
        self.__vars['Progress'] = tk.IntVar()
        
        self.config(**self.cmd_strt['window_config'])
        self.minsize(*self.cmd_strt['minsize'])
        self.resizable(*self.cmd_strt['resizable'])
        for i,v in self.cmd_strt['rowconfig'].items():
            self.rowconfigure(i,**v)
        for i,v in self.cmd_strt['colconfig'].items():
            self.columnconfigure(i,**v)
        
        for nem in self.__labels.keys():
            self.__labels[nem] = ttk.Label(self,textvariable=self.__vars[nem],  **self.cmd_cnfg.get('Label'+nem,{}))
        self.__Progress = ttk.Progressbar(self, variable=self.__vars['Progress'], **self.cmd_cnfg.get('Progress',{}))
        
        for nem in self.__labels.keys():
            self.__labels[nem].grid(**self.cmd_grid.get('Label'+nem,{}))
        self.__Progress.grid(**self.cmd_grid.get('Progress',{}))
        
        #status:    0=waiting, 1=running, 2=done-open, 4=closed
        self.__sts_ = { 'status':0,'total_len':0,'len_so_far':0.0,
                        'curr_is_determ':False,'curr_file':'',
                        'curr_file_num':None,'curr_file_sz':0,'total_files':0}
        # [ (dlable_file, dest_string) , ...]
        self.__fls_ = []
        
        self.__vars['Of'].set('Of')
        bb_tk.STYLE.app_icon_setter(self)
        self.title('Preparing Download...')
        
    
    def __updtr(self,part,val,add=False):
        #update 'total' before 'len_so_far'
        #updating 'len_so_far' also updates the Percnt var
        #updating 'file' also increments 'cur_file_num' and the Countr var
        part = part.lower()
        if part == 'total':
            if add:
                val += self.__sts_['total_len']
            self.__vars['Total'].set(self.fmts['Total'].format(_quick_prefx(val),val))
            self.__sts_['total_len'] = val
            self.__Progress.config(maximum=val)
        elif part == 'len_so_far':
            val = val*1.0
            if add:
                val += self.__sts_['len_so_far']
            self.__vars['Recv'].set(self.fmts['Recv'].format(_quick_prefx(val),val))
            self.__vars['Progress'].set(int(val))
            if self.__sts_['total_len'] != 0:
                self.__vars['Percnt'].set(self.fmts['Percnt'].format(val/self.__sts_['total_len']))
            self.__sts_['len_so_far'] = val
        elif part == 'file':
            if self.__sts_['curr_file'] == val:
                return
            self.__sts_['curr_file'] = val
            self.__vars['File'].set(val)
            self.__sts_['curr_file_sz'] = 0
            i = self.__sts_['curr_file_num']
            if i is None:
                i = 0
            i += 1
            self.__sts_['curr_file_num'] = i
            newctr = "{} of {}".format(i,self.__sts_['total_files'])
            self.__vars['Countr'].set(newctr)
            self.title("Downloading {}...".format(newctr))
        else:
            print "WARNING: Invalid 'part' argument to updtr: {!r}".format(part)
        self.update_idletasks()
    
    def __file_callback(self,sz):
        if self.__sts_['status'] != 1:
            print "WARNING: file_callback called while status is set to {!r}".format(self.__sts_['status'])
            return
        old_fl_sz = self.__sts_['curr_file_sz']
        self.__sts_['curr_file_sz'] = sz
        sz = sz - old_fl_sz
        if not self.__sts_['curr_is_determ']:
            self.__updtr('total',sz,True)
        self.__updtr('len_so_far',sz,True)
    
    def __shutdown(self,failed=False):
        self.update_idletasks()
        self.overrideredirect(False)
        if failed:
            num = 1 + self.__sts_['total_files'] - self.__sts_['curr_file_num'] 
            bb_tk.tkMessageBox.showwarning("Download Failed","The download failed on file {!r}.\n{} file(s) not downloaded.".format(self.__sts_['curr_file'],num))
        self.__sts_['status'] = 4
        self.destroy()
    
    def add_file(self,dl_attachmnt,dest):
        if self.__sts_['status'] != 0:
            return (None, self.__sts_['status'])
            
        if not isinstance(dl_attachmnt, bb_tk.blackbird.downloadable_file):
            raise TypeError, "Argument 1 of add_file() must be a downloadable_file instance, not {!r}".format(dl_attachmnt.__class__.__name__)
        if dl_attachmnt.closed:
            return False
        if not isinstance(dest, basestring):
            raise TypeError, "Argument 2 of add_file() must be a filepath string, not {!r}".format(dest.__class__.__name__)
        self.__fls_.append( (dl_attachmnt, dest) )
        return True
    
    def start(self):
        if self.__sts_['status'] != 0:
            return (None, self.__sts_['status'])
        if not self.__fls_:
            return []
        
        self.grab_set()
        
        self.__sts_['status'] = 1
        
        toRun_det = []
        toRun_indet = []
        done = []
        
        for itm in self.__fls_:
            if itm[0].total_length is None or itm[0].total_length <= 0:
                toRun_indet.append( itm )
            self.__updtr('total',itm[0].total_length,True)
            toRun_det.append( itm )
        
        self.__sts_['total_files'] = len(toRun_det) + len(toRun_indet)
        
        
        self.deiconify()
        self.__Progress.config(mode='indeterminate')
        self.update_idletasks()
        self.overrideredirect(True)
        
        for fl,dest in toRun_indet:
            self.__updtr('file',fl.name)
            print "dest: {}".format(dest)
            try:
                ret = fl.read_to(dest,progress_funct=self.__file_callback)
            except:
                try:
                    self.__shutdown()
                finally:
                    raise
                    return Exception
            if not ret:
                self.__shutdown(True)
                return False
        
        self.__sts_['curr_is_determ'] = True
        self.__Progress.config(mode='determinate')
        
        for fl,dest in toRun_det:
            self.__updtr('file',fl.name)
            try:
                ret = fl.read_to(dest,progress_funct=self.__file_callback)
            except:
                try:
                    self.__shutdown()
                finally:
                    raise
                    return Exception
            if not ret:
                self.__shutdown(True)
                return False
        
        self.title('Complete!')
        self.update_idletasks()
        self.overrideredirect(False)
        
        self.__sts_['status'] = 2
        return True

#class loadbar_group(tk.Toplevel):
#    
#    dimensions = { 'window_config':{'pady':5,'padx':5},
#                'minsize':(500,400), 
#                'resizable':(False,True),
#                'rowconfig':{0:{'weight':1}},  
#                'maxsize':(500,1500),
#                'ldrsSum_config':{'borderwidth':2,'relief':'groove','width':490},
#                'ldrsScroll_config':{'borderwidth':3,'relief':'sunken'},
#                'ldrsSum_grid':{'column':0,'row':1,'sticky':'nesw'},  
#                'ldrsScroll_grid':{'column':0,'row':0,'sticky':'nesw'},
#                'ldrsScroll_colconfig':{0:{'weight':1}}
#                }
#                #ldrsScrollbar = ttk.Scrollbar(ldrsScroll, orient=tk.VERTICAL)
#                #ldrsScrollbar.grid(row=0,column=1,sticky='nesw')
#                #
#                #ldrsCanvas = tk.Canvas(ldrsScroll,yscrollcommand=ldrsScrollbar.set)
#                #ldrsCanvas.grid(column=0,row=0,sticky='nesw')
#                #
#                #ldrsScrollbar.config(command=ldrsCanvas.yview)
#                #ldrsCanvas.xview_moveto(0)
#                #ldrsCanvas.yview_moveto(0)
#                #
#                #ldrsBody = ttk.Frame(ldrsCanvas)
#                #interior_id = ldrsCanvas.create_window(0,0,window=ldrsBody, anchor='nw')
#                
#    
#    def __init__(self, master, *args, **kwargs):
#        #ttk.Frame.__init__(self,master,*args,**kwargs)
#        
#        self.__loadbarz = {}
#        
#    
#    def add_loadbar(self, 
#    
#    
#    
#    def add_download_loadbar(self, dlable_file, dest_path):
#        

