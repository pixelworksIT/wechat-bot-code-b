import setuptools

with open("README.md", "r") as fh:
    long_description = fh.read()

setuptools.setup(
    name = "wechatbot",
    version = "0.0.1",
    author = "HouYu Li",
    author_email = "hyli@pixelworks.com",
    description = "WeChat bot job modules and actions.",
    long_description = long_description,
    long_description_content_type = "text/markdown",
    url = "https://github.com/pixelworksIT/wechatbot",
    license = "Apache Software License",
    packages=setuptools.find_packages(),
    #install_requires = ["wechatbothelper"],
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: Apache Software License",
        "Operating System :: OS Independent"
    ],
)