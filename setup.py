from setuptools import setup, find_packages

from mmpy_bot import get_version

install_requires = (
    'websocket-client>=0.22.0',
    'six>=1.10.0',
    'requests>=2.4.0',
    'schedule>=0.5.0',
)

excludes = (
    '*test*',
    '*local_settings*',
)

setup(
    name="mmpy_bot",
    version=get_version(),
    author="Alex Tzonkov",
    author_email="alex.tzonkov@gmail.com",
    license='MIT',
    description="A python based bot for Mattermost",
    keywords="chat bot mattermost",
    long_description=open('README.md').read(),
    long_description_content_type="text/markdown",
    url="https://github.com/attzonko/mmpy_bot",
    platforms=['Any'],
    packages=find_packages(exclude=excludes),
    install_requires=install_requires,
    entry_points={
        'console_scripts': [
            'mmpy_bot = mmpy_bot.cli:main',
        ],
    },
    classifiers=[
        'Development Status :: 5 - Production/Stable',
        "License :: OSI Approved :: MIT License",
        'Intended Audience :: Developers',
        'Operating System :: OS Independent',
        'Programming Language :: Python',
        'Programming Language :: Python :: 2',
        'Programming Language :: Python :: 2.7',
        'Programming Language :: Python :: 3',
        'Programming Language :: Python :: 3.4',
        'Programming Language :: Python :: 3.5',
        'Topic :: Internet :: WWW/HTTP',
        'Topic :: Software Development :: Libraries :: Python Modules',
    ]
)
