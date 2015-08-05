# -*- coding: utf-8 -*-
# ===============================================================================
#
# Authors: Massimiliano Cannata, Milan Antonovic
#
# Copyright (c) 2015 IST-SUPSI (www.supsi.ch/ist)
#
# This program is free software; you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation; either version 2 of the License, or (at your option)
# any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program; if not, write to the Free Software
# Foundation, Inc., 51 Franklin Street, Fifth Floor, Boston, MA  02110-1301  USA
#
# ===============================================================================
import xml.sax.saxutils as sax

class SOSException(ValueError):
  """SOS Exception class

  Attributes:
    code (int): the error code
    locator (str): the locator identifing where error occurred
    msg (str): the error message
    children (list): the children errors

  """

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
        self.children.append(msg)
  
  def __str__(self):
    """convert to XML string"""
    return self.ToXML()

  def __repr__(self):
    """convert to XML string"""
    return self.ToXML()
  
  def AddText(self, text):
    """append child error text"""
    self.children.append(text)

  def ToXML(self):
    """render as XML"""
    exchildren = [self.exceptiontext % (c,) for c in self.children]
    extextlist = [self.exceptiontext % (self.msg,)] + exchildren
    extext = "\n".join(extextlist)
    if not self.locator==None:
        body = self.exceptionLoc % (self.locator,self.code, extext)
    else:
        body = self.exception % (self.code, extext)
    return self.exceptionreport % (body,)
