## 0.1.2 ... 2019-11-19 05:44:14

 * Correct version check in test_zdeploy() (was checking against tbx
   version)
 * Trigger another travis build for the version tag

## 0.1.1 ... 2019-11-19 05:22:09

 * Add tests and payload for 'fx version'
 * Tweaks to .travis.yml to test tagged versions

## 0.1.0 ... 2019-11-18 16:11:43

 * Drop GitPython since tbx provides the functionality needed.
 * Support command line access to fx with fx/__main__.py, rewritten to use
   docopt-dispatch.
 * Update requirements.txt.
 * Skip past unused tags 0.0.5 through 0.0.8.


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
