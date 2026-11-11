# Model × Harness Fieldtest

同一个模型，换个 API 渠道、换个日常顺手的客户端，干活的手感到底差多少？

平时大家看排行榜看腻了，但真到自己写代码、修 bug 的时候，总会犯嘀咕：第三方中转的权重和官方是不是一回事？同一个模型塞进 OMP 和 Claude Code 里，出来的东西会有多大区别？与其空想，不如挑几道能看见成品、能跑通测试的活儿，直接拉出来溜溜。

| 实验记录 | 对比组合 | 看点 |
|---|---|---|
| [GLM-5.3（满血开箱）](experiments/glm-5.3-full-harness/README.md) | 智谱官方 API × OMP / Claude Code | 放开客户端默认全套工具重跑两轮：子代理 0 触发，OMP 主动调内置浏览器自检，Token 账单 Claude 约 1.44×；抓到 `read(URL)` 旁路并独立补测 |
| [GLM-5.3-Flash（精简工具）](experiments/glm-5.3-flash/README.md) | 智谱官方 API × OMP / Claude Code | 同题两轮重跑：方差大过客户端差异；B 有“只修方法不修根因”的样本，D 两组独立写出 11/11、一组早调清理掉到 7/11 |
| [GLM-5.3（精简工具）](experiments/glm-5.3/README.md) | 智谱官方 API × OMP / Claude Code | 早期仅开放六个基础工具的两轮记录：B/C 饱和、D 拉出方案光谱；第二轮 Claude 经 pip download 读上游 |
| [DeepSeek V4.1 Flash 1017](experiments/deepseek-v4.1-flash-1017/README.md) | OpenCode Go / 官方 API × OMP / Claude Code | 2D 鹈鹕骑车、Requests / Pytest 真实修 bug、算法题，以及测试途中踩的几个大坑 |

这里的规矩很简单：用平时跟助手说话的方式发指令，不塞一整套评分细则，也不给算法提示。模型自己找文件、改代码、跑测试；交卷之后我们直接打开网页看画面、起服务验逻辑、用对拍和回归套件卡边界。

测试途中踩的坑、超时的半成品、甚至因为目录没隔离好导致模型“偷看”隔壁答案的乌龙，全都原样留着。补测就单开记录，绝不拿最好看的一次偷偷覆盖旧档。

## 客户端实测规矩（满血开箱）

既然测的是 Model × Harness 的真实干活体验，客户端自带的原生工具链与上下文管理机制就是待测本体，控制变量必须守住两条边界：

1. **保留开箱默认全套能力，严禁阉割内置工具**：不传 `--tools` 白名单，不加 `--no-lsp`、`--no-prewalk`、`--no-pty` 等自废武功的开关。让 OMP 带着默认的 `lsp`、`ast_edit`、`eval`（含内置无头 `browser`）、`task` 子代理、`todo` 与 `pty` 上场；让 Claude Code 带着默认的 `Agent`/`Explore` 子代理、`TodoWrite` 与全套原生工具上场。（早期 GLM-5.3 / Flash 档曾把两端削成裸六件套，原档保留作历史对照，后续重测单开新档。）
2. **只做“防模型串台”与“防答案串读”两项最小隔离**：
   - **全角色模型锁死 + 空历史状态**：每次运行挂载全新临时配置目录（`PI_CODING_AGENT_DIR` / `CLAUDE_CONFIG_DIR`，天然隔离本机 `history.db` 历史会话），将主模型与所有子代理/辅助角色（OMP 的 `modelRoles`、`task.agentModelOverrides`；Claude Code 的 `ANTHROPIC_DEFAULT_HAIKU/SONNET/OPUS_MODEL`、`CLAUDE_CODE_SUBAGENT_MODEL`）统一绑死到当前被测模型，清空 `fallbackChains`，防止其他模型在子任务或限流时下场代答。
   - **私有工作区 + 最小防作弊钩子**：每场分配独立随机工作目录与私有临时目录，依赖目录置于仓库外部；钩子仅拦截访问本评测仓库、宿主配置、隔壁工作区，以及外网搜题或拉取上游源码包（`web_search` / `WebSearch` / `WebFetch`、`pip download`、GitHub / PyPI 等外部域名），放行 `localhost` / `127.0.0.1` 本地回环供浏览器预览与本地服务自测。
   - **全链路记账与独立审计**：子代理产生的调用与 Token 一并计入单场总开销；若发生越界读取，分数如实保留、审计单独标记并剔除独立推导比较。

## 目录结构

每次折腾新模型或新客户端，都在 `experiments/` 下单开一档：

```text
experiments/<模型版本>/
  README.md       结果总表与完整测试过程
  prompts/        发给模型的原话
  artifacts/      网页成品、代码、修复补丁 (patch)
  results/        脱敏后的运行摘要与页面截图
  reports/        各阶段的详细记录
  evaluation/     独立验收脚本与复现说明
  experiment.json 版本信息、对比矩阵与上游仓库基准 commit
```

多轮重跑的实验（如 GLM-5.3、GLM-5.3-Flash）在档内再按 `r1/`、`r2/` 分轮存放 `prompts/`、`artifacts/`、`results/` 与 `evaluation/`，总表 README 与 experiment.json 放在档根。

为了控制仓库体积、保护本地环境隐私，这里只放生成的网页、代码补丁、验收脚本和脱敏摘要；不打包上游完整源码、Python 运行时、依赖库或带本机路径的原始会话日志。Requests 与 Pytest 复现片段保留各自的上游许可证。
