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
from lxml import etree as et


def getElemTxt(node):
    """Return the text value of an XML node

    Args:
        node: the etree node element

    Returns:
        The string of the node value

    Raises:
        Exception: node has no child node or is not of type TEXT
    """
    if node.hasChildNodes():
        val = node.firstChild
        if val.nodeType == val.TEXT_NODE:
            return str(val.data)
        else:
            err_txt = "get node text value: \"%s\" is not of type TEXT" %(node.nodeName)
            raise Exception(err_txt)
    else:
            err_txt = "get node text value: \"%s\" has no child node" %(node.nodeName)
            raise Exception(err_txt)

def getElemAtt(node,att):
    """Return the attribute of an XML node element

    Args:
        node: the etree node element
        att: the attribute name

    Returns:
        The string of the attribute value

    Raises:
        Exception: node has not attribute
    """
    if att in list(node.attributes.keys()):
        return str(node.getAttribute(att))
    else:
        err_txt = "get node attribute value: \"%s\"has no \"%s\" attribute" %(node.nodeName,att)
        raise Exception(err_txt)

def get_name_from_urn(stringa,urnName,sosConfig):
    """Validate the URN and extract the name (last elment)

    Args:
        stringa: URN type
        urnName: URN
        sosConfig: istSOS configuration object

    Returns:
        The name of the URN element

    Raises:
        Exception: Urn is not valid

    """
    a = stringa.split(":")
    name = a[-1]
    urn = sosConfig.urn[urnName].split(":")
    if len(a)>1:
        for index in range(len(urn)-1):
            if urn[index]==a[index]:
                pass
            else:
                raise Exception(1,"Urn \"%s\" is not valid: %s."%(a,urn))
    return name


