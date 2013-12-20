# -*- coding: utf-8 -*-


import xml.sax.saxutils as sax

class SOSException(ValueError):
  exceptionreport = '''<?xml version="1.0" encoding="UTF-8" standalone="no"?><ExceptionReport xmlns="http://www.opengis.net/ows/1.1" xmlns:xsi="http://www.w3.org/2001/XMLSchema-instance" xsi:schemaLocation="http://www.opengis.net/ows/1.1 ../owsExceptionReport.xsd" version="1.0.0" xml:lang="en">
%s  
</ExceptionReport>'''
  exceptionLoc = ''' <Exception locator="%s" exceptionCode="%s">
%s  
 </Exception>'''
  exception = ''' <Exception exceptionCode="%s">
%s  
 </Exception>'''
  exceptiontext = '''  <ExceptionText>
    %s
  </ExceptionText>'''

  def __init__(self, code, locator, msg, othermsgs = []):
    self.code = code
    self.locator = locator
    self.msg = sax.escape(str(msg))
    self.children = []
    for msg in othermsgs:
#        self.children.append(sax.escape(msg))
        self.children.append(msg)
  
  def __str__(self):
    return self.ToXML()

  def __repr__(self):
    return self.ToXML()
  
  def AddText(self, text):
    self.children.append(text)

  def ToXML(self):
    exchildren = [self.exceptiontext % (c,) for c in self.children]
    extextlist = [self.exceptiontext % (self.msg,)] + exchildren
    extext = "\n".join(extextlist)
    if not self.locator==None:
        body = self.exceptionLoc % (self.locator,self.code, extext)
    else:
        body = self.exception % (self.code, extext)
    return self.exceptionreport % (body,)
