import argparse, os, re

EXT_CREATE_TOKEN = 'Ext.create\((.*?)\)'
INDEX_HTML_TEMPLATE = '''
<html>
   <head>
      <script type="text/javascript" src="%s"></script>
   <head>
   <body>
      Index page that simulates your webapp.
   </body>
</html
'''

def process(path):
   ext_components = set()
   for (dirpath, dirnames, filenames) in os.walk(path):
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

   # create the fake JS file                  
   with open('app.js', 'w') as f:
      for ext_component in ext_components:
         f.write("Ext.create('%s');\n" % ext_component)
         
   with open('index.html', 'w') as f:
      pass
         
   

if __name__ == "__main__":
    arg_parser = argparse.ArgumentParser(description='jslib custom builder')
    arg_parser.add_argument('-sourcedir', help='Path to the directory containing the JS files', action='store',
                            dest='sourcedir', required=True)
    params = vars(arg_parser.parse_args())
    process(params['sourcedir'])
    
