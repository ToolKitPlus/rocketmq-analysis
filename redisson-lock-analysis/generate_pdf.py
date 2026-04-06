#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Redisson 分布式锁源码解析 PDF 生成脚本
生成一份适合手机查看的源码解读指南（代码字体较小，避免过度换行）
"""

import os
from reportlab.lib.pagesizes import A4
from reportlab.lib.styles import ParagraphStyle
from reportlab.lib.units import mm
from reportlab.lib import colors
from reportlab.platypus import (
    SimpleDocTemplate, Paragraph, Spacer, Preformatted,
    HRFlowable, PageBreak, Table, TableStyle
)
from reportlab.lib.enums import TA_CENTER, TA_JUSTIFY
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont


# ── 字体注册（尽量使用系统中文字体，fallback 到内置字体）──────────────────────
def register_fonts():
    """注册中文字体，优先使用系统字体"""
    font_paths = [
        # Ubuntu / Debian
        "/usr/share/fonts/truetype/noto/NotoSansCJK-Regular.ttc",
        "/usr/share/fonts/truetype/noto/NotoSerifCJK-Regular.ttc",
        "/usr/share/fonts/opentype/noto/NotoSansCJK-Regular.ttc",
        "/usr/share/fonts/opentype/noto/NotoSerifCJK-Regular.ttc",
        # CentOS / RHEL
        "/usr/share/fonts/chinese/TrueType/uming.ttf",
        "/usr/share/fonts/chinese/TrueType/ukai.ttf",
        # macOS
        "/System/Library/Fonts/PingFang.ttc",
        # Windows
        "C:/Windows/Fonts/simhei.ttf",
        "C:/Windows/Fonts/msyh.ttc",
    ]
    for path in font_paths:
        if os.path.exists(path):
            try:
                pdfmetrics.registerFont(TTFont("ChineseFont", path))
                pdfmetrics.registerFont(TTFont("ChineseFont-Bold", path))
                return "ChineseFont"
            except Exception:
                continue
    return None  # 未找到中文字体，fallback 到 Helvetica


def build_styles(cn_font):
    """构建 PDF 样式"""
    body_font = cn_font if cn_font else "Helvetica"
    bold_font = (cn_font + "-Bold") if cn_font else "Helvetica-Bold"

    styles = {}

    # 文档标题
    styles["DocTitle"] = ParagraphStyle(
        "DocTitle",
        fontName=bold_font,
        fontSize=20,
        leading=28,
        textColor=colors.HexColor("#1a237e"),
        alignment=TA_CENTER,
        spaceAfter=8,
    )

    # 章节标题 H1
    styles["H1"] = ParagraphStyle(
        "H1",
        fontName=bold_font,
        fontSize=15,
        leading=22,
        textColor=colors.HexColor("#0d47a1"),
        spaceBefore=16,
        spaceAfter=6,
        borderPad=4,
    )

    # 章节标题 H2
    styles["H2"] = ParagraphStyle(
        "H2",
        fontName=bold_font,
        fontSize=12,
        leading=18,
        textColor=colors.HexColor("#1565c0"),
        spaceBefore=12,
        spaceAfter=4,
    )

    # 章节标题 H3
    styles["H3"] = ParagraphStyle(
        "H3",
        fontName=bold_font,
        fontSize=10,
        leading=16,
        textColor=colors.HexColor("#1976d2"),
        spaceBefore=8,
        spaceAfter=3,
    )

    # 正文
    styles["Body"] = ParagraphStyle(
        "Body",
        fontName=body_font,
        fontSize=9,
        leading=14,
        alignment=TA_JUSTIFY,
        spaceBefore=2,
        spaceAfter=4,
    )

    # 代码块（关键：字体小，适合手机查看不换行）
    styles["Code"] = ParagraphStyle(
        "Code",
        fontName="Courier",
        fontSize=7,           # 代码字体较小，手机友好
        leading=10,
        backColor=colors.HexColor("#f5f5f5"),
        borderColor=colors.HexColor("#e0e0e0"),
        borderWidth=0.5,
        borderPad=6,
        spaceBefore=4,
        spaceAfter=4,
        leftIndent=4,
        rightIndent=4,
        wordWrap="CJK",
    )

    # 注释文字（灰色）
    styles["Comment"] = ParagraphStyle(
        "Comment",
        fontName=body_font,
        fontSize=8,
        leading=12,
        textColor=colors.HexColor("#555555"),
        leftIndent=8,
        spaceBefore=1,
        spaceAfter=1,
    )

    # 要点提示
    styles["Tip"] = ParagraphStyle(
        "Tip",
        fontName=body_font,
        fontSize=8.5,
        leading=13,
        textColor=colors.HexColor("#1b5e20"),
        backColor=colors.HexColor("#e8f5e9"),
        borderColor=colors.HexColor("#a5d6a7"),
        borderWidth=0.8,
        borderPad=5,
        spaceBefore=4,
        spaceAfter=4,
        leftIndent=4,
    )

    # 警告提示
    styles["Warning"] = ParagraphStyle(
        "Warning",
        fontName=body_font,
        fontSize=8.5,
        leading=13,
        textColor=colors.HexColor("#b71c1c"),
        backColor=colors.HexColor("#ffebee"),
        borderColor=colors.HexColor("#ef9a9a"),
        borderWidth=0.8,
        borderPad=5,
        spaceBefore=4,
        spaceAfter=4,
        leftIndent=4,
    )

    # 小标注
    styles["Label"] = ParagraphStyle(
        "Label",
        fontName=bold_font,
        fontSize=8,
        leading=11,
        textColor=colors.HexColor("#4a148c"),
        spaceBefore=2,
        spaceAfter=1,
    )

    return styles


def code_block(code_text, styles):
    """将代码文本转换为 Preformatted 段落（保留缩进和换行）"""
    return Preformatted(code_text, styles["Code"])


def h(text, level, styles):
    """生成标题段落"""
    key = f"H{level}"
    return Paragraph(text, styles[key])


def p(text, styles, style_key="Body"):
    """生成正文段落"""
    return Paragraph(text, styles[style_key])


def tip(text, styles):
    return Paragraph(f"[TIP] {text}", styles["Tip"])


def warn(text, styles):
    return Paragraph(f"[WARNING] {text}", styles["Warning"])


def sep(styles):
    return HRFlowable(width="100%", thickness=0.5, color=colors.HexColor("#bdbdbd"), spaceAfter=6, spaceBefore=6)


# ════════════════════════════════════════════════════════════════
# 文档内容构建
# ════════════════════════════════════════════════════════════════

def build_content(styles):
    story = []

    # ── 封面 ─────────────────────────────────────────────────────
    story.append(Spacer(1, 30 * mm))
    story.append(Paragraph("Redisson 分布式锁源码解读指南", styles["DocTitle"]))
    story.append(Spacer(1, 4 * mm))
    story.append(Paragraph("-- 加锁 · 解锁 · Watchdog 逐行注解 --", ParagraphStyle(
        "subtitle", fontName="Helvetica", fontSize=11, alignment=TA_CENTER,
        textColor=colors.HexColor("#546e7a"), leading=18,
    )))
    story.append(Spacer(1, 6 * mm))
    story.append(Paragraph("版本参考: Redisson 3.x (基于 Redis 单机/集群)", ParagraphStyle(
        "ver", fontName="Helvetica", fontSize=8, alignment=TA_CENTER,
        textColor=colors.grey, leading=12,
    )))
    story.append(PageBreak())

    # ── 目录 ─────────────────────────────────────────────────────
    story.append(h("目录", 1, styles))
    toc_data = [
        ["章节", "主要内容"],
        ["1. 整体架构", "RedissonLock 类图、继承关系、核心字段"],
        ["2. 加锁机制", "lock() -> tryAcquire -> Lua 脚本原子加锁"],
        ["3. 可重入计数", "HINCRBY 实现可重入、Hash 数据结构"],
        ["4. Watchdog 续期", "看门狗原理、renewExpiration 定时任务"],
        ["5. 解锁机制", "unlock() -> Lua 脚本原子解锁 -> Pub/Sub 通知"],
        ["6. 公平锁", "RedissonFairLock 队列排队加锁"],
        ["7. 红锁 RedLock", "多节点加锁、过半原则"],
        ["8. 常见面试题", "与 SETNX 方案对比、ABA 问题分析"],
    ]
    toc_table = Table(toc_data, colWidths=[55 * mm, 115 * mm])
    toc_table.setStyle(TableStyle([
        ("BACKGROUND", (0, 0), (-1, 0), colors.HexColor("#0d47a1")),
        ("TEXTCOLOR", (0, 0), (-1, 0), colors.white),
        ("FONTSIZE", (0, 0), (-1, 0), 9),
        ("FONTSIZE", (0, 1), (-1, -1), 8),
        ("ROWBACKGROUNDS", (0, 1), (-1, -1), [colors.white, colors.HexColor("#e8eaf6")]),
        ("GRID", (0, 0), (-1, -1), 0.4, colors.HexColor("#9fa8da")),
        ("LEFTPADDING", (0, 0), (-1, -1), 6),
        ("TOPPADDING", (0, 0), (-1, -1), 4),
        ("BOTTOMPADDING", (0, 0), (-1, -1), 4),
        ("VALIGN", (0, 0), (-1, -1), "MIDDLE"),
    ]))
    story.append(toc_table)
    story.append(PageBreak())

    # ════════════════════════════════════════════════════════════
    # 第 1 章：整体架构
    # ════════════════════════════════════════════════════════════
    story.append(h("1. 整体架构", 1, styles))
    story.append(p(
        "Redisson 锁体系以 RedissonBaseLock 为抽象父类，向上实现 "
        "RLock（继承自 java.util.concurrent.locks.Lock）接口，"
        "向下派生出多种锁实现：", styles
    ))

    arch_data = [
        ["类/接口", "说明"],
        ["RLock (interface)", "顶层锁接口，扩展 Lock，增加 tryLock(time,unit) 等方法"],
        ["RedissonBaseLock", "抽象基类，实现 Watchdog 逻辑、线程 ID 管理"],
        ["RedissonLock", "普通可重入分布式锁（最常用）"],
        ["RedissonFairLock", "公平锁，Redis List 维护等待队列"],
        ["RedissonReadLock", "读写锁中的读锁"],
        ["RedissonWriteLock", "读写锁中的写锁"],
        ["RedissonMultiLock", "联锁，要求所有锁均加锁成功"],
        ["RedissonRedLock", "红锁，要求过半节点加锁成功（已 deprecated）"],
    ]
    arch_table = Table(arch_data, colWidths=[60 * mm, 110 * mm])
    arch_table.setStyle(TableStyle([
        ("BACKGROUND", (0, 0), (-1, 0), colors.HexColor("#1565c0")),
        ("TEXTCOLOR", (0, 0), (-1, 0), colors.white),
        ("FONTSIZE", (0, 0), (-1, 0), 8.5),
        ("FONTSIZE", (0, 1), (-1, -1), 7.5),
        ("ROWBACKGROUNDS", (0, 1), (-1, -1), [colors.white, colors.HexColor("#e3f2fd")]),
        ("GRID", (0, 0), (-1, -1), 0.4, colors.HexColor("#90caf9")),
        ("LEFTPADDING", (0, 0), (-1, -1), 5),
        ("TOPPADDING", (0, 0), (-1, -1), 3),
        ("BOTTOMPADDING", (0, 0), (-1, -1), 3),
        ("VALIGN", (0, 0), (-1, -1), "MIDDLE"),
    ]))
    story.append(arch_table)
    story.append(Spacer(1, 4 * mm))

    story.append(h("1.1 RedissonBaseLock 核心字段", 2, styles))
    story.append(code_block(
"""// RedissonBaseLock.java (部分字段)

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
}""", styles))
    story.append(tip("UUID 在 Redisson 客户端启动时生成，每个 JVM 实例唯一，配合 threadId 共同标识锁的持有者。", styles))

    story.append(h("1.2 Redis 中锁的数据结构", 2, styles))
    story.append(p(
        "Redisson 普通锁使用 Redis Hash 存储，Key 为锁名，Field 为 "
        "UUID:threadId，Value 为可重入次数：", styles
    ))
    story.append(code_block(
"""# Redis 中锁的存储形式（HGETALL my-lock）
my-lock (Hash)
  +-- field: "a1b2c3d4-...-uuid:1"   value: 1   # 线程1持锁，重入次数=1
  +-- field: "a1b2c3d4-...-uuid:1"   value: 2   # 同一线程再次加锁，重入次数=2

# TTL 由 PEXPIRE 单独设置（单位：毫秒）
PEXPIRE my-lock 30000""", styles))
    story.append(PageBreak())

    # ════════════════════════════════════════════════════════════
    # 第 2 章：加锁机制
    # ════════════════════════════════════════════════════════════
    story.append(h("2. 加锁机制", 1, styles))
    story.append(p(
        "加锁入口有三个：lock()（阻塞永久等待）、"
        "lock(leaseTime, unit)（阻塞指定 leaseTime）、"
        "tryLock(waitTime, leaseTime, unit)（带超时的非阻塞）。"
        "三者最终均汇聚到 tryAcquire。", styles
    ))

    story.append(h("2.1 lock() 方法调用链", 2, styles))
    story.append(code_block(
"""// RedissonLock.java

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
            // 再次尝试加锁
            ttl = tryAcquire(-1, leaseTime, unit, threadId);

            // 成功则退出
            if (ttl == null) {
                break;
            }

            // (7) 使用 Semaphore 阻塞等待解锁通知，最多等待 ttl 毫秒
            //     当其他线程 unlock() 后会 publish 解锁消息，唤醒此处
            if (ttl >= 0) {
                try {
                    // getLatch() 返回 Semaphore，等待锁释放信号
                    future.getNow().getLatch().tryAcquire(ttl, TimeUnit.MILLISECONDS);
                } catch (InterruptedException e) {
                    if (interruptibly) throw e;
                }
            } else {
                // ttl < 0 说明持有者已过期（理论上不常见），直接等
                future.getNow().getLatch().acquire();
            }
        }
    } finally {
        // (8) 取消订阅解锁通知
        unsubscribe(future, threadId);
    }
}""", styles))
    story.append(tip("subscribe/unsubscribe 使用 Redis Pub/Sub，channel 名为 redisson_lock__channel:{lockName}。等锁期间不轮询 Redis，资源效率更高。", styles))

    story.append(h("2.2 tryAcquire — 同步转异步", 2, styles))
    story.append(code_block(
"""// RedissonLock.java

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
        // (2) 未指定 leaseTime（即 lock() 调用）：先用 internalLockLeaseTime 加锁
        //     加锁成功后再启动 Watchdog 续期
        ttlRemainingFuture = tryLockInnerAsync(waitTime,
                                internalLockLeaseTime,
                                TimeUnit.MILLISECONDS, threadId, LOCK_SCRIPT);
    }

    // (3) 注册回调，处理加锁结果
    CompletionStage<Long> f = ttlRemainingFuture.thenApply(ttlRemaining -> {
        // ttlRemaining == null 代表加锁成功
        if (ttlRemaining == null) {
            if (leaseTime > 0) {
                // 指定了 leaseTime，记录到 internalLockLeaseTime（续期用）
                internalLockLeaseTime = unit.toMillis(leaseTime);
            } else {
                // 未指定 leaseTime，启动 Watchdog
                scheduleExpirationRenewal(threadId);
            }
        }
        return ttlRemaining;
    });
    return new CompletableFutureWrapper<>(f);
}""", styles))

    story.append(h("2.3 tryLockInnerAsync — Lua 原子加锁", 2, styles))
    story.append(p(
        "真正执行 Redis 操作的方法。使用 Lua 脚本保证检查+设置的原子性，"
        "避免 SETNX + EXPIRE 两步之间的竞态条件。", styles
    ))
    story.append(code_block(
"""// RedissonLock.java

<T> RFuture<T> tryLockInnerAsync(long waitTime, long leaseTime,
                                   TimeUnit unit, long threadId,
                                   RedisStrictCommand<T> command) {
    // 调用 evalWriteAsync 在 Redis 上执行 Lua 脚本
    // KEYS[1]  = 锁名（如 "my-lock"）
    // ARGV[1]  = 过期时间（毫秒）
    // ARGV[2]  = lockName = UUID + ":" + threadId
    return evalWriteAsync(getRawName(), LongCodec.INSTANCE, command,

        // Lua 脚本（原子执行，不会被其他命令插入）
        // 第 1 步：检查锁是否存在
        "if (redis.call('exists', KEYS[1]) == 0) then " +
            // 锁不存在：创建 Hash，Field=lockName，Value=1（首次加锁）
            "   redis.call('hincrby', KEYS[1], ARGV[2], 1); " +
            // 设置过期时间（防止死锁）
            "   redis.call('pexpire', KEYS[1], ARGV[1]); " +
            // 返回 nil 代表加锁成功
            "   return nil; " +
        "end; " +

        // 第 2 步：锁已存在，检查是否当前线程持有（可重入）
        "if (redis.call('hexists', KEYS[1], ARGV[2]) == 1) then " +
            // 可重入：重入计数 +1
            "   redis.call('hincrby', KEYS[1], ARGV[2], 1); " +
            // 刷新过期时间
            "   redis.call('pexpire', KEYS[1], ARGV[1]); " +
            // 返回 nil 代表加锁成功（重入）
            "   return nil; " +
        "end; " +

        // 第 3 步：锁被他人持有，返回锁的剩余过期时间（毫秒）
        "return redis.call('pttl', KEYS[1]);",

        // 参数
        Collections.singletonList(getRawName()),   // KEYS[1]
        unit.toMillis(leaseTime),                  // ARGV[1]
        getLockName(threadId));                    // ARGV[2] = UUID:threadId
}""", styles))
    story.append(tip(
        "Lua 脚本在 Redis 中是原子执行的。整个 exists->hincrby->pexpire 序列不会被其他命令打断，"
        "因此不需要额外的乐观锁（CAS）。", styles
    ))
    story.append(warn(
        "若调用 lock(leaseTime, unit) 指定了 leaseTime，Watchdog 不会启动。"
        "leaseTime 到期后，即使业务未完成锁也会自动释放，存在安全风险。"
        "推荐使用无参 lock() 配合 Watchdog。", styles
    ))
    story.append(PageBreak())

    # ════════════════════════════════════════════════════════════
    # 第 3 章：可重入计数
    # ════════════════════════════════════════════════════════════
    story.append(h("3. 可重入计数详解", 1, styles))
    story.append(p(
        "Redisson 分布式锁支持同一线程多次加锁（可重入），"
        "依靠 Redis Hash 的 HINCRBY 命令实现计数。", styles
    ))
    story.append(h("3.1 加锁时计数 +1", 2, styles))
    story.append(code_block(
"""-- Lua 脚本片段（加锁时）

-- 第一次加锁：hincrby my-lock "uuid:1" 1  -> value = 1
-- 第二次加锁（重入）：hincrby my-lock "uuid:1" 1  -> value = 2
redis.call('hincrby', KEYS[1], ARGV[2], 1)
redis.call('pexpire', KEYS[1], ARGV[1])

-- Redis 中结果：
-- HGETALL my-lock -> 1) "uuid:1"  2) "2"  （重入 2 次）""", styles))

    story.append(h("3.2 解锁时计数 -1", 2, styles))
    story.append(code_block(
"""-- Lua 脚本片段（解锁时，详见第5章）

-- HINCRBY 减 1
local counter = redis.call('hincrby', KEYS[1], ARGV[3], -1)

if (counter > 0) then
    -- 重入计数 > 0，还有外层锁未释放，只刷新过期时间
    redis.call('pexpire', KEYS[1], ARGV[2])
    return 0   -- 0 = 锁未完全释放
else
    -- 计数归零：删除整个 Hash Key，锁完全释放
    redis.call('del', KEYS[1])
    -- 通过 Pub/Sub 通知等待的线程
    redis.call('publish', KEYS[2], ARGV[1])
    return 1   -- 1 = 锁已完全释放
end""", styles))

    story.append(h("3.3 可重入示例", 2, styles))
    story.append(code_block(
"""RLock lock = redisson.getLock("my-lock");

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
}""", styles))
    story.append(tip("可重入次数必须与 lock 次数精确匹配，否则锁将提前/无法释放。", styles))
    story.append(PageBreak())

    # ════════════════════════════════════════════════════════════
    # 第 4 章：Watchdog 续期
    # ════════════════════════════════════════════════════════════
    story.append(h("4. Watchdog（看门狗）续期机制", 1, styles))
    story.append(p(
        "当使用无参 lock() 时，Redisson 会启动一个后台定时任务，"
        "每隔 leaseTime/3（默认 10 秒）自动刷新锁的过期时间，"
        "防止业务耗时超过 leaseTime 导致锁提前释放。", styles
    ))

    story.append(h("4.1 scheduleExpirationRenewal — 注册 Watchdog", 2, styles))
    story.append(code_block(
"""// RedissonBaseLock.java

protected void scheduleExpirationRenewal(long threadId) {
    // (1) 创建/获取 ExpirationEntry（每个锁名对应一个）
    ExpirationEntry entry = new ExpirationEntry();
    ExpirationEntry oldEntry =
        EXPIRATION_RENEWAL_MAP.putIfAbsent(getEntryName(), entry);

    if (oldEntry != null) {
        // 同一个 JVM 内，同一个锁被同一线程再次加锁（重入）
        // 只需在已有 entry 中记录当前 threadId，不重复注册定时任务
        oldEntry.addThreadId(threadId);
    } else {
        // 首次加锁，注册当前 threadId，并启动续期定时任务
        entry.addThreadId(threadId);
        try {
            renewExpiration();    // <-- 真正注册定时任务
        } finally {
            // 防止在注册期间线程被中断导致 entry 残留
            if (Thread.currentThread().isInterrupted()) {
                cancelExpirationRenewal(threadId);
            }
        }
    }
}""", styles))

    story.append(h("4.2 renewExpiration — 定时续期任务", 2, styles))
    story.append(code_block(
"""// RedissonBaseLock.java

private void renewExpiration() {
    ExpirationEntry ee = EXPIRATION_RENEWAL_MAP.get(getEntryName());
    if (ee == null) {
        // 锁已被释放，不再续期
        return;
    }

    // (1) 使用 Netty HashedWheelTimer 调度延迟任务
    //     延迟时间 = internalLockLeaseTime / 3 （默认 30000/3 = 10000 ms）
    Timeout task = commandExecutor.getServiceManager().newTimeout(
        new TimerTask() {
            @Override
            public void run(Timeout timeout) throws Exception {

                // (2) 检查 entry 是否还在 Map 中（锁是否已释放）
                ExpirationEntry ent =
                    EXPIRATION_RENEWAL_MAP.get(getEntryName());
                if (ent == null) {
                    return;   // 锁已解除，停止续期
                }

                // (3) 获取持锁线程 ID（最早进入的那个线程）
                Long threadId = ent.getFirstThreadId();
                if (threadId == null) {
                    return;
                }

                // (4) 执行续期 Lua 脚本（异步）
                CompletionStage<Boolean> future =
                    renewExpirationAsync(threadId);

                future.whenComplete((res, e) -> {
                    if (e != null) {
                        // 续期失败（Redis 连接异常等），打印错误，停止续期
                        log.error("Can't update lock {} expiration",
                                  getRawName(), e);
                        EXPIRATION_RENEWAL_MAP.remove(getEntryName());
                        return;
                    }
                    if (res) {
                        // (5) 续期成功，递归调用自身，形成循环续期
                        renewExpiration();
                    } else {
                        // 续期返回 false，说明锁已不存在（被其他原因删除）
                        cancelExpirationRenewal(null);
                    }
                });
            }
        },
        // 延迟时间（毫秒）= leaseTime / 3
        internalLockLeaseTime / 3, TimeUnit.MILLISECONDS
    );

    // (6) 将 Task 引用保存到 entry，以便 unlock 时能取消
    ee.setTimeout(task);
}""", styles))

    story.append(h("4.3 renewExpirationAsync — 续期 Lua 脚本", 2, styles))
    story.append(code_block(
"""// RedissonBaseLock.java

protected CompletionStage<Boolean> renewExpirationAsync(long threadId) {
    return evalWriteAsync(getRawName(), LongCodec.INSTANCE,
        RedisCommands.EVAL_BOOLEAN,

        // Lua 脚本
        // 检查锁是否仍由当前线程持有（避免误续他人的锁）
        "if (redis.call('hexists', KEYS[1], ARGV[2]) == 1) then " +
            // 重置过期时间为 leaseTime（30 秒）
            "   redis.call('pexpire', KEYS[1], ARGV[1]); " +
            // 返回 1（true）代表续期成功
            "   return 1; " +
        "end; " +
        // 锁不再由本线程持有，返回 0（false）
        "return 0;",

        // 参数
        Collections.singletonList(getRawName()),  // KEYS[1] = 锁名
        internalLockLeaseTime,                    // ARGV[1] = leaseTime（ms）
        getLockName(threadId));                   // ARGV[2] = UUID:threadId
}""", styles))
    story.append(tip(
        "Watchdog 的续期判断基于 hexists，只有锁仍由本线程持有时才续期。"
        "即使 JVM 假死（GC Stop-The-World）导致 Watchdog 超过 leaseTime 未跑，"
        "锁也会自然过期，不会永久阻塞其他节点。", styles
    ))
    story.append(warn(
        "Watchdog 依赖 Netty 线程池，若应用整体卡死（如 OOM），续期线程也将停止，"
        "30 秒后锁会自动释放。这是一种兜底机制，不能依赖 Watchdog 保证绝对安全。", styles
    ))

    story.append(h("4.4 cancelExpirationRenewal — 取消 Watchdog", 2, styles))
    story.append(code_block(
"""// RedissonBaseLock.java -- 解锁时调用

protected void cancelExpirationRenewal(Long threadId) {
    ExpirationEntry task = EXPIRATION_RENEWAL_MAP.get(getEntryName());
    if (task == null) {
        return;
    }

    if (threadId != null) {
        // (1) 从 entry 中移除当前 threadId（重入场景）
        task.removeThreadId(threadId);
    }

    // (2) 若 entry 中没有更多线程持有（或 threadId==null 表示强制取消）
    if (threadId == null || task.hasNoThreads()) {
        // 取消 Timeout 定时任务（调用 HashedWheelTimer cancel）
        Timeout timeout = task.getTimeout();
        if (timeout != null) {
            timeout.cancel();
        }
        // 从全局 Map 中移除，彻底停止续期
        EXPIRATION_RENEWAL_MAP.remove(getEntryName());
    }
}""", styles))
    story.append(PageBreak())

    # ════════════════════════════════════════════════════════════
    # 第 5 章：解锁机制
    # ════════════════════════════════════════════════════════════
    story.append(h("5. 解锁机制", 1, styles))
    story.append(p(
        "解锁入口为 unlock()，核心也是一段 Lua 脚本，"
        "保证计数递减、Key 删除、Pub/Sub 通知的原子性。", styles
    ))

    story.append(h("5.1 unlock() 调用链", 2, styles))
    story.append(code_block(
"""// RedissonLock.java

@Override
public void unlock() {
    try {
        // 同步等待异步解锁完成
        get(unlockAsync(Thread.currentThread().getId()));
    } catch (RedisException e) {
        // 解锁时可能抛出 "attempt to unlock lock, not locked by current thread"
        // 这是非法解锁，向上层抛出
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
        // (2) 无论解锁成功与否，先取消 Watchdog
        cancelExpirationRenewal(threadId);

        if (e != null) {
            // (3) Redis 通信异常，向上抛出
            throw commandExecutor.convertException(e);
        }

        if (opStatus == null) {
            // (4) opStatus==null 说明当前线程根本没持有这把锁
            //     抛出 IllegalMonitorStateException（类似 synchronized 非法解锁）
            IllegalMonitorStateException cause =
                new IllegalMonitorStateException(
                    "attempt to unlock lock, not locked by current thread node id: "
                    + id + " thread-id: " + threadId);
            throw new CompletionException(cause);
        }
        return null;
    });

    return new CompletableFutureWrapper<>(f);
}""", styles))

    story.append(h("5.2 unlockInnerAsync — Lua 原子解锁", 2, styles))
    story.append(code_block(
"""// RedissonLock.java

protected RFuture<Boolean> unlockInnerAsync(long threadId) {
    // KEYS[1] = 锁名
    // KEYS[2] = Pub/Sub channel = "redisson_lock__channel:{lockName}"
    // ARGV[1] = 解锁消息（固定值 0）
    // ARGV[2] = leaseTime（续期/解锁后过期时间）
    // ARGV[3] = lockName = UUID:threadId
    return evalWriteAsync(getRawName(), LongCodec.INSTANCE,
        RedisCommands.EVAL_BOOLEAN,

        // Lua 脚本（原子执行）
        // 第 1 步：检查当前线程是否持有锁（防止误解锁）
        "if (redis.call('hexists', KEYS[1], ARGV[3]) == 0) then " +
            // 当前线程未持有此锁，返回 nil（调用方抛 IllegalMonitorStateException）
            "   return nil; " +
        "end; " +

        // 第 2 步：重入计数 -1
        "local counter = redis.call('hincrby', KEYS[1], ARGV[3], -1); " +

        // 第 3 步：判断计数值
        "if (counter > 0) then " +
            // 仍有重入层级，锁未完全释放，刷新过期时间
            "   redis.call('pexpire', KEYS[1], ARGV[2]); " +
            // 返回 0（锁未完全释放）
            "   return 0; " +
        "else " +
            // 计数归零，彻底删除锁 Key
            "   redis.call('del', KEYS[1]); " +
            // 通过 Pub/Sub 广播解锁消息，唤醒所有等待线程
            "   redis.call('publish', KEYS[2], ARGV[1]); " +
            // 返回 1（锁完全释放）
            "   return 1; " +
        "end; " +
        // 未预期的情况，返回 nil
        "return nil;",

        // 参数传入
        Arrays.asList(getRawName(), getChannelName()),  // KEYS
        LockPubSub.UNLOCK_MESSAGE,                      // ARGV[1] = 0
        internalLockLeaseTime,                          // ARGV[2]
        getLockName(threadId));                         // ARGV[3]
}""", styles))

    story.append(h("5.3 Pub/Sub 通知等待线程", 2, styles))
    story.append(code_block(
"""// LockPubSub.java（节选）

public class LockPubSub extends PublishSubscribeService {

    // 解锁消息常量
    public static final Long UNLOCK_MESSAGE     = 0L;  // 普通解锁
    public static final Long READ_UNLOCK_MESSAGE = 1L; // 读锁解锁（读写锁用）

    @Override
    protected void onMessage(RedissonLockEntry value, Long message) {
        if (message.equals(UNLOCK_MESSAGE)) {
            // 收到解锁通知：释放 Semaphore，唤醒 lock() 中等待的线程
            Listener listener = value.getListeners().poll();
            if (listener != null) {
                listener.onEvent(value);
            } else {
                // 无监听器时，直接 release Semaphore（允许等待线程重试加锁）
                value.getLatch().release();
            }
        } else if (message.equals(READ_UNLOCK_MESSAGE)) {
            // 读写锁场景
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
}""", styles))
    story.append(tip(
        "Pub/Sub channel 名格式：redisson_lock__channel:{lockName}。"
        "一个 channel 对应一把锁，所有等待该锁的线程/节点都订阅此 channel。"
        "解锁时只 publish 一次消息，但等待队列中的线程会轮流被唤醒（Semaphore 每次只 release 1）。", styles
    ))
    story.append(PageBreak())

    # ════════════════════════════════════════════════════════════
    # 第 6 章：公平锁
    # ════════════════════════════════════════════════════════════
    story.append(h("6. 公平锁 RedissonFairLock", 1, styles))
    story.append(p(
        "普通 RedissonLock 不保证加锁顺序（等待线程随机竞争）。"
        "RedissonFairLock 通过 Redis List 维护等待队列，"
        "确保先到先得。", styles
    ))

    story.append(h("6.1 数据结构", 2, styles))
    story.append(code_block(
"""# 公平锁使用两个 Key：
# 1. Hash Key（与普通锁相同）：存储持锁者
my-fair-lock (Hash)
  +-- "uuid:1" -> 1

# 2. List Key（等待队列）：存储等待的线程标识
redisson_lock_queue:{my-fair-lock} (List)
  +-- 0) "uuid:2"    <- 队首（最先等待，下一个获得锁）
  +-- 1) "uuid:3"

# 3. ZSet Key（超时记录）：记录每个等待者的超时时间戳
redisson_lock_timeout:{my-fair-lock} (ZSet)
  +-- "uuid:2" -> 1700000010000   <- score = 超时时间戳（毫秒）
  +-- "uuid:3" -> 1700000020000""", styles))

    story.append(h("6.2 公平锁 Lua 加锁脚本（核心逻辑）", 2, styles))
    story.append(code_block(
"""-- RedissonFairLock 加锁 Lua 脚本（简化版）

-- (1) 清理已超时的等待者（防止死等）
while true do
    local firstThreadId = redis.call('lindex', KEYS[2], 0)  -- 取队首
    if firstThreadId == false then break end

    local timeout = tonumber(redis.call('zscore', KEYS[3], firstThreadId))
    if timeout <= tonumber(ARGV[4]) then  -- ARGV[4] = 当前时间戳
        -- 已超时，从队列和 ZSet 中移除
        redis.call('zrem', KEYS[3], firstThreadId)
        redis.call('lpop', KEYS[2])
    else
        break
    end
end

-- (2) 尝试加锁（同普通锁逻辑，但增加了队首判断）
if (redis.call('exists', KEYS[1]) == 0) then
    local firstThreadId = redis.call('lindex', KEYS[2], 0)
    -- 仅当队列为空 OR 队首就是当前线程时，才允许加锁
    if firstThreadId == false or firstThreadId == ARGV[2] then
        -- 从队列和 ZSet 中移除自己（不再是等待者）
        redis.call('lpop', KEYS[2])
        redis.call('zrem', KEYS[3], ARGV[2])
        -- 加锁
        redis.call('hset', KEYS[1], ARGV[2], 1)
        redis.call('pexpire', KEYS[1], ARGV[1])
        return nil
    end
end

-- (3) 加锁失败：将当前线程加入等待队列
if redis.call('zscore', KEYS[3], ARGV[2]) == false then
    redis.call('rpush', KEYS[2], ARGV[2])  -- 加入队尾
    -- 记录超时时间 = 当前时间 + 等待超时
    redis.call('zadd', KEYS[3], tonumber(ARGV[3]) + tonumber(ARGV[4]), ARGV[2])
end

-- (4) 返回剩余等待时间
local ttl = redis.call('pttl', KEYS[1])
return ttl""", styles))
    story.append(PageBreak())

    # ════════════════════════════════════════════════════════════
    # 第 7 章：红锁
    # ════════════════════════════════════════════════════════════
    story.append(h("7. 红锁 RedLock", 1, styles))
    story.append(p(
        "Redis 单机存在单点故障。RedLock 算法（Martin Kleppmann 分析，Antirez 提出）"
        "通过向 N 个独立 Redis 节点（N>=3，推荐 5）分别加锁，"
        "过半成功（N/2+1）才认为加锁成功。", styles
    ))
    story.append(warn(
        "RedLock 在 Redisson 3.24.0+ 已标记为 @Deprecated，"
        "官方建议使用 RedissonMultiLock 或基于 Redis Cluster 的单 RedissonLock。"
        "Martin Kleppmann 在论文中指出 RedLock 在系统时钟漂移场景下仍有安全问题。", styles
    ))

    story.append(h("7.1 RedissonMultiLock 加锁流程", 2, styles))
    story.append(code_block(
"""// RedissonMultiLock.java（简化）

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
            // Redis 超时，视为加锁失败，但仍需解锁（防止实际加锁成功）
            unlockInner(Collections.singletonList(lock));
            lockAcquired = false;
        } catch (Exception e) {
            lockAcquired = false;
        }

        if (lockAcquired) {
            acquiredLocks.add(lock);
        } else {
            // (2) 失败数超过允许值，释放所有已加锁的子锁
            if (locks.size() - acquiredLocks.size() == failedLocksLimit + 1) {
                unlockInner(acquiredLocks);
                if (waitTime <= 0) {
                    return false;
                }
                failedLocksLimit++;
                acquiredLocks.clear();
                iterator = locks.listIterator(); // 重新遍历
            }
        }

        // (3) 检查总等待时间是否已超限
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
}""", styles))
    story.append(PageBreak())

    # ════════════════════════════════════════════════════════════
    # 第 8 章：常见面试题
    # ════════════════════════════════════════════════════════════
    story.append(h("8. 常见面试题与知识点汇总", 1, styles))

    qa_data = [
        ["问题", "简答"],
        ["Redisson 如何保证加锁原子性？",
         "使用 Lua 脚本，整个 exists->hincrby->pexpire 序列在 Redis 单线程模型下原子执行，无需额外 CAS。"],
        ["为什么用 Hash 而不是 String？",
         "Hash 可在一个 Key 下存储多个 Field，天然支持可重入计数（Field=UUID:threadId，Value=次数）。"],
        ["Watchdog 怎么实现？",
         "Netty HashedWheelTimer 每隔 leaseTime/3 执行一次 renewExpirationAsync Lua 脚本，"
         "hexists 校验通过后 pexpire 续期。unlock 时调用 timeout.cancel() 停止。"],
        ["为什么不用 SETNX+EXPIRE？",
         "两步非原子，SETNX 成功后若 JVM 崩溃，锁永不过期（死锁）。"
         "Redis 2.6.12 后可用 SET key value NX PX ms 原子解决，但不支持可重入。"],
        ["非持锁线程能 unlock 吗？",
         "不能。Lua 脚本第一步 hexists 校验 UUID:threadId，不匹配返回 nil，"
         "Java 层抛 IllegalMonitorStateException。"],
        ["锁超时业务未完成怎么办？",
         "使用无参 lock()，Watchdog 自动续期，无需担心超时。\n"
         "若指定了 leaseTime，则锁到期后自动释放，不续期。"],
        ["Redisson 锁在 Redis 集群下安全吗？",
         "slot 内安全（同一 Key 路由到同一节点）。主从切换时若主未同步到从就宕机，"
         "新主上锁丢失，短暂出现双写。可用 RedLock 降低概率（但有时钟漂移问题）。"],
        ["tryLock 和 lock 区别？",
         "lock() 阻塞直到成功；tryLock(waitTime) 等待 waitTime 后返回 false；"
         "tryLock() 立即返回。三者底层均调用 tryAcquire。"],
    ]
    qa_table = Table(qa_data, colWidths=[62 * mm, 108 * mm])
    qa_table.setStyle(TableStyle([
        ("BACKGROUND", (0, 0), (-1, 0), colors.HexColor("#4a148c")),
        ("TEXTCOLOR", (0, 0), (-1, 0), colors.white),
        ("FONTSIZE", (0, 0), (-1, 0), 9),
        ("FONTSIZE", (0, 1), (-1, -1), 7.5),
        ("ROWBACKGROUNDS", (0, 1), (-1, -1), [colors.white, colors.HexColor("#f3e5f5")]),
        ("GRID", (0, 0), (-1, -1), 0.4, colors.HexColor("#ce93d8")),
        ("LEFTPADDING", (0, 0), (-1, -1), 5),
        ("TOPPADDING", (0, 0), (-1, -1), 4),
        ("BOTTOMPADDING", (0, 0), (-1, -1), 4),
        ("VALIGN", (0, 0), (-1, -1), "TOP"),
        ("FONTNAME", (0, 1), (0, -1), "Helvetica-Bold"),
    ]))
    story.append(qa_table)
    story.append(Spacer(1, 6 * mm))

    # ── 完整时序图（ASCII）─────────────────────────────────────────
    story.append(h("8.1 lock() 完整时序（ASCII 时序图）", 2, styles))
    story.append(code_block(
"""Thread-1 (Client A)            Redis                    Thread-2 (Client B)
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
     |                             |-- nil (加锁成功) ----------->|""", styles))
    story.append(PageBreak())

    # ── 附录 ─────────────────────────────────────────────────────
    story.append(h("附录：关键 Redis 命令速查", 1, styles))
    cmd_data = [
        ["命令", "用途", "在 Redisson 中使用场景"],
        ["HINCRBY key field delta", "Hash Field 值增加 delta（原子）", "加锁计数+1 / 解锁计数-1"],
        ["HEXISTS key field", "检查 Hash Field 是否存在", "校验当前线程是否持锁"],
        ["PEXPIRE key ms", "设置 Key 过期时间（毫秒）", "加锁/续期"],
        ["PTTL key", "返回 Key 剩余过期时间（毫秒）", "加锁失败时返回等待时长"],
        ["DEL key", "删除 Key", "解锁，计数归零时删除"],
        ["PUBLISH channel msg", "向 channel 发布消息", "解锁后通知等待线程"],
        ["SUBSCRIBE channel", "订阅 channel", "等锁时监听解锁事件"],
        ["EVAL script keys args", "原子执行 Lua 脚本", "所有加/解锁核心操作"],
        ["LINDEX key 0", "取 List 头部元素（不移除）", "公平锁：取队首等待者"],
        ["RPUSH key val", "List 尾部追加元素", "公平锁：进入等待队列"],
        ["LPOP key", "移除并返回 List 头部", "公平锁：出队获锁"],
        ["ZADD key score member", "ZSet 添加元素", "公平锁：记录等待超时"],
        ["ZREM key member", "ZSet 删除元素", "公平锁：超时清理"],
    ]
    cmd_table = Table(cmd_data, colWidths=[52 * mm, 58 * mm, 60 * mm])
    cmd_table.setStyle(TableStyle([
        ("BACKGROUND", (0, 0), (-1, 0), colors.HexColor("#004d40")),
        ("TEXTCOLOR", (0, 0), (-1, 0), colors.white),
        ("FONTSIZE", (0, 0), (-1, 0), 8),
        ("FONTSIZE", (0, 1), (-1, -1), 7),
        ("FONTNAME", (0, 0), (-1, 0), "Helvetica-Bold"),
        ("FONTNAME", (0, 1), (0, -1), "Courier"),
        ("ROWBACKGROUNDS", (0, 1), (-1, -1), [colors.white, colors.HexColor("#e0f2f1")]),
        ("GRID", (0, 0), (-1, -1), 0.4, colors.HexColor("#80cbc4")),
        ("LEFTPADDING", (0, 0), (-1, -1), 4),
        ("TOPPADDING", (0, 0), (-1, -1), 3),
        ("BOTTOMPADDING", (0, 0), (-1, -1), 3),
        ("VALIGN", (0, 0), (-1, -1), "MIDDLE"),
    ]))
    story.append(cmd_table)
    story.append(Spacer(1, 6 * mm))

    story.append(sep(styles))
    story.append(p(
        "本文档基于 Redisson 3.x 源码整理，源代码版权归 Redisson 项目及其贡献者所有。"
        "本文仅供学习参考，如有错误欢迎指正。", styles, "Comment"
    ))

    return story


# ════════════════════════════════════════════════════════════════
# 主函数
# ════════════════════════════════════════════════════════════════

def main():
    output_path = os.path.join(
        os.path.dirname(os.path.abspath(__file__)),
        "Redisson_Lock_Source_Analysis.pdf"
    )

    cn_font = register_fonts()
    styles = build_styles(cn_font)

    doc = SimpleDocTemplate(
        output_path,
        pagesize=A4,
        leftMargin=18 * mm,
        rightMargin=18 * mm,
        topMargin=18 * mm,
        bottomMargin=18 * mm,
        title="Redisson 分布式锁源码解读指南",
        author="ToolKitPlus/rocketmq-analysis",
        subject="Redisson Lock Source Code Analysis",
        creator="reportlab",
    )

    # 页眉页脚
    def on_page(canvas, doc):
        canvas.saveState()
        canvas.setFont("Helvetica", 7)
        canvas.setFillColor(colors.HexColor("#757575"))
        canvas.drawString(18 * mm, 10 * mm,
                          "Redisson Lock Source Analysis -- ToolKitPlus")
        canvas.drawRightString(A4[0] - 18 * mm, 10 * mm,
                               f"Page {doc.page}")
        canvas.setStrokeColor(colors.HexColor("#e0e0e0"))
        canvas.setLineWidth(0.5)
        canvas.line(18 * mm, 14 * mm, A4[0] - 18 * mm, 14 * mm)
        canvas.restoreState()

    story = build_content(styles)
    doc.build(story, onFirstPage=on_page, onLaterPages=on_page)
    print(f"PDF generated: {output_path}")


if __name__ == "__main__":
    main()
