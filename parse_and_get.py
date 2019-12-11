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

from io import StringIO, BytesIO
from os import path
from lxml import etree as et

def parse_and_get_ns(source):
    events = "start", "start-ns"
    root = None
    ns = {}
    
    if isinstance(source, bytes):
        if not isinstance(source, BytesIO) and path.isfile(source):
            file_parsed = open(source, 'rb')
        elif not hasattr(source, 'read'):
            file_parsed = BytesIO(source)
        else:
            file_parsed = source
            
    else:
        if not isinstance(source, StringIO) and path.isfile(source):
            file_parsed = open(source, 'rb')
        elif not hasattr(source, 'read'):
            file_parsed = StringIO(source)
        else:
            file_parsed = source

    for event, elem in et.iterparse(file_parsed, events):
        if event == "start-ns":
            if elem[0] in ns and ns[elem[0]] != elem[1]:
                # NOTE: It is perfectly valid to have the same prefix refer
                #   to different URI namespaces in different parts of the
                #   document. This exception serves as a reminder that this
                #   solution is not robust.  Use at your own peril.
                raise KeyError("Duplicate prefix with different URI found.")
            ns[elem[0]] = "%s" % elem[1]
        elif event == "start":
            if root is None:
                root = elem
    return et.ElementTree(root), ns
