from main import db
from functions.database.models import ResDefData, TagFile
import functions.database.classify as classify

def run():
    try:
        classify.filter_github()

        # 분류: 퍼블릭
        db.session.query(ResDefData).filter(
            ResDefData.tags == '',
            ((ResDefData.res_url.op('regexp')("/[0-9]+/|[0-9]+$|notice_?view|/post/|/press/")) |
             (ResDefData.res_url.op('regexp')(r'(\/|=)[0-9a-z-]+(\.(html))*\/*$'))),
            ~ResDefData.res_url.like('%{}%'.format("download"))
        ).update({"tags": 'public'}, synchronize_session='fetch')

        # 분류: 파일
        db.session.query(ResDefData).filter(
            ((ResDefData.res_url.op('regexp')("\\.(pdf|xlsx|docx|ppt[x]{0,1}|hwp|txt|ai)+$")) |
             (ResDefData.res_url.like('%{}%'.format("download")))),
            ResDefData.tags == ''
        ).update({"tags": 'file'}, synchronize_session='fetch')

        # 파일 태그 업데이트
        insert_stmt = TagFile.__table__.insert().prefix_with("ignore").from_select(
            ['id', 'url'],
            db.session.query(ResDefData.id, ResDefData.res_url).filter(ResDefData.tags == 'file')
        )
        db.session.execute(insert_stmt)
        update_filetype()

        # 분류: 불필요한 정보 노출
        db.session.query(ResDefData).filter(
            (ResDefData.tags == '') | (ResDefData.tags == 'public'),
            ((ResDefData.res_title.op('regexp')(r'시스템.메.지|Apache')) |
             (ResDefData.res_url.op('regexp')(r'editor|plugin/|namo|dext|CVS|root|[Rr]epository|changelog|jsessionid')) |
             (ResDefData.res_content.op('regexp')(r'시스템.메.지|워드프레스')))
        ).update({'tags': 'expose'}, synchronize_session='fetch')

        # 분류: 관리자 페이지
        classify_query = classify.is_admin()
        if classify_query is not None:
            db.session.execute(classify_query)

        # 분류: 로그인 페이지
        db.session.query(ResDefData).filter(
            ResDefData.tags == '',
            ((ResDefData.res_title.op('regexp')(r'로그인|login')) |
             (ResDefData.res_url.op('regexp')(r'login\.[a-zA-Z]*$')) |
             (ResDefData.res_content.op('regexp')(r'login'))),
            ~ResDefData.res_url.op('regexp')(r'regist|password')
        ).update({'tags': 'login'}, synchronize_session='fetch')

        db.session.commit()
    except Exception as e:
        db.session.rollback()
        raise e
    finally:
        db.session.close()

def update_filetype():
    try:
        filetypes = ['pdf', 'xlsx', 'docx', 'pptx']
        for filetype in filetypes:
            db.session.query(TagFile).filter(
                TagFile.url.op('regexp')(f'{filetype}+$')
            ).update({'filetype': filetype}, synchronize_session='evaluate')

        # ppt의 경우 추가적인 조건 처리
        db.session.query(TagFile).filter(
            TagFile.url.op('regexp')(r'ppt+$')
        ).update({'filetype': 'pptx'}, synchronize_session='evaluate')

        # 파일 타입이 없는 경우 'others'로 설정
        db.session.query(TagFile).filter(
            TagFile.filetype == ''
        ).update({'filetype': 'others'}, synchronize_session='evaluate')

        db.session.commit()
    except Exception as e:
        db.session.rollback()
        raise e
    finally:
        db.session.close()