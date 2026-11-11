# GLM-5.3：同一端点下的 Claude Code 与 OMP（两轮）

> **注**：本档为早期仅开放六个基础文件/终端工具的历史记录；保留客户端全套默认内置工具的两轮重测见 **[GLM-5.3（满血开箱）](../glm-5.3-full-harness/README.md)**。

对象是智谱官方接口的 **GLM-5.3**（`https://open.bigmodel.cn/api/anthropic`，Anthropic 兼容协议，thinking 请求 high 档），客户端为 Claude Code `2.1.322` 与 OMP `18.18.6`，系统 Python 3.13.14。题面沿用 DeepSeek 轮的 A–D：鹈鹕 HTML、Requests 重定向（SWE-bench `psf__requests-1963`）、AtCoder ABC378 E、Pytest unittest 清理（SWE-bench `pytest-dev__pytest-7151`）；源码提交、依赖与验收脚本一致，D 题扩为 11 项并在运行前冻结。

每题每客户端每轮一次，不补跑，不与历史轮次排名。第二轮是同配置重跑，主要用于观察单轮结果的方差。

| 轮次 | 任务 | Claude Code | OMP |
|---|---|---|---|
| 1 | A 鹈鹕 HTML | 已交付，10m38s；静态 JS 语法过 | 已交付，7m05s；静态 JS 语法过 |
| 1 | B Requests 重定向 | **7/7**，7m20s | **7/7**，6m34s |
| 1 | C 子数组余数和 | **41/41**，3m48s（归并排序统计逆序对） | **41/41**，1m13s（树状数组） |
| 1 | D Pytest 清理 | **10/11**，17m46s | **10/11**，15m51s |
| 2 | A 鹈鹕 HTML | 已交付，7m27s；内嵌脚本，语法过 | 已交付，6m23s；纯 SVG 动画，无脚本 |
| 2 | B Requests 重定向 | **7/7**，10m03s | **7/7**，3m51s |
| 2 | C 子数组余数和 | **41/41**，1m16s（树状数组） | 39/41，2m04s（归并排序，两个 20 万用例超时） |
| 2 | D Pytest 清理 | **11/11**，21m31s，**读过上游源码**¹ | **10/11**，16m51s |

> ¹ 11/11 是交付补丁的实测分数；因解题过程读取了上游参考实现，该项不计入独立解题比较，见下文。

两轮 8 次同题对比 OMP 快了 7 次（只有第二轮 C 题输给对手），但速度优势要在“对”的前提下看：第二轮 OMP 在 C 题用时比对手长的同时，还挂了两个规模用例。

## B 题：四轮全绿，且只有一种修法

四组交付全部 7/7。第一轮双方、第二轮双方（Claude 用 `req = resp.request`，OMP 用 `req = prepared_request`，语义等价）都落在同一个根因修复上：**让每一跳重定向基于上一跳实际发出的请求，而不是最初的请求**，方法、body、认证状态随之正确延续。对这个量级的模型，B 题已经没有区分度。

第二轮 Claude 解题中下载了 Requests 2.34.2 参考包，解压命令因带 `../` 命中路径守卫钩子被拦，日志审查未发现读取包内代码（[审计](r2/results/B-claude/audit.json)），成绩保留。

## C 题：正确性全过、只有压测能抓的 bug

第一轮双方满分（Claude 归并排序统计逆序对，OMP 树状数组，20 万规模均在一秒内）。第二轮算法对调：Claude 树状数组满分；OMP 的归并排序把右半边递归了两次：

```python
inv += count_inversions(arr[mid:])[0]
right = count_inversions(arr[mid:])[1]   # 同一个子问题算了第二遍
```

（[r2/artifacts/C/C-omp/main.py](r2/artifacts/C/C-omp/main.py)）

结果：39 项正确性用例全过，递推却变成 T(n)=3T(n/2)+O(n)，两个 20 万元素规模用例超过 15 秒超时。这种“多写一行”的 bug 骗得过全部功能用例，只有规模压测能抓——这正是 C 题保留大用例的价值。

## D 题：拉出一条方案光谱

四组交付（加上 Flash 轮共八组）恰好铺开了同一道题的解法空间：

| 方案形态 | 出处 | 验收 | 短板 |
|---|---|---|---|
| `teardown()` 里顺序调 `tearDown()`、`doCleanups()`（无 `try/finally`） | 第一轮 Claude、第二轮 OMP | 10/11 | 顺序正确；`doCleanups()` 吞掉清理异常，且 `tearDown()` 抛错时会跳过清理 |
| `teardown()` 里 `try: tearDown()` / `finally: doCleanups()` | 第一轮 OMP | 10/11 | 顺序与双重失败清理均守住；仅挂在 `doCleanups()` 把清理异常塞进已被抛弃的 `_Outcome` |
| `try/finally` + 给 `doCleanups()` 包一层结果感知的 outcome | 第二轮 Claude | 11/11 | 无（但非独立推导，见下节） |

（Flash 轮补齐了光谱另外两端：不碰 `doCleanups()`、自己跑 `_cleanups` 循环并上报的两组独立 11/11，以及在 `runtest` 捕获异常时早调 `doCleanups()` 导致连挂四项的 7/11，见 [GLM-5.3-Flash](../glm-5.3-flash/README.md)。）

结构性结论与 DeepSeek 轮的解剖一致：**11 项里最难的是“同时报告原失败与清理异常”，朴素 try/finally 在结构上不可能过这一项**——要么绕开 `doCleanups()` 自己接管清理循环并把异常上报 pytest，要么给 outcome 做结果感知包装。本轮四组都守住了严格顺序（setup → test → debug → teardown → cleanup-last → cleanup-first），没有出现清理先于 tearDown / pdb 的倒序形态。

第一轮 Claude 在最终回复里主动说明“清理异常会被吞掉”但没有动手解决——自我报告准确、修复未跟上，这个样本值得留档。

双重失败诊断（测试与 tearDown 同时失败，事后追加、不计入 11 项）：结果直接由补丁是否包了 `try/finally` 决定——第一轮 Claude 与第二轮 OMP 未加 `try/finally` 而漏清理，第一轮 OMP 独立写出 `try/finally` 执行了清理，第二轮 Claude 则是在读过上游后照搬了 `try/finally`。单看独立样本（OMP 两轮一有一无），是否顺手护住 `tearDown` 异常同样随轮次波动。

## D 题与上游源码：字符串钩子漏掉了 pip download

两轮使用了逐字节相同的 `guard.py` / `guard.ts` 黑名单（拦截仓库目录名、`curl`/`wget`、GitHub 域名与 `../` 相对路径，但未拦截 `pip` 或 `zipfile`），两轮走出了不同路径：

- 第一轮：Claude 尝试 `ls` 宿主依赖目录，因路径含仓库目录名 `model-harness-fieldtest` 被 PreToolUse 钩子当场阻止，操作单独留档。
- 第二轮：Claude 改在 `/tmp` 下跑 `python -m pip download` 并用绝对路径解压，绕过了基于子串匹配的钩子，读取 Pytest 8.3.3 与 7.1.3 等版本的生命周期实现后写出带结果感知 outcome 的修复，实测 11/11（[审计](r2/results/D-claude/audit.json)）。

处理方式：补丁分数保留（11 项实测全过），审计记录 `upstream_source_read: true`，同时把该项从“独立解题比较”中剔除。这是 DeepSeek 轮 D1 默写事件之后定下的规矩——**审计标记先行，分数与独立性分开表述**。教训同样明确：仅禁 `curl`/`wget` 和特定域名的字符串钩子拦不住包管理器，物理断网或显式封禁 `pip` 才能堵住这类旁路。

## A 题：四次交付、零视觉验收

本地文件浏览器预览被工具策略阻止，四份 HTML 只做了静态 JS 语法检查——语法检查不能代替打开浏览器看画面，所以 A 题只记“已交付”，不评价美观与动画质量。原提示词没有要求手机适配或动画。第二轮 OMP 用无脚本的纯 SVG 实现动画，恰好绕开了“只能查语法”的尴尬。

## 运行条件

- Claude 最终元数据显示 maxOutputTokens=32000；Claude 侧请求别名 `glm-5.3[1M]`，OMP 侧独立注册 `glm-5.3`、1M 上下文、131072 maxTokens。两端默认/注册限制不等价，不声称输出预算一致。费用不作比较：客户端对自定义模型的计价没有独立核实。
- 每题新会话、独立状态；禁用备用模型链、子代理、额外技能与 MCP，只开放本地文件与 shell 工具；无总时间上限。第一轮 A 与 B、C 批次有运行重叠，耗时均为实际墙钟。
- 随机工作目录与路径保护钩子降低串读风险；未配置 OS 沙箱，不宣称完全隔离。日志审查未发现成功读取旧答案。第一轮 OMP 在 C 题用过 /tmp 临时测试文件，未发现其他候选读取。
- D 题 11 项在运行前冻结；预检使用 `-c NUL`。源码 tox.ini 在 Python 3.13 下把 addDuration 的 RuntimeWarning 升为错误，是两组共同的额外兼容干扰，均自行处理；主持人未中途修改源码或提示。独立验收同样以 `-c NUL` 隔离仓库配置。Claude 报告原有 unittest/debugging 测试套件仍存在兼容失败，这不等于整个历史套件全通过。
- 原始日志：`.local/glm53`（第一轮）、`.local/glm53-r2`（第二轮），本机忽略目录；公开树只保存脱敏摘要、交付与验收材料。

## 复现与材料

- [r1/](r1/)、[r2/](r2/)：各轮 prompts（A–D 中文原话）、artifacts（HTML / changes.patch / main.py）、results（result.json、verification.json、审计与双重失败诊断）。
- 独立验收脚本与复现指南见 [r1/evaluation/README.md](r1/evaluation/README.md)（两轮共用；Requests 与 Pytest 源码提交、依赖版本、sitecustomize 兼容层都在里面）。
- 相关链接：[AtCoder ABC378 E](https://atcoder.jp/contests/abc378/tasks/abc378_e) · [SWE-bench](https://huggingface.co/datasets/princeton-nlp/SWE-bench)
