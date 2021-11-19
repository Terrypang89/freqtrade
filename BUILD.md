# freqtrade Build on raspberry pi Ubuntu-21 with Python 3.9.7 

# [Update on 19-11-2021](https://www.freqtrade.io/en/stable/installation/)

update repository
- [X] sudo apt-get update

install packages
- [X] sudo apt install -y python3-pip python3-venv python3-dev python3-pandas git curl gcc libhdf5-serial-dev

Download `develop` branch of freqtrade repository
- [X] git clone https://github.com/freqtrade/freqtrade.git

Enter downloaded directory
- [X] cd freqtrade

switch branch (1): novice user
- [X] git checkout stable

switch branch (2): advanced user
- [X] git checkout develop

install, Install freqtrade from scratch
- [X] ./setup.sh -i

# Error solving:

(If meet error on during ./setup -i)

[Building wheel for py-find-1st (PEP 517) ... error
  ERROR: Command errored out with exit status 1:
   command: /home/henk/.env/bin/python3 /home/henk/.env/lib/python3.8/site-packages/pip/_vendor/pep517/_in_process.py build_wheel /tmp/tmpzdpaxmq1
       cwd: /tmp/pip-install-n9a4m062/py-find-1st
  Complete output (18 lines)](https://giters.com/freqtrade/freqtrade/issues/5321)
- [X] sudo apt-get install -y libhdf5-serial-dev


(If manual install ta-lib)

[: ta-lib configure: error: cannot guess build type; you must specify one](https://github.com/mrjbq7/ta-lib/issues/222)
- [X] wget 'http://git.savannah.gnu.org/gitweb/?p=config.git;a=blob_plain;f=config.guess;hb=HEAD' -O config.guess
- [X] wget 'http://git.savannah.gnu.org/gitweb/?p=config.git;a=blob_plain;f=config.sub;hb=HEAD' -O config.sub
