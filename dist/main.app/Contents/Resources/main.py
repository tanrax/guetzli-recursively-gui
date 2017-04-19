#!/usr/bin/env python
# -*- coding: utf-8 -*-
from os import path, walk, remove, rename
from imghdr import what
from subprocess import call
from tkinter import Frame, Tk, Button, Label, filedialog, ttk, font, PhotoImage
import threading


class Application(Frame):

    def __init__(self, master=None):
        Frame.__init__(self, master)
        master.title('Guetzli recursively GUI')
        master.minsize(width=500, height=140)
        master.maxsize(width=500, height=140)
        self.font_general = font.Font(family='Helvetica', size=14)
        self.font_run = font.Font(family='Helvetica', size=18)
        self.center(master)
        self.pack()
        self.create_widgets()
        self.top_dir = ''
        self.TEMP_FILE = 'temp.jpg'
        self.TYPES = ('jpeg',)
        self.num_images = 0

    def create_widgets(self):
        # Button select folder
        self.button_select_folder = Button(self)
        self.button_select_folder['text'] = 'Choose folder'
        self.button_select_folder['pady'] = 10
        self.button_select_folder['font'] = self.font_general
        self.button_select_folder['command'] = self.open_folder
        self.button_select_folder.pack(side='top')
        # Label path folder
        self.label_path = Label(self)
        self.label_path['text'] = ''
        self.label_path['pady'] = 10
        self.label_path['font'] = self.font_general
        # Button run
        self.button_run = Button(self)
        self.button_run['text'] = 'Optimize'
        self.button_run['font'] = self.font_run
        self.button_run['pady'] = 10
        self.button_run['state'] = 'disabled'
        self.button_run['command'] = self._start_optimize
        self.button_run.pack(side='top')
        # Progressbar
        self.progress_bar = ttk.Progressbar(self)
        self.progress_bar['length'] = 500

    def center(self, toplevel):
        toplevel.update_idletasks()
        w = toplevel.winfo_screenwidth()
        h = toplevel.winfo_screenheight()
        size = tuple(
                int(_) for _ in toplevel.geometry().split('+')[0].split('x')
                )
        x = w/2 - size[0]/2
        y = h/2 - size[1]/2
        toplevel.geometry('%dx%d+%d+%d' % (size + (x, y)))

    def open_folder(self):
        self.button_run['state'] = 'disabled'
        self.top_dir = filedialog.askdirectory(initialdir='.')
        self.label_path['text'] = 'Looking for images to optimize... Please, wait'
        self._start_count_images()

    def _update_label_num_files(self):
        self.label_path['text'] = f'{self.num_images} images found'
        if self.num_images > 0:
            self.button_run['state'] = 'normal'
        self.button_run.pack_forget()
        self.label_path.pack(side='top')
        self.button_run.pack(side='top')

    def _start_count_images(self):
        newthread = threading.Thread(target=self.count_images)
        newthread.start()

    def _start_optimize(self):
        newthread = threading.Thread(target=self.run_guetzli)
        newthread.start()

    def count_images(self):
        num = 0
        for dirpath, dirnames, files in walk(self.top_dir):
            for name in files:
                url = path.join(dirpath, name)
                # Check type
                if what(url) in self.TYPES:
                    num += 1
        self.num_images = num
        self._update_label_num_files()

    def run_guetzli(self):
        # Show progress bar
        self.progress_bar['value'] = 0
        self.progress_bar['maximum'] = self.num_images
        self.progress_bar.pack(side='bottom')
        self.button_run['state'] = 'disabled'
        self.button_select_folder['state'] = 'disabled'
        # Run guetzli
        for dirpath, dirnames, files in walk(self.top_dir):
            for name in files:
                url = path.join(dirpath, name)
                self.label_path['text'] = f'Working... {name}'
                # Check type
                if what(url) in self.TYPES:
                    # Get urls
                    url_out = path.join(self.top_dir, self.TEMP_FILE)
                    # Remove temp image
                    try:
                        remove(url_out)
                    except:
                        pass
                    # Execute guetzli
                    call(['guetzli-osx', url, url_out])
                    # Check if it is cost effective to replace it
                    size_source = path.getsize(url)
                    size_out = 0
                    try:
                        size_out = path.getsize(url_out)
                    except:
                        size_out = size_source
                    size_acurate = 100 * size_out / size_source
                    if size_acurate < 100:
                        # Remove source
                        try:
                            remove(url)
                        except:
                            pass
                        # Move temp to source
                        rename(url_out, url)
                    # Increment progress bar
                    self.progress_bar['value'] += 1
        # Message finish
        self.button_select_folder['state'] = 'normal'
        self.label_path['text'] = 'Finish!'
        self.progress_bar.pack_forget()

root = Tk()
app = Application(master=root)
app.mainloop()
