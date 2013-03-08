import os

class BuildShaver:
  #EXT_DEFINE_TEMPLATE = 'Ext.define("%s"'
  EXT_DEFINE_TEMPLATE = "Ext.define('%s'"
  
  def __init__(self, used_classes, source_build_file):
    self.used_classes = used_classes
    #self.source_build_file = source_build_file
    self.source_build_file = source_build_file
    with open(source_build_file, 'r') as f:
      self.content = f.read()
    
    
  def __get_class_definition(self, class_name):
    start = self.__get_start_index(class_name)
    print start
    
  def __get_start_index(self, class_name):
    return self.content.find(self.EXT_DEFINE_TEMPLATE % class_name)
  
  def __get_end_index(self, start_index):
    braces_level = 1
    
    start_offset = (start_index + len(self.EXT_DEFINE_TEMPLATE))
    
    end_index = start_offset
    for index, char in enumerate(self.content[start_offset:]):
      end_index = end_index + 1
      #print index, char
      if char == '(':
        braces_level = braces_level + 1
      elif char == ')':
        braces_level = braces_level - 1
        
      if braces_level == 0:
        break
      
#    if self.content[end_index] == ';':
 #     end_index = end_index + 1
      
    return end_index
      
    #print end_index
    #print self.content[start_index:end_index]
      #switch (char):
  
  def __match(self, class_name):
    start = self.__get_start_index(class_name)
    end = self.__get_end_index(start)
    print 'The range is', start, end
    return range(start, end)
    
    
  
  def __check_index_within_bounds(self, index, bounds_list):
    print index, bounds_list
    return True
    
  def shave(self):
    
    forbidden_bytes = set()
    for class_name in self.used_classes:
      print class_name
      #bounds = self.__match(class_name)
      forbidden_bytes.update(self.__match(class_name))
    
    
    print 'how many forbidden bytes?', len(forbidden_bytes)
    input_size = os.stat(self.source_build_file).st_size
    percent_point = input_size / 100
    
    percent_done = 0;
    counter = 0
    print 'Streaming file...'
    with open(self.source_build_file + '.out', 'w') as out:
      with open(self.source_build_file, 'r') as input:
        for index, byte in enumerate(input.read()):
          counter = counter + 1
          if counter == percent_point:
            counter = 0
            percent_done = percent_done + 1
            print 'Done: %i%%' % percent_done
            out.flush()
          
          if index not in forbidden_bytes:
#            print 'writing byte!'
            out.write(byte)
          #let_byte_go = self.__check_index_within_bounds(index, bounds)
          #print byte
          
      
