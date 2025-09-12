-- Discord Bot 数据库初始化脚本
-- 创建所需的表结构

-- 用户请求限制表
CREATE TABLE IF NOT EXISTS user_requests (
    id SERIAL PRIMARY KEY,
    user_id BIGINT NOT NULL,
    date DATE NOT NULL DEFAULT CURRENT_DATE,
    count INTEGER DEFAULT 1,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    UNIQUE(user_id, date)
);

-- VIP用户管理表
CREATE TABLE IF NOT EXISTS vip_users (
    id SERIAL PRIMARY KEY,
    user_id BIGINT UNIQUE NOT NULL,
    username VARCHAR(255),
    granted_by BIGINT,
    granted_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    expires_at TIMESTAMP,
    active BOOLEAN DEFAULT TRUE,
    notes TEXT
);

-- 管理员豁免用户表
CREATE TABLE IF NOT EXISTS exempt_users (
    id SERIAL PRIMARY KEY,
    user_id BIGINT UNIQUE NOT NULL,
    username VARCHAR(255),
    granted_by BIGINT,
    granted_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    active BOOLEAN DEFAULT TRUE,
    notes TEXT
);

-- TradingView Webhook数据存储表
CREATE TABLE IF NOT EXISTS tradingview_data (
    id SERIAL PRIMARY KEY,
    symbol VARCHAR(50) NOT NULL,
    timeframe VARCHAR(20),
    data_type VARCHAR(20),
    action VARCHAR(20),
    quantity DOUBLE PRECISION,
    take_profit_price DOUBLE PRECISION,
    stop_loss_price DOUBLE PRECISION,
    osc_rating DOUBLE PRECISION,
    trend_rating DOUBLE PRECISION,
    risk_level INTEGER,
    bullish_osc_rating DOUBLE PRECISION,
    bullish_trend_rating DOUBLE PRECISION,
    bearish_osc_rating DOUBLE PRECISION,
    bearish_trend_rating DOUBLE PRECISION,
    current_timeframe VARCHAR(20),
    trigger_indicator VARCHAR(100),
    trigger_timeframe VARCHAR(20),
    raw_data TEXT,
    parsed_signals TEXT,
    received_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    processed_at TIMESTAMP,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- 个人Webhook管理表
CREATE TABLE IF NOT EXISTS personal_webhooks (
    id SERIAL PRIMARY KEY,
    user_id BIGINT UNIQUE NOT NULL,
    username VARCHAR(255),
    secret_token VARCHAR(64) UNIQUE NOT NULL,
    webhook_url TEXT NOT NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    last_used TIMESTAMP,
    active BOOLEAN DEFAULT TRUE,
    use_count INTEGER DEFAULT 0
);

-- 报告缓存表
CREATE TABLE IF NOT EXISTS report_cache (
    id SERIAL PRIMARY KEY,
    symbol VARCHAR(20) NOT NULL,
    timeframe VARCHAR(10) NOT NULL,
    cache_key VARCHAR(255) UNIQUE NOT NULL,
    report_data JSONB NOT NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    expires_at TIMESTAMP NOT NULL,
    ai_model VARCHAR(50),
    request_count INTEGER DEFAULT 1
);

-- AI分析日志表
CREATE TABLE IF NOT EXISTS ai_analysis_log (
    id SERIAL PRIMARY KEY,
    user_id BIGINT,
    symbol VARCHAR(20),
    analysis_type VARCHAR(50),
    ai_model VARCHAR(50),
    request_data JSONB,
    response_data JSONB,
    processing_time DECIMAL(10,3),
    success BOOLEAN DEFAULT TRUE,
    error_message TEXT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- 系统配置表
CREATE TABLE IF NOT EXISTS system_config (
    id SERIAL PRIMARY KEY,
    config_key VARCHAR(100) UNIQUE NOT NULL,
    config_value TEXT,
    description TEXT,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_by VARCHAR(255)
);

-- 创建索引优化查询性能
CREATE INDEX IF NOT EXISTS idx_user_requests_user_date ON user_requests(user_id, date);
CREATE INDEX IF NOT EXISTS idx_tradingview_data_symbol_time ON tradingview_data(symbol, timestamp);
CREATE INDEX IF NOT EXISTS idx_personal_webhooks_user ON personal_webhooks(user_id);
CREATE INDEX IF NOT EXISTS idx_report_cache_expires ON report_cache(expires_at);
CREATE INDEX IF NOT EXISTS idx_ai_analysis_created ON ai_analysis_log(created_at);

-- 插入默认系统配置
INSERT INTO system_config (config_key, config_value, description) VALUES
('daily_request_limit', '50', '用户每日请求限制'),
('vip_request_limit', '200', 'VIP用户每日请求限制'),
('report_cache_hours', '2', '报告缓存有效期（小时）'),
('webhook_rate_limit', '100', 'Webhook每小时请求限制'),
('ai_timeout_seconds', '30', 'AI分析超时时间（秒）')
ON CONFLICT (config_key) DO NOTHING;

-- 创建自动清理过期数据的函数
CREATE OR REPLACE FUNCTION cleanup_expired_data() RETURNS void AS $$
BEGIN
    -- 清理过期的报告缓存
    DELETE FROM report_cache WHERE expires_at < NOW();
    
    -- 清理30天前的请求记录
    DELETE FROM user_requests WHERE date < CURRENT_DATE - INTERVAL '30 days';
    
    -- 清理90天前的AI分析日志
    DELETE FROM ai_analysis_log WHERE created_at < NOW() - INTERVAL '90 days';
    
    -- 清理180天前的TradingView数据
    DELETE FROM tradingview_data WHERE created_at < NOW() - INTERVAL '180 days';
END;
$$ LANGUAGE plpgsql;

-- 创建定时清理任务触发器（可选，需要pg_cron扩展）
-- SELECT cron.schedule('cleanup-expired-data', '0 2 * * *', 'SELECT cleanup_expired_data();');

COMMIT;