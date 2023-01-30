import setuptools

with open('readme.md') as fh:
    long_description = fh.read()

setuptools.setup(
    name='md.persistence.yaml',
    version='0.1.0',
    description='Provides implementation for persisted runtime data, using YAML format',
    long_description=long_description,
    long_description_content_type='text/markdown',
    license='License :: OSI Approved :: MIT License',
    package_dir={'': 'lib'},
    py_modules=['md.persistence.yaml'],
    install_requires=['md.python.dict==1.*', 'md.persistence==0.*'],
    dependency_links=[
        'https://source.md.land/python/md-python-dict/'
        'https://source.md.land/python/md-persistence/'
    ],
    classifiers=[
        'Programming Language :: Python :: 3',
        'License :: OSI Approved :: MIT License',
        'Operating System :: OS Independent',
    ],
    python_requires='>=3.6',
)
