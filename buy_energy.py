import asyncio
import os
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import ContextTypes
from models import get_user_session, calculate_mock_cost, format_energy, get_wallet_addresses, add_wallet_address
from tron_api import TronAPI
from config import TRON_NETWORK

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
        print(f"DEBUG: 检测到buy_energy:pay:confirm回调，用户ID: {user_id}")
        await confirm_payment(query, context)
        
    elif callback_data == "buy_energy:close":
        # 关闭闪租页 - 清除地址选择状态
        session = get_user_session(user_id)
        session.selected_address = None
        session.address_balance = None
        await query.edit_message_text("您可以随时通过主菜单返回。\n\n发送 /start 重新开始。")
        
    elif callback_data == "buy_energy:cancel_input":
        # 取消输入
        session = get_user_session(user_id)
        session.pending_input = None
        await query.delete_message()  # 删除提示消息
        
    elif callback_data == "insufficient:later":
        # 关闭余额不足消息
        await query.delete_message()
        
    elif callback_data == "deposit:show":
        # 显示充值页面
        await show_deposit_page(query, context)
        
    elif callback_data == "deposit:later":
        # 关闭充值页面
        await query.delete_message()
        
    elif callback_data == "success:buy_more":
        # 从成功页面返回闪租页
        await return_to_buy_energy_page(query, context)
        
    elif callback_data == "success:check_balance":
        # 显示订单详情和余额信息
        await show_order_details(query, context)
        
    elif callback_data == "order:check_status":
        # 查询最新订单状态
        await show_order_status(query, context)
        
    elif callback_data == "deposit:rates":
        # 显示详细汇率信息
        await show_exchange_rates(query, context)
        
    elif callback_data == "order:close":
        # 关闭订单详情页面
        await query.delete_message()

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
            network=TRON_NETWORK,
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
    """确认支付处理 - BUY按钮点击处理"""
    user_id = query.from_user.id
    session = get_user_session(user_id)
    
    print(f"DEBUG: BUY按钮被点击，用户ID: {user_id}")
    print(f"DEBUG: 用户会话状态 - 能量: {session.selected_energy}, 时长: {session.selected_duration}, 地址: {session.selected_address}")
    
    # 获取所需费用和用户余额
    required_cost = float(session.computed_cost)
    user_balance_info = session.user_balance
    user_trx_balance = float(user_balance_info['TRX'])
    
    print(f"DEBUG: 所需费用: {required_cost} TRX, 用户余额: {user_trx_balance} TRX")
    
    # 检查余额是否充足
    if required_cost > user_trx_balance:
        print(f"DEBUG: 余额不足，显示充值消息")
        # 余额不足，显示充值消息
        await show_insufficient_balance_message(query, context, required_cost, user_trx_balance)
    else:
        print(f"DEBUG: 余额充足，开始处理支付")
        # 余额充足，执行支付并显示成功消息
        await process_successful_payment(query, context, session, required_cost)

async def process_successful_payment(query, context, session, cost: float):
    """处理成功支付流程"""
    user_id = session.user_id
    
    print(f"DEBUG: 开始处理成功支付，用户: {user_id}, 费用: {cost}")
    
    # 解析能量数量为整数
    energy_amount = parse_energy_amount(session.selected_energy)
    print(f"DEBUG: 解析能量数量: {energy_amount}")
    
    # 调用后端API创建真实订单
    print(f"DEBUG: 准备创建订单 - 能量: {energy_amount}, 时长: {session.selected_duration}, 地址: {session.selected_address}")
    order_result = session.create_order(
        energy_amount=energy_amount,
        duration=session.selected_duration,
        receive_address=session.selected_address
    )
    print(f"DEBUG: 订单创建结果: {order_result}")
    
    if order_result["success"]:
        # 订单创建成功
        order_data = order_result["order"]
        session.last_order_id = order_data["id"]
        session.last_transaction_hash = order_data.get("tx_hash", "pending")
        
        print(f"DEBUG: 订单创建成功，ID: {order_data['id']}")
        
        # 格式化能量数量显示
        energy_display = format_energy_display(session.selected_energy)
        
        # 创建成功消息
        text = f"""✅ 交易成功完成！

🎯 地址: {session.selected_address[:6]}...{session.selected_address[-6:]}
⚡ 数量: {energy_display}
📅 时长: {session.selected_duration}
💵 费用: {cost:.2f} TRX
🆔 订单ID: {order_data["id"][:8]}
💰 余额: {session.user_balance['TRX']} TRX

预计能量将在几分钟内到达您的钱包。
✅ 已发送。"""
        
        keyboard = InlineKeyboardMarkup([
            [
                InlineKeyboardButton("⚡ 继续购买", callback_data="success:buy_more"),
                InlineKeyboardButton("📊 订单状态", callback_data="order:check_status")
            ],
            [
                InlineKeyboardButton("🔄 查看余额", callback_data="success:check_balance")
            ]
        ])
        
        print(f"DEBUG: 准备发送成功消息到用户 {user_id}")
        
        try:
            # 发送成功消息
            message = await context.bot.send_message(
                chat_id=user_id,
                text=text,
                reply_markup=keyboard,
                parse_mode='Markdown'
            )
            print(f"DEBUG: 成功消息发送完成，消息ID: {message.message_id}")
        except Exception as e:
            print(f"DEBUG: 发送成功消息失败: {e}")
            # 尝试发送简单版本
            await context.bot.send_message(
                chat_id=user_id,
                text=f"✅ 订单创建成功！订单ID: {order_data['id'][:8]}"
            )
    else:
        # 订单创建失败
        error_msg = order_result.get("message", "订单创建失败")
        print(f"DEBUG: 订单创建失败: {error_msg}")
        await query.answer(f"订单失败: {error_msg}", show_alert=True)

def parse_energy_amount(energy_str: str) -> int:
    """解析能量字符串为整数值"""
    if energy_str.endswith("K"):
        if energy_str == "65K":
            return 65000
        elif energy_str == "135K":
            return 135000
        elif energy_str == "270K":
            return 270000
        elif energy_str == "540K":
            return 540000
        else:
            return int(float(energy_str[:-1]) * 1000)
    elif energy_str.endswith("M"):
        if energy_str == "1M":
            return 1000000
        else:
            return int(float(energy_str[:-1]) * 1000000)
    elif energy_str.isdigit():
        return int(energy_str)
    else:
        return 65000  # 默认值

def format_energy_display(energy_str: str) -> str:
    """格式化能量显示"""
    energy_amount = parse_energy_amount(energy_str)
    return f"{energy_amount:,}".replace(",", " ")

async def show_insufficient_balance_message(query, context, required_cost: float, current_balance: float):
    """显示余额不足充值提醒消息"""
    print(f"DEBUG: 准备显示余额不足消息，所需: {required_cost}, 当前: {current_balance}")
    
    # 计算需要充值的数量（加上一些缓冲）
    needed_amount = required_cost - current_balance
    recommended_amount = max(10.0, needed_amount + 5.0)  # 至少充值10 TRX，额外加5 TRX缓冲
    
    text = f"""💰 余额不足提醒

📊 订单详情：
💵 所需费用：{required_cost:.2f} TRX
💳 当前余额：{current_balance:.3f} TRX
❌ 不足金额：{needed_amount:.2f} TRX

💡 建议充值：{recommended_amount:.0f} TRX
（包含缓冲金额，可用于多次交易）

🔄 支持的充值方式：
• TRX (TRON网络)
• USDT TRC20

💱 汇率：1 TRX = 0.38826 USDT
例如充值 {recommended_amount:.0f} USDT ≈ {recommended_amount/0.38826:.1f} TRX

⚡ 充值后余额通常在5分钟内到账"""
    
    keyboard = InlineKeyboardMarkup([
        [
            InlineKeyboardButton("💳 立即充值", callback_data="deposit:show"),
        ],
        [
            InlineKeyboardButton("📊 查看详细汇率", callback_data="deposit:rates"),
            InlineKeyboardButton("❌ 稍后充值", callback_data="insufficient:later")
        ],
        [
            InlineKeyboardButton("🔙 返回购买页", callback_data="main:buy_energy")
        ]
    ])
    
    print(f"DEBUG: 准备发送余额不足消息到用户 {query.from_user.id}")
    
    try:
        # 发送新消息而不是编辑原消息
        message = await context.bot.send_message(
            chat_id=query.from_user.id,
            text=text,
            reply_markup=keyboard,
            parse_mode='Markdown'
        )
        print(f"DEBUG: 余额不足消息发送成功，消息ID: {message.message_id}")
    except Exception as e:
        print(f"DEBUG: 发送余额不足消息失败: {e}")
        raise

async def show_exchange_rates(query, context):
    """显示详细汇率信息"""
    text = """💱 详细充值汇率信息

🔸 当前汇率（实时更新）
• 1 TRX = 0.38826 USDT
• 1 USDT = 2.576 TRX

📊 充值参考表：
┌──────────────┬──────────────┐
│   TRX金额    │  USDT等值    │
├──────────────┼──────────────┤
│   10 TRX     │   3.88 USDT  │
│   20 TRX     │   7.77 USDT  │
│   50 TRX     │  19.41 USDT  │
│  100 TRX     │  38.83 USDT  │
│  200 TRX     │  77.65 USDT  │
└──────────────┴──────────────┘

⚠️ 重要说明：
• 最低充值金额：10 TRX 或 10 USDT
• 充值小于最低金额不会到账
• 充值确认时间：通常3-5分钟
• 汇率可能有轻微波动

🔄 支持的网络：
• TRX：TRON主网
• USDT：TRC20（TRON网络）"""
    
    keyboard = InlineKeyboardMarkup([
        [
            InlineKeyboardButton("💳 立即充值", callback_data="deposit:show")
        ],
        [
            InlineKeyboardButton("🔙 返回", callback_data="insufficient:later")
        ]
    ])
    
    await query.edit_message_text(text, reply_markup=keyboard, parse_mode='Markdown')

async def show_deposit_page(query, context):
    deposit_address = "TYwv7C4Fik2tYuHBwuNSzrnJ4Bw7NukyRb"
    
    text = f"""Transfer the desired amount to the wallet below:

{deposit_address}

❗Only TRX and USDT TRC20 are accepted for payment.

When paying in USDT TRC20, the rate is 1 TRX = 0.38826 USDT. For example,
when replenishing the balance by 10 USDT
your balance will receive: 25.75594 TRX

After replenishment, your balance will be updated within 5 minutes.

🔁 Refund

A 10% fee applies to mistaken top-ups, withdrawals, or refunds to cover costs and maintain stable service. Please double-check before transferring funds.

⚠️ Minimum deposit amount is 10 TRX / 10 USDT. If you send a smaller amount, the balance will not be credited  ⏳ [ 03:00 ]"""
    
    keyboard = InlineKeyboardMarkup([
        [InlineKeyboardButton("❌ Later", callback_data="deposit:later")]
    ])
    
    # 删除原消息并发送新消息
    await query.delete_message()
    
    # 发送充值页面消息
    deposit_message = await context.bot.send_message(
        chat_id=query.from_user.id,
        text=text,
        reply_markup=keyboard
    )
    
    # 启动倒计时任务
    asyncio.create_task(countdown_timer(context, query.from_user.id, deposit_message.message_id))

async def countdown_timer(context, chat_id: int, message_id: int):
    """3分钟倒计时功能"""
    deposit_address = "TYwv7C4Fik2tYuHBwuNSzrnJ4Bw7NukyRb"
    
    for remaining_seconds in range(180, -1, -5):  # 180秒到0，每5秒更新一次
        minutes = remaining_seconds // 60
        seconds = remaining_seconds % 60
        time_display = f"{minutes:02d}:{seconds:02d}"
        
        text = f"""Transfer the desired amount to the wallet below:

{deposit_address}

❗Only TRX and USDT TRC20 are accepted for payment.

When paying in USDT TRC20, the rate is 1 TRX = 0.38826 USDT. For example,
when replenishing the balance by 10 USDT
your balance will receive: 25.75594 TRX

After replenishment, your balance will be updated within 5 minutes.

🔁 Refund

A 10% fee applies to mistaken top-ups, withdrawals, or refunds to cover costs and maintain stable service. Please double-check before transferring funds.

⚠️ Minimum deposit amount is 10 TRX / 10 USDT. If you send a smaller amount, the balance will not be credited  ⏳ [ {time_display} ]"""
        
        keyboard = InlineKeyboardMarkup([
            [InlineKeyboardButton("❌ Later", callback_data="deposit:later")]
        ])
        
        try:
            await context.bot.edit_message_text(
                chat_id=chat_id,
                message_id=message_id,
                text=text,
                reply_markup=keyboard
            )
        except Exception:
            # 如果消息已被删除或编辑失败，停止倒计时
            return
            
        if remaining_seconds > 0:
            await asyncio.sleep(5)  # 等待5秒
    
    # 倒计时结束，删除消息
    try:
        await context.bot.delete_message(chat_id=chat_id, message_id=message_id)
    except Exception:
        pass  # 忽略删除失败的情况

async def return_to_buy_energy_page(query, context):
    """返回闪租页面"""
    user_id = query.from_user.id
    
    # 生成闪租页面内容
    text = generate_buy_energy_text(user_id)
    keyboard = generate_buy_energy_keyboard(user_id)
    
    # 编辑消息内容
    await query.edit_message_text(text, reply_markup=keyboard, parse_mode='Markdown')

async def show_order_details(query, context):
    """显示订单详情"""
    user_id = query.from_user.id
    session = get_user_session(user_id)
    
    # 生成TronScan链接
    tronscan_link = f"https://tronscan.org/#/transaction/{session.last_transaction_hash}"
    
    # 格式化能量数量显示
    energy_value = session.selected_energy
    if energy_value.endswith("K"):
        if energy_value == "65K":
            energy_display = "65 000"
        elif energy_value == "135K":
            energy_display = "135 000"
        elif energy_value == "270K":
            energy_display = "270 000"
        elif energy_value == "540K":
            energy_display = "540 000"
        else:
            energy_display = energy_value
    elif energy_value.endswith("M"):
        if energy_value == "1M":
            energy_display = "1 000 000"
        else:
            energy_display = energy_value
    elif energy_value.isdigit():
        val = int(energy_value)
        energy_display = f"{val:,}".replace(",", " ")
    else:
        energy_display = energy_value
    
    # 创建订单详情消息
    text = f"""📋 Order Details

🆔 Order ID: {session.last_order_id}
🔗 Transaction: [TRONSCAN LINK]({tronscan_link})
🎯 Wallet Address: {session.selected_address}
⚡ Quantity: {energy_display}
📅 Duration: {session.selected_duration}
💵 Cost: {session.computed_cost} TRX
💰 Balance: {session.user_balance['TRX']} TRX"""
    
    keyboard = InlineKeyboardMarkup([
        [
            InlineKeyboardButton("⚡ Buy more", callback_data="success:buy_more"),
            InlineKeyboardButton("❌ Close", callback_data="order:close")
        ]
    ])
    
    # 发送订单详情消息
    await context.bot.send_message(
        chat_id=user_id,
        text=text,
        reply_markup=keyboard,
        parse_mode='Markdown'
    )

async def show_order_status(query, context):
    """显示最新订单状态"""
    user_id = query.from_user.id
    session = get_user_session(user_id)
    
    if not session.last_order_id:
        await query.answer("没有找到最近的订单", show_alert=True)
        return
    
    # 显示状态查询提示
    status_message = await context.bot.send_message(
        chat_id=user_id,
        text="🔍 查询订单状态中..."
    )
    
    try:
        # 调用后端API查询订单状态
        order_data = session.get_order_status(session.last_order_id)
        
        if order_data:
            # 格式化状态显示
            status_emoji = {
                "pending": "⏳",
                "processing": "🔄", 
                "completed": "✅",
                "failed": "❌",
                "cancelled": "🚫"
            }.get(order_data["status"], "❓")
            
            status_text = {
                "pending": "等待处理",
                "processing": "处理中",
                "completed": "已完成",
                "failed": "失败",
                "cancelled": "已取消"
            }.get(order_data["status"], "未知状态")
            
            # 构建状态消息
            text = f"""📊 订单状态查询

🆔 订单ID: {order_data["id"][:8]}...
{status_emoji} 状态: {status_text}
⚡ 能量数量: {order_data["energy_amount"]:,}
📅 租用时长: {order_data["duration_hours"]}小时
💵 费用: {order_data["cost_trx"]} TRX
📍 接收地址: {order_data["receive_address"][:8]}...

📅 创建时间: {order_data["created_at"][:19].replace('T', ' ')}"""

            if order_data.get("tx_hash"):
                text += f"\n🔗 交易哈希: {order_data['tx_hash'][:8]}..."
            
            if order_data.get("error_message"):
                text += f"\n❌ 错误信息: {order_data['error_message']}"
            
            if order_data.get("completed_at"):
                text += f"\n✅ 完成时间: {order_data['completed_at'][:19].replace('T', ' ')}"
            
            keyboard = InlineKeyboardMarkup([
                [
                    InlineKeyboardButton("🔄 刷新状态", callback_data="order:check_status"),
                    InlineKeyboardButton("❌ 关闭", callback_data="order:close")
                ]
            ])
            
            await status_message.edit_text(text, reply_markup=keyboard)
            
        else:
            await status_message.edit_text("❌ 订单查询失败，请稍后再试")
            
    except Exception as e:
        logger.error(f"查询订单状态异常: {e}")
        await status_message.edit_text("❌ 查询订单状态时发生错误")