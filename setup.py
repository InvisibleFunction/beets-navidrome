from setuptools import setup, find_packages

setup(
    name='beets-navidrome',
    version='0.0.1',
    description='beets plugin for Navidrome',
    long_description=open('README.md').read(),
    long_description_content_type="text/markdown",
    url='https://github.com/InvisibleFunction/beets-navidrome',
    license='MIT',
    platforms='ALL',
    packages=['beetsplug'],
    namespace_packages=['beetsplug'],
    install_requires=[
        'beets>=2.4.0',
        'requests'
    ],
    python_requires=">=3.11",
)
