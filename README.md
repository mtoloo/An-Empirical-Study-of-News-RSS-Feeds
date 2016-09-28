# An-Empirical-Study-of-News-RSS-Feeds
Use of NoSQL Database for Handling Semi Structured Data: An Empirical Study of News RSS Feeds

**Requirements**
This project requires the following packages to be installed on your OS (preferably on linux-debian-8)

    python 2.7
    mysql-server
    mongodb

Also the following modules of python are required:

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

**How it works**
You have to create databases using `db.py` file. It contains two main method `init_mysql()` and `init_mongodb()` which have to be called first.
Then call `RSS.store_sites_rss()` from `rss.py` to load rss entries from a list of news sites into .json files under the `data` directory.
After completing .json files under the `data` directory, 