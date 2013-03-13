import argparse
from libraries.extjs41.build_trimmer import BuildTrimmer
from libraries.extjs41.usage_parser import ExtBuilder

EXT_BUILD_FILE_IN = r'ext-all-debug'

if __name__ == "__main__":
    arg_parser = argparse.ArgumentParser(description='jslib custom builder')
    arg_parser.add_argument('-sourcedir', help='Path to the directory containing the JS files', action='store',
                            dest='source_dir', required=True)
    arg_parser.add_argument('-extdir', help='Path to the ExtJS distribution folder', action='store',
                            dest='ext_dir', required=True)
    params = vars(arg_parser.parse_args())
    ext_builder = ExtBuilder(params['source_dir'], params['ext_dir'], EXT_BUILD_FILE_IN)
    
    need_these = [
      'Ext.picker.Date',
      # 'Ext.dom.Element',
      # 'Ext.EventObject' is actually called Ext.EventObjectImpl in the 'define' block
      'Ext.EventObject',
      'Ext.EventObjectImpl',
      'Ext.dom.CompositeElement',
      'Ext.util.TaskRunner',
      ]    
    unused_classes = ext_builder.get_unused_classes(need_these)
    print '\n\nunused=', unused_classes
    b = BuildTrimmer(unused_classes, params['ext_dir'] + '/%s.js' % EXT_BUILD_FILE_IN)
    b.trim()
