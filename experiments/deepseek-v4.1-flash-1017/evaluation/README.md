# 复现与验收

这些是主持人用的工具，不是给参测模型的上下文。候选只拿prompts和干净原项目，别把答案、patch或本目录一起放进去。

## 准备项目

B：psf/requests，commit `110048f9837f8441ea536804115e80b69f400277`。

D：pytest-dev/pytest，commit `2b51ed46d54be58da6bbcd28f68149b3fc2cd104`。

从固定commit取得干净源码，复制fixtures/B或fixtures/D中的复现入口。D归档缺少setuptools-scm生成文件，需要创建`src/_pytest/_version.py`：

```python
version = '5.4.1'
version_tuple = (5, 4, 1)
```

要检查某份交付，在干净源码上执行`git apply <changes.patch>`，不要应用到已经修过的目录。原项目许可证保留在对应fixtures目录。

## Python与依赖

原实验在Windows/Python3.9执行。旧Requests不适合直接丢给最新Python；这里不捆绑运行时。

D依赖安装到独立目录，通过环境变量`DSTEST_PYTEST_DEPS`传给run_pytest.py。固定版本：

```text
attrs==19.3.0
more-itertools==8.2.0
packaging==20.3
pluggy==0.13.1
py==1.8.1
wcwidth==0.1.9
colorama==0.4.3
atomicwrites==1.4.0
pyparsing==3.3.3
six==1.17.0
```

## 实际验收

从实验目录执行，工作区路径自己提供：

```text
python evaluation/verify.py B <requests-workspace>
python evaluation/verify.py C <algorithm-workspace>
python evaluation/verify_d.py <pytest-workspace>
python evaluation/diagnose_cleanup.py <pytest-workspace>
```

D验收默认用当前解释器，可通过`FIELDTEST_PYTHON`指定Python3.9；依赖环境变量也要保留。verify_d.py是预设10项；diagnose_cleanup.py是后来追加的清理错误诊断，两者不要合并成早已设计好的11项。脚本沿用Windows的NUL配置路径，没验证Linux/macOS，不承诺跨平台一键运行。

A直接用浏览器打开HTML。我们实际看了1000×700桌面及430×800手机视口；截图只是某个动画时刻，网页本身才是完整交付。
