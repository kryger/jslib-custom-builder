import os, re, sys
from parse_class import ExtClassParser
from Queue import Queue

EXT_CREATE_TOKEN = r'Ext.create\s*\((.*?)\)'
EXT_XTYPE_TOKEN = r"xtype\s*:\s*'(.*?)'"
EXT_DEFAULT_TYPE_TOKEN = r"defaultType\s*:\s*'(.*?)'"
EXT_LAYOUT_TOKEN = r"layout\s*:\s*'(.*?)'"
EXT_PROXY_TOKEN = r'proxy\s*:\s*\{(.*?)\}'
EXT_FIELDS_TOKEN = r'fields\s*:\s*\[(.*?)\]'
EXT_TYPE_TOKEN = r"type\s*:\s*'(.*?)'"

class ExtBuilder:
  EXT_DEFINE_TEMPLATE = 'Ext.define('
  
  def __init__(self, js_project_path, ext_path, in_build_file):
    self.js_project_path = js_project_path
    self.ext_path = ext_path
    self.ext_hierarchy = self.__create_ext_class_hierarchy()
    self.in_build_file = in_build_file
  
  def get_unused_classes(self, need_these):
    used_classes = self.__get_used_classes(need_these)
    # print type(used_classes)
    print 'used=', used_classes
    embedded_classes = self.__get_embedded_classes()
    print '\nembedded=', embedded_classes
    return embedded_classes - used_classes
  
  def __get_embedded_classes(self):
    double_or_single_quote = re.compile(r'\'|\"')
    embedded_classes = set()
    for line in open('%s/%s.js' % (self.ext_path, self.in_build_file)).readlines():
      if line.startswith(self.EXT_DEFINE_TEMPLATE):
        
        class_name = double_or_single_quote.split(line)[1]
        embedded_classes.add(class_name)
      
    return embedded_classes
  
  def test(self, name):
    return self.__get_canonical_name(name)
  
  def __get_canonical_name(self, component_name):
    for component in self.ext_hierarchy:
      if (component_name == component['class_name']) or component_name in component['alt_class_names'] or component_name in component['xtypes']:
        return component['class_name']
      
    return component_name
  
  def __get_used_classes(self, need_these):
    modules_used = self.__extract_used_modules()
    # exit()
    already_processed = set()
    
    modules_used_normalised = set()
    
    for module in modules_used:
      modules_used_normalised.add(self.__get_canonical_name(module))
    
    q = Queue()
    for module in modules_used_normalised:
      # print 'adding to q', module
      q.put(module)
      
    for module in need_these:
      # print 'Forced requirement for', module
      q.put(self.__get_canonical_name(module))
    # print '\n\n'
      
    
    while not q.empty():
      module = q.get()
      # print 'processing module=', module
      
      # parser = ExtClassParser(self.ext_path, module)
      already_processed.add(module)
      # print 'module required=', module
      
      data = self.__get_from_hier(module)

      if not data:
         continue
       
      parent = self.__get_canonical_name(data['parent'])
      dependencies = data['requires']
      mixins = data['mixins']
      uses = data['uses']

      if parent and (parent not in already_processed):
        q.put(parent)
        
      for dependency in dependencies:
        dependency_canon = self.__get_canonical_name(dependency)
        if dependency_canon not in already_processed:
          # print 'adding %s as a dependency of %s' % (dependency_canon, data['class_name'])
          q.put(dependency_canon)
          
      for mixin in mixins:
        mixin_canon = self.__get_canonical_name(mixin)
        if mixin_canon not in already_processed:
          # print 'adding %s as a mixin of %s' % (mixin_canon, data['class_name'])
          q.put(mixin_canon)
          
      for u in uses:
        u_canon = self.__get_canonical_name(u)
        if u_canon not in already_processed:
          # print 'adding %s as a uses of %s' % (u_canon, data['class_name'])
          q.put(u_canon)
    
    return already_processed
  
  def __get_from_hier(self, module):
    for e in self.ext_hierarchy:
       if module == e['class_name']:
         return e
       
    # raise Exception('Module not found in ExtJS hierarchy: %s' % module)
    return None
  
  def __create_ext_class_hierarchy(self):
    names_set = set()
    ext_components = []
    for (dirpath, dirnames, filenames) in os.walk(self.ext_path + '/src'):
        for filename in filenames:
          ext_class_file = '%s/%s' % (dirpath, filename)
          
          p = ExtClassParser(self.ext_path, ext_class_file)
          names_set.add(p.get_class_name())
          ext_components.append({
            "file":p.get_file_location(),
            "parent":p.get_extends(),
            "requires":p.get_requires(),
            "alt_class_names":p.get_alt_class_names(),
            "class_name":p.get_class_name(),
            "mixins":p.get_mixins(),
            "uses":p.get_uses(),
            "xtypes":p.get_xtypes(),
            
            }
            )
    
    print 'FINISHED PARSING EXTJS SOURCE (%i components)\n\n' % len(ext_components)
    return ext_components
    
    
  def __extract_used_modules(self):
    ext_components = set()
    for (dirpath, dirnames, filenames) in os.walk(self.js_project_path):
        for filename in filenames:
          jsfile = '%s/%s' % (dirpath, filename)
          
          with open(jsfile, 'r') as f:
              contents = f.read();
              class_matches = re.findall(EXT_CREATE_TOKEN, contents, re.DOTALL)
              if class_matches:
                for match in class_matches:
                    # at this point match contains XXX in Ext.create(XXX)
                    ext_component_quoted = match.split(',')[0].strip()
                    # add, getting rid of quotes
                    unquoted = ext_component_quoted[1:-1]
                    canonical = self.__get_canonical_name(unquoted)
                    if canonical not in ext_components:
                        print 'detected Ext.create element:', canonical
                        ext_components.add(canonical)

              for pattern in [EXT_PROXY_TOKEN, EXT_FIELDS_TOKEN]:
                proxy_matches = re.findall(pattern, contents, re.DOTALL)
                if proxy_matches:
                    for match in proxy_matches:
                      for typ in re.finditer(EXT_TYPE_TOKEN, match):
                          canonical = self.__get_canonical_name(typ.group(1))
                          if canonical not in ext_components:
                            print 'detected proxy/reader/grid field type element:', canonical
                            ext_components.add(canonical)
                           
              patterns = [EXT_XTYPE_TOKEN, EXT_DEFAULT_TYPE_TOKEN, EXT_LAYOUT_TOKEN]
              
              for pattern in patterns:
                  for def_type in re.finditer(pattern, contents):
                        # group (1) is the capturing group
                        canonical = self.__get_canonical_name(def_type.group(1))
                        if canonical not in ext_components:
                           print 'detected element: %s' % canonical
                           ext_components.add(canonical)

    return ext_components
         
