# 模型与渠道实测复盘（三）：AI Studio 反代 vs Antigravity 反代 vs 官方 CLI——Hydrogen 指纹鉴证与性能判断

> ⚠️ **反代风控高危警示**：**反代接入违反上游服务条款，使用需极度谨慎！本次针对 Antigravity 反代渠道的一轮四题满血 Agent 测评（112 轮高频工具调用、超 1,160 万 Token 缓存读取），直接触发风控导致笔者损失了一个 Gemini Ultra 5x 账户。** 本文仅作技术层面的渠道流特征拆解、原厂客户端对照与模型同源性考据，不构成任何反代使用建议。

> **测试背景与三方数据底座**：前两篇复盘（[精简六工具](harness-comparison-minimal-tools.md) · [满血开箱客户端终评](harness-comparison-full-default.md)）聚焦于“固定模型、横向换客户端（OMP vs Claude Code）”。而在最新归档的 [`Gemini 4 Hydrogen 三方实测对照`](../experiments/gemini-4-hydrogen-omp/README.md) 中，我们针对同一套四道题拉通了**三条真实链路**：
> 1. **OMP × AI Studio 反代渠道**（`gemini-4-hydrogen`，经 `/v1` OpenAI 兼容协议转换接入，设 `--thinking xhigh`）；
> 2. **OMP × Antigravity 反代渠道**（`gemini-4-hydrogen-xhigh`，经 `/v1beta` Google 原生协议接入，设 `--thinking xhigh`）；
> 3. **Antigravity 官方 CLI（`agy cli` 原厂客户端直连）**：不经任何第三方网关，在四个独立外部目录逐题串行实测。
>
> 结果**三方在客观题全部打出 `7/7 + 41/41 + 11/11`（含事后双重失败清理诊断全过）的大满贯**。结合 OMP 落盘 `stdout.jsonl` 的字节级抓包与官方 `agy cli` 的原生界面记录，本文直接用实锤证据把“AI Studio 与 Antigravity 到底是不是同一个模型、思维链文风与长度差异意味着什么”一次讲透。

---

## 一、模型指纹与原厂印证：谷歌并未部署异模，文风差异100%来自下游旁路摘要器

针对网传“AI Studio 与 Antigravity 思维链口气完全不像同一个模型、怀疑其中一边部署了缩水模型”的猜测，本次三方对照给出了闭环铁证：

### 1. 跨轮加密状态指纹（`thought_signature`）完全同源

在多轮工具调用中，谷歌推理后端会在每次 `toolCall` 下发高熵加密块 `thought_signature` 供下一轮还原隐式推理状态。将两条反代链路全部 8 场运行的签名块 Base64 解码并剥离外层封装后：

- **AI Studio 反代渠道**（`/v1` 封装于 `perCall.google.thought_signature`）：内层密文全部以固定的 5 字节 Google Tink AEAD 密钥头 **`01 69 14 7d 13`**（Base64 前缀 `AWkUfR...`）打头；
- **Antigravity 反代渠道**（`/v1beta` 原生裸签名）：解码后内层密文**分毫不差，同样全部以 5 字节 Tink 密钥头 `01 69 14 7d 13`（`AWkUfR...`）打头**。

不仅密码学包头同源，连跨客户端生成的代码与画面细节都撞出了几乎克隆级的“模型 DNA”：比如 **Antigravity 官方 CLI** 在 A 题画出的左上角徽章文案（`海滨骑行 · 2D 鹈鹕自行车`）与 `OMP × Antigravity 反代` **一字不差**，在 D 题独立推导出的 `getattr(unittest.case, "_Outcome", None)` + `addDuration` 修复结构则与 `OMP × AI Studio 反代` **完全同构**。

### 2. 原厂 `agy cli` 直接坐实“旁路思维摘要器”滤镜

为什么肉眼看 AI Studio 和 Antigravity 的 `thinking` 输出像两个性格截然不同的模型？看抓包字符比与原厂 CLI 的直接对照：

| 接入路径与代表场次 | 计费思考 `reasoningTokens` | 可见 `thinking` 字符数 | `字符 / Token` 比值 | 可见思维链文风特征 |
|---|---:|---:|---:|---|
| **OMP × AI Studio 反代**（`D-hydrogen`） | `33,089` | `51,715` | `1.56` | `summary: false`；强制 `**粗体小标题**` + 第一人称口语（甚至带 `I must find it!`） |
| **OMP × Antigravity 反代**（`D-hydrogen-xhigh`） | `82,231` | `142,859` | `1.74` | `summary: true`；冷静的第三人称工程笔记，首句常现 `I'm thinking through how to approach this.` |
| **Antigravity 官方 CLI**（`A/B/C/D-agy-cli`） | 订阅制未暴露 | 折叠摘要行 | — | **原厂界面原封不动出现**：B 题 `(I'm thinking through how to approach this.)`、C 题 `(Initial observation: ...)`、D 题 `(Executing test scripts...)` |

两条关键结论一目了然：
- **可见文本只是旁路摘要，不是原始思维链**：正常英文 `1 token ≈ 4 字符`，而实测可见 `thinking` 除以计费思考 Token 仅 **`0.91 ~ 1.78` 字符/token**（单轮加密签名块体积最高达 `45.1 KB`）。这证明前端看到的只是两条业务管线各自挂载的**下游旁路摘要器（Thought Summarizer）**简报，不会反向进入主模型上下文，更不影响主模型智商。
- **原厂 CLI 一锤定音**：未经任何第三方网关的原厂 `agy cli` 吐出了与 Antigravity 反代一模一样的固定开场白与第三人称诊断句式，证实这套摘要模板 100% 出自谷歌 Antigravity 官方服务端。

---

## 二、思考长度差异与三方行为规模同台比对

剥开摘要器文风后，三条路径在工程行为与思考配额上的真实关系非常清晰：

| 对比维度 | OMP × AI Studio 反代 (`xhigh`) | OMP × Antigravity 反代 (`xhigh`) | **Antigravity 官方 CLI（原厂直连）** |
|---|---|---|---|
| **客观题得分（B / C / D）** | **7/7 · 41/41 · 11/11** | **7/7 · 41/41 · 11/11** | **7/7 · 41/41 · 11/11** |
| **A 题视觉自检方式** | 调 OMP 内置 `browser` 截图 2 轮 | 调 OMP 内置 `browser` 截图 4 轮 | **自写 PowerShell 拉临时浏览器配置目录（`$tmpProf`）自检改画** |
| **四题工具 / 动作总数** | **104 次** | **172 次** | **152 次**（67 读 / 16 改 / 69 命令，0 联网） |
| **450 字无工具盲测思考量** | `10,676` tok（`56.7s`） | **`35,463` tok（`3.32×`，`173.1s`）** | — |
| **正式四题累计思考 / 耗时** | 思考 **`53.7k` tok**；总墙钟 **`13m57s`** | 思考 **`150.8k` tok（`2.81×`）**；总墙钟 **`25m09s`** | **CLI 累计思考计时 `20m17s`¹**（A `4m20s` / B `4m53s` / C `1m47s` / D `9m17s`） |

> ¹ **官方 `agy cli` 计时口径严谨注记**：`agy cli` 界面显示的 `Thought for ...` 累加的是各轮模型思考流耗时（已含最终回复前的短思考如 `5s, 178 tokens`），但**未计入本地命令执行耗时以及最后一段文字/代码流式输出时间**（如 A 题思考计 `4m20s`，而磁盘上 `index.html` 从首次创建到自检改定实际横跨 `8m39s`）。算上 152 次本地动作与输出流时间后，**原厂 `agy cli` 的真实端到端耗时、动作密度（152 次 vs 172 次）与 `OMP × Antigravity 反代`（`25m09s`）几乎严丝合缝处在同一水位**。

顺带放进同一个满血 `OMP` 的跨模型纵向坐标里看：此前 [`GLM-5.3（满血开箱）`](../experiments/glm-5.3-full-harness/README.md) 两轮独立运行均耗时 `25m02s`、D 题全部卡在 `10/11`、A 题只能用无头浏览器查报错与 DOM 矩阵；而 Hydrogen 无论是走 OMP 还是原厂 `agy cli`，全部一次推穿 D 题 `11/11` 并自发完成浏览器渲染审图闭环。

---

## 三、客观评价总结（不做反代推荐）

鉴于反代 Antigravity 的极高封号代价（再次警示本次反代测评直接折损一个 **Gemini Ultra 5x** 账户），本文**不做任何反代使用推荐**，仅基于三方实测给出四条客观结论：

1. **当前这套简单题库已触顶，暂无法从得分上区分不同思考长度的干活表现**：
   - 现有 A/B/C/D 四题对 Hydrogen 级别模型偏简单，AI Studio 反代、Antigravity 反代与 Antigravity 官方 CLI 三方全部轻松满分。因此，**仅凭本套简单题库目前的结果，还看不出同设 `xhigh` 下不同思维链长度给实际工作性能带来的区别**。
2. **相对可以确认谷歌并未如网传在 AI Studio / Antigravity 部署不同模型**：
   - 综合 Tink 加密签名包头同源、原厂 `agy cli` 印证的摘要器模板特征，以及跨客户端高度一致的代码与 SVG 细节，**可以相对确认两边跑的是同一套 Hydrogen 模型权重**，并非“一套满血、一套残血”。
3. **两边内部预设提示词是否带来性能差异目前尚无法判断**：
   - AI Studio、Antigravity 以及原厂 `agy cli` 各自注入的系统预设提示词（System / Meta Prompt）与工具封装在更极限场景下是否会拉开表现差距，在当前饱和题库下无法下定论（唯一能直观看到的是：没有内置 `browser` 工具时，Hydrogen 在 `agy cli` 里也会自己写命令调系统浏览器兜底）。
4. **按思维链预算对标推算，Antigravity 渠道至少不可能输给 AI Studio 渠道**：
   - 从同开 `xhigh` 时的真实思考释放量（`53.7k` vs `150.8k`）以及原厂 `agy cli` 高达 `20m17s` 的纯思考时长来看，**笔者可以简单假定：AI Studio 渠道 `xhigh` 给到的思维链长度大致等效于 Antigravity 渠道的 `high` 档**，而 Antigravity 的 `xhigh` 放开了更长一档的思考预算。
   - 按照推理模型寻常评测经验——“同源底座下，有效思维链越长、复杂任务容错越稳”——**至少在模型硬上限上，Antigravity 渠道不可能输给 AI Studio 渠道**。后续若要实测测出多出来的两倍思考预算究竟能换回多少准确率增量，则需要升级到无法靠跑单测试错兜底的高难度构造题或跨模块并发深水区题库。
