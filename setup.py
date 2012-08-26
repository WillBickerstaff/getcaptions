#!/usr/bin/env python

from distutils.core import setup

setup(name='getcaptions',
      version='0.1.0',
      description='Utility to download video captions',
      long_description=('A utility that locates playlists on youtube, '
                        'and downloads captions for all videos in the list. '
                        'The caption language can be selected and the output '
                        'is converted to markdown.'),
      author='Will Bickerstaff',
      author_email='will.bickerstaff@gmail.com',
      url='https://github.com/WillBickerstaff/pyPlaylistCap',
      packages=['lib', 'lib.yt'],
      scripts=['bin/getcaptions'],
      license='MIT License',
      classifiers=['Development Status :: 4 - Beta',
                   'Environment :: X11 Applications',
                   'Programming Language :: Python :: 2.7',
                   'License :: OSI Approved :: MIT License',
                   'Natural Language :: English',
                   'Topic :: Multimedia :: Video',
                   'Topic :: Text Processing :: Markup',
                   'Intended Audience :: End Users/Desktop',
                   'Intended Audience :: Education']
     )
