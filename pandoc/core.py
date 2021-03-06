#!/usr/bin/python
# -*- encoding: utf-8 -*-
"""

"""
import subprocess
from os.path import exists
from tempfile import NamedTemporaryFile
import os

# Import find executable engine
try:
    from shutil import which
except ImportError:
    from distutils.spawn import find_executable

    which = find_executable

# Path to the executable
PANDOC_PATH = which('pandoc')


class Document(object):
    """A formatted document."""

    # removed pdf and epub which cannot be handled by stdout
    OUTPUT_FORMATS = (
        'asciidoc', 'beamer', 'commonmark', 'context', 'docbook',
        'docx', 'dokuwiki', 'dzslides', 'epub', 'epub3', 'fb2',
        'haddock', 'html', 'html5', 'icml', 'json', 'latex', 'man',
        'markdown', 'markdown_github', 'markdown_mmd',
        'markdown_phpextra', 'markdown_strict', 'mediawiki', 'native',
        'odt', 'opendocument', 'opml', 'org', 'pdf', 'plain',
        'revealjs', 'rst', 'rtf', 's5', 'slideous', 'slidy', 'texinfo',
        'textile'
    )

    # TODO: Add odt, epub formats (requires file access, not stdout)

    def __init__(self):
        self._content = None
        self._format = None
        self._register_formats()
        self.arguments = []

        if not exists(PANDOC_PATH):
            raise OSError("Path to pandoc executable does not exists")


    def bib(self, bibfile):
        if not exists(bibfile):
            raise IOError("Bib file not found: %s" % bibfile)
        self.add_argument("bibliography=%s" % bibfile)


    def csl(self, cslfile):
        if not exists(cslfile):
            raise IOError("CSL file not found: %s" % cslfile)
        self.add_argument("csl=%s" % cslfile)

    def abbr(self, abbrfile):
        if not exists(abbrfile):
            raise IOError("Abbreviations file not found: " + abbrfile)
        self.add_argument("citation-abbreviations=%s" % abbrfile)


    def add_argument(self, arg):
        self.arguments.append("--%s" % arg)
        return self.arguments


    @classmethod
    def _register_formats(cls):
        """Adds format properties."""
        for fmt in cls.OUTPUT_FORMATS:
            clean_fmt = fmt.replace('+', '_')
            setattr(cls, clean_fmt, property(
                (lambda x, fmt=fmt: cls._output(x, fmt)), # fget
                (lambda x, y, fmt=fmt: cls._input(x, y, fmt)))) # fset


    def _input(self, value, format=None):
        # format = format.replace('_', '+')
        self._content = value
        self._format = format


    def _output(self, format):
        subprocess_arguments = [PANDOC_PATH, '--from=%s' % self._format, '--to=%s' % format]
        subprocess_arguments.extend(self.arguments)

        p = subprocess.Popen(
                subprocess_arguments,
                stdin=subprocess.PIPE,
                stdout=subprocess.PIPE
        )
        return p.communicate(self._content)[0]


    def to_file(self, output_filename):
        '''Handles pdf and epub format.
        Inpute: output_filename should have the proper extension.
        Output: The name of the file created, or an IOError if failed'''
        temp_file = NamedTemporaryFile(mode="w", suffix=".md", delete=False)
        temp_file.write(self._content)
        temp_file.close()

        subprocess_arguments = [PANDOC_PATH, temp_file.name, '-o %s' % output_filename]
        subprocess_arguments.extend(self.arguments)
        cmd = " ".join(subprocess_arguments)

        fin = os.popen(cmd)
        msg = fin.read()
        fin.close()
        if msg:
            print("Pandoc message: {}",format(msg))

        os.remove(temp_file.name)

        if exists(output_filename):
            return output_filename
        else:
            raise IOError("Failed creating file: %s" % output_filename)
