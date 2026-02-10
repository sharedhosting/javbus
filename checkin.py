#!/usr/bin/env python3
"""
JavBus论坛多用户签到脚本
支持从多个用户文件中读取cookies进行签到
当cookies失效时，通过Bark或Gotify发送通知
"""

import requests
import json
import time
import os
import glob
from lxml import etree


class JavBusCheckIn:
    def __init__(self, bark_url=None, gotify_url=None, gotify_token=None):
        self.bark_url = bark_url
        self.gotify_url = gotify_url
        self.gotify_token = gotify_token
        self.session = requests.Session()
        self.session.headers.update({
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:122.0) Gecko/20100101 Firefox/122.0'
        })

    def send_notification(self, title, message):
        """发送通知到Bark或Gotify"""
        success = False
        
        # 尝试发送Bark通知
        if self.bark_url:
            try:
                bark_full_url = f"{self.bark_url}/{title}/{message}"
                response = requests.get(bark_full_url, timeout=10)
                if response.status_code == 200:
                    print(f"Bark通知发送成功: {title}")
                    success = True
                else:
                    print(f"Bark通知发送失败，状态码: {response.status_code}")
            except Exception as e:
                print(f"Bark通知发送异常: {str(e)}")
        
        # 如果Bark失败或未配置，尝试Gotify
        if not success and self.gotify_url and self.gotify_token:
            try:
                gotify_data = {
                    'title': title,
                    'message': message,
                    'priority': 5
                }
                headers = {'Authorization': f'Bearer {self.gotify_token}'}
                response = requests.post(
                    f"{self.gotify_url}/message", 
                    data=gotify_data, 
                    headers=headers, 
                    timeout=10
                )
                if response.status_code == 200:
                    print(f"Gotify通知发送成功: {title}")
                    success = True
                else:
                    print(f"Gotify通知发送失败，状态码: {response.status_code}")
            except Exception as e:
                print(f"Gotify通知发送异常: {str(e)}")
        
        if not success:
            print("所有通知方式都失败")

    def check_in_single_user(self, username, cookie):
        """对单个用户进行签到"""
        url = "https://www.javbus.com/forum/home.php?mod=spacecp&ac=credit&op=log&suboperation=creditrulelog"
        headers = {
            'authority': 'www.javbus.com',
            'method': 'GET',
            'path': '/forum/home.php?mod=spacecp&ac=credit',
            'scheme': 'https',
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:122.0) Gecko/20100101 Firefox/122.0',
            'Upgrade-Insecure-Requests': '1',
            'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8',
            'Accept-Language': 'zh-CN,zh;q=0.8,zh-TW;q=0.7,zh-HK;q=0.5,en-US;q=0.3,en;q=0.2',
            'Accept-Encoding': 'gzip, deflate',
            'Cookie': cookie,
            'referer': 'https://www.javbus.com/forum/home.php?mod=spacecp'
        }

        try:
            r = self.session.get(url, headers=headers, timeout=60)
            
            if '每天登录' in r.text or '每天登錄' in r.text:
                h = etree.HTML(r.text)
                data = h.xpath('//tr/td[6]/text()')
                if data:
                    last_checkin_time = data[0]
                    msg = f"[{username}] 签到成功或今日已签到, 最后签到时间: {last_checkin_time}"
                else:
                    msg = f"[{username}] 签到成功或今日已签到"
            else:
                msg = f"[{username}] 签到失败, 可能是cookie失效了!"
                # 发送失效通知
                self.send_notification(
                    f"JavBus Cookie失效 - {username}",
                    f"用户 {username} 的JavBus Cookie已失效，请及时更新。"
                )
                
        except requests.exceptions.RequestException as e:
            msg = f"[{username}] 无法正常连接到网站: {str(e)}"
        except Exception as e:
            msg = f"[{username}] 签到过程中出现异常: {str(e)}"
            
        return msg

    def load_cookies_from_files(self):
        """从当前目录下的txt文件加载cookies"""
        cookies_dict = {}
        txt_files = glob.glob("*.txt")
        
        for file in txt_files:
            username = os.path.splitext(file)[0]  # 去掉.txt扩展名作为用户名
            try:
                with open(file, 'r', encoding='utf-8') as f:
                    cookie_content = f.read().strip()
                    if cookie_content:
                        cookies_dict[username] = cookie_content
                        print(f"已加载用户 [{username}] 的cookies")
                    else:
                        print(f"警告: 文件 {file} 为空")
            except Exception as e:
                print(f"读取文件 {file} 失败: {str(e)}")
                
        return cookies_dict

    def run_check_in(self):
        """运行签到程序"""
        print("---------- 开始JavBus论坛批量签到 ----------")
        print(f'当前北京时间为: {time.strftime("%Y-%m-%d %H:%M:%S", time.localtime(time.time()+28800))}')
        
        # 加载所有用户的cookies
        cookies_dict = self.load_cookies_from_files()
        
        if not cookies_dict:
            print("没有找到任何用户cookies文件，请确保当前目录下有以用户名命名的.txt文件")
            return
            
        results = []
        for username, cookie in cookies_dict.items():
            print(f"\n正在处理用户: {username}")
            result = self.check_in_single_user(username, cookie)
            results.append(result)
            print(result)
            # 添加延迟避免请求过快
            time.sleep(2)
        
        print("\n---------- 所有用户签到完成 ----------")
        
        # 输出汇总结果
        print("\n签到结果汇总:")
        for result in results:
            print(result)


def main():
    # 从环境变量获取通知配置
    bark_url = os.environ.get("BARK_URL")  # 例如: https://api.day.app/your_bark_key
    gotify_url = os.environ.get("GOTIFY_URL")  # 例如: https://your-gotify-instance.com
    gotify_token = os.environ.get("GOTIFY_TOKEN")  # Gotify应用令牌
    
    # 创建签到实例
    checker = JavBusCheckIn(
        bark_url=bark_url,
        gotify_url=gotify_url,
        gotify_token=gotify_token
    )
    
    # 运行签到
    checker.run_check_in()


if __name__ == "__main__":
    main()