import poplib
from email.parser import Parser
from email.header import decode_header
from email.utils import parseaddr


class Mail:
    fromAccount = ''
    toAccount = ''
    subject = ''
    content = ''


# 解析消息头中的字符串
def decode_str(s):
    value, charset = decode_header(s)[0]
    if charset:
        value = value.decode(charset)
    return value


# 将邮件附件或内容保存至文件
# 即邮件中的附件数据写入附件文件
def savefile(filename, data, path):
    try:
        filepath = path + filename
        print('Save as: ' + filepath)
        f = open(filepath, 'wb')
    except:
        print(filepath + ' open failed')
        # f.close()
    else:
        f.write(data)
        f.close()


# 获取邮件的字符编码，首先在message中寻找编码，如果没有，就在header的Content-Type中寻找
def guess_charset(msg):
    charset = msg.get_charset()
    if charset is None:
        content_type = msg.get('Content-Type', '').lower()
        pos = content_type.find('charset=')
        if pos >= 0:
            charset = content_type[pos + 8:].strip()
    return charset


# 解析邮件的函数，首先打印收件人、发件人、标题
# 然后调用message的walk循环处理邮件中的每一个子对象（包括文本、html、附件一次或多次）
# 邮件头属性中的filename存在则该子对象是附件，对附件名称进行编码并将附件下载到指定目录
# 由于网络上传输的邮件都是编码以后的格式，需要在get_payload的时候指定decode=True来转换成可输出的编码
# 如果邮件是text或者html格式，打印格式并输出转码以后的子对象内容
def get_title(msg):
    mail = Mail()
    for header in ['From', 'To', 'Subject']:
        value = msg.get(header, '')
        if value:
            if header == 'Subject':
                value = decode_str(value)
                mail.subject = value
            else:
                hdr, addr = parseaddr(value)
                name = decode_str(addr)
                value = name + ' < ' + addr + ' > '
                if header == 'From':
                    mail.fromAccount = value
                elif header == 'To':
                    mail.toAccount = value
    return mail


def get_content(msg):
    for part in msg.walk():
        filename = part.get_filename()
        content_type = part.get_content_type()
        charset = guess_charset(part)
        if filename:
            continue
        else:
            email_content_type = ''
            content = ''
            if content_type == 'text/plain':
                email_content_type = 'text'
            elif content_type == 'text/html':
                email_content_type = 'html'
            if charset:
                content = part.get_payload(decode=True).decode(charset)
            if email_content_type == 'html':
                return content
    return ''


def email_server(email):
    address = email.split('@')[-1]
    return 'pop.' + address


def get_12306_orders(email, password):
    pop3_server = email_server(email)
    server = poplib.POP3(pop3_server, 110)
    server.user(email)
    server.pass_(password)

    resp, mails, objects = server.list()
    count = len(mails)
    # 取出某一个邮件的全部信息
    fetched_mails = []
    for x in range(int(count / 2), count + 1):
        resp, lines, octets = server.retr(x)
        # 邮件取出的信息是bytes，转换成Parser支持的str
        lists = []
        for e in lines:
            lists.append(e.decode())
        msg_content = '\r\n'.join(lists)
        msg = Parser().parsestr(msg_content)
        mail = get_title(msg)
        # print(mail.subject)
        # msgDate = msg["date"]
        # print(msgDate)
        if mail.subject.find('网上购票系统') >= 0:
            mail.content = get_content(msg)
            fetched_mails.append(mail)
            # print(mail.content)
    server.quit()
    return fetched_mails
