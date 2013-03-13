import os, re
from block_finder import ExtBlockFinder

class BuildTrimmer:
  def __init__(self, unused_classes, source_build_file):
    self.unused_classes = unused_classes
    self.source_build_file = source_build_file
    with open(source_build_file, 'r') as f:
      lines = f.readlines()
      self.ext_block_finder = ExtBlockFinder(lines)
    
    
  def trim(self):
    forbidden_lines = set()
    for index, class_name in enumerate(self.unused_classes):
      print '[%i/%i] Trimming off: %s' % (index + 1, len(self.unused_classes), class_name)
      start, end = self.ext_block_finder.find(class_name)
      
      if start < 1:
        print 'class not found:', class_name
        continue
      
      forbidden_lines.update(range(start, end + 1))
    
    out_name = self.source_build_file + '.out.js'
    print 'Saving file: %s' % out_name
    with open(self.source_build_file + '.cut.js', 'w') as out_cut:
      with open(self.source_build_file + '.out.js', 'w') as out:
         with open(self.source_build_file, 'r') as input:
            for index, line in enumerate(input.readlines()):
               if index not in forbidden_lines:
                  out.write(line)
               else:
                  out_cut.write(line)
