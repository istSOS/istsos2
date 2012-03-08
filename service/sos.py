
"""
class bufferProxy:
    # Adapted from
    # http://www.modpython.org/pipermail/mod_python/2004-November/016841.html
    # allows clearing output in case of error
    def __init__(self,outputBuffer):
        self.outputBuffer = outputBuffer
    def write(self,data,flush=None):
        self.outputBuffer.write(data)
        status = '200 OK'
        # prepare response header
        response_headers = [('Content-Type', content_type),
                            ('Content-Length', str(len(method)))]
        # send response header
        start_response(status, response_headers)   
"""        
def application(environ, start_response):
    import sys
    from os import path

    #from mod_python import util, apache, psp
    import urllib
    import cStringIO
    import traceback
    import decimal

    outputBuffer = cStringIO.StringIO()
    root_path = path.abspath(path.dirname(__file__))
    sys.path.append(root_path)
    import sosConfig
    
    if not sosConfig.istSOS_librarypath=="" or sosCOnfig.istSOS_librarypath==None:
        sys.path.insert(0, sosConfig.istSOS_librarypath)
    import istSOS
    from istSOS import sosDatabase
    from istSOS import sosException

    from cgi import parse_qs, escape
    
    
    
    # Always escape user input to avoid script injection
    # age = escape(parse_qs(environ['QUERY_STRING'])['age'])
    """
    #===============================
    # READ REQUEST
    #===============================
    # read the request method
    method = str(environ['REQUEST_METHOD']).upper()
        
    if method=="GET":
        # Returns a dictionary containing lists as values.
        request = parse_qs(environ['QUERY_STRING'])
        
    if method=="POST":
        # the environment variable CONTENT_LENGTH may be empty or missing
        try:
            request_body_size = int(environ.get('CONTENT_LENGTH', 0))
        except (ValueError):
            request_body_size = 0

        # get the request
        request = environ['wsgi.input'].read(request_body_size)
    """
    try:
        #===============================
        # CALL ISTSOS AND PRODUCE RESPONSE
        #===============================
        # call istSOS to manage the request and generate the response
        pgdb = sosDatabase.sosPgDB(sosConfig.connection["user"],
                           sosConfig.connection["password"],
                           sosConfig.connection["dbname"],
                           sosConfig.connection["host"],
                           sosConfig.connection["port"])
        
        from istSOS.filters import factory_filters as FF
        from istSOS.responders import factory_response as FR
        from istSOS.renderers import factory_render as FRe
        
        req_filter = FF.sosFactoryFilter(environ)
        response = FR.sosFactoryResponse(req_filter,pgdb)
        render = FRe.sosFactoryRender(response)
        try:
	        content_type = req_filter.responseFormat
        except:
            content_type = 'application/xml; charset=utf-8'

        #===============================
        # SEND RESPONSE
        #===============================
        # HTTP response code and message
        status = '200 OK'
        # prepare response header
        response_headers = [('Content-Type', content_type),
                            ('Content-Length', str(len(render)))]
        # send response header
        start_response(status, response_headers)
        #send response body
        return [render]
        """
        except Exception as e:        
            #===============================
            # SEND RESPONSE
            #===============================
            # HTTP response code and message
            status = '200 OK'
            # prepare response header
            response_headers = [('Content-Type', 'application/xml'),
                                ('Content-Length', str(len(e)))]
            # send response header
            start_response(status, response_headers)
            #send response body
            return [e]
        """
            

    except sosException.SOSException, e:
        response_body = e.ToXML()
        # HTTP response code and message
        status = '200 OK'
        # prepare response header
        response_headers = [('Content-Type', 'application/xml; charset=utf-8'),
                            ('Content-Length', str(len(response_body)))]
        # send response header
        start_response(status, response_headers)
        # send response
        return [response_body.encode('utf-8')]
    
    except Exception, e:
        othertext = traceback.format_exception(*sys.exc_info())        
        response_body = "%s" % (sosException.SOSException(e.__class__.__name__, e, othertext),)
        # HTTP response code and message
        status = '200 OK'
        # prepare response header
        response_headers = [('Content-Type', 'application/xml; charset=utf-8'),
                            ('Content-Length', str(len(response_body)))]
        # send response header
        start_response(status, response_headers)
        # send response
        return [response_body.encode('utf-8')]
        
    return
    
