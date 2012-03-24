# -*- coding: utf-8 -*-
#! /usr/bin/env python
import urllib, urllib2, cookielib, random
from BeautifulSoup import BeautifulSoup

DOMAIN = "http://202.112.154.91"
VCODE_URL = DOMAIN + "/validateCodeAction.do"
LOGIN_URL = DOMAIN + "/loginAction.do"
COURSE_URL = DOMAIN + "/xskbAction.do?actionType=1"
LOGOUT_URL = DOMAIN + "/logout.do"

cookieJar = cookielib.CookieJar()
opener= urllib2.build_opener(urllib2.HTTPCookieProcessor(cookieJar))
opener.addheaders = [('User-Agent', "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/535.11 (KHTML, like Gecko) Chrome/17.0.963.56 Safari/535.11")]

# 1st, get_session_cookie
opener.open(DOMAIN)

def get_vcode_image():
    "返回验证码图片的字节流"
    params = {"random":random.random()}
    vcode_url = VCODE_URL + "?" + urllib.urlencode(params)
    resp = opener.open(vcode_url)
    return resp.read()

def save_image():
    "工具方法，将验证码图片直接保存到本地文件'yzm.jpeg'中"
    file = open("yzm.jpeg", "w")
    file.write(get_vcode_image())
    file.close()

def login(sno, password, vcode):
    """
    登录选课系统，成功返回True，失败False。参数：
    sno         学号
    password    密码
    vcode       验证码
    """
    params = {}
    params['zjh'] = sno
    params['mm'] = password
    params['v_yzm'] = vcode
    data = urllib.urlencode(params)
    resp = opener.open(LOGIN_URL, data)
    # 如果content-type中的charset=gb2312,则登录成功，否则为登录失败
    soup = BeautifulSoup(resp.read())
    return soup.originalEncoding == 'gb2312'

def logout():
    """
    登出系统
    """
    params = {'loginType':'platformLogin'}
    opener.open(LOGOUT_URL, urllib.urlencode(params))

def get_courses():
    """
    返回所有课程信息的列表，必须在login()成功后调用
    """
    courses = []
    resp = opener.open(COURSE_URL)
    soup = BeautifulSoup(resp.read(), fromEncoding='gbk')
    table = soup.findAll(attrs={"class":"displayTag"})[1]
    for tr in table.tbody.findAll("tr"):
        tds = tr.findAll("td")
        def get_course_item(item_start_pos):
            """
            得到课程的时间地点信息
            'item_start_pos': 该信息在表格中的开始位置
            """
            item = {}
            info = [tds[x].text for x in \
                    range(item_start_pos, item_start_pos + 7)]
            # 1. 周次列表
            # [1,3,5,7,9]表示第1,3,5,7,9周上课
            item['week'] = week_to_list(info[0]) 
            # 2. 星期几[1-7]
            item['d'] = int(info[1])    
            # 起始节次于持续节次
            st, lt = int(info[2]), int(info[3])
            # 3. 节次,[1,2]表示第一第二节上课
            item['session'] = range(st, st + lt)
            # 4. 地点
            item['where'] = info[6]
            return item
        if len(tds) > 10:
            course = {}
            course['cid'] = tds[1].text     #课程号
            course['name'] = tds[2].text    # 课程名
            course['order'] = tds[3].text   # 课序号
            course['credit'] = tds[4].text  # 学分 
            course['teacher'] = tds[7].text # 教师
            item = get_course_item(10) 
            course['items'] = [item]
            courses.append(course)
        else:
            lastcourse = courses[-1]
            item = get_course_item(0)
            lastcourse['items'].append(item)
    return courses

def week_to_list(week):
    if '-' in week:
        start,end = week.split('-')
        return range(get_number(start), get_number(end) + 1)
    if ',' in week:
        return [get_number(x) for x in week.split(',')]
    return [get_number(week)]

def get_number(text):
    """
    return number contained in 'text'
    get_number(u'a12b') => 12
    get_number(u'aa123bb456') => 123456
    """
    digits = [x for x in text if x.isdigit()]
    return int(''.join(digits))
