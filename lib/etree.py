# -*- coding: utf-8 -*-

try:
  from lxml import et
  lib = "lxml"
except ImportError:
  try:
    # Python 2.5
    import xml.etree.cElementTree as et
    lib = "xml.etree.cElementTree"
  except ImportError:
    try:
      # Python 2.5
      import xml.etree.ElementTree as et
      lib = "xml.etree.ElementTree"
    except ImportError:
      try:
        # normal cElementTree install
        import cElementTree as et
        lib = "cElementTree"
      except ImportError:
        try:
          # normal ElementTree install
          import elementtree.ElementTree as et
          lib = "ElementTree"
        except ImportError:
          print >> sys.stderr, ("Failed to import ElementTree from any known place")
          