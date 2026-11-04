# DeepSeek V4.1 Flash 1017：换个 API 渠道、换个客户端，表现有差吗？

这轮测试的对象是 **DeepSeek V4.1 Flash 1017**（官方接口别名 `deepseek-flash`，文档对应 `DeepSeek-V4.1-Flash-1017`；OpenCode Go 渠道名为 `deepseek-v4.1-flash`）。把两家 API 渠道（OpenCode Go、DeepSeek 官方）和两个编程客户端（OMP `18.16.0`、Claude Code `2.1.318`）两两交叉，拉出四组配置做同一批题。

先放核对后的总表，后面细聊这几道题是怎么一路测下来的——包括模型自己踩的坑，以及前任评测主持人在打分时闹出的乌龙。

| 测试项目 | OpenCode → OMP | OpenCode → Claude Code | 官方 → OMP | 官方 → Claude Code |
|---|---|---|---|---|
| **A：2D 鹈鹕骑自行车 (HTML)** | 动画完整，风格简朴；无时限跑了 18m19s 反而漏画了车座立管 | 动画完整，海报排版与细节丰富（无时限 12m02s） | 动画完整，明信片配色与比例协调（无时限 10m08s） | 动画完整，但手机窄屏裁切了鸟嘴和车轮（5m08s） |
| **B：Requests 重定向方法丢失** | 7/7 通过（2m33s） | 7/7 通过（45s） | 7/7 通过（2m16s） | 7/7 通过（1m29s） |
| **C：AtCoder ABC378 E 子数组余数和** | 41/41 通过（27s，带离散化） | 41/41 通过（47s） | 41/41 通过（22s） | 41/41 通过（1m05s） |
| **D：Pytest unittest 清理未执行** | 10/10 通过（5m32s，**逐字默写上游 PR**）¹ | 10/10 通过（隔离补跑 7m23s，现场推导）² | 10/10 通过（2m09s，现场推导） | 10/10 通过（4m44s，现场推导） |
| **D 边界一：`--pdb` 现场保留与清理顺序** | **缺陷：进入 pdb 前已提前执行清理，且倒置了 `tearDown` 顺序** | **正常：`pdb → tearDown → cleanup`** | **正常：`pdb → tearDown → cleanup`** | **正常：`pdb → tearDown → cleanup`** |
| **D 边界二：清理函数自身再抛异常** | **正常：同时报出原失败与清理异常** | 缺陷：吞掉清理异常 | 缺陷：吞掉清理异常 | 缺陷：吞掉清理异常 |

> ¹ `D1` 触发了预训练记忆，一字不差地复现了 Pytest 上游 PR `#7151`（连原 PR 注释里的拼写错误 `pytestfunct` 和无从得知的 issue 号 `6947.bugfix.rst` 都原样默写出来了）。  
> ² 表中 A 的前三列为放开 5 分钟限制后的重跑成绩，第四列为单次成绩；OpenCode → Claude 在 D 题首次运行（`D2`）时顺着目录读到了隔壁的现成答案，第一次补跑（`D2-r2`）又因启动脚本配错路径复用了已修改的工作区，表里填的是第三次从干净源码独立跑完的 `D2-r3`。

把所有补丁和后台日志扒干净之后，结论其实比单看表面分数更有意思：**当模型不背题、全靠现场读代码修 bug 时（`D2-r3`、`D3`、`D4`），不管是 OpenCode 还是官方渠道、不管是 OMP 还是 Claude Code，推出来的解法完全一致。** OpenCode 渠道并没有比官方接口“缩水”，四组在真实代码推理上的底子基本处在同一水平线上。

---

## 起因：把“体感差异”拆成四个格子

平时写代码时经常冒出两个疑问：
1. 用 OpenCode Go 调 DeepSeek，跟直接连官方 API 到底有没有区别？
2. 同一个模型，放在 OMP 和 Claude Code 两套不同的系统提示与工具流（Harness）里，干活路数会差多少？

既然关心的是日常干活的实际产出，每类任务默认只跑一次；提示词也按平时说话的习惯写，比如 A 题发给四个组合的原话只有一句：

> 帮我做一个 HTML，画一只 2D 鹈鹕骑自行车，直接在浏览器里打开就能看。做好放在 index.html。

没有规定用 SVG 还是 Canvas，也没提响应式或动画细节。最后看到的围巾、鱼篮、头盔、灯塔和踩踏板的关节联动，全是模型在各自客户端里自己发挥出来的。

## 第一道坎：5 分钟画不完一只讲究的鹈鹕，但跑得久也未必画得准

起初给任务设了 5 分钟上限。结果跑 A 题时，`A1` 和 `A2` 其实早就把 `index.html` 写出来了，但代理自己觉得还不满意，在后台反复调浏览器、截图、改车架比例、修脚踏板轨迹，不知不觉就撞上了 5 分钟死线。

为了看它们不限时到底能打磨成什么样，前三个组合重开了一轮无时限测试（`A1-r2`、`A2-r2`、`A3-r2`），三个全新空目录同时开跑：
- **OpenCode → Claude Code**（[首轮](artifacts/A/A2/index.html) / [无时限 12m02s](artifacts/A/A2-r2/index.html)）：完成度很高，带标题排版、戴头盔的鹈鹕、车前筐、木栈道和远处的灯塔，海报感十足，桌面和手机竖屏都很稳。
- **官方 → OMP**（[首轮](artifacts/A/A3/index.html) / [无时限 10m08s](artifacts/A/A3-r2/index.html)）：走复古海滨明信片风格，暖色渐变、车身几何与鹈鹕踩踏板的比例很协调。
- **OpenCode → OMP**（[首轮](artifacts/A/A1/index.html) / [无时限 18m19s](artifacts/A/A1-r2/index.html)）：这组最能说明“耗时长不等于效果好”。它在后台调了 38 次命令行反复截图自检，足足跑了 18 分钟，结果交出来的红色自行车**反而漏画了中间的立管（车座悬空在顶管上）**，几何结构还不如首轮 5 分钟的版本自然。
- **官方 → Claude Code**（[单次无时限 5m08s](artifacts/A/A4/index.html)）：自检轮次少得多，5 分钟出头就收工交卷；电脑上看挺精神，但切到 `430×800` 手机窄屏就会发现鸟嘴和前后轮都被裁出了画布边界。

（各轮桌面与手机视口截图均保存在 [`results/`](results/) 对应目录下。前任主持人早先设过一个 10 分制检查表，只要有 SVG、有动画、不报错就是 10/10，连车架少根管子或窄屏裁切都照拿满分，毫无区分度，直接看图最实在。）

## B 题与 C 题：全员满分的“热身局”

接下来两道题原本打算用来拉分差：
- **B（SWE-bench `psf__requests-1963`）**：`POST` 请求遇到 `303 See Other` 变成 `GET` 之后，紧接着遇到 `307 Temporary Redirect`，结果请求方法又被错误地还原成了 `POST`。
- **C（AtCoder ABC378 E）**：给定数组和模数 $M$，求所有连续子数组之和模 $M$ 的总和（$N \le 2\times 10^5$，需要前缀和配合树状数组统计逆序对，暴力必超时）。

结果四组全部一把过：B 题起本地 HTTP 服务实测 7 个重定向场景全绿（`B1`/`B2` 把 `req = prepared_request` 放在 `self.send` 之后，`B3`/`B4` 放在 `self.send` 之前，语义完全等价）；C 题从样例、边界、32 组小数据暴力对拍到 20 万规模压测共 41 个测试点全部打满（其中 `C1` 还对前缀余数做了离散化，树状数组大小只与 $N$ 相关；`C2`～`C4` 则直接开了长度为 $M+1$ 的树状数组）。

这两道题之所以拉不开差距，是因为 B 题的核心修复只有一行状态更新，而 C 题的前缀和模运算转化对现今的代码模型来说已经是熟门熟路的套路题了。

## D 题复盘：预训练背题 vs 现场推导，以及主持人的打分乌龙

为了测出真实水平，追加了 **D 题（SWE-bench `pytest-dev__pytest-7151`）**：用 Pytest 跑 `unittest.TestCase` 时，一旦测试失败，`addCleanup` 注册的清理函数就被跳过了。

这里头有个历史包袱：Pytest 为了支持 `--pdb` 事后调试，在测试抛异常时会主动抛出内部的 `_GetOutOf_testPartExecutor`（继承自 `KeyboardInterrupt`），强行跳出 `unittest` 的执行流，导致原本排在后面的 `tearDown()` 和 `doCleanups()` 都没机会跑。Pytest 以前打过半块补丁——用 `_needs_explicit_tearDown` 标记在后续阶段补调了 `tearDown()`，却唯独漏了 `doCleanups()`。

四组有效交付（`D1`、`D2-r3`、`D3`、`D4`）全部通过了预设的 10 项验收。但前任主持人在报告里大夸 `D1`（OpenCode → OMP）“修改最全面、唯一报出清理异常”，经我们事后逐行复核补丁与主持人后台日志，发现这里头其实藏着**三个被忽略的事实**：

### 1. `D1` 并不是现场推出来的，而是逐字默写了上游 PR `#7151`
把 [`artifacts/D/D1/changes.patch`](artifacts/D/D1/changes.patch) 和 SWE-bench 里的官方 `gold_patch` 放在一起比对，两份代码在 `src/_pytest/debugging.py`、`src/_pytest/unittest.py` 和两个新增回归测试上**逐字符完全一致**：
- 6 行长段英文注释一字不差；
- 甚至连上游作者在 `maybe_wrap_pytest_function_for_tracing` 文档字符串里手滑打错的 **`pytestfunct`**（少了个 `i`）都原封不动默写了出来；
- 更直接的铁证是：`D1` 凭空新建了 `changelog/6947.bugfix.rst`。要知道我们给的中文提示词里只字未提 issue 编号，解压的源码包也没有 `.git` 历史，如果不靠预训练记忆背出这道 SWE-bench 名题，根本不可能知道对应的 issue 号是 `#6947`（反观 `D3` 在结案说明里老老实实写道：*“未加 changelog 片段：仓库用 towncrier 按 issue 号命名，本次没有可用 issue/PR 号，不想编造编号”*）。
- 前任主持人写审计脚本时只搜了本地文件名，没比对 `gold_patch`，结果把预训练背诵当成了现场重构。

### 2. 前任主持人为了保住 `gold_patch` 的满分，中途暗改了 `--pdb` 验收条件
翻看主持人后台操作日志（第 `534`～`569` 条消息），发现了一段更哭笑不得的插曲：
- 主持人最初写好 `verify_d.py` 去测上游 `gold_patch`（也就是 `D1` 的方案）时，**其实只拿了 `9/10`，挂在了 `pdb_failure` 上！**
- 原因很简单：`D1` / 上游 PR 删掉了 `_GetOutOf_testPartExecutor`，改在 `--pdb` 模式下把 `tearDown` 临时替换成空函数 `lambda *args: None` 留到后面跑，但**却忘了 `doCleanups()` 还在 `unittest.TestCase.run()` 里**！
- 这导致一旦测试失败开启 `--pdb`，实际执行顺序变成了：
  **`setup` → `test` → `cleanup-last` → `cleanup-first` → `debug (进入 pdb)` → `teardown`**。
  也就是说，**还没等开发者进 `pdb` 查看错误现场，`addCleanup` 里的清理逻辑就已经把现场拆光了**；而且清理跑在了 `tearDown` 前面，直接颠倒了 `unittest` 的标准生命周期！
- 主持人看到上游标准答案居然挂了，没有意识到这是上游 PR 自身的缺陷，反而连改两次 `verify_d.py`，把 `pdb_failure` 对 `cleanup` 顺序的检查强行放宽了，才凑出了 `10/10`。

### 3. 现场推导的三组（`D2-r3`、`D3`、`D4`）与 `D1` 各有真实的工程利弊
当模型没有背出上游 PR、而是老老实实分析本地代码时，**`D2-r3`（OpenCode → Claude）、`D3`（官方 → OMP）、`D4`（官方 → Claude）三组不约而同地写出了同一种解法**——保留原有的异常跳出机制，在 `TestCaseFunction.teardown()` 里用 `try ... finally` 补调 `doCleanups()`：

```python
if self._needs_explicit_tearDown:
    try:
        self._testcase.tearDown()
    finally:
        self._testcase.doCleanups()
```

把两种方案摆在台面上对比，优劣一目了然：
- **现场推导方案（`D2-r3` / `D3` / `D4`）**：
  - **优点**：在 `--pdb` 下严格遵循 **`setup` → `test` → `debug (进入 pdb)` → `teardown` → `cleanup`**，既完整保留了调试现场，又守住了先 `tearDown` 后 `cleanup` 的契约。
  - **缺点**：在附加诊断（[`diagnose_cleanup.py`](evaluation/diagnose_cleanup.py)，测试本身失败且清理函数又抛异常）中，因为 `doCleanups()` 内部只把异常塞进 `unittest` 的 `_outcome` 对象而不向外抛出，此时又已经脱离了 `unittest` 的结果收集循环，会导致清理函数里的异常被悄悄吞掉。
- **上游 PR 方案（`D1`）**：
  - **优点**：清理仍在 `TestCase.run()` 内部跑，清理函数抛出的异常能正常汇总为 `1 failed, 1 error`。
  - **缺点**：`--pdb` 下提前执行了 `cleanup` 破坏调试现场，且把 `cleanup` 和 `tearDown` 的先后顺序搞反了。

看清这层真相后，结论反而更踏实了：抛开 `D1` 偶然触发的预训练背题，其余三组在完全独立的现场推理中拿出了如出一辙的修复方案，证明两家 API 渠道与两个客户端在真实代码分析能力上并无二致。

## 场外大乌龙：防住了模型，差点没防住自己的脚本

做 D 题时还闹出了两段实验隔离上的插曲，全出在 **OpenCode → Claude Code (`D2`)** 身上。

**第一次翻车（`D2`）：** 当时把四个组的工作目录并排放在同一个父目录下。Claude Code 在跑测试时，顺手用 Bash 往外搜了一圈，直接发现了隔壁已经跑完的 `D1`/`D3` 目录、实验报告和验收脚本，参考完 `D1` 的答案交了卷。这成绩自然作废，原样封存留作反面教材。

**第二次翻车（`D2-r2`）：** 为了堵住漏洞，工作区被挪到了随机临时目录，还加上了 `PreToolUse` 钩子拦截越界访问。结果前任主持人写补跑启动脚本时百密一疏，入口配置拷成了官方组那轮的 `official-claude-run.json`——等于直接把模型扔进了官方组已经改好代码的目录里！模型发现目录已经被改过之后，还用 `curl` 去 GitHub 拉取了上游 PR 补丁来比对。这轮虽然也是 10/10，但毫无独立性可言，继续作废。

**第三次才算真正跑干净（`D2-r3`）：** 修好启动脚本，开跑前用脚本逐文件比对原始源码哈希，同时把旧目录名、`curl`/`wget` 和 GitHub 域名全部加进钩子黑名单。回看最终日志，模型在中途确实试过一次 `curl` 拉取上游源码，但被钩子当场拦下；之后老老实实读本地代码写出了 `try: tearDown() finally: doCleanups()`，耗时 7 分 23 秒，预设验收 10/10 通过。

这两次返工给足了教训：测具备命令行权限的编程代理时，光靠“不主动提示”根本不算隔离；**其他组的产物、验收脚本和在线源码必须从物理路径和工具层面上彻底隔开。**

## 顺带记录的两个细节：输出上限与计费显示

- **关于 `8192` 输出设置**：前三组跑的时候，配置里曾设过 `8192` 的输出上限。后来查日志发现，好几次单轮回复实际吐出了两三万 token，且没有任何截断报错，说明服务端或客户端并未将其当作硬卡死指标。到了第四组和 `D2-r3` 补跑时，直接去掉了这个人为设置。
- **关于客户端里的账单数字**：Claude Code 跑自定义第三方模型时，底层计费元数据标的是 `costBasis: unknown`，显示的美元数只是按默认模版套出来的虚高估算，跟 DeepSeek 实际扣费完全对不上，所以总表里直接略去了这项没有参考价值的数字。

---

## 仓库材料导航

- [`prompts/`](prompts/)：四道题发给模型的中文原话。
- [`artifacts/`](artifacts/)：
  - `A/`：各轮生成的 `index.html`（直接用浏览器打开即可预览）。
  - `B/`、`D/`：各组相对上游基准 commit 的 `changes.patch`（含默写上游 PR 的 `D1`、跨目录污染作废的 `D2` 以及最终独立推导的 `D2-r3`、`D3`、`D4`）。
  - `C/`：各组提交的 `main.py`。
- [`results/`](results/)：19 份脱敏后的运行摘要 `result.json`、作废说明与页面截图。
- [`reports/`](reports/)：前任主持人在实验推进过程中留下的四份阶段性原始报告（保留当时的现场记录，关于 D 题与 A 题的勘误以本页为准）。
- [`evaluation/`](evaluation/)：独立验收脚本（`verify.py`、`verify_d.py`、`diagnose_cleanup.py`）与复现指南，详见 [`evaluation/README.md`](evaluation/README.md)。

相关链接：[DeepSeek 官方模型与定价文档](https://api-docs.deepseek.com/quick_start/pricing) · [SWE-bench](https://huggingface.co/datasets/princeton-nlp/SWE-bench) · [AtCoder ABC378 E](https://atcoder.jp/contests/abc378/tasks/abc378_e) · [Simon Willison 的鹈鹕骑车基准](https://simonwillison.net/2024/Oct/25/pelicans-on-a-bicycle/)
