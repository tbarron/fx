## 0.0.5 ...

 * Drop GitPython since tbx provides the functionality needed.
 * Support command line access to fx with fx/__main__.py, rewritten to use
   docopt-dispatch.
 * Update requirements.txt.


## 0.0.4 ... 2019-11-17 10:10:08

 * Mark strings containing escapes with 'r' to keep flake8 happy
 * Update requirements: pip 19.3.1 or better, tbx 1.1.6 or better, flake8,
   and pytest; re-install
 * Update .travis.yml to test on Python 3.8 and 3.6, drop 2.7 and to only
   test branch 'travis' and maj.min.micro versions


## 0.0.3 ... 2018.0112 14:30:34

 * New test to vet code quality using flake8


## 0.0.2 ... 2018.0112 08:17:51

 * Support arguments from stdin in 'fx -x ...' (xargs emulation)


## 0.0.1 ... 2018.0110 19:01:33

 * Basic functionality brought forward from backscratcher repo
