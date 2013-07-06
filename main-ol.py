#!/usr/bin/python
# -*- coding: utf-8 -*-
import argparse, os, re

OPENLAYERS_TOKEN = 'OpenLayers\\.([\\w\\.]+)'

def process(path, buildconfigfile = 'openlayers-custom.cfg'):
   ol_classes = set()
   for (dirpath, dirnames, filenames) in os.walk(path):
      for filename in filenames:
         jsfile = '%s/%s' % (dirpath, filename)
         
         with open(jsfile, 'r') as f:
            contents = f.read();
            matches =  re.findall(OPENLAYERS_TOKEN,contents,re.DOTALL)
            for match in matches:
               p = re.compile('\\.[a-z]')
               
               classname = match
               endindex = None
               for f in p.finditer(match):
                  endindex = f.start()
                  classname = match[0:endindex]
                  break
               
               ol_classes.add('OpenLayers.%s' % classname)
               
   # OpenLayers expects renderers to be there, even if it's not an explicit dependency            
   ol_classes.add('OpenLayers.Renderer.SVG')
   ol_classes.add('OpenLayers.Renderer.VML')
   ol_classes.add('OpenLayers.Renderer.Canvas')

   
   with open(buildconfigfile, 'w') as f:
      f.write('[first]\n')
      f.write('[last]\n')
      f.write('[include]\n')
      
      for classname in ol_classes:
         f.write('%s.js\n' % classname.replace('.', '/'))
      f.write('[exclude]\n')
      print 'Wrote %s file with %i entries.' % (buildconfigfile, len(ol_classes))
   
      
   

if __name__ == "__main__":
    arg_parser = argparse.ArgumentParser(description='jslib custom builder')
    arg_parser.add_argument('-sourcedir', help='Path to the directory containing the JS files', action='store',
                            dest='sourcedir', required=True)
    params = vars(arg_parser.parse_args())
    process(params['sourcedir'])
    
