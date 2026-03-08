#!/usr/bin/env python3
"""
风控模块 - 仓位管理、止损、风险控制
"""

class RiskController:
    """风控控制器"""
    
    def __init__(self, config):
        """
        初始化风控控制器
        
        Args:
            config: 风控配置字典
        """
        self.max_position_pct = config.get('max_position_pct', 10.0)  # 单币种最大仓位比例
        self.max_total_position_pct = config.get('max_total_position_pct', 50.0)  # 总仓位比例
        self.stop_loss_pct = config.get('stop_loss_pct', 5.0)  # 止损比例
        self.daily_loss_limit_pct = config.get('daily_loss_limit_pct', 10.0)  # 日亏损上限
        self.max_trades_per_day = config.get('max_trades_per_day', 20)  # 每日最大交易次数
        
        self.daily_pnl = 0.0  # 当日盈亏
        self.daily_trades = 0  # 当日交易次数
        self.positions = {}  # 当前持仓 {symbol: {'entry_price': float, 'quantity': float}}
    
    def can_open_position(self, symbol, price, quantity, total_capital):
        """
        检查是否可以开仓
        
        Args:
            symbol: 交易对
            price: 当前价格
            quantity: 数量
            total_capital: 总资金
        
        Returns:
            tuple: (bool, str) - (是否允许, 原因)
        """
        # 检查日亏损限制
        if self.daily_pnl < 0 and abs(self.daily_pnl) / total_capital * 100 >= self.daily_loss_limit_pct:
            return False, f"触发日亏损闸门 ({self.daily_loss_limit_pct}%)"
        
        # 检查每日交易次数
        if self.daily_trades >= self.max_trades_per_day:
            return False, f"超过每日最大交易次数 ({self.max_trades_per_day})"
        
        # 检查单币种仓位
        position_value = price * quantity
        position_pct = position_value / total_capital * 100
        if position_pct > self.max_position_pct:
            return False, f"单币种仓位超限 ({position_pct:.2f}% > {self.max_position_pct}%)"
        
        # 检查总仓位
        current_total_value = sum(
            self.positions[s]['entry_price'] * self.positions[s]['quantity']
            for s in self.positions
        )
        new_total_value = current_total_value + position_value
        new_total_pct = new_total_value / total_capital * 100
        if new_total_pct > self.max_total_position_pct:
            return False, f"总仓位超限 ({new_total_pct:.2f}% > {self.max_total_position_pct}%)"
        
        return True, "通过风控检查"
    
    def check_stop_loss(self, symbol, current_price):
        """
        检查是否触发止损
        
        Args:
            symbol: 交易对
            current_price: 当前价格
        
        Returns:
            tuple: (bool, float) - (是否止损, 亏损比例)
        """
        if symbol not in self.positions:
            return False, 0.0
        
        entry_price = self.positions[symbol]['entry_price']
        loss_pct = (entry_price - current_price) / entry_price * 100
        
        if loss_pct >= self.stop_loss_pct:
            return True, loss_pct
        
        return False, loss_pct
    
    def open_position(self, symbol, price, quantity):
        """
        开仓
        
        Args:
            symbol: 交易对
            price: 开仓价格
            quantity: 数量
        """
        self.positions[symbol] = {
            'entry_price': price,
            'quantity': quantity
        }
        self.daily_trades += 1
    
    def close_position(self, symbol, exit_price):
        """
        平仓
        
        Args:
            symbol: 交易对
            exit_price: 平仓价格
        
        Returns:
            float: 盈亏金额
        """
        if symbol not in self.positions:
            return 0.0
        
        position = self.positions[symbol]
        entry_price = position['entry_price']
        quantity = position['quantity']
        
        pnl = (exit_price - entry_price) * quantity
        self.daily_pnl += pnl
        self.daily_trades += 1
        
        del self.positions[symbol]
        return pnl
    
    def reset_daily_stats(self):
        """重置每日统计（每天开盘前调用）"""
        self.daily_pnl = 0.0
        self.daily_trades = 0
    
    def get_position_summary(self):
        """
        获取持仓摘要
        
        Returns:
            dict: 持仓摘要
        """
        return {
            'positions': len(self.positions),
            'symbols': list(self.positions.keys()),
            'daily_pnl': self.daily_pnl,
            'daily_trades': self.daily_trades
        }
    
    def calculate_position_size(self, symbol, price, total_capital, risk_pct=2.0):
        """
        计算建议仓位大小（基于风险比例）
        
        Args:
            symbol: 交易对
            price: 当前价格
            total_capital: 总资金
            risk_pct: 单笔风险比例（默认2%）
        
        Returns:
            float: 建议数量
        """
        # 风险金额 = 总资金 × 风险比例
        risk_amount = total_capital * (risk_pct / 100)
        
        # 止损金额 = 价格 × 止损比例
        stop_loss_amount = price * (self.stop_loss_pct / 100)
        
        # 建议数量 = 风险金额 / 止损金额
        suggested_quantity = risk_amount / stop_loss_amount
        
        return suggested_quantity
