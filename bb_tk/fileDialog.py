#!/usr/bin/env python

#import bb_tk

import subprocess,os
from sys import platform as sysplatform

import Tkinter as tk
import tkFileDialog

__all__ = ['askdirectory','askopenfile','askopenfiles','askopenfilename', \
           'askopenfilenames','asksaveasfile','asksaveasfilename']

#if linux, try zenity

# GENERAL
#   `zenity %dialog-type% ...`

# FILE SELECTION
#`zenity --file-selection --title %string% --window-icon %path% ...`

#   `--multiple`                permits multi-selection
#   `--separator %string%`      return separator for --multiple [Def: "|"]
#
#   `--directory`               can only select a directory
#
#   `--save`                    
#   `--filename %basename%`     initial filename to save as for `--save`
#   `--confirm-overwrite`       confirmation popup if selection exists with `--save`
#

global _zenity_available
_zenity_available = False

if sysplatform.lower().startswith("linux"):
    tmp,prtz = None,None
    try:
        tmp = subprocess.check_output(['zenity','--version'],stderr=subprocess.STDOUT,universal_newlines=True)
        tmp = tmp.split('\n',1)[0].strip()
        if tmp.count('.') >= 1:
            prtz = tmp.split('.')
            if prtz[0].isdigit():
                prtz[0] = int(prtz[0])
            else:
                prtz[0] = None
            if prtz[1].isdigit():
                prtz[1] = int(prtz[1])
            else:
                prtz[1] = None
                
            if prtz[0] and prtz[1] is not None and (prtz[0] > 2 or (prtz[0] == 2 and prtz[1] >= 23)):
                _zenity_available = True
    except:
        pass
    finally:
        del prtz
        del tmp

class _zenity_file_selection(tkFileDialog._Dialog):
    
    #ztype: o[pen],s[ave],d[irectory]
    
    _separator = '\n'
    
    def __handle_return(self,val,retcode,allow_new=False):
        """Parse returned value
        
        (-9, None)      No idea what happened.
        (-3, None)      Incompatible zenity version.
        (-2, Exception) Error occurred, raisable exception provided.
        (-1, '')        Empty return value.
        (-1, [...])     The paths in the list don't exist.
        (-1, None)      Not a valid return value.
        ( 0, ...)       Directory/File(s) exist.
        ( 1, ...)       Valid path, parent exists but file doesn't (new file).
                            If multiple files are handled and this code is
                            used, at least one fits this description.
        """
        if val == '\n':
            return (-1,'')
        if not isinstance(val,basestring) or (val and val[-1] != '\n'):
            return (-1,None)
        if not val:
            return (-1,'')
        val = val[:-1]
        if not val:
            return (-1,'')
        for part in ['This option is not available','--']:
            if val.startswith(part):
                return (-3, None)
        for part in ['You must specify a dialog type', 'Two or more dialogs']:
            if val.startswith(part):
                return (-9, None)
        if retcode == 0 or (val[0] == '/' or ( 65 <= ord(val[0]) <= 90 and val[1:3] in [':\\',':/'])):
            parts = val.split(self._separator)
            code = 0
            retparts = []
            for nem in parts:
                nem2 = os.path.abspath(os.path.normpath(nem))
                if os.path.exists(nem2) or os.access(nem2,os.F_OK):
                    if code >= 0:
                        retparts.append(nem2)
                
                elif os.path.isdir(os.path.dirname(nem2)) and not (self.options['ztype'] == 'o' or (self.options['ztype'] == 'd' and self.options['mustexist'])):
                    if code >= 0:
                        retparts.append(nem2)
                        if code == 0:
                            code = 1
                
                else:
                    if code >= 0:
                        code = -1
                        retparts = []
                    retparts.append(nem)
                print retparts
            
            return (code, tuple(retparts))
        return (-9, None)
    
    def _handle_patterns(self,pattrnz):
        pattrnz = pattrnz.strip().split()
        newpatternz = []
        for p in pattrnz:
            if p == '*.*' and '*' not in newpatternz:
                newpatternz.append('*')
            if p.lower() not in newpatternz:
                newpatternz.append(p.lower())
            if p.upper() not in newpatternz:
                newpatternz.append(p.upper())
        
        return " ".join(newpatternz)
    
    def _fixoptions(self):
        ztype = str(self.options.get('ztype','o') or 'o').lower()[0]
        if ztype not in ['o','s','d']:
            ztype = 'o'
        
        newopts = {}
        newopts['ztype'] = ztype
        newopts['title'] = {'o':'Open','s':'Save As','d':'Choose Directory'}.get(ztype)
        newopts['initialdir']  = ""
        newopts['initialfile'] = "" 
        filetypez = []
        newopts['confirmoverwrite'] = True
        newopts['multiple'] = False
        
        
        
        for k,v in self.options.items():
            if k.lower() == 'title':
                newopts['title'] = v
            
            elif k.lower() == 'filetypes':
                newopts['filetypes'] = tuple(self.options['filetypes'])
                
                for labl,pattrnz in newopts['filetypes']:
                    filetypez.append( "{} | {}".format(labl, self._handle_patterns(pattrnz)) )
            
            elif k.lower() == 'initialdir':
                v = os.path.abspath(os.path.expanduser(v))
                if os.path.isdir(v):
                    newopts['initialdir'] = v
                else:
                    newopts['initialdir'] = os.path.expanduser('~')
            elif k.lower() == 'initialfile':
                newopts['initialfile'] = v
            
            elif k.lower() == 'defaultextension':
                newopts['defaultextension'] =  v if (v != '.') else ''
            
            elif k.lower() == 'confirmoverwrite':
                newopts['confirmoverwrite'] = bool(v)
            
            elif k.lower() == 'multiple':
                newopts['multiple'] = bool(v)
            
            elif k.lower() == 'mustexist':
                newopts['mustexist'] = bool(v)
        
        #set up arguments
        self.__args = ['zenity','--file-selection','--separator',self._separator, \
                                '--title',newopts['title']]
        
        if ztype == 'd':
            self.__args.append('--directory')
            #using --directory with a file-filter makes directories unselectable
            filetypez = []
        elif ztype == 's':
            self.__args.append('--save')
        
        filename_arg = os.path.join(newopts['initialdir'],newopts['initialfile'])
        if filename_arg:
            self.__args.extend( ['--filename',filename_arg] )
        
        for ft in filetypez:
            self.__args.extend( ['--file-filter',ft] )
        
        if newopts['confirmoverwrite']:
            self.__args.append('--confirm-overwrite')
        
        if newopts['multiple']:
            self.__args.append('--multiple')
        
        self.options = newopts
    
    def __error(self,noexist=[]):
        #zenity --error [--text %str%] [--title %str%] [--window-icon (error|info|question|warning)] [--no-wrap] [--no-markup]"
        if noexist and isinstance(noexist,(list,tuple)):
            errstr = "File <b>{}</b> does not exist."
            noexist = ["<b>{}</b>".format(i) for i in noexist]
            if len(noexist) > 1:
                errstr = "Files "
                errstr += ", ".join(noexist[:-1])
                if len(noexist) > 2:
                    errstr += ","
                errstr += " and {} do not exist.".format(noexist[-1])
            else:
                errstr = errstr.format(noexist[0])
            errproc = subprocess.Popen(['zenity','--error','--text',errstr],stdout=subprocess.PIPE,stderr=subprocess.PIPE)
            i = errproc.wait()
            return
    
    def __run(self):
        result = ''
        global _zenity_available
        try:
            proc = subprocess.Popen(self.__args,stdout=subprocess.PIPE,stderr=subprocess.PIPE,universal_newlines=True)
            result,errdata = proc.communicate()
        except OSError:
            if self.__args[0] == 'zenity' and _zenity_available:
                _zenity_available = False
                raise RuntimeError, "An invalid option was set and fixed, try again."
            else:
                if self.__args[0].startswith('--'):
                    self.__args = ['zenity'] + self.__args
                    return self.__run()
                elif _zenity_available:
                    _zenity_available = False
                    raise RuntimeError, "An invalid option was set and fixed, try again."
                else:
                    raise RuntimeError, "An internal error has occurred. " \
                            "Specifically, the program 'zenity' should have " \
                            "been called, but zenity is not the first argument " \
                            "in the subprocess call."
        print "###RESULT: {!r}".format(result)
        print "###ERRDATA: {!r}".format(errdata)
        opt_mult = bool(self.options.get('multiple',False))
        res_code, res_value = self.__handle_return(result,proc.returncode)
        err_code, err_value = self.__handle_return(errdata,None)
        print "###        CODE   VALUE"
        print "###RESULT: {:<5}  {}".format(res_code,res_value)
        print "### ERROR: {:<5}  {!r}\n".format(err_code, err_value)
        
        if res_code >= 0:
            if self.options['ztype'] == 's':
                if res_value and '.' not in os.path.basename(res_value[0]):
                    #screw Tk implementation, no need to add an extension if the file exists
                    if not os.path.exists(res_value[0]):
                        res_value = ( res_value[0] + self.options['defaultextension'] , )
            if opt_mult:
                return res_value
            return res_value[0] if res_value else ''
        
        elif res_code == -1 and isinstance(res_value, (list,tuple)):
            self.__error(res_value)
            return self.__run()
        
        if proc.returncode in [1,5]:
            #cancelled/closed
            return () if opt_mult else ''
        
        if proc.returncode == -1 or proc.returncode > 5 or err_code < 0:
            if err_code == -2:
                raise err_value
            if err_code == -3:
                _zenity_available = False
                raise EnvironmentError, "An invalid option was set and fixed, try again."
            raise RuntimeError, "Bad response provided by zenity; issue unknown."
        
        
    
    def show(self, **options):
        
        for k,v in options.items():
            self.options[k] = v
        
        self._fixoptions()
        
        return self.__run()


def askopenfilename(**options):
    if _zenity_available:
        return _zenity_file_selection(**options).show(ztype='o')
    return tkFileDialog.askopenfilename(**options)

def asksaveasfilename(**options):
    if _zenity_available:
        return _zenity_file_selection(**options).show(ztype='s')
    return tkFileDialog.asksaveasfilename(**options)

def askopenfilenames(**options):
    options['multiple']=1
    return askopenfilename(**options)

def askopenfile(mode = "r", **options):
    filename = askopenfilename(**options)
    if filename:
        return open(filename, mode)
    return None

def askopenfiles(mode = "r", **options):
    files = askopenfilenames(**options)
    if files:
        ofiles=[]
        for filename in files:
            ofiles.append(open(filename, mode))
        files = ofiles
    return files

def asksaveasfile(mode = "w", **options):
    filename = asksaveasfilename(**options)
    if filename:
        return open(filename, mode)
    return None

def askdirectory(**options):
    if _zenity_available:
        return _zenity_file_selection(**options).show(ztype='d')
    return tkFileDialog.askdirectory(**options)
