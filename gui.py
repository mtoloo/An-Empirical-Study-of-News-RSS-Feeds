#!/usr/bin/python

import json
from Tkinter import Tk, Frame, BOTH, Button, RAISED, RIGHT, LEFT, Y, RIDGE, Label, W, Text, E, S, N, END, DISABLED, \
    NORMAL, Radiobutton, StringVar
from ttk import Style, Progressbar

import time

from datetime import datetime, timedelta

from db import DB
from rss import RSS


class Example(Frame):
    def __init__(self, parent):
        Frame.__init__(self, parent)

        self.progress_current = 0
        self.last_update = time.time()
        self.stopped = False
        self.mysql_engine = StringVar()
        self.parent = parent
        self.init_ui()
        self.set_status()

    def init_ui(self):
        w = 700
        h = 400
        sw = self.parent.winfo_screenwidth()
        sh = self.parent.winfo_screenheight()
        x = (sw - w) / 2
        y = (sh - h) / 2
        self.parent.geometry('%dx%d+%d+%d' % (w, h, x, y))

        self.parent.title("An-Empirical-Study-of-News-RSS-Feeds")
        # self.pack(fill=BOTH, expand=True)

        command_frame = Frame(self)
        command_frame.grid(rowspan=4, column=0)
        Button(self, text="Update RSS", command=self.update_rss).grid(row=1, column=0)
        myisamRadio = Radiobutton(self, text="MyISAM", variable=self.mysql_engine, value='myisam')
        myisamRadio.grid(row=2, column=0)
        innodbRadio = Radiobutton(self, text="InnoDB", variable=self.mysql_engine, value='innodb')
        innodbRadio.grid(row=3, column=0)
        Button(self, text="Initialize Database", command=self.initialize_database).grid(row=4, column=0)
        self.fill_database_button = Button(self, text="Insert", command=self.fill_database_from_files )
        self.fill_database_button.grid(row=5, column=0)
        self.benchmark_button = Button(self, text="Select", command=self.select_benchmark)
        self.benchmark_button.grid(row=6, column=0)
        self.benchmark_button = Button(self, text="Update", command=self.update_benchmark)
        self.benchmark_button.grid(row=7, column=0)
        self.stop_button = Button(self, text="Stop", command=self.stop)
        self.stop_button.grid(row=8, column=0, pady=4)
        # Button(self, text="Close", command=self.quit).grid(row=8, column=0, pady=4)

        Label(self, text="Log").grid(row=0, column=1)
        self.area = Text(self)
        self.area.grid(row=1, column=1, columnspan=2, rowspan=7, padx=10, sticky=E + W + S + N)

        self.progress_bar = Progressbar(self, orient='horizontal')
        self.progress_bar.grid(row=8, column=2, columnspan=2)
        self.progress_bar.grid_forget()
        self.progress_text = Label(self, text="Ready", width=30)
        self.progress_text.grid(row=8, column=1)
        self.progress_text.grid_forget()

        self.pack()

    def update_rss(self):
        self.log(json.dumps(RSS.count_stored_rss(), indent=4))
        self.log("\nworking...\n")
        self.stopped = False
        self.progress_started()
        RSS.store_sites_rss(self.show_progress)
        self.progress_finished()
        self.log(json.dumps(RSS.count_stored_rss(), indent=4))

    def initialize_database(self):
        self.log_separator()
        self.progress_started("Initialize...", 2)
        self.show_progress(1)
        DB.init_mysql(self.mysql_engine.get())
        self.show_progress(2)
        DB.init_mongo()
        self.progress_finished()

    def fill_database_from_files(self):
        self.log("init...")
        news = RSS.load_all_news_as_array()
        users = DB.generate_users()
        DB.assign_news_to_users_randomly(news=news, users=users)
        self.progress_started("MySQL", len(news))
        self.show_progress(0, 0, "mysql : news ..")
        news = DB.store_data_into_mysql(news, self.show_progress)
        if self.stopped: return
        self.show_progress(0, len(users), 'init users..')
        user_news_count = DB.assign_news_to_users_randomly(news, users)
        if self.stopped: return
        self.show_progress(0, user_news_count, 'mysql: users reading news..')
        DB.store_users_in_mysql(users, self.show_progress)
        if self.stopped: return
        self.progress_finished()
        self.parent.update()
        time.sleep(1)
        self.progress_started("MongoDB")
        self.show_progress(0, len(news), 'mongo: news')
        DB.store_data_into_mongodb(news, self.show_progress)
        if self.stopped: return
        self.show_progress(0, user_news_count, 'mongo: users reading news..')
        DB.store_users_into_mongodb(users, self.show_progress)
        if self.stopped: return
        self.progress_finished()
        self.set_status()

    def select_benchmark(self):
        self.log_separator()
        count = 1000
        self.progress_started("MySQL", total=count)
        DB.select_users_mysql(count, self.show_progress)
        self.progress_finished()
        self.parent.update()
        time.sleep(1)
        self.progress_started("Mongodb")
        DB.select_users_mongo(count, self.show_progress)
        self.progress_finished()

    def update_benchmark(self):
        self.log_separator()
        count = 1000
        self.progress_started("MySQL", total=count)
        DB.update_users_reading_news_mysql(count, self.show_progress)
        self.progress_finished()
        self.parent.update()
        time.sleep(1)
        self.progress_started("Mongodb")
        DB.update_users_reading_news_mongo(count, self.show_progress)
        self.progress_finished()

    def log(self, s):
        self.area.insert(END, s + '\n')

    def log_separator(self):
        self.log("-" * 20)

    def set_status(self):
        self.rss_total = RSS.count_stored_rss()['Total']
        self.db_mysql_created = DB.mysql_created()
        self.db_mysql_count = 0
        if self.db_mysql_created:
            self.db_mysql_count = DB.mysql_stat()['news']

        self.fill_database_button['state'] = NORMAL if self.db_mysql_created else DISABLED
        self.benchmark_button['state'] = NORMAL if self.db_mysql_count else DISABLED
        self.stop_button['state'] = NORMAL if self.stopped else DISABLED
        # self.mysql_engine.set('innodb')

    def stop(self):
        self.stopped = True
        self.stop_button['state'] = DISABLED
        self.parent.update()

    def show_progress(self, current=None, total=None, text=None):
        if total:
            self.progress_bar['maximum'] = total
        if current is None:
            current = self.progress_current + 1
        self.progress_current = current
        if text:
            text += " (%d)" % (total or self.progress_bar['maximum'])
            self.progress_text['text'] = text
        self.stop_button['state'] = NORMAL
        if time.time() - self.last_update > 0.1:
            self.progress_bar['value'] = current
            self.parent.update()
            self.last_update = time.time()
        return not self.stopped

    def progress_started(self, log=None, total=None):
        self.start_time = datetime.now()
        self.progress_bar.grid(row=8, column=2, columnspan=2)
        self.progress_text.grid(row=8, column=1)
        if log:
            self.log(log)
        self.show_progress(0, total=total or 0, text=log or '')

    def progress_finished(self):
        duration = datetime.now() - self.start_time
        self.log("Duration: %s" % str(duration))
        self.progress_bar.grid_remove()
        self.progress_text.grid_remove()

if __name__ == '__main__':
    root = Tk()
    app = Example(root)
    root.mainloop()
