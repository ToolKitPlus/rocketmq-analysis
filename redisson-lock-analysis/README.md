# Redisson 分布式锁源码解读指南

本目录包含 **Redisson 分布式锁源码逐行解析** 文档，以 PDF 形式输出，适合在手机端查看（代码字体较小，避免过度换行）。

## 文件说明

| 文件 | 说明 |
|------|------|
| `Redisson_Lock_Source_Analysis.pdf` | 生成好的源码解读 PDF（17 页，A4 格式） |
| `generate_pdf.py` | PDF 生成脚本（Python 3 + reportlab） |

## PDF 内容目录

| 章节 | 主要内容 |
|------|----------|
| 1. 整体架构 | RedissonLock 类图、继承关系、核心字段 |
| 2. 加锁机制 | `lock()` → `tryAcquire` → Lua 脚本原子加锁 |
| 3. 可重入计数 | `HINCRBY` 实现可重入、Hash 数据结构 |
| 4. Watchdog 续期 | 看门狗原理、`renewExpiration` 定时任务 |
| 5. 解锁机制 | `unlock()` → Lua 脚本原子解锁 → Pub/Sub 通知 |
| 6. 公平锁 | `RedissonFairLock` 队列排队加锁 |
| 7. 红锁 RedLock | 多节点加锁、过半原则 |
| 8. 常见面试题 | 与 SETNX 方案对比、时序图 |
| 附录 | 关键 Redis 命令速查表 |

## 核心知识点

### 加锁 — Lua 原子脚本

```lua
-- exists → hincrby → pexpire，原子执行，无竞态
if (redis.call('exists', KEYS[1]) == 0) then
    redis.call('hincrby', KEYS[1], ARGV[2], 1)
    redis.call('pexpire', KEYS[1], ARGV[1])
    return nil        -- 加锁成功
end
if (redis.call('hexists', KEYS[1], ARGV[2]) == 1) then
    redis.call('hincrby', KEYS[1], ARGV[2], 1)  -- 可重入
    redis.call('pexpire', KEYS[1], ARGV[1])
    return nil
end
return redis.call('pttl', KEYS[1])  -- 锁被他人持有，返回剩余 TTL
```

### Watchdog — 自动续期

- 每隔 `leaseTime / 3`（默认 **10 秒**）执行一次续期 Lua 脚本
- 使用 Netty `HashedWheelTimer`，不阻塞业务线程
- `unlock()` 时调用 `timeout.cancel()` 停止续期
- 基于 `hexists` 校验，只续期当前线程持有的锁

### 解锁 — Lua 原子脚本 + Pub/Sub 通知

```lua
if (redis.call('hexists', KEYS[1], ARGV[3]) == 0) then return nil end
local counter = redis.call('hincrby', KEYS[1], ARGV[3], -1)
if (counter > 0) then
    redis.call('pexpire', KEYS[1], ARGV[2])
    return 0
else
    redis.call('del', KEYS[1])
    redis.call('publish', KEYS[2], ARGV[1])  -- 通知等待线程
    return 1
end
```

## 重新生成 PDF

```bash
# 安装依赖
pip3 install reportlab

# 生成 PDF
python3 generate_pdf.py
```

> **注意**：中文字符需要系统安装 Noto CJK 字体（Ubuntu: `apt install fonts-noto-cjk`）。
> 若未安装中文字体，中文将以拉丁字符替代显示，但 PDF 结构和代码内容完整。

## 版本参考

- Redisson **3.x**（核心逻辑自 3.0 起基本稳定）
- Redis **2.6+**（需要 EVAL Lua 脚本支持）
