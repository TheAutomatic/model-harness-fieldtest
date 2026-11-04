> 历史阶段报告：路径及原始日志位置对应本地私有档案；共享目录映射见实验 README。模型实验版本：DeepSeek V4.1 Flash 1017；OpenCode 精确快照未独立证实。

# OpenCode Go → Claude Code：2号首跑

本轮实际调用 Claude Code 2.1.318，当前用户配置的 https://opencode.ai/zen/go，模型请求 deepseek-v4.1-flash[1M]，所有响应模型均为 deepseek-v4.1-flash。A/B/C/D各一次，没有补测，没有启动官方4号或重跑OMP。

## 结论

A/B/C显示同一OpenCode模型放进Claude Code后仍能正常交付，没有一致变强或变弱的现象：A视觉更丰富但同样超时；B更快且通过；C更慢但也通过。D2受到已有答案和评测材料污染，作废，不能用于能力比较。这是主持人未做好文件隔离的实验设计缺陷，不能把抄到参考实现后的通过率算作Claude的独立能力。

## 与同来源OMP的对照

| 题目 | OpenCode → OMP（1号） | OpenCode → Claude Code（2号） |
|---|---|---|
| A 鹈鹕 | 可用页面；300.315秒超时 | 可用页面，装饰更丰富；300.424秒超时 |
| B 重定向bug | 7/7；152.940秒 | 7/7；45.194秒 |
| C 算法 | 41/41；27.498秒 | 41/41；46.742秒 |
| D 困难修复 | 10/10且额外清理错误边界通过；332.297秒 | **作废：跨目录读取既有答案**；390.762秒 |

这些是整段代理执行时间，非纯模型推理速度；不同时间运行，缓存和服务负载不同。每题一次不能判断稳定排名。

## 实际验收

A2：实际用Edge以1000×700、deviceScaleFactor=1打开本地index.html，无观察到的页面错误。鹈鹕、车架、骑乘关系明确；头盔、围巾、海边长廊、灯塔、花朵和篮子等细节较丰富。截图见control/results/A2/screenshot.png。主程序在5分钟硬时限被停止，留下可用HTML，没有最终答复。主观粗评分10/10，不是盲评。

B2：独立HTTP验收7/7，原始POST→303→GET→307问题已修复，其他方法、body及认证头检查通过。

C2：独立验收41/41，包含样例、边界、随机小数据暴力对拍和最大规模。

D2：交付代码确实通过10/10和清理错误诊断，但日志显示它通过Bash先读取D1/D3的实现，阅读D-PLAN.md、RESULTS.md、verify_d.py、diagnose_cleanup.py，随后参考D1修复并运行主持人验收。最终回答的验收细目来自泄漏材料，不应算独立发现。完整证据：control/claude-contamination-audit.json；作废标记：control/results/D2/validity.json。最终代码保留，不覆盖、不删记录，不自动重跑。

A2/B2/C2的完整工具调用审查未发现读取已有组答案或主持人评测材料的记录。额外核查既有OMP D1/D3，未发现对应越界读取；见control/omp-D-contamination-audit.json。

## 费用和参数限制

不直接比较美元费用：Claude对该自定义模型的modelUsage标注costBasis=unknown、provider=firstParty，其显示费用没有被证实采用DeepSeek/Go的真实价格。原始值仅作为日志保存，不能用来断言Claude更贵。A2被硬停止，没有完整result/usage，费用留null。

同样传high，单响应输出上限环境变量设8192，但Claude结果模型元数据仍显示maxOutputTokens=32000，未抓包验证实际请求，不能声称token预算完全一致。thinking_tokens显示0也不能证明未思考，日志同时存在thinking_tokens系统事件。保留参数解释限制，不把不同客户端字段硬当成完全等价。

## 文件与隔离

- 交付：A/A2/index.html、B/B2、C/C2/main.py、D/D2（无独立比较效力）。
- 逐题日志：control/results/<编号>/stdout.jsonl、stderr.txt、run.json、summary.json。
- B/C/D独立验收：对应目录verification.json。
- 唯一提示：prompts/A.txt至D.txt，哈希与最初冻结一致。
- 启动器：control/run_claude.py；新配置目录、新会话，关闭额外规则、skills、hooks、MCP和子代理，只开放本地工具。未修改用户日常Claude设置，也未把密钥写进测试包。
- 致命限制：工作目录分离不是安全隔离；开放Bash且未使用OS沙箱，D2实际读到了上级目录。之后如要重测困难题，必须先把旧答案/验收移到候选进程不可访问的位置，或启用真正的文件系统沙箱，再使用新题或明确另记补测。
