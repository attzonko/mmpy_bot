from setuptools import find_packages, setup

excludes = (
    "*test*",
    "*local_settings*",
)


def requires(filename: str):
    return open(filename).read().splitlines()


setup(
    name="mmpy_bot",
    version="2.0.0",
    author="Alex Tzonkov",
    author_email="alex.tzonkov@gmail.com",
    license="MIT",
    description="A python based bot for Mattermost with its own webhook server.",
    keywords="chat bot mattermost",
    long_description=open("README.md").read(),
    long_description_content_type="text/markdown",
    url="https://github.com/attzonko/mmpy_bot",
    python_requires=">=3.8",
    platforms=["Any"],
    packages=find_packages(exclude=excludes),
    install_requires=requires("requirements.txt"),
    extras_require={"dev": requires("dev-requirements.txt")},
    entry_points={
        "console_scripts": [
            "mmpy_bot = mmpy_bot.cli:main",
        ],
    },
    classifiers=[
        "Development Status :: 5 - Production/Stable",
        "License :: OSI Approved :: MIT License",
        "Intended Audience :: Developers",
        "Operating System :: OS Independent",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3.9",
        "Topic :: Internet :: WWW/HTTP",
        "Topic :: Software Development :: Libraries :: Python Modules",
    ],
)
