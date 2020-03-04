import leke
import time
import random
import json
from getpass import getpass
from global_library import *


def delay_func(delay_time):
    for time_left in range(delay_time, -1, -1):
        if time_left % 10 == 9:
            length = len('Countdown... [{}]'.format(time_left)) + 3
            print('\r' + ' ' * length, end='')
        print('\r Countdown... [{}]'.format(time_left), end='')
        time.sleep(1)
    print('\r' + ' ' * 18, end='')
    print('\r Countdown Finished!')


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

print('你有以下课时未完成学习:')
for course in s.courses:
    for lesson in course:
        if lesson.status < 3 and lesson.total_duration is not None:
            print('{}: {}'.format(course.name, lesson.name))
print()
print('支持以下几种模式:')
print('[0] 鸡血模式: 快速完成所有课程的学习.')
print('[1] 修仙模式: 昼夜不停的模拟真人完成所有课程的学习.')
print('[2] 禅模式: 自定义学习时间段，只在学习时间内完成所有课程的学习. ')
mode = int(input_check('输入你的选择: ', 1, [0, 1, 2], "你输入的数据有误：数据应该为整数！", "你只能输入0, 1, 2这三个整数中的一个"))
print()
if mode == 2:
    print('按照下面的示例格式化你的输入')
    print('Sample input: 7-12 14-16 18-22')
    time_ranges = format_time_range_input(input('输入学习时间段: '))
print('你有以下课程:')
for index in range(0, len(s.courses)):
    print('[{}] {}'.format(str(index), s.courses[index].name))
sequence = list(range(0, len(s.courses)))
sequence_input = input('输入排序, 用空格分隔: ')
print()
if sequence_input != '':
    sequence = sequence_input.split(' ')
    for index in range(0, len(sequence)):
        try:
            sequence[index] = int(sequence[index])
        except ValueError:
            pass

while True:
    for course_index in sequence:
        course = s.courses[course_index]
        for lesson in course:
            if lesson.status < 3 and lesson.total_duration is not None:
                print('{}: {}'.format(course.name, lesson.name))
                if mode == 0:
                    time.sleep(10)
                    lesson.submit_record()
                    time.sleep(10)
                elif mode == 1:
                    lesson.begin()
                    print('Delay begin!')
                    delay = int(lesson.total_duration / 1000) + 60 * (5 + random.randint(5, 10))
                    delay_func(delay)
                    print('Submit record!')
                    lesson.submit_record()
                    print('Wait before start next class...\nDelay begin!')
                    delay = 60 * random.randint(10, 20)
                    delay_func(delay)
                    print()
                elif mode == 2:
                    lesson.begin()
                    print('Delay begin!')
                    delay = int(lesson.total_duration / 1000) + 60 * (5 + random.randint(5, 10))
                    delay_func(delay)
                    while not check_time_range(time_ranges):
                        print('Out of study range, submission pending...')
                        delay_func(1800)
                    print('Submit record!')
                    lesson.submit_record()
                    print('Wait before start next class...\nDelay begin!')
                    delay = 60 * random.randint(10, 20)
                    delay_func(delay)
                    print()
                else:
                    print('ERR')
                    time.sleep(5)
                    exit()

    print('所有课程已完成!')
    print('Wait for one hour...')
    delay = 60 * 60
    delay_func(delay)
    print()
    s.load_data()
