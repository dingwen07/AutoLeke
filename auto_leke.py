import requests
import json
import urllib
import time
from bs4 import BeautifulSoup
from getpass import getpass

headers = {
    "accept":
    "text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.9",
    "accept-language": "zh-CN,zh;q=0.9,en-US;q=0.8,en;q=0.7,zh-TW;q=0.6",
    "cache-control": "max-age=0",
    "content-type": "application/x-www-form-urlencoded",
    "sec-fetch-mode": "navigate",
    "sec-fetch-site": "same-origin",
    "sec-fetch-user": "?1",
    "upgrade-insecure-requests": "1"
}

# Login
username = input('Please input username: ')
password = getpass()
url = 'https://cas.leke.cn/login?service='
login_data = {
    "ty": "yyyy",
    "loginName": username,
    "password": password,
    "authCode": ""
}
print('Logging your in...')
session = requests.Session()
login_response = session.post(url, headers=headers, data=login_data)
try:
    ticket = session.cookies.get('ticket')
    nickname = urllib.parse.unquote(session.cookies.get('_nk_'))
except:
    print('Login failed!')
    exit()
print('Login successful!')
print('Currently logged in as {}'.format(nickname))
print()

# Get course data
print('Requesting course data...')
course_response = session.get(
    'https://course.leke.cn/auth/course/common/lesson/getStudentCourses.htm?userId=&hasShowOverCourse=false'
)
course_data = json.loads(course_response.content.decode())

# Process and print course details
print('All courses in the account:')
counter = 0
for item in course_data['data']['studentCourses']:
    print('[{}] {}'.format(str(counter), item['courseName']))
    counter = counter + 1
course_selection = int(input('Please select a course: '))
print()
#course_selection = 3
course_id = course_data['data']['studentCourses'][course_selection]['courseId']

# Get stuCid
course_html_response = session.get(
    'https://resource.leke.cn/auth/student/resource/study/studyCourseDetail.htm?courseId={}&userId='
    .format(str(course_id)))
soup = BeautifulSoup(course_html_response.content, 'html.parser')
stu_cid = soup.find(id='jStuCid')['value']

# Get lesson data
print('Requesting course details...')
course_referer = 'https://resource.leke.cn/auth/student/resource/study/studyCourseDetail.htm?courseId={}&userId='.format(
    str(course_id))
course_headers = {
    "accept": "application/json, text/javascript, */*; q=0.01",
    "accept-language": "zh-CN,zh;q=0.9,en-US;q=0.8,en;q=0.7,zh-TW;q=0.6",
    "content-type": "application/x-www-form-urlencoded;charset=UTF-8",
    "sec-fetch-mode": "cors",
    "sec-fetch-site": "same-origin",
    "x-requested-with": "XMLHttpRequest",
    "referer": course_referer
}
course_url = 'https://resource.leke.cn/auth/student/resource/study/groupCourseListData.htm'
lesson_response = session.post(
    course_url,
    headers=course_headers,
    data='stuCid={}&curPage=1&pageSize=999'.format(stu_cid))
lesson_data = json.loads(lesson_response.content.decode())

# Get userId
user_id = lesson_data['datas']['page']['dataList'][0]['modifiedBy']

# Process lesson data
print('All lessons in this course:')
chapter_counter = 0
lesson_counter = 0
lesson_pair_dict = {}
for chapter in lesson_data['datas']['page']['dataList']:
    chapter_counter = chapter_counter + 1
    print('Chapter {}: {}'.format(str(chapter_counter), chapter['gcName']))
    for lesson in chapter['coursewareList']:
        print('[{}] {}'.format(str(lesson_counter), lesson['courseName']))
        lesson_pair_dict[str(lesson_counter)] = [
            lesson['stuCwid'], lesson['totalDuration']]
        lesson_counter = lesson_counter + 1
lesson_selection = input('Please select a lesson: ')
print()
#lesson_selection = '9'
stu_cwid = lesson_pair_dict[lesson_selection][0]

# Perform HTTP/GET
lesson_begin_url = 'https://resource.leke.cn/auth/student/resource/study/studyCourseware.htm?stuCwid={}&stuCid={}'.format(
    str(stu_cwid), str(stu_cid))
lesson_begin_data = session.get(lesson_begin_url, headers=course_headers)

# Auto pause
lesson_length = lesson_pair_dict[lesson_selection][1]/60000
print('The length of the lesson is: {} minuts and {} seconds.'.format(
    str(int(lesson_length)), str(int((lesson_length % 1)*60))))
delay = int(lesson_pair_dict[lesson_selection][1]/1000)
delay_str = input('Please input delay (minuts) before submittion: ')
if delay_str != '':
    delay = int(60 * float(delay_str))
for i in range(delay, 0, -1):
    time.sleep(1)
    print("\r Countdown... [{}]".format(i), end="")


# Perform HTTP/POST
save_record_data_raw = '{{"p":{{"userId":"{}","gcId":"{}","duration":0,"frameNumber":0,"isComplete":true,"answerRecord":"","userName":"{}","cwId":"{}","rightRate":0}},"m":"r_saveStudyAnswerRecord_request"}}'.format(
    str(user_id), str(stu_cid), nickname, str(stu_cwid))
save_record_data_encode = urllib.parse.quote(
    save_record_data_raw.encode('utf-8', 'replace'))
save_record_data = 'data={}'.format(save_record_data_encode)
invoke_url = 'http://resource.leke.cn/api/w/res/invoke.htm?ticket={}'.format(
    ticket)
save_record_response = session.post(invoke_url,
                                    headers=headers,
                                    data=save_record_data)
print(save_record_response.content.decode())
