import argparse, os, re
from Queue import Queue
from libraries.extjs41.parse_class import ExtClassParser
EXT_CREATE_TOKEN = 'Ext.create\((.*?)\)'

class ExtBuilder:
  def __init__(self, js_project_path, ext_path):
    self.js_project_path = js_project_path
    self.ext_path = ext_path
     
   
  def build(self):
    ext_hierarchy = self.__create_ext_class_hierarchy()
    
    modules_used = self.__extract_used_modules()
    already_processed = set()
    
    q = Queue()
    for module in modules_used:
      q.put(module)
      
      
    while not q.empty():
      module = q.get()
      
      parser = ExtClassParser(self.ext_path, module)
      already_processed.add(module)
      
      dependencies = parser.get_requires()
      parent = parser.get_extends()
      if parent and (parent not in already_processed):
        q.put(parser.get_extends())
        
      for dependency in dependencies:
        if dependency not in already_processed:
          q.put(dependency)
          
    return already_processed
      
  def __create_ext_class_hierarchy(self):
    for (dirpath, dirnames, filenames) in os.walk(self.ext_path):
        for filename in filenames:
          ext_class_file = '%s/%s' % (dirpath, filename)
          
          #with open(ext_class_file, 'r') as f:
           #   contents = f.read();
          p = ExtClassParser(self.ext_path, ext_class_file)
          
          
          
              #matches =  re.search(EXT_CREATE_TOKEN,contents,re.DOTALL)
#              if matches:
 #               for match in matches.groups():
                    # at this point match contains XXX in Ext.create(XXX)
  #                  ext_component_quoted = match.split(',')[0].strip()
                    # add, getting rid of quotes
   #                 ext_components.add(ext_component_quoted[1:-1])

    print 'FINISHED PARSING EXTJS SOURCE'
    return ext_components
    
    
  def __extract_used_modules(self):
    ext_components = set()
    for (dirpath, dirnames, filenames) in os.walk(self.js_project_path):
        for filename in filenames:
          jsfile = '%s/%s' % (dirpath, filename)
          
          with open(jsfile, 'r') as f:
              contents = f.read();
              matches =  re.search(EXT_CREATE_TOKEN,contents,re.DOTALL)
              if matches:
                for match in matches.groups():
                    # at this point match contains XXX in Ext.create(XXX)
                    ext_component_quoted = match.split(',')[0].strip()
                    # add, getting rid of quotes
                    ext_components.add(ext_component_quoted[1:-1])

    return ext_components
         
   
   


if __name__ == "__main__":
    arg_parser = argparse.ArgumentParser(description='jslib custom builder')
    arg_parser.add_argument('-sourcedir', help='Path to the directory containing the JS files', action='store',
                            dest='source_dir', required=True)
    arg_parser.add_argument('-extdir', help='Path to the ExtJS distribution folder', action='store',
                            dest='ext_dir', required=True)
    params = vars(arg_parser.parse_args())
    
    ext_builder = ExtBuilder(params['source_dir'], params['ext_dir'])
    print ext_builder.build()
    
    
