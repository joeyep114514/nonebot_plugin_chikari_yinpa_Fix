import setuptools

with open("README.md", "r", encoding='utf-8') as fh:
    long_description = fh.read()

setuptools.setup(
    name="nonebot-plugin-chikari-yinpa-fix",
    version="1.4.6",
    author="joeyep114514",
    author_email="joeyep114514@outlook.com",
    description="Fixed something by AI",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/mrqx0195/nonebot_plugin_chikari_yinpa",
    packages=setuptools.find_packages(),
    install_requires=[
        'Pillow',
        'nonebot2>=2.0.0',
        'nonebot-adapter-onebot',
        'nonebot-plugin-localstore',
    ],
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
)
