from multiprocessing import Process, Manager, current_process
from tqdm import tqdm

import logging, os, sys, signal
import functions.crawler.searcher as searcher
import functions.database.utils as utils


# =====================================================
# ==                 DISCRIPTION                     ==
# =====================================================


#   [ process_start 호출 후 진행 ]

#   → process_function 각 args별로 프로세스 4개 실행
#   → 각각의 process_function 내부에서 worker_function 호출
#   → worker_function 내부에서 각각 wrapper_*_*** 함수 호출
#   → 크롤러 진행 후 내부 프로세서 종료, 외부 프로세스 종료


# =====================================================
# ==                  PROCESSOR                      ==
# =====================================================


def process_function(func, items, process_count):
    from app import app
    
    chunk_size = (len(items) + process_count - 1) // process_count
    chunks = [items[i * chunk_size:(i + 1) * chunk_size] for i in range(process_count)]

    # === 프로세스 큐 세팅 ===

    manager = Manager()
    progress_queue = manager.Queue()

    processes = []
    for chunk in chunks:
        p = Process(target=worker_function, args=(func, chunk, progress_queue))
        processes.append(p)
        with app.app_context():
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

    process_name = func.__name__ 
    total_items = len(items)

    # === 프로세스 완료 시 Pbar 업데이트 ===

    with tqdm(total=total_items) as pbar:
        pbar.set_description(process_name)
        completed_items = 0

        while completed_items < total_items:
            completed_items += progress_queue.get()
            pbar.update(1)

    # === 내부 프로세스 종료 ===

    for p in processes:
        p.join()

    terminate_children()


# =====================================================
# ==                 PROCESS START                   ==
# =====================================================


def process_start(args, key_dict):
    from app import app
    
    count = sum(1 for value in args.values() if value)
    if count > 0:
        count = max(1, int(12 / count))

    # === 외부 프로세스 생성 ===

    processes = []
    def start_searcher(key, count):
        if args[key]:
            if key == "b_def":
                p = Process(target=process_function, args=(wrapper_b_def, key_dict[key], count))
            elif key == "g_def":
                p = Process(target=process_function, args=(wrapper_g_def, key_dict[key], count))
            elif key == "b_git":
                p = Process(target=process_function, args=(wrapper_b_git, key_dict[key], count))
            elif key == "g_git":
                p = Process(target=process_function, args=(wrapper_g_git, key_dict[key], count))
            
            with app.app_context():
                p.start()
                processes.append(p)
           
    for key in args.keys():
        start_searcher(key, count)

    # === 외부 프로세스 종료 ===

    for p in processes:
        p.join() # → 외부 프로세스가 종료되면 Client에 알려야 함

    return 0


# =====================================================
# ==                   WRAPPERS                      ==
# =====================================================


def wrapper_b_def(item):
    try:
        searcher.bing_search(item)
    except Exception as e:
        if 'Critical' in str(e):
            raise ValueError(f"Critical error encountered in b_def")
        else:
            logging.error(f"Error in bing_search: {e}")
            utils.update_status('b', item, 'notstarted')

def wrapper_g_def(item):
    try:
        searcher.google_search(item)
    except Exception as e:
        if 'Critical' in str(e):
            raise ValueError(f"Critical error encountered in g_def")
        else:
            logging.error(f"Error in google_search: {e}")
            utils.update_status('g', item, 'notstarted')

def wrapper_b_git(item):
    try:
        searcher.bing_search(item, True)
    except Exception as e:
        if 'Critical' in str(e):
            raise ValueError(f"Critical error encountered in b_git")
        else:
            logging.error(f"Error in bing_search (git): {e}")
            utils.update_status('b', item, 'notstarted', True)

def wrapper_g_git(item):
    try:
        searcher.google_search(item, True)
    except Exception as e:
        if 'Critical' in str(e):
            raise ValueError(f"Critical error encountered in g_git")
        else:
            logging.error(f"Error in google_search (git): {e}")
            utils.update_status('g', item, 'notstarted', True)

# === 실행 함수 ===

def worker_function(func, items, progress_queue):
    for item in items:
        try:
            func(item)
            progress_queue.put(1)

        except Exception as e:
            logging.error(f"Critical error encountered. Terminating process {current_process().name}.")
            this_index = items.index(item)

            searchengine, git = "g", False
            
            if "_git" in str(e): git = True
            if "b_" in str(e): searchengine = "b"
            
            notstarted_list = items[this_index:]
            for notstarted_url in notstarted_list:
                utils.update_status(searchengine, notstarted_url, 'notstarted', git)

            os._exit(1)