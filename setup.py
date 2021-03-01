from setuptools import find_packages, setup

from mmpy_bot import __version__


def requires(filename: str):
    return open(filename).read().splitlines()


excludes = (
    "*test*",
    "*local_settings*",
)

setup(
    name="mmpy_bot",
    version=__version__,
    author="Alex Tzonkov",
    author_email="alex.tzonkov@gmail.com",
    license="MIT",
    description="A python based bot for Mattermost with its own webhook server.",
    keywords="chat bot mattermost",
    long_description=open("README.md").read(),
    long_description_content_type="text/markdown",
    url="https://github.com/attzonko/mmpy_bot",
    platforms=["Any"],
    packages=find_packages(exclude=excludes),
    install_requires=requires("requirements.txt"),
    extras_require={"dev": requires("dev-requirements.txt")},
    classifiers=[
        "Development Status :: 5 - Production/Stable",
        "License :: OSI Approved :: MIT License",
        "Intended Audience :: Developers",
        "Operating System :: OS Independent",
        "Programming Language :: Python :: 3.6",
        "Programming Language :: Python :: 3.7",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3.9",
        "Topic :: Internet :: WWW/HTTP",
        "Topic :: Software Development :: Libraries :: Python Modules",
    ],
)
