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
    # ListComp 객체 생성 및 추가
    comp_instance = ListComp(company=comp)
    try:
        db.session.add(comp_instance)
        db.session.commit()
    except IntegrityError:
        db.session.rollback()
        comp_instance = db.session.query(ListComp).filter(ListComp.company == comp).first()

    # 중복되지 않는 루트 도메인 추출
    root_keys = {find_rootdomain(key) for key in keys}

    # ListRoot와 ListSub에 중복 삽입 방지 로직 추가
    existing_root_keys = db.session.query(ListRoot.url).filter(ListRoot.url.in_(root_keys)).all()
    existing_root_keys = {result[0] for result in existing_root_keys}

    # 새로운 루트 도메인들만 추가
    new_root_keys = root_keys - existing_root_keys

    if new_root_keys:
        root_instances = [ListRoot(company=comp, url=root_key) for root_key in new_root_keys]
        root_instances_for_subdomain = [ListSub(rootdomain=root_key, url=root_key, is_root=True) for root_key in new_root_keys]

        try:
            db.session.bulk_save_objects(root_instances)
            db.session.bulk_save_objects(root_instances_for_subdomain)
            db.session.commit()
        except IntegrityError:
            db.session.rollback()

    # 서브도메인 및 요청 키 추가
    subdomain_instances = []
    req_key_instances = []

    # 이미 있는 서브 도메인 필터링
    for root_key in root_keys:
        for key in keys:
            if key != root_key:
                subdomain_instances.append(ListSub(rootdomain=root_key, url=key, is_root=False))
            req_key_instances.append(ReqKeys(key=key))

    # 중복된 ReqKeys 처리
    existing_keys = db.session.query(ReqKeys.key).filter(ReqKeys.key.in_(keys)).all()
    existing_keys_set = {result[0] for result in existing_keys}
    
    # 새로운 ReqKeys만 추가
    new_req_key_instances = [ReqKeys(key=key) for key in keys if key not in existing_keys_set]

    try:
        if subdomain_instances:
            db.session.bulk_save_objects(subdomain_instances)
        if new_req_key_instances:
            db.session.bulk_save_objects(new_req_key_instances)
        
        db.session.commit()
    except IntegrityError:
        db.session.rollback()

    return 0

def create_task_list(task):
    task_list = []
    keys = db.session.query(ReqKeys.key).filter(
        getattr(ReqKeys, task) == 'notstarted',
        ReqKeys.id > 1000
    ).limit(36).all()

    task_list = [key[0] for key in keys]
    db.session.query(ReqKeys).filter(ReqKeys.key.in_(task_list)).update({
        task: 'processing',
        f"{task}_status": 'running'
    }, synchronize_session=False)
    
    db.session.commit()
    return task_list

def save_to_database(se, sd, title, link, content, git=False, original_url=None, cached_data=None):
    from app import app

    with app.app_context():
        if "bing" in link or "github" in sd:
            return 0

        subdomain = sd.split(":")[0] if ":" in sd else sd

        data_instance = ResGitData if git else ResDefData
        new_data = data_instance(
            searchengine=se, subdomain=subdomain, res_title=title, res_url=link, res_content=content
        )
        
        try:
            db.session.add(new_data)
            db.session.commit()
        except IntegrityError as e:
            db.session.rollback()
            error_code = e.orig.args[0]
            
            if error_code == 1062: 
                return 0
            elif error_code == 1452: 
                rootdomain = find_rootdomain(subdomain)
                root_instance = ListRoot(url=rootdomain)
                subdomain_instance = ListSub(rootdomain=rootdomain, url=subdomain, is_root=(rootdomain == subdomain))
                
                db.session.add(root_instance)
                db.session.add(subdomain_instance)
                db.session.commit()

                if original_url:
                    company = db.session.query(ReqKeys).join(ListSub, ListSub.url == ReqKeys.key)\
                                                    .join(ListRoot, ListRoot.url == ListSub.rootdomain)\
                                                    .filter(ReqKeys.key == original_url).first()
                    if company:
                        new_root = ListRoot(company=company.company, url=rootdomain)
                        db.session.add(new_root)
                        db.session.commit()
                
                db.session.add(new_data)
                db.session.commit()

        if cached_data:
            cache_instance = ResCacheData(url=link, cache=cached_data)
            db.session.add(cache_instance)
            db.session.commit()
        
        return 0

def update_status(se, url, status, git=False):
    from app import app

    column = f"{se}_git".lower() if git else f"{se}_def".lower()
    with app.app_context():
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