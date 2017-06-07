# -*- coding: utf-8 -*-

# download niconico comments
# for Python3 on Windows

import xml.etree.ElementTree as ET
import codecs
import subprocess
import datetime
import os

def read_xml(path):
    return ET.fromstring(codecs.open(path, 'r+', 'utf-8').read())

def extract_data(root):
    date, vpos, text = [], [], []
    for r in root:
        if 'date' in r.attrib:
            date.append(int(r.attrib['date']))
            vpos.append(int(r.attrib['vpos']))
            text.append(r.text)
    return date, vpos, text

def download_coment(email, password, target_id, WaybackTime):
    cmd = 'java -jar Saccubus1.66.3.11\saccubus\saccubus.jar %s %s %s %s @DLC' % (email, password, target_id, WaybackTime)
    subprocess.call(cmd.split())

def get_stamp_name(date):
    return str(datetime.datetime.fromtimestamp(date)).replace(':', '.')

def get_WaybackTime(date):
    return str(datetime.datetime.fromtimestamp(date)).replace('-', '/')

def get_WaybackTime_add_minutes(date, minutes=30):
    return str(datetime.datetime.fromtimestamp(date) + datetime.timedelta(minutes=minutes)).replace('-', '/')

email = 'example@email.com'
password = 'password'
target_id = 1397552685
WaybackTime='2114/04/16 12:00:00'
xml_path = u'[out]comment\[1397552685]ご注文はうさぎですか？　第1羽「ひと目で、尋常でないもふもふだと見抜いたよ」.xml' # ask saccubus
save_path = u'comments\\'

WaybackTime='2015-04-16 20.26.53'.replace('-', '/').replace('.', ':') # sometime gets invalid WaybackTime message and abort, then try again reasigning WaybackTime by manual, and add some minutes
# first, download latest 1000 comments, here set WaybackTime just now or futur time
download_coment(email, password, target_id, WaybackTime)

while True:
    # read and check the oldest comment time for now
    xml = read_xml(xml_path)
    date, vpos, text = extract_data(xml)
    first_date = min(date)

    # rename comment file downloaded at last loop
    os.rename(xml_path, '%s' % (save_path + get_stamp_name(first_date) + '.xml'))

    # download 1000 comments from the oldest comment
    WaybackTime = get_WaybackTime_add_minutes(first_date)
    print (WaybackTime)
    download_coment(email, password, target_id, WaybackTime)

