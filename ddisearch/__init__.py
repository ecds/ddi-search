# file ddisearch/__init__.py
#
# Copyright 2014 Emory University
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#    http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

'''
Django website for search and display access to DDI XML descriptions
of research datasets such as those provided by the ICPSR.  Uses
eXist-db for powerful full text searching.

'''

__version_info__ = (1, 1, 0, None)

# Dot-connect all but the last. Last is dash-connected if not None.
__version__ = '.'.join(str(i) for i in __version_info__[:-1])
if __version_info__[-1] is not None:
    __version__ += ('-%s' % (__version_info__[-1],))
