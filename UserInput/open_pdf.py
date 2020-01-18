"""
Class that runs a seperate thread from main process to automatically opens
pdf that user is inputting metadata for and closes it before it is opened
by the main process for metadata insertion
"""

import PyPDF2

import subprocess
import threading

class OpenPDF(threading.Thread):

    def __init__(self, queue, pdf_file):
        threading.Thread.__init__(self)
        self.queue = queue
        self.pdf_file = pdf_file

    def open_pdf(self):
        child = subprocess.Popen(["evince", self.pdf_file],
                                 shell=False,
                                 stdout=subprocess.PIPE,
                                 stderr=subprocess.PIPE)
        output = child.communidate()[0]
