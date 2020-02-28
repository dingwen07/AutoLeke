import requests
import json
import urllib
from bs4 import BeautifulSoup

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


class Session(object):
    '''
    request_session = None
    courses = []
    '''

    def __init__(self, login_name, password):
        super().__init__()
        login_url = 'https://cas.leke.cn/login?service='
        login_data = {
            "ty": "yyyy",
            "loginName": login_name,
            "password": password,
            "authCode": ""
        }
        self.request_session = requests.Session()
        login_response = self.request_session.post(login_url, headers=headers, data=login_data)
        self.courses = []
        self.load_data()

    def __iter__(self):
        return SessionIterator(self.courses)

    def load_data(self):
        self.courses = []
        course_response = self.request_session.get(
            'https://course.leke.cn/auth/course/common/lesson/getStudentCourses.htm?userId=&hasShowOverCourse=false')
        course_data = json.loads(course_response.content.decode())
        for item in course_data['data']['studentCourses']:
            self.courses.append(Course(self.request_session, item['courseId'], item['courseName']))


class Course(object):
    '''
    course_id = 0
    stu_cid = 0
    name = ''
    request_session = None
    lessons = []
    '''

    def __init__(self, request_session, course_id, name):
        super().__init__()
        self.course_id = course_id
        self.name = name
        self.request_session = request_session
        # Get stuCid
        course_html_response = self.request_session.get(
            'https://resource.leke.cn/auth/student/resource/study/studyCourseDetail.htm?courseId={}&userId='.format(
                str(self.course_id)))
        soup = BeautifulSoup(course_html_response.content, 'html.parser')
        self.stu_cid = int(soup.find(id='jStuCid')['value'])
        self.lessons = []
        self.load_data()

    def __iter__(self):
        return CourseIterator(self.lessons)

    def load_data(self):
        course_html_response = self.request_session.get(
            'https://resource.leke.cn/auth/student/resource/study/studyCourseDetail.htm?courseId={}&userId='.format(
                str(self.course_id)))
        soup = BeautifulSoup(course_html_response.content, 'html.parser')
        self.stu_cid = int(soup.find(id='jStuCid')['value'])
        self.lessons = []
        course_referer = 'https://resource.leke.cn/auth/student/resource/study/studyCourseDetail.htm?courseId={}&userId='.format(
            str(self.course_id))
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
        lesson_response = self.request_session.post(course_url, headers=course_headers,
                                                    data='stuCid={}&curPage=1&pageSize=999'.format(str(self.stu_cid)))
        lesson_data = json.loads(lesson_response.content.decode())
        user_id = lesson_data['datas']['page']['dataList'][0]['modifiedBy']
        for c in lesson_data['datas']['page']['dataList']:
            chapter = []
            for l in c['coursewareList']:
                chapter.append(
                    Lesson(self.request_session, course_headers, user_id, self.stu_cid, l['stuCwid'], l['status'],
                           l['totalDuration'], l['courseName']))
            self.lessons.append(chapter)


class Lesson(object):
    '''
    ticket = ''
    nickname = ''
    user_id = 0
    stu_cid = 0
    stu_cwid = 0
    status = 1
    total_duration = 0
    request_session = None
    name = ''
    course_headers = {}
    '''

    def __init__(self, request_session, course_headers, user_id, stu_cid, stu_cwid, status, total_duration, name):
        super().__init__()
        self.request_session = request_session
        self.course_headers = course_headers
        self.user_id = user_id
        self.stu_cid = stu_cid
        self.stu_cwid = stu_cwid
        self.status = status
        self.total_duration = total_duration
        self.name = name
        self.ticket = self.request_session.cookies.get('ticket')
        self.nickname = urllib.parse.unquote(self.request_session.cookies.get('_nk_'))

    def begin(self):
        lesson_begin_url = 'https://resource.leke.cn/auth/student/resource/study/studyCourseware.htm?stuCwid={}&stuCid={}'.format(
            str(self.stu_cwid), str(self.stu_cid))
        lesson_begin_data = self.request_session.get(lesson_begin_url, headers=self.course_headers)

    def submit_record(self):
        save_record_data_raw = '{{"p":{{"userId":"{}","gcId":"{}","duration":0,"frameNumber":0,"isComplete":true,"answerRecord":"","userName":"{}","cwId":"{}","rightRate":0}},"m":"r_saveStudyAnswerRecord_request"}}'.format(
            str(self.user_id), str(self.stu_cid), self.nickname, str(self.stu_cwid))
        save_record_data_encode = urllib.parse.quote(save_record_data_raw.encode('utf-8', 'replace'))
        save_record_data = 'data={}'.format(save_record_data_encode)
        invoke_url = 'http://resource.leke.cn/api/w/res/invoke.htm?ticket={}'.format(self.ticket)
        save_record_response = self.request_session.post(invoke_url, headers=headers, data=save_record_data)
        return save_record_response


class SessionIterator(object):

    def __init__(self, data):
        super().__init__()
        self.data = data
        self.now_course = 0
        self.it = iter(self.data[0])

    def __iter__(self):
        return self

    def __next__(self):
        while self.now_course < len(self.data):
            try:
                return next(self.it)
            except StopIteration:
                self.now_course = self.now_course + 1
                if self.now_course < len(self.data):
                    self.it = iter(self.data[self.now_course])
        raise StopIteration


class CourseIterator(object):

    def __init__(self, data):
        super().__init__()
        self.data = data
        self.now_chapter = 0
        self.now_lesson = 0

    def __iter__(self):
        return self

    def __next__(self):
        while self.now_chapter < len(self.data):
            while self.now_lesson < len(self.data[self.now_chapter]):
                self.now_lesson = self.now_lesson + 1
                return self.data[self.now_chapter][self.now_lesson - 1]
            self.now_chapter = self.now_chapter + 1
            self.now_lesson = 0
        raise StopIteration
