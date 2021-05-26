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
        login_response = self.request_session.post(login_url,
                                                   headers=headers,
                                                   data=login_data)
        self.courses = []
        self.load_data()

    def __iter__(self):
        return SessionIterator(self.courses)

    def load_data(self):
        self.courses = []
        course_response = self.request_session.get(
            'https://course.leke.cn/auth/course/common/lesson/getStudentCourses.htm?userId=&hasShowOverCourse=false'
        )
        course_data = json.loads(course_response.content.decode())
        for item in course_data['data']['studentCourses']:
            if item['courseType'] == 2:
                self.courses.append(
                    Course(
                        self.request_session, {
                            'course_id': item['courseId'],
                            'course_type': item['courseType'],
                            'name': item['courseName']
                        }))


class Course(object):

    '''
    course_id = 0
    stu_cid = 0
    name = ''
    request_session = None
    lessons = []
    '''
    def __init__(self, request_session, data):
        super().__init__()
        self.data = {}
        self.data['course_id'] = data['course_id']
        self.data['name'] = data['name']
        self.name = data['name']
        self.data['course_type'] = data['course_type']
        self.course_type = data['course_type']
        self.request_session = request_session
        # Get stuCid
        self.course_referer = 'https://webapp.leke.cn/page/ltcr/mall/my-lesson-detail?courseId={}'.format(
            str(self.data['course_id']))
        self.course_headers = {
            "accept": "application/json, text/javascript, */*; q=0.01",
            "accept-language":
                "zh-CN,zh;q=0.9,en-US;q=0.8,en;q=0.7,zh-TW;q=0.6",
            "content-type": "application/json",
            "sec-fetch-mode": "cors",
            "sec-fetch-site": "same-origin",
            "x-requested-with": "XMLHttpRequest",
            "referer": self.course_referer
        }
        self.course_url = 'https://webapp.leke.cn/proxy/resource/auth/student/resource/study/groupStudentCourseListDataNew.htm'
        post_data = json.loads('{"courseId": "","lastNodeId": 0,"pageSize": 10}')
        post_data['courseId'] = str(self.data['course_id'])
        self.lesson_response = self.request_session.post(
            self.course_url,
            headers=self.course_headers,
            data=json.dumps(post_data))
        self.data['stu_cid'] = json.loads(self.lesson_response.content.decode())['data'][0]['singleCourseList'][0]['stuCid']
        self.lessons = []
        self.load_data()

    def __iter__(self):
        return CourseIterator(self.lessons)

    def load_data(self):
        post_data = json.loads('{"courseId": "","lastNodeId": 0,"pageSize": 10}')
        post_data['courseId'] = str(self.data['course_id'])
        course_referer = 'https://resource.leke.cn/auth/student/resource/study/studyCourseDetail.htm?courseId={}&userId='.format(
            str(self.data['course_id']))
        course_headers = {
            "accept": "application/json, text/javascript, */*; q=0.01",
            "accept-language":
            "zh-CN,zh;q=0.9,en-US;q=0.8,en;q=0.7,zh-TW;q=0.6",
            "content-type": "application/x-www-form-urlencoded;charset=UTF-8",
            "sec-fetch-mode": "cors",
            "sec-fetch-site": "same-origin",
            "x-requested-with": "XMLHttpRequest",
            "referer": course_referer
        }
        course_url = 'https://resource.leke.cn/auth/student/resource/study/groupCourseListData.htm'
        lesson_response = self.request_session.post(
            course_url,
            headers=course_headers,
            data='stuCid={}&curPage=1&pageSize=999'.format(
                str(self.data['stu_cid'])))
        lesson_data = json.loads(lesson_response.content.decode())
        user_id = lesson_data['datas']['page']['dataList'][0]['modifiedBy']
        for c in lesson_data['datas']['page']['dataList']:
            chapter = []
            for l in c['coursewareList']:
                chapter.append(
                    Lesson(
                        self.request_session, course_headers, {
                            'user_id': user_id,
                            'stu_cid': self.data['stu_cid'],
                            'stu_cwid': l['stuCwid'],
                            'status': l['status'],
                            'total_duration': l['totalDuration'],
                            'name': l['courseName']
                        }))
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
    def __init__(self, request_session, course_headers, data):
        super().__init__()
        self.data = {}
        self.request_session = request_session
        self.course_headers = course_headers
        self.data['user_id'] = data['user_id']
        self.data['stu_cid'] = data['stu_cid']
        self.data['stu_cwid'] = data['stu_cwid']
        self.data['status'] = data['status']
        self.status = data['status']
        self.data['total_duration'] = data['total_duration']
        self.total_duration = data['total_duration']
        self.data['name'] = data['name']
        self.name = data['name']
        self.ticket = self.request_session.cookies.get('ticket')
        self.nickname = urllib.parse.unquote(
            self.request_session.cookies.get('_nk_'))

    def begin(self):
        lesson_begin_url = 'https://resource.leke.cn/auth/student/resource/study/studyCourseware.htm?stuCwid={}&stuCid={}'.format(
            str(self.data['stu_cwid']), str(self.data['stu_cid']))
        lesson_begin_data = self.request_session.get(
            lesson_begin_url, headers=self.course_headers)

    def submit_record(self):
        save_record_data_raw = '{{"p":{{"userId":"{}","gcId":"{}","duration":0,"frameNumber":0,"isComplete":true,"answerRecord":"","userName":"{}","cwId":"{}","rightRate":0}},"m":"r_saveStudyAnswerRecord_request"}}'.format(
            str(self.data['user_id']), str(self.data['stu_cid']),
            self.nickname, str(self.data['stu_cwid']))
        save_record_data_encode = urllib.parse.quote(
            save_record_data_raw.encode('utf-8', 'replace'))
        save_record_data = 'data={}'.format(save_record_data_encode)
        invoke_url = 'http://resource.leke.cn/api/w/res/invoke.htm?ticket={}'.format(
            self.ticket)
        save_record_response = self.request_session.post(invoke_url,
                                                         headers=headers,
                                                         data=save_record_data)
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
