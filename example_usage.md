# JavBus多用户签到脚本使用说明

## 功能特点
- 支持多用户同时签到
- 自动从同级目录下的用户名.txt文件读取cookies
- 当cookies失效时，通过Bark或Gotify发送通知
- 改进原GitHub Actions版本，支持本地运行

## 使用方法

### 1. 准备用户cookies文件
在/workspace目录下创建以用户名命名的txt文件，例如：
- `aaa.txt` - 存放用户aaa的cookies
- `bbb.txt` - 存放用户bbb的cookies

每个文件内容为对应的cookie字符串。

### 2. 配置通知服务（可选）
设置以下环境变量来启用失效通知：

#### Bark通知
```bash
export BARK_URL="https://api.day.app/your_bark_key"
```

#### Gotify通知
```bash
export GOTIFY_URL="https://your-gotify-instance.com"
export GOTIFY_TOKEN="your_gotify_app_token"
```

### 3. 安装依赖
```bash
pip install -r requirements.txt
```

### 4. 运行脚本
直接运行Python脚本：
```bash
python checkin.py
```

或使用shell脚本：
```bash
./run_checkin.sh
```

### 5. 设置定时任务（可选）
如果需要定时执行，可以在crontab中添加：
```bash
# 每天早上8点执行签到
0 8 * * * cd /workspace && ./run_checkin.sh >> /var/log/javbus-checkin.log 2>&1
```

## 注意事项
- 请确保cookie格式正确
- 建议在不同时间点执行脚本以避免被检测为异常访问
- 当收到cookie失效通知时，请及时更新对应用户的txt文件