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
    process2 = Process(target=count_down, args=('B'))
    process3 = Process(target=count_down, args=('C'))
    process4 = Process(target=count_down, args=('D'))
    process5 = Process(target=count_down, args=('E'))
    process6 = Process(target=count_down, args=('F'))
    process7 = Process(target=count_down, args=('G'))
    process8 = Process(target=count_down, args=('H'))
    process9 = Process(target=count_down, args=('J'))
    process10 = Process(target=count_down, args=('K'))

    process1.start()
    process2.start()
    process3.start()
    process4.start()
    process5.start()
    process6.start()
    process7.start()
    process8.start()
    process9.start()
    process10.start()

    process1.join()
    process2.join()
    process3.join()
    process4.join()
    process5.join()
    process6.join()
    process7.join()
    process8.join()
    process9.join()
    process10.join()

    print('Done.')
    # count_down('Single')

    # 1: 3.79
    # 2: 3.81
    # 3: 3.88
    # 4: 3.78
    # 5: 3.81
    # 6: 4.06
    # 7: 4.58
    # 8: 5.12
    # 9: 5.51
    # 10: 5.66

