# wechat-bot-code-b

This is a framework of WeChat bot, based on [ItChat](https://github.com/littlecodersh/ItChat).

## Idea explained

The execute file `wechatbotexec` in package `wechatbot-exec` start the main process based on `ItChat`.

When recieving message from friend or being @ in group chat, it will take the first word as a module name or a sub-package name in package `wechatbot`, and the second word, if exists, as a module name in the package named by first word. Then it will dynamically load module and try to run `run(msg, *args)` function in that module.

The sub-package named by first word is called `Job`, while a module is called `Action`.

## The run logic

If only first word and no second word, run `wechatbot.1stword.run(msg, *args)`, otherwise run `wechatbot.1stword.2ndword.run(msg, *args)`. Any words after second word will be passed to `run(msg, *args)` as `*args`.

## Package explained

### wechatbot

This is the main package that should contain all real action codes.

The suggested package structure is:
```
wechatbot /
    |- __init__.py
    |- help.py
        |- def run(msg, *args): ...
    |- job (1st word) /
        |- __init__.py
        |- action.py (2nd word)
            |- def run(msg, *args): ...
            |- def help_desc(): ...
        |- help.py
            |- def run(msg, *args): ...
            |- def help_desc(): ...
```

You can use the default `sayhello` and `sayhello.greet` as an example to start your own jobs and actions.

### wechatbot-exec

This package provides the main process execute file `wechatbotexec`.

### wechatbot-helper

This package contains all other useful functions but should not mess up the main package codes.

## Setup

```
$ git clone https://github.com/pixelworksIT/wechat-bot-code-b.git
$ cd wechat-bot-code-b
$ virtualenv -p <path_of_python_bin> venv
$ . venv/bin/activate
$ cd wechatbot-helper
$ pip install .
$ cd ../wechatbot
$ pip install .
$ cd ../wechatbot-exec
$ pip install .
$ wechatbotexec
```
Use WeChat scan to login and try to send following message to the bot

`sayhello greet "Your Name" -n "Your Nickname"`