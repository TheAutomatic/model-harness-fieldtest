# GLM-5.3-Flash：同配置两轮，方差先于客户端差异

对象是智谱官方接口的 **GLM-5.3-Flash**（Anthropic 兼容端点，thinking 请求 high 档），客户端 Claude Code `2.1.322` 与 OMP `18.18.8`（注意：[GLM-5.3 主实验](../glm-5.3/README.md)两轮用的是 OMP 18.18.6），系统 Python 3.13.14。题面与验收条件和主实验完全一致：A–D 每客户端每轮一次，同题并发，独立会话与工作区，两轮重叠进行。

| 轮次 | 任务 | Claude Code | OMP |
|---|---|---|---|
| 1 | A 鹈鹕 HTML | 已交付，19m16s | 已交付，1m11s |
| 1 | B Requests 重定向 | 7/7，10m15s | 7/7，6m13s |
| 1 | C 子数组余数和 | 41/41，3m06s | 41/41，4m02s |
| 1 | D Pytest 清理 | 10/11，24m56s | **11/11**，19m17s |
| 2 | A 鹈鹕 HTML | 已交付，8m26s | 已交付，3m03s |
| 2 | B Requests 重定向 | **3/7**，5m40s | 7/7，7m51s |
| 2 | C 子数组余数和 | 41/41，4m45s | 41/41，3m39s |
| 2 | D Pytest 清理 | **11/11**，36m47s | **7/11**，13m59s |

| 两轮合计 | Claude Code | OMP |
|---|---|---|
| B Requests 重定向 | 10/14 | **14/14** |
| C 子数组余数和 | 82/82 | 82/82 |
| D Pytest 清理 | **21/22** | 18/22 |
| 各题耗时相加 | 113m11s | 59m15s |

OMP 在 8 次同题对比中快了 6 次（第一轮 A/B/D、第二轮 A/C/D）；第一轮 C、第二轮 B 是 Claude Code 更快。

## 先说结论：同配置重跑的方差盖过客户端差异

两轮之间题面、验收、模型与客户端配置都没有变，但单题成绩大幅摆动：B 题 Claude 7/7 → 3/7；D 题 OMP 11/11 → 7/11、Claude 10/11 → 11/11；D 题 Claude 耗时 24m56s → 36m47s（注：两轮重叠执行使 B/C/D 阶段处于同机同端点四路并发，墙钟时间亦受并发争抢放大）。任何“某客户端更强”的单轮结论在这个数据面前都站不住——主实验坚持“单轮记录不用于推断稳定胜率”，本实验把这句话变成了实证。合计分上 Claude 的 D 21/22 领先，但那恰逢它 11/11 的一轮；换个样本日重跑，没人知道结果。

## B 题第二轮 Claude 3/7：方法修对了，根因没动

失败的四个用例（303/302/301_then_307、auth_cross_host）里，方法序列其实全部正确（如 `POST → GET → GET`）——它把 `method = req.method` 提到循环外，让 303 改写出的 GET 能延续到下一跳 307，这一步是对的。挂在另外两个维度：

- 循环体里每一跳仍然 `req.copy()` **最初的**请求，于是 303 那跳被清空的 body 在 307 那跳带着 `'payload'` 整体复活；
- 跨域第一跳被剥离的 `Authorization` 也在第二跳变回 `Bearer offline-test`。

验收脚本同时核对方法、body、auth 三元组（[r2/results/B-claude/verification.json](r2/results/B-claude/verification.json) 里四条失败记录全是 body/auth 复活，方法无一错）。同题 OMP 用一行 `req = prepared_request`（每跳基于上一次实际发出的请求）根治，还顺手写了 HISTORY.rst changelog。“理解了一个症状”与“找到根因”的差距，这题是全场最干净的样本。

## D 题：两组独立写出 11/11，另一组早调清理掉到 7/11

- **第一轮 OMP 11/11**：`teardown()` 里 try/finally 之后不调 `doCleanups()`，自己 pop `_cleanups` 循环执行，异常经 `addError` 上报——严格顺序与“同时报告原失败与清理异常”两项全守住（[补丁](r1/artifacts/D/D-omp/changes.patch)）。
- **第二轮 Claude 11/11**：同样的自实现 `_run_cleanups`，异常走 `_addexcinfo`，并在注释里准确解释了为什么直接调 `doCleanups()` 会把异常吞进抛弃型 `_Outcome`（[补丁](r2/artifacts/D/D-claude/changes.patch)）。
- **第二轮 OMP 7/11**：保留 `_GetOutOf_testPartExecutor`，在 `runtest()` 捕获异常处直接调用 `with contextlib.suppress(Exception): self._testcase.doCleanups()`（[补丁](r2/artifacts/D/D-omp/changes.patch)）。模型在结案说明里自称“对齐上游修法”，实则比上游 PR #7151 / `gold_patch` 错得更重：`gold_patch` 删掉了异常跳出机制、仅在 `--pdb` 下延后 `tearDown`，在本轮 11 项验收中实测可得 10/11（只挂 `pdb_failure`）；而这版修法在普通 `failure`、`error` 下也把顺序颠倒成 `setup → test → cleanup-last → cleanup-first → teardown`，再加上 `pdb_failure` 提前拆现场、抛弃型 `_Outcome` 与 `suppress` 双重吞掉清理异常，连挂四项只拿 7/11。
- **第一轮 Claude 10/11**：朴素 `try/finally` + `doCleanups()`，只挂在清理异常上报，与主实验第一轮 OMP 形态一致（主实验另两组 10/11 未包 `try/finally`）。

两次 11/11 均为独立推导（audit 无上游读取记录），且都绕开了 `doCleanups()` 自己接管清理循环——与主实验的结构性结论闭环。事后双重失败诊断（`double-failure-diagnostic.json`）四组均为 `cleanup_ran: true`（前三组靠 `try/finally` 守住，第二轮 OMP 则是因为在 `tearDown` 之前已经倒序跑完了清理）。

## 其余

- C 题四组 82/82：对这个模型同样饱和。
- A 题四次交付、零视觉验收（本地浏览器预览被工具策略阻止；两份 Claude 含内嵌脚本且语法检查通过，两份 OMP 为无脚本的纯 SVG + CSS 动画），与主实验同样受限，不评价画面。
- 外部命令记录在 `audit.json`（第一轮 `B-claude` 一次 `curl` 探测 PyPI 被钩子当场拦截；第二轮 `B-omp` 为跑原仓库测试发起后台 `pip install`，随会话结束被取消，均未读取上游源码），交付补丁一律按同一验收标准计分。

## 材料导航

- [第一轮交付](r1/artifacts/) · [第一轮验收](r1/results/) · [第二轮交付](r2/artifacts/) · [第二轮验收](r2/results/)
- 题面原话：[r1/prompts/](r1/prompts/)（两轮相同）
- 复现与验收说明：[r1/evaluation/README.md](r1/evaluation/README.md)
