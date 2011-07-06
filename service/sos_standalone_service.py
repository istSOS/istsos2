import sos
from wsgiref.util import setup_testing_defaults
from wsgiref.simple_server import make_server

httpd = make_server('', 8099, sos.application)
print ""
print "========================WARNING=========================="
print " THIS IS A DEVELOPEMENT TEST SERVICE, FOR PRODCUTION"
print " ENVIRONMENT YOU ARE SUGGESTED TO USE APACHE and mod_wsgi"
print " OPPORTUZNELY CONFIGURED..."
print "========================================================="
print ""
print "SOS service is now available at http://localhost:8099..."
httpd.serve_forever()
