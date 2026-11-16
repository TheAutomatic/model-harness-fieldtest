# Gemini 4 Hydrogen 三方实测对照：OMP × 双反代渠道 vs Antigravity 官方 CLI

> ⚠️ **反代风控高危警示**：**反代接入违反上游服务条款，切勿盲目模仿！本次针对 Antigravity 反代渠道的一轮四题满血 Agent 测评，直接触发风控导致损失了一个 Gemini Ultra 5x 账户。** 本档仅作模型同源性、渠道流特征与原厂客户端对照的客观技术留档，不做任何反代渠道推荐。

本档围绕同属 `Gemini 4 Hydrogen` 的三条真实调用路径，使用完全相同的四道题与离线验收脚本做单轮同台实测：

1. **OMP × AI Studio 反代渠道**（`OMP 18.20.2` 满血默认工具链，`gemini-4-hydrogen`，经 `/v1` OpenAI 兼容转换接入，`--thinking xhigh`）；
2. **OMP × Antigravity 反代渠道**（`OMP 18.20.2` 满血默认工具链，`gemini-4-hydrogen-xhigh`，经 `/v1beta` Google 原生协议接入，`--thinking xhigh`）；
3. **Antigravity 官方 CLI（`agy cli` 原厂客户端直连）**：在完全独立的四个外部随机目录中逐题串行运行官方 `agy cli` 交互会话，不经任何第三方反代网关，作为原厂基线参照。

隔离口径严格对齐仓库的[满血开箱规矩](../../README.md#客户端实测规矩满血开箱)：
- **OMP 两路**：保留全部默认原生工具（含 `eval`、内置无头 `browser`、`lsp`、`ast_edit`、`task` 子代理等），每场独立临时 `PI_CODING_AGENT_DIR` 锁死全角色 `:xhigh` 模型，扩展钩子封堵外网搜索/拉包与跨目录读取。
- **原厂 `agy cli` 一路**：预先为四道题部署互不相邻的独立随机目录并注入离线依赖兜底（确保裸终端直接跑 `python reproduce.py` 与 `python run_pytest.py` 零联网可用），按 `A → B → C → D` 单目录串行测试；事后核对 CLI 动作摘要确认 **152 次动作全部为本地 `read / edit / command`，0 次联网搜索或外部抓取**。

---

## 一、前置探针与中长提示词摸底（OMP 双反代链路）

正式跑题前，先在 OMP 下对两条反代端点做了两轮摸底：

1. **连通与 3 轮工具闭环探针**：两边均一次零报错跑通，次轮正常命中 `cacheRead` 缓存（`11.21s` vs `12.32s`）。
2. **约 450 字服务端并发工程题无工具盲测**：
   - **正文质量同处第一梯队**：两边均一次性完整命中全部五个维度的核心不变量与状态机修复闭环。
   - **思考预算呈现 3 倍级差**：同样请求 `--thinking xhigh`，**AI Studio 反代渠道**输出思维链 **`10,676` tokens**（`56.7s`），而 **Antigravity 反代渠道**输出思维链高达 **`35,463` tokens（`3.32×`）**、耗时 **`173.1s`（`3.05×`）**；同时 `/v1beta` 原生协议对首轮系统提示词与工具 Schema 分词比 `/v1` 转换层省约 **10%**（`7,822` vs `8,725` input tokens）。

---

## 二、三方正式单轮成绩单与耗时 / 开销明细

| 任务 | OMP × AI Studio 反代 (`hydrogen`, `xhigh`) | OMP × Antigravity 反代 (`hydrogen-xhigh`, `xhigh`) | **Antigravity 官方 CLI（原厂直连）** |
|---|---|---|---|
| **A 鹈鹕骑车 HTML** | **已交付（38.0 KB）**，墙钟 `3m47s`；`browser` 截图自检 2 轮，双视口零报错零溢出 | **已交付（62.5 KB）**，墙钟 `5m23s`；`browser` 截图自检 4 轮 + 日落切换，双视口零报错零溢出 | **已交付（67.5 KB）**，思考计时 `4m20s`²（文件改画跨度 `8m39s`）；写脚本拉临时浏览器自检，零报错零溢出 |
| **B Requests 重定向** | **7/7**，墙钟 `3m00s`；直击根因 `req = prepared_request` | **7/7**，墙钟 `6m01s`；直击根因 `req = prepared_request` | **7/7**，思考计时 `4m53s`²；直击根因 `req = prepared_request` |
| **C 子数组余数和** | **41/41**，墙钟 `33.4s`；4 轮一把写出树状数组满分 | **41/41**，墙钟 `1m07s`；6 轮树状数组满分 | **41/41**，思考计时 `1m47s`²；写出 4 层 32 叉分块树 + C 层 `sum` 加速满分 |
| **D Pytest 清理** | **11/11**，墙钟 `6m37s`；补 `_Outcome` 与双重失败保护（`cleanup_ran: true`） | **11/11**，墙钟 `12m38s`；手写 `_TeardownOutcome` 与双重失败保护（`cleanup_ran: true`） | **11/11**，思考计时 `9m17s`²；补 `_Outcome` + 173 行回归单测 + 自跑 `test_debugging.py`（`cleanup_ran: true`） |

### 逐场与合计开销明细

| 场次 / 合计 | 计时指标 | 轮数 | 工具/动作数 | 未缓存输入 (k) | 缓存读取 (k) | 总输出 (k) | 其中思考 `reasoning` (k) | 等价基准折算 ($)¹ |
|---|---|---:|---:|---:|---:|---:|---:|---:|
| `A-hydrogen`（AI Studio 反代） | 墙钟 3m47s | 9 | 10 | 85.5 | 256.5 | 38.7 | 5.4 | $0.44 |
| `A-hydrogen-xhigh`（Antigravity 反代） | 墙钟 5m23s | 16 | 16 | 210.0 | 1,027.5 | 49.7 | 18.5 | $0.76 |
| **`A-agy-cli`（官方 CLI）** | **思考 4m20s²** | — | **14**（7读/2改/5命令） | — | — | — | — | 订阅制未暴露 |
| `B-hydrogen`（AI Studio 反代） | 墙钟 3m00s | 22 | 35 | 83.6 | 671.6 | 19.5 | 13.5 | $0.32 |
| `B-hydrogen-xhigh`（Antigravity 反代） | 墙钟 6m01s | 33 | 56 | 159.2 | 2,611.1 | 52.1 | 43.5 | $0.83 |
| **`B-agy-cli`（官方 CLI）** | **思考 4m53s²** | — | **40**（20读/4改/16命令） | — | — | — | — | 订阅制未暴露 |
| `C-hydrogen`（AI Studio 反代） | 墙钟 0m33s | 4 | 3 | 17.5 | 24.3 | 3.1 | 1.7 | $0.05 |
| `C-hydrogen-xhigh`（Antigravity 反代） | 墙钟 1m07s | 6 | 6 | 20.7 | 57.7 | 8.7 | 6.6 | $0.10 |
| **`C-agy-cli`（官方 CLI）** | **思考 1m47s²** | — | **13**（1读/1改/11命令） | — | — | — | — | 订阅制未暴露 |
| `D-hydrogen`（AI Studio 反代） | 墙钟 6m37s | 39 | 56 | 216.2 | 2,931.2 | 42.2 | 33.1 | $0.86 |
| `D-hydrogen-xhigh`（Antigravity 反代） | 12m38s | 57 | 94 | 266.4 | 7,927.4 | 101.3 | 82.2 | $1.75 |
| **`D-agy-cli`（官方 CLI）** | **思考 9m17s²** | — | **85**（39读/9改/37命令） | — | — | — | — | 订阅制未暴露 |
| **合计：OMP × AI Studio 反代** | **墙钟 13m57s** | **74** | **104** | **402.8** | **3,883.6** | **103.5** | **53.7** | **$1.67** |
| `D-hydrogen-xhigh`（Antigravity 反代） | 墙钟 12m38s | 57 | 94 | 266.4 | 7,927.4 | 101.3 | 82.2 | $1.75 |
| **合计：Antigravity 官方 CLI** | **累计思考 20m17s²** | — | **152**（67读/16改/69命令） | — | — | — | — | **订阅制未暴露** |

> ¹ OMP 两路按统一官方基准单价（输入 `$1.50/M`、缓存读取 `$0.075/M`、含思考总输出 `$7.50/M`）折算等价理论账单以衡量资源消耗倍率（`2.06×`），不代表渠道实付折扣价；OMP 全部 8 场子代理派生全为 `0`，三方全部 12 场均零外网参考污染（`upstream_source_read = false`）。
> ² **官方 `agy cli` 计时口径说明**：界面折叠行显示的 `○ Thought for Xm Ys` + 末轮 `▸ Thought for Xs` 统计的是**各轮模型思考流耗时之和**（A `4m14s+6s=4m20s`、B `4m49s+4s=4m53s`、C `1m47s`、D `9m12s+5s=9m17s`，合计 **`20m17s`**），其中不包含本地命令执行耗时、代码生成输出流耗时以及最后一段文字回复的输出时间（例如 A 题思考计 `4m20s`，而磁盘上 `index.html` 从首次写入到末次修改横跨 `8m39s`）。算上 152 次本地动作执行与输出流时间后，原厂 `agy cli` 的实际端到端耗时与 `OMP × Antigravity 反代`（墙钟 `25m09s`、172 次工具）高度吻合。

---

## 三、四道题三方对照的关键技术看点

### 1. D 题（Pytest `unittest` 清理生命周期）：三方全部独立拿下 `11/11` 大满贯

在此前 [`GLM-5.3（满血开箱）`](../glm-5.3-full-harness/README.md) 的两轮重测中，四场独立运行全部卡在 `10/11`（漏掉 `unittest.TestCase.run()` 退出后 `_outcome` 已被置空导致清理异常丢失的机制）。而本次三条 Hydrogen 路径在**零外网参考**下，全部顺着本机 Python 标准库源码独立推穿，**三场全拿 `11/11` 且双重失败诊断均为 `cleanup_ran: true`**：

- **OMP × AI Studio 反代（`D-hydrogen`，墙钟 6m37s）**（[补丁](artifacts/D/D-hydrogen/changes.patch) · [验收](results/D-hydrogen/verification.json)）：
  复用标准库 `unittest.case._Outcome(self)` 临时挂载到 `self._testcase._outcome` 执行 `doCleanups()`，用 `suppress_exc=teardown_failed` 防止 `tearDown()` 已抛错时重复记录，并补齐 Python 3.12+ `addDuration` 空实现。
- **OMP × Antigravity 反代（`D-hydrogen-xhigh`，墙钟 12m38s）**（[补丁](artifacts/D/D-hydrogen-xhigh/changes.patch) · [验收](results/D-hydrogen-xhigh/verification.json)）：
  不依赖私有 `_Outcome` 类，手写带 `@contextlib.contextmanager def testPartExecutor(...)` 的轻量 `_TeardownOutcome` 完整接管 LIFO 清理异常路由。
- **Antigravity 官方 CLI（`D-agy-cli`，思考 9m17s / 85 次动作）**（[补丁](artifacts/D/D-agy-cli/changes.patch) · [验收](results/D-agy-cli/verification.json)）：
  核心修复思路与 `D-hydrogen` **完全同构**（同样通过 `getattr(unittest.case, "_Outcome", None)` 临时挂载 `outcome_cls(self)` + 补齐 `addDuration`），同时在 `testing/test_unittest.py` 里手写了 **173 行、4 组完整回归单测**，并主动跑完 `testing/test_debugging.py` 全套 `TestPDB` 用例验证未破坏 `--pdb`。

### 2. A 题（2D 鹈鹕骑车单文件 HTML）：连徽章文案都一字不差的模型同源印记

- **OMP × AI Studio 反代（`A-hydrogen`，38.0 KB）**（[HTML](artifacts/A/A-hydrogen/index.html) · [桌面截图](results/A-hydrogen/screenshot.png) · [窄屏截图](results/A-hydrogen/mobile.png)）：青绿复古车 + 藤编车筐小蓝鱼 + 底部独立药丸控制栏，2 轮 `browser` 截图多模态自检。
- **OMP × Antigravity 反代（`A-hydrogen-xhigh`，62.5 KB）**（[HTML](artifacts/A/A-hydrogen-xhigh/index.html) · [桌面截图](results/A-hydrogen-xhigh/screenshot.png) · [窄屏截图](results/A-hydrogen-xhigh/mobile.png)）：红色弯梁车 + 日落模式切换，4 轮截图自查修好膝关节几何，左上角徽章写着 **`海滨骑行 · 2D 鹈鹕自行车`**。
- **Antigravity 官方 CLI（`A-agy-cli`，67.5 KB）**（[HTML](artifacts/A/A-agy-cli/index.html) · [桌面截图](results/A-agy-cli/screenshot.png) · [窄屏截图](results/A-agy-cli/mobile.png)）：哪怕没有 OMP 的内置 `browser` 工具，模型在官方 CLI 里也自己通过 PowerShell 拉起临时浏览器配置目录（`$tmpProf`）渲染自检并改画；桌面端（`1000×700`）呈现多层羽翼、白羽大腿、车灯与车筐小蓝鱼，左上角徽章文案同样一字不差写着 **`海滨骑行 · 2D 鹈鹕自行车`**（注：`430×800` 窄屏下无溢出零报错，仅底部绝对定位药丸按钮文字竖排换行后轻擦车轮下缘，按规矩窄屏不作扣分项）。

### 3. B 题与 C 题：三方全满，官方 CLI 在 C 题写出 32 叉分块树优化

- **B 题（Requests 重定向）**：三方全部在 `requests/sessions.py` 循环末尾写出与上游官方一致的一行根因修复 `req = prepared_request`（[`B-hydrogen`](artifacts/B/B-hydrogen/changes.patch) · [`B-hydrogen-xhigh`](artifacts/B/B-hydrogen-xhigh/changes.patch) · [`B-agy-cli`](artifacts/B/B-agy-cli/changes.patch)），全数 **`7/7`**。
- **C 题（AtCoder 模和子数组）**：OMP 两路均用树状数组一次拿下 **`41/41`**；原厂 `C-agy-cli`（[源码](artifacts/C/C-agy-cli/main.py)）则专门针对 CPython 写了 **4 层 Base-32 计数树（`32^4 > 10^6`）**，用最多 4 次短切片内置 C 函数 `sum()` 替代位运算循环，并在交卷前自己在命令行跑了 4 轮基准测试，同样 **`41/41`** 全过。

---

## 四、三方闭环鉴证结论（完整拆解见[复盘文档](../../notes/hydrogen-channel-forensics-and-tier-eval.md)）

把 **OMP 双反代** 与 **Antigravity 官方 CLI** 三组实测拼齐后，证据链彻底闭环：

1. **原厂 CLI 直接印证了 Antigravity 旁路摘要器指纹**：此前我们在 OMP 抓包中发现 Antigravity 反代返回第三人称工程笔记摘要、且常以固定句式 `I'm thinking through how to approach this.` 或 `Initial ...` 开头；本次在**未经任何第三方网关的原厂 `agy cli`** 界面里，B 题折叠摘要原封不动出现了 `(I'm thinking through how to approach this.)`，A/C/D 也全部是同款第三人称工程诊断体，证实这套摘要器文风 100% 来自谷歌 Antigravity 官方管线本身。
2. **谷歌并未在 AI Studio / Antigravity 部署不同底层模型**：无论是完全一致的 Tink AEAD `thought_signature` 密钥头（`01 69 14 7d 13`），还是跨客户端高度一致的解题构思与 SVG 细节特征，都确认两边底层是同一套 Hydrogen 模型。
3. **本套简单题库三方均已触顶，但按思考配额对标 Antigravity 至少不会输给 AI Studio**：
   - 现有四道题对 Hydrogen 梯队偏简单，三方全部满分，仅凭当前得分还看不出不同思考长度或服务端内部预设提示词带来的实际干活上限差异。
   - 但从动作规模与思考时长看，原厂 `agy cli`（152 次动作、累计纯思考 `20m17s`）与 `OMP × Antigravity 反代`（172 次工具、总墙钟 `25m09s`）完全同级，而 AI Studio 反代开 `xhigh` 释放的思考量约为 Antigravity `xhigh` 的三分之一（大致等效 Antigravity 的 `high` 档）。按同源推理模型“思考越充分越稳健”的寻常评测经验判断，**至少 Antigravity 渠道不可能输给 AI Studio 渠道**；唯独切记切勿用反代方式调 Antigravity（本轮直接折损一个 Gemini Ultra 5x 账号），要测或用 Antigravity 务必走官方原厂客户端。

## 材料导航

- 实验元数据：[experiment.json](experiment.json)
- 题目原话：[prompts/](prompts/)
- 交付物与补丁：[A 鹈鹕 HTML](artifacts/A/) · [B Requests 补丁](artifacts/B/) · [C 算法源码](artifacts/C/) · [D Pytest 补丁](artifacts/D/)
- 结果、截图与审计：[results/](results/)
- 独立验收脚本与说明：[evaluation/](evaluation/)
- 跨渠道字节级鉴证与原厂对照复盘：[../../notes/hydrogen-channel-forensics-and-tier-eval.md](../../notes/hydrogen-channel-forensics-and-tier-eval.md)
