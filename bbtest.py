#!/usr/bin/env python


class bb(object):
    def __init__(self,*args,**kwargs):
        object.__init__(self)
        
        self._bb_args = args
        self._bb_kwargs = kwargs
        self.__blkbrd = None
        self.Blackboard = None
        
        self.reload()
    
    def reload(self):
        
        try:
            self.Blackboard.logout()
        except:
            pass
        
        if self.__blkbrd:
            
            try:
                
                del self.Blackboard
                
                self.__blkbrd = reload(self.__blkbrd)
            
            except Exception as E:
                self.__blkbrd = self.Blackboard = None
                print "An Exception was raised during reload of 'blackbird':\n{}".format(E)
                return
        else:
            self.__blkbrd = __import__('blackbird')
        
        
        try:
            self.Blackboard = self.__blkbrd.Blackboard(*self._bb_args,**self._bb_kwargs)
        except Exception as E:
            print "An Exception was raised while instantiating a Blackboard instance:\n{}".format(E)
            return
        
        x = self.Blackboard.login()
        print "[[ {} ]]".format(x)
    
    def __getattr__(self,attr):
        if attr in dir(self.Blackboard):
            print "#Found {!r} attr in Blackboard".format(attr)
            return self.Blackboard.__getattribute__(attr)
        raise AttributeError, "Neither bb objects nor Blackboard objects have a {!r} attribute".format(attr)
    
