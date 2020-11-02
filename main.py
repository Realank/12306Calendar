import urllib
import mail
import order
import urllib.parse
from icalendar import Calendar, Event
from http.server import HTTPServer, BaseHTTPRequestHandler

PORT = 8081


def gen_ics(email, password):
    mail_list = mail.get_12306_orders(email, password)
    cal = Calendar()

    cal.add('prodid', '-//My calendar product//mxm.dk//')
    cal.add('version', '2.0')
    cal.add('summary', '乘车信息')
    for m in mail_list:
        print(m.subject)
        o = order.gen_order(m.subject, m.content)
        print(str(
            o.type) + ' ' + o.name + ' ' + o.time_str + ' ' + o.number + ' ' + o.train + ' ' + o.seat + ' ' + o.from_to + ' ' + o.detail)

        event = Event()
        event.add('summary', o.summary)
        event.add('dtstart', o.time)
        event.add('dtend', o.time)
        event['uid'] = 'same'
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
        print('user:' + user + ' password:' + password)
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
