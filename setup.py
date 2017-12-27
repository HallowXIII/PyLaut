from setuptools import setup, find_packages
from os import path

here = path.abspath(path.dirname(__file__))

# Get the long description from the README file
with open(path.join(here, 'README.md'), encoding='utf-8') as f:
    long_description = f.read()

setup(
    name='PyLaut',

    #Using semver
    version='0.1.0',

    description='A Python package to aid in computer-assisted conlanging',
    long_description=long_description,

    url='https://github.com/HallowXIII/PyLaut',

    author='Isaac "HallowXIII" Milton and Robert "Pthagnar" Williams',
    author_email='zephyrnox@gmail.com',

    license='MIT',

    # See https://pypi.python.org/pypi?%3Aaction=list_classifiers
    classifiers=[
        'Development Status :: 2 - Pre-Alpha',

        'Intended Audience :: Other Audience',
        'Topic :: Text Processing :: Linguistic',

        'License :: OSI Approved :: MIT License',

        'Programming Language :: Python :: 3',
        'Programming Language :: Python :: 3.3',
        'Programming Language :: Python :: 3.4',
        'Programming Language :: Python :: 3.5',
    ],

    keywords='linguistics diachrony conlanging',

    # You can just specify the packages manually here if your project is
    # simple. Or you can use find_packages().
    packages=find_packages(),

    # If there are data files included in your packages that need to be
    # have to be included in MANIFEST.in as well.
    package_data={'pylaut': ['data/monophone', 'data/monophone_ipa',
                             'data/monophone_ipa_diacritics',
                             'data/phoible-segf', 'data/phoible-segf_ipa']
    },

    #dependencies for the package
    install_requires = [
        'lark-parser'
    ]

)
