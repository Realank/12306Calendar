import urllib
from datetime import datetime
import mail
import order
import urllib.parse
from icalendar import Calendar, Event
from http.server import HTTPServer, BaseHTTPRequestHandler
import sqlite3

PORT = 8081


def save_db(email, password):
    mail_list = mail.get_12306_orders(email, password)
    if len(mail_list) == 0:
        print('读取不到邮件')
        return
    con = sqlite3.connect("orders.db")
    cur = con.cursor()
    sql = "CREATE TABLE IF NOT EXISTS orders(id INTEGER PRIMARY KEY AUTOINCREMENT, email TEXT, number TEXT, date TEXT, summary TEXT, detail TEXT)"
    cur.execute(sql)
    for m in mail_list:
        # print(m.subject)
        o = order.gen_order(m.subject, m.content)
        # print(str(
        #     o.type) + ' ' + o.name + ' ' + o.time_str + ' ' + o.number + ' ' + o.train + ' ' + o.seat + ' ' + o.from_to + ' ' + o.detail)

        cur.execute("SELECT * FROM orders WHERE number='" + o.number + "'")
        same_order = cur.fetchone()
        if o.type == 1 and same_order:
            # 已经存在此购票信息
            continue
        if o.type > 1 and same_order:
            # 退票和改签
            cur.execute("DELETE FROM orders WHERE number='" + o.number + "'")
            if o.type == 3:
                continue
        data = "'" + email + "','" + o.number + "','" + o.time_str + "','" + o.summary + "','" + o.detail + "'"
        # print('INSERT INTO orders (email,number,date,summary,detail) VALUES (%s)' % data)
        cur.execute('INSERT INTO orders (email,number,date,summary,detail) VALUES (%s)' % data)
        cur.execute(sql)
    cur.execute("SELECT number,date,summary,detail FROM orders")
    orders = cur.fetchall()
    con.commit()
    # 关闭游标
    cur.close()
    # 断开数据库连接
    con.close()
    return orders


def gen_ics(email, password):
    save_db(email, password)
    orders = save_db(email, password)
    cal = Calendar()

    cal.add('prodid', '-//My calendar product//rlk.cn//')
    cal.add('version', '2.0')
    cal.add('summary', '乘车信息')
    cal.add('X-WR-CALNAME', 'calendar_name')
    for o in orders:
        (number, date, summary, detail) = o
        time = datetime.strptime(date, '%Y年%m月%d日%H:%M')
        event = Event()
        event.add('summary', summary)
        event.add('dtstart', time)
        event.add('dtend', time)
        event.add('description', detail)
        event.add('uid', number)
        create_time = datetime.today()
        event.add('create', create_time)
        event.add('last-modified', create_time)
        event.add('dtstamp', create_time)
        event.add('sequence', "0")
        cal.add_component(event)

    return cal.to_ical()
    # f = open('example.ics', 'wb+')
    # f.write(cal.to_ical())
    # f.close()


class Handler(BaseHTTPRequestHandler):

    def do_GET(self):
        url_change = urllib.parse.urlparse(self.path)  # 将url拆分为6个部分
        query = url_change.query  # 取出拆分后6个部分中的查询模块query
        lst_query = urllib.parse.parse_qsl(query)  # 使用parse_qsl返回列表
        dict1 = dict(lst_query)  # 将返回的列表转换为字典
        user = dict1['u']
        password = dict1['p']
        # print('user:' + user + ' password:' + password)
        self.send_response(200)
        self.send_header('Content-Type', 'application/octet-stream')
        self.send_header('Content-Disposition', 'attachment; FileName=my.ics')
        self.end_headers()
        content = gen_ics(user, password)
        self.wfile.write(content)


if __name__ == '__main__':
    server_address = ('', PORT)
    httpd = HTTPServer(server_address, Handler)
    httpd.serve_forever()
