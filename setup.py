#!/usr/bin/env python
import setuptools


setuptools.setup(
    name='jarvis',
    use_scm_version=True,
    description='A python slackbot',
    keywords='jarvis slack slackbot',
    author='Kevin James',
    author_email='KevinJames@thekev.in',
    url='https://github.com/TheKevJames/jarvis.git',
    license='MIT License',
    packages=setuptools.find_packages(),
    install_requires=['requests', 'setuptools_scm', 'slackclient'],
    setup_requires=['pytest-runner', 'setuptools_scm'],
    tests_require=['pytest', 'pytest-cov', 'pytest-pep8'],
    classifiers=[
        'Programming Language :: Python',
        'Development Status :: 5 - Production/Stable',
        'Natural Language :: English',
        'Intended Audience :: End Users/Desktop',
        'License :: OSI Approved :: MIT License',
    ],
    entry_points={
        'console_scripts': [
            'jarvis-init = jarvis.entrypoint:init',
            'jarvis-run = jarvis.entrypoint:run',
            'jarvis-update = jarvis.entrypoint:update'
        ],
    },
)
