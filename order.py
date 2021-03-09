from bs4 import BeautifulSoup
import re
import datetime


class Order:
    type = 0  # 0 NA 1 买票 2 改签 3 退票
    orderId = ''
    number = ''
    name = ''
    time = ''
    time_str = ''
    train = ''
    seat = ''
    from_to = ''
    detail = ''
    summary = ''


def gen_type(subject):
    if subject.find('支付') >= 0:
        return 1
    if subject.find('改签') >= 0:
        return 2
    if subject.find('退票') >= 0:
        return 3
    return 0


def get_detail(content, order):
    soup = BeautifulSoup(content, 'lxml')
    list = soup.select('table tr>td>div')
    for div in list:
        if div.text.find('您于') >= 0:
            order.number = div.span.text
        if (div.text.find('，检票口') >= 0 and div.text.find('票价') >= 0) or \
                (div.text.find('，退票费') >= 0 and div.text.find('，应退票款') >= 0):
            order.detail = div.select('div')[0].text.strip()
    try:
        get_more(order)
    except:
        print('process order failed' + order.detail)


def get_more(order):
    if order.detail is None:
        return
    order.name = re.search(r'([\u4e00-\u9fa5]{2,4})\uFF0C', order.detail).group(1)
    order.time_str = re.search(r'[\u4e00-\u9fa5]+\uFF0C([\u4e00-\u9fa50-9:]+)\u5F00\uFF0C', order.detail).group(1)
    order.time = datetime.datetime.strptime(order.time_str, '%Y年%m月%d日%H:%M')
    order.from_to = re.search(r'\uFF0C([\u4e00-\u9fa5]{2,10}-[\u4e00-\u9fa5]{2,10})\uFF0C', order.detail).group(1)
    order.train = re.search(r'\uFF0C([CGZTKDLYN]?[0-9]{1,4})\u6B21', order.detail).group(1)
    order.seat = re.search(r'[,\uFF0C]([0-9]{1,2}\u8F66[0-9ABCDEF]{1,3}\u53F7)', order.detail).group(1)
    order.summary = (order.train + ' ' + order.seat + ' ' + order.from_to).replace('站', '')


def gen_order(subject, content):
    order = Order()
    order.type = gen_type(subject)
    # if order.type == 3:
    #     print(content)
    get_detail(content, order)
    return order
