from distutils.core import setup

from zabby import __version__

setup(
    name='zabby',
    version=__version__,
    packages=['zabby', 'zabby.core', 'zabby.tests'],
    url='https://github.com/blin/zabby',
    license='MIT',
    author='blin',
    author_email='blin@f4oe.org',
    description='This is a fork of zabbix agent to python',
    scripts=['bin/zabby'],
    classifiers=[
        'Development Status :: 1 - Planning',
        'Topic :: System :: Monitoring',
        'Intended Audience :: System Administrators',
        'Programming Language :: Python :: 2',
        'Programming Language :: Python :: 2.6',
        'Programming Language :: Python :: 2.7',
        'Programming Language :: Python :: 3',
        'Programming Language :: Python :: 3.1',
        'Programming Language :: Python :: 3.2',
        'Programming Language :: Python :: 3.3',
        'Operating System :: POSIX :: Linux',
        'License :: OSI Approved :: MIT License',
    ]
)
