from distutils.core import setup

setup(
    name='metraapi',
    version='0.2.0',
    author='Ian Dees, Eric Stein',
    author_email='toba@des.truct.org',
    packages=['metraapi'],
    package_data={
        '': ['*.csv', '*.zip'],
    },
    url='https://github.com/eastein/metraapi',
    license='LICENSE',
    description='Wrapper for the Metra real time arrivals data.',
    long_description=open('README.md').read(),
    install_requires=[
        'requests>=2.7.0',
        'pytz',
        'six'
    ]
)
