from setuptools import setup, find_packages

from mattermost_bot import get_version

install_requires = (
    'websocket-client>=0.22.0',
    'six>=1.10.0',
    'requests>=2.4.0',
)

excludes = (
    '*test*',
    '*local_settings*',
)

setup(
    name='mattermost_bot',
    version=get_version(),
    license='MIT',
    description='Simple bot for MatterMost',
    keywords="chat bot mattermost",
    long_description=open('README.md').read(),
    author="GoTLiuM InSPiRiT",
    author_email='gotlium@gmail.com',
    url='http://github.com/LPgenerator/mattermost_bot',
    platforms=['Any'],
    packages=find_packages(exclude=excludes),
    install_requires=install_requires,
    entry_points={
        'console_scripts': [
            'matterbot = mattermost_bot.cli:main',
        ],
    },
    classifiers=[
        'Development Status :: 5 - Production/Stable',
        'License :: OSI Approved :: GNU General Public License (GPL)',
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
