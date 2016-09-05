#!/usr/bin/env python

import httplib,urlparse

def check_url(url_arg,follow=5,ret_type=0):
    """Check the status of a page via URL 
    
    'follow' argument should be an integer representing the number of
        redirects to follow before returning.
    'ret_type' is a bit-map. Values below should be bitwise-OR'd:
            0   return True if the url returns a 2xx response; else False
            1   return a boolean and the status code of the page.
            2   return a boolean and the status message from the page.
            4   return a boolean and the HTTPResponse from the page.
        -
        If ret_type is greater than zero, it will be a tuple of the
        bitmapped values passed.
    """
    if follow is True:
        follow = 5
    url_arg = url_arg.strip()
    if not urlparse.urlparse(url_arg).scheme:
        url_arg = 'http://{}'.format(url_arg)
    parse = urlparse.urlparse(url_arg)
    scheme = parse.scheme
    netloc = parse.netloc
    fpath = parse.path
    if parse.query:
        fpath += "?{}".format(parse.query)
    if parse.fragment:
        fpath += "#{}".format(parse.fragment)
    
    conn = None
    if scheme == 'https':
        conn = httplib.HTTPSConnection(netloc)
    else:
        conn = httplib.HTTPConnection(netloc)
    conn.request('HEAD', fpath)
    response = conn.getresponse()
    conn.close()
    
    if follow > 0 and response.status in (301,302,303,307):
        try:
            follow = int(follow)
        except: 
            raise TypeError, "Non-integer argument passed to parameter 'follow'"
        newloc = response.getheader('location')
        if newloc:
            return check_url(newloc,follow-1,ret_type)
        return False
    
    if ret_type:
        ret = [response.status==200]
        if ret_type&1:
            ret.append(response.status)
        if ret_type&2:
            ret.append(response.reason)
        if ret_type&4:
            ret.append(response)
        return tuple(ret)
    else:
        return response.status==200

url_exists = check_url
