
from os import path

PROJECT_DIR = path.dirname(path.dirname(path.abspath(__file__))) + '/'

def fromNameGetKey(name):
    stations = []
    with open(PROJECT_DIR + 'code/stations.txt', encoding='utf-8') as f:
        result = f.read()
        # print(result)


        # lstrip() 方法用于截掉字符串左边的空格或指定字符。
        result = result.lstrip('@').split('@')
        for i in result:
            tmp_info = i.split('|')
            stations.append({
                'key': tmp_info[2],
                'name': tmp_info[1],
                'pinyin': tmp_info[3],
                'id': tmp_info[5]
            })
        # print(stations)

        for dict in stations:
            if dict['name'] == name:
                return dict['key']



START_TIME = '2019-02-10'  # 出发时间
FROM_NAME = '广州'  # 出发站
TO_NAME = '深圳'   # 到达站
FROM_STATION = fromNameGetKey(FROM_NAME)
TO_STATION   = fromNameGetKey(TO_NAME)

PASSENGER_NAME = '' # 乘客姓名
ID_NUM = ''  # 乘客身份证号码
MOBILE_NUM = ''  # 乘客/用户 手机号码


# print(from_station, to_station)
# print(PROJECT_DIR)