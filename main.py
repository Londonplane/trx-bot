import logging
import asyncio
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import Application, CommandHandler, CallbackQueryHandler, ContextTypes, MessageHandler, filters
from config import BOT_TOKEN
from models import get_user_session, format_energy
from buy_energy import handle_buy_energy_callback, generate_buy_energy_text, generate_buy_energy_keyboard

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
        mock_addresses = [
            "TRX9Uhjn948ynC8J2LRRHVpbdYT6GKRTLz",
            "TBrLXQs4q2XQ29dGFbyiTCcvXuN2tGJvSK", 
            "TNRLJjF9uGp2gZMZVQWcJSkbKnH7wdvGRw"
        ]
        
        session = get_user_session(user_id)
        session.selected_address = mock_addresses[addr_index]
        
        # 返回闪租页
        text = generate_buy_energy_text(user_id)
        keyboard = generate_buy_energy_keyboard(user_id)
        await query.edit_message_text(text, reply_markup=keyboard)
        
    elif callback_data == "address:new":
        # 添加新地址
        session = get_user_session(user_id)
        session.pending_input = "new_address"
        
        prompt_text = "请发送新的TRON地址用于接收能量："
        prompt_keyboard = InlineKeyboardMarkup([[
            InlineKeyboardButton("取消", callback_data="address:cancel_new")
        ]])
        await context.bot.send_message(
            chat_id=user_id,
            text=prompt_text,
            reply_markup=prompt_keyboard
        )
        
    elif callback_data == "address:back":
        # 返回闪租页
        text = generate_buy_energy_text(user_id)
        keyboard = generate_buy_energy_keyboard(user_id)
        await query.edit_message_text(text, reply_markup=keyboard)
        
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
        
        await query.edit_message_text(success_text, reply_markup=keyboard)
        
    elif callback_data == "buy_energy:back":
        # 返回闪租页
        text = generate_buy_energy_text(user_id)
        keyboard = generate_buy_energy_keyboard(user_id)
        await query.edit_message_text(text, reply_markup=keyboard)

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
            await update.message.reply_text(text_content, reply_markup=keyboard)
            
        except ValueError:
            await update.message.reply_text("❌ 请输入有效的整数")
            
    elif session.pending_input == "new_address":
        # 处理新地址输入
        if len(text) == 34 and text.startswith('T'):
            # 简单的地址格式验证
            session.selected_address = text
            session.pending_input = None
            
            await update.message.reply_text(f"✅ 已添加地址：{text[:6]}...{text[-4:]}")
            
            # 发送新的闪租卡片
            text_content = generate_buy_energy_text(user_id)
            keyboard = generate_buy_energy_keyboard(user_id)
            await update.message.reply_text(text_content, reply_markup=keyboard)
        else:
            await update.message.reply_text("❌ 请输入有效的TRON地址（以T开头，34个字符）")

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
        ]
    ]
    
    reply_markup = InlineKeyboardMarkup(keyboard)
    
    try:
        await update.message.reply_text(text, reply_markup=reply_markup)
        logger.info(f"成功发送回复给用户 {user_id}")
    except Exception as e:
        logger.error(f"发送消息失败: {e}")
        print(f"发送消息错误: {e}")

def main():
    """主函数"""
    # 使用配置文件中的Bot Token
    application = Application.builder().token(BOT_TOKEN).build()
    
    # 添加处理器
    application.add_handler(CommandHandler("start", start_command))
    application.add_handler(CallbackQueryHandler(handle_callback_query))
    application.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_text_message))
    
    # 启动Bot
    print("Bot正在启动...")
    try:
        application.run_polling(drop_pending_updates=True)
    except KeyboardInterrupt:
        print("Bot已停止")

if __name__ == "__main__":
    main()