from main import db

class ListComp(db.Model):
    __tablename__ = 'list_company'

    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    company = db.Column(db.String(50), nullable=False)

    def __repr__(self):
        return f'<ListComp id={self.id} company={self.company}>'
    
class ListRoot(db.Model):
    __tablename__ = 'list_rootdomain'

    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    company = db.Column(db.String(50), nullable=False)
    url = db.Column(db.String(50), nullable=False)

    def __repr__(self):
        return f'<ListComp id={self.id} company={self.company} url={self.url}>'
    
class ListSub(db.Model):
    __tablename__ = 'list_subdomain'

    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    rootdomain = db.Column(db.String(50), nullable=False)
    url = db.Column(db.String(50), nullable=False)
    is_root = db.Column(db.Integer, nullable=False, default=0)

    def __repr__(self):
        return f'<ListComp id={self.id} rootdomain={self.rootdomain} url={self.url}, is_root={self.is_root}>'

class ResDefData(db.Model):
    __tablename__ = 'res_data_def'

    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    searchengine = db.Column(db.String(1), nullable=False)
    subdomain = db.Column(db.String(50), nullable=False)
    tags = db.Column(db.String(100), nullable=False, default="") 
    res_title = db.Column(db.String(100), nullable=False)
    res_url = db.Column(db.Text, nullable=False)
    res_content = db.Column(db.Text)
    update_time = db.Column(db.TIMESTAMP, nullable=False, server_default=db.func.current_timestamp())

    def __repr__(self):
        return f'''<ResDefData id={self.id} searchengine={self.searchengine} subdomain={self.subdomain} tags={self.tags}
        res_title={self.res_title} res_url={self.res_url} res_content={self.res_content} update_time={self.update_time}>'''
    
class ResGitData(db.Model):
    __tablename__ = 'res_data_git'

    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    searchengine = db.Column(db.String(1), nullable=False)
    subdomain = db.Column(db.String(50), nullable=False)
    filtered = db.Column(db.Integer, nullable=False)
    res_title = db.Column(db.String(100), nullable=False)
    res_url = db.Column(db.Text, nullable=False)
    res_content = db.Column(db.Text)
    update_time = db.Column(db.TIMESTAMP, nullable=False, server_default=db.func.current_timestamp())

    def __repr__(self):
        return f'''<ResGitData id={self.id} searchengine={self.searchengine} subdomain={self.subdomain} filtered={self.filtered}
        res_title={self.res_title} res_url={self.res_url} res_content={self.res_content} update_time={self.update_time}>'''
    
class ResCacheData(db.Model):
    __tablename__ = 'res_data_cache'

    url = db.Column(db.String(750), primary_key=True, nullable=False)
    cache = db.Column(db.LargeBinary, nullable=True)

    def __repr__(self):
        return f'<ListComp url={self.url} cache={self.cache}>'

class ReqKeys(db.Model):
    __tablename__ = 'req_keys'

    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    key = db.Column(db.String(50), nullable=False)
    
    b_def = db.Column(db.Enum('notstarted', 'processing', 'finished', name='status_enum'), default='notstarted', nullable=False)
    b_def_status = db.Column(db.Enum('none', 'running', 'killed', 'done', name='status_enum'), default='none', nullable=False)
    
    g_def = db.Column(db.Enum('notstarted', 'processing', 'finished', name='status_enum'), default='notstarted', nullable=False)
    g_def_status = db.Column(db.Enum('none', 'running', 'killed', 'done', name='status_enum'), default='none', nullable=False)

    b_git = db.Column(db.Enum('notstarted', 'processing', 'finished', name='status_enum'), default='notstarted', nullable=False)
    b_git_status = db.Column(db.Enum('none', 'running', 'killed', 'done', name='status_enum'), default='none', nullable=False)

    g_git = db.Column(db.Enum('notstarted', 'processing', 'finished', name='status_enum'), default='notstarted', nullable=False)
    g_git_status = db.Column(db.Enum('none', 'running', 'killed', 'done', name='status_enum'), default='none', nullable=False)

    def __repr__(self):
        return f'''<ReqKeys id={self.id} key={self.key}
        b_def={self.b_def} b_def_status={self.b_def_status} g_def={self.g_def} g_def_status={self.g_def_status}
        b_git={self.g_git} b_git_status={self.b_git} g_git={self.g_git} g_git_status={self.g_git_status}>'''
    
class TagExp(db.Model):
    __tablename__ = 'res_tags_expose'

    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    url = db.Column(db.Text, nullable=False)
    restype = db.Column(db.Enum('error', 'sample', 'servinfo', 'classified', 'others', name='restype_enum'))
    exp_content = db.Column(db.Text, nullable=True)

    def __repr__(self):
        return f"<TagExp id={self.id} url={self.url} restype={self.restype} exp_content={self.exp_content}>"
    
class TagFile(db.Model):
    __tablename__ = 'res_tags_file'

    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    url = db.Column(db.Text, nullable=False)
    filetype = db.Column(db.Enum('pdf','pptx','xlsx','docx','others'))
    title = db.Column(db.String(200))
    moddate = db.Column(db.TIMESTAMP)
    data = db.Column(db.Text)
    is_link = db.Column(db.Integer)

    def __repr__(self):
        return f'''<TagFile id={self.id} url={self.url} filetype={self.filetype}
        title={self.title} moddate={self.moddate} data={self.data} is_link={self.is_link}>'''
    
class ReqStat(db.Model):
    __tablename__ = 'req_status'
    
    searchengine = db.Column(db.String(6), primary_key=True)
    last_request = db.Column(db.DATETIME(timezone=True))

    def __repr__(self):
        return f'<ReqStat searchengine={self.searchengine} last_request={self.last_request}>'