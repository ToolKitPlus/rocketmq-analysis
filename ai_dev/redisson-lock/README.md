# Redisson 分布式锁源码解读指南

本目录包含 **Redisson 分布式锁源码逐行解析** 文档，以 EPUB 形式输出，适合在手机 / 电子书阅读器查看。
每个核心方法均附有「整体设计思想」说明，帮助读者深入理解 Redisson 的设计决策与权衡。

## 文件说明

| 文件 | 说明 |
|------|------|
| `Redisson_Lock_Source_Analysis.epub` | 生成好的源码解读 EPUB（可直接用手机/Kindle/iBooks 打开） |
| `generate_epub.py` | EPUB 生成脚本（Python 3 + ebooklib） |

## EPUB 内容目录

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

## 重新生成 EPUB

```bash
# 安装依赖
pip3 install ebooklib

# 生成 EPUB
python3 generate_epub.py
```

> **注意**：EPUB 内嵌 CSS 字体声明，阅读器只需支持 CJK 字体即可正常显示中文。
> 大多数现代阅读器（Kindle、iBooks、微信读书等）均支持直接打开 `.epub` 文件。

## 版本参考

- Redisson **3.x**（核心逻辑自 3.0 起基本稳定）
- Redis **2.6+**（需要 EVAL Lua 脚本支持）
