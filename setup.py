from setuptools import setup, find_packages

setup(
    name='pcm',
    version='0.1',
    install_requires=['Click'],
    entry_points={'console_scripts': ['pcm=pcm.__main__:cli']}
)
