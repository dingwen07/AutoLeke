import leke
import time
import random
from getpass import getpass

def delay_func(delay_time):
    for i in range(delay_time, -1, -1):
        if i % 10 == 9:
            length =  len('Countdown... [{}]'.format(i)) + 2
            print('\r' + ' ' * length, end='')
        print('\r Countdown... [{}]'.format(i), end='')
        time.sleep(1)
    print('\r' + ' ' * 18, end='')
    print('\r Countdown Finished!')


username = input('Username: ')
password = getpass()
s = leke.Session(username, password)

for o in s.courses:
    for m in o.lessons:
        for i in m:
            if(i.status < 3 and i.total_duration != None):
                print('{}: {}'.format(o.name, i.name))

print('支持以下几种模式:')
print('[0] 鸡血模式: 快速完成所有课程的学习.')
print('[1] 修仙模式: 昼夜不停的模拟真人完成所有课程的学习.')
print('[2] 禅模式: 自定义学习时间，只在学习时间内完成所有课程的学习. (NOT YET IMPLEMENTED)')
mode = int(input('输入你的选择: '))

while True:
    s.load_data()
    for o in s.courses:
        for m in o.lessons:
            for i in m:
                if i.status < 3 and i.total_duration != None:
                    print('{}: {}'.format(o.name, i.name))
                    if mode == 0:
                        time.sleep(10)
                        i.submit_record()
                        time.sleep(10)
                    elif mode == 1:
                        i.begin()
                        print('Delay begin!')
                        delay = int(i.total_duration/1000) + \
                            60 * (5 + random.randint(5, 10))
                        delay_func(delay)
                        print('Submit record!')
                        i.submit_record()
                        print('Wait before start next class...\nDelay begin!')
                        delay = 60 * random.randint(10, 20)
                        delay_func(delay)
                    else:
                        print('ERR')
                        time.sleep(5)
                        exit()
    print('Wait for one hour...')
    delay = 60 * 60
    delay_func(delay)
