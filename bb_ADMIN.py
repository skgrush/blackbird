#!/usr/bin/env python

from bbconsts import *
import urllib,re
import weakref

_webapps_re = re.compile(r'^\s*/webapps')

class tool(object):
    
    __slots__ = ('add','__getattr__')
    
    def __new__(cls,parent="Required"):
        self = super(tool, cls).__new__(cls)
        
        if isinstance(parent,basestring):
            raise TypeError, "tool class constructor requires its new parent Blackboard instance as an argument"
        if parent.__class__.__name__ != 'Blackboard':
            raise TypeError, "parent argument must be a Blackboard instance"
        
        bb_parent = parent
        
        
        tool_dict = {}
        
        def add(clazz):
            if type(clazz) is not bb_tool:
                raise TypeError, "Can only add bb_tool classes."
            if clazz.__name__ in tool_dict:
                return False
            tool_dict[clazz.__name__] = clazz(bb_parent)
            return True
        self.add = add
        
        def _getattr(attr):
            if attr not in tool_dict:
                raise AttributeError, "Failed to find tool {!r}".format(attr)
            return tool_dict[attr]
        self.__getattr__ = _getattr
        
        return self

class bb_tool(type):
    def __new__(cls,name,bases, dct):
        #print "### bb_tool type called; __new__({},{},{},{})".format(cls,name,bases,dct)
        return type.__new__(cls,name,bases,dct)

class course_browser(object):
    __metaclass__ = bb_tool
    
    __slots__ = ('_parent','get_catalog')
    
    def __new__(cls,parent):
        self = super(course_browser, cls).__new__(cls)
        
        self._parent = parent
        
        linst = parent._Blackboard__LOGIN_INST
        base_url = linst.url_gen('domain','webapps')+'/blackboard/execute/viewCatalog'
        opnr = linst.open
        base_args = {'searchOperator':'NotBlank','command':'SavedSearch','sortCol':'identifier','type':'Course','sortDir':'ASCENDING','searchField':'CourseId','numResults':1000}
        
        
        attributes = {'run_before':False,'catalog_format':(),'catalog':[]}
        
        def _parse_page(soup):
            
            tmp_catalog = []
            
            databody = soup.find(id='listContainer_databody')
            if not databody:
                return None,None
            header = databody.find_previous_sibling('thead')
            if header:
                th_list = []
                for th in header.find_all('th'):
                    a_ent = th.find('a')
                    if a_ent:
                        th_list.append(a_ent.get_text(strip=True))
                    else:
                        th_list.append(th.get_text(strip=True))
                if th_list:
                    th_list.insert(0,'id')
                    attributes['catalog_format'] = tuple(th_list)
            
            tr_row =databody.find('tr',recursive=False)
            
            while tr_row:
                row_id = None
                row_parts = []
                for part in tr_row.find_all(['th','td'],recursive=False):
                    if part.name == 'th':
                        lnk = part.find('a',href=_webapps_re)
                        if lnk:
                            href = lnk.get('href')
                            if href and 'course_id' in href:
                                if 'course_id%3d_' in href.lower():
                                    row_id = href.lower().rsplit('course_id%3d_',1)[1]
                                else:
                                    row_id = href.lower().rsplit('course_id=_',1)[1]
                                row_id = row_id.split('_1')[0]
                                if row_id.isdigit():
                                    row_id = int(row_id)
                        row_parts.append(part.stripped_strings.next() or None)
                    else:
                        row_parts.append(part.get_text(strip=True) or None)
                row_parts.insert(0,row_id)
                tmp_catalog.append(tuple(row_parts))
                
                tr_row = tr_row.find_next_sibling('tr')
                if not tr_row:
                    print "@@@@@@Found end?"
            
            itemct_tuple = (None,None,None)
            
            itemcount = soup.find(id='listContainer_itemcount')
            if itemcount:
                print "@@@@@@Found itemcount"
                cts = itemcount.find_all('strong')
                itemct_list = [None,None,None]
                if len(cts) >= 2:
                    itemct_list[0] = cts[0].get_text(strip=True)
                    itemct_list[1] = cts[1].get_text(strip=True)
                    try:
                        itemct_list[0] = int(itemct_list[0])
                        itemct_list[1] = int(itemct_list[1])
                    except:
                        pass
                if len(cts) >= 3:
                    itemct_list[2] = cts[2].get_text(strip=True)
                    try:
                        itemct_list[2] = int(itemct_list[2])
                    except:
                        pass
                itemct_tuple = tuple(itemct_list)
                
            return (itemct_tuple,tmp_catalog)
        
        def _get_catalog():
            if attributes['run_before'] and attributes['catalog']:
                return (attributes['catalog_format'],attributes['catalog'])
            base_args['startIndex'] = 0
            url = base_url+'?'+urllib.urlencode(base_args)
            bb_page = opnr(url,parser='html.parser')
            if not bb_page or bb_page is NOT_LOGGED_IN:
                x = self._parent.login()
                if not x or x is NOT_LOGGED_IN:
                    return NOT_LOGGED_IN
                bb_page = opnr(url,parser='html.parser')
            
            itmct,catlg = _parse_page(bb_page.soup)
            if not (itmct and catlg):
                return False
            
            if itmct[0] is not None and itmct[1] and itmct[2] and ( 0 <itmct[0] < itmct[1] < itmct[2]):
                print "@@@@@@ Getting next catalog page; itmct={}".format(itmct)
                base_args['startIndex'] = 1000
                url = base_url+'?'+urllib.urlencode(base_args)
                print "@@@@@@ New URL:  {!r}".format(url)
                bb_page = opnr(url,parser='html.parser')
                if not bb_page or bb_page is NOT_LOGGED_IN:
                    return NOT_LOGGED_IN
                
                itmct2,catlg2 = _parse_page(bb_page.soup)
                if itmct2[0] and itmct2[1] and itmct2[2] and (itmct[1] < itmct2[0]):
                    print "@@@@@@ Extending catalog!"
                    catlg.extend(catlg2)
                    print "@@@@@@ Catalog extended."
                else:
                    print "@@@@@@ NOT extending catalog. itmct2={}".format(itmct2)
            else:
                print "@@@@@@ NOT getting next catalog page; itmct={}".format(itmct)
            
            attributes['run_before'] = True
            attributes['catalog'] = catlg
            return (attributes['catalog_format'],attributes['catalog'])
        
        self.get_catalog = _get_catalog
        
        return self
    
    @property
    def parent(i):
        return i._parent
    
    def tocsv(s,flpath):
        x = s.get_catalog()
        if not x:
            return x
        fmt,catlog = x
        with open(flpath,'w+') as ofl:
            ofl.write('\t'.join(fmt).encode('utf8')+'\n')
            for tuble in catlog:
                ofl.write('\t'.join(map(unicode,tuble)).encode('utf8')+'\n')
        return True
    

