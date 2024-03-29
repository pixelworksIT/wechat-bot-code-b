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

import argparse

# Description for current module (Action)
_help_desc = u'Just say hello\n\tand echo input'

# Definition of options needed in config file, with default value, and/or comment,
# Options in this module should be in [sayhello.greet] section. Can be empty.
_config_opts = [
    {
        u'name': u'count_args',
        u'default': u'1',
        u'description': u'Count number of args and tell user.'
    }
]

def run(context, *args):
    """Just print out hello message and recieved arguments"""

    msg = context[u'msg']
    config = context[u'config']

    action_msg = None

    module_name_parts = __name__.split(u'.')

    arg_parser = argparse.ArgumentParser(
        prog = u'%s %s' % (module_name_parts[-2], module_name_parts[-1])
    )
    arg_parser.add_argument(u'name', metavar = u'YourName',
        help = u'Please give your name, then I can say hello to you.'
    )
    arg_parser.add_argument(u'-n', metavar = u'NickName', nargs = u'?',
        const = u'unknown', default = u'unknown',
        help = u'May I know your nick name?'
    )

    try:
        my_args = arg_parser.parse_args(args)
    except:
        action_msg = arg_parser.format_help()
        return action_msg

    if config[u'count_args'] == u'1':
        action_msg = u'Hello %s! %d args\nConfigured to count args,' % (my_args.name, len(args))
    else:
        action_msg = u'Hello %s!' % (my_args.name)

    if my_args.n != u'unknown':
        action_msg += u'\nGlad to know your nickname %s.' % (my_args.n)

    return action_msg