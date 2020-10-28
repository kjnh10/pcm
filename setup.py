from setuptools import setup, find_packages

setup(
    name='pcm',
    use_scm_version=True,
    setup_requires=[
        "setuptools_scm"
    ],
    description="tiny programing contest manager",
    author='kjnh10',
    author_email='kojinho10@gmail.com',
    url='https://github.com/kjnh10/pcm',
    packages=find_packages(),
    include_package_data=True,
    install_requires=[
            'Click>=7.0',
            'online-judge-tools>=9.0.0',
            'online-judge-verify-helper',
            'toml',
            'pyside2',
            'pyperclip',
            ],
    entry_points={
        'console_scripts': ['pcm=pcm.__main__:cli', 'pcm-cc=pcm.cc_server.__main__:main']
    },
    python_requires='>=3.6',
    classifiers=[
        "Development Status :: 4 - Beta",
        "Environment :: Console",
        "Intended Audience :: Developers",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
        "Programming Language :: Python :: 3.7",
        "Programming Language :: Python :: 3.8",
        ],
)

