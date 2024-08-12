from multiprocessing import Process
import functions.crawler.searcher as searcher
import json, signal

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


############### WRAPPER ###############

def wrapper_search(engine, item, is_git):
    if engine == 'google':
        if is_git: searcher.google_search(item, "github")
        else: searcher.google_search(item)
    elif engine == 'bing':
        if is_git: searcher.bing_search(item, "github")
        else: searcher.bing_search(item)

def wrapper_google_search(item):
    wrapper_search('google', item, False)

def wrapper_bing_search(item):
    wrapper_search('bing', item, False)

def wrapper_google_search_github(item):
    wrapper_search('google', item, True)

def wrapper_bing_search_github(item):
    wrapper_search('bing', item, True)

############### MAIN ###############

def process_start(json_data):
    args = json.loads(json_data)
    
    def start_searcher(key):
        if args[key]:
            ls = create_task_list(key)
            if key == "google":
                p = Process(target=process_function, args=(wrapper_google_search, ls, 2))
            elif key == "github_google":
                p = Process(target=process_function, args=(wrapper_google_search_github, ls, 2))
            elif key == "bing":
                p = Process(target=process_function, args=(wrapper_bing_search, ls, 2))
            elif key == "github_bing":
                p = Process(target=process_function, args=(wrapper_bing_search_github, ls, 2))
            p.start()

        return 0

    for key in args.keys():
        start_searcher(key)

    return 0