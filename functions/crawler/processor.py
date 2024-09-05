from multiprocessing import Process, Manager, current_process
from tqdm import tqdm

import logging, os, sys, signal

import functions.crawler.searcher as searcher
import functions.database.utils as utils

logging.basicConfig(filename='C:\\Users\\itf\\Documents\\selenium-search-api\\logs\\crawler_error.log', level=logging.WARNING,
                    encoding="utf-8", format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')

############### PROCESS ###############

def process_function(func, items, process_count):
    chunk_size = (len(items) + process_count - 1) // process_count
    chunks = [items[i * chunk_size:(i + 1) * chunk_size] for i in range(process_count)]

    # Create a shared queue for progress tracking
    manager = Manager()
    progress_queue = manager.Queue()

    # Create and start processes
    processes = []
    for chunk in chunks:
        p = Process(target=worker_function, args=(func, chunk, progress_queue))
        pbar.set_description(f'{func.__name__}: ')
        processes.append(p)
        p.start()

    def terminate_children():
        for p in processes:
            p.terminate()
        for p in processes:
            p.join()

    def signal_handler(signum, frame):
        terminate_children()
        sys.exit(0)

    signal.signal(signal.SIGTERM, signal_handler)
    signal.signal(signal.SIGINT, signal_handler)

    total_items = len(items)
    with tqdm(total=total_items) as pbar:
        completed_items = 0
        while completed_items < total_items:
            completed_items += progress_queue.get()
            pbar.update(1)

    for p in processes:
        p.join()

    terminate_children()

############### MAIN ###############

def process_start(args):
    count = sum(1 for value in args.values() if value)

    if count > 0:
        count = max(1, int(12 / count))

    def start_searcher(key, count):
        if args[key]:
            ls = utils.create_task_list(key)
            if key == "g_def":
                p = Process(target=process_function, args=(wrapper_g_def, ls, count))
            elif key == "b_def":
                p = Process(target=process_function, args=(wrapper_b_def, ls, count))
            elif key == "g_git":
                p = Process(target=process_function, args=(wrapper_g_git, ls, count))
            elif key == "b_git":
                p = Process(target=process_function, args=(wrapper_b_git, ls, count))

            p.start()
            return 0

    for key in args.keys():
        start_searcher(key, count)

    return 0

############### WRAPPER ###############

def wrapper_g_def(item):
    try:
        searcher.google_search(item)
    except Exception as e:
        if 'Critical' in str(e):
            raise ValueError(f"Critical error encountered in g_def")
        else:
            logging.error(f"Error in google_search: {e}")
            utils.update_status('g', item, 'notstarted')

def wrapper_b_def(item):
    try:
        searcher.bing_search(item)
    except Exception as e:
        if 'Critical' in str(e):
            raise ValueError(f"Critical error encountered in b_def")
        else:
            logging.error(f"Error in bing_search: {e}")
            utils.update_status('b', item, 'notstarted', True)

def wrapper_g_git(item):
    try:
        searcher.google_search(item, True)
    except Exception as e:
        if 'Critical' in str(e):
            raise ValueError(f"Critical error encountered in g_git")
        else:
            logging.error(f"Error in google_search with git: {e}")
            utils.update_status('g', item, 'notstarted', True)

def wrapper_b_git(item):
    try:
        searcher.bing_search(item, True)
    except Exception as e:
        if 'Critical' in str(e):
            raise ValueError(f"Critical error encountered in b_git")
        else:
            logging.error(f"Error in bing_search with git: {e}")
            utils.update_status('g', item, 'notstarted', True)

def worker_function(func, items, progress_queue):
    for item in items:
        try:
            func(item)
            progress_queue.put(1)
        except Exception as e:
            logging.error(f"Critical error encountered. Terminating process {current_process().name}.")
            this_index = items.index(item)

            searchengine = "g"
            git = False

            if "g_git" in str(e): git = True
            elif "b_def" in str(e): searchengine = "b"
            elif "b_git" in str(e):
                git = True
                searchengine = "b"

            notstarted_list = items[this_index:]
            for notstarted_url in notstarted_list:
                utils.update_status(searchengine, notstarted_url, 'notstarted', git)

            os._exit(1)
