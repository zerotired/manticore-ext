#!/usr/bin/env python
from setuptools import setup, find_packages
setup(
    name='zt.manticore.ext',
    version='0.1.2',
    url='https://github.com/zerotired/manticore-ext',
    download_url='',
    license='BSD',
    author='Andreas Motl',
    author_email='a.motl@zerotired.com',
    description='Python documentation generator based on Sphinx',
    long_desc='',
    zip_safe=False,
    classifiers=[
        'Development Status :: 4 - Beta',
        'Environment :: Console',
        'Environment :: Web Environment',
        'Intended Audience :: Developers',
        'License :: OSI Approved :: BSD License',
        'Operating System :: OS Independent',
        'Programming Language :: Python',
        'Programming Language :: Python :: 2',
        'Topic :: Documentation',
        'Topic :: Text Processing',
        'Topic :: Utilities',
        ],
    platforms='any',
    packages=find_packages('src'),
    include_package_data=True,
    package_dir={'': 'src'},
    namespace_packages=['zt'],
    entry_points = {
        'console_scripts': [
            'be = libbe.ui.command_line:main',
            'bugseverywhere-html = zt.manticore.ext.bugseverywhere:build_html',
            'changes-aggregate = zt.manticore.ext.changes:aggregate',
            'statistics-build = zt.manticore.ext.statistics:build_statistics',
            'gource-render-all = zt.manticore.ext.gource:render_all',
            'gource-render-single = zt.manticore.ext.gource:render_single',
            'laig = zt.manticore.ext.laig:run',
        ],
    },
    extras_require=dict(
        test=[],
    ),
    install_requires=[
        'setuptools',
        'Sphinx',
        'docutils',
        'PyYAML',
        'Bugs-Everywhere',
    ]
)
