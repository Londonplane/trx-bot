import asyncio
import os
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import ContextTypes
from models import get_user_session, calculate_mock_cost, format_energy, get_wallet_addresses, add_wallet_address
from tron_api import TronAPI

def generate_buy_energy_text(user_id: int) -> str:
    """生成闪租页文本内容"""
    session = get_user_session(user_id)
    
    # 重新计算成本
    session.computed_cost = calculate_mock_cost(session.selected_energy, session.selected_duration)
    
    # 格式化能量显示（数字格式，用空格分隔千位）
    energy_value = session.selected_energy
    if energy_value.endswith("K"):
        if energy_value == "65K":
            energy_display = "65 000"
            energy_command = "65000"
        elif energy_value == "135K":
            energy_display = "135 000"
            energy_command = "135000"
        elif energy_value == "270K":
            energy_display = "270 000"
            energy_command = "270000"
        elif energy_value == "540K":
            energy_display = "540 000"
            energy_command = "540000"
        else:
            energy_display = energy_value
            energy_command = energy_value.replace("K", "000")
    elif energy_value.endswith("M"):
        if energy_value == "1M":
            energy_display = "1 000 000"
            energy_command = "1000000"
        else:
            energy_display = energy_value
            energy_command = energy_value.replace("M", "000000")
    elif energy_value.isdigit():
        # 自定义数量，格式化显示
        val = int(energy_value)
        energy_display = f"{val:,}".replace(",", " ")
        energy_command = energy_value
    else:
        energy_display = energy_value
        energy_command = energy_value
    
    # 开头文案根据是否选择地址决定
    if session.selected_address:
        intro_text = "Calculation of the cost of purchasing energy:"
    else:
        intro_text = "Select the required number of days and energy, and then click Address - to select an address from your favorites or add a new one.\n\nCalculating the cost of purchasing energy:"
    
    # 地址信息部分
    address_section = ""
    if session.selected_address:
        address_display = session.selected_address
        address_section += f"🎯 Address: {address_display}\n"
        
        # 如果有地址余额信息，显示它
        if hasattr(session, 'address_balance') and session.address_balance:
            address_section += f"ℹ️ Address balance:\n"
            address_section += f"TRX: {session.address_balance.get('TRX', '0')}\n"
            address_section += f"ENERGY: {session.address_balance.get('ENERGY', '0')}\n"
            # 显示带宽信息（如果有的话）
            bandwidth = session.address_balance.get('BANDWIDTH')
            if bandwidth and bandwidth != '0':
                address_section += f"BANDWIDTH: {bandwidth}\n"
            address_section += "\n"
    
    # 成本计算部分
    cost_section = f"""⚡️ Amount: {energy_display}
📆 Period: {session.selected_duration} 
💵 Cost: {session.computed_cost} TRX """
    
    # 组装订单命令部分
    if session.selected_address:
        command_address = session.selected_address
    else:
        command_address = "YOUR_TRX_ADDRESS"
    
    command_section = f"""Assemble your order with buttons. If the buttons do not have the required values, use the format command::
`BUY {energy_command} {session.selected_duration} {command_address}`"""
    
    # 余额信息部分
    balance_section = f"Your balance: {session.user_balance['TRX']}"
    
    # 组合最终文本
    text_parts = [intro_text]
    if address_section:
        text_parts.append(address_section)
    text_parts.extend([cost_section, "", command_section, "", balance_section])
    
    return "\n".join(text_parts)

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
    
    # 检查是否完成所有必要选择（时长、能量、地址）
    has_duration = session.selected_duration is not None and session.selected_duration != ""
    has_energy = session.selected_energy is not None and session.selected_energy != ""
    has_address = session.selected_address is not None and session.selected_address != ""
    all_selected = has_duration and has_energy and has_address
    
    keyboard = [
        duration_buttons,      # 第一行：时长选择
        energy_buttons,        # 第二行：能量选择  
        [other_button],        # 第三行：Other amount
    ]
    
    if all_selected:
        # 完整状态：显示BUY、Change address、Address balance、Later
        keyboard.extend([
            [InlineKeyboardButton("✅ BUY", callback_data="buy_energy:pay:confirm")],  # 第四行：BUY按钮
            [                                                                          # 第五行：地址操作
                InlineKeyboardButton("✅ Change address", callback_data="buy_energy:address:select"),
                InlineKeyboardButton("🔄 Address balance", callback_data="buy_energy:balance:refresh")
            ],
            [InlineKeyboardButton("❌ Later", callback_data="buy_energy:close")]       # 第六行：Later
        ])
    else:
        # 初始状态：只显示Select address、Later
        keyboard.extend([
            [InlineKeyboardButton("✅ Select address", callback_data="buy_energy:address:select")],  # 第四行：选择地址
            [InlineKeyboardButton("❌ Later", callback_data="buy_energy:close")]                      # 第五行：Later
        ])
    
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
        await query.edit_message_text(text, reply_markup=keyboard, parse_mode='Markdown')
        
    elif callback_data.startswith("buy_energy:duration:"):
        # 选择时长
        duration = callback_data.split(":")[-1]
        session = get_user_session(user_id)
        session.selected_duration = duration
        
        # 更新消息
        text = generate_buy_energy_text(user_id)
        keyboard = generate_buy_energy_keyboard(user_id)
        await query.edit_message_text(text, reply_markup=keyboard, parse_mode='Markdown')
        
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
                reply_markup=prompt_keyboard,
                parse_mode='Markdown'
            )
        else:
            session.selected_energy = energy
            # 更新消息
            text = generate_buy_energy_text(user_id)
            keyboard = generate_buy_energy_keyboard(user_id)
            await query.edit_message_text(text, reply_markup=keyboard, parse_mode='Markdown')
            
    elif callback_data == "buy_energy:address:select":
        # 地址选择功能（暂时用Mock地址）
        await show_address_selection(query, context)
        
    elif callback_data == "buy_energy:balance:refresh":
        # 刷新地址余额
        await refresh_address_balance(query, context)
        
    elif callback_data == "buy_energy:pay:confirm":
        # 确认支付
        await confirm_payment(query, context)
        
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
    
    # 获取用户的钱包地址列表
    user_addresses = get_wallet_addresses(user_id)
    
    if not user_addresses:
        # 用户还没有绑定地址
        text = """🏠 钱包地址管理

您还没有绑定任何钱包地址。

请添加您的TRON钱包地址来接收能量："""
        
        keyboard = [
            [InlineKeyboardButton("➕ 添加新地址", callback_data="address:new")],
            [InlineKeyboardButton("⬅️ 返回", callback_data="address:back")]
        ]
    else:
        # 显示用户的地址列表
        text = f"""🏠 钱包地址管理

请选择用于接收能量的地址：

📊 共有 {len(user_addresses)} 个地址"""
        
        keyboard = []
        for i, addr in enumerate(user_addresses):
            short_addr = f"{addr[:6]}...{addr[-4:]}"
            # 如果是当前选中的地址，添加标记
            if addr == get_user_session(user_id).selected_address:
                button_text = f"✅ {short_addr}"
            else:
                button_text = f"📍 {short_addr}"
            keyboard.append([InlineKeyboardButton(button_text, callback_data=f"address:select:{i}")])
        
        keyboard.extend([
            [InlineKeyboardButton("➕ 添加新地址", callback_data="address:new")],
            [InlineKeyboardButton("⬅️ 返回", callback_data="address:back")]
        ])
    
    await query.edit_message_text(text, reply_markup=InlineKeyboardMarkup(keyboard), parse_mode='Markdown')

async def refresh_address_balance(query, context):
    """刷新地址余额"""
    user_id = query.from_user.id
    session = get_user_session(user_id)
    
    if not session.selected_address:
        await query.answer("请先选择一个地址！", show_alert=True)
        return
    
    # 显示更新提示消息
    updating_message = await context.bot.send_message(
        chat_id=user_id,
        text="🔄 Updating balance…"
    )
    
    try:
        # 创建API客户端
        api = TronAPI(
            api_url=os.getenv('TRON_API_URL', 'https://api.trongrid.io'),
            api_key=os.getenv('TRON_API_KEY')
        )
        
        # 查询余额
        balance = api.get_account_balance(session.selected_address)
        
        if balance:
            # 更新会话中的余额信息，包含带宽
            session.address_balance = {
                'TRX': f"{balance.trx_balance:.6f}",
                'ENERGY': f"{balance.energy_available:,}",
                'BANDWIDTH': f"{balance.bandwidth_available:,}"
            }
            
            # 重新生成页面
            text = generate_buy_energy_text(user_id)
            keyboard = generate_buy_energy_keyboard(user_id)
            await query.edit_message_text(text, reply_markup=keyboard, parse_mode='Markdown')
            
        else:
            # 查询失败，但不设置为Error，而是提示用户
            await query.answer("余额查询失败，地址可能未激活或网络问题", show_alert=True)
            
    except Exception as e:
        # 异常处理，提供详细错误信息
        await query.answer(f"网络错误: {str(e)[:50]}...", show_alert=True)
    
    finally:
        # 删除更新提示消息
        try:
            await context.bot.delete_message(
                chat_id=user_id,
                message_id=updating_message.message_id
            )
        except Exception:
            pass  # 忽略删除消息时的错误

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