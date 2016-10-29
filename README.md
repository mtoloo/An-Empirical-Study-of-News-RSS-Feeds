# An-Empirical-Study-of-News-RSS-Feeds
Use of NoSQL Database for Handling Semi Structured Data: An Empirical Study of News RSS Feeds

**Requirements**

This project requires the following packages to be installed on your OS (preferably on linux-debian-8)

    python 2.7
    mysql-server
    mongodb
    python-dev
    python-tk

Also the following modules of python are required to be installed:

    feedparser
    MySQLdb
    pymongo

**Installing**

For MySQLdb python module to be installed on Linux, you have to had `libmysqlclient-dev` to be installed at first:

    apt-get install libmysqlclient-dev

Then using `pip` command, you have to be able to install all required modules:

    pip install MySQLdb
    pip install feedparser
    pip install pymongo

Take a look a config.py file and make necessary changes.
Also Database specified in config.py should be created.
