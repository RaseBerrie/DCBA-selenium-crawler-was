import functions.crawler.searcher as searcher
import functions.database.utils as utils

import json, signal
from multiprocessing import Process

############### PROCESS ###############

def process_function(func, items, process_count):
    if (len(items) % process_count) == 0:
        chunk_size = (len(items) // process_count)
    else:
        chunk_size = (len(items) // process_count) + 1
    chunks = [items[i * chunk_size:(i + 1) * chunk_size] for i in range(process_count)]
    
    flag = True
    processes = []
    for chunk in chunks:
        if flag:
            p = Process(target=worker_function, args=(func, chunk))
            processes.append(p)
            p.start()        
        if len(processes) == process_count:
            flag = False

    def terminate_children():
        for p in processes:
            p.terminate()
            p.join()

    def signal_handler():
        terminate_children()
        raise SystemExit(0)
    
    signal.signal(signal.SIGTERM, signal_handler)
    signal.signal(signal.SIGINT, signal_handler)

############### MAIN ###############

def process_start(args):
    def start_searcher(key):
        if args[key]:
            ls = utils.create_task_list(key)
            if key == "g_def":
                p = Process(target=process_function, args=(wrapper_g_def, ls, 2))
            elif key == "b_def":
                p = Process(target=process_function, args=(wrapper_b_def, ls, 2))
            elif key == "g_git":
                p = Process(target=process_function, args=(wrapper_g_git, ls, 2))
            elif key == "b_git":
                p = Process(target=process_function, args=(wrapper_b_git, ls, 2))

            p.start()
            return 0

    for key in args.keys():
        start_searcher(key)

    return 0

############### WRAPPER ###############

def wrapper_g_def(item):
    searcher.google_search(item)

def wrapper_b_def(item):
    searcher.bing_search(item)

def wrapper_g_git(item):
    searcher.google_search(item, True)

def wrapper_b_git(item):
    searcher.bing_search(item, True)

def worker_function(func, items):
    for item in items: func(item)
    return 0