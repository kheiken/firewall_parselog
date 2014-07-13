Parse logfiles and store them in SQLite/MySQL
=============================================

Using Vagrant
-------------

Run `vagrant up`.

Visit http://127.0.0.1:8084 to manage the database and view entries.
The username for MySQL is root, there is no password.

To add a new log file:

```sh
$ vagrant up
$ vagrant ssh
$ cd /vagrant
$ ./parselog.py <logfile>
```

Local usage
-----------

### Requirements

 * Python 3 (Debian: python3, Arch Linux: python)
 * Pip (Debian: python3-pip, Arch Linux: python-pip)


### Installation

Run `pip3 install -r requirements.txt` to install the required Python packages.

### Configuration

Set `DATABASE_DSN` to your suit your needs.

### Usage

Run `./parselog.py <logfile>` to parse a log file. Duh.