<p align='center'>
<img width='20%' src='https://fqms.github.io/images/favicon.png' />
</p>

<p align='center'>
<a href='https://travis-ci.com/mrf345/FQM'>
  <img src='https://travis-ci.com/mrf345/FQM.svg?branch=master'>
</a>
<a href='https://coveralls.io/github/mrf345/FQM?branch=master'>
  <img src='https://coveralls.io/repos/github/mrf345/FQM/badge.svg?branch=master' alt='Coverage Status' />
</a>
<img alt="GitHub closed issues" src="https://img.shields.io/github/issues-closed/mrf345/FQM">
<img alt="GitHub" src="https://img.shields.io/github/license/mrf345/FQM">
</p>

<h3 align='center'> Free Queue Manager (beta). A web based queue management system built with Python Flask as back-end, and Bootstrap, jQuery as front-end. </h3>
<hr />


## Features:
> - Support for POS USB printers on major operating systems. <br />
> - Customize-able interfaces. <br />
> - Supports text-to-speech announcement. <br />

## Setup:
#### - Using installer.sh for Linux, MacOS:
> - Execute the following commands in a terminal window
> 1. `chmod +x installer.sh`
> 2. `./installer.sh --install`
> 3. `./installer.sh --run`
> - If you want to remove the virtual environment and installed there dependencies
> 4. `./installer.sh --uninstall`

#### - From the source:
> - Execute the following commands in a terminal window
> 1. `git clone https://github.com/mrf345/FQM.git` <br />
> 2. `cd FQM` <br />
> - You can choose to use Python 3.7 or Python 3.8 <br />
> 3. `pip install -r requirements/dev.txt` <br />
> 4. `python run.py` <br />

> - To checkout the supported command-line options:
> 1. `python run.py --help` <br />

```bash
Usage: run.py [OPTIONS]

If no `ip` is passed it will default to `127.0.0.1`
If no `port` is passed it will default to a random port.

Options:
  --cli        To use command-line interface instead of GUI.
  --quiet      To silence web server logs.
  --ip TEXT    IP address to stream the service on.
  --port TEXT  Port to stream the service through.
  --help       Show this message and exit.
```

#### - With executable:
> You can get an executable that's suitable to your OS from : <br />
> - https://fqms.github.io/#download <br />
> - https://sourceforge.net/projects/free-queue-manager/ <br />

## Documentation:
> You can find a useful user guide for the current version on : <br />
> https://fqms.github.io/images/user_guide.pdf


<br />
<p align='center'>
<img width='70%' src='https://fqms.github.io/images/logo.gif' />
</p>
