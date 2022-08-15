#! /usr/bin/python

from distutils.core import setup
import glob


setup(name='memorize_flashcards',
    version='1.0',
    maintainer='Omer Dagan',
    maintainer_email='mr.omer.dagan@gmail.com',
    packages=["memorize_flashcards"],
    package_dir={'': "python"},
    data_files=[
    	('/usr/bin', glob.glob('tree/usr/bin/*')),
    	('/etc/memorize-flashcards', glob.glob('tree/etc/memorize-flashcards/*')),
    	('/etc/bash_completion.d', glob.glob('tree/etc/bash_completion.d/*')),
    ],
    license='GPL-3.0',
    long_description=open('README.txt').read(),
)
