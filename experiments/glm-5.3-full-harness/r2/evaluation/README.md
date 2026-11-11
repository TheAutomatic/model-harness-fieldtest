# 本轮复现与验收

所有执行均使用系统 Python 3.13.14。沿用固定的 Requests 与 Pytest 源码提交（见上次实验的源码提交信息），但不沿用历史分数。

## 运行准备

Requests：commit 110048f9837f8441ea536804115e80b69f400277。复制 fixtures/B/reproduce.py 到源码根。将 requests/packages/urllib3/packages/ssl_match_hostname/__init__.py 的 from _implementation import 改为 from ._implementation import。

Pytest：commit 2b51ed46d54be58da6bbcd28f68149b3fc2cd104。复制 fixtures/D 下两个 Python 文件到源码根；创建 src/_pytest/_version.py，设置 version = '5.4.1' 与 version_tuple = (5, 4, 1)。

两组都在根目录加入相同 sitecustomize.py：

```python
import collections, collections.abc, os
for name in ('Mapping', 'MutableMapping', 'Callable', 'Iterable'):
    if not hasattr(collections, name):
        setattr(collections, name, getattr(collections.abc, name))
os.environ['PYTEST_ADDOPTS'] = '--assert=plain'
```

依赖安装在独立目录：attrs==19.3.0、more-itertools==8.2.0、packaging==20.3、pluggy==0.13.1、py==1.11.0、wcwidth==0.1.9、colorama==0.4.3、atomicwrites==1.4.0、pyparsing==3.3.3、six==1.17.0、legacy-cgi==2.6.4。

将 PYTHONPATH 设置为工作区与置于评测仓库外的独立依赖目录，将 DSTEST_PYTEST_DEPS 指向该依赖目录，PYTEST_DISABLE_PLUGIN_AUTOLOAD=1。基线预检确认 Requests 出现 POST → GET → POST，Pytest 复现中故意失败与清理检查都失败。

## 独立验收

```text
python evaluation/verify.py B <requests-workspace>
python evaluation/verify.py C <algorithm-workspace>
python evaluation/verify_d.py <pytest-workspace>
```

D 共 11 项，包含清理异常诊断。pdb 检查要求完整顺序为 setup → test → debug → teardown → cleanup-last → cleanup-first。验收脚本及其他候选答案不要交给模型。

A 只按原提示词要求核查（2D 鹈鹕骑车单文件 HTML），不将手机窄屏适配当成硬性扣分项。验收时通过本地回环 HTTP 服务挂载 `index.html`，用无头 Chromium 分别在桌面（`1000×700`）与移动端（`430×800`）视口采集实测截图、控制台报错与布局溢出信息。
