############### INFO ###############

# 1. 저장된 링크를 한 줄씩 불러옴
# 2. 포트 번호 삭제
# 3. 데이터베이스에 없다면 저장
# 4. 루트 도메인이라면 그렇다고 표시 (아니라면 Default 값으로)
# 5. 해당되는 루트 도메인과 연결

############### FUNCTION ###############
def rootdomain(cur):
    cur.execute("SELECT sub_url FROM domain_sub") #수정필요
    datas = cur.fetchall()

    notfoundcount = 0
    s = set()
    for data in datas:
        line = data[0]
        print("DATA: " + line)

        if ":" in line:
            tmp = line.split(":")
            line = tmp[0] # 포트 번호 삭제

        found = 0
        tmp = line.split(".")

        # tmp에서 com이 나오는 인덱스 번호를 found에 저장함
        if tmp.count('com') == 1:
            found = tmp.index('com')
            found = found - 1

            tmplist = tmp[found:]
            tmpstr = ".".join(tmplist)
            s.add(tmpstr)
        elif (tmp.count('kr') == 1):
            if tmp.count('or') == 1:
                found = tmp.index('or')
                found = found - 1

                tmplist = tmp[found:]
                tmpstr = ".".join(tmplist)
                s.add(tmpstr)
            elif tmp.count('co') == 1:
                found = tmp.index('co')
                found = found - 1

                tmplist = tmp[found:]
                tmpstr = ".".join(tmplist)
                s.add(tmpstr)
            else:
                found = tmp.index('kr')
                found = found - 1

                tmplist = tmp[found:]
                tmpstr = ".".join(tmplist)
                s.add(tmpstr)
        elif tmp.count('jp') == 1:
            found = tmp.index('jp')
            found = found - 1

            tmplist = tmp[found:]
            tmpstr = ".".join(tmplist)
            s.add(tmpstr)
        elif tmp.count('net') == 1:
            found = tmp.index('net')
            found = found - 1

            tmplist = tmp[found:]
            tmpstr = ".".join(tmplist)
            s.add(tmpstr)
        elif ((tmp.count('co') == 1) and (tmp.count('uk') == 1)):
            found = tmp.index('co')
            found = found - 1

            tmplist = tmp[found:]
            tmpstr = ".".join(tmplist)
            s.add(tmpstr)
        elif tmp.count('ca') == 1:
            found = tmp.index('ca')
            found = found - 1

            tmplist = tmp[found:]
            tmpstr = ".".join(tmplist)
            s.add(tmpstr)
        elif tmp.count('uz') == 1:
            found = tmp.index('uz')
            found = found - 1

            tmplist = tmp[found:]
            tmpstr = ".".join(tmplist)
            s.add(tmpstr)
        elif tmp.count('in') == 1:
            found = tmp.index('in')
            found = found - 1

            tmplist = tmp[found:]
            tmpstr = ".".join(tmplist)
            s.add(tmpstr)
        elif tmp.count('cn') == 1:
            found = tmp.index('cn')
            found = found - 1

            tmplist = tmp[found:]
            tmpstr = ".".join(tmplist)
            s.add(tmpstr)
        elif ((tmp.count('co') == 1) and (tmp.count('uk') == 1)):
            found = tmp.index('co')
            found = found - 1

            tmplist = tmp[found:]
            tmpstr = ".".join(tmplist)
            s.add(tmpstr)
        else:
            notfoundcount = notfoundcount + 1

    for line in s:
        cur.execute("INSERT IGNORE INTO domain_root(root_url) VALUES('{0}')".format(line))
    
    return 0