# Gemini 4 Hydrogen vs Hydrogen-xHigh（OMP 满血开箱）：同设 `xhigh` 思维等级的单轮对决

本档在 `OMP 18.20.2` 满血默认工具链下，拉通对比同属 Hydrogen 家族的两个端点模型，并统一将客户端思维等级固定为 **`--thinking xhigh`**：

- **`gemini-4-hydrogen`**：走 OpenAI 兼容协议（`/v1`，`openai-completions`），支持 `efforts: [low, medium, high, xhigh]`。
- **`gemini-4-hydrogen-xhigh`**：走 Google Gemini 原生协议（`/v1beta`，`google-generative-ai`），支持 `efforts: [low, medium, high, xhigh]`。（注：该渠道下 Carbon / Argon 提供 `-high` 后缀模型，而 Hydrogen 实际暴露的高配型号即为 `gemini-4-hydrogen-xhigh`，无 `-high` ID。）

严格遵守仓库的[满血开箱规矩](../../README.md#客户端实测规矩满血开箱)：
1. **全套原生工具开启 + 全角色同模隔离**：保留 OMP 全部默认工具（含 `eval`、内置无头 `browser`、`lsp`、`ast_edit`、`task` 子代理等）；每场独立挂载全新临时 `PI_CODING_AGENT_DIR`（无历史 `history.db` 记忆，仅同步本地 `SYSTEM_TEMPLATE.md` 规避上游网关误拦），将全部 9 个 `modelRoles` 与全部 6 类 `task.agentModelOverrides` 强制绑死到当前被测模型的 `:xhigh`，清空 `fallbackChains`。
2. **工作区与外网答案封堵**：扩展钩子同时拦截 `web_search`、`read(http/https 外网 URL)`、外网 `curl/wget/pip download`、宿主机评测仓与兄弟工作区，仅放行 `127.0.0.1` / `localhost` 回环自测；严格按 `A → B → C → D` 顺序推进，同题双模同时起步、跨题零重叠。

---

## 一、前置探针与中长提示词同台摸底

正式跑题前，先用两轮探针验证端点健康度与 `xhigh` 思维档位的实际行为：

1. **连通与 3 轮工具闭环探针**（`read` 读文件 → `bash` 跑脚本 → 汇总输出）：两边均一次零报错跑通，第二轮起正常命中 `cacheRead` 缓存（耗时 `11.21s` vs `12.32s`）。
2. **约 450 字服务端并发工程题盲测**（不调工具，诊断异步 HTTP 连接池在 `307` 未读尽分块流、跨域凭据泄漏、一次性异步生成器空体挂起、`CancelledError` 被吞与脏连接回池五个维度的不变量及状态机修复方案）：
   - **正文质量同处第一梯队**：两边均一次性完整命中全部核心不变量与状态流转闭环，未漏任何边界。
   - **思考预算呈现 3 倍级差**：同样请求 `--thinking xhigh`，`gemini-4-hydrogen` 输出思维链 **`10,676` tokens**（耗时 `56.7s`），而走 `/v1beta` 的 `gemini-4-hydrogen-xhigh` 输出思维链高达 **`35,463` tokens（`3.32×`）**、耗时 **`173.1s`（`3.05×`）**；与此同时，原生 Google 协议对首轮系统提示词与工具 Schema 的分词比 OpenAI 兼容层省约 **10%**（`7,822` vs `8,725` input tokens）。

带着“**3 倍思考深度在真实工程题里能不能换来更高得分**”这个问题，进入正式四题实测。

---

## 二、正式单轮成绩单与全链路 Token 账单

| 任务 | `gemini-4-hydrogen` (`xhigh`) | `gemini-4-hydrogen-xhigh` (`xhigh`) |
|---|---|---|
| **A 鹈鹕骑车 HTML** | **已交付，3m47s**（`226.6s`）；调 `eval`+`browser` 截图多模态自检 2 轮，零报错零溢出 | **已交付，5m23s**（`323.0s`）；调 `eval`+`browser` 截图多模态自检 4 轮（自查修好膝关节朝向），带日落切换，零报错零溢出 |
| **B Requests 重定向** | **7/7，3m00s**（`180.0s`）；直击根因 `req = prepared_request` | **7/7，6m01s**（`360.9s`）；直击根因 `req = prepared_request` |
| **C 子数组余数和** | **41/41，33.4s**；4 轮一把写出树状数组满分 | **41/41，1m07s**（`66.9s`）；6 轮树状数组满分 |
| **D Pytest 清理** | **11/11，6m37s**（`397.1s`）；独立补齐 `_outcome` 与双重失败保护（`cleanup_ran: true`） | **11/11，12m38s**（`758.3s`）；独立手写 `_TeardownOutcome` 闭环与双重失败保护（`cleanup_ran: true`） |

### 逐场与合计开销明细

| 场次 / 合计 | 墙钟耗时 | 轮数 | 工具调用 | 未缓存输入 (k) | 缓存读取 (k) | 总输出 (k) | 其中思考 `reasoning` (k) | 按官方单价折算 ($)¹ |
|---|---:|---:|---:|---:|---:|---:|---:|---:|
| `A-hydrogen` | 3m47s | 9 | 10 | 85.5 | 256.5 | 38.7 | 5.4 | $0.44 |
| `A-hydrogen-xhigh` | 5m23s | 16 | 16 | 210.0 | 1,027.5 | 49.7 | 18.5 | $0.76 |
| `B-hydrogen` | 3m00s | 22 | 35 | 83.6 | 671.6 | 19.5 | 13.5 | $0.32 |
| `B-hydrogen-xhigh` | 6m01s | 33 | 56 | 159.2 | 2,611.1 | 52.1 | 43.5 | $0.83 |
| `C-hydrogen` | 0m33s | 4 | 3 | 17.5 | 24.3 | 3.1 | 1.7 | $0.05 |
| `C-hydrogen-xhigh` | 1m07s | 6 | 6 | 20.7 | 57.7 | 8.7 | 6.6 | $0.10 |
| `D-hydrogen` | 6m37s | 39 | 56 | 216.2 | 2,931.2 | 42.2 | 33.1 | $0.86 |
| `D-hydrogen-xhigh` | 12m38s | 57 | 94 | 266.4 | 7,927.4 | 101.3 | 82.2 | $1.75 |
| **合计：`hydrogen`** | **13m57s** | **74** | **104** | **402.8** | **3,883.6** | **103.5** | **53.7** | **$1.67** |
| **合计：`hydrogen-xhigh`** | **25m09s (`1.80×`)** | **112 (`1.51×`)** | **172 (`1.65×`)** | **656.3 (`1.63×`)** | **11,623.7 (`2.99×`)** | **211.7 (`2.05×`)** | **150.8 (`2.81×`)** | **$3.44 (`2.06×`)** |

> ¹ 按模型计费单价（输入 `$1.50/M`、缓存读取 `$0.075/M`、含思考总输出 `$7.50/M`）由客户端逐轮实测累加。审计结果确认：8 场运行子代理派生次数全为 **`0`**（`subagent_spawns = 0`），响应模型 100% 纯净，零越界读取外网或宿主机材料（`upstream_source_read = false`）。

---

## 三、四道题的关键技术看点

### 1. D 题（Pytest `unittest` 清理生命周期）：双双独立拿下 `11/11` 大满贯

在此前 [`GLM-5.3（满血开箱）`](../glm-5.3-full-harness/README.md) 的两轮重测中，四场独立运行全部卡在 `10/11`（挂在 `failure_and_cleanup_error`），连偷看到上游 Pytest 7.0 源码的那场也因为破坏 `--pdb` 时序只拿到 `10/11`。

而本档两款 Hydrogen 模型在**零外网参考**下，双双从 Python 标准库 `unittest.case` 的内部机制直接推穿了这道题，**两场全部 `11/11` 全绿，且事后“测试与 `tearDown` 双重失败”诊断均为 `cleanup_ran: true`**：

- **为什么普通 `self._testcase.doCleanups()` 拿不到第 11 分？**
  在标准库 `unittest.TestCase.run()` 退出后，`self._outcome` 已被清空为 `None`；此时在 Pytest 的 `TestCaseFunction.teardown()` 里裸调 `doCleanups()` 会落入无 `_outcome` 分支，清理回调抛出的异常不会经 `testPartExecutor` 转发给 `TestCaseFunction.addError()`，导致原测试失败与清理报错无法按 Pytest 规范并列上报。
- **`D-hydrogen` 的解法（6m37s，$0.86）**（[补丁](artifacts/D/D-hydrogen/changes.patch) · [验收](results/D-hydrogen/verification.json)）：
  直接复用标准库 `unittest.case._Outcome(self)` 临时挂载到 `self._testcase._outcome` 再执行 `doCleanups()`，同时用 `suppress_exc=teardown_failed` 防止 `tearDown()` 已经抛错时二次覆盖 `_excinfo`，并顺手补齐了 Python 3.12+ `unittest` 新增的 `addDuration` 空实现与回归单测，仅改 30 余行核心代码即一击通关。
- **`D-hydrogen-xhigh` 的解法（12m38s，$1.75）**（[补丁](artifacts/D/D-hydrogen-xhigh/changes.patch) · [验收](results/D-hydrogen-xhigh/verification.json)）：
  不依赖标准库私有 `_Outcome` 类，而是自己在 `_do_cleanups()` 内手写了一个带 `@contextlib.contextmanager def testPartExecutor(...)` 的轻量 `_TeardownOutcome`，精准放行 `KeyboardInterrupt / SystemExit / exit.Exception`、捕获首个清理异常的同时保证剩余 LIFO 清理全部跑完，再按 `tear_down_exc` 优先于 `cleanup_exc` 的顺序抛出，工程完备度极高。

### 2. A 题（2D 鹈鹕骑车单文件 HTML）：多模态视觉闭环的威力

与纯文本模型只能靠 DOM 属性盲猜画面不同，Hydrogen 原生具备多模态读图能力（`input: ["text", "image"]`）。两场运行都在首轮主动通过 `read("xd://eval/browser")` 查阅内置浏览器文档，随后拉起无头浏览器加载本地 `index.html`，**直接调 `tab.screenshot()` 把渲染出来的真实网页截图喂回给自己的视觉编码器审图改画**：

- **`A-hydrogen`（3m47s，38.0 KB）**（[HTML](artifacts/A/A-hydrogen/index.html) · [桌面截图](results/A-hydrogen/screenshot.png) · [窄屏截图](results/A-hydrogen/mobile.png)）：
  海滨灯塔与帆船背景下的青绿色复古单车，车头藤编车筐里探出一条小蓝鱼，鹈鹕系着橙色围巾、双腿按二连杆逆运动学（IK）随曲柄自然踩踏；底部药丸控制栏（暂停、按车铃、无级倍速滑块）独立置于画框下方，桌面（`1000×700`）与窄屏（`430×800`）均零溢出、零遮挡。
- **`A-hydrogen-xhigh`（5m23s，62.5 KB）**（[HTML](artifacts/A/A-hydrogen-xhigh/index.html) · [桌面截图](results/A-hydrogen-xhigh/screenshot.png) · [窄屏截图](results/A-hydrogen-xhigh/mobile.png)）：
  连续做了 **4 轮“截图 → 视觉审图 → 改 SVG/JS”迭代**——甚至在审图时自己发现膝关节弯曲方向不够自然并专门修了一版 IK 几何；成品配齐红色弯梁车、白色挡泥板、木质海滨护栏野花、三档速度切换（悠闲/巡航/冲刺）、车铃声效以及**日景/日落一键切换**，控件收纳在宽幅路面带内，双视口同样零报错、零裁切。

### 3. B 题与 C 题：干净利落零失误

- **B 题（Requests 重定向方法与鉴权状态传递）**：两边均没有掉进“只修 `method` 漏 `body` 或跨主机 `Authorization` 复活”的局部补丁陷阱，双双在 `requests/sessions.py` 循环末尾写出与上游官方一致的一行根因修复 `req = prepared_request`（[`B-hydrogen` 补丁](artifacts/B/B-hydrogen/changes.patch) · [`B-hydrogen-xhigh` 补丁](artifacts/B/B-hydrogen-xhigh/changes.patch)），全数 **`7/7`**。（注：初始工作区未预打 `ssl_match_hostname` 在 Python 3.13 下的相对导入垫片，两组在自测时均自行定位并绕过；B 题各有 1 次探查外部 Python 路径或长行读取触发扩展拦截，不影响主工作区独立解题。）
- **C 题（AtCoder 模和子数组树状数组）**：`C-hydrogen` 仅用 **4 轮、33.4 秒**（花费 `$0.05`）一把写出 1-indexed 树状数组拿下 **`41/41`**；`C-hydrogen-xhigh` 用 **6 轮、66.9 秒**同样一次全过 **`41/41`**。

---

## 四、结论：`hydrogen` vs `hydrogen-xhigh`（均开 `xhigh`）怎么选？

把一轮四题的成品质量、客观题满分率与账单摆在一起，结论非常明朗：

1. **硬实力与上限完全同级（客观题双双 `7/7 + 41/41 + 11/11` 全满贯）**：在本仓全部测试过的模型里，Hydrogen 系列是首个单轮独立把 B、C、D（含 D 题第 11 项清理异常并报与事后双重失败诊断）**全部一次打穿且零外网污染**的模型系列；加上多模态 + OMP 内置无头浏览器的“真机看图改画”闭环，A 题的画面完成度也显著高出一截。
2. **日常主力首选 `gemini-4-hydrogen`（配 `--thinking xhigh`）**：在客观题得分完全拉平的前提下，`gemini-4-hydrogen` 全程仅用 **`13m57s`**、折算 **`$1.67`** 就交齐了四道题；而 `gemini-4-hydrogen-xhigh` 因为单轮思考深出 **`2.81×`**、多做了 **`51%`** 的校验轮次（导致缓存复读滚到 **`2.99×`**），总耗时拉长到 **`25m09s`（`1.80×`）**、总成本翻倍到 **`$3.44`（`2.06×`）**。
3. **`gemini-4-hydrogen-xhigh` 适合留给不计时间成本的审美打磨或极端防御重构**：它在 A 题多自检两轮磨出了日落主题切换与更精细的关节细节，在 D 题不依赖标准库私有类而手写完整 `_TeardownOutcome` 执行器——这种“宁可多花一倍时间和预算也要把边角料雕透”的习性，适合挂在后台啃高风险核心模块或精修前端交互，日常高频开发用普通 `hydrogen:xhigh` 性价比高得多。

## 材料导航

- 实验元数据：[experiment.json](experiment.json)
- 题目原话：[prompts/](prompts/)
- 交付物与补丁：[A 鹈鹕 HTML](artifacts/A/) · [B Requests 补丁](artifacts/B/) · [C 算法源码](artifacts/C/) · [D Pytest 补丁](artifacts/D/)
- 结果、截图与审计：[results/](results/)
- 独立验收脚本与说明：[evaluation/](evaluation/)
