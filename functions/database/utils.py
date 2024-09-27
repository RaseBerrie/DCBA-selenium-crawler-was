from main import db
from functions.database.models import ResDefData, ResGitData, ResCacheData, ListComp, ListRoot, ListSub, ReqKeys

from sqlalchemy.exc import IntegrityError

def find_rootdomain(domain):
    if ":" in domain:
        tmp = domain.split(":")
        domain = tmp[0]

    found = 0
    tmp = domain.split(".")

    tld = tmp[-1]
    second_level = tmp[-2] if len(tmp) > 1 else ''

    if tld in ['com', 'jp', 'net', 'ca', 'uz', 'in', 'cn']:
        found = tmp.index(tld)
    elif tld == 'kr':
        found = tmp.index(second_level if second_level in ['or', 'co', 'ac'] else tld)
    elif tld == 'co' and second_level == 'uk':
        found = tmp.index('co')

    found = found - 1
    tmp_list = tmp[found:]

    result = ".".join(tmp_list)
    return result

def insert_into_keys(comp, keys):
    comp_instance = ListComp(company=comp)
    db.session.add(comp_instance)
    
    root_key_set = set()
    for key in keys:
        root_key_set.add(find_rootdomain(key))
    
    root_keys = list(root_key_set)
    for root_key in root_keys:
        root_instance = ListRoot(company=comp_instance, url=root_key)
        db.session.add(root_instance)
        
        subdomain_instance = ListSub(rootdomain=root_key, url=root_key, is_root=True)
        db.session.add(subdomain_instance)
        
        for key in keys:
            if key != root_key:
                subdomain_instance = ListSub(rootdomain=root_key, url=key, is_root=False)
                db.session.add(subdomain_instance)

            try:
                req_key_instance = ReqKeys(key=key)
                db.session.add(req_key_instance)
            except IntegrityError:
                db.session.rollback()

    db.session.commit()
    return 0

def create_task_list(task):
    task_list = []
    keys = db.session.query(ReqKeys).filter(getattr(ReqKeys, task) == 'notstarted', ReqKeys.id > 1000).limit(36).all()
    
    for key in keys:
        task_list.append(key.key)
    
    for task_url in task_list:
        db.session.query(ReqKeys).filter_by(key=task_url).update({
            task: 'processing', 
            f"{task}_status": 'running'
        })
    
    db.session.commit()
    return task_list

def save_to_database(se, sd, title, link, content, git=False, original_url=None, cached_data=None):
    if "bing" in link or "github" in sd:
        return 0

    subdomain = sd.split(":")[0] if ":" in sd else sd
    
    if git:
        data_instance = ResGitData(searchengine=se, subdomain=subdomain,
                                   res_title=title, res_url=link, res_content=content)
    else:
        data_instance = ResDefData(searchengine=se, subdomain=subdomain,
                                   res_title=title, res_url=link, res_content=content)
    
    try:
        db.session.add(data_instance)
        db.session.commit()
    except IntegrityError as e:
        db.session.rollback()
        if e.orig.args[0] == 1062:
            return 0  # Ignore duplicates
        elif e.orig.args[0] == 1452:
            rootdomain = find_rootdomain(subdomain)
            root_instance = ListRoot(url=rootdomain)
            subdomain_instance = ListSub(rootdomain=rootdomain, url=subdomain, is_root=(rootdomain == subdomain))
            
            db.session.add(root_instance)
            db.session.add(subdomain_instance)
            db.session.commit()

            if original_url:
                company = db.session.query(ReqKeys).join(ListSub, ListSub.url == ReqKeys.key).join(ListRoot, ListRoot.url == ListSub.rootdomain).filter(ReqKeys.key == original_url).first()
                if company:
                    new_root = ListRoot(company=company.company, url=rootdomain)
                    db.session.add(new_root)
                    db.session.commit()
            
            db.session.add(data_instance)
            db.session.commit()
    
    if cached_data:
        cache_instance = ResCacheData(url=link, cache=cached_data)
        db.session.add(cache_instance)
        db.session.commit()
    
    return 0

def update_status(se, url, status, git=False):
    column = f"{se}_git" if git else f"{se}_def"
    
    db.session.query(ReqKeys).filter_by(key=url).update({
        column: status
    })
    
    if status == 'notstarted':
        db.session.query(ReqKeys).filter_by(key=url).update({
            f"{column}_status": 'killed'
        })
    elif status == 'finished':
        db.session.query(ReqKeys).filter_by(key=url).update({
            f"{column}_status": 'done'
        })
    
    db.session.commit()
    return 0