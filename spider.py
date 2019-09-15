import os
import sys
import time
import json
import multiprocessing
import requests
from settings import USERNAME,PASSWORD,OUTPUT_DIR,TIME_CONTROL

requests.packages.urllib3.disable_warnings()

FILE_FORMAT = {"cpp": ".cpp", "python3": ".py", "python": ".py", "mysql": ".sql", "golang": ".go", "java": ".java",
                   "c": ".c", "javascript": ".js", "php": ".php", "csharp": ".cs", "ruby": ".rb", "swift": ".swift",
                   "scala": ".scl", "kotlin": ".kt", "rust": ".rs"}

# 各种语言的注释符号 用于生成文件头，需要补充
COMMENT_SIGN = {
    "cpp": "//", "python3": "#", "python": "#","c": "#",
}


SLEEP_TIME = 5  # in second，登录失败时的休眠时间
LIMIT = 20    # 每页多少个
LEETCODE_CN = 'https://leetcode-cn.com'
SUBMISSIONS_URL = "https://leetcode-cn.com/api/submissions/?offset=%d&limit=%d&lastkey="


def login(username, password):
    sess = requests.session()
    sess.encoding = "utf-8"
    url = LEETCODE_CN + '/accounts/login/'
    while True:
        try:
            sess.get(url, verify=False)
            data = dict(login=username,password=password)
            result = sess.post(url, data=data, headers=dict(Referer=url))
            if result.ok:
                print ("Login Success")
                break
        except:
            print ("Login Failed! Wait Till Next Round!")
            time.sleep(SLEEP_TIME)

    return sess


def get_submissions(sess):
    offset = 0
    submissions = []
    while True:
        print ("Current Page:", str(offset))
        url = SUBMISSIONS_URL % (offset,LIMIT)
        resp = sess.get(url, verify=False)
        offset += LIMIT
        data = json.loads(resp.text)
        sub = data.get('submissions_dump',None) 
        if sub is None:
            # print ("END")
            break
        submissions.extend(sub)
    return submissions


def filter_submission(submission):
    status = submission['status_display']
    lang = submission['lang']

    if status != "Accepted":
        return False

    if time.time() - submission['timestamp'] > TIME_CONTROL:
        return False

    if lang not in FILE_FORMAT:
        return False

    return True


def save_submission(submission,output_dir=None):  
    code = submission['code']
    timestamp = submission['timestamp']
    createtime = time.strftime("%Y-%m-%d %H:%M:%S", time.localtime(timestamp))
    title = submission['title'].replace(' ','')

    ext = FILE_FORMAT.get(submission['lang'],'txt')
    filename = title + ext

    comment_sign = COMMENT_SIGN.get(submission['lang'],'')

    if output_dir is None:
        output_dir = OUTPUT_DIR

    if not os.path.exists(output_dir):
        os.mkdir(output_dir)

    filename = os.path.join(output_dir,filename)

    if os.path.exists(filename):
        return

    with open(filename,'w') as f:
        f.write(comment_sign + title+'\n')
        f.write(comment_sign + createtime+'\n\n')
        f.write(code)

    print(filename+' saved')


def get_submissions_q(q,sess):
    offset = 0
    while True:
        print ("Current Page:", str(offset))
        url = SUBMISSIONS_URL % (offset,LIMIT)
        resp = sess.get(url, verify=False)
        offset += LIMIT
        data = json.loads(resp.text)
        sub = data.get('submissions_dump',None) 
        if sub is None:
            # print ("END")
            break
        for s in sub:
            q.put(s)

def save_submission_q(q,output_dir=None):
    while True:
        submission = q.get()
        if filter_submission(submission):
            save_submission(submission)

        if q.empty():
            break

def mmain():
    """多进程版下载器"""
    sess = login(username=USERNAME, password=PASSWORD)

    q = multiprocessing.Queue()
    p1 = multiprocessing.Process(target=get_submissions_q,args=(q,sess))

    p2 = multiprocessing.Process(target=save_submission_q,args=(q,))
    p1.start()
    p2.start()


def main():
    sess = login(username=USERNAME, password=PASSWORD)
    submissions = get_submissions(sess)

    for submission in submissions:
        if filter_submission(submission):
            save_submission(submission)

if __name__ == '__main__':
    main()