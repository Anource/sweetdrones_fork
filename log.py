import time


def print_log(message, log):
    if log:
        ftime = time.strftime('%Y-%m-%d %H:%M:%S')
        mtime = str(round(time.time() - int(time.time()), 3))[1:]
        ltime = ftime + mtime + '\t' + message
        print(ltime)
