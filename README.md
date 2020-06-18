<p align='center'>
<img width='20%' src='https://fqms.github.io/images/favicon.png' />
</p>

<p align='center'>
<a href='https://travis-ci.org/mrf345/FQM'>
  <img src='https://travis-ci.org/mrf345/FQM.svg?branch=master'>
</a>
<a href='https://github.com/mrf345/FQM/releases'>
  <img src='https://img.shields.io/github/v/release/mrf345/FQM.svg' alt='release'>
</a>
</p>

<p align='center'>
<a href='https://coveralls.io/github/mrf345/FQM?branch=master'>
  <img src='https://coveralls.io/repos/github/mrf345/FQM/badge.svg?branch=master' alt='Coverage Status' />
</a>
<a href='https://www.python.org/dev/peps/pep-0008/'>
  <img src='https://img.shields.io/badge/code%20style-PEP8-orange.svg' alt='Code Style PEP8' />
</a>
<a href='https://github.com/mrf345/FQM/issues?q=is%3Aissue+is%3Aclosed'>
  <img alt="GitHub closed issues" src="https://img.shields.io/github/issues-closed/mrf345/FQM">
</a>
</p>

<h3 align='center'> Free Queue Manager (beta). A web based queue management system built with Python Flask, Bootstrap and jQuery. </h3>
<hr />


### Features:
- Support for POS USB printers on major operating systems.
- Customize-able interfaces.
- Supports text-to-speech announcement.

### Setup:

#### - With executable:
You can find an executable that's suitable to your OS from :

- [FQMS](https://fqms.github.io/#download)
- [Github Release](https://github.com/mrf345/FQM/releases/)
- [Sourceforge](https://sourceforge.net/projects/free-queue-manager/)


#### - From the source:
- Make sure to install and use **Python 3.7** or **3.8**
- Execute the following commands in a terminal window:
1. `git clone https://github.com/mrf345/FQM.git`
2. `cd FQM`
3. `python -m pip install -r requirements/deploy.txt`
4. `python run.py --cli`

- To checkout the supported command-line options `python run.py --help`:
```bash
Usage: run.py [OPTIONS]

  FQM command-line interface (CLI):

  * If `--cli` is not used, initializing GUI will be attempted.

  * If no `ip` is passed it will default to `127.0.0.1`.

  * If no `port` is passed it will default to a random port.

Options:
  --cli        To use commandline interface instead of GUI.
  --quiet      To silence web server logs.
  --ip TEXT    IP address to stream the service on.
  --port TEXT  Port to stream the service through.
  --help       Show this message and exit.
```


#### - For development on Linux\MacOS:
- Make sure to install and use **Python 3.7**
- Execute the following commands in a terminal window:
1. `chmod +x installer.sh`
2. `./installer.sh --install`
3. `./installer.sh --run`

- To checkout the supported command-line options `./installer.sh --help`:
```bash
./installer.sh --help: Examples

    ./installer.sh --install        to install packages required
    ./installer.sh --uninstall      to remove packages installed
    ./installer.sh --run            to run FQM
    ./installer.sh --test           to run FQM tests
    ./installer.sh --migration      to run FQM migration
    ./installer.sh --help           to print out this message
```

#### - Database migration:
Since the `0.7` release we're able to migrate the data generated in previous releases to the new ones.

- You'll have to copy the `data.sqlite` file from the main project folder to the new release project folder.
- If you've uploaded any `Multimedia` files to your previous setup, make sure to copy them over to the new project folder manually from and to `FQM/static/multimedia/` folder.

**Make sure the migration steps are performed prior to running the new release of the system**.

### Documentation:
- [Useful but very outdated user guide](https://fqms.github.io/images/user_guide.pdf).
- [How do i add support for my language ?](docs/localization.md)
- [How do i add additional settings and customizations ?](docs/settings.md)


<br />
<p align='center'>
<img width='70%' src='https://fqms.github.io/images/logo.gif' />
</p>
