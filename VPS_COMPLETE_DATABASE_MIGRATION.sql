-- VPS完整数据库迁移脚本
-- 解决所有数据库模式不匹配问题

BEGIN;

-- 添加missing reason字段
DO $$ 
BEGIN 
    IF NOT EXISTS (
        SELECT 1 FROM information_schema.columns 
        WHERE table_name = 'exempt_users' AND column_name = 'reason'
    ) THEN
        ALTER TABLE exempt_users ADD COLUMN reason VARCHAR(255) DEFAULT 'VIP用户';
        RAISE NOTICE '✅ 添加reason字段成功';
    ELSE
        RAISE NOTICE '⚠️ reason字段已存在';
    END IF;
END $$;

-- 添加missing added_by字段
DO $$ 
BEGIN 
    IF NOT EXISTS (
        SELECT 1 FROM information_schema.columns 
        WHERE table_name = 'exempt_users' AND column_name = 'added_by'
    ) THEN
        ALTER TABLE exempt_users ADD COLUMN added_by VARCHAR(255) DEFAULT 'System';
        RAISE NOTICE '✅ 添加added_by字段成功';
    ELSE
        RAISE NOTICE '⚠️ added_by字段已存在';
    END IF;
END $$;

-- 添加missing created_at字段
DO $$ 
BEGIN 
    IF NOT EXISTS (
        SELECT 1 FROM information_schema.columns 
        WHERE table_name = 'exempt_users' AND column_name = 'created_at'
    ) THEN
        ALTER TABLE exempt_users ADD COLUMN created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP;
        RAISE NOTICE '✅ 添加created_at字段成功';
    ELSE
        RAISE NOTICE '⚠️ created_at字段已存在';
    END IF;
END $$;

-- 添加missing updated_at字段
DO $$ 
BEGIN 
    IF NOT EXISTS (
        SELECT 1 FROM information_schema.columns 
        WHERE table_name = 'exempt_users' AND column_name = 'updated_at'
    ) THEN
        ALTER TABLE exempt_users ADD COLUMN updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP;
        RAISE NOTICE '✅ 添加updated_at字段成功';
    ELSE
        RAISE NOTICE '⚠️ updated_at字段已存在';
    END IF;
END $$;

-- 更新现有数据的默认值
UPDATE exempt_users SET 
    reason = COALESCE(reason, 'VIP用户'),
    added_by = COALESCE(added_by, 'System'),
    created_at = COALESCE(created_at, CURRENT_TIMESTAMP),
    updated_at = COALESCE(updated_at, CURRENT_TIMESTAMP)
WHERE reason IS NULL OR added_by IS NULL OR created_at IS NULL OR updated_at IS NULL;

COMMIT;

-- 验证最终表结构
\echo '📋 最终exempt_users表结构:'
SELECT column_name, data_type, is_nullable, column_default 
FROM information_schema.columns 
WHERE table_name = 'exempt_users' 
ORDER BY ordinal_position;

-- 显示数据
\echo '📋 exempt_users表数据:'
SELECT user_id, username, reason, added_by, created_at FROM exempt_users;