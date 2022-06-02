import setuptools
from codecs import open
from os import path

def get_requirements(remove_links=True):
    """
    lists the requirements to install.
    """
    try:
        with open('requirements.txt') as f:
            requirements = f.read().splitlines()
    except Exception as ex:
        with open('DecoraterBotUtils.egg-info\requires.txt') as f:
            requirements = f.read().splitlines()
    if remove_links:
        for requirement in requirements:
            # git repository url.
            if requirement.startswith("git+"):
                requirements.remove(requirement)
            # subversion repository url.
            if requirement.startswith("svn+"):
                requirements.remove(requirement)
            # mercurial repository url.
            if requirement.startswith("hg+"):
                requirements.remove(requirement)
    return requirements

here = path.abspath(path.dirname(__file__))

# Get the long description from the README file
with open(path.join(here, 'README.md'), encoding='utf-8') as f:
    long_description = f.read()

setuptools.setup(
    name='perdido',
    version='0.0.3',
    license='BSD-Clause-2',
    author='Ludovic Moncla',
    author_email='moncla.ludovic@gmail.com',
    description="PERDIDO Geoparser python library",
    long_description=long_description,
    long_description_content_type='text/markdown',
    url='https://github.com/ludovicmoncla/perdido',
    packages=setuptools.find_packages(),
    classifiers=[
         # How mature is this project? Common values are
         #   3 - Alpha
         #   4 - Beta
         #   5 - Production/Stable
         'Development Status :: 3 - Alpha',

         # Pick your license as you wish (should match "license" above)
         'License :: OSI Approved :: BSD License',

         'Operating System :: POSIX :: Other',
         'Operating System :: MacOS',

         'Programming Language :: Python :: 3',
    ],
    keywords='geoparsing named-entity-recognition geographic-information-retrieval toponym-resolution toponym-disambiguation',
    install_requires=get_requirements(),
)