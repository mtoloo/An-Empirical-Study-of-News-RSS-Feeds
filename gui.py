#!/usr/bin/python
# -*- coding: utf-8 -*-

"""
ZetCode Tkinter tutorial

This script shows a simple window
on the screen.

Author: Jan Bodnar
Last modified: November 2015
Website: www.zetcode.com
"""
import json
from Tkinter import Tk, Frame, BOTH, Button, RAISED, RIGHT, LEFT, Y, RIDGE, Label, W, Text, E, S, N, END
from ttk import Style

import time

from datetime import datetime, timedelta

from db import DB
from rss import RSS


class Example(Frame):
    def __init__(self, parent):
        Frame.__init__(self, parent)

        self.parent = parent

        self.init_ui()

    def init_ui(self):
        w = 700
        h = 400
        sw = self.parent.winfo_screenwidth()
        sh = self.parent.winfo_screenheight()
        x = (sw - w) / 2
        y = (sh - h) / 2
        self.parent.geometry('%dx%d+%d+%d' % (w, h, x, y))

        self.parent.title("An-Empirical-Study-of-News-RSS-Feeds")
        self.pack(fill=BOTH, expand=True)

        self.columnconfigure(1, weight=1)
        self.columnconfigure(5, pad=7)
        self.rowconfigure(3, weight=1)
        self.rowconfigure(5, pad=7)

        lbl = Label(self, text="Log")
        lbl.grid(sticky=S, pady=4, padx=5)

        self.area = Text(self)
        self.area.grid(row=1, column=0, columnspan=2, rowspan=4,
                  padx=5, sticky=E + W + S + N)

        abtn = Button(self, text="Update RSS", command=self.update_rss)
        abtn.grid(row=1, column=3)

        abtn = Button(self, text="Initialize Database", command=self.initialize_database)
        abtn.grid(row=2, column=3)

        abtn = Button(self, text="Fill Database", command=self.fill_database_from_files)
        abtn.grid(row=3, column=3)

        cbtn = Button(self, text="Close", command=self.quit)
        cbtn.grid(row=4, column=3, pady=4)

        Button(self, text="Benchmark", command=self.benchmark).grid(row=1, column=4)
        Button(self, text="MyISAM", command=self.change_to_myisam).grid(row=2, column=4)
        Button(self, text="InnoDB", command=self.change_to_innodb).grid(row=3, column=4)

    def update_rss(self):
        self.log(json.dumps(RSS.count_stored_rss(), indent=4))
        self.log("\nworking...\n")
        RSS.store_sites_rss()
        self.log(json.dumps(RSS.count_stored_rss(), indent=4))

    def initialize_database(self):
        self.log("mysql..")
        DB.init_mysql()
        self.log("mongo..")
        DB.init_mongo()
        self.log_separator()

    def fill_database_from_files(self):
        self.log("init...")
        news = RSS.load_all_news_as_array()
        users = DB.generate_users()
        DB.assign_news_to_users_randomly(news=news, users=users)
        self.log_begin("mysql..")
        news = DB.store_data_into_mysql(news)
        DB.assign_news_to_users_randomly(news, users)
        DB.store_users_in_mysql(users)
        self.log_end()
        self.log_begin("mongo...")
        DB.store_data_into_mongodb(news)
        DB.store_users_into_mongodb(users)
        self.log_end()
        self.log_separator()

    def benchmark(self):
        count = 100
        self.log_begin("Mysql...")
        DB.select_users_mysql(count)
        self.log_end()
        self.log_begin("Mongodb...")
        DB.select_users_mongo(count)
        self.log_end()
        self.log_separator()

    def log(self, s):
        self.area.insert(END, s + '\n')
        self.parent.update()

    def log_begin(self, s):
        self.start_time = datetime.now()
        self.log(s)

    def log_end(self, s=None):
        if s:
            self.log(s)
        duration = datetime.now() - self.start_time
        self.log("Time: %s" % str(duration))

    def log_separator(self):
        self.log("-" * 20)

    def change_to_myisam(self):
        DB.mysql_change_engine("MyISAM")

    def change_to_innodb(self):
        DB.mysql_change_engine("InnoDB")


def main():
    root = Tk()
    root.geometry("250x150+300+300")
    app = Example(root)
    root.mainloop()


if __name__ == '__main__':
    main()
