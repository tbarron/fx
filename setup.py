from setuptools import setup

def execfile(fname, gdict, ldict):
    exec(compile(open(fname, 'rb').read(), fname, 'exec'),
         gdict,
         ldict)
execfile("./fx/version.py", globals(), locals())

setup(name="fx",
      version=__version__,
      author="Tom Barron",
      author_email="tusculum@gmail.com",
      entry_points={'console_scripts': ["fx = fx:main"]}
      )
