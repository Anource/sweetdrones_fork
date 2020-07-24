from multiprocessing import Process
import numpy as np
import time
import copy
from main import DronesProject, simulation_params

import vk_log
token = 'a5f92c3aa82877091fd3ba8a98f493b34d8355a0266b6bf5371268b9df05f78f8cdad25ace67a54448c0f'
api_v = '5.101'
bot = vk_log.vk(token, api_v)
uid = 62619861  # ID юзера вк, кому присылать сообщения


def hms(time_s):
    if time_s >= 86400:
        d = int(time_s / 86400)
        h = int((time_s - 86400 * d) / 3600)
        m = int((time_s - 86400 * d - 3600 * h) / 60)
        s = int((time_s - 86400 * d - 3600 * h - 60 * m))
        return f'{d}d {h}h {m}m {s}s'
    elif 3600 <= time_s < 86400:
        h = int(time_s / 3600)
        m = int((time_s - 3600 * h) / 60)
        s = int((time_s - 3600 * h - 60 * m))
        return f'{h}h {m}m {s}s'
    elif 60 <= time_s < 3600:
        m = int(time_s / 60)
        s = int(time_s - 60 * m)
        return f'{m}m {s}s'
    elif 0 <= time_s < 60:
        s = int(time_s)
        return f'{s}s'


def average_data(data, process):
    print(f'Started with process {process}')
    block_time = time.time()
    local_initial_data = copy.deepcopy(simulation_params)
    for key in data:
        if key != 'save_code':
            local_initial_data[key] = data[key]
    save_code = data['save_code']
    errors_in_exception = 0
    coverage_pso = []
    coverage_kmeans = []
    coverage_twice_pso = []
    coverage_twice_kmeans = []
    completed = 0
    mid_time = time.time()
    while completed < local_initial_data['average_runs']:
        try:
            # print(f'Trying: {completed}')
            simulation = DronesProject(local_initial_data)
            simulation.start(pso=True, kmeans=True)
            c_pso, c_kmeans = simulation.get_coverage()
            ct_pso, ct_kmeans = simulation.get_twice_coverage()
        except BaseException:
            print(f'Aargh! Error in process {process}. Try again.')
            errors_in_exception += 1
            continue
        else:
            coverage_pso.append(c_pso)
            coverage_kmeans.append(c_kmeans)
            coverage_twice_pso.append(ct_pso)
            coverage_twice_kmeans.append(ct_kmeans)
            if not completed % int(local_initial_data['average_runs'] / 5):

                bot.send_message(uid, f"[MIDDLE REPORT] MP {process}\n"
                                      f"Case {save_code}\n"
                                      f"Stage {completed}/{local_initial_data['average_runs']}\n"
                                      f"Time: {hms(time.time() - mid_time)}\n"
                                      f"Estimated: {hms((time.time() - mid_time) * int(5 - 5 * completed / local_initial_data['average_runs'])) if completed else 'unknown'}")
                mid_time = time.time()
            completed += 1

    coverage_pso = np.average(coverage_pso, axis=0)
    coverage_kmeans = np.average(coverage_kmeans, axis=0)
    np.save(f'cases/{save_code}_{process}_pso.npy', coverage_pso)
    np.save(f'cases/{save_code}_{process}_kmeans.npy', coverage_kmeans)
    np.save(f'cases/tw_{save_code}_{process}_pso.npy', coverage_twice_pso)
    np.save(f'cases/tw_{save_code}_{process}_kmeans.npy', coverage_twice_kmeans)
    print('Errors:', errors_in_exception)
    bot.send_message(uid, f"[FINAL REPORT] MP {process}\n"
                          f"Case {save_code}\n"
                          f"Stage {completed}/{local_initial_data['average_runs']}\n"
                          f"Total time: {hms(time.time() - block_time)}")


# Вводить только те данные, которые меняются в текущей симуляции; остальные подхватятся из дефолтного списка
changed_data_01 = {
    'average_runs': 500,
    'drone_t_upd': 5.,
    'save_code': 'c2_equal_groups_t5'
}

changed_data_02 = {
    'average_runs': 500,
    'drone_t_upd': 5.,
    'groups_limits': [34, 39, 45, 55, 77],
    'save_code': 'c2_not_equal_groups_t5'
}

changed_data_03 = {
    'average_runs': 500,
    'drone_t_upd': 0.,
    'save_code': 'c2_equal_groups_t0'
}

changed_data_04 = {
    'average_runs': 500,
    'drone_t_upd': 0.,
    'groups_limits': [34, 39, 45, 55, 77],
    'save_code': 'c2_not_equal_groups_t0'
}

use_multiprocess = True


def average_data_multiprocess(data, process_name):
    average_data(data, process_name)


if __name__ == '__main__':
    # average_data(changed_data_03, 'default')
    if use_multiprocess:
        process1 = Process(target=average_data_multiprocess, args=(changed_data_01, 'A'))
        process2 = Process(target=average_data_multiprocess, args=(changed_data_02, 'B'))
        process3 = Process(target=average_data_multiprocess, args=(changed_data_03, 'C'))
        process4 = Process(target=average_data_multiprocess, args=(changed_data_04, 'D'))
        # process5 = Process(target=average_data_multiprocess, args=(changed_data_01, 'E'))
        # process6 = Process(target=average_data_multiprocess, args=(changed_data_01, 'F'))

        process1.start()
        process2.start()
        process3.start()
        process4.start()
        # process5.start()
        # process6.start()

        process1.join()
        process2.join()
        process3.join()
        process4.join()
        # process5.join()
        # process6.join()
