## #!/usr/bin/env python3
##
# Copyright 2019 Pixelworks Inc.
#
# Author: Houyu Li <hyli@pixelworks.com>
#
# Sample action 'greet' in sample job 'sayhello'
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
# 		http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.
#
## // ##

def run(msg, *args):
    """Just print out hello message and recieved arguments"""

    all_args_string = u''
    for arg in args:
        all_args_string += arg + u' '
    return u'Hello %s, I got %d args, they are %s' % (msg[u'User'].NickName, len(args), all_args_string)

def help_desc():
    """Description for current module (Action)"""
    return u'Just say hello\n\tand echo input'