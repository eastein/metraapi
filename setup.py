from distutils.core import setup

setup(
    name='metraapi',
    version='0.1',
    author='Ian Dees',
    author_email='ian.dees@gmail.com',
    packages=['metraapi'],
    url='http://github.com/iandees/metraapi',
    license='LICENSE',
    description='Wrapper for the Metra real time arrivals data.',
    long_description=open('README.md').read(),
    install_requires=[
        'requests==1.2.3',
        'pytz'
    ]
)

