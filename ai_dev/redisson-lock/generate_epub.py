#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Redisson 分布式锁源码解析 EPUB 生成脚本
生成一份适合手机 / 电子书阅读器查看的源码解读指南，包含每个方法的整体设计思想。
依赖：pip3 install ebooklib
"""

import os
import textwrap
from ebooklib import epub

# ──────────────────────────────────────────────────────────────
# CSS 样式
# ──────────────────────────────────────────────────────────────
STYLE_CSS = """
body {
    font-family: "Noto Sans CJK SC", "Source Han Sans CN", "PingFang SC",
                 "Microsoft YaHei", "WenQuanYi Micro Hei", sans-serif;
    font-size: 1em;
    line-height: 1.75;
    margin: 1em 1.2em;
    color: #212121;
    background: #ffffff;
}
h1 {
    font-size: 1.6em;
    color: #0d47a1;
    border-bottom: 2px solid #0d47a1;
    padding-bottom: 0.3em;
    margin-top: 1.5em;
}
h2 {
    font-size: 1.25em;
    color: #1565c0;
    border-left: 4px solid #1976d2;
    padding-left: 0.5em;
    margin-top: 1.2em;
}
h3 {
    font-size: 1.05em;
    color: #1976d2;
    margin-top: 1em;
}
p { margin: 0.6em 0; }
pre {
    font-family: "Courier New", "DejaVu Sans Mono", "Noto Sans Mono CJK SC",
                 "WenQuanYi Micro Hei Mono", monospace;
    font-size: 0.78em;
    background: #f5f5f5;
    border: 1px solid #e0e0e0;
    border-left: 3px solid #1976d2;
    padding: 0.8em 1em;
    margin: 0.6em 0;
    white-space: pre;
    overflow-x: auto;
    line-height: 1.5;
}
.tip {
    background: #e8f5e9;
    border: 1px solid #a5d6a7;
    border-left: 4px solid #388e3c;
    padding: 0.6em 1em;
    margin: 0.6em 0;
    color: #1b5e20;
    font-size: 0.9em;
    border-radius: 3px;
}
.warn {
    background: #ffebee;
    border: 1px solid #ef9a9a;
    border-left: 4px solid #c62828;
    padding: 0.6em 1em;
    margin: 0.6em 0;
    color: #b71c1c;
    font-size: 0.9em;
    border-radius: 3px;
}
.design {
    background: #e3f2fd;
    border: 1px solid #90caf9;
    border-left: 4px solid #1565c0;
    padding: 0.6em 1em;
    margin: 0.8em 0;
    color: #0d47a1;
    font-size: 0.92em;
    border-radius: 3px;
}
.design h3 {
    color: #0d47a1;
    font-size: 1em;
    margin: 0 0 0.4em 0;
}
table {
    width: 100%;
    border-collapse: collapse;
    font-size: 0.85em;
    margin: 0.8em 0;
}
thead tr { background: #0d47a1; color: #ffffff; }
th, td {
    border: 1px solid #c5cae9;
    padding: 0.45em 0.7em;
    vertical-align: top;
}
tr:nth-child(even) { background: #e8eaf6; }
.cover-title {
    text-align: center;
    font-size: 2em;
    color: #1a237e;
    margin-top: 2em;
}
.cover-sub {
    text-align: center;
    font-size: 1.1em;
    color: #546e7a;
    margin-top: 0.5em;
}
.cover-ver {
    text-align: center;
    font-size: 0.85em;
    color: #90a4ae;
    margin-top: 1em;
}
hr {
    border: none;
    border-top: 1px solid #bdbdbd;
    margin: 1.5em 0;
}
.comment { color: #757575; font-size: 0.85em; }
"""


# ──────────────────────────────────────────────────────────────
# 辅助函数（返回 HTML 字符串，避免 f-string 嵌套引号冲突）
# ──────────────────────────────────────────────────────────────

def pre(code):
    """代码块（转义 HTML 特殊字符，保留缩进）"""
    code = code.replace("&", "&amp;").replace("<", "&lt;").replace(">", "&gt;")
    return "<pre>" + code + "</pre>\n"


def tip(text):
    return '<div class="tip">&#128161; ' + text + '</div>\n'


def warn(text):
    return '<div class="warn">&#9888; ' + text + '</div>\n'


def design(title, *paras):
    """整体设计思想框"""
    inner = "".join("<p>" + p + "</p>\n" for p in paras)
    return (
        '<div class="design">'
        '<h3>&#128161; 整体设计思想：' + title + '</h3>'
        + inner
        + '</div>\n'
    )


def html_table(headers, rows):
    """生成 HTML 表格"""
    ths = "".join("<th>" + h + "</th>" for h in headers)
    trs = ""
    for row in rows:
        tds = "".join("<td>" + str(c) + "</td>" for c in row)
        trs += "<tr>" + tds + "</tr>\n"
    return (
        "<table><thead><tr>" + ths + "</tr></thead>"
        "<tbody>" + trs + "</tbody></table>\n"
    )


def h(level, text):
    tag = "h" + str(level)
    return "<" + tag + ">" + text + "</" + tag + ">\n"


def p(text):
    return "<p>" + text + "</p>\n"


# ──────────────────────────────────────────────────────────────
# 各章节内容
# ──────────────────────────────────────────────────────────────

def chapter_cover():
    return (
        '<div class="cover-title">Redisson 分布式锁<br/>源码解读指南</div>\n'
        '<div class="cover-sub">———— 加锁 · 解锁 · Watchdog 逐行注解 ————</div>\n'
        '<div class="cover-ver">版本参考：Redisson 3.x（基于 Redis 单机 / 集群）</div>\n'
        "<hr/>\n"
        '<p class="comment">本文档基于 Redisson 3.x 源码整理，'
        "源代码版权归 Redisson 项目及其贡献者所有。本文仅供学习参考。</p>\n"
    )


def chapter_toc():
    rows = [
        ("1. 整体架构",       "RedissonLock 类图、继承关系、核心字段"),
        ("2. 加锁机制",       "lock() → tryAcquire → Lua 脚本原子加锁"),
        ("3. 可重入计数",     "HINCRBY 实现可重入、Hash 数据结构"),
        ("4. Watchdog 续期",  "看门狗原理、renewExpiration 定时任务"),
        ("5. 解锁机制",       "unlock() → Lua 脚本原子解锁 → Pub/Sub 通知"),
        ("6. 公平锁",         "RedissonFairLock 队列排队加锁"),
        ("7. 红锁 RedLock",   "多节点加锁、过半原则"),
        ("8. 常见面试题",     "与 SETNX 方案对比、ABA 问题分析"),
        ("附录",              "关键 Redis 命令速查表"),
    ]
    return h(1, "目录") + html_table(["章节", "主要内容"], rows)


def chapter1():
    arch_rows = [
        ("RLock (interface)",   "顶层锁接口，扩展 Lock，增加 tryLock(time,unit) 等方法"),
        ("RedissonBaseLock",    "抽象基类，实现 Watchdog 逻辑、线程 ID 管理"),
        ("RedissonLock",        "普通可重入分布式锁（最常用）"),
        ("RedissonFairLock",    "公平锁，Redis List 维护等待队列"),
        ("RedissonReadLock",    "读写锁中的读锁"),
        ("RedissonWriteLock",   "读写锁中的写锁"),
        ("RedissonMultiLock",   "联锁，要求所有锁均加锁成功"),
        ("RedissonRedLock",     "红锁，要求过半节点加锁成功（已 deprecated）"),
    ]

    code_fields = """\
// RedissonBaseLock.java (部分字段)

public abstract class RedissonBaseLock extends RedissonExpirable implements RLock {

    // (1) Watchdog 默认超时时间 = 30 秒
    //     若调用 lock() 不指定 leaseTime，则使用此值
    protected static final long internalLockLeaseTime =
        Config.DEFAULT_LOCK_WATCHDOG_TIMEOUT;

    // (2) 锁的唯一标识前缀：UUID + ":" + threadId
    //     每个 Redisson 客户端实例拥有唯一 UUID
    protected final String id;        // = UUID (由 CommandAsyncExecutor 维护)
    protected final String entryName; // = id + ":" + lockName

    // (3) Watchdog 心跳续期任务 Map
    //     key = entryName，value = ExpirationEntry（持有 threadId 集合 + Future）
    private static final ConcurrentMap<String, ExpirationEntry> EXPIRATION_RENEWAL_MAP
        = new ConcurrentHashMap<>();

    // (4) 命令执行器（封装了 Netty 异步通信到 Redis）
    protected final CommandAsyncExecutor commandExecutor;

    // (5) 发布订阅器（等锁时监听解锁事件，避免轮询）
    protected final LockPubSub pubSub;
}"""

    code_hash = """\
# Redis 中锁的存储形式（HGETALL my-lock）
my-lock (Hash)
  +-- field: "a1b2c3d4-...-uuid:1"   value: 1   # 线程1持锁，重入次数=1
  +-- field: "a1b2c3d4-...-uuid:1"   value: 2   # 同一线程再次加锁，重入次数=2

# TTL 由 PEXPIRE 单独设置（单位：毫秒）
PEXPIRE my-lock 30000"""

    out = h(1, "1. 整体架构")
    out += p("Redisson 锁体系以 <strong>RedissonBaseLock</strong> 为抽象父类，向上实现 "
             "<code>RLock</code>（继承自 <code>java.util.concurrent.locks.Lock</code>）接口，"
             "向下派生出多种锁实现：")
    out += html_table(["类 / 接口", "说明"], arch_rows)
    out += design(
        "分层继承 + 接口抽象",
        "Redisson 采用标准 JUC Lock 接口作为顶层契约，让分布式锁对上层代码透明——"
        "业务代码无需感知底层是本地锁还是 Redis 锁，便于切换和测试。",
        "RedissonBaseLock 抽象基类集中处理 Watchdog 续期、UUID 管理、线程 ID 绑定等"
        "与具体加解锁策略无关的横切逻辑（类似 AOP），各子类只需实现 "
        "tryLockInnerAsync / unlockInnerAsync 两个核心 Lua 脚本，职责单一、易于扩展。",
        "这种设计使得添加新锁类型（如读写锁、信号量）只需继承 RedissonBaseLock "
        "并实现对应 Lua 脚本，不影响已有逻辑。",
    )
    out += h(2, "1.1 RedissonBaseLock 核心字段")
    out += pre(code_fields)
    out += tip("UUID 在 Redisson 客户端启动时生成，每个 JVM 实例唯一，"
               "配合 threadId 共同标识锁的持有者，"
               "解决了分布式场景下「谁持有锁」的身份认证问题。")
    out += h(2, "1.2 Redis 中锁的数据结构")
    out += p("Redisson 普通锁使用 Redis <strong>Hash</strong> 存储，Key 为锁名，Field 为 "
             "<code>UUID:threadId</code>，Value 为可重入次数：")
    out += pre(code_hash)
    out += design(
        "用 Hash 代替 String 存锁",
        "传统 SETNX/SET NX 方案用 String 存储持锁者标识，"
        "无法在单个 Key 内同时记录「谁持有」和「重入次数」两个维度的信息。",
        "Redisson 选用 Hash：Field = UUID:threadId（身份），Value = 重入计数（状态）。"
        "同一 Key 下可用 HINCRBY 原子加减计数，天然支持可重入语义，"
        "且 HEXISTS 可在 O(1) 时间内校验持锁身份。",
        "这一数据结构选择是整个可重入机制的基石——"
        "后续所有 Lua 脚本都基于此结构设计。",
    )
    return out


def chapter2():
    code_lock = """\
// RedissonLock.java

@Override
public void lock() {
    try {
        // (1) 调用带参版本，leaseTime=-1 代表使用 Watchdog 模式（不手动设置过期）
        lock(-1, null, false);
    } catch (InterruptedException e) {
        throw new IllegalStateException();
    }
}

private void lock(long leaseTime, TimeUnit unit, boolean interruptibly)
        throws InterruptedException {

    // (2) 获取当前线程 ID（用于标识锁持有者）
    long threadId = Thread.currentThread().getId();

    // (3) 尝试异步加锁；ttl=null 代表加锁成功；ttl>0 代表锁被他人持有
    Long ttl = tryAcquire(-1, leaseTime, unit, threadId);

    // (4) 加锁成功，直接返回
    if (ttl == null) {
        return;
    }

    // (5) 加锁失败，订阅解锁事件（避免自旋轮询，节省 CPU）
    RFuture<RedissonLockEntry> future = subscribe(threadId);
    // 等待订阅完成（命令发送到 Redis pub/sub）
    commandExecutor.syncSubscription(future);

    try {
        // (6) 进入自旋等待循环
        while (true) {
            ttl = tryAcquire(-1, leaseTime, unit, threadId);
            if (ttl == null) {
                break;
            }
            // (7) Semaphore 阻塞等待解锁通知，最多等待 ttl 毫秒
            //     unlock() 后 publish 解锁消息，唤醒此处
            if (ttl >= 0) {
                try {
                    future.getNow().getLatch().tryAcquire(ttl, TimeUnit.MILLISECONDS);
                } catch (InterruptedException e) {
                    if (interruptibly) throw e;
                }
            } else {
                // ttl < 0 说明持有者已过期，直接等
                future.getNow().getLatch().acquire();
            }
        }
    } finally {
        // (8) 取消订阅解锁通知
        unsubscribe(future, threadId);
    }
}"""

    code_try_acquire = """\
// RedissonLock.java

private Long tryAcquire(long waitTime, long leaseTime,
                         TimeUnit unit, long threadId) {
    // 把异步 Future 转成同步结果
    return get(tryAcquireAsync(waitTime, leaseTime, unit, threadId));
}

private <T> RFuture<Long> tryAcquireAsync(long waitTime, long leaseTime,
                                            TimeUnit unit, long threadId) {
    RFuture<Long> ttlRemainingFuture;

    if (leaseTime > 0) {
        // (1) 指定了 leaseTime：直接设置固定过期时间（不启用 Watchdog）
        ttlRemainingFuture = tryLockInnerAsync(waitTime,
                                leaseTime, unit, threadId, LOCK_SCRIPT);
    } else {
        // (2) 未指定 leaseTime：先用 internalLockLeaseTime 加锁，再启动 Watchdog
        ttlRemainingFuture = tryLockInnerAsync(waitTime,
                                internalLockLeaseTime,
                                TimeUnit.MILLISECONDS, threadId, LOCK_SCRIPT);
    }

    // (3) 注册回调，处理加锁结果
    CompletionStage<Long> f = ttlRemainingFuture.thenApply(ttlRemaining -> {
        if (ttlRemaining == null) {          // 加锁成功
            if (leaseTime > 0) {
                internalLockLeaseTime = unit.toMillis(leaseTime);
            } else {
                scheduleExpirationRenewal(threadId);  // 启动 Watchdog
            }
        }
        return ttlRemaining;
    });
    return new CompletableFutureWrapper<>(f);
}"""

    code_lua_lock = """\
// RedissonLock.java

<T> RFuture<T> tryLockInnerAsync(long waitTime, long leaseTime,
                                   TimeUnit unit, long threadId,
                                   RedisStrictCommand<T> command) {
    // KEYS[1]  = 锁名（如 "my-lock"）
    // ARGV[1]  = 过期时间（毫秒）
    // ARGV[2]  = lockName = UUID + ":" + threadId
    return evalWriteAsync(getRawName(), LongCodec.INSTANCE, command,

        // Lua 脚本（原子执行）
        // 第 1 步：锁不存在 -> 新建并加锁
        "if (redis.call('exists', KEYS[1]) == 0) then " +
            "   redis.call('hincrby', KEYS[1], ARGV[2], 1); " +
            "   redis.call('pexpire', KEYS[1], ARGV[1]); " +
            "   return nil; " +       // nil = 加锁成功
        "end; " +

        // 第 2 步：锁存在且是当前线程 -> 可重入，计数 +1
        "if (redis.call('hexists', KEYS[1], ARGV[2]) == 1) then " +
            "   redis.call('hincrby', KEYS[1], ARGV[2], 1); " +
            "   redis.call('pexpire', KEYS[1], ARGV[1]); " +
            "   return nil; " +
        "end; " +

        // 第 3 步：锁被他人持有 -> 返回剩余 TTL（毫秒）
        "return redis.call('pttl', KEYS[1]);",

        Collections.singletonList(getRawName()),   // KEYS[1]
        unit.toMillis(leaseTime),                  // ARGV[1]
        getLockName(threadId));                    // ARGV[2]
}"""

    out = h(1, "2. 加锁机制")
    out += p("加锁入口有三个：<code>lock()</code>（阻塞永久等待）、"
             "<code>lock(leaseTime, unit)</code>（阻塞指定 leaseTime）、"
             "<code>tryLock(waitTime, leaseTime, unit)</code>（带超时的非阻塞）。"
             "三者最终均汇聚到 <code>tryAcquire</code>。")
    out += design(
        "三入口收敛到单一加锁路径",
        "面向使用者提供多个语义清晰的入口（阻塞/非阻塞/带超时），"
        "但所有入口最终都收敛到 tryAcquireAsync 这一处核心异步逻辑，"
        "避免代码重复，同时保证加锁策略的一致性。",
        "这与 JUC ReentrantLock 的设计哲学一致：外部 API 多样，内部实现统一（AQS）。",
        "异步化（返回 CompletionStage）是 Redisson 的核心设计取向，"
        "通过 Netty 事件循环执行 Redis 命令，不阻塞业务线程，"
        "底层 get() 方法在同步调用时才阻塞等待结果。",
    )
    out += h(2, "2.1 lock() 方法调用链")
    out += pre(code_lock)
    out += tip("subscribe/unsubscribe 使用 Redis Pub/Sub，"
               "channel 名为 redisson_lock__channel:{lockName}。"
               "等锁期间不轮询 Redis，资源效率更高。")
    out += design(
        "Pub/Sub + Semaphore 替代自旋轮询",
        "朴素的分布式锁等待方案是「加锁失败 → sleep → 重试」，"
        "这会造成大量无效 Redis 请求（惊群效应），在高并发竞争场景下性能极差。",
        "Redisson 借鉴 JUC AQS 的条件等待思想：加锁失败时，"
        "通过 Redis Pub/Sub 订阅解锁 channel，"
        "然后用 Java Semaphore.tryAcquire(ttl) 挂起当前线程。"
        "锁持有者 unlock() 时 PUBLISH 消息，Semaphore 被 release，"
        "等待线程精确唤醒后立即重试加锁。",
        "这一设计将等待开销从 O(QPS \xd7 轮询间隔) 降低到接近 O(1)——"
        "只有锁真正释放时才触发唤醒，极大减少了空转和 Redis 压力。",
    )
    out += h(2, "2.2 tryAcquire — 同步转异步")
    out += pre(code_try_acquire)
    out += design(
        "leaseTime 语义分叉决策",
        "加锁时面临两种场景：用户明确指定了锁的有效期（leaseTime > 0），"
        "或用户希望锁跟随业务生命周期自动管理（无参 lock()）。",
        "对于前者，Redisson 直接使用用户指定的 TTL，不启动 Watchdog——"
        "锁的生命周期由用户承担，适合已知最大执行时间的场景。",
        "对于后者，先以默认 30s 加锁（保证 Redis 中锁必然有 TTL 兜底，"
        "防止进程崩溃时死锁），加锁成功后再启动 Watchdog 持续续期。"
        "这一「先设 TTL 兜底、后续期维持」的两段式设计，"
        "在安全性（不会永久占锁）和活性（不会因超时提前释放）之间取得了最佳平衡。",
    )
    out += h(2, "2.3 tryLockInnerAsync — Lua 原子加锁")
    out += p("真正执行 Redis 操作的方法。使用 Lua 脚本保证检查+设置的原子性，"
             "避免 SETNX + EXPIRE 两步之间的竞态条件。")
    out += pre(code_lua_lock)
    out += tip("Lua 脚本在 Redis 中是原子执行的。"
               "整个 exists→hincrby→pexpire 序列不会被其他命令打断，"
               "因此不需要额外的乐观锁（CAS）。")
    out += warn("若调用 lock(leaseTime, unit) 指定了 leaseTime，Watchdog 不会启动。"
                "leaseTime 到期后，即使业务未完成锁也会自动释放，存在安全风险。"
                "推荐使用无参 lock() 配合 Watchdog。")
    out += design(
        "Lua 脚本保证原子性——三分支状态机",
        "加锁操作本质上是一个三分支状态机：① 锁不存在 → 新建并加锁；"
        "② 锁存在且自己持有 → 可重入，计数 +1；"
        "③ 锁存在但他人持有 → 返回剩余 TTL（告知等待时间）。",
        "这三个分支必须原子执行，否则在「检查」和「设置」之间"
        "可能有其他客户端插入，导致两个客户端同时认为自己加锁成功（ABA 竞态）。"
        "Redis 的 EVAL 命令保证 Lua 脚本以单线程方式原子执行，"
        "从根本上消除竞态。",
        "返回值的语义设计也值得关注：nil 表示成功，正整数表示失败且给出等待时长，"
        "这让调用方能精确地用 Semaphore.tryAcquire(ttl) 等待，而非盲目 sleep。",
    )
    return out


def chapter3():
    code_incr = """\
-- Lua 脚本片段（加锁时）

-- 第一次加锁：hincrby my-lock "uuid:1" 1  -> value = 1
-- 第二次加锁（重入）：hincrby my-lock "uuid:1" 1  -> value = 2
redis.call('hincrby', KEYS[1], ARGV[2], 1)
redis.call('pexpire', KEYS[1], ARGV[1])

-- Redis 中结果：
-- HGETALL my-lock -> 1) "uuid:1"  2) "2"  （重入 2 次）"""

    code_decr = """\
-- Lua 脚本片段（解锁时，详见第 5 章）

local counter = redis.call('hincrby', KEYS[1], ARGV[3], -1)

if (counter > 0) then
    -- 重入计数 > 0，还有外层锁未释放，只刷新过期时间
    redis.call('pexpire', KEYS[1], ARGV[2])
    return 0   -- 0 = 锁未完全释放
else
    -- 计数归零：删除整个 Hash Key，锁完全释放
    redis.call('del', KEYS[1])
    redis.call('publish', KEYS[2], ARGV[1])  -- 通知等待线程
    return 1   -- 1 = 锁已完全释放
end"""

    code_example = """\
RLock lock = redisson.getLock("my-lock");

lock.lock();        // Redis: HSET my-lock uuid:1 1, PEXPIRE my-lock 30000
try {
    doWork1();
    lock.lock();    // Redis: HINCRBY my-lock uuid:1 1  (value=2)
    try {
        doWork2();
    } finally {
        lock.unlock(); // Redis: HINCRBY my-lock uuid:1 -1 (value=1), 不删 Key
    }
} finally {
    lock.unlock();  // Redis: HINCRBY my-lock uuid:1 -1 (value=0), DEL my-lock
}"""

    out = h(1, "3. 可重入计数详解")
    out += p("Redisson 分布式锁支持同一线程多次加锁（可重入），"
             "依靠 Redis Hash 的 <code>HINCRBY</code> 命令实现计数。")
    out += design(
        "可重入语义与 JUC ReentrantLock 对齐",
        "Java 本地锁 ReentrantLock 支持可重入，避免同一线程在嵌套调用中自锁自死。"
        "分布式锁若不支持可重入，调用链中任何一层重复加同一把锁就会死锁，"
        "严重限制业务代码的可组合性。",
        "Redisson 通过 Hash Value 记录重入深度，lock/unlock 对称地执行 "
        "HINCRBY +1/-1，只有计数降到 0 时才真正释放锁（DEL Key），"
        "语义与 ReentrantLock 完全一致，业务代码迁移成本极低。",
        "关键约束：重入次数必须精确对称，加几次锁就要解几次锁，"
        "否则锁提前或延迟释放。建议始终在 try-finally 中配对使用 lock/unlock。",
    )
    out += h(2, "3.1 加锁时计数 +1")
    out += pre(code_incr)
    out += h(2, "3.2 解锁时计数 -1")
    out += pre(code_decr)
    out += h(2, "3.3 可重入示例")
    out += pre(code_example)
    out += tip("可重入次数必须与 lock 次数精确匹配，否则锁将提前 / 无法释放。")
    return out


def chapter4():
    code_schedule = """\
// RedissonBaseLock.java

protected void scheduleExpirationRenewal(long threadId) {
    // (1) 创建/获取 ExpirationEntry（每个锁名对应一个）
    ExpirationEntry entry = new ExpirationEntry();
    ExpirationEntry oldEntry =
        EXPIRATION_RENEWAL_MAP.putIfAbsent(getEntryName(), entry);

    if (oldEntry != null) {
        // 同一 JVM 内同一锁被同一线程再次加锁（重入）
        // 只需在已有 entry 中记录当前 threadId，不重复注册定时任务
        oldEntry.addThreadId(threadId);
    } else {
        // 首次加锁，注册当前 threadId，并启动续期定时任务
        entry.addThreadId(threadId);
        try {
            renewExpiration();    // <-- 真正注册定时任务
        } finally {
            if (Thread.currentThread().isInterrupted()) {
                cancelExpirationRenewal(threadId);
            }
        }
    }
}"""

    code_renew = """\
// RedissonBaseLock.java

private void renewExpiration() {
    ExpirationEntry ee = EXPIRATION_RENEWAL_MAP.get(getEntryName());
    if (ee == null) {
        return;   // 锁已被释放，不再续期
    }

    // (1) 使用 Netty HashedWheelTimer 调度延迟任务
    //     延迟时间 = internalLockLeaseTime / 3（默认 10000 ms）
    Timeout task = commandExecutor.getServiceManager().newTimeout(
        new TimerTask() {
            @Override
            public void run(Timeout timeout) throws Exception {
                ExpirationEntry ent = EXPIRATION_RENEWAL_MAP.get(getEntryName());
                if (ent == null) {
                    return;   // 锁已解除，停止续期
                }

                Long threadId = ent.getFirstThreadId();
                if (threadId == null) {
                    return;
                }

                // (4) 执行续期 Lua 脚本（异步）
                CompletionStage<Boolean> future = renewExpirationAsync(threadId);
                future.whenComplete((res, e) -> {
                    if (e != null) {
                        log.error("Can't update lock {} expiration", getRawName(), e);
                        EXPIRATION_RENEWAL_MAP.remove(getEntryName());
                        return;
                    }
                    if (res) {
                        // (5) 续期成功，递归注册下一次任务
                        renewExpiration();
                    } else {
                        // 锁已不存在，停止续期
                        cancelExpirationRenewal(null);
                    }
                });
            }
        },
        internalLockLeaseTime / 3, TimeUnit.MILLISECONDS
    );

    // (6) 保存 Task 引用，unlock 时取消
    ee.setTimeout(task);
}"""

    code_renew_lua = """\
// RedissonBaseLock.java

protected CompletionStage<Boolean> renewExpirationAsync(long threadId) {
    return evalWriteAsync(getRawName(), LongCodec.INSTANCE,
        RedisCommands.EVAL_BOOLEAN,

        // 检查锁是否仍由当前线程持有（避免误续他人的锁）
        "if (redis.call('hexists', KEYS[1], ARGV[2]) == 1) then " +
            "   redis.call('pexpire', KEYS[1], ARGV[1]); " +
            "   return 1; " +    // 续期成功
        "end; " +
        "return 0;",            // 锁已不属于本线程

        Collections.singletonList(getRawName()),  // KEYS[1]
        internalLockLeaseTime,                    // ARGV[1]
        getLockName(threadId));                   // ARGV[2]
}"""

    code_cancel = """\
// RedissonBaseLock.java

protected void cancelExpirationRenewal(Long threadId) {
    ExpirationEntry task = EXPIRATION_RENEWAL_MAP.get(getEntryName());
    if (task == null) {
        return;
    }

    if (threadId != null) {
        task.removeThreadId(threadId);  // 移除当前 threadId（重入场景）
    }

    if (threadId == null || task.hasNoThreads()) {
        Timeout timeout = task.getTimeout();
        if (timeout != null) {
            timeout.cancel();   // 取消 HashedWheelTimer 定时任务
        }
        EXPIRATION_RENEWAL_MAP.remove(getEntryName());  // 彻底停止续期
    }
}"""

    out = h(1, "4. Watchdog（看门狗）续期机制")
    out += p("当使用无参 <code>lock()</code> 时，Redisson 会启动一个后台定时任务，"
             "每隔 <code>leaseTime/3</code>（默认 10 秒）自动刷新锁的过期时间，"
             "防止业务耗时超过 leaseTime 导致锁提前释放。")
    out += design(
        "Watchdog——用心跳代替静态超时",
        "分布式锁最大的两难困境：TTL 太短则业务未完成锁已过期，"
        "造成并发安全问题；TTL 太长则进程崩溃后其他节点等待时间过长，可用性下降。",
        "Watchdog 打破了这一困境：锁的初始 TTL 固定为 30s（防崩溃死锁），"
        "但只要持锁进程存活，Watchdog 每 10s 续期一次，"
        "使锁「实际上永不过期」直到业务主动 unlock。"
        "进程崩溃时 Watchdog 随之停止，锁在最多 30s 后自动释放，兜底安全。",
        "续期间隔选择 leaseTime/3 是工程权衡：续期过频浪费 Redis 带宽，"
        "过稀则在网络抖动时可能漏过一次续期导致锁意外过期。"
        "1/3 的间隔在默认 30s TTL 下意味着允许连续两次续期失败（20s），仍有足够余量。",
    )
    out += h(2, "4.1 scheduleExpirationRenewal — 注册 Watchdog")
    out += pre(code_schedule)
    out += design(
        "ConcurrentHashMap 去重定时任务",
        "同一 JVM 内同一把锁可能被多个线程并发持有（可重入场景），"
        "若每次加锁都注册一个新的定时续期任务，会造成定时任务泛滥。",
        "Redisson 以锁名（entryName）为 Key，用 "
        "ConcurrentHashMap.putIfAbsent 保证只有第一次加锁才真正注册定时任务；"
        "重入时只在已有 Entry 中追加 threadId 记录。"
        "cancelExpirationRenewal 时检查 threadId 集合是否为空，"
        "只有最后一个持锁线程释放后才真正取消任务。",
        "这一「引用计数 + 单任务」模式，有效控制了后台资源消耗。",
    )
    out += h(2, "4.2 renewExpiration — 定时续期任务")
    out += pre(code_renew)
    out += design(
        "HashedWheelTimer + 尾递归——非阻塞心跳循环",
        "续期任务需要在后台周期性执行。Redisson 选择了 Netty 的 "
        "HashedWheelTimer + 回调尾递归：续期成功后在回调内再次调用 "
        "renewExpiration() 注册下一个单次延迟任务，形成自驱动循环。",
        "优势：① HashedWheelTimer 专为大量定时任务设计，"
        "内存和 CPU 开销远低于线程池定时器；"
        "② 每次续期都是「上一次成功后」才注册下一次，"
        "若 Redis 连接中断导致续期失败，任务链自然断裂，不会继续无意义重试（fail-fast）；"
        "③ 全程基于 Netty 事件循环，不阻塞任何业务线程。",
    )
    out += h(2, "4.3 renewExpirationAsync — 续期 Lua 脚本")
    out += pre(code_renew_lua)
    out += tip("Watchdog 的续期判断基于 hexists，只有锁仍由本线程持有时才续期。"
               "即使 JVM 假死（GC Stop-The-World）导致 Watchdog 超过 leaseTime 未跑，"
               "锁也会自然过期，不会永久阻塞其他节点。")
    out += warn("Watchdog 依赖 Netty 线程池，若应用整体卡死（如 OOM），续期线程也将停止，"
                "30 秒后锁会自动释放。这是一种兜底机制，不能依赖 Watchdog 保证绝对安全。")
    out += h(2, "4.4 cancelExpirationRenewal — 取消 Watchdog")
    out += pre(code_cancel)
    return out


def chapter5():
    code_unlock = """\
// RedissonLock.java

@Override
public void unlock() {
    try {
        get(unlockAsync(Thread.currentThread().getId()));
    } catch (RedisException e) {
        if (e.getCause() instanceof IllegalMonitorStateException) {
            throw (IllegalMonitorStateException) e.getCause();
        } else {
            throw e;
        }
    }
}

@Override
public RFuture<Void> unlockAsync(long threadId) {
    return getServiceManager().execute(() -> unlockAsync0(threadId));
}

private RFuture<Void> unlockAsync0(long threadId) {
    // (1) 执行 Lua 解锁脚本
    CompletionStage<Boolean> future = unlockInnerAsync(threadId);

    CompletionStage<Void> f = future.handle((opStatus, e) -> {
        // (2) 无论结果如何，先取消 Watchdog
        cancelExpirationRenewal(threadId);

        if (e != null) {
            throw commandExecutor.convertException(e);
        }

        if (opStatus == null) {
            // (4) 当前线程未持有此锁，抛出 IllegalMonitorStateException
            IllegalMonitorStateException cause =
                new IllegalMonitorStateException(
                    "attempt to unlock lock, not locked by current thread node id: "
                    + id + " thread-id: " + threadId);
            throw new CompletionException(cause);
        }
        return null;
    });

    return new CompletableFutureWrapper<>(f);
}"""

    code_unlock_lua = """\
// RedissonLock.java

protected RFuture<Boolean> unlockInnerAsync(long threadId) {
    // KEYS[1] = 锁名
    // KEYS[2] = Pub/Sub channel
    // ARGV[1] = 解锁消息（固定值 0）
    // ARGV[2] = leaseTime
    // ARGV[3] = lockName = UUID:threadId
    return evalWriteAsync(getRawName(), LongCodec.INSTANCE,
        RedisCommands.EVAL_BOOLEAN,

        // 第 1 步：校验身份（防止误解锁）
        "if (redis.call('hexists', KEYS[1], ARGV[3]) == 0) then " +
            "   return nil; " +   // 未持有，返回 nil（Java 层抛异常）
        "end; " +

        // 第 2 步：重入计数 -1
        "local counter = redis.call('hincrby', KEYS[1], ARGV[3], -1); " +

        // 第 3 步：根据计数决定是否释放锁
        "if (counter > 0) then " +
            "   redis.call('pexpire', KEYS[1], ARGV[2]); " +  // 仍有重入，刷新 TTL
            "   return 0; " +
        "else " +
            "   redis.call('del', KEYS[1]); " +               // 计数归零，删除 Key
            "   redis.call('publish', KEYS[2], ARGV[1]); " +  // 广播解锁消息
            "   return 1; " +
        "end; " +
        "return nil;",

        Arrays.asList(getRawName(), getChannelName()),  // KEYS
        LockPubSub.UNLOCK_MESSAGE,                      // ARGV[1]
        internalLockLeaseTime,                          // ARGV[2]
        getLockName(threadId));                         // ARGV[3]
}"""

    code_pubsub = """\
// LockPubSub.java（节选）

public class LockPubSub extends PublishSubscribeService {

    public static final Long UNLOCK_MESSAGE      = 0L;  // 普通解锁
    public static final Long READ_UNLOCK_MESSAGE = 1L;  // 读锁解锁（读写锁用）

    @Override
    protected void onMessage(RedissonLockEntry value, Long message) {
        if (message.equals(UNLOCK_MESSAGE)) {
            // 收到解锁通知：释放 Semaphore，唤醒 lock() 中等待的线程
            Listener listener = value.getListeners().poll();
            if (listener != null) {
                listener.onEvent(value);
            } else {
                value.getLatch().release();
            }
        } else if (message.equals(READ_UNLOCK_MESSAGE)) {
            while (true) {
                Listener listener = value.getListeners().poll();
                if (listener == null) {
                    value.getLatch().release();
                    break;
                }
                listener.onEvent(value);
            }
        }
    }
}"""

    out = h(1, "5. 解锁机制")
    out += p("解锁入口为 <code>unlock()</code>，核心也是一段 Lua 脚本，"
             "保证计数递减、Key 删除、Pub/Sub 通知的原子性。")
    out += design(
        "解锁三步原子化 + 防误解锁",
        "解锁操作至少涉及三件事：校验持锁身份（防止 A 释放 B 的锁）、"
        "递减重入计数（支持可重入）、Key 完全归零后通知等待者（Pub/Sub）。"
        "这三步必须原子完成。",
        "Redisson 使用 Lua 脚本，将 hexists 校验、hincrby 递减、del + publish "
        "合并为单个原子操作，彻底消除竞态窗口。",
        "返回值语义：nil 表示当前线程未持有此锁（非法解锁），"
        "0 表示解锁成功但还有重入层，1 表示锁完全释放并已通知等待者。"
        "Java 层根据 nil 抛出 IllegalMonitorStateException，"
        "与 synchronized 的非法 monitor 操作行为对齐。",
    )
    out += h(2, "5.1 unlock() 调用链")
    out += pre(code_unlock)
    out += design(
        "解锁流程中的 Watchdog 取消时机",
        "cancelExpirationRenewal 在 handle 回调中，"
        "无论解锁 Lua 脚本成功还是失败（Redis 异常），都会被第一时间调用。",
        "这是防御性设计：哪怕解锁失败（如网络超时），Watchdog 也必须停止续期，"
        "避免已「逻辑解锁」的场景中 Watchdog 仍在为一把「僵尸锁」续期，"
        "导致其他节点无法在 TTL 内获得锁。",
        "这体现了「最终一致性优先」的工程哲学："
        "宁可让锁稍早过期（靠 TTL 兜底），也不能让续期线程逃逸生命周期边界。",
    )
    out += h(2, "5.2 unlockInnerAsync — Lua 原子解锁")
    out += pre(code_unlock_lua)
    out += h(2, "5.3 Pub/Sub 通知等待线程")
    out += pre(code_pubsub)
    out += tip("Pub/Sub channel 名格式：redisson_lock__channel:{lockName}。"
               "一个 channel 对应一把锁，所有等待该锁的线程/节点都订阅此 channel。"
               "解锁时只 publish 一次消息，但等待队列中的线程会轮流被唤醒"
               "（Semaphore 每次只 release 1）。")
    return out


def chapter6():
    code_ds = """\
# 公平锁使用三个 Key：

# 1. Hash Key（与普通锁相同）：存储持锁者
my-fair-lock (Hash)
  +-- "uuid:1" -> 1

# 2. List Key（等待队列）：严格 FIFO，RPUSH 入队、LPOP 出队
redisson_lock_queue:{my-fair-lock} (List)
  +-- 0) "uuid:2"    <- 队首（最先等待，下一个获得锁）
  +-- 1) "uuid:3"

# 3. ZSet Key（超时记录）：score = 超时时间戳（毫秒 epoch）
redisson_lock_timeout:{my-fair-lock} (ZSet)
  +-- "uuid:2" -> 1700000010000
  +-- "uuid:3" -> 1700000020000"""

    code_fair_lua = """\
-- RedissonFairLock 加锁 Lua 脚本（简化版）

-- (1) 清理已超时的等待者（防止超时节点永久阻塞队列）
while true do
    local firstThreadId = redis.call('lindex', KEYS[2], 0)
    if firstThreadId == false then break end

    local timeout = tonumber(redis.call('zscore', KEYS[3], firstThreadId))
    if timeout <= tonumber(ARGV[4]) then  -- ARGV[4] = 当前时间戳
        redis.call('zrem', KEYS[3], firstThreadId)
        redis.call('lpop', KEYS[2])
    else
        break
    end
end

-- (2) 仅当队列为空 OR 当前线程是队首时才允许加锁
if (redis.call('exists', KEYS[1]) == 0) then
    local firstThreadId = redis.call('lindex', KEYS[2], 0)
    if firstThreadId == false or firstThreadId == ARGV[2] then
        redis.call('lpop', KEYS[2])
        redis.call('zrem', KEYS[3], ARGV[2])
        redis.call('hset', KEYS[1], ARGV[2], 1)
        redis.call('pexpire', KEYS[1], ARGV[1])
        return nil   -- 加锁成功
    end
end

-- (3) 加锁失败：幂等入队（已在队则不重复）
if redis.call('zscore', KEYS[3], ARGV[2]) == false then
    redis.call('rpush', KEYS[2], ARGV[2])
    redis.call('zadd', KEYS[3], tonumber(ARGV[3]) + tonumber(ARGV[4]), ARGV[2])
end

-- (4) 返回剩余等待时间
return redis.call('pttl', KEYS[1])"""

    out = h(1, "6. 公平锁 RedissonFairLock")
    out += p("普通 RedissonLock 不保证加锁顺序（等待线程随机竞争）。"
             "RedissonFairLock 通过 Redis List 维护等待队列，确保先到先得。")
    out += design(
        "三结构协同实现分布式公平队列",
        "本地公平锁（如 ReentrantLock(true)）直接利用 AQS 的 CLH 队列排队，"
        "节点在 JVM 内存中，入队/出队是本地操作。"
        "分布式公平锁需要在多个 JVM 进程间共享等待序列，不能用内存队列。",
        "Redisson 用三个 Redis 数据结构协同工作："
        "① Hash（持锁者 + 重入计数）；"
        "② List（有序等待队列，RPUSH 入队、LPOP 出队，严格 FIFO）；"
        "③ ZSet（各等待者的超时时间戳）。"
        "每次加锁前先从 List/ZSet 清理已超时的等待者，防止超时节点永久阻塞队列。",
        "这种多结构联合事务由单个 Lua 脚本原子完成，"
        "保证「清理超时者→判断队首→加锁 or 入队」整个流程不被并发干扰。"
        "代价是 Lua 脚本更复杂，加锁延迟略高于普通锁。",
    )
    out += h(2, "6.1 数据结构")
    out += pre(code_ds)
    out += h(2, "6.2 公平锁 Lua 加锁脚本（核心逻辑）")
    out += pre(code_fair_lua)
    return out


def chapter7():
    code_multilock = """\
// RedissonMultiLock.java（简化）

@Override
public boolean tryLock(long waitTime, long leaseTime, TimeUnit unit)
        throws InterruptedException {

    long newLeaseTime = -1;
    if (leaseTime > 0) {
        newLeaseTime = unit.toMillis(waitTime) * 2;
    }

    long time = System.currentTimeMillis();
    long remainTime = -1;
    if (waitTime > 0) {
        remainTime = unit.toMillis(waitTime);
    }
    long lockWaitTime = calcLockWaitTime(remainTime);

    // (1) 允许失败的子锁数量 = 总数 - 最少成功数
    int failedLocksLimit = failedLocksLimit();
    List<RLock> acquiredLocks = new ArrayList<>(locks.size());

    for (ListIterator<RLock> iterator = locks.listIterator(); iterator.hasNext();) {
        RLock lock = iterator.next();
        boolean lockAcquired;

        try {
            if (waitTime <= 0 && leaseTime <= 0) {
                lockAcquired = lock.tryLock(100, -1, TimeUnit.MILLISECONDS);
            } else {
                long awaitTime = Math.min(lockWaitTime, remainTime);
                lockAcquired = lock.tryLock(awaitTime, newLeaseTime,
                                            TimeUnit.MILLISECONDS);
            }
        } catch (RedisResponseTimeoutException e) {
            // Redis 超时，视为失败但仍需解锁（防止实际已成功）
            unlockInner(Collections.singletonList(lock));
            lockAcquired = false;
        } catch (Exception e) {
            lockAcquired = false;
        }

        if (lockAcquired) {
            acquiredLocks.add(lock);
        } else {
            // (2) 失败数超限，释放已获取的子锁并重试
            if (locks.size() - acquiredLocks.size() == failedLocksLimit + 1) {
                unlockInner(acquiredLocks);
                if (waitTime <= 0) {
                    return false;
                }
                failedLocksLimit++;
                acquiredLocks.clear();
                iterator = locks.listIterator();
            }
        }

        // (3) 检查总等待时间是否超限
        if (remainTime > 0) {
            remainTime -= (System.currentTimeMillis() - time);
            time = System.currentTimeMillis();
            if (remainTime <= 0) {
                unlockInner(acquiredLocks);
                return false;
            }
        }
    }
    // (4) 过半加锁成功，返回 true
    return true;
}"""

    out = h(1, "7. 红锁 RedLock")
    out += p("Redis 单机存在单点故障。RedLock 算法通过向 N 个独立 Redis 节点（N\u22653，推荐 5）"
             "分别加锁，过半成功（N/2+1）才认为加锁成功。")
    out += warn("RedLock 在 Redisson 3.24.0+ 已标记为 @Deprecated，"
                "官方建议使用 RedissonMultiLock 或基于 Redis Cluster 的单 RedissonLock。"
                "Martin Kleppmann 在论文中指出 RedLock 在系统时钟漂移场景下仍有安全问题。")
    out += design(
        "分布式共识——过半原则与 Quorum 写",
        "单节点 Redis 的主从架构存在脑裂风险：主节点加锁成功，"
        "尚未同步到从节点时主节点宕机，新从节点升主后锁信息丢失，"
        "导致两个客户端同时持有同一把锁。",
        "RedLock 借鉴分布式共识（Quorum）思想：向 N 个完全独立的 Redis 主节点分别加锁，"
        "只有严格超过半数（N/2+1）的节点加锁成功，"
        "且加锁耗时小于锁的有效期，才认为整体加锁成功。"
        "即便 N/2 个节点宕机，剩余节点的锁仍能保证互斥。",
        "核心局限：RedLock 依赖各节点时钟基本同步，且要求网络延迟远小于 TTL。"
        "Martin Kleppmann 指出，在 GC 停顿、网络分区、时钟漂移叠加时，"
        "RedLock 无法提供强安全保证。"
        "工程上推荐 Raft/ZooKeeper 等真正的共识协议用于强一致场景，"
        "RedLock 仅适合对安全要求不极端的场景。",
    )
    out += h(2, "7.1 RedissonMultiLock 加锁流程")
    out += pre(code_multilock)
    return out


def chapter8():
    qa_rows = [
        ("Redisson 如何保证加锁原子性？",
         "使用 Lua 脚本，整个 exists→hincrby→pexpire 序列在 Redis 单线程模型下"
         "原子执行，无需额外 CAS。"),
        ("为什么用 Hash 而不是 String？",
         "Hash 可在一个 Key 下存储多个 Field，"
         "天然支持可重入计数（Field=UUID:threadId，Value=次数）。"),
        ("Watchdog 怎么实现？",
         "Netty HashedWheelTimer 每隔 leaseTime/3 执行一次 renewExpirationAsync Lua 脚本，"
         "hexists 校验通过后 pexpire 续期。unlock 时调用 timeout.cancel() 停止。"),
        ("为什么不用 SETNX+EXPIRE？",
         "两步非原子，SETNX 成功后若 JVM 崩溃，锁永不过期（死锁）。"
         "Redis 2.6.12 后可用 SET key value NX PX ms 原子解决，但不支持可重入。"),
        ("非持锁线程能 unlock 吗？",
         "不能。Lua 脚本第一步 hexists 校验 UUID:threadId，不匹配返回 nil，"
         "Java 层抛 IllegalMonitorStateException。"),
        ("锁超时业务未完成怎么办？",
         "使用无参 lock()，Watchdog 自动续期，无需担心超时。"
         "若指定了 leaseTime，则锁到期后自动释放，不续期。"),
        ("Redisson 锁在 Redis 集群下安全吗？",
         "slot 内安全（同一 Key 路由到同一节点）。"
         "主从切换时若主未同步到从就宕机，新主上锁丢失，短暂出现双写。"
         "可用 RedLock 降低概率（但有时钟漂移问题）。"),
        ("tryLock 和 lock 区别？",
         "lock() 阻塞直到成功；tryLock(waitTime) 等待 waitTime 后返回 false；"
         "tryLock() 立即返回。三者底层均调用 tryAcquire。"),
    ]

    seq = """\
Thread-1 (Client A)            Redis                    Thread-2 (Client B)
     |                             |                             |
     |-- lock() ------------------>|                             |
     |   Lua: EXISTS my-lock = 0   |                             |
     |   HINCRBY my-lock uuid1:1 1 |                             |
     |   PEXPIRE my-lock 30000     |                             |
     |<-- nil (加锁成功) ----------|                             |
     |                             |                             |
     |   [scheduleExpirationRenewal]                             |
     |   Watchdog: +10s 续期       |                             |
     |                             |                             |
     |                             |-- lock() ------------------>|
     |                             |   Lua: EXISTS my-lock = 1   |
     |                             |   HEXISTS = 0 (非 uuid2:1)  |
     |                             |   return PTTL = 25000 ----->|
     |                             |   subscribe channel          |
     |                             |   latch.tryAcquire(25000ms)  |
     |                             |                             |
     |-- unlock() ---------------->|                             |
     |   Lua: HINCRBY uuid1:1 -1=0 |                             |
     |   DEL my-lock               |                             |
     |   PUBLISH channel 0         |                             |
     |<-- 1 (解锁成功) -----------|                             |
     |   cancelExpirationRenewal   |                             |
     |                             |-- onMessage(0) ------------>|
     |                             |   latch.release()            |
     |                             |                             |
     |                             |<-- lock() (重试) -----------|
     |                             |   Lua: EXISTS = 0           |
     |                             |   HINCRBY uuid2:1 1         |
     |                             |   PEXPIRE 30000             |
     |                             |-- nil (加锁成功) ----------->|"""

    out = h(1, "8. 常见面试题与知识点汇总")
    out += html_table(["问题", "简答"], qa_rows)
    out += h(2, "8.1 lock() 完整时序（ASCII 时序图）")
    out += pre(seq)
    return out


def chapter_appendix():
    cmd_rows = [
        ("HINCRBY key field delta", "Hash Field 值增加 delta（原子）",   "加锁计数+1 / 解锁计数-1"),
        ("HEXISTS key field",       "检查 Hash Field 是否存在",          "校验当前线程是否持锁"),
        ("PEXPIRE key ms",          "设置 Key 过期时间（毫秒）",          "加锁/续期"),
        ("PTTL key",                "返回 Key 剩余过期时间（毫秒）",      "加锁失败时返回等待时长"),
        ("DEL key",                 "删除 Key",                          "解锁，计数归零时删除"),
        ("PUBLISH channel msg",     "向 channel 发布消息",               "解锁后通知等待线程"),
        ("SUBSCRIBE channel",       "订阅 channel",                      "等锁时监听解锁事件"),
        ("EVAL script keys args",   "原子执行 Lua 脚本",                 "所有加/解锁核心操作"),
        ("LINDEX key 0",            "取 List 头部元素（不移除）",         "公平锁：取队首等待者"),
        ("RPUSH key val",           "List 尾部追加元素",                 "公平锁：进入等待队列"),
        ("LPOP key",                "移除并返回 List 头部",              "公平锁：出队获锁"),
        ("ZADD key score member",   "ZSet 添加元素",                     "公平锁：记录等待超时"),
        ("ZREM key member",         "ZSet 删除元素",                     "公平锁：超时清理"),
    ]
    out = h(1, "附录：关键 Redis 命令速查")
    out += html_table(["命令", "用途", "在 Redisson 中使用场景"], cmd_rows)
    out += "<hr/>\n"
    out += '<p class="comment">本文档基于 Redisson 3.x 源码整理，' \
           "源代码版权归 Redisson 项目及其贡献者所有。本文仅供学习参考，如有错误欢迎指正。</p>\n"
    return out


# ──────────────────────────────────────────────────────────────
# EPUB 构建
# ──────────────────────────────────────────────────────────────

CHAPTERS = [
    ("cover",     "封面",              chapter_cover),
    ("toc",       "目录",              chapter_toc),
    ("ch1",       "1. 整体架构",       chapter1),
    ("ch2",       "2. 加锁机制",       chapter2),
    ("ch3",       "3. 可重入计数",     chapter3),
    ("ch4",       "4. Watchdog 续期",  chapter4),
    ("ch5",       "5. 解锁机制",       chapter5),
    ("ch6",       "6. 公平锁",         chapter6),
    ("ch7",       "7. 红锁 RedLock",   chapter7),
    ("ch8",       "8. 常见面试题",     chapter8),
    ("appendix",  "附录",              chapter_appendix),
]


def build_epub():
    book = epub.EpubBook()
    book.set_identifier("redisson-lock-analysis-epub-001")
    book.set_title("Redisson 分布式锁源码解读指南")
    book.set_language("zh")
    book.add_author("ToolKitPlus/rocketmq-analysis")
    book.add_metadata(
        "DC", "description",
        "Redisson 分布式锁源码逐行注解，含每个方法的整体设计思想，适合手机 / 电子书阅读器",
    )

    # CSS
    css_item = epub.EpubItem(
        uid="style",
        file_name="style.css",
        media_type="text/css",
        content=STYLE_CSS.encode("utf-8"),
    )
    book.add_item(css_item)

    epub_chapters = []
    for uid, title, content_fn in CHAPTERS:
        body = content_fn()
        html = textwrap.dedent("""\
        <?xml version="1.0" encoding="utf-8"?>
        <!DOCTYPE html>
        <html xmlns="http://www.w3.org/1999/xhtml" xml:lang="zh">
        <head>
          <meta charset="utf-8"/>
          <title>{title}</title>
          <link rel="stylesheet" type="text/css" href="style.css"/>
        </head>
        <body>
        {body}
        </body>
        </html>
        """).format(title=title, body=body)

        chapter = epub.EpubHtml(
            title=title,
            file_name=uid + ".xhtml",
            lang="zh",
            content=html.encode("utf-8"),
        )
        chapter.add_item(css_item)
        book.add_item(chapter)
        epub_chapters.append(chapter)

    # 目录（不含封面和目录页自身）
    book.toc = tuple(
        epub.Link(uid + ".xhtml", title, uid)
        for uid, title, _ in CHAPTERS
        if uid not in ("cover", "toc")
    )

    book.add_item(epub.EpubNcx())
    book.add_item(epub.EpubNav())

    book.spine = ["nav"] + epub_chapters

    output_path = os.path.join(
        os.path.dirname(os.path.abspath(__file__)),
        "Redisson_Lock_Source_Analysis.epub",
    )
    epub.write_epub(output_path, book)
    print("EPUB generated: " + output_path)
    return output_path


if __name__ == "__main__":
    build_epub()
