## #!/usr/bin/env python3
##
# Copyright 2019 Pixelworks Inc.
#
# Author: Houyu Li <hyli@pixelworks.com>
#
# Helper function for job module
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

import os, sys, re

def help(user_display_name, module_file_fullpath, module_name):
    """Generate help message for all actions can be used in the job"""

    my_path = os.path.dirname(module_file_fullpath)
    my_fname = os.path.basename(module_file_fullpath)
    my_package = module_name.rsplit(u'.')[-2] # ex: sayhello
    my_package_path = module_name.rsplit(u'.', 1)[-2] # ex: wechatbot.sayhello

    help_msg = u'Actions in "%s":\n========\n' % (my_package)

    for action_py in os.listdir(my_path):

        action_name = u''
        action_desc = u''

        # Skip non-file
        if not os.path.isfile(os.path.join(my_path, action_py)):
            continue
        # Skip self
        if action_py == my_fname:
            continue
        # Folders start with "__"
        if re.findall(u'^__.+', action_py):
            continue
        # Folders start with "."
        if re.findall(u'^\..*', action_py):
            continue

        action_name = re.sub(u'\.py$', u'', action_py)

        # Load action module
        action_module_path = u'%s.%s' % (my_package_path, action_name)
        action_from_path = my_package_path

        # Import the "help" module
        try:
            action_module = __import__(
                action_module_path, fromlist = [action_from_path])
        except:
            print(u"Cannot import %s." % (action_module_path), file = sys.stderr)
            continue
        # Get Job description
        try:
            action_desc = action_module._help_desc
        except:
            action_desc = u'[no description]'
            print(u"No _help_desc for %s." % (action_module_path), file = sys.stderr)

        # Arrange action_name and action_desc in help_msg
        help_msg += u'> %s\n\t%s\n' % (action_name, action_desc)

    # Tail messages
    help_msg += u'========\nTo get detailed usage for\neach action, try:\n'
    if user_display_name:
        help_msg += u'@%s\u2005%s <action> -h' % (user_display_name, my_package)
    else:
        help_msg += u'%s <action> -h' % (my_package)

    return help_msg
