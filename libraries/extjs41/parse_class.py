#!/usr/bin/python
# -*- coding: utf-8 -*-
import re
import os.path


class ExtClassParser:

    EXT_DEFINE_TOKEN = "^\s*Ext.define\('Ext\.(.*?)',"
    EXT_DEFINE_TOKEN_DOUBLEQUOTE = 'Ext.define\("Ext\.(.*?)",'
    EXT_REQUIRES_TOKEN_SINGLE = "requires:\s?'(.*?)'"
    EXT_REQUIRES_TOKEN_MULTI = 'requires:\s?\[(.*?)\]'
    EXT_XTYPES_TOKEN_SINGLE = "^\s*alias:\s?'(.*?)'"
    EXT_XTYPES_TOKEN_MULTI = "^\s*alias:\s?\[(.*?)\]"
    EXT_USES_TOKEN = 'uses\s*:\s*\[(.*?)\]'
    EXT_MIXINS_TOKEN = 'mixins:\s?\{(.*?)\}'
    EXT_EXTENDS_TOKEN = "^\s*extend:\s?'(.*?)'"
    EXT_ALTERNATE_CLASS_NAME_TOKEN_SINGLE = \
        "alternateClassName:\s?'(.*?)'"
    EXT_ALTERNATE_CLASS_NAME_TOKEN_ARRAY = \
        "alternateClassName:\s?\[(.*?)\]"

    def __init__(self, src_root, class_file_location):
        self.src_root = src_root
        self.class_file_location = class_file_location
        self.__parse()

    def __parse(self):
        with open(self.class_file_location, 'r') as f:
            contents = f.read()

            self.class_name = self.__process_class_name(contents)
            self.requires = self.__process_requires(contents,
                    self.class_file_location)
            self.mixins = self.__process_mixins(contents,
                    self.class_file_location)
            self.uses = self.__process_uses(contents,
                    self.class_file_location)
            self.extends = self.__process_extends(contents)
            self.alternate_class_names = \
                self.__process_alternate_class_names(contents,
                    self.class_file_location)
            self.xtypes = self.__process_xtypes(contents,
                    self.class_file_location)

            print '''
Parsed module= %s
classname=%s
extends=%s
mixins=%s
uses=%s
requires=%s
alt=%s
alias=%s''' \
                % (
                self.class_file_location,
                self.class_name,
                self.extends,
                self.mixins,
                self.uses,
                self.requires,
                self.alternate_class_names,
                self.xtypes,
                )

    # extract list of alternative class names for this module

    def __process_alternate_class_names(self, contents, module_path):
        matches = re.search(self.EXT_ALTERNATE_CLASS_NAME_TOKEN_ARRAY,
                            contents, re.DOTALL)

        if not matches:
            matches = \
                re.search(self.EXT_ALTERNATE_CLASS_NAME_TOKEN_SINGLE,
                          contents, re.DOTALL)
            if not matches:

          # class has no alternate class names

                return []

        alt_blocks = matches.groups()
        assert len(alt_blocks) == 1, \
            'At most one \'alternateClassName\' property expected in the module, found: %i; offending file: %s' \
            % (len(alt_blocks), module_path)
        alt_array_string = alt_blocks[0]

      # entire 'alternateClassName' block squeezed into a single line, for example:
      # "observable:Ext.util.Observable,animate:Ext.util.Animate,elementCt:Ext.util.ElementContainer,renderable:Ext.util.Renderable,state:Ext.state.Stateful"

        alt_array_string_sub = re.sub("[\s']", '', alt_array_string)
        return alt_array_string_sub.split(',')

    # extract list of classes the module mixins

    def __process_mixins(self, contents, module_path):
        matches = re.search(self.EXT_MIXINS_TOKEN, contents, re.DOTALL)

        if not matches:

        # class has no mixins

            return []

        mixins_blocks = matches.groups()
        assert len(mixins_blocks) == 1, \
            'At most one \'mixins\' property expected in the module, found: %i; offending file: %s' \
            % (len(mixins_blocks), module_path)
        mixins_array_string = mixins_blocks[0]

      # entire 'mixins' block squeezed into a single line
      # observable:Ext.util.Observable,animate:Ext.util.Animate,elementCt:Ext.util.ElementContainer,renderable:Ext.util.Renderable,state:Ext.state.Stateful

        mixins_array_string_sub = re.sub("[\s']", '',
                mixins_array_string)
        mixins = []
        for component in mixins_array_string_sub.split(','):
            mixins.append(component.split(':')[1])

        return mixins

    # extract list of classes the module uses

    def __process_uses(self, contents, module_path):
        matches = re.search(self.EXT_USES_TOKEN, contents, re.DOTALL)

        if not matches:

        # class has no own dependencies

            return []

        uses_blocks = matches.groups()
        assert len(uses_blocks) == 1, \
            'At most one \'uses\' property expected in the module, found: %i; offending file: %s' \
            % (len(uses_blocks), module_path)

        uses_array_string = uses_blocks[0]

      # remove spaces, new lines and apostrophes

        uses_array_string = re.sub("[\s']", '', uses_array_string)
        return uses_array_string.split(',')

    # extract list of aliases (xtype/etc.)

    def __process_xtypes(self, contents, module_path):
        if not self.class_name:
            return []

        matches = re.search(self.EXT_XTYPES_TOKEN_SINGLE, contents,
                            re.MULTILINE)

        if not matches:
            matches = re.search(self.EXT_XTYPES_TOKEN_MULTI, contents,
                                re.MULTILINE)
            if not matches:

          # no alias names

                return []

        require_blocks = matches.groups()
        assert len(require_blocks) == 1, \
            'At most one \'alias\' property expected in the module, found: %i; offending file: %s' \
            % (len(require_blocks), module_path)

        requires_array_string = require_blocks[0]

      # remove spaces, new lines and apostrophes

        requires_array_string = re.sub("[\s']", '',
                requires_array_string)

        out = []
        for component in requires_array_string.split(','):
            out.append(component.split('.')[1])

        return out

    # extract list of classes the module requires

    def __process_requires(self, contents, module_path):
        matches = re.search(self.EXT_REQUIRES_TOKEN_MULTI, contents,
                            re.DOTALL)

      # class has no own dependencies

        if not matches:
            matches = re.search(self.EXT_REQUIRES_TOKEN_SINGLE,
                                contents, re.DOTALL)
            if not matches:
                return []

        require_blocks = matches.groups()

        assert len(require_blocks) == 1, \
            'At most one \'requires\' property expected in the module, found: %i; offending file: %s' \
            % (len(require_blocks), module_path)

        requires_array_string = require_blocks[0]

      # remove spaces, new lines and apostrophes

        requires_array_string = re.sub("[\s']", '',
                requires_array_string)

        return requires_array_string.split(',')

    # extract name of the class the module extends

    def __process_extends(self, contents):
        matches = re.search(self.EXT_EXTENDS_TOKEN, contents,
                            re.MULTILINE)
        if not matches:
            return None

        extend_blocks = matches.groups()

        assert len(extend_blocks) == 1, \
            'At most one \'extend\' property expected in the module, found: %i; offending file: %s' \
            % (len(extend_blocks), module_path)

        return extend_blocks[0]

    # extract name of the class in the module

    def __process_class_name(self, contents):
        matches = re.search(self.EXT_DEFINE_TOKEN, contents,
                            re.MULTILINE)
        if not matches:
            matches = re.search(self.EXT_DEFINE_TOKEN_DOUBLEQUOTE,
                                contents, re.MULTILINE)
            if not matches:

            # TODO raise exception?

                return None

        classname_blocks = matches.groups()

        return 'Ext.%s' % classname_blocks[0]

    def __construct_path(self, ext_class_name):
        print 'in=', ext_class_name
        components = ext_class_name.split('.')

        full_path = [self.src_root]

      # add the components, skipping the "Ext." part which is first

        full_path.extend(components[1:])

      # FIXME OS-specific path separator

        return '%s.js' % '/'.join(full_path)

    def get_requires(self):
        return self.requires

    def get_file_location(self):
        return self.class_file_location

    def get_extends(self):
        return self.extends

    def get_alt_class_names(self):
        return self.alternate_class_names

    def get_class_name(self):
        return self.class_name

    def get_mixins(self):
        return self.mixins

    def get_uses(self):
        return self.uses

    def get_xtypes(self):
        return self.xtypes


