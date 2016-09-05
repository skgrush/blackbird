#!/usr/bin/env python

print "Tree Browser!"

import weakref,os
import bb_tk,loadbars

blackbird = bb_tk.blackbird
bb_utilities = bb_tk.bb_utilities

from Tkinter import *
from ttk import *
import tkFileDialog


class ItemError(ValueError):
    pass

class TreeError(RuntimeError):
    pass

class content_tree(object):
    """A content tree that can optionally be standalone
    
    'master' is the parent widget of the content_tree. If it is None,
        the content_tree will be given its own window.
    -
    KWARGS:
        'visible_columns' should be an iterable containing names of 
            attributes of the content_object class that will be displayed.
            If it is not provided, all attributes are shown.
        'raise_on_baditem' is a Boolean; if True, exceptions are raised
            when items are added that are of the wrong type. If false,
            items will be silently discarded. [Def: False]
        'raise_on_dupe' is like 'raise_on_baditem', but for duplicate items.
        'selectmode' determines what the user may select. Options are:
            'browse'    Only one item at a time
            'extended'  Multiple at a time
            'none'      Disable selection
        'title' is the title of the window (ignored if 'master' is defined)
        'text_cancel' is the text for the cancel button. If it is None,
            there is no Cancel button. [Def: "Cancel"]
        'text_submit' is the text for the submit button. If it is None,
            there is no Submit button. [Def: "Submit"]
        'courses' is a Boolean; if True, the tree's roots will be course
            objects. If False, content_object instances can be added
            directly (NotImplemented).
    """
    def __init__(self, master, **kwargs):
        self.master = master
        
        self.columns = [attr for attr in blackbird.content_object.__slots__ if attr[0] != '_']
        
        
        def_visible_cols = self.columns[:]
        for val in ['attachments']:
            def_visible_cols.remove(val)
        
        #getting kwargs
        visible_columns  = kwargs.get('visible_columns',def_visible_cols)
        #good visible_columns value: ('name','ext_link','attachments')
        raise_on_baditem = kwargs.get('raise_on_noid',False)
        raise_on_dupe    = kwargs.get('raise_on_dupe',False)
        self.selectmode  = kwargs.get('selectmode','extended')
        self.w_title     = kwargs.get('title','Tree Browser')
        self.text_cancel = kwargs.get('text_cancel','Cancel')
        self.text_submit = kwargs.get('text_cancel','Submit')
        self.use_courses = True
        
        #parsing,saving kwargs
        self.visible_columns = []
        
        for i in visible_columns:
            if i in def_visible_cols:
                self.visible_columns.append(i)
        
        self.visible_columns = tuple(self.visible_columns + ['attachments'])
        
        self.raise_on = ( bool(raise_on_baditem), bool(raise_on_dupe) )
        self.__selectmode = 'extended'
        
        
        self._content = {}
        
        self.__inst_data = {}
        
        self._course_obj = None
        
        self._idx_of_type = self.columns.index('type')
    
    @property
    def generate(self):
        if self.master:
            return self.__generate_embedded
        return self.__generate_standalone
    
    @property
    def selectmode(self):
        return self.__selectmode
    
    @selectmode.setter
    def selectmode(self, val):
        if val is None: val = 'none'
        if isinstance(val,basestring):
            val = val.lower()
            if val in ['none','browse','extended']:
                self.__selectmode = val
                return
        raise ValueError, "content_tree attribute 'selectmode' must be none, browse, or extended"
    
    def __add_content(self, parent_id, *items):
        
        #content is added as a tuple with an iid set to its content_id
        #attachments are added 
        
        if parent_id is None or parent_id == '':
            parent_id = ''
        
        for item in items:
            
            added = False
            
            try:
                ret_item = ['']*len(self.columns)
                
                cont_id = item.content_id
                
                if cont_id is None:
                    continue
                
                for i in range(len(self.columns)):
                    x = None
                    if self.columns[i] == 'attachments':
                        x = len(item.attachments)
                    else:
                        x = getattr(item, self.columns[i])
                    
                    ret_item[i] = '' if x is None else x
                
                if cont_id not in self._content:
                    self._content[cont_id] = (parent_id, ret_item)
                    added = True
                
                else:
                    raise ItemError, "Item {} already in _content".format(item)
                
            except ItemError:
                #LOG_exception
                if self.raise_on[1]:
                    raise
            
            except e:
                #LOG_exception
                pass
            
            if added and item._contents:
                self.__add_content(cont_id, *item._contents)
    
    #def add_content(self, parent_id, *items):
    #    
    #    if parent_id is None or parent_id == '':
    #        parent_id = ''
    #    
    #    for item in items:
    #        if not isinstance(item,blackbird.content_object):
    #            if self.raise_on[0]:
    #                raise TypeError, "add_content() items must be blackbird.content_objects, not {!r}".format(item.__class__.__name__)
    #            continue
    #        if 'content_id' not in item.all_set_attrs:
    #            if self.raise_on[0]:
    #                raise ItemError, "item {} has no content_id".format(item)
    #            continue
    #        if item['content_id'] in self._content:
    #            if self.raise_on[1]:
    #                raise ItemError, "item {} already added to tree".format(item)
    #        self._content[item['content_id']] = item
    
    
    def set_course(self,course_obj):
        if not isinstance(course_obj,blackbird.course_object):
            raise TypeError, "set_course() argument must be a course_object instance"
        self._content = {}
        content_dict = course_obj.content_dict
        
        if not content_dict:
            return
        
        if not isinstance(content_dict.values()[0],blackbird.content_object):
            ret = course_obj.bb_inst.update_course_content(course_obj)
            
            content_dict = course_obj.content_dict
            if not ret or not isinstance(content_dict.values()[0],blackbird.content_object):
                return
        
        self._course_obj = course_obj
        self.__add_content(None,*content_dict.values())
    
    ##################
    ## Tree Methods ##
    ##################
    
    def __download_files(self,*args):
        # args = [ (content_object, filename), ... ]
        
        goodargs = []
        for i in args:
            if not isinstance(i,(tuple,list)) or len(i) < 2:
                continue
            if not (isinstance(i[0],blackbird.content_object) and \
                    isinstance(i[1],basestring)):
                continue
            goodargs.append(i)
        if not goodargs:
            return
        initdir = bb_tk.CONFIG.getopt('defaultdir')
        
        loadwin = loadbars.loadbar_window(master=self.__inst_data.get('frame').master)
        
        print "State: {}".format(self.__inst_data.get('frame').state())
        self.__inst_data.get('frame').master.state('normal')
        print "State: {}".format(self.__inst_data.get('frame').state())
        
        if len(goodargs) == 1:
            contentobj,filenem = goodargs[0]
            ext = os.path.splitext(filenem)[1]
            initfile = filenem
            ftypes = [('Whatever','.*')]
            if ext:
                ftypes.insert(0,('',ext))
            
            ret = tkFileDialog.asksaveasfilename(defaultextension=ext, \
                    filetypes=ftypes,initialdir=initdir,initialfile=initfile, \
                    parent=self.__inst_data.get('frame').master)
            if not ret:
                return None
            
            dl_attach = contentobj.download_attachment(filenem)
            if dl_attach is blackbird.NOT_LOGGED_IN:
                return dl_attach
            
            loadwin.add_file(dl_attach,ret)
        else:
            retdir = tkFileDialog.askdirectory(initialdir=initdir, \
                        parent=self.__inst_data.get('frame').master,mustexist=True)
            
            if not retdir:
                return None
            
            for contentobj,filenem in goodargs:
                filepath = os.path.join(retdir,filenem)
                try:
                    dl_attach = contentobj.download_attachment(filenem)
                except TypeError:
                    continue
                if not dl_attach:
                    continue
                if dl_attach is blackbird.NOT_LOGGED_IN:
                    return dl_attach
                
                loadwin.add_file(dl_attach,filepath)
        
        retted = loadwin.start()
        
        if retted == True:
            return True
        if retted == []:
            return None
        elif retted == Exception:
            return Exception
        elif retted == False:
            return False
        
        loadwin.quit()
        self.__inst_data.get('frame').deiconify()
    
    def __context_menu(self,event=None):
        catch_event_types = ['5',5]
        
        tree = self.__inst_data.get('tree')
        if not event or event.type not in catch_event_types or not tree:
            return
        
        tree_region = None
        try:
            tree_region = tree.identify_region(event.x,event.y) #requires Tk 8.6
        except TclError: pass
        
        tree_row_iid = tree.identify_row(event.y)
        tree_col_index = tree.identify_column(event.x)
        tree_col_name = None
        if tree_col_index:
            try:    
                tree_col_name = tree.column(tree_col_index,option='id')
            except TclError: pass
        
        tree_hover_element = None
        try:
            print "###Try identify('element',x,y)"
            tree_hover_element = tree.identify('element',event.x,event.y)
            print "###Success! {!r}".format(tree_hover_element)
        except:
            print "###Failed. :("
        
        selection = []
        try:
            selection = list(tree.selection())
        except:
            pass
        
        #if there's no selection, check if mouse if over a row; if not,
        #   just return. If there IS a selection, bypass this block
        if not selection and tree_row_iid:
            selection = [tree_row_iid]
        elif not selection:
            return
        
        context_menu_object = Menu(tree,tearoff=0)
        
        if len(selection) == 1:
            itm = selection[0]
            if not (isinstance(itm,basestring) and itm.isdigit()):
                print "Not a normal item (couldn't get its iid)"
                return
            itm_id = int(itm)
            itm = self._course_obj.get_contentitem(itm_id)
            if not itm:
                print "_course_obj didn't have the iid...."
                return
            elif not isinstance(itm,blackbird.content_object):
                print "course_object.get_contentitem returned a non-content_object..."
                return
            
            if itm['ext_link']:
                url = itm['ext_link']
                titl = "Open external link in browser"
                
                exiss,code,reason = bb_utilities.check_url(url,ret_type=3)
                
                if exiss:
                    context_menu_object.add_command(label=titl,command=(lambda: bb_tk.CONFIG.browser_open(url,2)))
                else:
                    context_menu_object.add_command(label="External link returned '{}: {}'".format(code,reason),state=DISABLED)
            
            gend_bb_url = itm._generate_bb_url()
            
            if itm['type'] and gend_bb_url:
                titl = "Open in Blackboard"
                
                context_menu_object.add_command(label=titl,command=(lambda: bb_tk.CONFIG.browser_open(gend_bb_url,2)))
            
            
            if itm['yt_id']:
                titl = itm['yt_title']
                
                if not titl: titl = "video"
                
                elif len(titl) > 40:
                    titl = '"{}..."'.format(titl[:40])
                
                else:
                    titl = '"{}"'.format(titl)
                titl = "Watch {} On Youtube".format(titl)
                url = 'https://youtu.be/{}'.format(itm['yt_id'])
                exiss,code,reason = bb_utilities.check_url(url,ret_type=3)
                
                if exiss:
                    context_menu_object.add_command(label=titl,command=(lambda: bb_tk.CONFIG.browser_open(url,2)))
                else:
                    context_menu_object.add_command(label="YouTube returned '{}: {}'".format(code,reason),state=DISABLED)
            
        else: #multi-select
            pass
        
        attachmntz = []
        
        for itm_id in selection:
            x = self._course_obj.get_contentitem(int(itm_id))
            if not x:
                continue
            for fnem,_,_,_ in x.attachments:
                attachmntz.append( (x,fnem) )
        
        attach_menu = Menu(context_menu_object,tearoff=0)
        
        if attachmntz:
            
            attach_menu.add_command(label="Download All",command=(lambda: self.__download_files(*attachmntz)))
            attach_menu.add_separator()
            
            for x in attachmntz:
                try:
                    nem = x[0].get_attachment(x[1])[0]
                except:
                    continue
                attach_menu.add_command(label=nem,command=(lambda: self.__download_files(x)))
            
            context_menu_object.add_cascade(label="Attachments",menu=attach_menu)
        
        else:
            context_menu_object.add_command(label="Attachments",state='disabled')
        
        
        
        context_menu_object.tk_popup(event.x_root, event.y_root)
        
        # Menu entry types
        ##################
        # Open External Link in {Browser}               [Requires ext_link]
        # Open In Blackboard                            [If type not in (document,file,link,youtube)]
        # Watch on YouTube                              [If yt_id]
        # 
        # (CASCADE \/)
        # Download All Attachments                      [Requires Attachments]
        # -------------                                 [        ...         ]
        # Download Attachment 1                         [        ...         ]
        # ......                                        [        ...         ]
        # Download Attachment N                         [        ...         ]
        
        
        
        
        
        #tree.identify_row      = returns iid of row clicked
        #                           !!only checks y-coord; x-coord could be any value
        #tree.identify_column   = physical column id (icon col="#0", first="#1", etc)
        #                           !!only checks x-coord; y-coord could be off of tree!
        #tree.identify_region   = One of:
        #                           'nothing'   not a function part of the widget
        #                           'heading'   heading
        #                           'separator' heading sep.; identify_column returns the col to the left
        #                           'tree'      the icon column or right-side space
        #                           'cell'      an actual cell (non-icon column)
        
        #"Right" Click
        #on Mac: key '<2>' and '<Control-1>'
        #else:   key '<3>'
        
        #event.type (5) = 'ButtonRelease'
        #event.type (8) = 'Leave' #mouse left the widget
        #event.x|y      == mouse's x|y coord relative to the widget
        #event.x|y_root == mouse's x|y coord relative to the screen
        
        #menu.post(event.x_root, event.y_root)
    
    def __cancel(self, event=None):
        if self.__inst_data and self.__inst_data.get('tree') and self.__inst_data.get('frame'):
            self.__inst_data['selection'] = None
            self.__exit()
        return
    
    
    def __submit(self, event=None):
        if self.__inst_data and self.__inst_data.get('tree') and self.__inst_data.get('frame'):
            selectn = list(self.__inst_data['tree'].selection())
            self.__inst_data['selection'] = selectn
            self.__exit()
            return
        raise RuntimeError, "__submit method called, but __inst_data attribute was not set."
    
    def __exit(self,event=None):
        if self.__inst_data:
            
            
            if self.__inst_data.get('frame'):
                
                try:
                    self.__inst_data['frame'].quit()
                    print "Ran __exit"
                except TclError:
                    print "__exit did not quit"
                
                return
                
            #    try:
            #        if self.__inst_data['frame'].winfo_exists():
            #            self.__inst_data['frame'].destroy()
            #    except TclError:
            #        pass
            #    del self.__inst_data['frame']
            #
            #if self.__inst_data.get('tree'):
            #    try:
            #        if self.__inst_data['tree'].winfo_exists():
            #            self.__inst_data['tree'].destroy()
            #    except TclError:
            #        pass
            #    del self.__inst_data['tree']
    
    def __generate_standalone(self):
        ###########################
        #+   0    |   1   |   2   |
        #0          tree
        #--------------------------
        #1        | Cancl |  Ok 
        
        
        zeframe = Frame(None)
        
        if self.text_cancel or self.text_submit:
            zeframe.columnconfigure(0,weight=1)
            zeframe.columnconfigure(1)
            zeframe.columnconfigure(2)
            zeframe.rowconfigure(0,weight=1)
            zeframe.rowconfigure(1)
        else:
            zeframe.columnconfigure(0,weight=1)
            zeframe.columnconfigure(1)
            zeframe.columnconfigure(2)
            zeframe.rowconfigure(0,weight=1)
        
        self.__inst_data['frame'] = weakref.proxy(zeframe)
        
        zetree = Treeview(zeframe, columns=self.columns, displaycolumns=\
                     self.visible_columns, selectmode=self.selectmode, \
                     show='tree headings')
        cancel = None
        submit = None
        
        zetree.grid(row=0,column=0,columnspan=3,sticky='nesw')
        if self.text_cancel:
            cancel = Button(zeframe,text=self.text_cancel,command=self.__cancel)
            cancel.grid(row=1,column=1,sticky='nesw')
        if self.text_submit:
            submit = Button(zeframe,text="Submit",command=self.__submit)
            submit.grid(row=1,column=2,sticky='nesw')
        
        self.__inst_data['tree'] = weakref.proxy(zetree)
        
        for col in self.visible_columns:
            zetree.heading(col,text=col)
        
        
        zeframe.winfo_toplevel().title(self.w_title)
        zeframe.winfo_toplevel().rowconfigure(0,weight=1)
        zeframe.winfo_toplevel().columnconfigure(0,weight=1)
        
        for item_iid in self._content.keys():
            self.__tree_adder(item_iid)
        
        zeframe.grid(column=0,row=0,sticky='nesw')
        
        for keybnd in bb_tk.CONFIG.getopt('rightclick'):
            zetree.bind(keybnd,self.__context_menu)
        
        isset = bb_tk.STYLE.app_icon_setter(zeframe)
        print "Set icon? {}".format(isset)
        
        print "Tree Master: {}".format(self.__inst_data['tree'].master)
        print "Frame Master: {}".format(self.__inst_data['frame'].master)
        
        zeframe.winfo_toplevel().protocol("WM_DELETE_WINDOW", self.__exit)
        zeframe.winfo_toplevel().deiconify()
        zeframe.mainloop()
        
        selection = None
        if 'selection' in self.__inst_data:
            selection = self.__inst_data['selection']
            del self.__inst_data['selection']
        
        bb_tk.check_tk()
        
        return selection
    
    def __tree_adder(self,iid):
        
        tree = self.__inst_data.get('tree')
        
        if not tree:
            raise TreeError, "A tree insertion was attempted, but the tree is dereferenced."
        
        parnt,item = self._content.get(iid,(None,None))
        
        if item is None:
            #item is not in _contents, so return None
            return None
        
        if tree.exists(str(iid)):
            #item is already in the tree
            return True
        
        img = bb_tk.STYLE.get_icon(item[self._idx_of_type])
        typ = item[self._idx_of_type] or ''
        if parnt is None or parnt == '':
            #this is a root node!
            tree.insert('','end',iid,values=item, image=img, text=typ)
        
        else:
            #not a root node
            
            if tree.exists(str(parnt)):
                #parent node already inserted
                pass
            
            elif parnt in self._content:
                #parent not in tree, but is in _content
                ret = self.__tree_adder(parnt)
                
                if not ret:
                    return ret
            else:
                raise TreeError, "Failed to insert tree node; parent not in _content"
            tree.insert(str(parnt), 'end', iid, values=item, image=img, text=typ)
            
            return True
    
    def __generate_embedded(self):
        pass

    
    
    def emergency_destroy(self):
        tree = self.__inst_data.get('tree')
        frem = self.__inst_data.get('frame')
        if tree is not None:
            tree_class = "ShabbITTYbiPBOOP"
            try:
                tree_class = NotImplemented if not hasattr(tree,'__class__') else tree.__class__
            except:
                print "Failed to get '__class__' attribute from tree weakref."
            
            if tree_class != "ShabbITTYbiPBOOP" and 'tree' in self.__inst_data:
                if tree_class is NotImplemented or tree_class == NotImplemented:
                    print "Tree weakref does not have a '__class__' attribute."
                else:
                    print "Type of tree weakref is {!r}".format(tree_class.__name__)
                    try:
                        print "Attempting to destroy tree..."
                        tree.destroy()
                        print "It... worked??"
                    except Exception as e:
                        print "Failed. Raised a {} exception.".format(e.__class__.__name__)
            
            print "Deleting tree weakref from inst data..."
            del self.__inst_data['tree']
        else:
            print "Tree not in inst data :)"
        
        if frem is not None:
            try:
                frem.destroy()
            except:
                pass
            try:
                del self.__inst_data['frame']
            except:
                pass
        
        
