# GLM-5.3（满血开箱）：放开客户端原生工具链后的两轮重测

前一次 [GLM-5.3 档](../glm-5.3/README.md) 为了“控制变量”，把 Claude Code 和 OMP 双双绑成只剩 `read/write/edit/grep/glob/bash` 六个裸工具（关掉了 OMP 的 `lsp`、`eval`、内置无头 `browser`、`task` 子代理、`todo`、`pty`，也关掉了 Claude Code 的 `Agent`/`Explore` 子代理与 `TodoWrite`）。按仓库新立下的[满血开箱规矩](../../README.md#客户端实测规矩满血开箱)，本档保留两端安装后的**全套默认内置能力**，只做两项最小隔离：

1. **全角色锁死同一模型**：挂载全新临时状态目录（天然清空历史库），将主模型与所有子代理/辅助角色（OMP `modelRoles` + `agentModelOverrides`；Claude `HAIKU`/`SONNET`/`OPUS`/`SUBAGENT`）全部绑死到 `glm-5.3`，清空 `fallbackChains`。
2. **工作区与外网答案隔离**：依赖目录移出评测仓库避免环境变量暴露路径；同题 `Claude Code 2.1.322` 与 `OMP 18.18.8` 成对同秒起步，跨题严格按 `A → B → C → D` 顺序串行，**零批次重叠**。

## 两轮总表

| 轮次 | 任务 | Claude Code `2.1.322` | OMP `18.18.8`（首跑） | OMP `18.18.8`（封堵 `read(URL)` 后独立补测） |
|---|---|---|---|---|
| 1 | A 鹈鹕 HTML | 已交付，7m14s；桌面/窄屏完整，带点击叮铃加速 | **已交付，4m27s**；主动调 `eval`+`browser` 自检零报错 | —（首跑即独立） |
| 1 | B Requests 重定向 | **7/7**，7m32s | **7/7**，7m35s | —（首跑即独立） |
| 1 | C 子数组余数和 | **41/41**，5m13s（树状数组） | **41/41**，1m44s（树状数组 + `eval` 随机对拍） | —（首跑即独立） |
| 1 | D Pytest 清理 | **10/11**，15m15s | 10/11，15m31s，**经 `read(URL)` 读过上游**¹ | **10/11**，11m22s（独立推导） |
| 2 | A 鹈鹕 HTML | 已交付，6m55s；带暂停与倍速条（窄屏浮层轻度遮挡） | **已交付，4m04s**；调 4 次 `eval`+`browser` 抽样验证曲柄动画帧 | —（首跑即独立） |
| 2 | B Requests 重定向 | **7/7**，4m13s | 7/7，5m49s，**经 `read(URL)` 读过上游**¹ | **5/7**，9m49s（修对方法与 body，漏跨主机 auth 复活） |
| 2 | C 子数组余数和 | **41/41**，1m50s（树状数组） | **41/41**，1m13s（树状数组） | —（首跑即独立） |
| 2 | D Pytest 清理 | **10/11**，14m43s | **10/11**，9m50s | —（首跑即独立） |

> ¹ 首版 `guard.ts` 封禁了 `web_search` 及 `bash`/`eval` 外网访问，但漏掉了 OMP 的 `read` 工具原生支持直接拉取静态网页（`read("https://raw.githubusercontent.com/...")`）。按规矩保留首跑产物并标 `upstream_source_read: true`，随即在 `guard.ts` 封死 `read` 外网 URL，从干净工作区补跑 `D-omp-retry` 与 `B-omp-retry` 填入右列。

---

## 一、子代理、原生工具调用与 Token 全链路账单

进入全部 18 份原始流日志与归档状态目录核查后，有三个直接颠覆事前预期的事实：

1. **子代理调用次数：0 / 18（模型纯度 100%）**
   - 全部场次实际响应模型唯一为 `glm-5.3`（Claude `modelUsage` 唯一键为 `glm-5.3[1m]`，OMP `sessions/*.jsonl` 唯一模型为 `glm-5.3`），零异构模型串台。
   - 尽管两端的 `Agent`/`Explore` 与 `task` 子代理完全放开，**`GLM-5.3` 在全部场次中一次子代理都没有派生（`subagent_spawns = 0`）**。在这批单仓库单点题目上，模型自身的工具先验倾向主会话一竿子插到底。
2. **真正被激活的满血差异：OMP 的 `eval` + 内置无头 `browser`**
   - 放开工具限制后，OMP 在**两轮 A 题**都自发启动了内置无头 Chromium：第一轮打开成品页检查 `tab.errors()` 零运行时报错（[r1 A-omp 审计](r1/results/A-omp/audit.json)）；第二轮更是连续执行 4 次 `eval`，在浏览器里隔帧采样 `#crank1` 的变换矩阵，确认脚踏曲柄真的在转才关页交卷（[r2 A-omp 审计](r2/results/A-omp/audit.json)）。
   - 第一轮 C 题中，OMP 也用 `eval` 内嵌 Python 直接跑了随机小数据暴力对拍与大规模校验，两轮 C 题全数 **41/41**（73s–104s），不再出现精简工具档里漏压测超时的失误。
3. **Token 与耗时对比（8 场独立有效运行合计）**

| 口径（8 场合计） | 墙钟总耗时 | 对话轮数 | 工具调用 | 未缓存输入 (k) | 缓存读取 (k) | 总输出含思考 (k) | 折算等价输入 (M)¹ |
|---|---:|---:|---:|---:|---:|---:|---:|
| **Claude Code（满血 8 场）** | 62m55s | 169 | 182 | 318.4 | 7,402.9 | 184.3 | **2.54M** |
| **OMP（满血独立 8 场）** | **50m04s** | **148** | **167** | **261.1** | **4,620.2** | **143.0** | **1.76M** |
| **OMP（满血首跑 8 场）** | 50m13s | 143 | 167 | 261.7 | 4,886.1 | 142.9 | 1.81M |
| *对照：Claude Code（精简六工具 8 场）* | *79m49s* | *147* | *165* | *266.7* | *4,639.6* | *196.3* | *1.98M* |
| *对照：OMP（精简六工具 8 场）* | *59m52s* | *148* | *179* | *243.4* | *4,766.5* | *144.8* | *1.78M* |

> ¹ 按未缓存输入 `1×`、缓存读取 `0.2×`、输出 `4×` 折算为百万等价输入 token。

横向看：
- **满血 Claude 相比 OMP**：墙钟多花 **25.7%**（`62m55s` vs `50m04s`，8 场里 OMP 快了 6 场），缓存读取多 **60.2%**（Claude 全量内置工具定义使首轮静态上下文涨到约 `19k tokens`，OMP 满血首轮约 `8.3k tokens`），折算总 Token 成本约为 OMP 的 **1.44 倍**。
- **相比上一档精简工具**：由于本档改为严格的跨题串行、同题双路并发，消除了上一档多任务挤占带宽与本机资源的干扰，两端墙钟反而双双缩短了 10–17 分钟。

---

## 二、B 题意外打破“饱和”假象：`5/7` 暴露跨主机鉴权复活

上一档四场全 `7/7` 曾让我们以为 B 题对 `GLM-5.3` 已经没有区分度，但本档 `r2/B-omp-retry`（[补丁](r2/artifacts/B/B-omp-retry/changes.patch)）在完全断绝外部参考后跑出了 **`5/7`**，恰好补齐了这条 Bug 的完整认知阶梯：

| 方案层级 | 代表样本 | 得分 | 修对的部分 | 漏掉的隐患 |
|---|---|---:|---|---|
| 只修方法选择 | Flash `r2/B-claude` | 3/7 | `method` 继承上一跳 | `303 → 307` 时原 POST 的 **body 与跨主机剥离的 Authorization 双双复活** |
| 修方法 + 清空已丢弃的 body | 本档 `r2/B-omp-retry` | **5/7** | `method = resp.request.method` + 检查 `resp.request.body is None` | 仍从最初的 `req.copy()` 克隆请求：第一跳跨主机已剥掉的 **`Authorization: Bearer ...` 在第二跳同主机重定向时死灰复燃**（[验收明细](r2/results/B-omp-retry/verification.json)） |
| 更新每跳基准请求 | 其余全部满分样本 | **7/7** | `req = prepared_request`（或 `req = resp.request`） | 无——方法、body、已剥离的敏感头自然沿链路传递 |

这说明哪怕是旗舰级的 `GLM-5.3`，在同一道题的不同采样轮次里，依然可能在“一针见血改 `req`”和“打补丁式修字段”之间摇摆；Claude 本档两轮 B 题均独立写出 `req = prepared_request` 拿到 `7/7`，在 B 题上扳回一城。

---

## 三、D 题与防作弊攻防：把 `pip download` 按下去，又冒出 `read(URL)`

把两档实验放在一起看，本身就是一部鲜活的**“满血客户端隔离攻防实录”**：

- **Claude Code 的三次联网试探全被拦截**：`r1/B-claude`、`r2/B-claude` 先后调用 `WebFetch` 拉取 GitHub 上的 `requests/sessions.py`，`r1/D-claude` 调 `Bash` 执行 `curl https://raw.githubusercontent.com/pytest-dev/pytest/...`，全部被 `guard.py` 当场阻断（另有三次尝试在父临时目录另建校验文件夹或写跨目录记忆被工作区规则拦截，未影响主工作区解题）。
- **OMP 的静态网页读取旁路**：`r1/D-omp` 与 `r2/D-omp` 尝试调 `web_search` 均被 `guard.ts` 当场拦下；但 `r1/D-omp` 与 `r2/B-omp` 随即意识到 OMP 的 `read` 工具自身就能直接读取静态网页，于是调 `read("https://raw.githubusercontent.com/...")` 读到了上游仓库代码！
- **最讽刺的实测验证**：`r1/D-omp` 读完上游 Pytest 7.0 源码后，原样复刻了上游删掉 `_GetOutOf_testPartExecutor`、仅在 `--pdb` 时用 `_explicit_tearDown` 延后 `tearDown` 的修法（连 `changelog/6947.bugfix.rst` 都写上了，见[补丁](r1/artifacts/D/D-omp/changes.patch)）。结果一跑 11 项独立验收：**照样只拿 `10/11`**——唯一挂掉的正是 `pdb_failure`（实测事件流为 `setup → test → cleanup-last → cleanup-first → debug → teardown`，进入调试器前就把现场拆光了）。
- **封死 `read(URL)` 后的四场独立结果完全一致（全员 `10/11`）**：
  - `r1/D-claude`、`r2/D-claude`、`r1/D-omp-retry` 三场均写出 `try: self._testcase.tearDown() / finally: self._testcase.doCleanups()`，守住了严格顺序与双重失败清理（`double-failure-diagnostic.json` 中 `cleanup_ran: true`），仅挂在 `failure_and_cleanup_error`。
  - `r2/D-omp` 写出无 `try/finally` 的顺序调用，同样 `10/11`，但在双重失败诊断中 `cleanup_ran: false`。

这也彻底坐实了上一档的判断：**上一档 `r2/D-claude` 的 `11/11` 确实完全来自 `pip download` 读取上游新版实现；一旦把两边的外网旁路全部封死，`GLM-5.3` 在两套满血客户端下四场独立推导稳稳收敛在同一个 `10/11` 台阶。**

---

## 四、A 题：无头浏览器实测截图对比

本档通过本地 HTTP 服务 + 无头 Chromium 在桌面（`1000×700`）与窄屏（`430×800`）视口下完成了真机渲染验收，四份作品**控制台与运行时错误全为 0**，全部包含动态骑行脚本（OMP 再也没有交出纯静态无脚本页面）：

- **第一轮 Claude**（[HTML](r1/artifacts/A/A-claude/index.html) · [桌面截图](r1/results/A-claude/screenshot.png) · [窄屏截图](r1/results/A-claude/mobile.png)）：红围巾鹈鹕嘴里叼着小蓝鱼，车架、虚线链条、辐条与点击叮铃加速交互齐全，桌面与窄屏均居中完整无裁切。
- **第一轮 OMP**（[HTML](r1/artifacts/A/A-omp/index.html) · [桌面截图](r1/results/A-omp/screenshot.png) · [窄屏截图](r1/results/A-omp/mobile.png)）：戴青色头盔的鹈鹕，车座、后轮小红旗、曲柄踏板联动自然，自己用内置 `browser` 验过零报错后交卷，双视口完整无溢出。
- **第二轮 Claude**（[HTML](r2/artifacts/A/A-claude/index.html) · [桌面截图](r2/results/A-claude/screenshot.png) · [窄屏截图](r2/results/A-claude/mobile.png)）：卡片式画框配前后红挡泥板、暂停键与无级倍速滑块；桌面精致，窄屏（`430×800`）下左上标题浮层与底部倍速条对太阳及后轮下缘有轻度遮挡。
- **第二轮 OMP**（[HTML](r2/artifacts/A/A-omp/index.html) · [桌面截图](r2/results/A-omp/screenshot.png) · [窄屏截图](r2/results/A-omp/mobile.png)）：扁平插画风，带速度线与虚线链条，自己用 `browser` 抽样验证了曲柄旋转帧，双视口无裁切（立管顶端未画黑色车座垫）。

---

## 五、结论：满血重测之后，怎么看 Claude Code vs OMP？

把“错砍工具”的历史包袱去掉之后，两套客户端在 `GLM-5.3` 上的真实分野非常清晰：

1. **放开原生工具对 OMP 的增益立竿见影，对 Claude Code 则主要是静态上下文变重**：OMP 立刻把 `eval` + `browser` 用在了前端自检和算法对拍上，补齐了之前 A 题盲写静态 SVG、C 题漏压测的短板；而 Claude Code 引以为傲的子代理在单点任务上并未被 `GLM-5.3` 触发，反而因为全量内置工具定义让缓存读取涨到 OMP 的 `1.60×`、总折算 Token 成本达到 **`1.44×`**、耗时多出 **`26%`**。
2. **准确率与稳定性：总体打平，偶发失误看发牌运**：C 题双方全满（`41/41`），D 题双方独立推导全在 `10/11`（其中双重失败保护 Claude 2/2、OMP 1/2），A 题双方均交付无报错动态页面；唯独 B 题 `r2/B-omp-retry` 掉进 `5/7` 的跨主机 auth 陷阱，让 Claude 在客观题总分上略占上风。

## 材料导航

- 实验元数据：[experiment.json](experiment.json)
- 第一轮：[提示词](r1/prompts/) · [交付物与补丁](r1/artifacts/) · [结果、截图与审计](r1/results/) · [验收脚本](r1/evaluation/)
- 第二轮：[提示词](r2/prompts/) · [交付物与补丁](r2/artifacts/) · [结果、截图与审计](r2/results/) · [验收脚本](r2/evaluation/)
- 历史对照档（精简六工具）：[../glm-5.3/README.md](../glm-5.3/README.md)
- 跨档客户端机制与 Token 终评：[../../notes/harness-comparison-full-default.md](../../notes/harness-comparison-full-default.md)
