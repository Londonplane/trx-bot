# 闪租页（Buy Energy）交互与开发规格文档

本页定义“/start → Buy Energy”后的主交互卡片及其子流程，作为开发对齐用的单页规格。目标是保证“单消息可编辑、参数即时更新、上下文保持”的交互体验。

## 1. 主卡片结构（Inline 交互消息）

- 顶部信息文本框（动态文案，随用户操作更新）
  - 使用说明（如何选择并下单）
  - 当前选择项：
    - Energy: <selected_energy>
    - Duration: <selected_duration>
    - Cost: <computed_cost>（由后台算法实时计算）
  - 账户信息：
    - User Balance: <TRX/USDT>（账号余额）
    - Address: <selected_address or “Not selected”>

- 按钮区（Inline Keyboard，建议4-5行分区）
  - Duration（多选一，高亮选中态，单行布局）
    - 1h | 1d | 3d | 7d | 14d（可配置，一行显示5个按钮）
  - Energy（多选一，高亮选中态，单行布局）
    - 65K | 135K | 270K | 540K | 1M（可配置，一行显示5个按钮）
  - 功能操作
    - ✏️ Other amount（自定义数值入口）
  - 地址与余额操作
    - ✅ Select address（未选地址时显示）
    - ✅ Change address（已选地址时显示）
    - Address balance（刷新选中地址链上余额/能量）
  - 提交与退出
    - Confirm / Pay（依据支付方式与余额可用状态启用/禁用）
    - ❌ Later（关闭/撤回当前卡片）

说明：
- 所有参数选择、余额刷新、地址选择均"编辑同一条消息"，不新增新卡片，保持上下文与整洁。
- 选中项需要明显高亮：时长选中使用"🔸"图标，能量选中使用"🔹"图标，并在顶部文本框即时反映。

## 2. 交互流程与状态更新

### 2.1 进入闪租页（由“Buy Energy”内联按钮触发）
- 发送主卡片（Inline），默认选中一个“Duration”与一个“Energy”（可配置默认，如 1d + 135K）。
- 顶部信息文本框展示默认 Cost（后台计算），以及用户余额、地址状态（未选时提示选择）。

### 2.2 切换时长（Duration 按钮）
- 用户点击任一 Duration：
  - 高亮选中该按钮（添加🔸图标），取消其他选中。
  - 后台计算 cost(selected_energy, selected_duration)。
  - 编辑原消息文本，更新 Duration、Cost 字段。
  - 保持按钮区不变，仅更新选中态与文本。

### 2.3 切换能量（Energy 预设按钮）
- 用户点击任一 Energy 预设：
  - 高亮选中该按钮（添加🔹图标），取消其他选中（如果之前是 Other amount 也取消）。
  - 后台计算 cost(selected_energy, selected_duration)。
  - 编辑原消息文本，更新 Energy、Cost 字段。

### 2.4 Other amount（自定义能量）
- 点击 Other amount 后：
  - 发送一条临时提示消息（单独消息）：  
    “Send the bot the required amount of energy (an integer, for example 65000):”  
    并附 Close 按钮。
- 用户在聊天中发送一个整数（例如 131000）：
  - 校验通过后，编辑原“Buy Energy”主卡片：设置 Energy=131000，保留当前 Duration。
  - 触发后台重新计算 Cost 并更新文本。
  - 自动删除临时提示消息（含 Close），仅保留更新后的主卡片。
- 输入校验失败（非整数或越界）：
  - 在临时提示消息下方再回一条错误提示（例如“Please send a valid integer within [min, max]”），不影响主卡片。
  - 允许用户再次输入；也可点击 Close 关闭临时提示。

### 2.5 Select address / Change address（地址管理）
- 在主卡片点击 Select address 或 Change address：
  - 移除/隐藏当前主卡片（删除消息或以“已切换到地址管理”替代）。
  - 打开“地址管理卡片”（见 3 节）。
- 在“地址管理卡片”点击某个地址：
  - 返回主卡片（通过编辑原主卡片的消息 ID，或以同一消息位重新渲染），更新 Address 字段为所选地址。
  - 主卡片按钮区同步恢复，包括“Change address”“Address balance”等。

### 2.6 Address balance（地址余额刷新）
- 点击 Address balance：
  - 立即发送一条临时状态提示：“🔄 Updating balance…”
  - 后台异步查询当前已选地址的链上数据（TRX 余额、ENERGY 可用/已租等）
  - 查询成功：
    - 编辑主卡片文本，增加/更新：
      - TRX: <最新余额>
      - ENERGY: <最新能量值>
    - 根据余额/成本联动更新 Confirm/Pay 按钮启用状态（不足则禁用或提示充值）。
    - 删除“Updating balance…”临时提示。
  - 查询失败：
    - 删除“Updating balance…”临时提示。
    - 在主卡片下方或以弹窗提示错误信息（例如“Failed to fetch balance, please try again later.”）。

### 2.7 Confirm / Pay（下单与支付）
- 点击 Confirm / Pay：
  - 后台校验（余额、地址、风控、库存/可用量上限）。
  - 通过后，生成订单并扣费/创建支付指引：
    - 若余额支付：扣费成功后返回“下单成功”状态，并提供“查看订单/续租/返回主菜单”。
    - 若需链上转账：展示支付地址与金额，进入待支付状态，监听上链结果后更新卡片。
  - 失败则以明确错误码与提示返回（余额不足/地址未选/参数不合法等）。

### 2.8 Later（稍后处理）
- 点击 Later：
  - 撤回/删除当前主卡片消息。
  - 可在聊天里回一条简短提示：“You can return anytime via Main Menu → Buy Energy.”

## 3. 地址管理卡片（Select address）

- 文本区（动态列出已绑定地址、当前默认/主地址标识）
  - 标题：Select an address for energy accrual
  - 已绑定列表（每个地址为一个按钮）
  - 操作提示：New address / Remove / Set default（可按阶段逐步上线）

- 按钮区
  - 地址列表按钮（点击即选择并回到主卡片）
  - New address
  - Back（返回主卡片，不改变当前选择）

### 3.1 New address 流程
- 点击 New address：
  - 发送一条临时提示消息：“Send the bot a new address for energy accrual:”
  - 附带 Back 按钮（用于取消本次新增动作，返回地址管理卡片）
- 用户输入一个 TRX 地址：
  - 校验合法性（前缀、长度、校验和，或通过链上查询验证有效性）。
  - 通过后：
    - 更新地址管理卡片文本：显示新增地址
    - 地址列表增加一个新按钮
    - 删除临时提示消息（含 Back）
  - 校验失败：
    - 在临时提示消息下方给出错误提示，不更新卡片；允许重新发送或点击 Back 取消。

### 3.2 选择地址返回主卡片
- 用户点击地址按钮：
  - 回到主卡片（编辑原卡片），更新 Address 字段，并切换按钮为“Change address”“Address balance”可见。
  - 不新建消息，保持整洁。

## 4. 文案与占位符建议

- 主卡片文本模板（示例）：
  - Title: Buy TRON Energy
  - How to use:
    - Select Duration and Energy, then Confirm to proceed.
  - Current selection:
    - Energy: {energy_formatted}
    - Duration: {duration_label}
    - Cost: {cost_formatted}
  - Account:
    - User Balance: {balance_TRX}/{balance_USDT}
    - Address: {address_display or “Not selected”}
  - Tips:
    - Prices update in real time. Please refresh balance before payment if needed.

- 临时提示消息：
  - Other amount: “Send the bot the required amount of energy (an integer, for example 65000):”
  - Address new: “Send the bot a new address for energy accrual:”
  - 余额刷新： “🔄 Updating balance…”

- 错误与校验：
  - 整数输入错误： “Please send a valid integer within {min}-{max}.”
  - 地址非法： “Invalid TRX address. Please check and resend.”
  - 余额不足： “Insufficient balance. Please Top Up or reduce Energy/Duration.”

## 5. 回调数据与状态管理（建议）

- 回调数据结构（callback_data，简化示例，注意 Telegram 64字节限制）：
  - dur:{code}（如 dur:1h / dur:1d / dur:3d）
  - eng:{preset_code}（如 eng:65k / eng:135k / eng:custom）
  - eng_custom:init（进入自定义提示）
  - addr:select（进入地址管理）
  - addr:choose:{short_id}（选择某地址）
  - addr:new:init（进入新增地址提示）
  - addr:balance（刷新地址余额）
  - pay:confirm
  - page:back（返回主卡片）
  - later:close

- 服务端会话状态（per chat + per user）：
  - selected_duration
  - selected_energy
  - selected_address
  - computed_cost（来自定价服务）
  - user_balance（账户余额缓存）
  - address_balance_cache（选中地址的链上余额/能量快照，带时间戳）
  - pending_prompt_type（none | custom_energy | new_address）
  - last_message_ids（主卡片消息ID、提示消息ID等）

- 幂等与一致性：
  - 对 Confirm/Pay 设置幂等键（order_draft_id）。
  - 同时限制快速重复点击（如 2-3 秒冷却或禁用按钮后再启用）。

## 6. 定价与可用性接口（后台）

- 定价计算 API
  - 输入：energy, duration, address(optional), user_tier(optional)
  - 输出：cost（按 TRX/USDT 报价）、有效期、库存校验、折扣信息
- 余额查询 API
  - 用户余额（系统账本）
  - 链上地址余额（TRX/ENERGY），异步更新
- 订单创建 API
  - 输入：用户ID、address、energy、duration、cost_quote_id
  - 输出：order_id、支付状态、支付指引（如需链上转账）
- 风控校验
  - 地址黑名单、日限额、频控、异常行为标识

## 7. 按钮可用状态与视觉

- 高亮选中：时长选中时在文案追加"🔸"，能量选中时在文案追加"🔹"。
- 禁用条件：
  - 未选择地址时禁用 Confirm/Pay。
  - 余额不足或报价过期时禁用 Confirm/Pay，并提示刷新/充值。
- 反馈速度：
  - 参数变动→立即回显 Cost（若定价API稍慢，可显示"Calculating…"过渡态，完成后编辑文本）。

## 8. 开发要点与一致性

- 所有主要操作都“编辑原有主卡片消息”，避免多卡片堆叠。
- 临时提示消息用于收集用户输入，获取到数据后自动删除，保持界面整洁。
- 允许任意时刻通过“Main Menu”或“Later”退出，避免卡死在流程中。
- 对于可能的多端并发（移动/桌面）：以服务器会话状态为权威，拒绝过期回调。

***

如需，我可以继续提供：
- aiogram/pyTelegramBotAPI 回调 handler skeleton（含 state 与 callback_data 编解码）
- InlineKeyboard JSON 原型（含按钮ID、分组与顺序）
- 定价与余额接口的伪协议（protobuf/JSON schema）