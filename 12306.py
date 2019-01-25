#!/usr/bin/env python
# _*_ coding:utf-8 _*_
__author__ = 'DH'

import qrcode
import requests
import json
import os, base64, threading, time, re, datetime
from urllib import parse

from urllib import request
from http import cookiejar

from conf import START_TIME, FROM_NAME, TO_NAME, FROM_STATION, TO_STATION, PASSENGER_NAME, ID_NUM, MOBILE_NUM


# "1,0,1,姓名,1,身份证号码,手机号码,N"
PASSENGER_TICKET_STR = "1,0,1,"+PASSENGER_NAME+",1,"+ID_NUM+","+MOBILE_NUM+",N"
# "姓名,1,身份证号码,1_"
OLD_PASSENGER_STR = PASSENGER_NAME+",1,"+ID_NUM+",1_"

# img = qrcode.make('hello, qrcode')
# img.save('test.png')


'''
参数 version 表示生成二维码的尺寸大小，取值范围是 1 至 40，最小尺寸 1 会生成 21 * 21 的二维码，version 每增加 1，生成的二维码就会添加 4 尺寸，例如 version 是 2，则生成 25 * 25 的二维码。 
参数 error_correction 指定二维码的容错系数，分别有以下4个系数： 
1.ERROR_CORRECT_L: 7%的字码可被容错 
2.ERROR_CORRECT_M: 15%的字码可被容错 
3.ERROR_CORRECT_Q: 25%的字码可被容错 
4.ERROR_CORRECT_H: 30%的字码可被容错 
参数 box_size 表示二维码里每个格子的像素大小。 
参数 border 表示边框的格子厚度是多少（默认是4）。 
运行代码后，会在代码的当前目录下生成一个test.png的二维码
'''
# qr = qrcode.QRCode(
#     version=1,
#     error_correction=qrcode.constants.ERROR_CORRECT_L,
#     box_size=10,
#     border=2,
# )
# qr.add_data('hello, qrcode')
# qr.make(fit=True)
# img = qr.make_image()
# img.save('123.png')


# qrcode.make('hello, qrcode').show()


CREATE_QR64 = 'https://kyfw.12306.cn/passport/web/create-qr64'
CHECK_QR = 'https://kyfw.12306.cn/passport/web/checkqr'
UAMTK = 'https://kyfw.12306.cn/passport/web/auth/uamtk'
UAM_AUTH_CLIENT = 'https://kyfw.12306.cn/otn/uamauthclient'
CHECK_USER = 'https://kyfw.12306.cn/otn/login/checkUser'
GET_PASSENGER_DTOS = 'https://kyfw.12306.cn/otn/confirmPassenger/getPassengerDTOs'
CHECK_ORDER_INFO = 'https://kyfw.12306.cn/otn/confirmPassenger/checkOrderInfo'
GET_QUEUE_COUNT = 'https://kyfw.12306.cn/otn/confirmPassenger/getQueueCount'
CONFIRM_SINGLE_FOR_QUEUE = 'https://kyfw.12306.cn/otn/confirmPassenger/confirmSingleForQueue'

# TODO 7.排队等待
QUERY_ORDER_WAIT_TIME = 'https://kyfw.12306.cn/otn/confirmPassenger/queryOrderWaitTime?random=%s&tourFlag=dc&_json_att=&REPEAT_SUBMIT_TOKEN=%s'
# TODO 8.订单结果 submitStatus为true购票成功
RESULT_ORDER_FOR_DCQUEUE = 'https://kyfw.12306.cn/otn/confirmPassenger/resultOrderForDcQueue'

# TODO  查票 时间 站点这里改 请求多次  waitCount=0 && orderId有值是结束
QUERY = f'https://kyfw.12306.cn/otn/leftTicket/queryZ?leftTicketDTO.train_date={START_TIME}&leftTicketDTO.from_station={FROM_STATION}&leftTicketDTO.to_station={TO_STATION}&purpose_codes=ADULT'

#  预定 cookie uamauthclient中获取
SUBMIT_ORDER_REQUEST = 'https://kyfw.12306.cn/otn/leftTicket/submitOrderRequest'

INIT_DC = 'https://kyfw.12306.cn/otn/confirmPassenger/initDc'

HEADERS = { 'Content-Type': 'application/x-www-form-urlencoded' }


def createqr64():

    data = {'appid': 'otn'}

    response = requests.post(CREATE_QR64, data=data, headers=HEADERS)
    data = json.loads(response.text)
    # print(data)

    if data['result_code'] == '0':

        img = data['image']  # 'data:image/png;base64,' + data['image']

        with open('qrcode.png', 'wb') as f:
            f.write(base64.b64decode(img))

        return data['uuid']

    else:
        return '-1'


def checkqr(uuid):
    data = {'appid': 'otn', 'uuid': uuid}

    response = requests.post(CHECK_QR, data=data, headers=HEADERS)

    # print('response.headers', response.headers)

    cookie_value = ''
    for key, value in response.cookies.items():
        cookie_value += key + '=' + value + ';'




    data = json.loads(response.text)
    print(data)

    result_code = data['result_code']

    if result_code == '2':
        print(cookie_value)
        return cookie_value
    else:
        return '-1'

# 获取newapptk
def uamtk(cookie):
    data = {'appid': 'otn'}

    headers = {
        'Cookie': cookie,
        'Content-Type': 'application/x-www-form-urlencoded'
    }
    response = requests.post(UAMTK, data=data, headers=headers, )
    data = json.loads(response.text)
    # print(data)
    if data['result_code'] == 0:
        return data['newapptk']
    else:
        print(data['result_message'])
        return '-1'


# 获取apptk
def uam_auth_client(newapptk):
    data = {'tk': newapptk}
    response = requests.post(UAM_AUTH_CLIENT, data=data, headers=HEADERS)
    data = json.loads(response.text)
    print(data)

    cookie_value = ''
    for key, value in response.cookies.items():
        cookie_value += key + '=' + value + ';'

    if data['result_code'] == 0:
        return cookie_value
    else:
        return '-1'

def check_user(cookie):
    headers = {
        'Cookie': cookie,
        'Content-Type': 'application/x-www-form-urlencoded'
    }
    response = requests.post(CHECK_USER, headers=headers)

    data = json.loads(response.text)
    print(data)
    if data['data']['flag'] == True:
        print('登录成功了')
        return '1'
    else:
        return '-1'


# 查票
def query():
    response = requests.get(QUERY)

    print(response.text)

    data = json.loads(response.text)
    # print(data)

    result = data['data']['result']
    for i in result:
        tem_list = i.split('|')

        print(tem_list[29])
        if tem_list[29] != '' and tem_list[29] != '无':
            print('硬座', tem_list[29])
            # 有票 订票 先检测用户登录是否过期 checkuser

            secretStr = tem_list[0]
            train_no = tem_list[2]
            stationTrainCode = tem_list[3]
            fromStationTelecode = tem_list[6]
            toStationTelecode = tem_list[7]
            leftTicket = tem_list[12]
            train_location = tem_list[15]

            uuid = createqr64()
            while True:
                cookie = checkqr(uuid)
                if cookie != '-1':
                    newapptk = uamtk(cookie)
                    if newapptk != '-1':
                        cookie1 = uam_auth_client(newapptk)
                        if cookie1 != '-1':
                            check_user_result = check_user(cookie1)
                            if check_user_result != '-1':
                                submitResult = submitOrderRequest(secretStr, cookie1)
                                if submitResult != '-1':
                                    repeat_submit_token, key_check_ischange = initDc(cookie1)
                                    if repeat_submit_token:
                                        getPassenger = getPassengerDTOs(repeat_submit_token, cookie1)
                                        if getPassenger != '-1':
                                            checkOrder = checkOrderInfo(repeat_submit_token, cookie1)
                                            if checkOrder != '-1':
                                                queue = getQueueCount(train_no, stationTrainCode, fromStationTelecode, toStationTelecode, leftTicket, train_location, repeat_submit_token, cookie1)
                                                if queue != '-1':
                                                    confirm = confirmSingleForQueue(key_check_ischange, leftTicket, train_location, repeat_submit_token, cookie1)
                                                    if confirm != '-1':
                                                        while True:
                                                            orderId = queryOrderWaitTime(repeat_submit_token, cookie1)
                                                            if orderId != '-1':
                                                                resultOrderForDcQueue(orderId, repeat_submit_token, cookie1)
                                                                break




                    break


            break

        else:
            print('无票', tem_list[29])
            return '-1'

        # tem_list.pop(0)
        # del tem_list[11]
        # print(tem_list)


def submitOrderRequest(secretStr, cookie):
    data = {
        "secretStr": parse.unquote(secretStr),  # 解密
        "train_date": START_TIME,  # "2019-02-04"
        "back_train_date": datetime.datetime.now().strftime('%Y-%m-%d'),  # 当前时间 2019-01-23
        "query_from_station_name": FROM_NAME,  # "广州"
        "query_to_station_name": TO_NAME,  # "深圳"
        "tour_flag": "dc",
        "purpose_codes": "ADULT",
        "undefined": ""
    }
    headers = {
        'Cookie': cookie,
        'Content-Type': 'application/x-www-form-urlencoded'
    }

    print('data:', data)
    print('headers:', headers)

    response = requests.post(SUBMIT_ORDER_REQUEST, data=data, headers=headers)

    print('预定:', response.text)
    data = json.loads(response.text)
    # print(data)

    if data['status'] == True:
        return '1'
    else:
        return '-1'


def initDc(cookie):
    data = { "_json_att": '' }
    headers = {
        'Cookie': cookie,
        'Content-Type': 'application/x-www-form-urlencoded'
    }

    # print('initDc:', cookie)
    response = requests.post(INIT_DC, data=data, headers=headers)
    # print('initDc:', response.text)

    # var globalRepeatSubmitToken = 'ebd473dc6357d6d522c10133776a73e7';
    repeat_submit_token = re.findall(r"var globalRepeatSubmitToken = '(.*?)'", response.text)[0]

    # 也可车票信息里面提取
    # liftTicket = re.findall(r"'leftTicketStr':'(.*?)'", response.text)[0]

    key_check_ischange = re.findall(r"'key_check_isChange':'(.*?)'", response.text)[0]

    print(repeat_submit_token)

    if repeat_submit_token:
        return (repeat_submit_token, key_check_ischange)
    else:
        return '-1'


# 获取用户乘客信息
def getPassengerDTOs(repeat_submit_token, cookie):
    data = {"_json_att": '', 'REPEAT_SUBMIT_TOKEN': repeat_submit_token}
    headers = {
        'Cookie': cookie,
        'Content-Type': 'application/x-www-form-urlencoded'
    }
    response = requests.post(GET_PASSENGER_DTOS, data=data, headers=headers)
    print('getPassengerDTOs:', response.text)

    data = json.loads(response.text)
    print(data)
    if data['status'] == True:
        return '1'
    else:
        return '-1'


def checkOrderInfo(repeat_submit_token, cookie):
    data = {
        "cancel_flag": "2",
        "bed_level_order_num": "000000000000000000000000000000",
        "passengerTicketStr": PASSENGER_TICKET_STR,
        "oldPassengerStr": OLD_PASSENGER_STR,
        "tour_flag": "dc",
        "randCode": "",
        "whatsSelect": "1",
        "_json_att": "",
        "REPEAT_SUBMIT_TOKEN": repeat_submit_token
    }
    headers = {
        'Cookie': cookie,
        'Content-Type': 'application/x-www-form-urlencoded'
    }
    response = requests.post(CHECK_ORDER_INFO, data=data, headers=headers)
    print('checkOrderInfo:', response.text)

    data = json.loads(response.text)
    print(data)
    if data['status'] == True:
        return '1'
    else:
        return '-1'

def getQueueCount(train_no, stationTrainCode, fromStationTelecode, toStationTelecode, leftTicket, train_location, repeat_submit_token, cookie):
    data = {
        #  TODO "Mon Feb 04 2019 00:00:00 GMT+0800 (中国标准时间)"
        "train_date": datetime.datetime.fromisoformat("2019-02-04").strftime("%a %b %d %Y ")  + '00:00:00 GMT+0800 (中国标准时间)',
        "train_no": train_no,
        "stationTrainCode": stationTrainCode,
        "seatType": "1", #
        "fromStationTelecode": fromStationTelecode,
        "toStationTelecode": toStationTelecode,
        "leftTicket": leftTicket,
        "purpose_codes": "00",
        "train_location": train_location,
        "_json_att": "",
        "REPEAT_SUBMIT_TOKEN": repeat_submit_token
    }
    headers = {
        'Cookie': cookie,
        'Content-Type': 'application/x-www-form-urlencoded'
    }
    response = requests.post(GET_QUEUE_COUNT, data=data, headers=headers)
    print('getQueueCount:', response.text)

    data = json.loads(response.text)
    print(data)

    if data['status'] == True:
        return '1'
    else:
        return '-1'


def confirmSingleForQueue(key_check_isChange, leftTicketStr, train_location, repeat_submit_token, cookie):
    data = {
        'passengerTicketStr': PASSENGER_TICKET_STR,  # 写死
        'oldPassengerStr': OLD_PASSENGER_STR,  # 写死
        'randCode': '',
        'purpose_codes': '00',
        'key_check_isChange': key_check_isChange,  # 跟repeat_submit_token  一起获得的
        'leftTicketStr': leftTicketStr,  # 跟repeat_submit_token  一起获得的
        'train_location': train_location,  # train_location = tem_list[15]
        'choose_seats': '',
        'seatDetailType': '000',
        'whatsSelect': '1',
        'roomType': '00',
        'dwAll': 'N',
        '_json_att': '',
        'REPEAT_SUBMIT_TOKEN': repeat_submit_token
    }

    headers = {
        'Cookie': cookie,
        'Content-Type': 'application/x-www-form-urlencoded'
    }
    response = requests.post(CONFIRM_SINGLE_FOR_QUEUE, data=data, headers=headers)
    print('confirmSingleForQueue:', response.text)

    data = json.loads(response.text)
    print(data)

    if data['status'] == True:
        # print('恭喜， 订票成功，请在30分钟内完成付款！')
        return '1'
    else:
        return '-1'


def queryOrderWaitTime(repeat_submit_token, cookie):
    random = int(round(time.time() * 1000))
    headers = {
        'Cookie': cookie,
        'Content-Type': 'application/x-www-form-urlencoded'
    }
    response = requests.get(QUERY_ORDER_WAIT_TIME % (random, repeat_submit_token), headers=headers)
    print(response.text)
    data = json.loads(response.text)
    if data['data']['waitCount'] == 0 and data['data']['orderId']:
        return data['data']['orderId']
    else:
        return '-1'


def resultOrderForDcQueue(orderSequence_no, repeat_submit_token, cookie):
    data = {
        'orderSequence_no': orderSequence_no,   # 订单号
        '_json_att': '',
        'REPEAT_SUBMIT_TOKEN': repeat_submit_token
    }

    headers = {
        'Cookie': cookie,
        'Content-Type': 'application/x-www-form-urlencoded'
    }
    response = requests.post(RESULT_ORDER_FOR_DCQUEUE, data=data, headers=headers)
    print('resultOrderForDcQueue:', response.text)

    data = json.loads(response.text)
    print(data)

    if data['data']['submitStatus'] == True:
        print('恭喜，订票成功，请在30分钟内完成付款！')
        return '1'
    else:
        return '-1'


def main():
    while True:
        query()


if __name__ == '__main__':
    main()
