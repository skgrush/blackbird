#!/usr/bin/env python


class BLACKBOARD_CONSTANT(object):
    
    __slots__ = ('valyu','boolean','locked')
    
    def __init__(self,value,boolee=True):
        object.__init__(self)
        privates = {'value': value,'boolean':bool(boolee)}
        #value = value
        #boolean = bool(boolean)
        #self.locked=True
        
        def valyu():
            return privates['value']
        self.valyu = valyu
        
        def boolean():
            return privates['boolean']
        self.boolean = boolean
        
        self.locked = 1
    
    def __str__(self):
        return self.valyu()
    def __repr__(self):
        return self.valyu()
    def __hash__(self):
        return hash(self.valyu())
    def __eq__(self,other):
        if type(other) is BLACKBOARD_CONSTANT:
            return self.__hash__() == hash(other.valyu())
        else:
            return self.valyu()==other
    def __ne__(self,other):
        return not self.__eq__(other)
    def __nonzero__(self):
        return self.boolean()
    def __setattr__(self,name,value):
        try:
            _ = self.locked
        except AttributeError:
            object.__setattr__(self,name,value)
            return
        raise AttributeError("Cannot change constant")
    
    def __delattr__(self,name):
        raise AttributeError("Cannot delete constant attributes")
    

NOT_LOGGED_IN=BLACKBOARD_CONSTANT("NOT_LOGGED_IN",False)
NA=BLACKBOARD_CONSTANT("N/A")

__all__ = ['NOT_LOGGED_IN','NA']
