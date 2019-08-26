## #!/usr/bin/env python3
##
# Copyright 2019 Pixelworks Inc.
#
# Author: Houyu Li <hyli@pixelworks.com>
#
# Helper functions for main bot
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
    """Generate help message for all jobs can be used in the bot"""

    my_path = os.path.dirname(module_file_fullpath)
    my_package = module_name.rsplit(u'.', 1)[-2]

    help_msg = u'Available Jobs:\n========\n'

    for job_dir in os.listdir(my_path):

        job_name = u''
        job_desc = u''

        # Skip file
        if os.path.isfile(os.path.join(my_path, job_dir)):
            continue
        # Folders start with "__"
        if re.findall(u'^__.+', job_dir):
            continue
        # Folders start with "."
        if re.findall(u'^\..*', job_dir):
            continue

        job_name = job_dir

        # Load "help" module from Job module
        job_help_module_path = u'%s.%s.help' % (my_package, job_name)
        job_help_from_path = u'%s.%s' % (my_package, job_name)

        # Import the "help" module
        try:
            job_help_module = __import__(
                job_help_module_path, fromlist = [job_help_from_path])
        except:
            print(u"Cannot import %s." % (job_help_module_path), file = sys.stderr)
            continue
        # Get Job description
        try:
            job_desc = job_help_module.help_desc()
        except:
            job_desc = u'[no description]'
            print(u"No help_desc() for %s." % (job_name), file = sys.stderr)

        # Arrange job_name and job_desc in help_msg
        help_msg += u'> %s\n\t%s\n' % (job_name, job_desc)

    # Tail messages
    help_msg += u'========\nTo get detailed usage for\neach job, try:\n'
    if user_display_name:
        help_msg += u'@%s\u2005<job> help' % (user_display_name)
    else:
        help_msg += u'<job> help'

    return help_msg
