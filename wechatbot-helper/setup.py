import setuptools

with open("README.md", "r") as fh:
    long_description = fh.read()

setuptools.setup(
    name = "wechatbothelper",
    version = "0.0.1",
    author = "HouYu Li",
    author_email = "hyli@pixelworks.com",
    description = "Helper functions for Python WeChat bot.",
    long_description = long_description,
    long_description_content_type = "text/markdown",
    url = "https://github.com/pixelworksIT/wechat-bot-code-b",
    license = "Apache Software License",
    packages=setuptools.find_packages(),
    install_requires = [],
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: Apache Software License",
        "Operating System :: OS Independent"
    ],
)