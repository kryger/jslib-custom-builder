import re, os.path

class ExtClassParser:
    EXT_DEFINE_TOKEN = "Ext.define\('(.*?)',"
    EXT_REQUIRES_TOKEN = 'requires:\s\[(.*?)\]'
    EXT_EXTENDS_TOKEN = "extend:\s'(.*?)'"
    EXT_ALTERNATE_CLASS_NAME_TOKEN_SINGLE = "alternateClassName:\s'(.*?)'"
    EXT_ALTERNATE_CLASS_NAME_TOKEN_ARRAY = "alternateClassName:\s\[(.*?)\]"
  
    def __init__(self, src_root, class_file_location):
      self.src_root = src_root
      self.class_file_location = class_file_location
      
      self.__parse()
      
    def __parse(self):
      module_path = self.class_file_location#self.__construct_path(self.class_name)
      # FIXME scan for alternative class names?
      if not os.path.isfile(module_path):
        print 'module not found:', module_path
        self.requires=[]
        self.extends=None
        self.alternate_class_names=[]
        return
      
      with open(module_path, 'r') as f:
        contents = f.read()
        
        self.class_name = self.__process_class_name(contents)
        self.requires = self.__process_requires(contents, module_path)
        self.extends = self.__process_extends(contents)
        self.alternate_class_names = self.__process_alternate_class_names(contents, module_path)
        
        print '\nParsed module=%s\nclassname=%s\nextends=%s\nrequires=%s\nalt=%s' % (module_path, self.class_name, self.extends, self.requires, self.alternate_class_names)
    
    # extract list of alternative class names for this module
    def __process_alternate_class_names(self, contents, module_path):
      matches =  re.search(self.EXT_ALTERNATE_CLASS_NAME_TOKEN_ARRAY,contents,re.DOTALL)
      
      # class has no own dependencies
      if not matches:
        matches =  re.search(self.EXT_ALTERNATE_CLASS_NAME_TOKEN_SINGLE,contents,re.DOTALL)
      
      if not matches:
        return []
      
      alternate_blocks_tuple = matches.groups()
      
      return list(alternate_blocks_tuple)
      
      #assert len(require_blocks) == 1, 'Exactly one \'requires\' property expected in the module, found: %i; offending file: %s' % (len(require_blocks), module_path)

      #requires_array_string = require_blocks[0]
      # remove spaces, new lines and apostrophes
      #requires_array_string = re.sub("[\s']", '', requires_array_string)
      
      #return requires_array_string.split(',')

    # extract list of classes the module requires
    def __process_requires(self, contents, module_path):
      matches =  re.search(self.EXT_REQUIRES_TOKEN,contents,re.DOTALL)
      
      # class has no own dependencies
      if not matches:
        return []
      
      require_blocks = matches.groups()
      
      assert len(require_blocks) == 1, 'Exactly one \'requires\' property expected in the module, found: %i; offending file: %s' % (len(require_blocks), module_path)

      requires_array_string = require_blocks[0]
      # remove spaces, new lines and apostrophes
      requires_array_string = re.sub("[\s']", '', requires_array_string)
      
      return requires_array_string.split(',')

    # extract name of the class the module extends      
    def __process_extends(self, contents):
      matches =  re.search(self.EXT_EXTENDS_TOKEN,contents,re.DOTALL)
      if not matches:
        return None
        
      extend_blocks = matches.groups()
      
      assert len(extend_blocks) == 1, 'Exactly one \'extend\' property expected in the module, found: %i; offending file: %s' % (len(extend_blocks), module_path)

      return extend_blocks[0]
    
    # extract name of the class in the module
    def __process_class_name(self, contents):
      matches =  re.search(self.EXT_DEFINE_TOKEN,contents)
      if not matches:
        return None
        
      extend_blocks = matches.groups()
      #print matches.groups()
      #assert len(extend_blocks) == 1, 'Exactly one \'extend\' property expected in the module, found: %i; offending file: %s' % (len(extend_blocks), module_path)

      return extend_blocks[0]
    
      
    def __construct_path(self, ext_class_name):
      components = ext_class_name.split('.')
      
      full_path = [self.src_root]
      
      # add the components, skipping the "Ext." part which is first
      full_path.extend(components[1:])
      
      # FIXME path separator
      return '%s.js' % ('/'.join(full_path))
    
    def get_requires(self):
      return self.requires
    
    
    def get_extends(self):
      return self.extends   