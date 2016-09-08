#!/usr/bin/env python
import setuptools


setuptools.setup(
    name='jarvis',
    version='2.0.0',
    description='A python slackbot',
    keywords='jarvis slack slackbot',
    author='Kevin James',
    author_email='KevinJames@thekev.in',
    url='https://github.com/TheKevJames/jarvis.git',
    license='MIT License',
    packages=setuptools.find_packages(),
    install_requires=['requests', 'slackclient'],
    classifiers=[
        'Programming Language :: Python',
        'Development Status :: 5 - Production/Stable',
        'Natural Language :: English',
        'Intended Audience :: End Users/Desktop',
        'License :: OSI Approved :: MIT License',
    ],
    entry_points={
        'console_scripts': [
            'jarvis = jarvis.entrypoint:run',
            'init = jarvis.entrypoint:init',
        ],
    },
)
