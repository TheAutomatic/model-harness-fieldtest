# 复现与验收指南

本目录存放实验结束后的独立验收脚本与最小复现入口。如果在本地重跑实验，请只把 `prompts/` 里的题目和干净的上游源码交给模型，切勿把本目录或已有的 `changes.patch` 放进模型可读的工作区。

## 1. 准备上游源码

- **B (`psf/requests`)**：检出 commit `110048f9837f8441ea536804115e80b69f400277`，将 `fixtures/B/reproduce.py` 复制到项目根目录。
- **D (`pytest-dev/pytest`)**：检出 commit `2b51ed46d54be58da6bbcd28f68149b3fc2cd104`，将 `fixtures/D/run_pytest.py` 与 `test_reproduce.py` 复制到项目根目录。由于源码归档不含 `setuptools-scm` 生成的版本文件，需手动创建 `src/_pytest/_version.py`：

```python
version = '5.4.1'
version_tuple = (5, 4, 1)
```

要验证某一组提交的修复，在干净源码根目录执行 `git apply <对应组的 changes.patch>` 即可。

## 2. Python 环境与依赖

两个开源项目年代较早，原实验在 Windows + Python 3.9 下运行。D 题的 Pytest 5.4.1 依赖可安装到独立目录，并通过环境变量 `DSTEST_PYTEST_DEPS` 传给 `run_pytest.py`：

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

## 3. 运行验收脚本

在 `experiments/deepseek-v4.1-flash-1017/` 目录下执行：

```bash
python evaluation/verify.py B <requests-工作区路径>
python evaluation/verify.py C <算法题-工作区路径>
python evaluation/verify_d.py <pytest-工作区路径>
python evaluation/diagnose_cleanup.py <pytest-工作区路径>
```

- `verify_d.py` 与 `diagnose_cleanup.py` 默认调用当前 Python 解释器，也可通过环境变量 `FIELDTEST_PYTHON` 指定 Python 3.9 路径（脚本内使用了 Windows 的 `NUL` 空配置名，在 Linux/macOS 下可按需改为 `/dev/null`）。
- A 题直接用浏览器打开 `artifacts/A/<组别>/index.html`，分别在桌面（`1000×700`）与移动端（`430×800`）视口下查看渲染与动画效果。
