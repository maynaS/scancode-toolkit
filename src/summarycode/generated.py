#
# Copyright (c) 2017 nexB Inc. and others. All rights reserved.
# http://nexb.com and https://github.com/nexB/scancode-toolkit/
# The ScanCode software is licensed under the Apache License version 2.0.
# Data generated with ScanCode require an acknowledgment.
# ScanCode is a trademark of nexB Inc.
#
# You may not use this software except in compliance with the License.
# You may obtain a copy of the License at: http://apache.org/licenses/LICENSE-2.0
# Unless required by applicable law or agreed to in writing, software distributed
# under the License is distributed on an "AS IS" BASIS, WITHOUT WARRANTIES OR
# CONDITIONS OF ANY KIND, either express or implied. See the License for the
# specific language governing permissions and limitations under the License.
#
# When you publish or redistribute any data created with ScanCode or any ScanCode
# derivative work, you must accompany this data with the following acknowledgment:
#
#  Generated with ScanCode and provided on an "AS IS" BASIS, WITHOUT WARRANTIES
#  OR CONDITIONS OF ANY KIND, either express or implied. No content created from
#  ScanCode should be considered or used as legal advice. Consult an Attorney
#  for any legal advice.
#  ScanCode is a free software code scanning tool from nexB Inc. and others.
#  Visit https://github.com/nexB/scancode-toolkit/ for support and download.

from __future__ import absolute_import
from __future__ import division
from __future__ import print_function
from __future__ import unicode_literals

from itertools import islice

from commoncode import compat
from commoncode.datautils import Boolean
from commoncode.text import toascii
from plugincode.scan import ScanPlugin
from plugincode.scan import scan_impl
from scancode import CommandLineOption
from scancode import OTHER_SCAN_GROUP
import typecode.contenttype

"""
Tag files as generated.
"""

# Tracing flag
TRACE = False


def logger_debug(*args):
    pass


if TRACE:
    import logging
    import sys

    logger = logging.getLogger(__name__)
    logging.basicConfig(stream=sys.stdout)
    logger.setLevel(logging.DEBUG)

    def logger_debug(*args):
        return logger.debug(' '.join(isinstance(a, compat.string_types) and a or repr(a) for a in args))


@scan_impl
class GeneratedCodeDetector(ScanPlugin):
    """
    Tag a file as generated.
    """
    resource_attributes = dict(is_generated=Boolean(
        help='True if this file is likely an automatically generated file.'))

    sort_order = 50

    options = [
        CommandLineOption(('--generated',),
            is_flag=True, default=False,
            help='Classify automatically generated code files with a flag.',
            help_group=OTHER_SCAN_GROUP,
            sort_order=50,
        )
    ]

    def is_enabled(self, generated, **kwargs):
        return generated

    def get_scanner(self, **kwargs):
        return generated_scanner


def generated_scanner(location, **kwargs):
    is_generated = False
    for _clue in get_generated_code_hint(location):
        # TODO: consider returning the "clue"
        is_generated = True
        break
    return dict(is_generated=is_generated)


GENERATED_KEYWORDS = tuple(g.lower() for g in (
    'generated by',
    'auto-generated',
    'automatically generated',
    # Apache Axis
    'auto-generated from wsdl',
    # jni javahl and others
    'do not edit this file',
    # jni javahl
    'it is machine generated',
    'by hibernate tools',
    'generated from idl',

    # castor generated files
    'following schema fragment specifies the',

    # Tomcat JSPC
    'automatically created by',

    # in GNU Classpath
    'this file was automatically generated by gnu.localegen from cldr',
    'this document is automatically generated by gnu.supplementgen',

    # linux kernel/u-boot
    'this was automagically generated from',

    # angular
    'this code is generated',
    'this code is generated - do not modify',

    # cython
    'generated by cython',
    # sqlite amalgamation
    'this file is an amalgamation of many separate c source files from sqlite',

    # various generated or last generated:
    'generated on',
    'last generated on',

    # in freepascal unicode
    "this is an automatically created file",

    # generated by Postgres ECPG sql to c preprocessor
    'processed by ecpg (regression mode)',
    'these include files are added by the preprocessor',

    'this readme is generated, please do not update',

    'this file was automatically generated by',
    'any changes will be lost if this file is regenerated',

    # yarn lock files
    'this is an autogenerated file. do not edit this file directly'

    'this file is generated by',
    'microsoft visual c++ generated include file',

    # OpenJDK:
    'generated by the idl-to-java compiler',
    'this file was mechanically generated: do not edit!',
    'generated by mc.java version 1.0, do not edit by hand!',
    'generated from input file',
    'generated content - do not edit',
    'generators: org.graalvm',

    'Generated by GNU Autoconf',

    'This file has been generated by the GUI designer. Do not modify',

    'file is generated by gopy gen. do not edit.',
    
    #https://github.com/Microsoft/azure-devops-python-api/blob/0d9537016bd45cf7f2140433c0ec54b44768f726/vsts/vsts/licensing/v4_1/licensing_client.py
    'generated file, do not edit',
    'changes may cause incorrect behavior and will be lost if the code is regenerated.',
    'this file is generated. best not to modify it, as it will likely be overwritten.',

    # in Ogg/Vorbis
    'function: static codebooks autogenerated by',
    
    # yarn lock
    'THIS IS AN AUTOGENERATED FILE. DO NOT EDIT THIS FILE DIRECTLY.',
    'This file has been automatically created by',
    'Please do not edit this file, all changes will be lost',

))


max_lines = 150


def get_generated_code_hint(location, generated_keywords=GENERATED_KEYWORDS):
    """
    Return a line of extracted text from a file if that file is likely
    generated source code.

    for each of the the first few lines of a source code file
      if generated keywords are found in the line as lowercase
         yield the line text as a 'potentially_ generated' annotation
    """
    T = typecode.contenttype.get_type(location)
    if not T.is_text:
        return
    with open(location, 'rb') as filein:
        for line in islice(filein, max_lines):
            text = toascii(line.strip())
            textl = text.lower()
            if any(kw in textl for kw in generated_keywords):
                # yield only the first 100 chars..
                yield text[:100]

