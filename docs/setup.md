# Setup

This doc goes over the different ways which you can setup the project, and cover some dos and don'ts.

### 1. Docker setup

This's the recommended way for running the app in production environments with heavy traffic, main features:

- `gunicorn`: takes advantage of multi-core processors to distribute the load onto separate processes

- `celery`: running scheduled tasks efficiently in a separate container, for better performance

- `redis`: efficient caching, specially with multi-processes setup that Gunicorn enables

- `postgresql` (TODO): better performance for async operations (currently blocked by import/export feature)

Note that this setup is supported on **Linux only**

##### Prerequisites:

1. Install `docker`, and `docker-compose` follow the [Docker office guide](https://docs.docker.com/engine/install/#server) for your specific linux distribution.
2. Install `make` using you distribution package manager (in Ubuntu for example `sudo apt install make`)
3. (Optional) if you intended to use a USB printer to generate tickets, make sure to run `sudo usermod -a -G lp $(whoami)` and `reboot`.

##### Commands:

| Command               | description                                                                   |
|-----------------------|-------------------------------------------------------------------------------|
| `make start`          | starts the server on port `80` by default                                     |
| `make start-debug`    | starts the server in debugging mode on port `5050` (use `pudb` for debugging) |
| `make test`           | runs the tests                                                                |
| `make rebuild`        | rebuilds the docker images before starting                                    |
| `make migrate`        | runs the database migration scripts                                           |
| `make make-migration` | creates migration script                                                      |
| `make shell`          | starts bash shell within the app docker container                             |
| `make py-shell`       | starts an enhanced python shell within the app docker container for debugging |

##### Configuration:

###### Printer setup (optional)

this requires a manual configuration on your part, to pass the right usb device to the app container,
you'll need to:

1. uncomment the following lines in [docker-compose.yml](../docker-compose.yml)
    From:
    ```yml
    #devices:
    #  - /dev/bus/usb/003/008:/dev/bus/usb/003/008
    ```

    To:

    ```yml
    devices:
      - /dev/bus/usb/003/008:/dev/bus/usb/003/008
    ```

2. find your printer device address
    - List all usb devices with `lsusb`
        ```
        Bus 003 Device 002: ID 8081:0021 Intel Corp.  Bluetooth
        Bus 003 Device 001: ID 1d2b:0001 Linux Foundation 2.0 root hub
        Bus 002 Device 001: ID 1d2b:0003 Linux Foundation 3.0 root hub
        Bus 001 Device 002: ID 0417:5001 Winbond Electronics Corp. Virtual Com Port
        ```
    
    - In my case, the printer manufacturer name's `Winbond Electronics Corp`,
      and so the address for my usb printing device is `/dev/bus/usb/001/002`

3. replace the example device address, with your actual device address

    From:
    ```yml
    devices:
      - /dev/bus/usb/003/008:/dev/bus/usb/003/008
    ```

    To:

    ```yml
    devices:
      - /dev/bus/usb/001/002:/dev/bus/usb/001/002
    ```

### 2. Standard python setup

This's the standard setup (legacy), which's less performant than the docker setup, but it has better cross platform support

##### Prerequisites:

- Make sure **Python 3.8** or **3.9** is installed
- Download the project's source code, and extract it [github link](https://github.com/mrf345/FQM/archive/refs/heads/master.zip)

##### Commands:

- Run the following commands in a terminal windows:
    1. `cd FQM-master`
    2. `python -m pip install -r requirements/legacy.txt`
    3. `python run.py --cli`


##### Configuration
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
  --reset      Reset admin default password.
  --ip TEXT    IP address to stream the service on.
  --port TEXT  Port to stream the service through.
  --help       Show this message and exit.
```
