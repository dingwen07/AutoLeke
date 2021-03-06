import urllib
import global_library
import leke
import json
from getpass import getpass
import os

credential_available = False
try:
    with open('leke_credential.json', 'r') as load_f:
        load_credential = json.load(load_f)
    username = load_credential['login_name']
    password = load_credential['password']
    credential_available = True
except Exception:
    credential_available = False
finally:
    if credential_available:
        selection = input('Use local credential? [Y/N]? ')
        if not (selection.lower() == 'y' or selection == ''):
            username = input('Username: ')
            password = getpass()
    else:
        username = input('Username: ')
        password = getpass()

s = leke.Session(username, password)

confirm = "y"
while confirm.upper() == "Y" or confirm.upper() == "YES":
    print('你有以下课程:')
    for index in range(0, len(s.courses)):
        print('[{}] {}'.format(str(index), s.courses[index].name))
    course_selection = int(global_library.input_check('请选择课程: ', 1, range(0, len(s.courses)), "你输入的数据有误：数据应该为整数！",
                                                      "你只能输入 0 ~ " + str(len(s.courses) - 1) + "这个范围内的整数！"))

    course = s.courses[course_selection]

    print('你有以下课时:')
    temp = 0
    for lesson in course:
        print('[{}] {}'.format(str(temp), lesson.name))
        temp = temp + 1
    lesson_selection = int(global_library.input_check('请选择课时（输入-1重新选择课程）: ', 1, range(-1, temp), "你输入的数据有误：数据应该为整数！",
                                                      "你只能输入 -1 ~ " + str(temp - 1) + "这个范围内的整数！"))
    del temp

    while lesson_selection == -1:
        print('你有以下课程:')
        for index in range(0, len(s.courses)):
            print('[{}] {}'.format(str(index), s.courses[index].name))
        course_selection = int(global_library.input_check('请选择课程: ', 1, range(0, len(s.courses)), "你输入的数据有误：数据应该为整数！",
                                                          "你只能输入 0 ~ " + str(len(s.courses) - 1) + "这个范围内的整数！"))

        course = s.courses[course_selection]

        print('你有以下课时:')
        temp = 0
        for lesson in course:
            print('[{}] {}'.format(str(temp), lesson.name))
            temp = temp + 1
        lesson_selection = int(global_library.input_check('请选择课时（输入-1重新选择课程）: ', 1, range(-1, temp), "你输入的数据有误：数据应该为整数！",
                                                          "你只能输入 -1 ~ " + str(temp - 1) + "这个范围内的整数！"))
        del temp

    lesson = leke.CourseIterator(course.lessons)
    for i in range(0, lesson_selection):
        next(lesson)
    lesson = next(lesson)
    lesson.begin()
    save_record_data_raw = '{{"p":{{"flag":1,"userId":"{}","gcId":"{}","userName":"{}","cwId":"{}","lockForEdit":"0"}},"m":"r_loadCourseware_request"}}'.format(
        str(lesson.data['user_id']), str(lesson.data['stu_cid']), lesson.nickname, str(lesson.data['stu_cwid']))
    save_record_data_encode = urllib.parse.quote(save_record_data_raw.encode('utf-8', 'replace'))
    save_record_data = 'data={}'.format(save_record_data_encode)
    invoke_url = 'https://resource.leke.cn/api/w/res/invoke.htm?ticket={}'.format(lesson.ticket)
    save_record_response = lesson.request_session.post(invoke_url, headers=leke.headers, data=save_record_data)
    if json.loads(save_record_response.content.decode())['p']['datas']['voicePath'][-1] == "8":
        while True:
            fileName = input("请设置文件名: ")
            if ('/' in fileName) or ('\\' in fileName) or (':' in fileName) or ('*' in fileName) or (
                    '\"' in fileName) or (
                    '<' in fileName) or ('>' in fileName) or ('|' in fileName) or ('?' in fileName):
                print(
                    "你输入的文件名中包含至少一个非法字符 / \\ : * \" < > | ? 无法使用他们作为文件名！")
            else:
                break
        data = json.loads(save_record_response.content.decode())['p']['datas']['voicePath']
        if os.path.isfile('{}.mp4'.format(fileName)):
            print("文件已存在！")
            while True:
                checkInput = input("你要覆盖它吗？(y/n)")
                if checkInput.upper() == "Y" or checkInput.upper() == "YES":
                    os.system(f'ffmpeg -i {data} -c copy \"{fileName}.mp4\" -y')
                    exit()
                elif checkInput.upper() == "N" or checkInput.upper() == "NO":
                    exit()
                else:
                    print("无法识别你输入的文字！")
        else:
            os.system(f'ffmpeg -i {data} -c copy \"{fileName}.mp4\"')
            print("你的视频已经下载至 " + os.getcwd())
    else:
        print("这一个课时是可翻页的，无法进行下载！")

    while True:
        confirm = input("需要继续下载其他视频吗（Y/N）？")
        if confirm.upper() == "Y" or confirm.upper() == "YES" or confirm.upper() == "N" or confirm.upper() == "NO":
            break
        else:
            print("输入有误，请重新输入！")


