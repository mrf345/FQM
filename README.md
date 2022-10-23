<p align='center'>
<img width='20%' src='https://fqms.github.io/images/favicon.png' />
</p>

<p align='center'>
<a href='https://github.com/mrf345/FQM/actions/workflows/ci.yml'>
  <img src='https://github.com/mrf345/FQM/workflows/Build/badge.svg'>
</a>
<a href='https://github.com/mrf345/FQM/releases'>
  <img src='https://img.shields.io/github/v/release/mrf345/FQM.svg' alt='release'>
</a>
</p>

<p align='center'>
<a href='https://github.com/mrf345/FQM/actions/workflows/ci.yml'>
  <img src='https://img.shields.io/endpoint?url=https://gist.githubusercontent.com/mrf345/bc746d7bfe356b54fbb93b2ea5d0d2a4/raw/FQM__heads_master.json' alt='Coverage Percentage' />
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

#### - From the source:

- Docker setup for production, follow this [guide](./docs/setup.md#1-docker-setup)
- Standard python setup (legacy), follow this [guide](./docs/setup.md#2-standard-python-setup)

#### - With executable [no longer supported]:

You can find an executable that's suitable to your OS from :

- [FQMS](https://fqms.github.io/#download)
- [Github Release](https://github.com/mrf345/FQM/releases/)
- [Sourceforge](https://sourceforge.net/projects/free-queue-manager/)


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
