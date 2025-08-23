import logging
import asyncio
import os
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup, BotCommand
from telegram.ext import Application, CommandHandler, CallbackQueryHandler, ContextTypes, MessageHandler, filters
from dotenv import load_dotenv
from tron_api import TronAPI
from models import get_user_session, format_energy
from buy_energy import handle_buy_energy_callback, generate_buy_energy_text, generate_buy_energy_keyboard

# 加载环境变量
load_dotenv()

# 配置日志
logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.INFO
)
logger = logging.getLogger(__name__)


async def handle_callback_query(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """处理所有回调查询"""
    query = update.callback_query
    callback_data = query.data
    
    # 路由到不同的处理器
    if callback_data.startswith("main:buy_energy") or callback_data.startswith("buy_energy:"):
        await handle_buy_energy_callback(update, context)
    elif callback_data.startswith("address:"):
        await handle_address_callback(update, context)
    elif callback_data.startswith("payment:"):
        await handle_payment_callback(update, context)
    elif callback_data.startswith("insufficient:") or callback_data.startswith("deposit:"):
        await handle_buy_energy_callback(update, context)
    elif callback_data.startswith("success:") or callback_data.startswith("order:"):
        await handle_buy_energy_callback(update, context)
    elif callback_data == "main:home":
        await start_command_from_callback(query, context)
    elif callback_data == "main:wallet_management":
        await handle_wallet_management(update, context)
    elif callback_data.startswith("wallet:"):
        await handle_wallet_callback(update, context)
    else:
        # 未实现的功能
        await query.answer(f"功能开发中：{callback_data}")

async def handle_address_callback(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """处理地址相关回调"""
    query = update.callback_query
    user_id = query.from_user.id
    callback_data = query.data
    
    await query.answer()
    
    if callback_data.startswith("address:select:"):
        # 选择地址
        addr_index = int(callback_data.split(":")[-1])
        session = get_user_session(user_id)
        
        # 从用户的钱包地址列表中获取地址
        from models import get_wallet_addresses
        user_addresses = get_wallet_addresses(user_id)
        
        if addr_index < len(user_addresses):
            session.selected_address = user_addresses[addr_index]
            
            # 返回闪租页
            text = generate_buy_energy_text(user_id)
            keyboard = generate_buy_energy_keyboard(user_id)
            await query.edit_message_text(text, reply_markup=keyboard, parse_mode='Markdown')
        else:
            await query.answer("地址索引无效", show_alert=True)
        
    elif callback_data == "address:new":
        # 添加新地址
        session = get_user_session(user_id)
        session.pending_input = "new_address"
        
        prompt_text = """➕ 添加新的TRON钱包地址

请发送您的TRON钱包地址用于接收能量：

📝 地址格式示例：
`TQ5kjKLLm9X4L2D1JgogNis6V1YoAm6sv2`

⚠️ 请确保地址正确，错误的地址可能导致能量丢失。"""
        
        prompt_keyboard = InlineKeyboardMarkup([[
            InlineKeyboardButton("❌ 取消", callback_data="address:cancel_new")
        ]])
        await context.bot.send_message(
            chat_id=user_id,
            text=prompt_text,
            reply_markup=prompt_keyboard,
            parse_mode='Markdown'
        )
        
    elif callback_data == "address:back":
        # 返回闪租页
        text = generate_buy_energy_text(user_id)
        keyboard = generate_buy_energy_keyboard(user_id)
        await query.edit_message_text(text, reply_markup=keyboard, parse_mode='Markdown')
        
    elif callback_data == "address:cancel_new":
        # 取消添加新地址
        session = get_user_session(user_id)
        session.pending_input = None
        await query.delete_message()

async def handle_payment_callback(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """处理支付相关回调"""
    query = update.callback_query
    user_id = query.from_user.id
    callback_data = query.data
    
    await query.answer()
    
    if callback_data == "payment:confirm":
        # 确认支付（Mock）
        session = get_user_session(user_id)
        energy_display = format_energy(session.selected_energy)
        
        success_text = f"""✅ 支付成功！

订单详情：
• 能量: {energy_display}
• 时长: {session.selected_duration}
• 地址: {session.selected_address[:6]}...{session.selected_address[-4:]}
• 费用: {session.computed_cost} TRX

注：这是演示版本，未执行实际转账。

感谢使用TRON能量助手！"""
        
        keyboard = InlineKeyboardMarkup([[
            InlineKeyboardButton("🏠 返回主菜单", callback_data="main:home"),
            InlineKeyboardButton("📋 查看订单", callback_data="main:orders")
        ]])
        
        await query.edit_message_text(success_text, reply_markup=keyboard, parse_mode='Markdown')
        
    elif callback_data == "buy_energy:back":
        # 返回闪租页
        text = generate_buy_energy_text(user_id)
        keyboard = generate_buy_energy_keyboard(user_id)
        await query.edit_message_text(text, reply_markup=keyboard, parse_mode='Markdown')

async def handle_balance_callback(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """处理余额查询回调"""
    query = update.callback_query
    user_id = query.from_user.id
    
    await query.answer()
    
    # 获取用户会话
    session = get_user_session(user_id)
    
    # 检查用户是否已选择地址
    if not hasattr(session, 'selected_address') or not session.selected_address:
        # 用户还没有选择地址，提示选择
        error_msg = """❌ 请先选择钱包地址

请点击"Receive Address"选择您的钱包地址，然后再查询余额。"""
        
        keyboard = InlineKeyboardMarkup([[
            InlineKeyboardButton("🏠 返回主菜单", callback_data="main:home")
        ]])
        
        await query.edit_message_text(error_msg, reply_markup=keyboard, parse_mode='Markdown')
        return
    
    address = session.selected_address
    
    # 显示查询中的消息
    loading_text = f"""🔍 正在查询地址余额...

📍 查询地址: `{address[:6]}...{address[-6:]}`

请稍候..."""
    await query.edit_message_text(loading_text, parse_mode='Markdown')
    
    try:
        # 创建API客户端并查询余额
        api = TronAPI(
            api_url=os.getenv('TRON_API_URL', 'https://api.trongrid.io'),
            api_key=os.getenv('TRON_API_KEY')
        )
        
        # 查询余额
        balance = api.get_account_balance(address)
        
        if balance:
            # 查询成功，显示结果
            message = api.format_balance_message(balance)
            keyboard = InlineKeyboardMarkup([[
                InlineKeyboardButton("🔄 刷新余额", callback_data="main:balance"),
                InlineKeyboardButton("🔙 返回闪租页", callback_data="main:buy_energy")
            ]])
            
            await query.edit_message_text(message, reply_markup=keyboard, parse_mode='Markdown')
            
        else:
            # 查询失败
            error_msg = f"""❌ 余额查询失败

📍 查询地址: `{address}`

可能的原因：
• 地址尚未激活（需要先接收一次TRX转账）
• 网络连接问题
• API服务暂时不可用

💡 提示：新地址需要先接收至少0.1 TRX才会被激活。"""
            
            keyboard = InlineKeyboardMarkup([[
                InlineKeyboardButton("🔄 重试", callback_data="main:balance"),
                InlineKeyboardButton("🔙 返回闪租页", callback_data="main:buy_energy")
            ]])
            
            await query.edit_message_text(error_msg, reply_markup=keyboard, parse_mode='Markdown')
            
    except Exception as e:
        logger.error(f"余额查询异常: {e}")
        await query.edit_message_text(
            f"""❌ 查询过程中发生错误

📍 查询地址: `{address}`

请稍后重试，或检查地址是否正确。""",
            reply_markup=InlineKeyboardMarkup([[
                InlineKeyboardButton("🔄 重试", callback_data="main:balance"),
                InlineKeyboardButton("🔙 返回闪租页", callback_data="main:buy_energy")
            ]]),
            parse_mode='Markdown'
        )

async def handle_balance_query_callback(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """处理余额查询相关回调"""
    query = update.callback_query
    user_id = query.from_user.id
    callback_data = query.data
    
    await query.answer()
    
    if callback_data == "balance:cancel":
        # 取消余额查询，返回主菜单
        session = get_user_session(user_id)
        session.pending_input = None
        
        # 调用start_command显示主菜单
        await start_command_from_callback(query, context)

async def handle_wallet_management(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """处理钱包管理主页面"""
    query = update.callback_query
    user_id = query.from_user.id
    
    await query.answer()
    
    # 获取用户的钱包地址列表
    from models import get_wallet_addresses
    user_addresses = get_wallet_addresses(user_id)
    
    if not user_addresses:
        text = """🏦 钱包管理

您还没有绑定任何钱包地址。

请添加您的TRON钱包地址："""
        keyboard = [
            [InlineKeyboardButton("➕ 添加新地址", callback_data="wallet:add")],
            [InlineKeyboardButton("🏠 返回主菜单", callback_data="main:home")]
        ]
    else:
        text = f"""🏦 钱包管理

📊 共有 {len(user_addresses)} 个钱包地址

地址列表："""
        
        keyboard = []
        for i, addr in enumerate(user_addresses):
            short_addr = f"{addr[:8]}...{addr[-6:]}"
            keyboard.append([
                InlineKeyboardButton(f"📍 {short_addr}", callback_data=f"wallet:view:{i}"),
                InlineKeyboardButton("❌", callback_data=f"wallet:delete:{i}")
            ])
        
        keyboard.extend([
            [InlineKeyboardButton("➕ 添加新地址", callback_data="wallet:add")],
            [InlineKeyboardButton("🏠 返回主菜单", callback_data="main:home")]
        ])
    
    await query.edit_message_text(text, reply_markup=InlineKeyboardMarkup(keyboard), parse_mode='Markdown')

async def handle_wallet_callback(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """处理钱包相关回调"""
    query = update.callback_query
    user_id = query.from_user.id
    callback_data = query.data
    
    await query.answer()
    
    if callback_data == "wallet:add":
        # 添加新地址
        session = get_user_session(user_id)
        session.pending_input = "wallet_new_address"
        
        prompt_text = """➕ 添加新的TRON钱包地址

请发送您的TRON钱包地址：

📝 地址格式示例：
`TQ5kjKLLm9X4L2D1JgogNis6V1YoAm6sv2`

⚠️ 请确保地址正确。"""
        
        prompt_keyboard = InlineKeyboardMarkup([[
            InlineKeyboardButton("❌ 取消", callback_data="wallet:cancel_add")
        ]])
        await context.bot.send_message(
            chat_id=user_id,
            text=prompt_text,
            reply_markup=prompt_keyboard,
            parse_mode='Markdown'
        )
        
    elif callback_data.startswith("wallet:view:"):
        # 查看地址详情
        addr_index = int(callback_data.split(":")[-1])
        from models import get_wallet_addresses
        user_addresses = get_wallet_addresses(user_id)
        
        if addr_index < len(user_addresses):
            address = user_addresses[addr_index]
            await show_address_details(query, context, address)
        else:
            await query.answer("地址索引无效", show_alert=True)
            
    elif callback_data.startswith("wallet:delete:"):
        # 删除地址确认
        addr_index = int(callback_data.split(":")[-1])
        from models import get_wallet_addresses
        user_addresses = get_wallet_addresses(user_id)
        
        if addr_index < len(user_addresses):
            address = user_addresses[addr_index]
            short_addr = f"{address[:8]}...{address[-6:]}"
            
            text = f"""⚠️ 删除地址确认

确定要删除以下地址吗？

📍 {short_addr}
`{address}`

⚠️ 此操作无法撤销！"""
            
            keyboard = InlineKeyboardMarkup([
                [
                    InlineKeyboardButton("✅ 确认删除", callback_data=f"wallet:confirm_delete:{addr_index}"),
                    InlineKeyboardButton("❌ 取消", callback_data="wallet:back")
                ]
            ])
            await query.edit_message_text(text, reply_markup=keyboard, parse_mode='Markdown')
        else:
            await query.answer("地址索引无效", show_alert=True)
            
    elif callback_data.startswith("wallet:confirm_delete:"):
        # 确认删除地址
        addr_index = int(callback_data.split(":")[-1])
        from models import get_wallet_addresses, remove_wallet_address
        user_addresses = get_wallet_addresses(user_id)
        
        if addr_index < len(user_addresses):
            address = user_addresses[addr_index]
            if remove_wallet_address(user_id, address):
                await query.answer("✅ 地址已删除", show_alert=True)
                # 返回钱包管理页面
                await handle_wallet_management(update, context)
            else:
                await query.answer("❌ 删除失败", show_alert=True)
        else:
            await query.answer("地址索引无效", show_alert=True)
            
    elif callback_data == "wallet:back":
        # 返回钱包管理主页面
        await handle_wallet_management(update, context)
        
    elif callback_data == "wallet:cancel_add":
        # 取消添加新地址
        session = get_user_session(user_id)
        session.pending_input = None
        await query.delete_message()
        
    elif callback_data.startswith("wallet:refresh:"):
        # 刷新地址余额
        address = callback_data.split(":", 2)[-1]  # 获取完整地址
        await refresh_wallet_address_balance(query, context, address)

async def show_address_details(query, context, address):
    """显示地址详情"""
    user_id = query.from_user.id
    
    # 先显示基本信息
    short_addr = f"{address[:8]}...{address[-6:]}"
    text = f"""📍 钱包地址详情

地址: {short_addr}
`{address}`

🔄 正在查询余额信息..."""
    
    keyboard = InlineKeyboardMarkup([
        [
            InlineKeyboardButton("🔄 刷新余额", callback_data=f"wallet:refresh:{address}"),
            InlineKeyboardButton("⬅️ 返回", callback_data="wallet:back")
        ]
    ])
    
    await query.edit_message_text(text, reply_markup=keyboard, parse_mode='Markdown')
    
    # 异步查询余额
    try:
        from tron_api import TronAPI
        import os
        api = TronAPI(
            api_url=os.getenv('TRON_API_URL', 'https://api.trongrid.io'),
            api_key=os.getenv('TRON_API_KEY')
        )
        
        balance = api.get_account_balance(address)
        
        if balance:
            text = f"""📍 钱包地址详情

地址: {short_addr}
`{address}`

💰 余额信息:
TRX: {balance.trx_balance:.6f}
ENERGY: {balance.energy_available:,}
BANDWIDTH: {balance.bandwidth_available:,}"""
        else:
            text = f"""📍 钱包地址详情

地址: {short_addr}
`{address}`

❌ 地址可能未激活或网络异常
💡 新地址需要先接收至少0.1 TRX才会被激活"""
            
    except Exception as e:
        text = f"""📍 钱包地址详情

地址: {short_addr}
`{address}`

❌ 查询余额时发生错误
请稍后重试"""
    
    await query.edit_message_text(text, reply_markup=keyboard, parse_mode='Markdown')

async def refresh_wallet_address_balance(query, context, address):
    """刷新钱包地址余额"""
    user_id = query.from_user.id
    
    # 显示刷新中的消息
    short_addr = f"{address[:8]}...{address[-6:]}"
    loading_text = f"""📍 钱包地址详情

地址: {short_addr}
`{address}`

🔄 正在刷新余额信息..."""
    
    keyboard = InlineKeyboardMarkup([
        [
            InlineKeyboardButton("🔄 刷新余额", callback_data=f"wallet:refresh:{address}"),
            InlineKeyboardButton("⬅️ 返回", callback_data="wallet:back")
        ]
    ])
    
    await query.edit_message_text(loading_text, reply_markup=keyboard, parse_mode='Markdown')
    
    # 异步查询余额
    try:
        from tron_api import TronAPI
        import os
        api = TronAPI(
            api_url=os.getenv('TRON_API_URL', 'https://api.trongrid.io'),
            api_key=os.getenv('TRON_API_KEY')
        )
        
        balance = api.get_account_balance(address)
        
        if balance:
            text = f"""📍 钱包地址详情

地址: {short_addr}
`{address}`

💰 余额信息:
TRX: {balance.trx_balance:.6f}
ENERGY: {balance.energy_available:,}
BANDWIDTH: {balance.bandwidth_available:,}

🕒 最后更新: 刚刚"""
        else:
            text = f"""📍 钱包地址详情

地址: {short_addr}
`{address}`

❌ 地址可能未激活或网络异常
💡 新地址需要先接收至少0.1 TRX才会被激活

🕒 最后更新: 刚刚"""
            
    except Exception as e:
        text = f"""📍 钱包地址详情

地址: {short_addr}
`{address}`

❌ 查询余额时发生错误
请稍后重试

🕒 最后更新: 刚刚"""
    
    await query.edit_message_text(text, reply_markup=keyboard, parse_mode='Markdown')

async def handle_text_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """处理文本消息（用于用户输入）"""
    user_id = update.effective_user.id
    text = update.message.text.strip()
    session = get_user_session(user_id)
    
    if session.pending_input == "custom_energy":
        # 处理自定义能量输入
        try:
            energy_value = int(text)
            if energy_value < 1000 or energy_value > 10000000:
                await update.message.reply_text("❌ 请输入有效的能量值（1,000 - 10,000,000）")
                return
            
            # 更新会话状态
            session.selected_energy = str(energy_value)
            session.pending_input = None
            
            # 发送确认消息并更新原来的卡片
            await update.message.reply_text(f"✅ 已设置能量为 {format_energy(str(energy_value))}")
            
            # 这里需要更新原来的闪租卡片，但需要消息ID
            # 简单起见，我们发送新的卡片
            text_content = generate_buy_energy_text(user_id)
            keyboard = generate_buy_energy_keyboard(user_id)
            await update.message.reply_text(text_content, reply_markup=keyboard, parse_mode='Markdown')
            
        except ValueError:
            await update.message.reply_text("❌ 请输入有效的整数")
            
    elif session.pending_input == "new_address":
        # 处理新地址输入
        from models import add_wallet_address, is_valid_tron_address
        
        if is_valid_tron_address(text):
            # 地址格式有效，尝试添加
            if add_wallet_address(user_id, text):
                # 添加成功，自动选择这个地址
                session.selected_address = text
                session.pending_input = None
                
                await update.message.reply_text(f"✅ 地址添加成功：`{text[:6]}...{text[-6:]}`\n\n🎯 已自动选择此地址用于接收能量。", parse_mode='Markdown')
                
                # 发送新的闪租卡片
                text_content = generate_buy_energy_text(user_id)
                keyboard = generate_buy_energy_keyboard(user_id)
                await update.message.reply_text(text_content, reply_markup=keyboard, parse_mode='Markdown')
            else:
                # 地址已存在
                await update.message.reply_text(f"ℹ️ 地址已存在：`{text[:6]}...{text[-6:]}`\n\n请输入其他地址或点击取消。", parse_mode='Markdown')
        else:
            await update.message.reply_text("❌ 地址格式无效！\n\n请输入有效的TRON地址（以T开头，34个字符）")
    
    elif session.pending_input == "wallet_new_address":
        # 处理钱包管理中的新地址输入
        from models import add_wallet_address, is_valid_tron_address
        
        if is_valid_tron_address(text):
            # 地址格式有效，尝试添加
            if add_wallet_address(user_id, text):
                # 添加成功
                session.pending_input = None
                
                await update.message.reply_text(f"✅ 地址添加成功：`{text[:6]}...{text[-6:]}`", parse_mode='Markdown')
                
                # 发送新的钱包管理页面
                from models import get_wallet_addresses
                user_addresses = get_wallet_addresses(user_id)
                
                text_content = f"""🏦 钱包管理

📊 共有 {len(user_addresses)} 个钱包地址

地址列表："""
                
                keyboard = []
                for i, addr in enumerate(user_addresses):
                    short_addr = f"{addr[:8]}...{addr[-6:]}"
                    keyboard.append([
                        InlineKeyboardButton(f"📍 {short_addr}", callback_data=f"wallet:view:{i}"),
                        InlineKeyboardButton("❌", callback_data=f"wallet:delete:{i}")
                    ])
                
                keyboard.extend([
                    [InlineKeyboardButton("➕ 添加新地址", callback_data="wallet:add")],
                    [InlineKeyboardButton("🏠 返回主菜单", callback_data="main:home")]
                ])
                
                await update.message.reply_text(text_content, reply_markup=InlineKeyboardMarkup(keyboard), parse_mode='Markdown')
            else:
                # 地址已存在
                await update.message.reply_text(f"ℹ️ 地址已存在：`{text[:6]}...{text[-6:]}`\n\n请输入其他地址或点击取消。", parse_mode='Markdown')
        else:
            await update.message.reply_text("❌ 地址格式无效！\n\n请输入有效的TRON地址（以T开头，34个字符）")
    
    
    elif session.pending_input == "balance_query":
        # 处理余额查询地址输入
        await handle_balance_query(update, context, text)

async def handle_balance_query(update: Update, context: ContextTypes.DEFAULT_TYPE, address: str):
    """处理余额查询"""
    user_id = update.effective_user.id
    session = get_user_session(user_id)
    
    # 验证地址格式
    api = TronAPI(
        api_url=os.getenv('TRON_API_URL', 'https://api.trongrid.io'),
        api_key=os.getenv('TRON_API_KEY')
    )
    
    if not api.is_valid_address(address):
        await update.message.reply_text("❌ 地址格式无效，请输入正确的TRON地址")
        return
    
    # 显示查询中的消息
    query_msg = await update.message.reply_text("🔍 正在查询地址余额，请稍候...")
    
    try:
        # 查询余额
        balance = api.get_account_balance(address)
        
        if balance:
            # 查询成功，显示结果
            message = api.format_balance_message(balance)
            keyboard = InlineKeyboardMarkup([[
                InlineKeyboardButton("🔄 重新查询", callback_data="main:balance"),
                InlineKeyboardButton("🏠 返回主菜单", callback_data="main:home")
            ]])
            
            await query_msg.edit_text(message, reply_markup=keyboard, parse_mode='Markdown')
            
            # 清理用户输入状态
            session.pending_input = None
            
        else:
            # 查询失败
            error_msg = f"""❌ 查询失败

可能的原因：
• 地址不存在或未激活
• 网络连接问题
• API服务暂时不可用

请检查地址是否正确：`{address}`"""
            
            keyboard = InlineKeyboardMarkup([[
                InlineKeyboardButton("🔄 重试", callback_data="main:balance"),
                InlineKeyboardButton("🏠 返回主菜单", callback_data="main:home")
            ]])
            
            await query_msg.edit_text(error_msg, reply_markup=keyboard, parse_mode='Markdown')
            session.pending_input = None
            
    except Exception as e:
        logger.error(f"余额查询异常: {e}")
        await query_msg.edit_text(
            "❌ 查询过程中发生错误，请稍后重试",
            reply_markup=InlineKeyboardMarkup([[
                InlineKeyboardButton("🔄 重试", callback_data="main:balance"),
                InlineKeyboardButton("🏠 返回主菜单", callback_data="main:home")
            ]])
        )
        session.pending_input = None

async def start_command_from_callback(query, context: ContextTypes.DEFAULT_TYPE):
    """从回调中调用start命令（用于返回主菜单）"""
    text = """🔋 TRON 能量助手

快速租能量、计次套餐、余额充值与代付，一站式完成

请选择一个操作开始："""

    keyboard = [
        [
            InlineKeyboardButton("⚡ Buy Energy（闪租）", callback_data="main:buy_energy"),
            InlineKeyboardButton("📦 Packages（笔数套餐）", callback_data="main:packages"),
        ],
        [
            InlineKeyboardButton("🧮 Calculator（能量计算器）", callback_data="main:calculator"),
            InlineKeyboardButton("💰 Top Up（余额充值）", callback_data="main:top_up"),
        ],
        [
            InlineKeyboardButton("🤝 Paymaster（能量代付）", callback_data="main:paymaster"),
            InlineKeyboardButton("📊 Market Price（行情）", callback_data="main:market_price"),
        ],
        [
            InlineKeyboardButton("🏦 钱包管理", callback_data="main:wallet_management"),
        ]
    ]
    
    reply_markup = InlineKeyboardMarkup(keyboard)
    await query.edit_message_text(text, reply_markup=reply_markup, parse_mode='Markdown')

async def start_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """处理/start命令"""
    logger.info(f"收到/start命令，用户ID: {update.effective_user.id}")
    print(f"DEBUG: 收到/start命令，用户ID: {update.effective_user.id}")
    
    # 清理用户的pending input状态
    user_id = update.effective_user.id
    session = get_user_session(user_id)
    session.pending_input = None
    
    text = """🔋 TRON 能量助手

快速租能量、计次套餐、余额充值与代付，一站式完成

请选择一个操作开始："""

    keyboard = [
        [
            InlineKeyboardButton("⚡ Buy Energy（闪租）", callback_data="main:buy_energy"),
            InlineKeyboardButton("📦 Packages（笔数套餐）", callback_data="main:packages"),
        ],
        [
            InlineKeyboardButton("🧮 Calculator（能量计算器）", callback_data="main:calculator"),
            InlineKeyboardButton("💰 Top Up（余额充值）", callback_data="main:top_up"),
        ],
        [
            InlineKeyboardButton("🤝 Paymaster（能量代付）", callback_data="main:paymaster"),
            InlineKeyboardButton("📊 Market Price（行情）", callback_data="main:market_price"),
        ],
        [
            InlineKeyboardButton("🏦 钱包管理", callback_data="main:wallet_management"),
        ]
    ]
    
    reply_markup = InlineKeyboardMarkup(keyboard)
    
    try:
        await update.message.reply_text(text, reply_markup=reply_markup, parse_mode='Markdown')
        logger.info(f"成功发送回复给用户 {user_id}")
    except Exception as e:
        logger.error(f"发送消息失败: {e}")
        print(f"发送消息错误: {e}")

async def setup_bot_commands(application):
    """设置机器人菜单命令"""
    commands = [
        BotCommand("start", "启动机器人并显示主菜单")
    ]
    await application.bot.set_my_commands(commands)

def main():
    """主函数"""
    # 首先尝试从环境变量获取Bot Token
    bot_token = os.getenv('TELEGRAM_BOT_TOKEN')
    
    # 如果环境变量没有，尝试从config.py获取
    if not bot_token:
        try:
            from config import BOT_TOKEN
            bot_token = BOT_TOKEN
            print("使用config.py中的Bot Token")
        except ImportError:
            pass
    
    if not bot_token:
        raise ValueError("请在.env文件中设置TELEGRAM_BOT_TOKEN环境变量，或在config.py中设置BOT_TOKEN")
    
    # 使用获取到的Bot Token
    application = Application.builder().token(bot_token).build()
    
    # 添加处理器
    application.add_handler(CommandHandler("start", start_command))
    application.add_handler(CallbackQueryHandler(handle_callback_query))
    application.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_text_message))
    
    # 设置机器人菜单命令
    async def post_init(application):
        await setup_bot_commands(application)
    
    application.post_init = post_init
    
    # 启动Bot
    print("Bot正在启动...")
    try:
        application.run_polling(drop_pending_updates=True, close_loop=False)
    except KeyboardInterrupt:
        print("Bot已停止")
    except Exception as e:
        print(f"启动错误: {e}")
        print("请确保没有其他Bot实例在运行")

if __name__ == "__main__":
    main()