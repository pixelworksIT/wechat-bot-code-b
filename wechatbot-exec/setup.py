import setuptools

with open("README.md", "r") as fh:
    long_description = fh.read()

setuptools.setup(
    name = "wechatbotexec",
    version = "0.0.1",
    author = "HouYu Li",
    author_email = "hyli@pixelworks.com",
    description = "Python WeChat bot main process, based on itchat.",
    long_description = long_description,
    long_description_content_type = "text/markdown",
    url = "https://github.com/pixelworksIT/wechatbot-exec",
    license = "Apache Software License",
    packages=setuptools.find_packages(),
    #install_requires = ["itchat", "wechatbot", "wechatbothelper"],
    install_requires = ["itchat"],
    entry_points = {
        'console_scripts':[
            'wechatbotexec=wechatbotexec.command:run'
        ]
    },
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: Apache Software License",
        "Operating System :: OS Independent"
    ],
)