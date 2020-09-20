import csv
import re
import pandas as pd
import requests
from bs4 import BeautifulSoup  # 从bs4引入BeautifulSoup


def get_cookie():
    raw_cookie_file = r'raw_cookie.txt'
    raw = ''
    with open(raw_cookie_file) as rf:
        raw = rf.readline()
    kvs = re.split(r'; ', raw)
    cookie = dict()
    for kv in kvs:
        key, value = re.split(r'=', kv)
        cookie[key] = value
    return cookie

# call by (guid, reviewer, content, time, reply, url, writer)
def get_sprites(guid, reviewer, r_content, r_time, reply, url, writer):
    # 请求网页
    http_session = requests.session()
    requests.utils.add_dict_to_cookiejar(http_session.cookies, get_cookie())
    fake_headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/79.0.3945.79 Safari/537.36'
    }
    response = http_session.get(url, headers=fake_headers)
    soup = BeautifulSoup(response.content, 'lxml', from_encoding='utf-8')

    ws = soup.find('div', class_='reply-items')
    # why ws is None sometimes?
    if ws is None:
        print(soup)
        return
    comments = ws.find_all('div', class_='item')
    # print(f'comments: {comments}')

    for each_comment in comments:
        tt = each_comment.find('div', class_='tt')
        follower = tt.find('span', class_='name').text
        follower = follower.strip()
        print(f'follower: {follower}')
        raw = tt.text
        if ':' not in raw:
            continue
        try:
            _, content = raw.split(r':')
        except ValueError as ve:
            print(f'raw: {raw}')
            continue
        content = content.strip()
        print(f'content: {content}')
        tc = each_comment.find('div', class_='tc clearfix')
        cid = tc.get('cid')
        rid = tc.get('rid')
        # print(f'cid: {cid}')
        # print(f'rid: {rid}')
        f_time = tc.find('span', class_='time').text
        # header: ['guid', 'reviewer', 'content', 'cid', 'rid', "follower", "content", 'time']
        writer.writerow([guid, reviewer, r_content, r_time, reply, cid, rid, follower, content, f_time])

    print("finished!")


def run(item):
    csv_file = item + '_comments.csv'
    data = pd.read_csv(csv_file, header=0, encoding="gbk")
    # print(data)
    prefix = r'https://club.jd.com/repay/'
    suffix = r'_1.html'
    csv_path = item + '_sprites_verbose.csv'
    sprite_csv = open(csv_path, 'w', encoding="utf-8", newline='')
    writer = csv.writer(sprite_csv)
    # 写入标题
    writer.writerow(['guid', 'reviewer', 'r_content', 'r_time', 'reply', 'cid', 'rid', "follower", "f_content", 'f_time'])
    # test for one comment
    # url = 'https://club.jd.com/repay/5375281_7c5554b2-c5a5-47c6-84a7-9c423ae52343_1.html'
    # get_sprites(url)
    for index, row in data.iterrows():
        if row['reply'] < 1:
            continue
        guid = row['guid']
        reviewer = row['name']
        content = row['content']
        time = row['time']
        reply = row['reply']
        url = prefix + item + '_' + guid + suffix
        print('-' * 50 + 'New URL' + '-' * 50)
        print(url)
        get_sprites(guid, reviewer, content, time, reply, url, writer)
    sprite_csv.close()


if __name__ == '__main__':
    items = [
        '100005855774' # AOC
        , '5375281' # AOC
        , '2357097' # SAMSUNG
        , '100008771796' # Xiaomi
        , '100004470520' # HUSHIDA
        , '100007193438' # SAMSUNG
        , '100004239411' # AOC
        , '100005827141' # AOC
        , '5155905' # AOC
        , '100000911929' # Skyworth
        , '100003414734' # HP
        , '1409795' # AOC
        , '1057210' # 1057210
        , '100003374425' # SAMSUNG
        , '827069' # Loctek
        , '2190033' # NB
        , '7080750' # AOC
        , '2316993' # Dell
        , '1769180' # Dell
        , '7299682' #飞利浦
        , '5189035' #飞利浦
        , '100003923139' #华硕
        , '8249576' #三星（SAMSUNG）
        , '8441866' #AOC
        , '1131222' #AOC
        , '3531552' #HKC/惠科 27英寸 VA面板 144Hz电竞 1800R曲面屏 hdmi吃鸡游戏 1080p 宽屏 滤蓝光不闪屏 电脑液晶显示器 G27
        , '11576278244' #松人 R240 24英寸曲面显示器 高清HDMI液晶 家用办公台式 窄边框 广视角 电脑屏幕 银白色
        , '100005489380' #飞利浦 27英寸 1500R曲面 75Hz刷新 全高清 微边框 HDMI接口 电脑液晶显示器屏 271E1C
        , '959834' #优派 21.5英寸高清显示器 AH-IPS硬屏广视角电脑显示屏 LED背光办公监控 液晶电脑显示器 VA2249s-2
        , '3980435' #微软之星 电脑显示器 家用办公 21.5英寸 VA面板 显示屏 广视角 支持壁挂 全高清液晶显示器 E2209
        , '1312126' #三星（SAMSUNG）27英寸广视角 爱眼不闪屏滤蓝光 HDMI全高清接口 液晶电脑显示器
        , '7126948' #优派 23.8英寸IPS窄边框显示器 爱眼滤蓝光不闪屏1080p学生用可壁挂显示器24 HDMI显示器VA2478-H-2
        , '2756389' #三星（SAMSUNG）23.5英寸曲面 可壁挂 HDMI接口 节能爱眼认证 FreeSync技术 电脑显示器（C24F396FHC）
        , '2165667' #戴尔（DELL）21.5英寸 广色域 HDMI高清接口 防眩光 微边框 家用办公 电脑显示器 SE2216H
    ]
    # items = ['10186809346' #松人 R240A 24英寸显示器 75hz IPS 窄边框 超薄 HDMI高清 办公台式 电脑屏幕 磨砂银
    #     , '6138452' #AOC AGON 爱攻 35英寸 21:9带鱼屏 2K高清 G-SYNC同步 吃鸡120Hz 人体工学升降游戏电竞曲面显示器 AG352UCG6
    #     , '7168868' # 三星（SAMSUNG）31.5英寸 4K/UHD高分辨率 爱眼 FreeSync技术LED背光 可壁挂PS4液晶电脑显示器 U32J590UQC
    #     , '100000830235' #戴尔(DELL) 23.8英寸 IPS广视角 影院级广色域 窄框 旋转升降 低蓝光 商务居家办公 台机电脑显示器(U2419H)
    #     , '2727328' #三星（SAMSUNG）27英寸曲面 可壁挂 HDMI接口 节能爱眼认证 FreeSync技术 电脑显示器（C27F396FHC）
    #     , '100007193438' #三星（SAMSUNG）23.8英寸 爱眼不闪屏滤蓝光 可壁挂 FreeSync 液晶电脑显示器 S24R352FHC（HDMI接口）
    #     , '7266482' #AOC C27V1QD 27英寸 1700R中心曲率 FHD高清 窄边框 中国节能产品认证 曲面显示器（HDMI+DP接口）
    #     , '5918529' #飞利浦 31.5英寸 2K QHD高分辨率 低蓝不闪屏 FreeSync技术 电竞模式 可壁挂 电脑液晶显示器 HDMI 327E8FJSW
    #     , '8324345' #AOC电脑显示器 23.8英寸全高清IPS屏 旋转升降窄边框 DP接口 家用办公TUV低蓝光爱眼不闪显示屏24P1U
    #          ]

    # items = [
    #     '493442'  # 戴尔(DELL) 24英寸 高清IPS屏 16:10 旋转升降 个人商务 家庭办公 影音娱乐 台式笔记本电脑显示器(U2412M)
    #     , '100008771796'  # 小米 显示器 23.8英寸 IPS技术硬屏 三微边设计 低蓝光模式 3年质保
    #     , '100004239411'  # AOC 23.8英寸 IPS 广色域 144Hz HDREffect技术 直男小钢炮 人体工学支架 游戏电竞显示器24G2
    #     , '1312114'  # 三星（SAMSUNG）23.6英寸 臻彩广视角不闪屏 爱眼 HDMI高清接口 液晶电脑显示器（S24E390HL）
    #     , '6312079'  # HKC/惠科 23.6英寸 VA面板 黑色 1800R曲面屏 hdmi纤薄微边框 1080p 宽屏 滤蓝光不闪屏 电脑液晶显示器 C240
    #     , '100005327364'  # 麦普森
    #     , '8665831'  # 戴尔（DELL）27英寸 IPS 旋转升降 爱眼低蓝光 三边微边框 可壁挂 个人商务办公 电脑显示器 S2719HS
    #     , '1582561933'  # AOC C27B1H 27英寸1700R曲面高清台式电脑显示屏幕HDMI游戏液显示器 JD仓配
    #     , '100000260760'  # 麦普森 桌置式旋转升降支架 屏幕支架 显示器增高支架 壁挂支架【承重4.0~4.3KG之间】M903
    #     , '5399268'  # 三星（SAMSUNG）26.9英寸 2K/QHD高分 窄边框旋转升降底座 type-C 反向快充 爱眼 电脑显示器(S27H850QFC)
    #     , '1333309'  # 飞利浦 21.5英寸 TN面板 LED背光 电脑液晶显示器 可壁挂 商务办公 223I5LSU2
    #     , '7815770'  # 戴尔(DELL) 23.8英寸 微边框IPS屏广视角 滤蓝光 旋转升降 商务办公娱乐 电脑台式机多接口显示器(P2419H)
    #     , '8126555'  # 飞利浦 27英寸 猛腾 1800R曲面 144Hz/FreeSync 广色域 游戏电竞吃鸡显示器 可挂壁 HDMI 278M6QJEB
    #     , '6574079'  # AOC 31.5英寸 2K IPS技术 10bit面板 广视角 FreeSync ΔE3 低蓝光不闪屏高分电脑显示器 Q3279VWFD8/WS
    #     , '1312124'  # 三星（SAMSUNG）23.6英寸 臻彩广视角不闪屏 HDMI高清接口 爱眼 液晶电脑显示器（S24E360HL）
    #     , '1268447'  # 戴尔（DELL）24英寸 IPS 广色域 旋转升降 微边框 16:10 个人商务 设计 电脑显示器 U2415
    #     , '8774259'  # 飞利浦 23.8英寸 升降旋转底座 原厂LGD IPS面板 低蓝光爱眼不闪屏 HDMI 商务办公显示器 可挂壁 243S7EHMB
    #     , '5326521'  # 联想（ThinkVision）23.8英寸 IPS技术 4mm纤薄机身 TUV滤蓝光爱眼不闪屏 电脑显示器New X24-20
    #     , '5483795'  # 华硕 ROG玩家国度 XG32VQ 31.5英寸 1800R曲面显示屏 2K显示器 144HZ显示器 电脑显示器 电竞液晶显示器
    #     , '4946544'  # AOC C2791VHE/WS 27英寸 1800R曲率 VA广视角 家用电竞双实力 不闪屏曲面电脑显示器
    #     , '100001118600'  # 华硕 ROG玩家国度 XG32VQR 31.5英寸曲面显示屏144hz显示器2K HDR Aura神光同步 电脑显示器 电竞显示器
    #     , '100000731986'  # 游戏悍将 27英寸144hz显示器电脑游戏吃鸡主机办公家用高清显示屏 CK27FC
    #     , '3212646'  # 三星（SAMSUNG）31.5英寸 1800R曲面 TUV爱眼认证 可壁挂 HDMI/DP高清接口 液晶电脑显示器（C32F395FWC）
    #     , '4370115'  # zeol 23.8英寸 广视角IPS屏 电脑屏幕 微窄边框 低蓝光爱眼不闪 准24英寸液晶显示器 HDMI（卓悦238）
    # ]
    # items = ['100005855774']
    for item in items:
        run(item)
