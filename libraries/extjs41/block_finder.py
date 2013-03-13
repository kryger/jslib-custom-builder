#!/usr/bin/python
# -*- coding: utf-8 -*-
import re
import os


class ExtBlockFinder:

    EXT_DEFINE_START = "Ext.define('%s'"
    EXT_DEFINE_END = '});'

    def __init__(self, content_lines):
        self.content_lines = content_lines

    def __get_start_index(self, class_name):
        """Return first line of the class definition, return -1 if class not found."""

        for (index, line) in enumerate(self.content_lines):
            if line.startswith(self.EXT_DEFINE_START % class_name):
                return index

        return -1

    def __get_end_index(self, start_index, class_name):
        """Return numer of the line that ends the specified class definition."""

        for line_index in range(start_index, len(self.content_lines)):
            line = self.content_lines[line_index]
            if line.startswith(self.EXT_DEFINE_END):
                return line_index

        raise Exception('Unable to match end for class %s' % class_name)

    def find(self, class_name):
        """Return a tuple containing index of the first and last line of the class definition."""

        start = self.__get_start_index(class_name)
        if start == -1:
            print 'WARNING, class name=%s not found, probably incorrectly extracted' \
                % class_name
            return (0, 0)

        end = self.__get_end_index(start, class_name)
        return (start, end)


