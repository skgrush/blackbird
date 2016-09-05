#!/usr/bin/env python

import os,subprocess

_desktop_env = os.environ.get('XDG_CURRENT_DESKTOP','')
#os.environ key                 desktop
#======================================
#KDE_FULL_SESSION               kde
#GNOME_DESKTOP_SESSION_ID       gnome
#DE  == ...                     gnome | kde | xfce | lxde
#XDG_CURRENT_DESKTOP == ...     KDE | GNOME | Unity
#DESKTOP_SESSION == 'default'   [CHECK ELSEWHERE]
#                   ...         
#                   (a)-(b)     (a)


_theme_name = ''
_icon_theme_name = ''
_primary_font = () #if set, (font_name, font_size|None)
_menu_icons_on = None
_button_icons_on = None

try:
    import gconf
except:
    gconf = None

def _update_theme_info(): #requires pygtk module; 
    
    
    ###
    ###Check for theme-name update
    ###
    
    #gtk.widget_class_list_style_properties
    dot_gtkrc = '~/.gtkrc-{}.0{}'
    flz = [('2',''),('2','-kde4'),('3',''),('3','-kde4')]
    
    for i in range(len(flz)):
        fl = os.path.expanduser( dot_gtkrc.format( *flz[i] ) )
        if os.path.exists( fl ):
            copy=False
            for j in range(i):
                if flz[j] and os.path.samefile(fl, flz[j]):
                    copy=True
                    break
            if not copy:
                flz[i] = fl
                continue
        flz[i] = None
    
    
    
    if gconf:
        _client = gconf.client_get_default()
        
        _theme_name = _client.get_string('/desktop/gnome/interface/gtk_theme') or ''
        _icon_theme_name = _client.get_string('/desktop/gnome/interface/icon_theme') or ''
        
        tmp = _client.get_string('/desktop/gnome/interface/font_name')
        if tmp:
            if tmp.rsplit(None,1)[-1].isdigit():
                tmp = tmp.rsplit(None,1)
                    _primary_font = tmp[0] , int(tmp[1])
            else:
                _primary_font = tmp.strip() , None
        
        tmp = _client.get_bool('/desktop/gnome/interface/buttons_have_icons')
        if tmp is not None:
            _button_icons_on = tmp
        tmp = _client.get_bool('/desktop/gnome/interface/menus_have_icons')
        if tmp is not None:
            _menu_icons_on = tmp
        
        del tmp
        
# import gtk
# styleO = gtk.widget_get_default_style()
# styleO. #TODO

# gtk.widget_class_find_style_property( gtk.%widget% , %property_name% )
