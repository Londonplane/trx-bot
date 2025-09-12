# 业务流程测试指南

## 📋 概述

本指南详细说明TRON能量助手Bot的完整业务流程测试方法，基于真实的三方交易模型：**顾客 → 平台 → 供应商**。

## 🏗️ 业务模型

### 三方角色定义

1. **👤 顾客（Customer）**
   - 钱包地址: `TCX13dZVJt1uCDCGA3F26KqEndpsSt2CHy`
   - 角色: 支付TRX购买能量租赁服务
   - 预期余额: 1000 TRX

2. **🏢 平台（Platform）**  
   - 钱包地址: `TAcrAuU78UyPZpZuVPCQo2ZVcfwmkskWLz`
   - 角色: 接收顾客支付，处理订单管理
   - 预期余额: 7000 TRX

3. **⚡ 供应商（Supplier）**
   - 钱包地址: `TVAcKMkSvL8Jbf58AKLnWFesYjiznNUnr4`
   - 角色: 向顾客提供实际的能量服务
   - 预期余额: 2000 TRX

### 交易流程

```
顾客A --[支付TRX]--> 平台B --[创建订单]--> 供应商C
   ↑                      ↓                    ↓
   └--[接收Energy]<-------[处理订单]<--[转移Energy]
```

## 🧪 测试流程

### 阶段1: 环境准备测试

```bash
# 运行完整的业务流程测试
python business_flow_test.py

# 或者运行新的测试架构
cd tests
python -m pytest features/ -v
```

#### 验证项目
- [ ] 后端服务健康检查 (localhost:8002/health)
- [ ] Telegram Bot服务连接
- [ ] TRON Shasta网络连接
- [ ] 三个测试钱包余额验证

### 阶段2: 顾客端流程测试

#### 2.1 参数选择测试
- [ ] 能量数量选择: 135K Energy
- [ ] 租用时长选择: 1天
- [ ] 参数组合验证
- [ ] UI状态更新

#### 2.2 地址管理测试
- [ ] 添加顾客钱包地址
- [ ] 地址格式验证
- [ ] 地址选择确认

#### 2.3 余额查询测试
- [ ] 查询顾客钱包余额
- [ ] 验证TRX余额充足性 (≥ 订单费用)
- [ ] 显示Energy和Bandwidth信息

#### 2.4 订单成本计算测试
- [ ] 基于参数计算订单费用
- [ ] 验证Mock计算结果 (~4.86 TRX)
- [ ] 成本显示格式验证

### 阶段3: 三方交易流程测试

#### 3.1 订单创建流程
```
测试场景: 顾客A购买135K Energy，租期1天

步骤1: 顾客确认订单参数
- 能量: 135,000 Energy
- 时长: 1天
- 接收地址: TCX13dZVJt1uCDCGA3F26KqEndpsSt2CHy
- 费用: ~4.86 TRX

步骤2: 生成支付信息
- 支付地址: TAcrAuU78UyPZpZuVPCQo2ZVcfwmkskWLz (平台钱包)
- 支付金额: 4.86 TRX
- 订单ID: 生成唯一订单标识
```

#### 3.2 交易执行流程 (当前限制)

**⚠️ 注意**: 以下功能当前未实现，仅为流程设计

```
步骤3: TRX转账执行 (未实现)
- 顾客A → 平台B: 转账4.86 TRX
- 交易哈希记录
- 区块链确认等待

步骤4: 平台处理 (未实现)  
- 平台B确认收款
- 创建供应商订单
- 更新订单状态为"已支付"

步骤5: 能量转移 (未实现)
- 供应商C执行Energy Delegation
- 135K Energy → 顾客A地址
- 能量转移确认

步骤6: 订单完成 (未实现)
- 系统确认交易完成
- 更新订单状态为"已完成"
- 发送完成通知
```

### 阶段4: 数据一致性验证

#### 4.1 交易前后余额对比
```
交易前余额:
- 顾客A: 1000 TRX, 0 Energy
- 平台B: 7000 TRX
- 供应商C: 2000 TRX, 135K+ Energy

预期交易后余额:
- 顾客A: 995.14 TRX, 135K Energy
- 平台B: 7004.86 TRX  
- 供应商C: 2000 TRX, 原Energy - 135K
```

#### 4.2 订单状态跟踪
- [ ] 订单创建状态
- [ ] 支付待确认状态
- [ ] 执行中状态
- [ ] 已完成状态

## 📊 测试用例

### 正常流程用例

#### 用例1: 标准135K能量1天订单
```json
{
  "name": "标准能量租赁订单",
  "customer": "TCX13dZVJt1uCDCGA3F26KqEndpsSt2CHy",
  "energy_amount": 135000,
  "duration": "1d",
  "expected_cost": 4.86,
  "payment_address": "TAcrAuU78UyPZpZuVPCQo2ZVcfwmkskWLz",
  "supplier": "TVAcKMkSvL8Jbf58AKLnWFesYjiznNUnr4"
}
```

#### 用例2: 大额1M能量7天订单
```json
{
  "name": "大额长期租赁订单",
  "customer": "TCX13dZVJt1uCDCGA3F26KqEndpsSt2CHy", 
  "energy_amount": 1000000,
  "duration": "7d",
  "expected_cost": 27.0,
  "payment_address": "TAcrAuU78UyPZpZuVPCQo2ZVcfwmkskWLz",
  "supplier": "TVAcKMkSvL8Jbf58AKLnWFesYjiznNUnr4"
}
```

### 异常情况用例

#### 用例3: 余额不足场景
```json
{
  "name": "顾客余额不足",
  "issue": "顾客余额 < 订单费用",
  "expected_behavior": "显示余额不足错误，阻止订单创建",
  "test_method": "修改测试钱包余额或创建大额订单"
}
```

#### 用例4: 网络异常场景
```json
{
  "name": "区块链网络异常",
  "issue": "TRON网络连接失败",
  "expected_behavior": "显示网络错误，提供重试选项",
  "test_method": "模拟网络断开或使用无效API端点"
}
```

## 🔧 测试工具

### 自动化测试脚本
```bash
# 运行完整业务流程测试
python tests/business_flow_test.py

# 运行特定功能测试
python tests/features/flash_rental/test_flash_rental_ui.py
python tests/features/flash_rental/test_balance_query.py
python tests/features/flash_rental/test_energy_calculation.py
```

### 手动测试清单

#### 基础功能验证
- [ ] 闪租页面可正常访问
- [ ] 参数选择功能正常
- [ ] 地址管理功能正常
- [ ] 余额查询功能正常
- [ ] 成本计算显示正常

#### 集成功能验证  
- [ ] 后端API连接正常
- [ ] 数据库读写正常
- [ ] TRON网络查询正常
- [ ] 用户会话管理正常

## 📈 预期结果

### 成功率指标
- **基础功能**: 100% 通过
- **集成功能**: 90%+ 通过  
- **业务流程**: 70%+ 通过 (部分功能未实现)

### 功能完整性
- ✅ **已实现**: 界面交互、参数选择、余额查询、成本计算
- ⚠️ **部分实现**: 订单创建、状态管理
- ❌ **未实现**: 链上交易、能量转移、支付确认

### 发现问题类型
1. **Mock数据限制**: 成本计算使用假数据
2. **交易功能缺失**: 无法执行真实TRX转账
3. **能量转移未实现**: 缺少Energy Delegation机制
4. **订单管理不完整**: 状态跟踪系统待完善

## 🚀 下一步计划

### 短期优化 (1-2周)
1. 完善成本计算算法，替换Mock数据
2. 实现订单持久化存储
3. 添加订单状态查询接口
4. 优化错误处理和用户提示

### 中期开发 (1个月)
1. 实现TRX转账功能
2. 集成Energy Delegation机制
3. 完善三方交易流程
4. 添加交易确认和通知

### 长期规划 (3个月)
1. 实现真实定价算法
2. 添加市场汇率集成
3. 完善订单管理系统
4. 支持批量订单处理

---

*最后更新: 2025-09-12*  
*测试版本: v2.2.1*