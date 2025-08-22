import requests
from config import BOT_TOKEN

def test_bot():
    """测试机器人连接"""
    base_url = f"https://api.telegram.org/bot{BOT_TOKEN}"
    
    # 获取机器人信息
    response = requests.get(f"{base_url}/getMe")
    if response.status_code == 200:
        bot_info = response.json()
        print(f"机器人连接正常: {bot_info['result']['username']}")
    else:
        print(f"机器人连接失败: {response.text}")
        return
    
    # 获取更新
    response = requests.get(f"{base_url}/getUpdates")
    if response.status_code == 200:
        updates = response.json()
        print(f"收到 {len(updates['result'])} 个更新:")
        for update in updates['result'][-5:]:  # 显示最近5个更新
            if 'message' in update:
                msg = update['message']
                user = msg.get('from', {})
                text = msg.get('text', '')
                print(f"  - 用户 {user.get('first_name', 'Unknown')} ({user.get('id', 'Unknown')}): {text}")
    else:
        print(f"获取更新失败: {response.text}")

if __name__ == "__main__":
    test_bot()