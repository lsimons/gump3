def bust_cache(req):
    req.headers_out['Cache-Control'] = 'no-cache'
    req.headers_out['Pragma'] = 'no-cache'
    req.headers_out['Expires'] = '-1'
