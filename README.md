# LeetCode 从零到精通：175 个可运行 Notebook

**175 章已生成，175 章在独立空内核执行通过。** 每章保存真实输出、状态表和断言结果，不是只创建目录或空模板。

课程包含 22 个模块、383 道去重代表题映射。代表题用于知识索引，不表示每道题都有完整平台适配代码，也不表示本项目覆盖 LeetCode 全站所有题。

## 从哪里开始

先打开 [课程索引](COURSE_INDEX.md)，再从 [N001：Notebook 与判题接口](notebooks/00_foundations/001_jupyter_and_judge.ipynb) 开始。章节编号是稳定文件索引；学习顺序以 [curriculum.json](specs/curriculum.json) 的 `learning_order` 为准，避免状态压缩、数位 DP 等章节缺少位运算先修。

每章包含：**通俗解释、基础知识、手算推导、核心代码片段、分段可执行实现、示例与可视化、测试用例讲解、练习提示、可独立运行的完整代码**。完整代码包含全部导入、接口和回归测试，可重启内核后只运行这一格，或者复制为 `.py` 文件执行。

本次改写吸收 `comment/README.md` 和 175 份同名逐章意见，保留原算法及测试，并校正部分算例和论证。指定的 `comment/REWRITE_BRIEF.md` 在读取的仓库快照中不存在，未将其视为已读。详见 [改写验收报告](reports/REWRITE_REPORT.md)。

## 安装与使用

验证环境：Python 3.13.5，nbformat 5.10.4，nbclient 0.10.4，ipykernel 7.2.0，Pandas 2.2.3，Node.js v22.16.0。完整实测环境见 [执行报告](reports/execution.json)。

```bash
python -m pip install -r requirements.txt
python -m ipykernel install --user --name python3
# 任选 JupyterLab 或其他 Notebook 前端；前端不是算法执行器依赖。
python -m pip install jupyterlab
jupyter lab
```

按顺序运行单章：

```bash
python scripts/execute_course.py --ids N001 --workers 1
python scripts/audit_course.py
```

重新执行全部章节：

```bash
python scripts/execute_course.py --workers 1
python scripts/audit_course.py
python scripts/verify_rewrite.py
```

执行器每章使用新的 Jupyter 内核，工作目录为该 Notebook 所在目录，`allow_errors=False`。失败会记入报告并以非零退出码结束；不会静默返回伪造答案。不要同时启动多个执行器写同一报告。

## 修改教程

`notebooks/` 是已执行、可直接学习的交付件；`scripts/lessons_*.py` 是算法、示例和测试的生成源；`comment/` 提供逐章详细讲解，`scripts/rewrite_from_comments.py` 负责整合、代码排版与已记录的文字纠错。修改对应源文件后，仅重建和重跑受影响章节：

```bash
python scripts/build_all.py --ids N029
python scripts/execute_course.py --ids N029 --workers 1
python scripts/audit_course.py
python scripts/verify_rewrite.py --ids N029
```

**重建会清除该章旧输出。** 不重跑就不能继续声称重建后的文件已经执行通过。直接手改 Notebook 可以临时实验，但下次重建会被生成源覆盖；需要长期保留的修改应回写相应源文件。

## 特殊运行时

SQL 章节运行真实 SQLite，其他数据库方言未在本项目执行。Pandas 使用真实 DataFrame 并检查列、索引与 dtype。Shell 需要 Bash、awk、sort、sed；JavaScript 需要 PATH 中可用的 `node`，不以 Python 模拟 JS。并发章节实际创建线程，可能挂起的案例都放入有超时且可终止的子进程。

相应原生代码另存于 `scripts/native/`，方便独立阅读；它们来自同一份生成源，Notebook 内保留测试。离线学习与执行不依赖访问 LeetCode，题面链接只用于进一步查阅。

## 已完成与边界

- 175 个固定文件路径均与规格匹配；全部 Notebook 格式合法、空内核执行成功，并保存实际断言输出。当前证据见 `reports/execution.json`。
- 测试覆盖样例、边界、结构不变量和适用时的小域穷举对照。性能冒烟与指数级参照分离。随机、并发测试不被当成等概率或活性的通用证明。
- 本轮**没有重新联网核验全部 383 道代表题的最新题面**。原规格中的 34 条身份核对记录是历史状态，不能继承为本轮全题面复核。平台收费权限、语言支持与约束可能变化。
- 没有提交 LeetCode 官方在线评测；部分接口采用明确的教学契约。例如 NestedIterator 使用 Python 嵌套列表，SQL 使用 SQLite，Pandas 可空类型和 JS 返回值扩展会在章内标明。
- 所有核心接口均有实现；低频高级拓展、各章开放练习和教学文字仍适合继续独立复审。运行成功不是逐章人工教学质量验收，也不是学习者已经掌握。

## 文件结构

```text
notebooks/               175 个带真实输出的 Notebook
scripts/lessons_*.py      逐章推导、实现、可视化、测试的生成源
scripts/native/          原生 SQL / Shell / JavaScript / 并发 Python
scripts/build_all.py      选择性重建
scripts/execute_course.py 空内核执行与唯一执行报告
scripts/audit_course.py   固定路径、接口标记与保存输出检查
scripts/rewrite_from_comments.py 逐章讲解整合、代码分段、完整代码
scripts/verify_rewrite.py 结构、原算法/测试保留、完整代码隔离执行
comment/                 保留的 175 份逐章意见与索引
reports/REWRITE_REPORT.md 改写验收摘要
reports/rewrite_verification.json 逐章源码与独立运行证据
specs/                   原始课程规格与代表题映射
reports/execution.json   逐章实际执行证据与环境
COURSE_INDEX.md           全部章节入口与先修学习顺序
```

## 后续学习原则

先独立预测输出，再执行；先写直接解法，再推导优化；改变一个条件，解释方法是否仍适用。结业看能否对未展示的变体给出正确实现、论证和边界，而不按题目数量计分。
