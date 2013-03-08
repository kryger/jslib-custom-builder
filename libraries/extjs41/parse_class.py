import re

class ExtClassParser:
    EXT_REQUIRES_TOKEN = 'requires:\s\[(.*?)\]'
    EXT_EXTENDS_TOKEN = "extend:\s'(.*?)'"
  
    def __init__(self, src_root, class_name):
      self.src_root = src_root
      self.class_name = class_name
      
      self.__parse()
      
    def __parse(self):
      #print 'parsing', self.src_root, self.class_name
      module_path = self.__construct_path(self.class_name)
      #print 'full path=', self.__construct_path(self.class_name)
      
      with open(module_path, 'r') as f:
        contents = f.read()
        
        self.requires = self.__process_requires(contents, module_path)
        self.extends = self.__process_extends(contents)
    
    # extract list of classes the module requires
    def __process_requires(self, contents, module_path):
      matches =  re.search(self.EXT_REQUIRES_TOKEN,contents,re.DOTALL)
      require_blocks = matches.groups()
      
      assert len(require_blocks) == 1, 'Exactly one \'requires\' property expected in the module, found: %i; offending file: %s' % (len(require_blocks), module_path)

      requires_array_string = require_blocks[0]
      # remove spaces, new lines and apostrophes
      requires_array_string = re.sub("[\s']", '', requires_array_string)
      
      return requires_array_string.split(',')

    # extract name of the class the module extends      
    def __process_extends(self, contents):
      matches =  re.search(self.EXT_EXTENDS_TOKEN,contents,re.DOTALL)
      extend_blocks = matches.groups()
      
      assert len(extend_blocks) == 1, 'Exactly one \'extend\' property expected in the module, found: %i; offending file: %s' % (len(extend_blocks), module_path)

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