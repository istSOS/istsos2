# -*- coding: utf-8 -*-


import xml.sax.saxutils as sax

class SOSException(ValueError):
  exceptionreport = '''<?xml version="1.0" encoding="UTF-8" standalone="no"?><ExceptionReport xmlns:xsi="http://www.w3.org/2001/XMLSchema-instance" xsi:schemaLocation="http://schemas.opengis.net/ows/1.0.0/owsExceptionReport.xsd" version="1.0.0" language="en">
%s  
</ExceptionReport>'''
  exception = ''' <Exception locator="service" exceptionCode="%s">
%s  
 </Exception>'''
  exceptiontext = '''  <ExceptionText>
    %s
  </ExceptionText>'''

  def __init__(self, code, msg, othermsgs = []):
    self.code = code
    self.msg = sax.escape(str(msg))
    self.children = []
    for msg in othermsgs:
        self.children.append(sax.escape(msg))
  
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
    body = self.exception % (self.code, extext)
    return self.exceptionreport % (body,)
