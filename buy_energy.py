import asyncio
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import ContextTypes
from models import get_user_session, calculate_mock_cost, format_energy

def generate_buy_energy_text(user_id: int) -> str:
    """生成闪租页文本内容"""
    session = get_user_session(user_id)
    
    # 重新计算成本
    session.computed_cost = calculate_mock_cost(session.selected_energy, session.selected_duration)
    
    # 格式化能量显示
    energy_display = format_energy(session.selected_energy)
    
    # 地址显示
    address_display = session.selected_address if session.selected_address else "未选择"
    if session.selected_address and len(session.selected_address) > 10:
        address_display = f"{session.selected_address[:6]}...{session.selected_address[-4:]}"
    
    text = f"""⚡ Buy TRON Energy

使用说明：
选择时长和能量数量，然后确认继续。

当前选择：
• Energy: {energy_display}
• Duration: {session.selected_duration}
• Cost: {session.computed_cost} TRX

账户信息：
• User Balance: {session.user_balance['TRX']} TRX / {session.user_balance['USDT']} USDT
• Address: {address_display}

提示：
价格实时更新。支付前如需要请刷新余额。"""
    
    return text

def generate_buy_energy_keyboard(user_id: int) -> InlineKeyboardMarkup:
    """生成闪租页键盘"""
    session = get_user_session(user_id)
    
    # Duration按钮行 - 单行布局，使用🔸高亮
    duration_buttons = []
    durations = [("1h", "1h"), ("1d", "1d"), ("3d", "3d"), ("7d", "7d"), ("14d", "14d")]
    for label, value in durations:
        display_text = f"🔸 {label}" if session.selected_duration == value else label
        duration_buttons.append(InlineKeyboardButton(display_text, callback_data=f"buy_energy:duration:{value}"))
    
    # Energy按钮行 - 单行布局，使用🔹高亮
    energy_buttons = []
    energies = [("65K", "65K"), ("135K", "135K"), ("270K", "270K"), ("540K", "540K"), ("1M", "1M")]
    for label, value in energies:
        display_text = f"🔹 {label}" if session.selected_energy == value else label
        energy_buttons.append(InlineKeyboardButton(display_text, callback_data=f"buy_energy:energy:{value}"))
    
    # Other amount按钮 - 使用铅笔图标
    other_selected = session.selected_energy not in ["65K", "135K", "270K", "540K", "1M"]
    other_text = f"✏️ Other amount" if not other_selected else f"🔹 ✏️ Other amount"
    other_button = InlineKeyboardButton(other_text, callback_data="buy_energy:energy:custom")
    
    # 地址和余额操作按钮 - 使用绿色对勾图标
    address_button_text = "✅ Change address" if session.selected_address else "✅ Select address"
    address_buttons = [
        InlineKeyboardButton(address_button_text, callback_data="buy_energy:address:select"),
        InlineKeyboardButton("Address balance", callback_data="buy_energy:balance:refresh")
    ]
    
    # 提交和退出按钮 - Later使用红色叉号
    confirm_enabled = session.selected_address is not None
    confirm_text = "Confirm / Pay" if confirm_enabled else "⚠️ Select address first"
    action_buttons = [
        InlineKeyboardButton(confirm_text, callback_data="buy_energy:pay:confirm" if confirm_enabled else "buy_energy:warning:address"),
        InlineKeyboardButton("❌ Later", callback_data="buy_energy:close")
    ]
    
    keyboard = [
        duration_buttons,      # 第一行：1h, 1d, 3d, 7d, 14d（单行）
        energy_buttons,        # 第二行：65K, 135K, 270K, 540K, 1M（单行）
        [other_button],        # 第三行：Other amount
        address_buttons,       # 第四行：地址相关
        action_buttons         # 第五行：确认和稍后
    ]
    
    return InlineKeyboardMarkup(keyboard)

async def handle_buy_energy_callback(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """处理闪租页回调"""
    query = update.callback_query
    user_id = query.from_user.id
    callback_data = query.data
    
    await query.answer()  # 回应回调查询
    
    if callback_data == "main:buy_energy":
        # 从主菜单进入闪租页
        text = generate_buy_energy_text(user_id)
        keyboard = generate_buy_energy_keyboard(user_id)
        await query.edit_message_text(text, reply_markup=keyboard)
        
    elif callback_data.startswith("buy_energy:duration:"):
        # 选择时长
        duration = callback_data.split(":")[-1]
        session = get_user_session(user_id)
        session.selected_duration = duration
        
        # 更新消息
        text = generate_buy_energy_text(user_id)
        keyboard = generate_buy_energy_keyboard(user_id)
        await query.edit_message_text(text, reply_markup=keyboard)
        
    elif callback_data.startswith("buy_energy:energy:"):
        # 选择能量
        energy = callback_data.split(":")[-1]
        session = get_user_session(user_id)
        
        if energy == "custom":
            # 处理自定义能量输入
            session.pending_input = "custom_energy"
            # 发送提示消息
            prompt_text = "✏️ 请发送您需要的能量数量（整数，例如 65000）："
            prompt_keyboard = InlineKeyboardMarkup([[
                InlineKeyboardButton("❌ 取消", callback_data="buy_energy:cancel_input")
            ]])
            await context.bot.send_message(
                chat_id=user_id,
                text=prompt_text,
                reply_markup=prompt_keyboard
            )
        else:
            session.selected_energy = energy
            # 更新消息
            text = generate_buy_energy_text(user_id)
            keyboard = generate_buy_energy_keyboard(user_id)
            await query.edit_message_text(text, reply_markup=keyboard)
            
    elif callback_data == "buy_energy:address:select":
        # 地址选择功能（暂时用Mock地址）
        await show_address_selection(query, context)
        
    elif callback_data == "buy_energy:balance:refresh":
        # 刷新地址余额
        await refresh_address_balance(query, context)
        
    elif callback_data == "buy_energy:pay:confirm":
        # 确认支付
        await confirm_payment(query, context)
        
    elif callback_data == "buy_energy:warning:address":
        # 地址未选择警告
        await query.answer("请先选择一个地址！", show_alert=True)
        
    elif callback_data == "buy_energy:close":
        # 关闭闪租页
        await query.edit_message_text("您可以随时通过主菜单返回。\n\n发送 /start 重新开始。")
        
    elif callback_data == "buy_energy:cancel_input":
        # 取消输入
        session = get_user_session(user_id)
        session.pending_input = None
        await query.delete_message()  # 删除提示消息

async def show_address_selection(query, context):
    """显示地址选择界面"""
    user_id = query.from_user.id
    
    # Mock地址列表
    mock_addresses = [
        "TRX9Uhjn948ynC8J2LRRHVpbdYT6GKRTLz",
        "TBrLXQs4q2XQ29dGFbyiTCcvXuN2tGJvSK", 
        "TNRLJjF9uGp2gZMZVQWcJSkbKnH7wdvGRw"
    ]
    
    text = "选择用于接收能量的地址："
    
    keyboard = []
    for i, addr in enumerate(mock_addresses):
        short_addr = f"{addr[:6]}...{addr[-4:]}"
        keyboard.append([InlineKeyboardButton(f"📍 {short_addr}", callback_data=f"address:select:{i}")])
    
    keyboard.append([
        InlineKeyboardButton("➕ 添加新地址", callback_data="address:new"),
        InlineKeyboardButton("⬅️ 返回", callback_data="address:back")
    ])
    
    await query.edit_message_text(text, reply_markup=InlineKeyboardMarkup(keyboard))

async def refresh_address_balance(query, context):
    """刷新地址余额"""
    user_id = query.from_user.id
    session = get_user_session(user_id)
    
    if not session.selected_address:
        await query.answer("请先选择一个地址！", show_alert=True)
        return
    
    # 显示刷新提示
    await query.answer("🔄 正在更新余额...")
    
    # 模拟异步查询（实际中这里会调用TRON API）
    import random
    await asyncio.sleep(1)  # 模拟网络延迟
    
    # Mock更新余额数据
    session.user_balance["TRX"] = f"{random.uniform(50, 200):.2f}"
    
    # 更新消息
    text = generate_buy_energy_text(user_id)
    keyboard = generate_buy_energy_keyboard(user_id)
    await query.edit_message_text(text, reply_markup=keyboard)

async def confirm_payment(query, context):
    """确认支付处理"""
    user_id = query.from_user.id
    session = get_user_session(user_id)
    
    # 生成订单摘要
    energy_display = format_energy(session.selected_energy)
    text = f"""📋 订单确认

能量数量: {energy_display}
租赁时长: {session.selected_duration}
接收地址: {session.selected_address[:6]}...{session.selected_address[-4:]}
费用: {session.computed_cost} TRX

⚠️ 这是演示版本，不会执行实际支付。

确认要继续吗？"""
    
    keyboard = InlineKeyboardMarkup([
        [
            InlineKeyboardButton("✅ 确认支付", callback_data="payment:confirm"),
            InlineKeyboardButton("❌ 取消", callback_data="buy_energy:back")
        ]
    ])
    
    await query.edit_message_text(text, reply_markup=keyboard)