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
import itchat

from threading import Thread

from itchat.content import *

class RunModuleError(Exception):
    """Base class for exceptions when loading and running module."""
    pass

def _run_module(module_path, from_path, msg = None, args = []):
    """Dynamic load module and run module.run()"""

    msg_result = u''
    target_module = None

    # Do import
    try:
        target_module = __import__(module_path, fromlist = [from_path])
    except:
        print(u"Cannot import %s." % (module_path), file = sys.stderr)
        raise RunModuleError(u"Job failed (import error).", 1)

    # Run job
    try:
        if args:
            msg_result = target_module.run(msg, *args)
        else:
            msg_result = target_module.run(msg)
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

    # Reply to
    reply_to = msg[u'User'].NickName
    if is_group_chat:
        reply_to = msg[u'ActualNickName']

    # Some default vars
    job_module = u'wechatbot'
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
        module_path = u'%s.%s' % (job_module, msg_texts[n_action_msg - 2].lower())
        from_path = job_module
    else:
        # Job and Action and maybe arguments specified
        module_path = u'%s.%s.%s' % (job_module, msg_texts[n_action_msg - 2].lower(), msg_texts[n_action_msg - 1].lower())
        from_path = u'%s.%s' % (job_module, msg_texts[n_action_msg - 2].lower())
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

    try:
        itchat.auto_login(
            enableCmdQR = 2,
            hotReload = True,
            statusStorageDir = file_login_status
        )

        itchat.run()
    except:
        print(u"Some error. Debug code.", file = sys.stderr)