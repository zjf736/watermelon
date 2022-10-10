import re, requests, json
from selenium import webdriver
import os,time
from selenium.webdriver.common.desired_capabilities import DesiredCapabilities
from selenium.webdriver.chrome.options import Options
import random
from base64 import b64decode


#关键链接 url = 'https://www.ixigua.com/api/public/videov2/brief/details?group_id=' + str(uid) + '&_signature=' + signa，视频的加密地址就在这个链接里
#我们观看源码中知道他采取的是base64加密
#phantomjs.exe他相当一个浏览器（没有页面的）
#西瓜采取的是AJAX相应数据



#调用get_home()获取首页的数据，调用w_file()保存离线html_home.txt（因数据是ajax加载的需要下载离线的txt方便后期分析）
def get_home(url):


    #添加一些请求的信息比如UA(请求头)
    dcap = dict(DesiredCapabilities.PHANTOMJS)

    dcap["-phantomjs.page.settings.userAgent-"] = (
        "-Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/92.0.4515.107 Safari/537.36 Edg/92.0.902.62-"
    )

    driver = webdriver.PhantomJS(
        desired_capabilities=dcap,
        executable_path=
        now_path + '\\phantomjs.exe',
    )

    driver.set_window_size(1920, 1080)

    driver.get(url)

    time.sleep(6)

    texts = driver.page_source  #texts 是主页的html文件

    driver.close()

    w_file(now_path + '\\data\\html_video.txt',texts)


def w_file(filepath, contents):

    with open(filepath,'w', encoding='gb18030') as wf:
        wf.write(contents)


#调用get_user_data()获取视频ID（ID用于请求https://www.ixigua.com/i+ID获取嵌在html中video的地址也就是MP4的真实地址）
def open_home_text(paths):

    f = open(paths,encoding='gb18030', errors='ignore')

    html_data = f.read()

    f.close()

    return html_data

#获取用户数据
def get_user_data():

    time.sleep(1.5)
    home_text = open_home_text('.\\data\\html_video.txt')
    video_title_ = re.compile(r'<h1 class="hasSource">(.*?)</h1>')
    video_title_1 = re.findall(video_title_, home_text)
    video_titles.append(video_title_1[0])
    video_uid_ = re.compile(
        r'<div class="xiguaBuddyPub xiguaBuddyPub__shortVideo" data-group-id="(.*?)"></div>'
    )
    video_uid_1 = re.findall(video_uid_, home_text)
    video_uid.append(video_uid_1[0])

#generate_random_str(randomlength=32)生成_signature（经过分析发现_signature是有规律的）
def generate_random_str(randomlength=32):

    """
  生成一个指定长度的随机字符串
  """
    s = '_24B4Z{}wo00f01'
    random_str = ''
    base_str = 'ABCDEFGHIGKLMNOPQRSTUVWXYZabcdefghigklmnopqrstuvwxyz0123456789'
    length = len(base_str) - 1
    for i in range(randomlength):
        random_str += base_str[random.randint(0, int(length))]

    x = random.randint(0,9)

    signature = s.format(x) + random_str

    return signature

#提取视频真实地址和画质
def get_url_json(uid,signa):

    #json中的video_1,video_2,video_3,video_4  对应了 360p，480p 720p，1080p (画质)

    url = 'https://www.ixigua.com/api/public/videov2/brief/details?group_id=' + str(uid) + '&_signature=' + signa

    res_json = requests.get(url,headers=headers).json()

    #判断是否存在1080p
    if "video_4" in res_json["data"]["videoResource"]["normal"]["video_list"]:

        main_url = res_json["data"]["videoResource"]["normal"]["video_list"]["video_4"]["main_url"]    #main_url是经过base64加密的视频地址
    else:
        main_url = res_json["data"]["videoResource"]["normal"]["video_list"]["video_3"]["main_url"]

    true_video_site = b64decode(main_url.encode()).decode()  #对main_url进行解码

    return true_video_site  #返回真实mp4地址


def if_video_true(uid,title):

    uid_url = f'https://www.ixigua.com/i{uid}'

    get_home(uid_url)

    home_text = open_home_text(paths=now_path + '\\data\\html_video.txt')

    sig = generate_random_str()   #生成_signature

    true_url = get_url_json(uid=uid,signa=sig)

    get_video_url(video_title=title,url=true_url)


def formatting(a,b):
    #格式化列表
    del a[0]
    del b[0]


def get_video_url(video_title,url):

    mp4 = requests.get(url,stream=True)
    if mp4.status_code == 200:
        progressbar(url, video_title)


#下载
def progressbar(video_url, video_title):

    n = 30
    e = 0
    start = time.time()  # 下载开始时间

    response = requests.get(video_url, stream=True)  # stream=True必须写上
    size = 0  # 初始化已下载大小
    chunk_size = 1024  # 每次下载的数据大小
    content_size = int(response.headers['content-length'])  # 下载文件总大小
    if response.status_code == 200:  # 判断是否响应成功
        print('视频大小:{size:.2f} MB'.format(
            size=content_size / chunk_size / 1024))  # 开始下载，显示下载文件大小
        filepath = 'video\\' + video_title + '.mp4'  # 设置图片name，注：必须加上扩展名
        with open(filepath, 'wb') as file:  # 显示进度条
            for data in response.iter_content(chunk_size=chunk_size):
                file.write(data)
                size += len(data)
                if e % n == 0:
                    print('[下载进度]:%s%.2f%%' %
                          ('▇' * int(size * 50 / content_size),
                           float(size / content_size * 100)),
                          end='\n')
                e +=1
        end = time.time()  # 下载结束时间

        print('Download completed!,times: %.2f秒' % (end - start))  # 输出下载用时时间
        print(f'视频【 {video_title} 】已经保存完毕')
        os.remove('.\\data\\html_video.txt')


if __name__=='__main__':

    global home_text, video_uid, video_titles,now_path
    video_uid = []  #视频id
    video_titles = []  #视频标题
    now_path = os.getcwd()  #获取当前工作目录


    #创建文件夹
    if not os.path.exists(now_path + '\\video'):
        os.mkdir(now_path + '\\video')
    if not os.path.exists(now_path + '\\data'):
        os.mkdir(now_path + '\\data')
    headers = {
        'cookie':
        '_ga=GA1.2.1377542255.1607840271; ttcid=f5d44ecf93154d5d9e8fe19318fedc0b38; Hm_lvt_db8ae92f7b33b6596893cdf8c004a1a2=1622370631,1622621697,1622623270,1622623925; passport_csrf_token_default=4e5cab603d463f949750c3b2a4ef9d9c; sid_guard=e11f6bbc4228d643508167385aec5363%7C1624284971%7C5183999%7CFri%2C+20-Aug-2021+14%3A16%3A10+GMT; uid_tt=53edd8928737eeb015a818ab26ab07ec; uid_tt_ss=53edd8928737eeb015a818ab26ab07ec; sid_tt=e11f6bbc4228d643508167385aec5363; sessionid=e11f6bbc4228d643508167385aec5363; sessionid_ss=e11f6bbc4228d643508167385aec5363; passport_csrf_token=4e5cab603d463f949750c3b2a4ef9d9c; MONITOR_WEB_ID=55bc8346-1c1d-4841-9486-0d1aeb68427b; ixigua-a-s=1; ttwid=1%7CzCbj5A71JotKJbX8u6GAfPSPLl_Cc2BqS0S7hisEyl8%7C1628228748%7C37843ca0c7b752bba56deffddc11d6d0000ca8370183b87db642715975c98d0c; __ac_nonce=0610ccf8100f6b2596aae; __ac_signature=_02B4Z6wo00f01jA7TkgAAIDCsDm0CQXDg3owH0rAAO0Qa0',
        'referer':
        'https://www.ixigua.com/?wid_try=1',
        'user-agent':
        'Mozilla/5.0 (Windows NT 10.0; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/81.0.4044.138 Safari/537.36'
    }


    while True:
        print('---------------------------------------------------------------------')
        print('--------------------------请输入视频的链接:--------------------------')
        print('---------------------------------------------------------------------')
        home_url = input()
        get_home(home_url)
        time.sleep(1)
        get_user_data()
        time.sleep(1)
        print(f'正在下载{video_titles[0]}')
        if_video_true(video_uid[0],video_titles[0])
        formatting(video_uid,video_titles)

