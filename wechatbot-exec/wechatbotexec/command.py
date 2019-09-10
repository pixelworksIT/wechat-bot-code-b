## #!/usr/bin/env python3
##
# Copyright 2019 Pixelworks Inc.
#
# Author: Houyu Li <hyli@pixelworks.com>
#
# Main command entry for WeChat bot
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

import os, sys, re, shlex
import configparser
import itchat

from threading import Thread

from itchat.content import *

# Config options resides in [DEFAULT] section
_config_opts = [
    {
        u'name': u'job_package',
        u'default': u'wechatbot',
        u'description': u'The package that contains all job sub-package and action modules.'
    }
]

# The config values for all jobs and actions
# Should be loaded in run()
_config = None

def _build_config(pkg_name):
    """Build package config options"""

    global _config

    # Get top-most package name
    pkg_name_parts = pkg_name.split(u'.')
    top_pkg_name = pkg_name_parts[0]
    # Import the top-most package first
    top_pkg = __import__(top_pkg_name)
    # Get the top-most package path
    this_pkg_fullpath = os.path.dirname(top_pkg.__file__)
    #If we have more sub package names
    if len(pkg_name_parts) > 1:
        this_pkg_fullpath += os.path.sep + os.path.sep.join(pkg_name_parts[1:])

    # Going through the package path
    for anything in os.listdir(this_pkg_fullpath):
        # Ignore anything start with "__"
        if re.findall(u'^__.+', anything):
            continue
        # Ignore anything start with "."
        if re.findall(u'^\..*', anything):
            continue

        if os.path.isdir(os.path.join(this_pkg_fullpath, anything)):
            # If anything is dir, dive in.
            _build_config(u'.'.join([pkg_name, anything]))
        else:
            # If anything is file, then import as module and deal with config opts
            ## Get the module name
            module_name = re.sub(u'\.py$', u'', anything)
            ## Import the module
            this_module = __import__(
                u'.'.join([pkg_name, module_name]),
                fromlist = [pkg_name]
            )
            ## Check if _config_opts is defined in module
            if (u'_config_opts' in dir(this_module)) and this_module._config_opts:
                ## Go on deal with config opts
                ### Section name first
                this_section_name = u'%s.%s' % (
                    pkg_name.replace(
                        _config[u'DEFAULT'][u'job_package'],
                        u'DEFAULT'
                    ),
                    module_name
                )
                if len(pkg_name_parts) > 1:
                    this_section_name = this_section_name.replace(
                        u'DEFAULT.', u''
                    )
                ### Add the section if not exist
                if not _config.has_section(this_section_name):
                    _config.add_section(this_section_name)
                ### Loop through all config opts, set if not exits
                for conf_opt in this_module._config_opts:
                    if (u'name' not in conf_opt.keys()) or (u'default' not in conf_opt.keys()):
                        ### If name or default not defined, skip
                        continue
                    if not _config.has_option(this_section_name, conf_opt[u'name']):
                        ### A specific option not exist, we add it
                        if u'description' in conf_opt.keys():
                            ### First add comment (description) if defined
                            _config.set(this_section_name, u'; %s' % (conf_opt[u'description']), u'')
                        ### Then add the option with default value
                        _config.set(this_section_name, conf_opt[u'name'], conf_opt[u'default'])


class RunModuleError(Exception):
    """Base class for exceptions when loading and running module."""
    pass

def _run_module(module_path, from_path, msg = None, args = []):
    """Dynamic load module and run module.run()"""
    global _config

    msg_result = u''
    target_module = None

    # Generate config section name for target_module
    target_section = module_path.replace(
        u'%s.' % (_config[u'DEFAULT'][u'job_package']),
        u''
    )
    if len(target_section.split(u'.')) == 1:
        target_section = u'DEFAULT.%s' % (target_section)

    # Do import
    try:
        target_module = __import__(module_path, fromlist = [from_path])
    except:
        print(u"Cannot import %s." % (module_path), file = sys.stderr)
        raise RunModuleError(u"Job failed (import error).", 1)

    # Use a context dict to include msg object and config dict
    context = {}
    context[u'msg'] = msg
    context[u'config'] = _config[target_section]

    # Run job
    try:
        if args:
            msg_result = target_module.run(context, *args)
        else:
            msg_result = target_module.run(context)
    except:
        print(u"Cannot run job %s.run()" % (module_path), file = sys.stderr)
        raise RunModuleError(u"Job failed (run error).", 2)

    return msg_result

def run_job_action(msg, is_group_chat = False):
    """Do requested job action"""

    # If in group chat, must be at@
    if is_group_chat and (not msg.isAt):
        print(u"Ignore not At(@) messasges in group chat", file = sys.stderr)
        return

    # Make _config is referenced as a global var
    global _config

    # Reply to
    reply_to = msg[u'User'].NickName
    if is_group_chat:
        reply_to = msg[u'ActualNickName']

    # Some default vars
    job_pkg = _config[u'DEFAULT'][u'job_package']
    module_path = u''
    from_path = u''
    action_args = []
    msg_job = u''

    # Different message parts limit whether 1 to 1 chat or group chat
    n_job_msg = 1
    n_action_msg = 2
    if is_group_chat:
        n_job_msg = 2
        n_action_msg = 3

    # Split message

    ## Replace some special characters
    msg_buff = msg[u'Content'].replace(u'\u2005', ' ') # FOUR-PER-EM SPACE
    msg_buff = msg_buff.replace(u'\u201c', '"') # LEFT DOUBLE QUOTATION MARK
    msg_buff = msg_buff.replace(u'\u201d', '"') # RIGHT DOUBLE QUOTATION MARK
    msg_buff = msg_buff.replace(u'\u2018', '\'') # LEFT SINGLE QUOTATION MARK
    msg_buff = msg_buff.replace(u'\u2019', '\'') # RIGHT SINGLE QUOTATION MARK
    ## // ##

    msg_texts = shlex.split(msg_buff)
    #msg_texts = re.compile('\s+').split(msg[u'Content'])

    # Remove all empty strings
    msg_texts = list(filter(None, msg_texts))

    # No job word
    if len(msg_texts) < n_job_msg:
        if is_group_chat:
            msg.user.send(u'@%s\u2005Job not specified.' % (reply_to))
        else:
            msg.user.send(u'Job not specified.')
        return

    # msg_texts index definition
    # [1] : primary module name under namespace "wechatbot", required, called "Job"
    # [2] : if exists, secondary module name under primary module, called "Action"
    # [3:] : all as arguments
    if len(msg_texts) < n_action_msg:
        # Only job word specified
        module_path = u'%s.%s' % (job_pkg, msg_texts[n_action_msg - 2].lower())
        from_path = job_pkg
    else:
        # Job and Action and maybe arguments specified
        module_path = u'%s.%s.%s' % (job_pkg, msg_texts[n_action_msg - 2].lower(), msg_texts[n_action_msg - 1].lower())
        from_path = u'%s.%s' % (job_pkg, msg_texts[n_action_msg - 2].lower())
        # If we have more than 3 items, then we have arguments
        if len(msg_texts) > n_action_msg:
            action_args = msg_texts[n_action_msg:]

    try:
        msg_job = _run_module(module_path, from_path, msg, action_args)
    except RunModuleError as err:
        msg_job = err.args[0]
        msg_job += u'\nTo get more help, try:\n'
        if len(msg_texts) < n_action_msg:
            if err.args[1] == 2:
                """If run error"""
                if is_group_chat:
                    msg_job += u'@%s\u2005%s help' % (msg[u'User'].Self.DisplayName, module_path.rsplit(u'.')[-1])
                else:
                    msg_job += u'%s help' % (module_path.rsplit(u'.')[-1])
            else:
                if is_group_chat:
                    msg_job += u'@%s\u2005help' % (msg[u'User'].Self.DisplayName)
                else:
                    msg_job += u'help'
        else:
            if is_group_chat:
                msg_job += u'@%s\u2005%s help' % (msg[u'User'].Self.DisplayName, from_path.rsplit(u'.')[-1])
            else:
                msg_job += u'%s help' % (from_path.rsplit(u'.')[-1])
    except:
        msg_job = u"Unknown error."

    # Reply
    if is_group_chat:
        msg.user.send(u'@%s\u2005%s' % (reply_to, msg_job))
    else:
        msg.user.send(msg_job)

# itchat Message registers

@itchat.msg_register(TEXT)
def reply_text(msg):
    """Handle message from a 1 to 1 chat"""
    # Running in thread
    job_thread = Thread(
        target = run_job_action,
        args = (msg, False)
    )
    job_thread.setDaemon(True)
    job_thread.start()

@itchat.msg_register(TEXT, isGroupChat = True)
def reply_text_group(msg):
    """Handle message from group chat"""
    if msg.isAt:
        # Running in thread
        job_thread = Thread(
            target = run_job_action,
            args = (msg, True)
        )
        job_thread.setDaemon(True)
        job_thread.start()

@itchat.msg_register([MAP, CARD, NOTE, SHARING, PICTURE, RECORDING, ATTACHMENT, VIDEO, FRIENDS])
def not_supported(msg):
    """We will not handle these types of messages"""
    msg_not_supported = u"%s is not supported." % (msg.type)
    msg.user.send(msg_not_supported)

# // #

def run():
    file_login_status = u'%s/.wechatbot_login_status' % (os.path.expanduser(u'~'))
    file_config = u'%s/.wechatbotrc' % (os.path.expanduser(u'~'))

    # try:
    print(u"Rebuilding config file ...")

    # Make sure these config vars are referenced as global var
    global _config
    global _config_opts

    # Re-build config file
    _config = configparser.ConfigParser()
    # If config file exists, read in first
    if os.path.isfile(file_config):
        _config.read(file_config)
    ## [DEFAULT] section
    for conf_opt in _config_opts:
        ## Loop through all config options to rebuild the config file
        if (u'name' not in conf_opt.keys()) or (u'default' not in conf_opt.keys()):
            ## If name or default not defined, skip
            continue
        if not _config.has_option(None, conf_opt[u'name']):
            ## A specific option not exist, we add it
            if u'description' in conf_opt.keys():
                ## First add comment (description) if defined
                _config.set(u'DEFAULT', u'; %s' % (conf_opt[u'description']), u'')
            ## Then add the option with default value
            _config.set(u'DEFAULT', conf_opt[u'name'], conf_opt[u'default'])

    # Go through all modules and packages and build the config structure
    _build_config(_config[u'DEFAULT'][u'job_package'])

    # Save config file
    with open(file_config, 'w') as configfile:
        _config.write(configfile)

    # Login WeChat and run
    itchat.auto_login(
        enableCmdQR = 2,
        hotReload = True,
        statusStorageDir = file_login_status
    )

    itchat.run()
    # except:
    #     print(u"Some error. Debug code.", file = sys.stderr)