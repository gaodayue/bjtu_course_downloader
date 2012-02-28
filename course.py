# -*- coding: utf-8 -*-
#! /usr/bin/env python
import urllib, urllib2, cookielib, random
from BeautifulSoup import BeautifulSoup

DOMAIN = "http://202.112.154.91"
VCODE_URL = DOMAIN + "/validateCodeAction.do"
LOGIN_URL = DOMAIN + "/loginAction.do"
COURSE_URL = DOMAIN + "/xskbAction.do?actionType=1"

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
        if len(tds) > 10:
            course = {}
            course['id'] = tds[1].text      #课序号
            course['name'] = tds[2].text    # 课程名
            course['order'] = tds[3].text   # 课序号
            course['credit'] = tds[4].text  # 学分 
            course['t'] = tds[7].text       # 教师
            time = {}
            time['week'] = tds[10].text     # 周次
            time['d'] = tds[11].text        # 星期几
            time['st'] = tds[12].text       # 起始节次
            time['lt'] = tds[13].text       # 持续节次
            time['where'] = tds[16].text    # 地点
            course['times'] = [time]        # 时间
            courses.append(course)
        else:
            lastcourse = courses[-1]
            time = {}
            time['week'] = tds[0].text     # 周次
            time['d'] = tds[1].text        # 星期几
            time['st'] = tds[2].text       # 起始节次
            time['lt'] = tds[3].text       # 持续节次
            time['where'] = tds[6].text    # 地点
            lastcourse['times'].append(time)
    return courses
    
