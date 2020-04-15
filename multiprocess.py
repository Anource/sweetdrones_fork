from multiprocessing import Process
import time


def count_down(name):
    stime = time.time()
    print('Process %s starting...' % name)
    s = 0
    for i in range(10_000_000):
        s += i**2 * (i / 15)
    # print('Process %s s: %i' % (name, s))
    print('Process %s time: %f' % (name, time.time() - stime))
    # print('Process %s exiting...' % name)


if __name__ == '__main__':
    process1 = Process(target=count_down, args=('A'))
    # process2 = Process(target=count_down, args=('B'))
    # process3 = Process(target=count_down, args=('C'))
    # process4 = Process(target=count_down, args=('D'))

    process1.start()
    # process2.start()
    # process3.start()
    # process4.start()

    process1.join()
    # process2.join()
    # process3.join()
    # process4.join()

    print('Done.')
    # count_down('Single')