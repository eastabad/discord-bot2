-- 数据库模式修复 - 添加缺失的字段
-- 为VPS数据库添加缺失的reason字段到exempt_users表

-- 检查表结构
SELECT column_name, data_type, is_nullable 
FROM information_schema.columns 
WHERE table_name = 'exempt_users' 
ORDER BY ordinal_position;

-- 添加缺失的reason字段（如果不存在）
DO $$ 
BEGIN 
    IF NOT EXISTS (
        SELECT 1 FROM information_schema.columns 
        WHERE table_name = 'exempt_users' AND column_name = 'reason'
    ) THEN
        ALTER TABLE exempt_users ADD COLUMN reason VARCHAR(255) DEFAULT 'VIP用户';
        UPDATE exempt_users SET reason = 'VIP用户' WHERE reason IS NULL;
    END IF;
END $$;

-- 验证修复结果
SELECT column_name, data_type, is_nullable 
FROM information_schema.columns 
WHERE table_name = 'exempt_users' 
ORDER BY ordinal_position;