## #!/usr/bin/env python3
##
# Copyright 2019 Pixelworks Inc.
#
# Author: Houyu Li <hyli@pixelworks.com>
#
# Help module for job 'sayhello'
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

import os

from wechatbothelper.job import help as job_help

# Description message for job 'sayhello'
_help_desc = u'A sample job'

# Definition of options needed in config file, with default value, and/or comment,
# Options in this module should be in [sayhello.help] section. Can be empty.
_config_opts = []

def run(context, *args):
    """Return available Action names with description"""

    msg = context[u'msg']

    my_display_name = None
    try:
        my_display_name = msg[u'User'].Self.DisplayName
    except:
        pass

    return job_help(my_display_name, __file__, __name__)
