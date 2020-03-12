import multiprocessing
from multiprocessing import Process

from capture import main as capture
from owl import main as logger

import tkinter

WIDTH = 200
HEIGHT = 100


if __name__ == '__main__':
    multiprocessing.freeze_support()

    logger_process = Process(target=logger)
    logger_process.daemon = True
    logger_process.start()

    capture_process = Process(target=capture, args=(2,))
    capture_process.daemon = True
    capture_process.start()

    window = tkinter.Tk()
    window.title("Logger")
    window.config(height=HEIGHT, width=WIDTH)
    button_widget = tkinter.Button(window, text="Stop logging", command=window.destroy)\
        .place(relx=0.5, rely=0.5, anchor=tkinter.CENTER)
    tkinter.mainloop()
