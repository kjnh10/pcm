from setuptools import setup, find_packages

setup(
    name='pcm',
    version='0.4.0',
    description="tiny programing contest manager",
    author='kjnh10',
    author_email='kojinho10@gmail.com',
    url='https://github.com/kjnh10/pcm',
    packages=find_packages(),
    include_package_data=True,
    install_requires=['Click>=7.0', 'online-judge-tools>=7.1.0', 'toml'],
    entry_points={'console_scripts': ['pcm=pcm.__main__:cli']},
    python_requires='>=3.5',
)
