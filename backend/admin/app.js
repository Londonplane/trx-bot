// TRON能量助手管理后台 JavaScript

const API_BASE_URL = 'http://localhost:8002/api';

// 页面导航
function showPage(pageId, title) {
    // 隐藏所有页面
    document.querySelectorAll('.page-content').forEach(page => {
        page.style.display = 'none';
    });
    
    // 显示指定页面
    document.getElementById(pageId).style.display = 'block';
    document.getElementById('page-title').textContent = title;
    
    // 更新导航状态
    document.querySelectorAll('.nav-link').forEach(link => {
        link.classList.remove('active');
    });
    event.target.classList.add('active');
}

function showDashboard() {
    showPage('dashboard-page', '数据概览');
    loadDashboardData();
}

function showOrders() {
    showPage('orders-page', '订单管理');
    loadOrdersData();
}

function showWallets() {
    showPage('wallets-page', '钱包池');
    loadWalletsData();
}

function showUsers() {
    showPage('users-page', '用户管理');
}

// API调用函数
async function apiCall(endpoint, options = {}) {
    try {
        const response = await fetch(`${API_BASE_URL}${endpoint}`, {
            headers: {
                'Content-Type': 'application/json',
                ...options.headers
            },
            ...options
        });
        
        if (!response.ok) {
            throw new Error(`HTTP error! status: ${response.status}`);
        }
        
        return await response.json();
    } catch (error) {
        console.error('API call failed:', error);
        return null;
    }
}

// 仪表板数据加载
async function loadDashboardData() {
    try {
        // 加载钱包数据
        const wallets = await apiCall('/supplier-wallets/');
        if (wallets) {
            updateWalletMetrics(wallets);
            updateWalletList(wallets);
        }

        // 模拟加载其他数据（实际应该调用相应API）
        updateOrderMetrics();
        initOrdersChart();
    } catch (error) {
        console.error('Error loading dashboard data:', error);
    }
}

function updateWalletMetrics(wallets) {
    const activeWallets = wallets.filter(w => w.is_active).length;
    document.getElementById('active-wallets').textContent = activeWallets;
}

function updateWalletList(wallets) {
    const walletList = document.getElementById('wallet-list');
    
    if (wallets.length === 0) {
        walletList.innerHTML = '<p class="text-muted mb-0">暂无钱包</p>';
        return;
    }
    
    const listHTML = wallets.map(wallet => `
        <div class="d-flex justify-content-between align-items-center mb-2 p-2 border-bottom">
            <div>
                <small class="text-muted">${wallet.wallet_address.substring(0, 8)}...${wallet.wallet_address.slice(-6)}</small>
                <br>
                <span class="badge ${wallet.is_active ? 'bg-success' : 'bg-secondary'} status-badge">
                    ${wallet.is_active ? '活跃' : '禁用'}
                </span>
            </div>
            <div class="text-end">
                <div><strong>${parseFloat(wallet.trx_balance).toFixed(2)} TRX</strong></div>
                <small class="text-muted">${wallet.energy_available.toLocaleString()} Energy</small>
            </div>
        </div>
    `).join('');
    
    walletList.innerHTML = listHTML;
}

function updateOrderMetrics() {
    // 模拟数据，实际应该调用API获取
    document.getElementById('today-orders').textContent = '12';
    document.getElementById('success-rate').textContent = '95.8%';
    document.getElementById('total-users').textContent = '248';
}

// 订单图表
let ordersChart;

function initOrdersChart() {
    const ctx = document.getElementById('ordersChart').getContext('2d');
    
    // 模拟数据，实际应该从API获取
    const data = {
        labels: ['今天', '昨天', '前天', '3天前', '4天前', '5天前', '6天前'],
        datasets: [{
            label: '成功订单',
            data: [12, 15, 8, 22, 18, 25, 20],
            borderColor: '#28a745',
            backgroundColor: 'rgba(40, 167, 69, 0.1)',
            tension: 0.4
        }, {
            label: '失败订单',
            data: [1, 0, 2, 1, 0, 1, 0],
            borderColor: '#dc3545',
            backgroundColor: 'rgba(220, 53, 69, 0.1)',
            tension: 0.4
        }]
    };
    
    ordersChart = new Chart(ctx, {
        type: 'line',
        data: data,
        options: {
            responsive: true,
            maintainAspectRatio: false,
            plugins: {
                legend: {
                    position: 'bottom',
                }
            },
            scales: {
                y: {
                    beginAtZero: true
                }
            }
        }
    });
}

// 订单管理
async function loadOrdersData() {
    const ordersTable = document.getElementById('orders-table');
    
    try {
        // 调用真实的API获取订单数据
        const orders = await apiCall('/orders/?limit=50');
        
        if (!orders || orders.length === 0) {
            ordersTable.innerHTML = '<tr><td colspan="7" class="text-center text-muted">暂无订单数据</td></tr>';
            return;
        }
        
        const tableHTML = orders.map(order => `
            <tr>
                <td>
                    <code>${order.id.substring(0, 8)}...</code>
                </td>
                <td>${order.user_id}</td>
                <td>${order.energy_amount.toLocaleString()}</td>
                <td>${parseFloat(order.cost_trx).toFixed(6)}</td>
                <td>
                    <span class="badge ${getStatusBadgeClass(order.status)}">
                        ${getStatusText(order.status)}
                    </span>
                </td>
                <td>${formatDateTime(order.created_at)}</td>
                <td>
                    <button class="btn btn-sm btn-outline-primary" onclick="viewOrder('${order.id}')">
                        <i class="bi bi-eye"></i>
                    </button>
                    ${order.status === 'pending' || order.status === 'processing' ? 
                        `<button class="btn btn-sm btn-outline-danger ms-1" onclick="cancelOrder('${order.id}')">
                            <i class="bi bi-x-circle"></i>
                        </button>` : ''}
                </td>
            </tr>
        `).join('');
        
        ordersTable.innerHTML = tableHTML;
    } catch (error) {
        console.error('Error loading orders:', error);
        ordersTable.innerHTML = '<tr><td colspan="7" class="text-center text-danger">加载失败</td></tr>';
    }
}

function getStatusBadgeClass(status) {
    const statusClasses = {
        'pending': 'bg-warning',
        'processing': 'bg-info',
        'completed': 'bg-success',
        'failed': 'bg-danger',
        'cancelled': 'bg-secondary'
    };
    return statusClasses[status] || 'bg-secondary';
}

function getStatusText(status) {
    const statusTexts = {
        'pending': '待处理',
        'processing': '处理中',
        'completed': '已完成',
        'failed': '失败',
        'cancelled': '已取消'
    };
    return statusTexts[status] || status;
}

function formatDateTime(isoString) {
    return new Date(isoString).toLocaleString('zh-CN');
}

function viewOrder(orderId) {
    // 创建模态框显示订单详情
    const modalHTML = `
        <div class="modal fade" id="orderModal" tabindex="-1">
            <div class="modal-dialog">
                <div class="modal-content">
                    <div class="modal-header">
                        <h5 class="modal-title">订单详情</h5>
                        <button type="button" class="btn-close" data-bs-dismiss="modal"></button>
                    </div>
                    <div class="modal-body" id="orderModalBody">
                        <div class="text-center">加载中...</div>
                    </div>
                </div>
            </div>
        </div>
    `;
    
    // 移除已存在的模态框
    const existingModal = document.getElementById('orderModal');
    if (existingModal) {
        existingModal.remove();
    }
    
    // 添加新模态框
    document.body.insertAdjacentHTML('beforeend', modalHTML);
    
    // 显示模态框
    const modal = new bootstrap.Modal(document.getElementById('orderModal'));
    modal.show();
    
    // 加载订单详情
    loadOrderDetail(orderId);
}

async function loadOrderDetail(orderId) {
    const modalBody = document.getElementById('orderModalBody');
    
    try {
        const order = await apiCall(`/orders/${orderId}`);
        
        if (order) {
            modalBody.innerHTML = `
                <div class="row">
                    <div class="col-sm-4"><strong>订单ID:</strong></div>
                    <div class="col-sm-8"><code>${order.id}</code></div>
                </div>
                <div class="row mt-2">
                    <div class="col-sm-4"><strong>用户ID:</strong></div>
                    <div class="col-sm-8">${order.user_id}</div>
                </div>
                <div class="row mt-2">
                    <div class="col-sm-4"><strong>接收地址:</strong></div>
                    <div class="col-sm-8"><code>${order.receive_address}</code></div>
                </div>
                <div class="row mt-2">
                    <div class="col-sm-4"><strong>Energy数量:</strong></div>
                    <div class="col-sm-8">${order.energy_amount.toLocaleString()}</div>
                </div>
                <div class="row mt-2">
                    <div class="col-sm-4"><strong>时长:</strong></div>
                    <div class="col-sm-8">${order.duration_hours} 小时</div>
                </div>
                <div class="row mt-2">
                    <div class="col-sm-4"><strong>费用:</strong></div>
                    <div class="col-sm-8">${parseFloat(order.cost_trx).toFixed(6)} TRX</div>
                </div>
                <div class="row mt-2">
                    <div class="col-sm-4"><strong>状态:</strong></div>
                    <div class="col-sm-8">
                        <span class="badge ${getStatusBadgeClass(order.status)}">
                            ${getStatusText(order.status)}
                        </span>
                    </div>
                </div>
                <div class="row mt-2">
                    <div class="col-sm-4"><strong>创建时间:</strong></div>
                    <div class="col-sm-8">${formatDateTime(order.created_at)}</div>
                </div>
                ${order.tx_hash ? `
                <div class="row mt-2">
                    <div class="col-sm-4"><strong>交易哈希:</strong></div>
                    <div class="col-sm-8"><code>${order.tx_hash}</code></div>
                </div>
                ` : ''}
                ${order.error_message ? `
                <div class="row mt-2">
                    <div class="col-sm-4"><strong>错误信息:</strong></div>
                    <div class="col-sm-8 text-danger">${order.error_message}</div>
                </div>
                ` : ''}
            `;
        } else {
            modalBody.innerHTML = '<div class="text-center text-danger">订单不存在</div>';
        }
    } catch (error) {
        modalBody.innerHTML = '<div class="text-center text-danger">加载失败</div>';
    }
}

async function cancelOrder(orderId) {
    if (!confirm('确定要取消这个订单吗？')) {
        return;
    }
    
    try {
        const result = await apiCall(`/orders/${orderId}/cancel`, {
            method: 'POST'
        });
        
        if (result && result.success) {
            showToast('订单已取消');
            loadOrdersData(); // 重新加载订单列表
        } else {
            showToast('取消订单失败', 'error');
        }
    } catch (error) {
        console.error('Cancel order failed:', error);
        showToast('取消订单失败', 'error');
    }
}

function searchOrders() {
    const searchTerm = document.getElementById('order-search').value;
    if (searchTerm.trim()) {
        alert(`搜索订单: ${searchTerm}\n\n此功能开发中...`);
    }
}

// 钱包池管理
async function loadWalletsData() {
    const walletsTable = document.getElementById('wallets-table');
    
    try {
        const wallets = await apiCall('/supplier-wallets/');
        
        if (!wallets || wallets.length === 0) {
            walletsTable.innerHTML = '<tr><td colspan="6" class="text-center text-muted">暂无钱包数据</td></tr>';
            return;
        }
        
        const tableHTML = wallets.map(wallet => `
            <tr>
                <td>
                    <code>${wallet.wallet_address}</code>
                </td>
                <td>
                    <strong>${parseFloat(wallet.trx_balance).toFixed(6)} TRX</strong>
                </td>
                <td>
                    ${wallet.energy_available.toLocaleString()} / ${wallet.energy_limit.toLocaleString()}
                </td>
                <td>
                    <span class="badge ${wallet.is_active ? 'bg-success' : 'bg-secondary'}">
                        ${wallet.is_active ? '活跃' : '禁用'}
                    </span>
                </td>
                <td>
                    ${wallet.last_balance_check ? formatDateTime(wallet.last_balance_check) : '未检查'}
                </td>
                <td>
                    <button class="btn btn-sm ${wallet.is_active ? 'btn-outline-warning' : 'btn-outline-success'}" 
                            onclick="toggleWallet(${wallet.id})">
                        ${wallet.is_active ? '禁用' : '启用'}
                    </button>
                </td>
            </tr>
        `).join('');
        
        walletsTable.innerHTML = tableHTML;
    } catch (error) {
        walletsTable.innerHTML = '<tr><td colspan="6" class="text-center text-danger">加载失败</td></tr>';
    }
}

async function toggleWallet(walletId) {
    try {
        const result = await apiCall(`/supplier-wallets/${walletId}/toggle`, {
            method: 'PUT'
        });
        
        if (result) {
            // 重新加载钱包数据
            loadWalletsData();
            showToast('钱包状态更新成功');
        } else {
            showToast('操作失败', 'error');
        }
    } catch (error) {
        console.error('Toggle wallet failed:', error);
        showToast('操作失败', 'error');
    }
}

// 通用函数
function refreshData() {
    const currentPage = document.querySelector('.page-content[style="display: block;"]').id;
    
    switch (currentPage) {
        case 'dashboard-page':
            loadDashboardData();
            break;
        case 'orders-page':
            loadOrdersData();
            break;
        case 'wallets-page':
            loadWalletsData();
            break;
    }
    
    showToast('数据已刷新');
}

function showToast(message, type = 'success') {
    // 简单的提示实现
    const alertClass = type === 'error' ? 'alert-danger' : 'alert-success';
    const alertHTML = `
        <div class="alert ${alertClass} alert-dismissible fade show position-fixed" 
             style="top: 20px; right: 20px; z-index: 9999;" role="alert">
            ${message}
            <button type="button" class="btn-close" data-bs-dismiss="alert"></button>
        </div>
    `;
    
    document.body.insertAdjacentHTML('beforeend', alertHTML);
    
    // 3秒后自动消失
    setTimeout(() => {
        const alert = document.querySelector('.alert:last-of-type');
        if (alert) {
            alert.remove();
        }
    }, 3000);
}

// 页面加载完成后初始化
document.addEventListener('DOMContentLoaded', function() {
    loadDashboardData();
});