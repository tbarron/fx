from fx import version
try:
    from setuptools import setup
except ImportError:
    from distutils.core import setup

setup(
    name="fx",
    description='Command line special effects',
    version=version.__version__,
    author="Tom Barron",
    author_email="tusculum@gmail.com",
    packages=['fx'],
    scripts=[],
)
