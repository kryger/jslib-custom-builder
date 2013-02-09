import argparse, os, re


EXT_CREATE_TOKEN = 'Ext.create\((.*?)\)'
#EXT_CREATE_TOKEN = '\((.*?)\)'
SINGLE_QUOTE_TOKEN = "'.*'"
# FIXME: Ext.createWidget

def process(path):
   ext_components = set()
   for (dirpath, dirnames, filenames) in os.walk(path):
      #print dirpath, dirnames, filenames
      for filename in filenames:
         jsfile = '%s/%s' % (dirpath, filename)
         
         with open(jsfile, 'r') as f:
            contents = f.read();
            #print contents
            matches =  re.search(EXT_CREATE_TOKEN,contents,re.DOTALL)
            if matches:
               for match in matches.groups():
                  # at this point match contains XXX in Ext.create(XXX)
                  #print match, '\n'
                  #component = match[match.find("'")
                  ext_component_quoted = match.split(',')[0].strip()
                  #print ext_component_quoted
                  # add, getting rid of quotes
                  ext_components.add(ext_component_quoted[1:-1])
                  
   print ext_components
   

if __name__ == "__main__":
    arg_parser = argparse.ArgumentParser(description='jslib custom builder')
    arg_parser.add_argument('-sourcedir', help='Path to the directory containing the JS files', action='store',
                            dest='sourcedir', required=True)
    params = vars(arg_parser.parse_args())
    process(params['sourcedir'])
    
