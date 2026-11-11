# Model × Harness Fieldtest

同一个模型，换个 API 渠道、换个日常顺手的客户端，干活的手感到底差多少？

平时大家看排行榜看腻了，但真到自己写代码、修 bug 的时候，总会犯嘀咕：第三方中转的权重和官方是不是一回事？同一个模型塞进 OMP 和 Claude Code 里，出来的东西会有多大区别？与其空想，不如挑几道能看见成品、能跑通测试的活儿，直接拉出来溜溜。

| 实验记录 | 对比组合 | 看点 |
|---|---|---|
| [GLM-5.3-Flash](experiments/glm-5.3-flash/README.md) | 智谱官方 API × OMP / Claude Code | 同题两轮重跑：方差大过客户端差异；B 有“只修方法不修根因”的样本，D 两组独立写出 11/11、一组早调清理掉到 7/11 |
| [GLM-5.3](experiments/glm-5.3/README.md) | 智谱官方 API × OMP / Claude Code | 两轮：B/C 饱和、D 拉出方案光谱；第二轮 Claude 经 pip download 读上游，分数保留、剔除独立比较 |
| [DeepSeek V4.1 Flash 1017](experiments/deepseek-v4.1-flash-1017/README.md) | OpenCode Go / 官方 API × OMP / Claude Code | 2D 鹈鹕骑车、Requests / Pytest 真实修 bug、算法题，以及测试途中踩的几个大坑 |

这里的规矩很简单：用平时跟助手说话的方式发指令，不塞一整套评分细则，也不给算法提示。模型自己找文件、改代码、跑测试；交卷之后我们直接打开网页看画面、起服务验逻辑、用对拍和回归套件卡边界。

测试途中踩的坑、超时的半成品、甚至因为目录没隔离好导致模型“偷看”隔壁答案的乌龙，全都原样留着。补测就单开记录，绝不拿最好看的一次偷偷覆盖旧档。

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
