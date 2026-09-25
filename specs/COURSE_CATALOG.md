> 此文件保留原始课程规格。当前 175 章已生成并执行；最新交付状态见根目录 README 与 reports/execution.json，不以此文件历史描述替代执行证据。

# LeetCode 从零到精通：175 个 Notebook 课程目录与逐章规格

版本：1.0　日期：2026-09-23　主语言：中文讲解 + Python算法实现

**交付边界：本包是教程生成规格，不是已经生成或执行过的175个Notebook。**
每章包含教学目标、知识点、代表题、必须实现代码、可视化、练习、单元测试；另外给出先修、难度层级、运行时和适用边界。
上一轮数量清单合计为189。本版合并交叉内容，明确为175章；补充JavaScript分支。
这些章节覆盖基础、主干与选定精通拓展，不等同于已逐题映射整个LeetCode题库，也不承诺所有新题只需套现有模板。

## 使用约定

- `curriculum.json`为唯一结构化权威；本Markdown为它的阅读视图。编号固定用于索引，实际学习/生成顺序见`learning_order`。
- 主线算法使用Python。SQL、Pandas、Shell、JavaScript、并发分支有自己的执行和测试契约；不以Python替代JS或Shell的实际运行。
- `canonical`典型题需要精讲；`warmup`热身；`preview`只作预告；`comparison`对照复用；`extension`明确是拓展而非必需解法。
- 每章先完成必须代码。可选代码不阻塞主线。一个章节可分若干教学小节，但仍只有一个固定Notebook路径，不额外创建空壳章节凑数。
- 测试条目是待实现的验收规格；不代表未来代码已经正确。测试、证明、性能分析分别完成，不能互相冒充。
- 练习未作答不应破坏教学区Run All。参考答案可在同一Notebook末尾折叠；不创建第二套重复课程编号。

## 模块总览

| 目录 | 内容 | 编号范围 | 数量 |
|---|---|---|---:|
| `00_foundations/` | Python 与运行基础 | N001–N010 | 10 |
| `01_reasoning/` | 复杂度、证明与测试思维 | N011–N016 | 6 |
| `02_array_string_hash/` | 数组、字符串与哈希 | N017–N024 | 8 |
| `03_pointers_windows/` | 双指针与滑动窗口 | N025–N030 | 6 |
| `04_prefix_intervals/` | 前缀、差分与区间 | N031–N036 | 6 |
| `05_sort_binary_search/` | 排序与二分 | N037–N044 | 8 |
| `06_linked_lists/` | 链表 | N045–N050 | 6 |
| `07_stack_queue/` | 栈、队列与单调结构 | N051–N056 | 6 |
| `08_heaps/` | 堆与优先队列 | N057–N061 | 5 |
| `09_recursion_backtracking/` | 递归、分治与回溯 | N062–N068 | 7 |
| `10_trees_tries/` | 树、BST 与 Trie | N069–N078 | 10 |
| `11_graphs/` | 图论 | N079–N092 | 14 |
| `12_greedy/` | 贪心 | N093–N097 | 5 |
| `13_dynamic_programming/` | 动态规划 | N098–N117 | 20 |
| `14_string_algorithms/` | 字符串算法 | N118–N123 | 6 |
| `15_math_bits_geometry/` | 数学、位运算与几何 | N124–N133 | 10 |
| `16_advanced_structures/` | 高级数据结构 | N134–N140 | 7 |
| `17_advanced_algorithms/` | 高级算法 | N141–N146 | 6 |
| `18_design/` | 数据结构设计 | N147–N151 | 5 |
| `19_specialized_tracks/` | SQL、Pandas、Shell 与 JavaScript | N152–N163 | 12 |
| `20_concurrency/` | 并发 | N164–N167 | 4 |
| `21_mastery/` | 综合迁移与结业 | N168–N175 | 8 |

合计：**175章**；课程中有**383道去重代表题**。代表题身份本轮重点核对**34道**，其余在结构化清单中标记为生成前核验。官方题的付费状态与语言支持未作全量核对。

## 完整文件目录

```text
notebooks/
  00_foundations/  # Python 与运行基础
    001_jupyter_and_judge.ipynb  # Notebook 与判题接口
    002_values_types_operators.ipynb  # 数值、布尔值与运算符
    003_branching_loops.ipynb  # 分支、循环与枚举
    004_functions_scope_contracts.ipynb  # 函数、作用域与契约
    005_lists_mutation_aliasing.ipynb  # 列表、索引与对象引用
    006_strings_unicode_parsing.ipynb  # 字符串与基础解析
    007_dict_set_tuple.ipynb  # 字典、集合、元组与哈希键
    008_standard_library_toolbox.ipynb  # 标准库算法工具箱
    009_classes_nodes_protocols.ipynb  # 类、节点与迭代协议
    010_debugging_reproducible_notebooks.ipynb  # 调试、断言与可复现执行
  01_reasoning/  # 复杂度、证明与测试思维
    011_time_space_complexity.ipynb  # 时间与空间复杂度
    012_constraints_to_algorithms.ipynb  # 从约束推导可行算法
    013_invariants_induction_termination.ipynb  # 循环不变量、归纳与终止性
    014_amortized_analysis.ipynb  # 均摊复杂度与操作计数
    015_bruteforce_oracles_properties.ipynb  # 暴力参照、穷举与性质测试
    016_problem_modeling_and_counterexamples.ipynb  # 问题建模与竞争解法反例
  02_array_string_hash/  # 数组、字符串与哈希
    017_array_scans_inplace.ipynb  # 数组扫描与原地覆盖
    018_matrix_traversal_simulation.ipynb  # 矩阵遍历与边界模拟
    019_hash_lookup_index.ipynb  # 哈希查找与索引映射
    020_hash_frequency_grouping.ipynb  # 频率统计与等价类分组
    021_hash_sets_sequence_dedup.ipynb  # 集合、去重与连续序列
    022_string_mapping_order.ipynb  # 字符串映射与字典序
    023_string_parsing_fsm.ipynb  # 字符串解析与有限状态机
    024_array_string_transformations.ipynb  # 数组与字符串的结构变换
  03_pointers_windows/  # 双指针与滑动窗口
    025_opposite_two_pointers.ipynb  # 相向双指针与有序配对
    026_same_direction_fast_slow.ipynb  # 同向双指针与稳定压缩
    027_k_sum_and_geometric_elimination.ipynb  # 三数和与双指针消元
    028_fixed_windows.ipynb  # 固定长度滑动窗口
    029_variable_windows.ipynb  # 可变窗口与最短覆盖
    030_window_counting_exactly_k.ipynb  # 滑动窗口计数与恰好K
  04_prefix_intervals/  # 前缀、差分与区间
    031_prefix_sums_xor_products.ipynb  # 前缀聚合与区间查询
    032_prefix_hash_counting.ipynb  # 前缀和与哈希计数
    033_prefix_sum_2d.ipynb  # 二维前缀和与容斥
    034_difference_arrays.ipynb  # 差分与批量区间更新
    035_interval_union_intersection.ipynb  # 区间合并、插入与交集
    036_sweep_line_events.ipynb  # 扫描线与事件排序
  05_sort_binary_search/  # 排序与二分
    037_elementary_sorts.ipynb  # 基础排序与比较模型
    038_merge_sort_and_inversions.ipynb  # 归并排序与逆序计数
    039_quicksort_partition.ipynb  # 快速排序与划分不变量
    040_heapsort_counting_bucket_radix.ipynb  # 堆排序与非比较排序
    041_quickselect_order_statistics.ipynb  # 快速选择与第K大
    042_binary_search_bounds.ipynb  # 二分查找与左右边界
    043_binary_search_on_answer.ipynb  # 二分答案与可行性判定
    044_binary_search_structured_data.ipynb  # 旋转数组、矩阵与峰值
  06_linked_lists/  # 链表
    045_linked_list_sentinels.ipynb  # 链表基础与哨兵节点
    046_linked_list_reversal.ipynb  # 链表反转与局部反转
    047_linked_list_fast_slow.ipynb  # 快慢指针、环与中点
    048_linked_list_merge_sort.ipynb  # 链表合并与归并排序
    049_linked_list_reordering_palindrome.ipynb  # 链表重排与回文
    050_linked_list_advanced_structures.ipynb  # K组反转、相交与随机指针
  07_stack_queue/  # 栈、队列与单调结构
    051_stack_matching_paths.ipynb  # 栈、括号与路径归约
    052_expression_parsing_stacks.ipynb  # 表达式解析与计算
    053_queue_deque_implementations.ipynb  # 队列、双端队列与循环缓冲区
    054_monotonic_stack_neighbors.ipynb  # 单调栈与最近更大更小元素
    055_monotonic_stack_contributions.ipynb  # 单调栈的面积与贡献计数
    056_monotonic_queue_windows.ipynb  # 单调队列与带负数的最短区间
  08_heaps/  # 堆与优先队列
    057_heap_fundamentals.ipynb  # 二叉堆、建堆与优先队列
    058_heap_top_k.ipynb  # Top-K、频率与流式维护
    059_heap_k_way_merge.ipynb  # K路归并与有序候选生成
    060_two_heaps_lazy_deletion.ipynb  # 双堆中位数与延迟删除
    061_heap_event_scheduling.ipynb  # 堆调度与离散事件模拟
  09_recursion_backtracking/  # 递归、分治与回溯
    062_recursion_contracts.ipynb  # 递归函数契约与调用栈
    063_divide_and_conquer_patterns.ipynb  # 分治的拆分与合并
    064_subsets_permutations_combinations.ipynb  # 子集、排列与组合回溯
    065_backtracking_dedup_pruning.ipynb  # 回溯去重与剪枝
    066_partitioning_and_search_constraints.ipynb  # 切分回溯与字符串约束
    067_grid_backtracking.ipynb  # 网格路径回溯与访问恢复
    068_constraint_satisfaction_queens_sudoku.ipynb  # 约束满足、数独与N皇后
  10_trees_tries/  # 树、BST 与 Trie
    069_tree_dfs_traversals.ipynb  # 树的递归与迭代遍历
    070_tree_bfs_views.ipynb  # 树的层序遍历与视图
    071_tree_bottom_up_aggregation.ipynb  # 树的自底向上聚合
    072_tree_path_problems.ipynb  # 树上路径与信息传递
    073_bst_invariants_operations.ipynb  # 二叉搜索树与有序操作
    074_tree_construction_serialization.ipynb  # 树的构建与序列化
    075_lowest_common_ancestor.ipynb  # 最近公共祖先与返回值语义
    076_tree_transformations_morris.ipynb  # 树的原地变换与Morris遍历
    077_trie_prefix_dictionary.ipynb  # Trie的前缀状态与词典查询
    078_trie_backtracking_wildcards.ipynb  # Trie与回溯的组合
  11_graphs/  # 图论
    079_graph_representations.ipynb  # 图的表示与建模
    080_graph_dfs_components_cycles.ipynb  # DFS、连通分量与环检测
    081_graph_bfs_multisource.ipynb  # BFS、最短步数与多源扩散
    082_topological_sort_dag.ipynb  # 拓扑排序与依赖图
    083_disjoint_set_union.ipynb  # 并查集与动态连通性
    084_dijkstra_zero_one_bfs.ipynb  # Dijkstra与0-1 BFS
    085_bellman_ford_floyd.ipynb  # Bellman-Ford、受限路径与Floyd
    086_minimum_spanning_trees.ipynb  # 最小生成树与割性质
    087_bipartite_graphs_matching.ipynb  # 二分图、增广路与匹配
    088_strongly_connected_components.ipynb  # 强连通分量与缩点
    089_bridges_articulation_points.ipynb  # 桥、割点与low-link
    090_eulerian_paths.ipynb  # 欧拉路径与Hierholzer
    091_functional_graphs.ipynb  # 函数图、环与入树
    092_max_flow_min_cut.ipynb  # 网络流、最小割与匹配归约
  12_greedy/  # 贪心
    093_greedy_exchange_intervals.ipynb  # 贪心选择与交换论证
    094_greedy_reachability_layers.ipynb  # 覆盖前沿、跳跃与层次贪心
    095_greedy_balance_two_pass.ipynb  # 收支平衡与双向约束
    096_greedy_heap_replacement.ipynb  # 堆贪心与撤销局部决策
    097_greedy_lexicographic_construction.ipynb  # 字典序构造与剩余可行性
  13_dynamic_programming/  # 动态规划
    098_dp_from_recursion_to_tables.ipynb  # 从递归到记忆化与表格
    099_linear_dp_and_kadane.ipynb  # 一维DP与以当前位置结尾的状态
    100_grid_dp.ipynb  # 网格DP与路径状态
    101_zero_one_knapsack.ipynb  # 0/1背包与逆序容量
    102_unbounded_bounded_group_knapsack.ipynb  # 完全、多重与分组背包
    103_lis_and_ordered_sequences.ipynb  # 最长递增子序列与耐心排序
    104_sequence_alignment_dp.ipynb  # 序列匹配、编辑距离与子序列计数
    105_string_segmentation_matching_dp.ipynb  # 字符串分割、解码与模式匹配
    106_finite_state_dp_stocks.ipynb  # 状态机DP与股票交易
    107_interval_dp.ipynb  # 区间DP与最后一步决策
    108_partition_dp.ipynb  # 划分DP与最后一段
    109_tree_dp_selection_matching.ipynb  # 树形DP与局部约束
    110_rerooting_dp.ipynb  # 换根DP与全节点答案
    111_dag_dp_and_longest_paths.ipynb  # DAG动态规划与隐式偏序
    112_bitmask_dp.ipynb  # 状态压缩DP与集合状态
    113_digit_dp.ipynb  # 数位DP、上界与前导零
    114_probability_expectation_dp.ipynb  # 概率与期望DP
    115_game_dp_minimax.ipynb  # 博弈DP与得分差
    116_profile_dp_grid_states.ipynb  # 轮廓DP与窄网格状态
    117_dp_optimization_basics.ipynb  # DP空间与转移优化
  14_string_algorithms/  # 字符串算法
    118_kmp_and_z_function.ipynb  # KMP与Z函数
    119_rolling_hash_substrings.ipynb  # 滚动哈希与子串比较
    120_palindrome_algorithms_manacher.ipynb  # 回文DP、中心扩展与Manacher
    121_aho_corasick_automaton.ipynb  # Aho–Corasick多模式匹配
    122_suffix_array_lcp.ipynb  # 后缀数组与LCP
    123_suffix_automaton.ipynb  # 后缀自动机与子串状态
  15_math_bits_geometry/  # 数学、位运算与几何
    124_bits_integer_representation.ipynb  # 位运算与整数表示
    125_bitmasks_xor_trie.ipynb  # 位掩码、异或与二进制Trie
    126_gcd_euclid_number_theory.ipynb  # 欧几里得算法与整除结构
    127_primes_sieves_factorization.ipynb  # 质数筛、最小质因子与分解
    128_modular_arithmetic_fast_power.ipynb  # 模运算、快速幂与逆元
    129_combinatorics_counting.ipynb  # 组合计数、容斥与Catalan
    130_matrix_exponentiation_recurrences.ipynb  # 线性递推与矩阵快速幂
    131_randomized_sampling_probability.ipynb  # 概率基础与随机采样
    132_impartial_games_sprague_grundy.ipynb  # 组合博弈、Nim与SG函数
    133_computational_geometry.ipynb  # 计算几何与凸包
  16_advanced_structures/  # 高级数据结构
    134_coordinate_compression_order_statistics.ipynb  # 坐标压缩与秩
    135_fenwick_tree.ipynb  # 树状数组与前缀聚合
    136_segment_tree_monoids.ipynb  # 线段树与区间聚合
    137_lazy_segment_tree_range_updates.ipynb  # 懒传播、动态节点与更新复合
    138_sparse_table_rmq.ipynb  # Sparse Table与静态RMQ
    139_balanced_trees_treaps_skiplists.ipynb  # 有序集合、Treap与跳表原理
    140_weighted_rollback_dsu.ipynb  # 带权与可回滚并查集
  17_advanced_algorithms/  # 高级算法
    141_euler_tour_binary_lifting.ipynb  # Euler序、倍增与树上查询
    142_meet_in_the_middle.ipynb  # 折半搜索与指数优化
    143_offline_queries_sweep_mo.ipynb  # 离线查询、扫描线与Mo算法
    144_state_graph_bidirectional_astar.ipynb  # 状态图、双向BFS与A*
    145_advanced_dp_optimization_conditions.ipynb  # 高级DP优化及其成立条件
    146_fft_ntt_convolution.ipynb  # FFT、NTT与卷积拓展
  18_design/  # 数据结构设计
    147_lru_lfu_caches.ipynb  # LRU与LFU缓存设计
    148_randomized_set_multiset.ipynb  # 随机集合与多重集合设计
    149_iterators_lazy_evaluation.ipynb  # 迭代器、惰性展开与查看下一项
    150_snapshots_persistent_versions.ipynb  # 快照、历史查询与可持久化
    151_composite_service_design.ipynb  # 多结构组合与时间序服务
  19_specialized_tracks/  # SQL、Pandas、Shell 与 JavaScript
    152_sql_select_null_sort.ipynb  # SQL入门、过滤与NULL
    153_sql_aggregation_joins.ipynb  # SQL聚合、连接与计数语义
    154_sql_subqueries_cte_antijoins.ipynb  # SQL子查询、CTE与反连接
    155_sql_window_rank_sequences.ipynb  # SQL窗口、排名与连续段
    156_sql_dates_retention_reports.ipynb  # SQL日期、留存与移动报表
    157_pandas_selection_cleaning.ipynb  # Pandas选择、缺失与类型
    158_pandas_aggregation_merge_reshape.ipynb  # Pandas连接、聚合与宽长变换
    159_pandas_time_rank_rolling.ipynb  # Pandas日期、排名与滚动统计
    160_shell_text_processing.ipynb  # Shell文本流与管道
    161_javascript_fundamentals_closures.ipynb  # JavaScript基础、闭包与对象
    162_javascript_functional_events.ipynb  # JavaScript函数组合、缓存与事件
    163_javascript_promises_timers.ipynb  # JavaScript异步、定时器与并发限制
  20_concurrency/  # 并发
    164_threads_ordering_events.ipynb  # 线程、互斥与顺序同步
    165_semaphores_conditions_alternation.ipynb  # 信号量、条件变量与交替执行
    166_barriers_bounded_queues.ipynb  # 屏障、生产消费与有界队列
    167_deadlocks_fairness_philosophers.ipynb  # 死锁、饥饿与哲学家问题
  21_mastery/  # 综合迁移与结业
    168_modeling_algorithm_selection.ipynb  # 约束建模与算法选择训练
    169_optimization_ladder_differential_testing.ipynb  # 从暴力到最优的优化阶梯
    170_proofs_and_counterexamples_workshop.ipynb  # 正确性证明与反例工作坊
    171_testing_debugging_performance.ipynb  # 测试、调试与性能回归
    172_medium_pattern_combinations.ipynb  # Medium综合题与机制组合
    173_hard_sequences_strings_capstone.ipynb  # Hard序列、字符串与设计综合
    174_hard_graph_tree_capstone.ipynb  # Hard图树、离线与查询综合
    175_unseen_transfer_final_project.ipynb  # 陌生题迁移与结业项目
```

## 逐章生成规格

## 00_foundations｜Python 与运行基础

### N001｜Notebook 与判题接口

**文件**：`notebooks/00_foundations/001_jupyter_and_judge.ipynb`

**层级 / 类型**：L0 / foundation；**先修**：无。

**教学目标**：独立运行单元格，并将普通函数包装为判题接口。

**知识点**：内核与执行顺序；表达式与输出；Solution 与返回值；Restart and Run All。

**代表 LeetCode 题**：
- [2235. Add Two Integers](https://leetcode.com/problems/add-two-integers/) — 基础热身；官方页面已核对题号与标题。

**必须实现的代码**：
- `sum_two(a, b)`。
- `Solution.sum(num1, num2)`。

**可视化**：单元格依赖与输入—函数—返回值流程表。

**练习**：
- 把打印答案改为返回答案。
- 清空内核后复现结果。

**单元测试规格**：
- sum_two(2,3)==5。
- sum_two(-4,4)==0。
- 清空内核后所有教学单元格可顺序执行。

**边界与生成要求**：本轮只交付课程规格，不创建占位Notebook；本章是未来教程的第一章。

---

### N002｜数值、布尔值与运算符

**文件**：`notebooks/00_foundations/002_values_types_operators.ipynb`

**层级 / 类型**：L0 / foundation；**先修**：N001。

**教学目标**：根据题意选择类型并写出数值表达式。

**知识点**：int/float/bool/None；整除与取模；比较运算；浮点近似。

**代表 LeetCode 题**：
- 2413. Smallest Even Multiple — 基础热身；生成前核验题面。
- 2469. Convert the Temperature — 基础热身；生成前核验题面。

**必须实现的代码**：
- `smallest_even_multiple(n)`。
- `convert_temperature(celsius)`。

**可视化**：整数除法与余数数轴；浮点误差数值表。

**练习**：
- 解释负数整除与向零截断的差异。
- 比较浮点结果时选择容差。

**单元测试规格**：
- n=5→10。
- n=6→6。
- 0摄氏度对应273.15开尔文与32华氏度，用容差比较。

**边界与生成要求**：代表题用于知识映射；先讲最小问题，再完成本章核心实现。对比与拓展题不强制变成独立完整题解。

---

### N003｜分支、循环与枚举

**文件**：`notebooks/00_foundations/003_branching_loops.ipynb`

**层级 / 类型**：L0 / foundation；**先修**：N002。

**教学目标**：将自然语言条件翻译为可终止的循环。

**知识点**：if/elif；for/while；range；break/continue；循环边界。

**代表 LeetCode 题**：
- 412. Fizz Buzz — 基础热身；生成前核验题面。

**必须实现的代码**：
- `fizz_buzz(n)`。
- `sum_even(n)`。

**可视化**：逐步展示循环变量、条件分支与输出。

**练习**：
- 不使用列表推导式实现。
- 将for版本改写成while版本。

**单元测试规格**：
- n=3→['1','2','Fizz']。
- n=15最后一项为FizzBuzz。
- 测试n=1。

**边界与生成要求**：代表题用于知识映射；先讲最小问题，再完成本章核心实现。对比与拓展题不强制变成独立完整题解。

---

### N004｜函数、作用域与契约

**文件**：`notebooks/00_foundations/004_functions_scope_contracts.ipynb`

**层级 / 类型**：L0 / foundation；**先修**：N003。

**教学目标**：把一个任务分解为参数清楚、返回值明确的函数。

**知识点**：位置与默认参数；局部作用域；类型标注；前置条件；可变默认参数风险。

**代表 LeetCode 题**：
- 1342. Number of Steps to Reduce a Number to Zero — 基础热身；生成前核验题面。

**必须实现的代码**：
- `number_of_steps(num)`。
- `is_even(num)`。

**可视化**：函数调用前后变量表。

**练习**：
- 拆分奇偶处理但不增加无用包装。
- 修复可变默认参数共享状态。

**单元测试规格**：
- num=14→6。
- num=0→0。
- num=1→1。
- 重复调用结果不受上次调用影响。

**边界与生成要求**：代表题用于知识映射；先讲最小问题，再完成本章核心实现。对比与拓展题不强制变成独立完整题解。

---

### N005｜列表、索引与对象引用

**文件**：`notebooks/00_foundations/005_lists_mutation_aliasing.ipynb`

**层级 / 类型**：L0 / foundation；**先修**：N004。

**教学目标**：正确操作列表并区分原地修改和创建副本。

**知识点**：索引与切片；append/pop；浅拷贝；二维列表别名；可变对象。

**代表 LeetCode 题**：
- 1929. Concatenation of Array — 基础热身；生成前核验题面。
- 1920. Build Array from Permutation — 基础热身；生成前核验题面。

**必须实现的代码**：
- `get_concatenation(nums)`。
- `build_matrix(rows, cols)`。

**可视化**：对象—引用关系图；二维列表单元格变化。

**练习**：
- 修复[[0]*m]*n。
- 不使用加号生成双倍数组。

**单元测试规格**：
- [1,2,1]→[1,2,1,1,2,1]。
- 修改矩阵一行不改变其他行。
- 函数不意外修改输入。

**边界与生成要求**：代表题用于知识映射；先讲最小问题，再完成本章核心实现。对比与拓展题不强制变成独立完整题解。

---

### N006｜字符串与基础解析

**文件**：`notebooks/00_foundations/006_strings_unicode_parsing.ipynb`

**层级 / 类型**：L0 / foundation；**先修**：N005。

**教学目标**：在字符和字符串层面完成基础转换。

**知识点**：不可变性；split/join；ord/chr；字符分类；Unicode 与题目字符集。

**代表 LeetCode 题**：
- 1108. Defanging an IP Address — 基础热身；生成前核验题面。
- 1678. Goal Parser Interpretation — 基础热身；生成前核验题面。

**必须实现的代码**：
- `defang_ip(address)`。
- `interpret(command)`。

**可视化**：字符位置、扫描指针与输出缓存表。

**练习**：
- 不用replace实现IP转换。
- 解释循环拼接与join的区别。

**单元测试规格**：
- 1.1.1.1→1[.]1[.]1[.]1。
- G()(al)→Goal。
- 空串按教学契约返回空串。

**边界与生成要求**：代表题用于知识映射；先讲最小问题，再完成本章核心实现。对比与拓展题不强制变成独立完整题解。

---

### N007｜字典、集合、元组与哈希键

**文件**：`notebooks/00_foundations/007_dict_set_tuple.ipynb`

**层级 / 类型**：L0 / foundation；**先修**：N005。

**教学目标**：选择集合做去重、字典做映射并理解可哈希性。

**知识点**：dict/set/tuple；键唯一性；计数；成员查询；平均复杂度的条件。

**代表 LeetCode 题**：
- 217. Contains Duplicate — 基础热身；生成前核验题面。

**必须实现的代码**：
- `contains_duplicate(nums)`。
- `count_values(nums)`。

**可视化**：数组到频次字典的构建过程。

**练习**：
- 不用set完成去重。
- 解释列表不能直接作为字典键。

**单元测试规格**：
- [1,2,1]→True。
- [1,2,3]→False。
- 空输入→False。
- 频次之和等于输入长度。

**边界与生成要求**：代表题用于知识映射；先讲最小问题，再完成本章核心实现。对比与拓展题不强制变成独立完整题解。

---

### N008｜标准库算法工具箱

**文件**：`notebooks/00_foundations/008_standard_library_toolbox.ipynb`

**层级 / 类型**：L0 / foundation；**先修**：N006, N007。

**教学目标**：根据所需操作选择工具而非重复造轮子。

**知识点**：Counter/defaultdict/deque；heapq/bisect导览；cache；itertools；math。

**代表 LeetCode 题**：
- 387. First Unique Character in a String — 基础热身；生成前核验题面。

**必须实现的代码**：
- `first_unique_char(s)`。
- `deque_queue_demo(items)`。

**可视化**：同一数据在计数器、队列与堆中的状态对照。

**练习**：
- 把手写计数改为Counter。
- 写出每种工具适用与不适用操作。

**单元测试规格**：
- leetcode→0。
- aabb→-1。
- deque入队后按原顺序出队。
- 不依赖字典意外插入键。

**边界与生成要求**：代表题用于知识映射；先讲最小问题，再完成本章核心实现。对比与拓展题不强制变成独立完整题解。

---

### N009｜类、节点与迭代协议

**文件**：`notebooks/00_foundations/009_classes_nodes_protocols.ipynb`

**层级 / 类型**：L0 / foundation；**先修**：N004, N005。

**教学目标**：能够读懂并构造链表和树的最小数据模型。

**知识点**：class/__init__；属性引用；ListNode/TreeNode；迭代器与生成器导览。

**代表 LeetCode 题**：
- 1290. Convert Binary Number in a Linked List to Integer — 基础热身；生成前核验题面。

**必须实现的代码**：
- `ListNode`。
- `TreeNode`。
- `list_to_nodes(values)`。
- `binary_list_to_int(head)`。

**可视化**：节点值和next引用图。

**练习**：
- 手工构造三个节点。
- 比较值相等与对象身份相同。

**单元测试规格**：
- 链表[1,0,1]→5。
- [0]→0。
- 构造后的节点彼此不同。
- 末节点next为None。

**边界与生成要求**：代表题用于知识映射；先讲最小问题，再完成本章核心实现。对比与拓展题不强制变成独立完整题解。

---

### N010｜调试、断言与可复现执行

**文件**：`notebooks/00_foundations/010_debugging_reproducible_notebooks.ipynb`

**层级 / 类型**：L0 / foundation；**先修**：N001, N004, N005。

**教学目标**：定位报错并用小测试固定修复结果。

**知识点**：traceback；assert；unittest；随机种子；内核污染；最小复现。

**代表 LeetCode 题**：
- 1480. Running Sum of 1d Array — 基础热身；生成前核验题面。

**必须实现的代码**：
- `running_sum(nums)`。
- `test_running_sum()`。

**可视化**：错误定位前后变量追踪表。

**练习**：
- 修复错位下标。
- 设计不会因前一单元格变量而通过的测试。

**单元测试规格**：
- [1,2,3]→[1,3,6]。
- 单元素保持不变。
- 教学扩展空数组→[]。
- 重复运行不累积旧状态。

**边界与生成要求**：代表题用于知识映射；先讲最小问题，再完成本章核心实现。对比与拓展题不强制变成独立完整题解。

---

## 01_reasoning｜复杂度、证明与测试思维

### N011｜时间与空间复杂度

**文件**：`notebooks/01_reasoning/011_time_space_complexity.ipynb`

**层级 / 类型**：L1 / foundation；**先修**：N007, N010。

**教学目标**：能按输入规模分析操作数和额外空间。

**知识点**：渐进上界；最坏/平均；递归栈；输出空间；位复杂度提醒。

**代表 LeetCode 题**：
- [1. Two Sum](https://leetcode.com/problems/two-sum/) — 对照或复用已有题；官方页面已核对题号与标题。

**必须实现的代码**：
- `two_sum_bruteforce(nums, target)`。
- `count_pair_checks(n)`。

**可视化**：n与枚举次数曲线，不用耗时曲线代替证明。

**练习**：
- 区分O(n²)和O(nm)。
- 分析切片带来的隐藏拷贝。

**单元测试规格**：
- 检查次数为n(n-1)/2。
- n=0与1时为0。
- 小数组结果与手工答案一致。

**边界与生成要求**：代表题用于知识映射；先讲最小问题，再完成本章核心实现。对比与拓展题不强制变成独立完整题解。

---

### N012｜从约束推导可行算法

**文件**：`notebooks/01_reasoning/012_constraints_to_algorithms.ipynb`

**层级 / 类型**：L1 / foundation；**先修**：N011。

**教学目标**：把约束当作筛选算法的依据而非死记规模表。

**知识点**：输入维度；值域；稀疏性；指数状态；常数与运行环境；输出规模。

**代表 LeetCode 题**：
- 217. Contains Duplicate — 对照或复用已有题；生成前核验题面。
- 215. Kth Largest Element in an Array — 只作动机预告，不要求提前实现；生成前核验题面。

**必须实现的代码**：
- `count_naive_operations(n)`。
- `compare_growth(ns)`。

**可视化**：n、nlogn、n²、2^n的操作量对照表。

**练习**：
- 相同n下比较稀疏图与稠密图。
- 解释n=20不保证所有指数算法可行。

**单元测试规格**：
- n=8时子集数为256。
- n=10时无序对数为45。
- 预测值由精确公式验证。

**边界与生成要求**：规模与复杂度对照仅作候选筛选；不得将某个n值写成不依赖硬件、常数、语言与输出规模的硬阈值。

---

### N013｜循环不变量、归纳与终止性

**文件**：`notebooks/01_reasoning/013_invariants_induction_termination.ipynb`

**层级 / 类型**：L1 / foundation；**先修**：N011。

**教学目标**：为简单算法写出初始化、保持和终止证明。

**知识点**：不变量；数学归纳法；递减量；部分正确性与终止性。

**代表 LeetCode 题**：
- 35. Search Insert Position — 只作动机预告，不要求提前实现；生成前核验题面。

**必须实现的代码**：
- `linear_insert_position(nums, target)`。
- `prefix_max(nums)`。

**可视化**：每次迭代中已处理区间及成立性质。

**练习**：
- 为前缀最大值写归纳证明。
- 构造越界错误最小反例。

**单元测试规格**：
- [1,3,5],4→2。
- 目标小于全部→0。
- 大于全部→n。
- 每步前缀最大值与max对照。

**边界与生成要求**：代表题用于知识映射；先讲最小问题，再完成本章核心实现。对比与拓展题不强制变成独立完整题解。

---

### N014｜均摊复杂度与操作计数

**文件**：`notebooks/01_reasoning/014_amortized_analysis.ipynb`

**层级 / 类型**：L1 / foundation；**先修**：N009, N011。

**教学目标**：区分单次昂贵操作和整个序列的总成本。

**知识点**：聚合法；记账法；势能直觉；动态数组；每元素至多进出一次。

**代表 LeetCode 题**：
- 232. Implement Queue using Stacks — 只作动机预告，不要求提前实现；生成前核验题面。

**必须实现的代码**：
- `TwoStackQueue`。
- `instrumented_push_pop(ops)`。

**可视化**：两栈迁移与累计操作数。

**练习**：
- 构造某次出队很慢的序列。
- 证明一批操作总成本线性。

**单元测试规格**：
- 连续入队1,2,3再出队得到1,2,3。
- 交替操作保持FIFO。
- 每元素迁移次数不超过一次。

**边界与生成要求**：代表题用于知识映射；先讲最小问题，再完成本章核心实现。对比与拓展题不强制变成独立完整题解。

---

### N015｜暴力参照、穷举与性质测试

**文件**：`notebooks/01_reasoning/015_bruteforce_oracles_properties.ipynb`

**层级 / 类型**：L1 / foundation；**先修**：N010, N011。

**教学目标**：用独立的小规模参照检验优化算法。

**知识点**：差分测试；小域穷举；变形性质；固定随机种子；测试不等于证明。

**代表 LeetCode 题**：
- 53. Maximum Subarray — 对照或复用已有题；生成前核验题面。

**必须实现的代码**：
- `max_subarray_bruteforce(nums)`。
- `enumerate_small_arrays(values, max_len)`。

**可视化**：两个实现的结果对照与失败样本缩减表。

**练习**：
- 枚举{-1,0,1}长度不超过5的非空数组。
- 加入全负反例。

**单元测试规格**：
- [-2,-1]→-1。
- [0]→0。
- 暴力版与独立逐段求和参照一致。
- 不把空子数组偷偷当候选。

**边界与生成要求**：代表题用于知识映射；先讲最小问题，再完成本章核心实现。对比与拓展题不强制变成独立完整题解。

---

### N016｜问题建模与竞争解法反例

**文件**：`notebooks/01_reasoning/016_problem_modeling_and_counterexamples.ipynb`

**层级 / 类型**：L1 / foundation；**先修**：N012, N013, N015。

**教学目标**：区分连续、非连续、计数和最优化等不同任务。

**知识点**：输入/输出契约；子数组与子序列；必要/充分条件；贪心反例。

**代表 LeetCode 题**：
- 53. Maximum Subarray — 对照或复用已有题；生成前核验题面。
- 300. Longest Increasing Subsequence — 只作动机预告，不要求提前实现；生成前核验题面。

**必须实现的代码**：
- `enumerate_subarrays(nums)`。
- `enumerate_subsequences(nums)`。

**可视化**：同一数组的连续区间和非连续选择对照。

**练习**：
- 把最大子数组改成最大子序列并解释变化。
- 反驳遇到正数就选的错误连续算法。

**单元测试规格**：
- 长度n的非空子数组数为n(n+1)/2。
- 含空集子序列选择数为2^n。
- 保留重复值时按索引计数。

**边界与生成要求**：代表题用于知识映射；先讲最小问题，再完成本章核心实现。对比与拓展题不强制变成独立完整题解。

---

## 02_array_string_hash｜数组、字符串与哈希

### N017｜数组扫描与原地覆盖

**文件**：`notebooks/02_array_string_hash/017_array_scans_inplace.ipynb`

**层级 / 类型**：L1 / core；**先修**：N005, N013。

**教学目标**：用读写指针维护已处理区间。

**知识点**：单遍扫描；原地契约；有效前缀；覆盖而非删除。

**代表 LeetCode 题**：
- 27. Remove Element — 典型应用；生成前核验题面。
- 283. Move Zeroes — 典型应用；生成前核验题面。

**必须实现的代码**：
- `remove_element(nums, val)`。
- `move_zeroes(nums)`。

**可视化**：读指针、写指针与有效区间动态表。

**练习**：
- 要求保持非零元素相对顺序。
- 把删除特定值推广到谓词过滤。

**单元测试规格**：
- [3,2,2,3],3→有效前缀[2,2]。
- 全删除→长度0。
- 移动零后非零顺序不变。

**边界与生成要求**：代表题用于知识映射；先讲最小问题，再完成本章核心实现。对比与拓展题不强制变成独立完整题解。

---

### N018｜矩阵遍历与边界模拟

**文件**：`notebooks/02_array_string_hash/018_matrix_traversal_simulation.ipynb`

**层级 / 类型**：L1 / core；**先修**：N005, N017。

**教学目标**：将二维坐标变化和边界收缩写成无重复遍历。

**知识点**：行列索引；四方向；转置；螺旋边界；一行一列退化情形。

**代表 LeetCode 题**：
- 54. Spiral Matrix — 典型应用；生成前核验题面。
- 48. Rotate Image — 典型应用；生成前核验题面。

**必须实现的代码**：
- `spiral_order(matrix)`。
- `rotate_square(matrix)`。

**可视化**：网格访问次序与四条边界。

**练习**：
- 实现逆时针螺旋。
- 解释非方阵不能套用原地旋转代码。

**单元测试规格**：
- 2×3矩阵输出6个元素且不重复。
- 1×n与n×1。
- 方阵旋转四次回到原矩阵。

**边界与生成要求**：代表题用于知识映射；先讲最小问题，再完成本章核心实现。对比与拓展题不强制变成独立完整题解。

---

### N019｜哈希查找与索引映射

**文件**：`notebooks/02_array_string_hash/019_hash_lookup_index.ipynb`

**层级 / 类型**：L1 / core；**先修**：N007, N015, N017。

**教学目标**：将两重枚举降为一次扫描和补数查询。

**知识点**：值到索引；先查后存；重复元素；平均复杂度假设。

**代表 LeetCode 题**：
- [1. Two Sum](https://leetcode.com/problems/two-sum/) — 典型应用；官方页面已核对题号与标题。

**必须实现的代码**：
- `two_sum(nums, target)`。
- `two_sum_bruteforce(nums, target)`。

**可视化**：已见元素字典和补数查找流程。

**练习**：
- 扩展为返回全部不同索引对。
- 说明不能重复使用同一元素。

**单元测试规格**：
- [2,7,11,15],9→索引0和1。
- [3,3],6→两个不同索引。
- 小域对拍并规范化输出。

**边界与生成要求**：代表题用于知识映射；先讲最小问题，再完成本章核心实现。对比与拓展题不强制变成独立完整题解。

---

### N020｜频率统计与等价类分组

**文件**：`notebooks/02_array_string_hash/020_hash_frequency_grouping.ipynb`

**层级 / 类型**：L1 / core；**先修**：N006, N007, N019。

**教学目标**：为对象构造不丢失等价信息的键。

**知识点**：频次数组；排序签名；哈希键；Counter；字符集前提。

**代表 LeetCode 题**：
- 242. Valid Anagram — 典型应用；生成前核验题面。
- 49. Group Anagrams — 典型应用；生成前核验题面。

**必须实现的代码**：
- `is_anagram(s, t)`。
- `group_anagrams(words)`。

**可视化**：单词→签名→分组桶图。

**练习**：
- 比较排序签名和计数签名。
- 支持非ASCII字符时调整实现。

**单元测试规格**：
- anagram/nagaram→True。
- rat/car→False。
- 分组结果排序后比较。
- 重复单词不丢失。

**边界与生成要求**：代表题用于知识映射；先讲最小问题，再完成本章核心实现。对比与拓展题不强制变成独立完整题解。

---

### N021｜集合、去重与连续序列

**文件**：`notebooks/02_array_string_hash/021_hash_sets_sequence_dedup.ipynb`

**层级 / 类型**：L1 / core；**先修**：N014, N019。

**教学目标**：只从连续段起点扩展以避免重复工作。

**知识点**：集合查询；起点判定；摊还扫描；重复数字。

**代表 LeetCode 题**：
- 128. Longest Consecutive Sequence — 典型应用；生成前核验题面。
- 349. Intersection of Two Arrays — 典型应用；生成前核验题面。

**必须实现的代码**：
- `longest_consecutive(nums)`。
- `unique_intersection(a, b)`。

**可视化**：整数数轴上的连续段与起点。

**练习**：
- 返回最长连续段本身。
- 构造从每个元素扩展的平方级反例。

**单元测试规格**：
- [100,4,200,1,3,2]→4。
- [1,1,2]→2。
- 空数组→0。
- 与排序参照对拍。

**边界与生成要求**：代表题用于知识映射；先讲最小问题，再完成本章核心实现。对比与拓展题不强制变成独立完整题解。

---

### N022｜字符串映射与字典序

**文件**：`notebooks/02_array_string_hash/022_string_mapping_order.ipynb`

**层级 / 类型**：L1 / core；**先修**：N006, N007。

**教学目标**：用双向映射表达一一对应关系。

**知识点**：字符映射；双射；字典序；前缀关系；位置编码。

**代表 LeetCode 题**：
- 205. Isomorphic Strings — 典型应用；生成前核验题面。
- 290. Word Pattern — 典型应用；生成前核验题面。

**必须实现的代码**：
- `is_isomorphic(s, t)`。
- `word_pattern(pattern, text)`。

**可视化**：两侧字符映射表及冲突位置。

**练习**：
- 解释单向映射不足。
- 构造两个源字符映射到同一目标的反例。

**单元测试规格**：
- egg/add→True。
- foo/bar→False。
- ab/aa→False。
- 长度不一致返回False。

**边界与生成要求**：代表题用于知识映射；先讲最小问题，再完成本章核心实现。对比与拓展题不强制变成独立完整题解。

---

### N023｜字符串解析与有限状态机

**文件**：`notebooks/02_array_string_hash/023_string_parsing_fsm.ipynb`

**层级 / 类型**：L1 / core；**先修**：N002, N006, N016。

**教学目标**：按状态和合法转移解析含符号与边界的输入。

**知识点**：空白；符号；数字扫描；32位截断；状态转移；非法后缀。

**代表 LeetCode 题**：
- 8. String to Integer (atoi) — 典型应用；生成前核验题面。
- 65. Valid Number — 拓展/替代算法，不声称必需或最优；生成前核验题面。

**必须实现的代码**：
- `my_atoi(s)`。
- `is_number(s)`。

**可视化**：解析状态图与指针轨迹。

**练习**：
- 区分完整数字校验和前缀转整数。
- 为指数符号设计状态。

**单元测试规格**：
- 空串→0。
- '  -42'→-42。
- '4193 with words'→4193。
- 超界按32位范围截断。
- 指数缺数字判非法。

**边界与生成要求**：代表题用于知识映射；先讲最小问题，再完成本章核心实现。对比与拓展题不强制变成独立完整题解。

---

### N024｜数组与字符串的结构变换

**文件**：`notebooks/02_array_string_hash/024_array_string_transformations.ipynb`

**层级 / 类型**：L1 / core；**先修**：N017, N018。

**教学目标**：利用位置关系完成旋转、编码和就地变换。

**知识点**：反转分解；循环置换；游程编码；长度与空间契约。

**代表 LeetCode 题**：
- 189. Rotate Array — 典型应用；生成前核验题面。
- 443. String Compression — 典型应用；生成前核验题面。

**必须实现的代码**：
- `rotate_array(nums, k)`。
- `compress(chars)`。

**可视化**：反转三步和压缩读写位置。

**练习**：
- 比较额外数组与原地旋转。
- 扩展多位次数编码。

**单元测试规格**：
- k大于长度时取模。
- 旋转n次位置回归。
- ['a','a','b']有效前缀为['a','2','b']。
- 验证长度返回值。

**边界与生成要求**：代表题用于知识映射；先讲最小问题，再完成本章核心实现。对比与拓展题不强制变成独立完整题解。

---

## 03_pointers_windows｜双指针与滑动窗口

### N025｜相向双指针与有序配对

**文件**：`notebooks/03_pointers_windows/025_opposite_two_pointers.ipynb`

**层级 / 类型**：L2 / core；**先修**：N013, N017, N022。

**教学目标**：利用有序性安全排除不可能答案。

**知识点**：左右端点；单调排除；排序前提；回文过滤。

**代表 LeetCode 题**：
- 167. Two Sum II - Input Array Is Sorted — 典型应用；生成前核验题面。
- 125. Valid Palindrome — 典型应用；生成前核验题面。

**必须实现的代码**：
- `two_sum_sorted(numbers, target)`。
- `is_palindrome(s)`。

**可视化**：左右端点排除区域及回文字符配对。

**练习**：
- 返回0基与1基索引分别测试。
- 构造无序输入使模板失效。

**单元测试规格**：
- [2,7,11,15],9→[1,2]。
- 'A man, a plan, a canal: Panama'→True。
- 小域有序数组对拍。

**边界与生成要求**：代表题用于知识映射；先讲最小问题，再完成本章核心实现。对比与拓展题不强制变成独立完整题解。

---

### N026｜同向双指针与稳定压缩

**文件**：`notebooks/03_pointers_windows/026_same_direction_fast_slow.ipynb`

**层级 / 类型**：L2 / core；**先修**：N017, N025。

**教学目标**：用不同移动速度维护有效前缀和相对顺序。

**知识点**：读写指针；重复计数；最多保留k次；稳定性。

**代表 LeetCode 题**：
- 26. Remove Duplicates from Sorted Array — 典型应用；生成前核验题面。
- 80. Remove Duplicates from Sorted Array II — 典型应用；生成前核验题面。

**必须实现的代码**：
- `remove_duplicates(nums)`。
- `keep_at_most_k(nums, k)`。

**可视化**：读写指针与最近k个保留元素。

**练习**：
- 从最多一次推广到最多k次。
- 说明输入必须有序。

**单元测试规格**：
- [1,1,2]→[1,2]有效前缀。
- 最多2次处理[1,1,1,2,2,3]→[1,1,2,2,3]。
- 全相同与空数组。

**边界与生成要求**：代表题用于知识映射；先讲最小问题，再完成本章核心实现。对比与拓展题不强制变成独立完整题解。

---

### N027｜三数和与双指针消元

**文件**：`notebooks/03_pointers_windows/027_k_sum_and_geometric_elimination.ipynb`

**层级 / 类型**：L2 / core；**先修**：N025, N020。

**教学目标**：将一维单调排除嵌入外层枚举。

**知识点**：排序；去重；固定元素；双指针；面积上界。

**代表 LeetCode 题**：
- 15. 3Sum — 典型应用；生成前核验题面。
- 11. Container With Most Water — 典型应用；生成前核验题面。

**必须实现的代码**：
- `three_sum(nums)`。
- `max_area(height)`。

**可视化**：固定i后左右指针轨迹；短边移动的排除解释。

**练习**：
- 推广四数和。
- 为跳过重复元素给出必要位置。

**单元测试规格**：
- [-1,0,1,2,-1,-4]仅两个不同三元组。
- [0,0,0,0]只返回一个。
- 最大面积与平方级参照对拍。

**边界与生成要求**：代表题用于知识映射；先讲最小问题，再完成本章核心实现。对比与拓展题不强制变成独立完整题解。

---

### N028｜固定长度滑动窗口

**文件**：`notebooks/03_pointers_windows/028_fixed_windows.ipynb`

**层级 / 类型**：L2 / core；**先修**：N020, N025。

**教学目标**：通过移出移入更新固定窗口统计量。

**知识点**：窗口长度；增量更新；频次向量；零长度契约。

**代表 LeetCode 题**：
- 643. Maximum Average Subarray I — 典型应用；生成前核验题面。
- 567. Permutation in String — 典型应用；生成前核验题面。

**必须实现的代码**：
- `max_average(nums, k)`。
- `check_inclusion(s1, s2)`。

**可视化**：窗口滑动时移入、移出与统计变化。

**练习**：
- 实现固定窗口元音计数。
- 比较重算窗口和增量更新。

**单元测试规格**：
- [1,12,-5,-6,50,3],k=4→12.75。
- k=1及k=n。
- ab/eidbaooo→True。
- 浮点结果使用容差。

**边界与生成要求**：代表题用于知识映射；先讲最小问题，再完成本章核心实现。对比与拓展题不强制变成独立完整题解。

---

### N029｜可变窗口与最短覆盖

**文件**：`notebooks/03_pointers_windows/029_variable_windows.ipynb`

**层级 / 类型**：L2 / core；**先修**：N020, N028。

**教学目标**：写出窗口有效条件并按方向收缩。

**知识点**：最长无重复；覆盖频次；缺失计数；收缩条件；可行性单调前提。

**代表 LeetCode 题**：
- [3. Longest Substring Without Repeating Characters](https://leetcode.com/problems/longest-substring-without-repeating-characters/) — 典型应用；官方页面已核对题号与标题。
- 76. Minimum Window Substring — 典型应用；生成前核验题面。

**必须实现的代码**：
- `length_of_longest_substring(s)`。
- `min_window(s, t)`。

**可视化**：窗口边界、字符频次及缺失计数时间线。

**练习**：
- 构造只用集合无法处理重复目标字符的反例。
- 解释非负和窗口的适用条件。

**单元测试规格**：
- abcabcbb→3。
- 空串→0。
- ADOBECODEBANC/ABC→BANC。
- a/aa→空串。
- 小字符集暴力对拍。

**边界与生成要求**：代表题用于知识映射；先讲最小问题，再完成本章核心实现。对比与拓展题不强制变成独立完整题解。

---

### N030｜滑动窗口计数与恰好K

**文件**：`notebooks/03_pointers_windows/030_window_counting_exactly_k.ipynb`

**层级 / 类型**：L4 / core；**先修**：N029, N015。

**教学目标**：从以右端点结尾的合法起点数推导计数。

**知识点**：at_most；exactly差分；非负/单调边界；计数溢出意识。

**代表 LeetCode 题**：
- 992. Subarrays with K Different Integers — 典型应用；生成前核验题面。
- 930. Binary Subarrays With Sum — 典型应用；生成前核验题面。

**必须实现的代码**：
- `at_most_k_distinct(nums, k)`。
- `exactly_k_distinct(nums, k)`。

**可视化**：每个右端点对应合法左端点区间。

**练习**：
- 推导exactly(K)=atMost(K)-atMost(K-1)。
- 解释含负数和限制为何可能失败。

**单元测试规格**：
- [1,2,1,2,3],k=2→7。
- k=0→0个非空子数组。
- 枚举长度≤6数组与暴力计数一致。

**边界与生成要求**：代表题用于知识映射；先讲最小问题，再完成本章核心实现。对比与拓展题不强制变成独立完整题解。

---

## 04_prefix_intervals｜前缀、差分与区间

### N031｜前缀聚合与区间查询

**文件**：`notebooks/04_prefix_intervals/031_prefix_sums_xor_products.ipynb`

**层级 / 类型**：L2 / core；**先修**：N017, N013。

**教学目标**：明确半开区间并区分可逆和不可逆聚合。

**知识点**：前缀和/异或；加法逆元；前后缀乘积；prefix min不能直接相减。

**代表 LeetCode 题**：
- 303. Range Sum Query - Immutable — 典型应用；生成前核验题面。
- 238. Product of Array Except Self — 典型应用；生成前核验题面。

**必须实现的代码**：
- `PrefixSum`。
- `product_except_self(nums)`。

**可视化**：前缀数组长度n+1与区间端点。

**练习**：
- 写出前缀异或查询。
- 构造前缀最小值无法恢复任意区间最小值的反例。

**单元测试规格**：
- [1,2,3]区间[1,3)和为5。
- 空区间和0。
- [1,2,3,4]乘积输出[24,12,8,6]。
- 测试一个零与两个零。

**边界与生成要求**：sum与xor可用逆操作恢复区间聚合；prefix min/max没有对应的通用相减公式。

---

### N032｜前缀和与哈希计数

**文件**：`notebooks/04_prefix_intervals/032_prefix_hash_counting.ipynb`

**层级 / 类型**：L2 / core；**先修**：N019, N031。

**教学目标**：将区间条件改写为前缀值之间的关系。

**知识点**：前缀差；频次与最早位置；余数类；初始前缀0。

**代表 LeetCode 题**：
- [560. Subarray Sum Equals K](https://leetcode.com/problems/subarray-sum-equals-k/) — 典型应用；官方页面已核对题号与标题。
- 523. Continuous Subarray Sum — 典型应用；生成前核验题面。

**必须实现的代码**：
- `subarray_sum(nums, k)`。
- `check_subarray_sum(nums, k)`。

**可视化**：前缀值流、匹配差值及频次更新。

**练习**：
- 分别求个数和最长长度。
- 给出负数使普通和窗口失败的例子。

**单元测试规格**：
- [1,1,1],k=2→2。
- [0,0,0],k=0→6。
- 先查询后更新。
- 余数题长度必须至少2。

**边界与生成要求**：代表题用于知识映射；先讲最小问题，再完成本章核心实现。对比与拓展题不强制变成独立完整题解。

---

### N033｜二维前缀和与容斥

**文件**：`notebooks/04_prefix_intervals/033_prefix_sum_2d.ipynb`

**层级 / 类型**：L2 / core；**先修**：N018, N031。

**教学目标**：用四项容斥查询矩形和且统一坐标约定。

**知识点**：二维累加；边界补零；半开矩形；容斥。

**代表 LeetCode 题**：
- 304. Range Sum Query 2D - Immutable — 典型应用；生成前核验题面。
- 1314. Matrix Block Sum — 典型应用；生成前核验题面。

**必须实现的代码**：
- `PrefixSum2D`。
- `matrix_block_sum(mat, k)`。

**可视化**：目标矩形与三块辅助区域面积示意。

**练习**：
- 不存额外边界行列时比较代码复杂度。
- 扩展统计矩形内非零数。

**单元测试规格**：
- 2×2矩阵[[1,2],[3,4]]全和10。
- 单格查询。
- k覆盖全图。
- 小矩阵逐格求和对拍。

**边界与生成要求**：代表题用于知识映射；先讲最小问题，再完成本章核心实现。对比与拓展题不强制变成独立完整题解。

---

### N034｜差分与批量区间更新

**文件**：`notebooks/04_prefix_intervals/034_difference_arrays.ipynb`

**层级 / 类型**：L2 / core；**先修**：N031, N033。

**教学目标**：把重复区间更新转化为边界事件。

**知识点**：一维/二维差分；前缀还原；端点抵消；闭区间转半开。

**代表 LeetCode 题**：
- 1109. Corporate Flight Bookings — 典型应用；生成前核验题面。
- 1094. Car Pooling — 典型应用；生成前核验题面。

**必须实现的代码**：
- `apply_range_add(n, updates)`。
- `car_pooling(trips, capacity)`。

**可视化**：差分脉冲与还原后的高度图。

**练习**：
- 实现矩形加值的二维差分。
- 解释末端哨兵单元。

**单元测试规格**：
- n=5, bookings=[[1,2,10],[2,3,20],[2,5,25]]→[10,55,45,25,25]。
- 端点贴边。
- 与逐元素更新对拍。

**边界与生成要求**：代表题用于知识映射；先讲最小问题，再完成本章核心实现。对比与拓展题不强制变成独立完整题解。

---

### N035｜区间合并、插入与交集

**文件**：`notebooks/04_prefix_intervals/035_interval_union_intersection.ipynb`

**层级 / 类型**：L2 / core；**先修**：N025, N017。

**教学目标**：明确开闭语义并按排序后的端点处理区间。

**知识点**：重叠判定；排序扫描；区间交集；相邻端点；规范化输出。

**代表 LeetCode 题**：
- 56. Merge Intervals — 典型应用；生成前核验题面。
- 57. Insert Interval — 典型应用；生成前核验题面。
- 986. Interval List Intersections — 典型应用；生成前核验题面。

**必须实现的代码**：
- `merge_intervals(intervals)`。
- `insert_interval(intervals, new)`。
- `interval_intersection(a, b)`。

**可视化**：数轴区间合并前后对照。

**练习**：
- 比较闭区间与半开区间的相邻合并条件。
- 输出覆盖总长度。

**单元测试规格**：
- [[1,3],[2,6],[8,10]]→[[1,6],[8,10]]。
- 嵌套及同端点。
- 输出有序不重叠且覆盖一致。

**边界与生成要求**：代表题用于知识映射；先讲最小问题，再完成本章核心实现。对比与拓展题不强制变成独立完整题解。

---

### N036｜扫描线与事件排序

**文件**：`notebooks/04_prefix_intervals/036_sweep_line_events.ipynb`

**层级 / 类型**：L2 / core；**先修**：N034, N035。

**教学目标**：用事件增减维护时间或空间中的活跃对象。

**知识点**：起止事件；同坐标次序；离线处理；最大重叠；面积扩展。

**代表 LeetCode 题**：
- 1094. Car Pooling — 典型应用；生成前核验题面。
- 2406. Divide Intervals Into Minimum Number of Groups — 典型应用；生成前核验题面。

**必须实现的代码**：
- `max_overlap(intervals, closed)`。
- `min_groups(intervals)`。

**可视化**：事件轴、活跃数阶梯图。

**练习**：
- 分别实现闭区间和半开区间扫描。
- 说明同坐标事件顺序改变答案。

**单元测试规格**：
- 闭区间[1,2]与[2,3]最大重叠2。
- 半开版本为1。
- 完全分离与完全嵌套。
- 与离散点枚举对拍。

**边界与生成要求**：代表题用于知识映射；先讲最小问题，再完成本章核心实现。对比与拓展题不强制变成独立完整题解。

---

## 05_sort_binary_search｜排序与二分

### N037｜基础排序与比较模型

**文件**：`notebooks/05_sort_binary_search/037_elementary_sorts.ipynb`

**层级 / 类型**：L2 / core；**先修**：N017, N011。

**教学目标**：手写简单排序并通过反例理解稳定性。

**知识点**：插入/选择/冒泡；比较与交换；稳定性；原地；排序后置条件。

**代表 LeetCode 题**：
- 912. Sort an Array — 对照或复用已有题；生成前核验题面。

**必须实现的代码**：
- `insertion_sort(a)`。
- `selection_sort(a)`。
- `bubble_sort(a)`。

**可视化**：带原始编号的相等键交换过程。

**练习**：
- 减少冒泡无效扫描。
- 寻找选择排序破坏稳定性的最小例子。

**单元测试规格**：
- 与sorted对拍。
- 空、单元素、全相同、逆序。
- 稳定版本保持相等键原序。

**边界与生成要求**：代表题用于知识映射；先讲最小问题，再完成本章核心实现。对比与拓展题不强制变成独立完整题解。

---

### N038｜归并排序与逆序计数

**文件**：`notebooks/05_sort_binary_search/038_merge_sort_and_inversions.ipynb`

**层级 / 类型**：L2 / core；**先修**：N037, N013, N015。

**教学目标**：从有序子问题合并中同时恢复答案和统计量。

**知识点**：分治；归并；递归树；稳定性；逆序对。

**代表 LeetCode 题**：
- 912. Sort an Array — 典型应用；生成前核验题面。
- 493. Reverse Pairs — 拓展/替代算法，不声称必需或最优；生成前核验题面。

**必须实现的代码**：
- `merge_sort(a)`。
- `count_inversions(a)`。
- `reverse_pairs(a)`。

**可视化**：分治树与跨中点计数指针。

**练习**：
- 区分普通逆序对与a[i]>2*a[j]。
- 用索引区间减少切片。

**单元测试规格**：
- [3,1,2]普通逆序对2。
- [1,3,2,3,1]翻转对2。
- 包含负数。
- 与双循环对拍。

**边界与生成要求**：代表题用于知识映射；先讲最小问题，再完成本章核心实现。对比与拓展题不强制变成独立完整题解。

---

### N039｜快速排序与划分不变量

**文件**：`notebooks/05_sort_binary_search/039_quicksort_partition.ipynb`

**层级 / 类型**：L2 / core；**先修**：N037, N038。

**教学目标**：保持划分区域含义并处理重复元素。

**知识点**：Lomuto/Hoare区别；三路划分；随机枢轴；最坏复杂度；递归深度。

**代表 LeetCode 题**：
- 912. Sort an Array — 对照或复用已有题；生成前核验题面。

**必须实现的代码**：
- `partition3(a, lo, hi)`。
- `quicksort(a, rng)`。

**可视化**：小于、等于、大于枢轴的三段区间。

**练习**：
- 构造固定枢轴退化输入。
- 改为先递归较短区间。

**单元测试规格**：
- 划分后三区满足关系。
- 排序前后多重集合相同。
- 大量重复值。
- 固定随机源可复现。

**边界与生成要求**：代表题用于知识映射；先讲最小问题，再完成本章核心实现。对比与拓展题不强制变成独立完整题解。

---

### N040｜堆排序与非比较排序

**文件**：`notebooks/05_sort_binary_search/040_heapsort_counting_bucket_radix.ipynb`

**层级 / 类型**：L2 / core；**先修**：N037, N039, N011。

**教学目标**：依据键类型和值域选择排序机制。

**知识点**：堆结构导览；计数/桶/基数；稳定子过程；比较下界适用条件。

**代表 LeetCode 题**：
- 912. Sort an Array — 对照或复用已有题；生成前核验题面。
- 164. Maximum Gap — 拓展/替代算法，不声称必需或最优；生成前核验题面。

**必须实现的代码**：
- `heap_sort(a)`。
- `counting_sort(a)`。
- `radix_sort_nonnegative(a)`。

**可视化**：计数桶、位数轮次与堆顶交换示意。

**练习**：
- 支持有负数的计数排序。
- 解释桶排序平均线性需要什么假设。

**单元测试规格**：
- 所有适用输入与sorted一致。
- 非负基数版遇负数明确拒绝。
- 重复键稳定性。
- 过大值域不盲目分配数组。

**边界与生成要求**：桶排序平均复杂度必须注明分布假设；计数/基数排序必须注明值域、键长和桶数。

---

### N041｜快速选择与第K大

**文件**：`notebooks/05_sort_binary_search/041_quickselect_order_statistics.ipynb`

**层级 / 类型**：L2 / core；**先修**：N039。

**教学目标**：只递归包含目标秩的划分区间。

**知识点**：秩；三路划分；期望与最坏复杂度；随机化。

**代表 LeetCode 题**：
- 215. Kth Largest Element in an Array — 典型应用；生成前核验题面。
- 973. K Closest Points to Origin — 典型应用；生成前核验题面。

**必须实现的代码**：
- `quickselect(a, k, rng)`。
- `kth_largest(nums, k)`。

**可视化**：每轮划分后丢弃的无关区间。

**练习**：
- 用堆给出另一解并比较K的影响。
- 保留输入的非原地接口。

**单元测试规格**：
- [3,2,1,5,6,4],k=2→5。
- k=1及n。
- 全重复。
- 与sorted索引结果对拍。

**边界与生成要求**：代表题用于知识映射；先讲最小问题，再完成本章核心实现。对比与拓展题不强制变成独立完整题解。

---

### N042｜二分查找与左右边界

**文件**：`notebooks/05_sort_binary_search/042_binary_search_bounds.ipynb`

**层级 / 类型**：L2 / core；**先修**：N013, N025, N037。

**教学目标**：用统一半开区间维护搜索不变量。

**知识点**：lower_bound/upper_bound；不存在；重复值；中点与边界推进。

**代表 LeetCode 题**：
- [704. Binary Search](https://leetcode.com/problems/binary-search/) — 典型应用；官方页面已核对题号与标题。
- 34. Find First and Last Position of Element in Sorted Array — 典型应用；生成前核验题面。
- 35. Search Insert Position — 典型应用；生成前核验题面。

**必须实现的代码**：
- `lower_bound(a, x)`。
- `upper_bound(a, x)`。
- `search_range(a, x)`。

**可视化**：未决区间与已证伪区间逐步缩小。

**练习**：
- 从lower_bound派生精确查找。
- 写出mid不变导致死循环的反例。

**单元测试规格**：
- [1,2,2,4],2→左右边界1和3。
- 空数组返回0。
- 与bisect对拍。
- 循环迭代数对数增长。

**边界与生成要求**：代表题用于知识映射；先讲最小问题，再完成本章核心实现。对比与拓展题不强制变成独立完整题解。

---

### N043｜二分答案与可行性判定

**文件**：`notebooks/05_sort_binary_search/043_binary_search_on_answer.ipynb`

**层级 / 类型**：L3 / core；**先修**：N042, N016。

**教学目标**：证明谓词单调后在答案空间搜索。

**知识点**：最小可行/最大可行；上下界；整数向上取整；判定器成本。

**代表 LeetCode 题**：
- 875. Koko Eating Bananas — 典型应用；生成前核验题面。
- 1011. Capacity To Ship Packages Within D Days — 典型应用；生成前核验题面。
- 410. Split Array Largest Sum — 典型应用；生成前核验题面。

**必须实现的代码**：
- `min_eating_speed(piles, h)`。
- `ship_within_days(weights, days)`。
- `first_true(lo, hi, feasible)`。

**可视化**：候选答案对应False/True分界。

**练习**：
- 为运力判定给出贪心装载论证。
- 构造不可单调谓词说明不能二分。

**单元测试规格**：
- [3,6,7,11],h=8→4。
- D=1与D=n。
- 小答案范围枚举最小可行值。
- 结果可行且前一个不可行。

**边界与生成要求**：代表题用于知识映射；先讲最小问题，再完成本章核心实现。对比与拓展题不强制变成独立完整题解。

---

### N044｜旋转数组、矩阵与峰值

**文件**：`notebooks/05_sort_binary_search/044_binary_search_structured_data.ipynb`

**层级 / 类型**：L3 / core；**先修**：N018, N042。

**教学目标**：根据局部结构构造正确的舍弃条件。

**知识点**：旋转有序；重复导致退化；矩阵单调；峰值存在性；二维转索引。

**代表 LeetCode 题**：
- 33. Search in Rotated Sorted Array — 典型应用；生成前核验题面。
- 81. Search in Rotated Sorted Array II — 典型应用；生成前核验题面。
- 74. Search a 2D Matrix — 典型应用；生成前核验题面。
- 162. Find Peak Element — 典型应用；生成前核验题面。

**必须实现的代码**：
- `search_rotated_unique(nums, target)`。
- `search_rotated_with_duplicates(nums, target)`。
- `search_matrix(matrix, target)`。
- `find_peak(nums)`。

**可视化**：局部有序段与搜索区间变化。

**练习**：
- 处理旋转数组重复值。
- 比较74的全局有序与240的行列有序。

**单元测试规格**：
- 未旋转与单元素。
- 重复元素反例。
- 峰值返回位置满足邻域条件，不强制唯一答案。
- 小数组与扫描对照。

**边界与生成要求**：代表题用于知识映射；先讲最小问题，再完成本章核心实现。对比与拓展题不强制变成独立完整题解。

---

## 06_linked_lists｜链表

### N045｜链表基础与哨兵节点

**文件**：`notebooks/06_linked_lists/045_linked_list_sentinels.ipynb`

**层级 / 类型**：L2 / core；**先修**：N009, N017。

**教学目标**：安全修改头部和中间节点而不遗失链条。

**知识点**：next重接；dummy；前驱；插入删除；对象身份。

**代表 LeetCode 题**：
- 203. Remove Linked List Elements — 典型应用；生成前核验题面。
- 707. Design Linked List — 典型应用；生成前核验题面。

**必须实现的代码**：
- `remove_elements(head, val)`。
- `MyLinkedList`。

**可视化**：删除前后节点引用重接图。

**练习**：
- 不使用dummy再实现一次。
- 说明两种写法边界复杂度。

**单元测试规格**：
- 删除头节点、尾节点与全部节点。
- 空链表。
- 序列化结果正确且无环。

**边界与生成要求**：代表题用于知识映射；先讲最小问题，再完成本章核心实现。对比与拓展题不强制变成独立完整题解。

---

### N046｜链表反转与局部反转

**文件**：`notebooks/06_linked_lists/046_linked_list_reversal.ipynb`

**层级 / 类型**：L2 / core；**先修**：N045, N013。

**教学目标**：在覆盖next前保存后继并维护已反转前缀。

**知识点**：prev/curr/next；循环不变量；子区间拼接；递归对照。

**代表 LeetCode 题**：
- [206. Reverse Linked List](https://leetcode.com/problems/reverse-linked-list/) — 典型应用；官方页面已核对题号与标题。
- 92. Reverse Linked List II — 典型应用；生成前核验题面。

**必须实现的代码**：
- `reverse_list(head)`。
- `reverse_between(head, left, right)`。

**可视化**：每步已反转前缀与剩余链表。

**练习**：
- 写递归反转并计入调用栈。
- 局部反转后验证两端拼接。

**单元测试规格**：
- [1,2,3]→[3,2,1]。
- 区间[2,4]反转[1,2,3,4,5]→[1,4,3,2,5]。
- 反转两次恢复原节点顺序。

**边界与生成要求**：代表题用于知识映射；先讲最小问题，再完成本章核心实现。对比与拓展题不强制变成独立完整题解。

---

### N047｜快慢指针、环与中点

**文件**：`notebooks/06_linked_lists/047_linked_list_fast_slow.ipynb`

**层级 / 类型**：L2 / core；**先修**：N045, N013。

**教学目标**：解释指针速度关系并处理不同中点约定。

**知识点**：Floyd相遇；环入口推导；奇偶长度；倒数第K个。

**代表 LeetCode 题**：
- 141. Linked List Cycle — 典型应用；生成前核验题面。
- 142. Linked List Cycle II — 典型应用；生成前核验题面。
- 876. Middle of the Linked List — 典型应用；生成前核验题面。
- 19. Remove Nth Node From End of List — 典型应用；生成前核验题面。

**必须实现的代码**：
- `has_cycle(head)`。
- `detect_cycle(head)`。
- `middle_node(head)`。
- `remove_nth_from_end(head, n)`。

**可视化**：环上快慢指针的位置表与距离示意。

**练习**：
- 推导相遇后回到头部的理由。
- 区分偶数长度前中点和后中点。

**单元测试规格**：
- 无环、入口为头、自环。
- 入口比较对象身份。
- 删除首尾节点。
- 中点约定与题目一致。

**边界与生成要求**：代表题用于知识映射；先讲最小问题，再完成本章核心实现。对比与拓展题不强制变成独立完整题解。

---

### N048｜链表合并与归并排序

**文件**：`notebooks/06_linked_lists/048_linked_list_merge_sort.ipynb`

**层级 / 类型**：L2 / core；**先修**：N038, N045, N047。

**教学目标**：复用节点完成有序合并并分析递归空间。

**知识点**：有序合并；断链；快慢分段；自底向上归并。

**代表 LeetCode 题**：
- 21. Merge Two Sorted Lists — 典型应用；生成前核验题面。
- 148. Sort List — 典型应用；生成前核验题面。

**必须实现的代码**：
- `merge_two_lists(a, b)`。
- `sort_list(head)`。

**可视化**：两路指针与逐轮归并段长度。

**练习**：
- 实现迭代自底向上链表归并。
- 说明递归版并非O(1)栈空间。

**单元测试规格**：
- 空链与非空链合并。
- 重复值稳定性。
- 排序后无节点丢失/重复/环。
- 与数组sorted对照。

**边界与生成要求**：代表题用于知识映射；先讲最小问题，再完成本章核心实现。对比与拓展题不强制变成独立完整题解。

---

### N049｜链表重排与回文

**文件**：`notebooks/06_linked_lists/049_linked_list_reordering_palindrome.ipynb`

**层级 / 类型**：L2 / core；**先修**：N046, N047, N048。

**教学目标**：组合中点、反转和合并且明确是否恢复输入。

**知识点**：前后半段；交替拼接；回文比较；修改副作用。

**代表 LeetCode 题**：
- 143. Reorder List — 典型应用；生成前核验题面。
- 234. Palindrome Linked List — 典型应用；生成前核验题面。

**必须实现的代码**：
- `reorder_list(head)`。
- `is_palindrome_list(head, restore=True)`。

**可视化**：链表分割、后段反转与交织过程。

**练习**：
- 回文检查后恢复原链。
- 用额外数组做独立参照。

**单元测试规格**：
- [1,2,2,1]→True。
- [1,2]→False。
- 重排奇偶长度。
- restore=True后节点next关系完全恢复。

**边界与生成要求**：代表题用于知识映射；先讲最小问题，再完成本章核心实现。对比与拓展题不强制变成独立完整题解。

---

### N050｜K组反转、相交与随机指针

**文件**：`notebooks/06_linked_lists/050_linked_list_advanced_structures.ipynb`

**层级 / 类型**：L4 / core；**先修**：N046, N048, N019。

**教学目标**：区分节点身份、引用拓扑与局部重连。

**知识点**：K组边界；指针换轨；深拷贝；随机边；映射与交织法。

**代表 LeetCode 题**：
- 25. Reverse Nodes in k-Group — 典型应用；生成前核验题面。
- 160. Intersection of Two Linked Lists — 典型应用；生成前核验题面。
- 138. Copy List with Random Pointer — 典型应用；生成前核验题面。

**必须实现的代码**：
- `reverse_k_group(head, k)`。
- `get_intersection_node(a, b)`。
- `copy_random_list(head)`。

**可视化**：节点身份与next/random两类边。

**练习**：
- 不足K组保持原序。
- 比较映射拷贝与交织拷贝的空间和副作用。

**单元测试规格**：
- k=1和k>长度。
- 相同值但不相交。
- 拷贝节点与原节点身份不同。
- 随机指针拓扑保持一致。

**边界与生成要求**：代表题用于知识映射；先讲最小问题，再完成本章核心实现。对比与拓展题不强制变成独立完整题解。

---

## 07_stack_queue｜栈、队列与单调结构

### N051｜栈、括号与路径归约

**文件**：`notebooks/07_stack_queue/051_stack_matching_paths.ipynb`

**层级 / 类型**：L2 / core；**先修**：N008, N013。

**教学目标**：把最近未匹配对象作为栈顶状态。

**知识点**：LIFO；括号匹配；消除相邻项；目录栈；空栈。

**代表 LeetCode 题**：
- 20. Valid Parentheses — 典型应用；生成前核验题面。
- 71. Simplify Path — 典型应用；生成前核验题面。
- 1047. Remove All Adjacent Duplicates In String — 典型应用；生成前核验题面。

**必须实现的代码**：
- `is_valid_parentheses(s)`。
- `simplify_path(path)`。
- `remove_adjacent_duplicates(s)`。

**可视化**：输入扫描和栈快照。

**练习**：
- 支持多类括号。
- 解释路径里的...不是上级目录。

**单元测试规格**：
- ()[]{}→True。
- ([)]→False。
- /a/./b/../../c/→/c。
- 连续斜杠和根目录。

**边界与生成要求**：代表题用于知识映射；先讲最小问题，再完成本章核心实现。对比与拓展题不强制变成独立完整题解。

---

### N052｜表达式解析与计算

**文件**：`notebooks/07_stack_queue/052_expression_parsing_stacks.ipynb`

**层级 / 类型**：L2 / core；**先修**：N023, N051。

**教学目标**：按优先级和结合性正确处理运算与括号。

**知识点**：操作数/运算符栈；后缀表达式；一元负号；向零截断除法。

**代表 LeetCode 题**：
- 150. Evaluate Reverse Polish Notation — 典型应用；生成前核验题面。
- 224. Basic Calculator — 典型应用；生成前核验题面。
- 227. Basic Calculator II — 典型应用；生成前核验题面。

**必须实现的代码**：
- `eval_rpn(tokens)`。
- `calculate_basic(s)`。
- `calculate_precedence(s)`。

**可视化**：中缀到求值栈的状态轨迹。

**练习**：
- 为一元负号构造案例。
- 比较Python整除与题意截断。

**单元测试规格**：
- ['2','1','+','3','*']→9。
- 3+2*2→7。
- -3/2按约定→-1。
- 括号嵌套与多位数。

**边界与生成要求**：代表题用于知识映射；先讲最小问题，再完成本章核心实现。对比与拓展题不强制变成独立完整题解。

---

### N053｜队列、双端队列与循环缓冲区

**文件**：`notebooks/07_stack_queue/053_queue_deque_implementations.ipynb`

**层级 / 类型**：L2 / core；**先修**：N008, N014, N051。

**教学目标**：实现FIFO并解释容器操作成本。

**知识点**：环形数组；head/tail/size；满空判定；双端操作；两栈队列。

**代表 LeetCode 题**：
- 622. Design Circular Queue — 典型应用；生成前核验题面。
- 641. Design Circular Deque — 典型应用；生成前核验题面。
- 232. Implement Queue using Stacks — 典型应用；生成前核验题面。

**必须实现的代码**：
- `CircularQueue`。
- `CircularDeque`。
- `TwoStackQueue`。

**可视化**：环形缓冲区下标绕回过程。

**练习**：
- 不用额外size区分满与空并说明容量变化。
- 比较deque与list.pop(0)。

**单元测试规格**：
- 容量1反复入出。
- 满队列拒绝入队。
- 空队列拒绝出队。
- 与deque随机操作对拍。

**边界与生成要求**：代表题用于知识映射；先讲最小问题，再完成本章核心实现。对比与拓展题不强制变成独立完整题解。

---

### N054｜单调栈与最近更大更小元素

**文件**：`notebooks/07_stack_queue/054_monotonic_stack_neighbors.ipynb`

**层级 / 类型**：L2 / core；**先修**：N014, N051。

**教学目标**：依据支配关系移除不可能再有用的候选。

**知识点**：索引栈；严格/非严格；左右边界；循环数组；均摊。

**代表 LeetCode 题**：
- [739. Daily Temperatures](https://leetcode.com/problems/daily-temperatures/) — 典型应用；官方页面已核对题号与标题。
- 496. Next Greater Element I — 典型应用；生成前核验题面。
- 503. Next Greater Element II — 典型应用；生成前核验题面。

**必须实现的代码**：
- `daily_temperatures(t)`。
- `next_greater_circular(nums)`。

**可视化**：每次出栈时确定的最近更大边界。

**练习**：
- 推导前一个更小元素。
- 解释相等元素如何处理。

**单元测试规格**：
- [73,74,75,71,69,72,76,73]→[1,1,4,2,1,1,0,0]。
- 全相同。
- 环形跨尾匹配。
- 每索引入出次数有界。

**边界与生成要求**：代表题用于知识映射；先讲最小问题，再完成本章核心实现。对比与拓展题不强制变成独立完整题解。

---

### N055｜单调栈的面积与贡献计数

**文件**：`notebooks/07_stack_queue/055_monotonic_stack_contributions.ipynb`

**层级 / 类型**：L4 / core；**先修**：N054, N031。

**教学目标**：从元素左右作用范围推导全局统计量。

**知识点**：直方图边界；哨兵；重复值去重归属；子数组贡献；模数。

**代表 LeetCode 题**：
- 84. Largest Rectangle in Histogram — 典型应用；生成前核验题面。
- 907. Sum of Subarray Minimums — 典型应用；生成前核验题面。
- 42. Trapping Rain Water — 对照或复用已有题；生成前核验题面。

**必须实现的代码**：
- `largest_rectangle(heights)`。
- `sum_subarray_mins(nums)`。

**可视化**：柱状图左右边界及每元素负责的区间矩形。

**练习**：
- 推导子数组最大值和。
- 构造两侧同时严格造成重复/漏计的案例。

**单元测试规格**：
- [2,1,5,6,2,3]→10。
- [3,1,2,4]最小值和17。
- 重复高度。
- 与所有区间枚举对拍。

**边界与生成要求**：代表题用于知识映射；先讲最小问题，再完成本章核心实现。对比与拓展题不强制变成独立完整题解。

---

### N056｜单调队列与带负数的最短区间

**文件**：`notebooks/07_stack_queue/056_monotonic_queue_windows.ipynb`

**层级 / 类型**：L4 / core；**先修**：N032, N053, N054。

**教学目标**：同时维护候选顺序和过期边界。

**知识点**：滑窗极值；前缀和支配；双端弹出；负数使普通窗口失效。

**代表 LeetCode 题**：
- 239. Sliding Window Maximum — 典型应用；生成前核验题面。
- [862. Shortest Subarray with Sum at Least K](https://leetcode.com/problems/shortest-subarray-with-sum-at-least-k/) — 典型应用；官方页面已核对题号与标题。

**必须实现的代码**：
- `max_sliding_window(nums, k)`。
- `shortest_subarray(nums, k)`。

**可视化**：队列索引、对应值与被支配候选删除轨迹。

**练习**：
- 解释最短区间中两种弹出条件。
- 构造负数窗口反例。

**单元测试规格**：
- [1,3,-1,-3,5,3,6,7],k=3→[3,3,5,5,6,7]。
- [2,-1,2],K=3→3。
- 无解返回-1。
- 暴力区间对拍。

**边界与生成要求**：代表题用于知识映射；先讲最小问题，再完成本章核心实现。对比与拓展题不强制变成独立完整题解。

---

## 08_heaps｜堆与优先队列

### N057｜二叉堆、建堆与优先队列

**文件**：`notebooks/08_heaps/057_heap_fundamentals.ipynb`

**层级 / 类型**：L2 / core；**先修**：N040, N009, N014。

**教学目标**：实现堆不变量并区分建堆与逐个插入成本。

**知识点**：完全二叉树；sift_up/down；heapify；最小/最大堆；稳定次序键。

**代表 LeetCode 题**：
- 1046. Last Stone Weight — 典型应用；生成前核验题面。
- 703. Kth Largest Element in a Stream — 只作动机预告，不要求提前实现；生成前核验题面。

**必须实现的代码**：
- `MinHeap`。
- `heapify_bottom_up(a)`。
- `last_stone_weight(stones)`。

**可视化**：堆的数组与树形双视图。

**练习**：
- 证明自底向上建堆的线性成本。
- 用负号封装最大堆并说明数据类型限制。

**单元测试规格**：
- 每次操作满足父节点≤子节点。
- 出堆序列等于sorted。
- 全相同与单元素。
- 与heapq操作对拍。

**边界与生成要求**：代表题用于知识映射；先讲最小问题，再完成本章核心实现。对比与拓展题不强制变成独立完整题解。

---

### N058｜Top-K、频率与流式维护

**文件**：`notebooks/08_heaps/058_heap_top_k.ipynb`

**层级 / 类型**：L2 / core；**先修**：N057, N020, N041。

**教学目标**：用大小K的堆保留当前所需候选。

**知识点**：小根堆维护最大K项；频率Top-K；流式输入；K边界。

**代表 LeetCode 题**：
- 215. Kth Largest Element in an Array — 典型应用；生成前核验题面。
- 347. Top K Frequent Elements — 典型应用；生成前核验题面。
- 703. Kth Largest Element in a Stream — 典型应用；生成前核验题面。

**必须实现的代码**：
- `kth_largest_heap(nums, k)`。
- `top_k_frequent(nums, k)`。
- `KthLargest`。

**可视化**：第K大阈值随输入变化。

**练习**：
- 比较排序、快选与堆的时间空间。
- 定义频率并列时的合法输出判定。

**单元测试规格**：
- 经典第2大样例→5。
- 频率并列不强制任意顺序。
- 流式结果逐步与排序参照一致。

**边界与生成要求**：代表题用于知识映射；先讲最小问题，再完成本章核心实现。对比与拓展题不强制变成独立完整题解。

---

### N059｜K路归并与有序候选生成

**文件**：`notebooks/08_heaps/059_heap_k_way_merge.ipynb`

**层级 / 类型**：L2 / core；**先修**：N048, N057。

**教学目标**：维护每一路尚未消费的最小候选。

**知识点**：堆头；惰性推进；元组比较；有序流；去重约定。

**代表 LeetCode 题**：
- 23. Merge k Sorted Lists — 典型应用；生成前核验题面。
- 373. Find K Pairs with Smallest Sums — 典型应用；生成前核验题面。

**必须实现的代码**：
- `merge_k_lists(lists)`。
- `k_smallest_pairs(a, b, k)`。

**可视化**：各路指针与堆中候选矩阵。

**练习**：
- 实现多个有序生成器归并。
- 避免比较不可排序节点对象。

**单元测试规格**：
- 含空链表与重复值。
- 输出长度等于总节点数。
- 小数组数对与笛卡尔积排序参照比较。

**边界与生成要求**：代表题用于知识映射；先讲最小问题，再完成本章核心实现。对比与拓展题不强制变成独立完整题解。

---

### N060｜双堆中位数与延迟删除

**文件**：`notebooks/08_heaps/060_two_heaps_lazy_deletion.ipynb`

**层级 / 类型**：L4 / core；**先修**：N057, N058, N028。

**教学目标**：维护两个半区的秩关系并剔除失效堆顶。

**知识点**：平衡；逻辑大小；延迟计数字典；过期元素；重复值。

**代表 LeetCode 题**：
- 295. Find Median from Data Stream — 典型应用；生成前核验题面。
- 480. Sliding Window Median — 典型应用；生成前核验题面。

**必须实现的代码**：
- `MedianFinder`。
- `sliding_window_median(nums, k)`。

**可视化**：左右堆、逻辑大小与待删除计数。

**练习**：
- 解释物理堆长不等于有效大小。
- 处理连续相等值的过期元素。

**单元测试规格**：
- 插入1,2中位数1.5，再插3为2。
- 滑窗奇偶K。
- 全重复。
- 每步与排序窗口对拍。

**边界与生成要求**：代表题用于知识映射；先讲最小问题，再完成本章核心实现。对比与拓展题不强制变成独立完整题解。

---

### N061｜堆调度与离散事件模拟

**文件**：`notebooks/08_heaps/061_heap_event_scheduling.ipynb`

**层级 / 类型**：L3 / core；**先修**：N036, N057, N059。

**教学目标**：区分按时间推进与逐时刻暴力模拟。

**知识点**：就绪队列；结束事件；空闲时间跳转；排序复合键；双堆。

**代表 LeetCode 题**：
- 1834. Single-Threaded CPU — 典型应用；生成前核验题面。
- 1882. Process Tasks Using Servers — 典型应用；生成前核验题面。

**必须实现的代码**：
- `single_threaded_order(tasks)`。
- `assign_tasks(servers, tasks)`。

**可视化**：甘特图与事件队列变化。

**练习**：
- 构造相同到达时间的多任务。
- 实现小规模逐时刻参照。

**单元测试规格**：
- [[1,2],[2,4],[3,2],[4,1]]执行顺序[0,2,3,1]。
- 长空闲段。
- 同权重按索引打破并列。

**边界与生成要求**：代表题用于知识映射；先讲最小问题，再完成本章核心实现。对比与拓展题不强制变成独立完整题解。

---

## 09_recursion_backtracking｜递归、分治与回溯

### N062｜递归函数契约与调用栈

**文件**：`notebooks/09_recursion_backtracking/062_recursion_contracts.ipynb`

**层级 / 类型**：L2 / core；**先修**：N004, N011, N013。

**教学目标**：按子问题含义编写递归而非猜测执行顺序。

**知识点**：基例；规模递减；参数与返回值；栈空间；尾递归不自动优化。

**代表 LeetCode 题**：
- 509. Fibonacci Number — 对照或复用已有题；生成前核验题面。
- 50. Pow(x, n) — 只作动机预告，不要求提前实现；生成前核验题面。

**必须实现的代码**：
- `factorial(n)`。
- `fib_recursive(n)`。
- `trace_calls(n)`。

**可视化**：调用树和返回值汇合表。

**练习**：
- 将一个递归函数改成显式栈。
- 构造缺失基例的错误并解释。

**单元测试规格**：
- 0!为1。
- fib(0)=0、fib(1)=1。
- 负输入按教学契约拒绝。
- 递归调用数与重复子问题计数。

**边界与生成要求**：代表题用于知识映射；先讲最小问题，再完成本章核心实现。对比与拓展题不强制变成独立完整题解。

---

### N063｜分治的拆分与合并

**文件**：`notebooks/09_recursion_backtracking/063_divide_and_conquer_patterns.ipynb`

**层级 / 类型**：L2 / core；**先修**：N038, N062。

**教学目标**：定义子问题输出并分析合并成本。

**知识点**：递归式；平衡与不平衡划分；分治正确性；主定理适用条件。

**代表 LeetCode 题**：
- 50. Pow(x, n) — 典型应用；生成前核验题面。
- 169. Majority Element — 对照或复用已有题；生成前核验题面。

**必须实现的代码**：
- `fast_pow(x, n)`。
- `majority_divide(nums)`。

**可视化**：指数折半树与区间合并树。

**练习**：
- 比较快速幂和线性乘法。
- 解释0的负指数不在合法输入中。

**单元测试规格**：
- 2^10=1024。
- 2^-2=0.25。
- 指数0。
- 多数元素与计数参照一致，存在性前提单列。

**边界与生成要求**：代表题用于知识映射；先讲最小问题，再完成本章核心实现。对比与拓展题不强制变成独立完整题解。

---

### N064｜子集、排列与组合回溯

**文件**：`notebooks/09_recursion_backtracking/064_subsets_permutations_combinations.ipynb`

**层级 / 类型**：L2 / core；**先修**：N062, N016。

**教学目标**：区分位置选择、使用标记与起点约束。

**知识点**：选择树；choose/explore/undo；路径拷贝；输出规模；完备性。

**代表 LeetCode 题**：
- [78. Subsets](https://leetcode.com/problems/subsets/) — 典型应用；官方页面已核对题号与标题。
- 46. Permutations — 典型应用；生成前核验题面。
- 77. Combinations — 典型应用；生成前核验题面。

**必须实现的代码**：
- `subsets(nums)`。
- `permute(nums)`。
- `combine(n, k)`。

**可视化**：三种选择树并列追踪。

**练习**：
- 不使用库函数枚举。
- 解释保存path引用为何错误。

**单元测试规格**：
- n=3子集8个、排列6个。
- 组合数与math.comb一致。
- 结果无重复且不共享可变列表。

**边界与生成要求**：代表题用于知识映射；先讲最小问题，再完成本章核心实现。对比与拓展题不强制变成独立完整题解。

---

### N065｜回溯去重与剪枝

**文件**：`notebooks/09_recursion_backtracking/065_backtracking_dedup_pruning.ipynb`

**层级 / 类型**：L2 / core；**先修**：N064, N037。

**教学目标**：区分同层重复和同一路径重复使用。

**知识点**：排序；起点；used标记；正数剪枝前提；状态恢复。

**代表 LeetCode 题**：
- 90. Subsets II — 典型应用；生成前核验题面。
- 47. Permutations II — 典型应用；生成前核验题面。
- 39. Combination Sum — 典型应用；生成前核验题面。
- 40. Combination Sum II — 典型应用；生成前核验题面。

**必须实现的代码**：
- `subsets_with_dup(nums)`。
- `permute_unique(nums)`。
- `combination_sum(candidates, target)`。

**可视化**：被跳过的同层分支与合法重复选择。

**练习**：
- 解释有负数时按和超标剪枝可能失效。
- 比较可重复与不可重复选取。

**单元测试规格**：
- [1,2,2]子集6个。
- [1,1,2]排列3个。
- 目标0按契约含空组合。
- 无重复结果且与穷举参照一致。

**边界与生成要求**：代表题用于知识映射；先讲最小问题，再完成本章核心实现。对比与拓展题不强制变成独立完整题解。

---

### N066｜切分回溯与字符串约束

**文件**：`notebooks/09_recursion_backtracking/066_partitioning_and_search_constraints.ipynb`

**层级 / 类型**：L2 / core；**先修**：N023, N064。

**教学目标**：把切分边界当作选择并维护合法前缀。

**知识点**：切分树；回文判断；前导零；剩余长度剪枝；恢复。

**代表 LeetCode 题**：
- 131. Palindrome Partitioning — 典型应用；生成前核验题面。
- 93. Restore IP Addresses — 典型应用；生成前核验题面。

**必须实现的代码**：
- `partition_palindromes(s)`。
- `restore_ip_addresses(s)`。

**可视化**：字符串切分树与剪枝位置。

**练习**：
- 预计算回文表作为进阶对照。
- 说明IP片段不能带多余前导零。

**单元测试规格**：
- aab→[['a','a','b'],['aa','b']]。
- 25525511135得到两解。
- 0000→0.0.0.0。
- 拼接后恢复原输入。

**边界与生成要求**：代表题用于知识映射；先讲最小问题，再完成本章核心实现。对比与拓展题不强制变成独立完整题解。

---

### N067｜网格路径回溯与访问恢复

**文件**：`notebooks/09_recursion_backtracking/067_grid_backtracking.ipynb`

**层级 / 类型**：L2 / core；**先修**：N018, N065。

**教学目标**：区分同一路径访问和全局访问限制。

**知识点**：四邻域；边界；visited；路径状态恢复；剪枝；分支因子。

**代表 LeetCode 题**：
- 79. Word Search — 典型应用；生成前核验题面。
- 980. Unique Paths III — 典型应用；生成前核验题面。

**必须实现的代码**：
- `exist(board, word)`。
- `unique_paths_iii(grid)`。

**可视化**：当前路径、已访问格与返回后的恢复快照。

**练习**：
- 禁止修改输入实现一次。
- 构造全局visited导致漏解的反例。

**单元测试规格**：
- 同一格不能重复用于单词。
- 失败分支后网格完全恢复。
- 小棋盘穷举路线对拍。

**边界与生成要求**：代表题用于知识映射；先讲最小问题，再完成本章核心实现。对比与拓展题不强制变成独立完整题解。

---

### N068｜约束满足、数独与N皇后

**文件**：`notebooks/09_recursion_backtracking/068_constraint_satisfaction_queens_sudoku.ipynb`

**层级 / 类型**：L3 / core；**先修**：N065, N067, N007。

**教学目标**：以约束传播缩小回溯分支并验证完整解。

**知识点**：行列/对角线约束；候选集；最少候选优先；位掩码扩展。

**代表 LeetCode 题**：
- 51. N-Queens — 典型应用；生成前核验题面。
- 37. Sudoku Solver — 典型应用；生成前核验题面。

**必须实现的代码**：
- `solve_n_queens(n)`。
- `solve_sudoku(board)`。

**可视化**：攻击范围与数独候选数热力图。

**练习**：
- 比较固定填格顺序与最少候选优先。
- 统计搜索节点而非只比运行时间。

**单元测试规格**：
- n=4有2解。
- n=1有1解。
- 数独保留题目已知格。
- 每行列宫合法。
- 无解教学输入不伪造答案。

**边界与生成要求**：位掩码皇后仅作拓展，集合版为必做；位掩码拓展先学N124。

---

## 10_trees_tries｜树、BST 与 Trie

### N069｜树的递归与迭代遍历

**文件**：`notebooks/10_trees_tries/069_tree_dfs_traversals.ipynb`

**层级 / 类型**：L2 / core；**先修**：N009, N051, N062。

**教学目标**：把节点处理时机对应到前中后序。

**知识点**：树结构；递归栈；显式栈；遍历输出；N叉树推广。

**代表 LeetCode 题**：
- 144. Binary Tree Preorder Traversal — 典型应用；生成前核验题面。
- 94. Binary Tree Inorder Traversal — 典型应用；生成前核验题面。
- 145. Binary Tree Postorder Traversal — 典型应用；生成前核验题面。

**必须实现的代码**：
- `preorder(root)`。
- `inorder(root)`。
- `postorder_iterative(root)`。
- `nary_preorder(root)`。

**可视化**：节点访问编号与显式栈变化。

**练习**：
- 每种遍历分别实现递归与迭代。
- 比较N叉树的孩子展开顺序。

**单元测试规格**：
- 空树→[]。
- 单节点。
- 偏斜树。
- 递归与迭代输出一致。
- 每节点访问一次。

**边界与生成要求**：代表题用于知识映射；先讲最小问题，再完成本章核心实现。对比与拓展题不强制变成独立完整题解。

---

### N070｜树的层序遍历与视图

**文件**：`notebooks/10_trees_tries/070_tree_bfs_views.ipynb`

**层级 / 类型**：L2 / core；**先修**：N053, N069。

**教学目标**：用层边界区分深度信息和全局队列。

**知识点**：BFS队列；层大小；锯齿遍历；侧视图；N叉树层序。

**代表 LeetCode 题**：
- 102. Binary Tree Level Order Traversal — 典型应用；生成前核验题面。
- 103. Binary Tree Zigzag Level Order Traversal — 典型应用；生成前核验题面。
- 199. Binary Tree Right Side View — 典型应用；生成前核验题面。

**必须实现的代码**：
- `level_order(root)`。
- `zigzag_level_order(root)`。
- `right_side_view(root)`。

**可视化**：树深度层与逐层队列状态。

**练习**：
- 不反转结果列表实现锯齿。
- 解释BFS辅助空间取决于最大层宽。

**单元测试规格**：
- [3,9,20,null,null,15,7]层序三层。
- 右视图[3,20,7]。
- 空树。
- 宽树与链状树。

**边界与生成要求**：代表题用于知识映射；先讲最小问题，再完成本章核心实现。对比与拓展题不强制变成独立完整题解。

---

### N071｜树的自底向上聚合

**文件**：`notebooks/10_trees_tries/071_tree_bottom_up_aggregation.ipynb`

**层级 / 类型**：L2 / core；**先修**：N069, N063。

**教学目标**：从子树返回最小充分信息而非重复遍历。

**知识点**：高度/深度；平衡；直径；后序；返回值与全局答案。

**代表 LeetCode 题**：
- 104. Maximum Depth of Binary Tree — 典型应用；生成前核验题面。
- 110. Balanced Binary Tree — 典型应用；生成前核验题面。
- 543. Diameter of Binary Tree — 典型应用；生成前核验题面。

**必须实现的代码**：
- `max_depth(root)`。
- `is_balanced(root)`。
- `diameter(root)`。

**可视化**：每节点标注左右高度和合并答案。

**练习**：
- 将平衡判断从重复高度计算改为一次遍历。
- 区分按边计与按点计直径。

**单元测试规格**：
- 单节点直径0。
- 三节点链直径2。
- 不平衡深链。
- 与逐点暴力最长路径对拍小树。

**边界与生成要求**：代表题用于知识映射；先讲最小问题，再完成本章核心实现。对比与拓展题不强制变成独立完整题解。

---

### N072｜树上路径与信息传递

**文件**：`notebooks/10_trees_tries/072_tree_path_problems.ipynb`

**层级 / 类型**：L3 / core；**先修**：N071, N032。

**教学目标**：区分向父亲延伸的路径和已完成的双侧路径。

**知识点**：根到叶；任意路径；负贡献截断；前缀计数与回溯清理。

**代表 LeetCode 题**：
- 112. Path Sum — 典型应用；生成前核验题面。
- 113. Path Sum II — 典型应用；生成前核验题面。
- 124. Binary Tree Maximum Path Sum — 典型应用；生成前核验题面。
- 437. Path Sum III — 典型应用；生成前核验题面。

**必须实现的代码**：
- `has_path_sum(root, target)`。
- `max_path_sum(root)`。
- `path_sum_count(root, target)`。

**可视化**：向上传递单臂路径与节点处合并双臂路径。

**练习**：
- 构造不能把双臂路径继续向上传递的反例。
- 清理前缀频次防止跨分支串线。

**单元测试规格**：
- 全负树返回最大节点而非0。
- [-10,9,20,null,null,15,7]最大和42。
- 前缀计数与所有起点暴力对拍。

**边界与生成要求**：代表题用于知识映射；先讲最小问题，再完成本章核心实现。对比与拓展题不强制变成独立完整题解。

---

### N073｜二叉搜索树与有序操作

**文件**：`notebooks/10_trees_tries/073_bst_invariants_operations.ipynb`

**层级 / 类型**：L3 / core；**先修**：N069, N071, N042。

**教学目标**：利用全子树范围约束而非只比较父子。

**知识点**：BST不变量；中序有序；上下界；搜索/插入/删除；后继；退化。

**代表 LeetCode 题**：
- 98. Validate Binary Search Tree — 典型应用；生成前核验题面。
- 230. Kth Smallest Element in a BST — 典型应用；生成前核验题面。
- 450. Delete Node in a BST — 典型应用；生成前核验题面。

**必须实现的代码**：
- `is_valid_bst(root)`。
- `kth_smallest(root, k)`。
- `insert_bst(root, x)`。
- `delete_bst(root, x)`。

**可视化**：搜索路径与两孩子删除的后继替换。

**练习**：
- 明确重复键策略。
- 解释普通BST不保证对数高度。

**单元测试规格**：
- 局部父子合法但远祖越界必须拒绝。
- 删除叶/单孩子/双孩子。
- 中序与排序集合一致。

**边界与生成要求**：代表题用于知识映射；先讲最小问题，再完成本章核心实现。对比与拓展题不强制变成独立完整题解。

---

### N074｜树的构建与序列化

**文件**：`notebooks/10_trees_tries/074_tree_construction_serialization.ipynb`

**层级 / 类型**：L3 / core；**先修**：N019, N069。

**教学目标**：在充分的编码约束下恢复树结构。

**知识点**：前中序划分；索引映射；空节点标记；可逆编码；重复值歧义。

**代表 LeetCode 题**：
- 105. Construct Binary Tree from Preorder and Inorder Traversal — 典型应用；生成前核验题面。
- 106. Construct Binary Tree from Inorder and Postorder Traversal — 典型应用；生成前核验题面。
- 297. Serialize and Deserialize Binary Tree — 典型应用；生成前核验题面。

**必须实现的代码**：
- `build_tree(preorder, inorder)`。
- `serialize(root)`。
- `deserialize(data)`。

**可视化**：遍历区间与根节点分割；编码序列。

**练习**：
- 说明缺少空标记为何可能歧义。
- 设计非法编码的明确错误。

**单元测试规格**：
- serialize/deserialize往返结构相同。
- 空树与负值。
- 构建后遍历恢复输入。
- 不在树编码中使用不受限eval。

**边界与生成要求**：代表题用于知识映射；先讲最小问题，再完成本章核心实现。对比与拓展题不强制变成独立完整题解。

---

### N075｜最近公共祖先与返回值语义

**文件**：`notebooks/10_trees_tries/075_lowest_common_ancestor.ipynb`

**层级 / 类型**：L3 / core；**先修**：N071, N073。

**教学目标**：用子树是否包含目标定义递归返回信息。

**知识点**：普通树LCA；BST路径；节点身份；目标存在性；路径法对照。

**代表 LeetCode 题**：
- 236. Lowest Common Ancestor of a Binary Tree — 典型应用；生成前核验题面。
- 235. Lowest Common Ancestor of a Binary Search Tree — 典型应用；生成前核验题面。

**必须实现的代码**：
- `lowest_common_ancestor(root, p, q)`。
- `lca_bst(root, p, q)`。

**可视化**：两条根路径的公共前缀与递归汇合点。

**练习**：
- 扩展到目标节点可能缺失的自编任务。
- 解释值相同不表示同一节点。

**单元测试规格**：
- 一个目标为另一个祖先。
- 目标在两侧。
- 使用对象身份断言。
- 与根路径法对拍。

**边界与生成要求**：代表题用于知识映射；先讲最小问题，再完成本章核心实现。对比与拓展题不强制变成独立完整题解。

---

### N076｜树的原地变换与Morris遍历

**文件**：`notebooks/10_trees_tries/076_tree_transformations_morris.ipynb`

**层级 / 类型**：L3 / core；**先修**：N046, N069, N074。

**教学目标**：在修改结构时保留并最终恢复必要的链接。

**知识点**：展开链表；镜像；临时线索；Morris；恢复义务；原地空间。

**代表 LeetCode 题**：
- 114. Flatten Binary Tree to Linked List — 典型应用；生成前核验题面。
- 226. Invert Binary Tree — 典型应用；生成前核验题面。
- 94. Binary Tree Inorder Traversal — 拓展/替代算法，不声称必需或最优；生成前核验题面。

**必须实现的代码**：
- `flatten(root)`。
- `invert_tree(root)`。
- `morris_inorder(root)`。

**可视化**：临时线索创建、沿线返回与删除的过程。

**练习**：
- 证明Morris临时边最后会删除。
- 解释早停遍历可能破坏恢复。

**单元测试规格**：
- 展开后right链等于原前序且left全空。
- 镜像两次复原。
- Morris执行前后树结构完全一致。

**边界与生成要求**：代表题用于知识映射；先讲最小问题，再完成本章核心实现。对比与拓展题不强制变成独立完整题解。

---

### N077｜Trie的前缀状态与词典查询

**文件**：`notebooks/10_trees_tries/077_trie_prefix_dictionary.ipynb`

**层级 / 类型**：L2 / core；**先修**：N007, N009, N069。

**教学目标**：把共享前缀编码成树路径并区分词尾。

**知识点**：字符边；终止标记；插入/搜索/前缀；字符集与空间。

**代表 LeetCode 题**：
- 208. Implement Trie (Prefix Tree) — 典型应用；生成前核验题面。
- 648. Replace Words — 典型应用；生成前核验题面。

**必须实现的代码**：
- `Trie.insert(word)`。
- `Trie.search(word)`。
- `Trie.startsWith(prefix)`。
- `replace_words(dictionary, sentence)`。

**可视化**：词典共享前缀树与终止标记。

**练习**：
- 支持删除词并保持其他共享前缀。
- 比较哈希完整词查询与前缀查询。

**单元测试规格**：
- 插入apple后search(app)=False、startsWith(app)=True。
- 重复插入。
- 词本身为其他词前缀。

**边界与生成要求**：代表题用于知识映射；先讲最小问题，再完成本章核心实现。对比与拓展题不强制变成独立完整题解。

---

### N078｜Trie与回溯的组合

**文件**：`notebooks/10_trees_tries/078_trie_backtracking_wildcards.ipynb`

**层级 / 类型**：L4 / core；**先修**：N067, N077。

**教学目标**：用词典前缀剪枝减少无效路径搜索。

**知识点**：Trie状态；通配符分支；网格DFS；结果去重；访问恢复。

**代表 LeetCode 题**：
- 211. Design Add and Search Words Data Structure — 典型应用；生成前核验题面。
- 212. Word Search II — 典型应用；生成前核验题面。

**必须实现的代码**：
- `WordDictionary`。
- `find_words(board, words)`。

**可视化**：网格路径与Trie节点同步推进图。

**练习**：
- 对比逐词搜索和共享Trie搜索。
- 处理词典中重复词与前缀词。

**单元测试规格**：
- bad/dad/mad词典中.a.匹配。
- 网格不重复使用格子。
- 输入网格恢复。
- 与逐词exist参照对拍。

**边界与生成要求**：代表题用于知识映射；先讲最小问题，再完成本章核心实现。对比与拓展题不强制变成独立完整题解。

---

## 11_graphs｜图论

### N079｜图的表示与建模

**文件**：`notebooks/11_graphs/079_graph_representations.ipynb`

**层级 / 类型**：L2 / core；**先修**：N018, N007, N053。

**教学目标**：从关系、网格或依赖中明确顶点、边和方向。

**知识点**：有向/无向；邻接表/矩阵/边表；度；隐式图；自环与重边。

**代表 LeetCode 题**：
- 997. Find the Town Judge — 基础热身；生成前核验题面。
- 1971. Find if Path Exists in Graph — 只作动机预告，不要求提前实现；生成前核验题面。

**必须实现的代码**：
- `build_adj_list(n, edges, directed)`。
- `adj_matrix_to_edges(matrix)`。
- `find_judge(n, trust)`。

**可视化**：同一图的三种表示和网格到图的对应。

**练习**：
- 把棋盘移动规则建模为边。
- 比较稀疏图与稠密图的存储成本。

**单元测试规格**：
- 无向边写入两个方向。
- 孤立顶点保留。
- 法官样例n=2,[[1,2]]→2。
- 转换不意外重复边。

**边界与生成要求**：代表题用于知识映射；先讲最小问题，再完成本章核心实现。对比与拓展题不强制变成独立完整题解。

---

### N080｜DFS、连通分量与环检测

**文件**：`notebooks/11_graphs/080_graph_dfs_components_cycles.ipynb`

**层级 / 类型**：L2 / core；**先修**：N062, N067, N079。

**教学目标**：用访问状态区分未访问、搜索中和已完成。

**知识点**：递归/迭代DFS；洪泛；分量；有向三色法；无向父边。

**代表 LeetCode 题**：
- 200. Number of Islands — 典型应用；生成前核验题面。
- 547. Number of Provinces — 典型应用；生成前核验题面。
- 133. Clone Graph — 典型应用；生成前核验题面。

**必须实现的代码**：
- `count_components(n, edges)`。
- `num_islands(grid)`。
- `has_directed_cycle(adj)`。
- `clone_graph(node)`。

**可视化**：DFS森林、发现顺序和回边。

**练习**：
- 用迭代DFS避免深递归。
- 比较有向与无向环检测条件。

**单元测试规格**：
- 空教学图与孤立点。
- 有向自环。
- 克隆图身份不同但邻接关系同构。
- 小图与并行独立可达性参照比较。

**边界与生成要求**：代表题用于知识映射；先讲最小问题，再完成本章核心实现。对比与拓展题不强制变成独立完整题解。

---

### N081｜BFS、最短步数与多源扩散

**文件**：`notebooks/11_graphs/081_graph_bfs_multisource.ipynb`

**层级 / 类型**：L2 / core；**先修**：N053, N079, N080。

**教学目标**：在等权边图上按距离层发现节点。

**知识点**：队列；入队即标记；多源初始化；网格最短路；不可达。

**代表 LeetCode 题**：
- 994. Rotting Oranges — 典型应用；生成前核验题面。
- 542. 01 Matrix — 典型应用；生成前核验题面。
- 1091. Shortest Path in Binary Matrix — 典型应用；生成前核验题面。

**必须实现的代码**：
- `bfs_distances(adj, sources)`。
- `oranges_rotting(grid)`。
- `update_matrix(mat)`。

**可视化**：逐轮扩散波前与距离矩阵。

**练习**：
- 把单源搜索改成多源。
- 解释一般非等权边不能直接用普通BFS。

**单元测试规格**：
- 全部新鲜但无腐烂源→-1。
- 没有新鲜橙→0。
- 多源距离等于各单源最小值。
- 对角移动规则单独测试。

**边界与生成要求**：代表题用于知识映射；先讲最小问题，再完成本章核心实现。对比与拓展题不强制变成独立完整题解。

---

### N082｜拓扑排序与依赖图

**文件**：`notebooks/11_graphs/082_topological_sort_dag.ipynb`

**层级 / 类型**：L3 / core；**先修**：N079, N080, N081。

**教学目标**：判断是否存在合法依赖顺序并处理多解。

**知识点**：入度；Kahn；三色DFS；DAG；环；偏序与全序。

**代表 LeetCode 题**：
- [207. Course Schedule](https://leetcode.com/problems/course-schedule/) — 典型应用；官方页面已核对题号与标题。
- 210. Course Schedule II — 典型应用；生成前核验题面。

**必须实现的代码**：
- `topological_sort(n, edges)`。
- `can_finish(n, prerequisites)`。
- `find_order(n, prerequisites)`。

**可视化**：入度归零队列与剩余边。

**练习**：
- 返回任一合法顺序而不是指定顺序。
- 扩展输出每门课最早层次。

**单元测试规格**：
- 无依赖。
- 有向环。
- 多种有效顺序均接受。
- 对每条边验证拓扑位置。
- 不要求唯一输出。

**边界与生成要求**：代表题用于知识映射；先讲最小问题，再完成本章核心实现。对比与拓展题不强制变成独立完整题解。

---

### N083｜并查集与动态连通性

**文件**：`notebooks/11_graphs/083_disjoint_set_union.ipynb`

**层级 / 类型**：L2 / core；**先修**：N079, N080, N014。

**教学目标**：只维护等价类信息并识别不支持的操作。

**知识点**：find/union；路径压缩；按大小合并；均摊；连通块计数。

**代表 LeetCode 题**：
- 684. Redundant Connection — 典型应用；生成前核验题面。
- 721. Accounts Merge — 典型应用；生成前核验题面。
- 1319. Number of Operations to Make Network Connected — 典型应用；生成前核验题面。

**必须实现的代码**：
- `DSU`。
- `find_redundant_connection(edges)`。
- `accounts_merge(accounts)`。

**可视化**：合并前后父指针森林。

**练习**：
- 对比连通性与路径查询。
- 解释普通DSU不能直接删除边。

**单元测试规格**：
- 重复union不减少分量数。
- [[1,2],[1,3],[2,3]]冗余边[2,3]。
- 随机小图与BFS连通性对拍。

**边界与生成要求**：代表题用于知识映射；先讲最小问题，再完成本章核心实现。对比与拓展题不强制变成独立完整题解。

---

### N084｜Dijkstra与0-1 BFS

**文件**：`notebooks/11_graphs/084_dijkstra_zero_one_bfs.ipynb`

**层级 / 类型**：L3 / core；**先修**：N057, N081, N013。

**教学目标**：根据权值范围选择正确的最短路调度规则。

**知识点**：非负边；松弛；过期堆项；0/1边；deque前后插入；最短路树。

**代表 LeetCode 题**：
- 743. Network Delay Time — 典型应用；生成前核验题面。
- 1368. Minimum Cost to Make at Least One Valid Path in a Grid — 典型应用；生成前核验题面。

**必须实现的代码**：
- `dijkstra(n, adj, source)`。
- `zero_one_bfs(n, adj, source)`。
- `network_delay_time(times, n, k)`。

**可视化**：距离估计、定型顺序和松弛边。

**练习**：
- 解释负边破坏Dijkstra论证。
- 用0-1 BFS替换堆并比较操作数。

**单元测试规格**：
- [[2,1,1],[2,3,1],[3,4,1]],n=4,k=2→2。
- 不可达→-1。
- 0权环。
- 与Bellman式小图参照对拍。

**边界与生成要求**：只在非负权条件下使用Dijkstra；0-1 BFS的边权必须属于{0,1}。

---

### N085｜Bellman-Ford、受限路径与Floyd

**文件**：`notebooks/11_graphs/085_bellman_ford_floyd.ipynb`

**层级 / 类型**：L3 / core；**先修**：N084, N031。

**教学目标**：区分限制边数的路径和一般最短路径。

**知识点**：分轮松弛；上一轮副本；负边/负环；全源DP；中间点顺序。

**代表 LeetCode 题**：
- 787. Cheapest Flights Within K Stops — 典型应用；生成前核验题面。
- 1334. Find the City With the Smallest Number of Neighbors at a Threshold Distance — 典型应用；生成前核验题面。

**必须实现的代码**：
- `bellman_ford(n, edges, source)`。
- `cheapest_flights(n, flights, src, dst, k)`。
- `floyd_warshall(n, edges)`。
- `find_the_city(n, edges, threshold)`。

**可视化**：按边数与按允许中间点的距离表。

**练习**：
- 构造原地松弛违反K站限制的例子。
- 对自编图加入可达负环检测。

**单元测试规格**：
- 0次中转只能用直达。
- 不可达。
- 平行边取最小。
- 非负小图与Dijkstra互验。
- 负环只在明确支持的教学接口测试。
- 阈值内可达城市数并列时按题意选最大编号。

**边界与生成要求**：代表题用于知识映射；先讲最小问题，再完成本章核心实现。对比与拓展题不强制变成独立完整题解。

---

### N086｜最小生成树与割性质

**文件**：`notebooks/11_graphs/086_minimum_spanning_trees.ipynb`

**层级 / 类型**：L3 / core；**先修**：N083, N084。

**教学目标**：区分连接全部顶点的最小总成本和最短路。

**知识点**：Kruskal；Prim；割性质；环性质；DSU；图不连通。

**代表 LeetCode 题**：
- 1584. Min Cost to Connect All Points — 典型应用；生成前核验题面。
- 1489. Find Critical and Pseudo-Critical Edges in Minimum Spanning Tree — 拓展/替代算法，不声称必需或最优；生成前核验题面。

**必须实现的代码**：
- `kruskal(n, edges)`。
- `prim(n, adj)`。
- `min_cost_connect_points(points)`。

**可视化**：每次跨割选择的边与逐步生成的森林。

**练习**：
- 构造MST路径不是最短路径的反例。
- 处理不连通图并明确返回契约。

**单元测试规格**：
- 单顶点成本0。
- 已知三角形权值1,2,3成本3。
- 相同权重允许多棵树。
- 小图穷举生成树对拍。

**边界与生成要求**：代表题用于知识映射；先讲最小问题，再完成本章核心实现。对比与拓展题不强制变成独立完整题解。

---

### N087｜二分图、增广路与匹配

**文件**：`notebooks/11_graphs/087_bipartite_graphs_matching.ipynb`

**层级 / 类型**：L3 / core；**先修**：N080, N081。

**教学目标**：用交替路径扩展匹配并识别适用图结构。

**知识点**：二染色；奇环；匹配；交替/增广路；Kőnig定理的条件。

**代表 LeetCode 题**：
- 785. Is Graph Bipartite? — 典型应用；生成前核验题面。
- 886. Possible Bipartition — 典型应用；生成前核验题面。
- [1349. Maximum Students Taking Exam](https://leetcode.com/problems/maximum-students-taking-exam/) — 拓展/替代算法，不声称必需或最优；官方页面已核对题号与标题。

**必须实现的代码**：
- `is_bipartite(adj)`。
- `maximum_bipartite_matching(left_adj, right_size)`。

**可视化**：二分图颜色与增广路径翻转。

**练习**：
- 把考场冲突图按列奇偶划分。
- 比较最大匹配与贪心随便配对。

**单元测试规格**：
- 三角形不可二分。
- 偶环可二分。
- 存在重配才能增广的例子。
- 小图匹配结果与穷举对拍。

**边界与生成要求**：1349是匹配归约拓展；先明确冲突图的二分性质，再用Kőnig定理。不能对任意冲突图照搬。

---

### N088｜强连通分量与缩点

**文件**：`notebooks/11_graphs/088_strongly_connected_components.ipynb`

**层级 / 类型**：L4 / advanced_extension；**先修**：N080, N082。

**教学目标**：把有向循环压缩为DAG并追踪安全状态。

**知识点**：Kosaraju；Tarjan lowlink；栈内标记；缩点；终止状态。

**代表 LeetCode 题**：
- [802. Find Eventual Safe States](https://leetcode.com/problems/find-eventual-safe-states/) — 拓展/替代算法，不声称必需或最优；官方页面已核对题号与标题。

**必须实现的代码**：
- `kosaraju_scc(adj)`。
- `tarjan_scc(adj)`。
- `condensation_graph(adj, component)`。

**可视化**：发现时间、lowlink与缩点前后图。

**练习**：
- 以反向拓扑法作802对照。
- 解释不在栈内节点不能直接更新Tarjan回边值。

**单元测试规格**：
- 单点自环为环分量。
- 相互可达点同分量。
- 缩点图无环。
- 两种SCC算法经规范化后分区一致。

**边界与生成要求**：SCC是802的教学替代解法；反向拓扑或三色DFS通常已足够。

---

### N089｜桥、割点与low-link

**文件**：`notebooks/11_graphs/089_bridges_articulation_points.ipynb`

**层级 / 类型**：L4 / advanced_extension；**先修**：N080, N088。

**教学目标**：根据DFS子树能否绕回祖先判断脆弱连接。

**知识点**：发现时间；low；父边编号；桥；根割点特例；重边扩展。

**代表 LeetCode 题**：
- [1192. Critical Connections in a Network](https://leetcode.com/problems/critical-connections-in-a-network/) — 典型应用；官方页面已核对题号与标题。
- 1568. Minimum Number of Days to Disconnect Island — 拓展/替代算法，不声称必需或最优；生成前核验题面。

**必须实现的代码**：
- `find_bridges(n, edges)`。
- `articulation_points(n, edges)`。

**可视化**：DFS树边、回边与low值回传。

**练习**：
- 用删边/删点暴力验证。
- 把无重边题扩展到多重图并按边ID处理。

**单元测试规格**：
- 三角形接单叶只叶边为桥。
- 树上每边为桥。
- DFS根只有一个孩子不是割点。
- 小图逐删边对拍。

**边界与生成要求**：代表题用于知识映射；先讲最小问题，再完成本章核心实现。对比与拓展题不强制变成独立完整题解。

---

### N090｜欧拉路径与Hierholzer

**文件**：`notebooks/11_graphs/090_eulerian_paths.ipynb`

**层级 / 类型**：L4 / advanced_extension；**先修**：N051, N079, N080, N037。

**教学目标**：在边不重用条件下构造完整行程。

**知识点**：边与点遍历区别；度条件；连通性；后序构造；词典序；重复边。

**代表 LeetCode 题**：
- 332. Reconstruct Itinerary — 典型应用；生成前核验题面。
- 2097. Valid Arrangement of Pairs — 典型应用；生成前核验题面。

**必须实现的代码**：
- `eulerian_path(edges)`。
- `find_itinerary(tickets)`。

**可视化**：沿边行走、局部闭环和倒序拼接。

**练习**：
- 构造逐步选最小边但不回溯会卡住的例子。
- 检查重票按多重边消费。

**单元测试规格**：
- 行程长度为边数+1。
- 每张票恰用一次。
- 重复票。
- 返回合法行程，不仅比较起点终点。

**边界与生成要求**：代表题用于知识映射；先讲最小问题，再完成本章核心实现。对比与拓展题不强制变成独立完整题解。

---

### N091｜函数图、环与入树

**文件**：`notebooks/11_graphs/091_functional_graphs.ipynb`

**层级 / 类型**：L4 / advanced_extension；**先修**：N082, N083, N088。

**教学目标**：利用每点至多一条出边分离环和链。

**知识点**：入度剥离；访问时间戳；环长；入树最长链；二元环特例。

**代表 LeetCode 题**：
- 2360. Longest Cycle in a Graph — 典型应用；生成前核验题面。
- 2127. Maximum Employees to Be Invited to a Meeting — 典型应用；生成前核验题面。

**必须实现的代码**：
- `longest_cycle(edges)`。
- `maximum_invitations(favorite)`。

**可视化**：函数图中的环、尾链和剥离层。

**练习**：
- 区分最大环与多个二元环加链的组合。
- 给出普通拓扑不能删除环的解释。

**单元测试规格**：
- 无环返回-1。
- 自编自环按接口处理。
- 两个独立二元环。
- 小规模邀请排列穷举校验。

**边界与生成要求**：代表题用于知识映射；先讲最小问题，再完成本章核心实现。对比与拓展题不强制变成独立完整题解。

---

### N092｜网络流、最小割与匹配归约

**文件**：`notebooks/11_graphs/092_max_flow_min_cut.ipynb`

**层级 / 类型**：L5 / advanced_extension；**先修**：N084, N087, N082。

**教学目标**：在小网络上实现流并以割容量验证最优性。

**知识点**：容量；流守恒；残量网络；反向边；Dinic层次图；最大流最小割。

**代表 LeetCode 题**：
- [1349. Maximum Students Taking Exam](https://leetcode.com/problems/maximum-students-taking-exam/) — 拓展/替代算法，不声称必需或最优；官方页面已核对题号与标题。

**必须实现的代码**：
- `Dinic.add_edge(u, v, capacity)`。
- `Dinic.max_flow(source, sink)`。
- `min_cut_reachable(source)`。
- `matching_via_flow(left_adj, right_size)`。

**可视化**：增广前后残量容量与最终割。

**练习**：
- 把二分匹配归约为单位容量流。
- 说明本章为通用算法拓展而非1349必需解法。

**单元测试规格**：
- 流量非负且不超容量。
- 中间点流守恒。
- 最大流等于最终割容量。
- 小图穷举割对拍。
- 0容量边。

**边界与生成要求**：网络流为精通拓展。1349可用轮廓DP或匹配；本章不能宣称网络流是该题必需方法。

---

## 12_greedy｜贪心

### N093｜贪心选择与交换论证

**文件**：`notebooks/12_greedy/093_greedy_exchange_intervals.ipynb`

**层级 / 类型**：L3 / core；**先修**：N035, N013, N016。

**教学目标**：用局部替换证明而不是用样例支持贪心。

**知识点**：最早结束；交换论证；最优解保持；排序策略反例。

**代表 LeetCode 题**：
- [435. Non-overlapping Intervals](https://leetcode.com/problems/non-overlapping-intervals/) — 典型应用；官方页面已核对题号与标题。
- 646. Maximum Length of Pair Chain — 典型应用；生成前核验题面。

**必须实现的代码**：
- `erase_overlap_intervals(intervals)`。
- `find_longest_chain(pairs)`。

**可视化**：不同排序策略产生的区间选择。

**练习**：
- 反驳按最短区间优先。
- 明确相邻端点在不同题目的兼容条件。

**单元测试规格**：
- [[1,2],[2,3],[3,4],[1,3]]最少删除1。
- 全重叠。
- 小区间集合穷举最优子集对拍。

**边界与生成要求**：代表题用于知识映射；先讲最小问题，再完成本章核心实现。对比与拓展题不强制变成独立完整题解。

---

### N094｜覆盖前沿、跳跃与层次贪心

**文件**：`notebooks/12_greedy/094_greedy_reachability_layers.ipynb`

**层级 / 类型**：L3 / core；**先修**：N013, N081。

**教学目标**：把可达位置集合压缩为最远边界。

**知识点**：最远可达；当前层/下一层；不可达；贪心领先性。

**代表 LeetCode 题**：
- 55. Jump Game — 典型应用；生成前核验题面。
- 45. Jump Game II — 典型应用；生成前核验题面。

**必须实现的代码**：
- `can_jump(nums)`。
- `min_jumps(nums)`。

**可视化**：当前步数覆盖区间与扩展前沿。

**练习**：
- 解释为什么选择当前能跳最远的落点不等于正确的前沿算法。
- 加入不可达教学变体。

**单元测试规格**：
- [2,3,1,1,4]可达且最少2跳。
- [3,2,1,0,4]不可达。
- 长度1为0跳。
- 与BFS位置图对拍。

**边界与生成要求**：代表题用于知识映射；先讲最小问题，再完成本章核心实现。对比与拓展题不强制变成独立完整题解。

---

### N095｜收支平衡与双向约束

**文件**：`notebooks/12_greedy/095_greedy_balance_two_pass.ipynb`

**层级 / 类型**：L3 / core；**先修**：N031, N093。

**教学目标**：用前缀亏损和两侧约束推导贪心。

**知识点**：前缀最小；候选起点排除；两遍扫描；局部约束合并。

**代表 LeetCode 题**：
- 134. Gas Station — 典型应用；生成前核验题面。
- 135. Candy — 典型应用；生成前核验题面。

**必须实现的代码**：
- `can_complete_circuit(gas, cost)`。
- `candy(ratings)`。

**可视化**：油量前缀曲线；左右糖果约束图。

**练习**：
- 证明一次失败能排除一段起点。
- 为什么糖果只从左向右扫描不够。

**单元测试规格**：
- gas=[1,2,3,4,5],cost=[3,4,5,1,2]→3。
- 总油不足→-1。
- ratings=[1,0,2]糖果5。
- 小规模穷举对拍。

**边界与生成要求**：代表题用于知识映射；先讲最小问题，再完成本章核心实现。对比与拓展题不强制变成独立完整题解。

---

### N096｜堆贪心与撤销局部决策

**文件**：`notebooks/12_greedy/096_greedy_heap_replacement.ipynb`

**层级 / 类型**：L4 / core；**先修**：N057, N061, N093。

**教学目标**：在资源受限时替换已选集合中的最差元素。

**知识点**：截止期排序；最大堆替换；可用项目；预算阈值；交换证明。

**代表 LeetCode 题**：
- 630. Course Schedule III — 典型应用；生成前核验题面。
- 502. IPO — 典型应用；生成前核验题面。

**必须实现的代码**：
- `schedule_course(courses)`。
- `find_maximized_capital(k, w, profits, capital)`。

**可视化**：截止期推进和已选集合替换。

**练习**：
- 构造永不撤销选择导致次优的实例。
- 用子集穷举作参照。

**单元测试规格**：
- 无法完成任何课程。
- 相同截止期。
- 无可选项目提前终止。
- 小实例和穷举最优数量/收益一致。

**边界与生成要求**：代表题用于知识映射；先讲最小问题，再完成本章核心实现。对比与拓展题不强制变成独立完整题解。

---

### N097｜字典序构造与剩余可行性

**文件**：`notebooks/12_greedy/097_greedy_lexicographic_construction.ipynb`

**层级 / 类型**：L3 / core；**先修**：N054, N020, N093。

**教学目标**：兼顾当前更优字符和未来完成约束。

**知识点**：单调栈；剩余次数；去重标记；前导零；构造可行性。

**代表 LeetCode 题**：
- 402. Remove K Digits — 典型应用；生成前核验题面。
- 316. Remove Duplicate Letters — 典型应用；生成前核验题面。
- 767. Reorganize String — 拓展/替代算法，不声称必需或最优；生成前核验题面。

**必须实现的代码**：
- `remove_k_digits(num, k)`。
- `remove_duplicate_letters(s)`。
- `reorganize_string(s)`。

**可视化**：弹出较差字符时剩余资源与可行性。

**练习**：
- 证明字符以后不再出现时不能弹出。
- 比较数值最小与字典序最小。

**单元测试规格**：
- 1432219,k=3→1219。
- 10200,k=1→200。
- cbacdcbc→acdb。
- 重排结果保留频次且无相邻相等。

**边界与生成要求**：代表题用于知识映射；先讲最小问题，再完成本章核心实现。对比与拓展题不强制变成独立完整题解。

---

## 13_dynamic_programming｜动态规划

### N098｜从递归到记忆化与表格

**文件**：`notebooks/13_dynamic_programming/098_dp_from_recursion_to_tables.ipynb`

**层级 / 类型**：L2 / core；**先修**：N062, N079, N015。

**教学目标**：从重复子问题推导状态和计算顺序。

**知识点**：状态充分性；缓存键；依赖DAG；基例；top-down/bottom-up；不可达。

**代表 LeetCode 题**：
- 70. Climbing Stairs — 典型应用；生成前核验题面。
- 322. Coin Change — 只作动机预告，不要求提前实现；生成前核验题面。

**必须实现的代码**：
- `climb_stairs_recursive(n)`。
- `climb_stairs_memo(n)`。
- `climb_stairs_table(n)`。

**可视化**：调用树压缩成状态DAG再展开成表。

**练习**：
- 解释缓存可变全局参数的风险。
- 用状态数而非递归树节点数分析。

**单元测试规格**：
- n=1→1、n=2→2、n=5→8。
- 三实现小规模一致。
- 缓存不同问题时隔离。

**边界与生成要求**：代表题用于知识映射；先讲最小问题，再完成本章核心实现。对比与拓展题不强制变成独立完整题解。

---

### N099｜一维DP与以当前位置结尾的状态

**文件**：`notebooks/13_dynamic_programming/099_linear_dp_and_kadane.ipynb`

**层级 / 类型**：L2 / core；**先修**：N098, N015。

**教学目标**：区分前缀最优和必须选当前位置的最优。

**知识点**：线性递推；House Robber；Kadane；滚动变量；负数基例。

**代表 LeetCode 题**：
- [198. House Robber](https://leetcode.com/problems/house-robber/) — 典型应用；官方页面已核对题号与标题。
- 213. House Robber II — 典型应用；生成前核验题面。
- 53. Maximum Subarray — 典型应用；生成前核验题面。

**必须实现的代码**：
- `rob(nums)`。
- `rob_circular(nums)`。
- `max_subarray(nums)`。

**可视化**：每位置选/不选与结尾最优两类表。

**练习**：
- 把环拆成互斥首尾约束。
- 返回一条最优选择方案。

**单元测试规格**：
- [2,7,9,3,1]→12。
- 环[2,3,2]→3。
- 全负最大子数组不返回0。
- 与枚举独立集/区间对拍。

**边界与生成要求**：代表题用于知识映射；先讲最小问题，再完成本章核心实现。对比与拓展题不强制变成独立完整题解。

---

### N100｜网格DP与路径状态

**文件**：`notebooks/13_dynamic_programming/100_grid_dp.ipynb`

**层级 / 类型**：L2 / core；**先修**：N018, N098, N031。

**教学目标**：根据允许方向建立无环转移并处理障碍。

**知识点**：坐标状态；边界；路径计数；最小代价；逆向需求状态。

**代表 LeetCode 题**：
- 62. Unique Paths — 典型应用；生成前核验题面。
- 63. Unique Paths II — 典型应用；生成前核验题面。
- 64. Minimum Path Sum — 典型应用；生成前核验题面。
- 174. Dungeon Game — 典型应用；生成前核验题面。

**必须实现的代码**：
- `unique_paths(m, n)`。
- `unique_paths_with_obstacles(grid)`。
- `min_path_sum(grid)`。
- `calculate_minimum_hp(dungeon)`。

**可视化**：网格转移箭头及逆向所需生命值。

**练习**：
- 对比最小路径和与最低初始生命值的状态。
- 滚动到一行。

**单元测试规格**：
- 3×7无障碍路径28。
- 起终点被阻挡→0。
- 单格地牢[-5]需6。
- 小网格路径枚举对拍。

**边界与生成要求**：代表题用于知识映射；先讲最小问题，再完成本章核心实现。对比与拓展题不强制变成独立完整题解。

---

### N101｜0/1背包与逆序容量

**文件**：`notebooks/13_dynamic_programming/101_zero_one_knapsack.ipynb`

**层级 / 类型**：L3 / core；**先修**：N098, N064。

**教学目标**：证明滚动数组逆序更新避免重复用物品。

**知识点**：物品维度；容量；最大值/可达；恰好/至多；负无穷初始化。

**代表 LeetCode 题**：
- 416. Partition Equal Subset Sum — 典型应用；生成前核验题面。
- 494. Target Sum — 典型应用；生成前核验题面。
- 1049. Last Stone Weight II — 典型应用；生成前核验题面。

**必须实现的代码**：
- `knapsack_01(weights, values, capacity)`。
- `can_partition(nums)`。
- `find_target_sum_ways(nums, target)`。

**可视化**：二维表到一维逆序更新的依赖。

**练习**：
- 用正序更新构造重复拿物品反例。
- 推导目标和向子集计数的转换。

**单元测试规格**：
- [1,5,11,5]可等分。
- 单物品不能重复用。
- [0,0],target=0有4种符号方案。
- 与子集穷举对拍。

**边界与生成要求**：代表题用于知识映射；先讲最小问题，再完成本章核心实现。对比与拓展题不强制变成独立完整题解。

---

### N102｜完全、多重与分组背包

**文件**：`notebooks/13_dynamic_programming/102_unbounded_bounded_group_knapsack.ipynb`

**层级 / 类型**：L3 / core；**先修**：N101, N098。

**教学目标**：根据可重复次数和对象顺序选择转移与循环顺序。

**知识点**：正序容量；有限次数；二进制分组；分组选择；组合/排列计数。

**代表 LeetCode 题**：
- 322. Coin Change — 典型应用；生成前核验题面。
- 518. Coin Change II — 典型应用；生成前核验题面。
- 377. Combination Sum IV — 典型应用；生成前核验题面。

**必须实现的代码**：
- `coin_change(coins, amount)`。
- `coin_change_combinations(coins, amount)`。
- `ordered_sum_count(nums, target)`。
- `bounded_knapsack(items, capacity)`。

**可视化**：不同循环顺序对应的选择序列图。

**练习**：
- 手写分组背包小例。
- 比较硬币组合数与有序方案数。

**单元测试规格**：
- coins=[1,2,5],amount=5组合4。
- [1,2],target=3排列3、组合2。
- 不可达返回约定值。
- 有限次数与展开物品0/1版互验。

**边界与生成要求**：代表题用于知识映射；先讲最小问题，再完成本章核心实现。对比与拓展题不强制变成独立完整题解。

---

### N103｜最长递增子序列与耐心排序

**文件**：`notebooks/13_dynamic_programming/103_lis_and_ordered_sequences.ipynb`

**层级 / 类型**：L3 / core；**先修**：N042, N098, N037。

**教学目标**：从平方DP推导最小尾值压缩并恢复一条解。

**知识点**：严格/非严格；tails不等于答案序列；lower/upper bound；前驱恢复。

**代表 LeetCode 题**：
- 300. Longest Increasing Subsequence — 典型应用；生成前核验题面。
- 354. Russian Doll Envelopes — 典型应用；生成前核验题面。
- 673. Number of Longest Increasing Subsequence — 拓展/替代算法，不声称必需或最优；生成前核验题面。

**必须实现的代码**：
- `lis_quadratic(nums)`。
- `lis_length(nums)`。
- `reconstruct_lis(nums)`。
- `max_envelopes(envelopes)`。

**可视化**：tails数组替换与前驱链。

**练习**：
- 证明tails按长度保持最小结尾。
- 处理信封同宽时排序方向。

**单元测试规格**：
- [10,9,2,5,3,7,101,18]长度4。
- 全相同严格长度1。
- 恢复序列递增且为原序列子序列。
- 与平方版对拍。

**边界与生成要求**：代表题用于知识映射；先讲最小问题，再完成本章核心实现。对比与拓展题不强制变成独立完整题解。

---

### N104｜序列匹配、编辑距离与子序列计数

**文件**：`notebooks/13_dynamic_programming/104_sequence_alignment_dp.ipynb`

**层级 / 类型**：L3 / core；**先修**：N098, N022。

**教学目标**：按两个前缀定义状态并区分最优值和方案数。

**知识点**：LCS；编辑增删改；不同子序列；空串边界；路径恢复。

**代表 LeetCode 题**：
- 1143. Longest Common Subsequence — 典型应用；生成前核验题面。
- 72. Edit Distance — 典型应用；生成前核验题面。
- 115. Distinct Subsequences — 典型应用；生成前核验题面。

**必须实现的代码**：
- `lcs(a, b)`。
- `edit_distance(a, b)`。
- `num_distinct(s, t)`。

**可视化**：二维状态表与匹配/删除/替换箭头。

**练习**：
- 恢复一条LCS。
- 解释不同子序列对相同字符仍可能有多种索引选择。

**单元测试规格**：
- abcde/ace→LCS3。
- horse/ros→距离3。
- rabbbit/rabbit→3。
- 空目标计数1。
- 短字符串穷举对拍。

**边界与生成要求**：代表题用于知识映射；先讲最小问题，再完成本章核心实现。对比与拓展题不强制变成独立完整题解。

---

### N105｜字符串分割、解码与模式匹配

**文件**：`notebooks/13_dynamic_programming/105_string_segmentation_matching_dp.ipynb`

**层级 / 类型**：L3 / core；**先修**：N098, N066, N104。

**教学目标**：把前缀能否完成和模式状态作为DP状态。

**知识点**：词典分割；多位解码；0的合法性；通配符与正则语义差异。

**代表 LeetCode 题**：
- 139. Word Break — 典型应用；生成前核验题面。
- 91. Decode Ways — 典型应用；生成前核验题面。
- 44. Wildcard Matching — 典型应用；生成前核验题面。
- 10. Regular Expression Matching — 典型应用；生成前核验题面。

**必须实现的代码**：
- `word_break(s, words)`。
- `num_decodings(s)`。
- `wildcard_match(s, p)`。
- `regex_match(s, p)`。

**可视化**：前缀切分边与模式匹配二维表。

**练习**：
- 比较*在通配符和简化正则中的不同含义。
- 给每类匹配写独立契约。

**单元测试规格**：
- leetcode可分。
- 06解码0。
- 226解码3。
- aab与c*a*b正则匹配。
- 空串模式边界逐项测。

**边界与生成要求**：代表题用于知识映射；先讲最小问题，再完成本章核心实现。对比与拓展题不强制变成独立完整题解。

---

### N106｜状态机DP与股票交易

**文件**：`notebooks/13_dynamic_programming/106_finite_state_dp_stocks.ipynb`

**层级 / 类型**：L3 / core；**先修**：N098, N099, N023。

**教学目标**：用持有状态和交易次数表达合法历史。

**知识点**：买卖状态；费用；冷冻期；K次交易；不可达初始化；同日更新顺序。

**代表 LeetCode 题**：
- 121. Best Time to Buy and Sell Stock — 典型应用；生成前核验题面。
- 122. Best Time to Buy and Sell Stock II — 典型应用；生成前核验题面。
- 188. Best Time to Buy and Sell Stock IV — 典型应用；生成前核验题面。
- 309. Best Time to Buy and Sell Stock with Cooldown — 典型应用；生成前核验题面。
- 714. Best Time to Buy and Sell Stock with Transaction Fee — 典型应用；生成前核验题面。

**必须实现的代码**：
- `max_profit_once(prices)`。
- `max_profit_k(prices, k)`。
- `max_profit_cooldown(prices)`。
- `max_profit_fee(prices, fee)`。

**可视化**：持有/卖出/冷冻状态图与逐日收益表。

**练习**：
- 从统一状态机派生无限次交易。
- 解释初始持有不能初始化为0。

**单元测试规格**：
- [7,1,5,3,6,4]单次5。
- [1,2,3,0,2]冷冻期3。
- 单调下降。
- 小天数枚举合法交易对拍。

**边界与生成要求**：代表题用于知识映射；先讲最小问题，再完成本章核心实现。对比与拓展题不强制变成独立完整题解。

---

### N107｜区间DP与最后一步决策

**文件**：`notebooks/13_dynamic_programming/107_interval_dp.ipynb`

**层级 / 类型**：L4 / core；**先修**：N098, N031, N063。

**教学目标**：通过选择区间内最后发生的操作分离子问题。

**知识点**：dp[l][r]；区间长度顺序；边界哨兵；最后操作；合并可行性。

**代表 LeetCode 题**：
- 312. Burst Balloons — 典型应用；生成前核验题面。
- [1000. Minimum Cost to Merge Stones](https://leetcode.com/problems/minimum-cost-to-merge-stones/) — 典型应用；官方页面已核对题号与标题。
- 1039. Minimum Score Triangulation of Polygon — 典型应用；生成前核验题面。

**必须实现的代码**：
- `burst_balloons(nums)`。
- `merge_stones(stones, k)`。
- `min_score_triangulation(values)`。

**可视化**：最后戳破/最后切分对应的区间树。

**练习**：
- 解释先选第一个气球难以分离子问题。
- 推导合并到一堆的余数条件。

**单元测试规格**：
- [3,1,5,8]戳气球167。
- [3,2,4,1],k=2成本20、k=3不可行。
- 短区间。
- 小规模全操作序列对拍。

**边界与生成要求**：代表题用于知识映射；先讲最小问题，再完成本章核心实现。对比与拓展题不强制变成独立完整题解。

---

### N108｜划分DP与最后一段

**文件**：`notebooks/13_dynamic_programming/108_partition_dp.ipynb`

**层级 / 类型**：L4 / core；**先修**：N098, N031, N107。

**教学目标**：用最后一段边界枚举前缀最优并计算段成本。

**知识点**：dp[i]/dp[k][i]；段成本；前缀优化；最少/恰好K段；无效状态。

**代表 LeetCode 题**：
- 1043. Partition Array for Maximum Sum — 典型应用；生成前核验题面。
- 1278. Palindrome Partitioning III — 典型应用；生成前核验题面。
- 1335. Minimum Difficulty of a Job Schedule — 典型应用；生成前核验题面。

**必须实现的代码**：
- `max_sum_after_partitioning(arr, k)`。
- `palindrome_partition_k(s, k)`。
- `min_difficulty(jobs, d)`。

**可视化**：前缀终点与最后一段候选跨度。

**练习**：
- 返回划分边界。
- 比较恰好d段与至多d段。

**单元测试规格**：
- [1,15,7,9,2,5,10],k=3→84。
- 工作数少于天数→-1。
- 段数1与n。
- 短输入枚举切分对拍。

**边界与生成要求**：代表题用于知识映射；先讲最小问题，再完成本章核心实现。对比与拓展题不强制变成独立完整题解。

---

### N109｜树形DP与局部约束

**文件**：`notebooks/13_dynamic_programming/109_tree_dp_selection_matching.ipynb`

**层级 / 类型**：L4 / core；**先修**：N071, N098, N101。

**教学目标**：用节点选与不选状态表达相邻冲突。

**知识点**：后序；子树独立；状态合并；树背包/匹配扩展；选取方案恢复。

**代表 LeetCode 题**：
- 337. House Robber III — 典型应用；生成前核验题面。
- 968. Binary Tree Cameras — 典型应用；生成前核验题面。

**必须实现的代码**：
- `rob_tree(root)`。
- `min_camera_cover(root)`。
- `tree_independent_set(adj, weights)`。

**可视化**：每节点选/不选收益或覆盖状态。

**练习**：
- 把二叉树推广到一般树。
- 构造只用一个最优值丢失父子兼容信息的例子。

**单元测试规格**：
- [3,2,3,null,3,null,1]收益7。
- 单节点摄像头1。
- 全零权。
- 小树枚举选点或摄像头集合对拍。

**边界与生成要求**：代表题用于知识映射；先讲最小问题，再完成本章核心实现。对比与拓展题不强制变成独立完整题解。

---

### N110｜换根DP与全节点答案

**文件**：`notebooks/13_dynamic_programming/110_rerooting_dp.ipynb`

**层级 / 类型**：L4 / core；**先修**：N109, N075, N081。

**教学目标**：从一个根的统计量推导相邻根的答案。

**知识点**：子树大小；两遍DFS；内外贡献；重根转移；距离和。

**代表 LeetCode 题**：
- 834. Sum of Distances in Tree — 典型应用；生成前核验题面。
- 2581. Count Number of Possible Root Nodes — 拓展/替代算法，不声称必需或最优；生成前核验题面。

**必须实现的代码**：
- `sum_of_distances_in_tree(n, edges)`。
- `root_count(edges, guesses, k)`。

**可视化**：根沿边移动时两侧距离变化。

**练习**：
- 推导ans[v]=ans[u]+n-2*size[v]。
- 构造链和星形的闭式答案。

**单元测试规格**：
- 三节点链距离和[3,2,3]。
- 单点0。
- 与每点BFS求距离和对拍。
- 猜测方向翻转只影响当前边。

**边界与生成要求**：代表题用于知识映射；先讲最小问题，再完成本章核心实现。对比与拓展题不强制变成独立完整题解。

---

### N111｜DAG动态规划与隐式偏序

**文件**：`notebooks/13_dynamic_programming/111_dag_dp_and_longest_paths.ipynb`

**层级 / 类型**：L4 / core；**先修**：N082, N098, N080。

**教学目标**：按拓扑顺序合并状态并避免循环依赖。

**知识点**：有向无环；最长路；路径计数；网格递增；记忆化DFS。

**代表 LeetCode 题**：
- 329. Longest Increasing Path in a Matrix — 典型应用；生成前核验题面。
- 1857. Largest Color Value in a Directed Graph — 典型应用；生成前核验题面。
- 2050. Parallel Courses III — 典型应用；生成前核验题面。

**必须实现的代码**：
- `longest_increasing_path(matrix)`。
- `largest_path_value(colors, edges)`。
- `minimum_course_time(n, relations, time)`。

**可视化**：偏序方向、拓扑层与多维状态传播。

**练习**：
- 解释矩阵递增约束为什么排除环。
- 带环课程输入明确拒绝。

**单元测试规格**：
- [[9,9,4],[6,6,8],[2,1,1]]最长4。
- 同值不连递增边。
- 颜色图有环返回-1。
- 小DAG枚举路径对拍。

**边界与生成要求**：代表题用于知识映射；先讲最小问题，再完成本章核心实现。对比与拓展题不强制变成独立完整题解。

---

### N112｜状态压缩DP与集合状态

**文件**：`notebooks/13_dynamic_programming/112_bitmask_dp.ipynb`

**层级 / 类型**：L4 / core；**先修**：N098, N124, N101, N064。

**教学目标**：把已选择对象集合编码成充分状态。

**知识点**：mask；最后位置；子集转移；访问状态图；状态数与转移数。

**代表 LeetCode 题**：
- 464. Can I Win — 典型应用；生成前核验题面。
- 691. Stickers to Spell Word — 典型应用；生成前核验题面。
- 1125. Smallest Sufficient Team — 典型应用；生成前核验题面。

**必须实现的代码**：
- `smallest_sufficient_team(skills, people)`。
- `min_stickers(stickers, target)`。
- `hamiltonian_path_dp(cost)`。

**可视化**：子集格点与mask二进制状态表。

**练习**：
- 为最小团队恢复人员索引。
- 区分O(2^n)状态和可能更多的转移。

**单元测试规格**：
- 重复技能人不造成错误。
- 无法覆盖的教学输入明确无解。
- 小技能集穷举人员集合对拍。
- 返回团队确实覆盖全部技能。

**边界与生成要求**：代表题用于知识映射；先讲最小问题，再完成本章核心实现。对比与拓展题不强制变成独立完整题解。

---

### N113｜数位DP、上界与前导零

**文件**：`notebooks/13_dynamic_programming/113_digit_dp.ipynb`

**层级 / 类型**：L4 / advanced_extension；**先修**：N098, N124, N023。

**教学目标**：用位位置与已用信息统计大整数区间。

**知识点**：tight；started；digit mask；缓存条件；区间差分；0是否计入。

**代表 LeetCode 题**：
- [2376. Count Special Integers](https://leetcode.com/problems/count-special-integers/) — 典型应用；官方页面已核对题号与标题。
- 233. Number of Digit One — 典型应用；生成前核验题面。
- 902. Numbers At Most N Given Digit Set — 典型应用；生成前核验题面。

**必须实现的代码**：
- `count_special_numbers(n)`。
- `count_digit_one(n)`。
- `count_from_digit_set(digits, n)`。

**可视化**：上界数字树与tight分支状态。

**练习**：
- 比较定长带前导零和不定长整数计数。
- 推导区间[L,R]差分。

**单元测试规格**：
- n=20互异数字数19。
- n=135→110。
- 数1在0..13共6次。
- 小n逐数枚举。
- 边界0单独定义。

**边界与生成要求**：正整数题排除0；started状态与最终计数规则必须一致，不能让前导零占用数字0。

---

### N114｜概率与期望DP

**文件**：`notebooks/13_dynamic_programming/114_probability_expectation_dp.ipynb`

**层级 / 类型**：L4 / advanced_extension；**先修**：N098, N081, N131。

**教学目标**：由全概率公式和条件期望建立转移。

**知识点**：概率质量；期望线性性；吸收状态；边界流失；数值容差；自循环方程。

**代表 LeetCode 题**：
- 688. Knight Probability in Chessboard — 典型应用；生成前核验题面。
- 837. New 21 Game — 典型应用；生成前核验题面。
- 808. Soup Servings — 拓展/替代算法，不声称必需或最优；生成前核验题面。

**必须实现的代码**：
- `knight_probability(n, k, row, col)`。
- `new21_game(n, k, max_pts)`。
- `expected_steps_small_chain(transitions)`。

**可视化**：概率质量在棋盘/状态图中的流动。

**练习**：
- 区分概率之和和期望之和。
- 写出含自循环的期望方程。

**单元测试规格**：
- n=3,k=2,起点(0,0)概率0.0625。
- k=0概率1。
- 概率在[0,1]。
- 小模型枚举路径或精确分数对照。

**边界与生成要求**：概率状态初始化、总质量和期望状态不同；含自循环时不能未经处理直接当DAG递推。

---

### N115｜博弈DP与得分差

**文件**：`notebooks/13_dynamic_programming/115_game_dp_minimax.ipynb`

**层级 / 类型**：L4 / advanced_extension；**先修**：N098, N107, N062。

**教学目标**：在双方最优前提下使用当前玩家视角。

**知识点**：minimax；零和；先后手；得分差；缓存；与概率决策区别。

**代表 LeetCode 题**：
- 486. Predict the Winner — 典型应用；生成前核验题面。
- 877. Stone Game — 典型应用；生成前核验题面。
- 1140. Stone Game II — 典型应用；生成前核验题面。
- 1406. Stone Game III — 典型应用；生成前核验题面。

**必须实现的代码**：
- `predict_the_winner(nums)`。
- `stone_game_ii(piles)`。
- `stone_game_iii(stone_value)`。

**可视化**：对手回合交替的博弈树与压缩状态。

**练习**：
- 推导difference=current_gain-next_difference。
- 解释一类题的结论不能替代通用DP。

**单元测试规格**：
- [1,5,2]先手不能赢。
- [1,5,233,7]能赢。
- 平局约定。
- 小长度完整minimax对拍。

**边界与生成要求**：代表题用于知识映射；先讲最小问题，再完成本章核心实现。对比与拓展题不强制变成独立完整题解。

---

### N116｜轮廓DP与窄网格状态

**文件**：`notebooks/13_dynamic_programming/116_profile_dp_grid_states.ipynb`

**层级 / 类型**：L4 / advanced_extension；**先修**：N112, N087, N128。

**教学目标**：仅保存已处理区域与未来相交的边界信息。

**知识点**：行掩码；合法状态；相邻行兼容；多进制状态；复杂度按宽度增长。

**代表 LeetCode 题**：
- [1349. Maximum Students Taking Exam](https://leetcode.com/problems/maximum-students-taking-exam/) — 典型应用；官方页面已核对题号与标题。
- 1931. Painting a Grid With Three Different Colors — 典型应用；生成前核验题面。
- [1411. Number of Ways to Paint N × 3 Grid](https://leetcode.com/problems/number-of-ways-to-paint-n-3-grid/) — 典型应用；官方页面已核对题号与标题。

**必须实现的代码**：
- `max_students_profile(seats)`。
- `color_the_grid(m, n)`。
- `num_of_ways_n3(n)`。

**可视化**：相邻两行状态和兼容关系图。

**练习**：
- 交换长宽以减少状态数但核对规则对称性。
- 与二分匹配解考场题对照。

**单元测试规格**：
- 一行考场按冲突规则。
- 1×1染色3。
- n×3在n=1为12。
- 小网格全枚举。
- 破损座位从状态中排除。

**边界与生成要求**：1411的三色演示可只用标签，不必依赖特定配色；题面染色约束以官方说明为准。

---

### N117｜DP空间与转移优化

**文件**：`notebooks/13_dynamic_programming/117_dp_optimization_basics.ipynb`

**层级 / 类型**：L4 / core；**先修**：N098, N056, N031, N099。

**教学目标**：先证明依赖与候选支配再删除状态或转移。

**知识点**：滚动数组；前缀和；单调队列；窗口DP；保留恢复路径的代价。

**代表 LeetCode 题**：
- 1425. Constrained Subsequence Sum — 典型应用；生成前核验题面。
- 1696. Jump Game VI — 典型应用；生成前核验题面。
- 629. K Inverse Pairs Array — 典型应用；生成前核验题面。

**必须实现的代码**：
- `constrained_subset_sum(nums, k)`。
- `max_result(nums, k)`。
- `k_inverse_pairs(n, k)`。

**可视化**：朴素转移窗口与单调候选压缩。

**练习**：
- 分别优化时间和空间并报告改变。
- 解释滚动数组后如何恢复路径。

**单元测试规格**：
- [1,-1,-2,4,-7,3],k=2最大得分7。
- 全负数组。
- k=1。
- 与未优化DP对拍。
- 逆序对数超上界为0。

**边界与生成要求**：代表题用于知识映射；先讲最小问题，再完成本章核心实现。对比与拓展题不强制变成独立完整题解。

---

## 14_string_algorithms｜字符串算法

### N118｜KMP与Z函数

**文件**：`notebooks/14_string_algorithms/118_kmp_and_z_function.ipynb`

**层级 / 类型**：L3 / core；**先修**：N006, N013, N077。

**教学目标**：利用已匹配前缀避免重复比较。

**知识点**：前缀函数；失配链接；Z区间；重叠匹配；总比较次数。

**代表 LeetCode 题**：
- 28. Find the Index of the First Occurrence in a String — 典型应用；生成前核验题面。
- 459. Repeated Substring Pattern — 典型应用；生成前核验题面。
- [2223. Sum of Scores of Built Strings](https://leetcode.com/problems/sum-of-scores-of-built-strings/) — 典型应用；官方页面已核对题号与标题。

**必须实现的代码**：
- `prefix_function(s)`。
- `kmp_find(text, pattern)`。
- `z_function(s)`。
- `sum_scores(s)`。

**可视化**：失败回跳与Z盒复用区间。

**练习**：
- 输出所有重叠匹配位置。
- 构造多次回跳的周期字符串。

**单元测试规格**：
- ababab中abab匹配起点0和2。
- 无匹配返回-1。
- babab总评分9。
- 与朴素匹配对拍。
- 空模式约定明确。

**边界与生成要求**：代表题用于知识映射；先讲最小问题，再完成本章核心实现。对比与拓展题不强制变成独立完整题解。

---

### N119｜滚动哈希与子串比较

**文件**：`notebooks/14_string_algorithms/119_rolling_hash_substrings.ipynb`

**层级 / 类型**：L4 / advanced_extension；**先修**：N031, N042, N128。

**教学目标**：理解哈希相等不是字符串相等的严格证明。

**知识点**：多项式前缀哈希；幂表；模数；碰撞；双哈希；精确复核代价。

**代表 LeetCode 题**：
- 1044. Longest Duplicate Substring — 典型应用；生成前核验题面。
- 187. Repeated DNA Sequences — 典型应用；生成前核验题面。
- 1316. Distinct Echo Substrings — 拓展/替代算法，不声称必需或最优；生成前核验题面。

**必须实现的代码**：
- `RollingHash`。
- `find_duplicate_length(s, length)`。
- `longest_duplicate_substring(s)`。

**可视化**：子串归一化哈希与碰撞示例。

**练习**：
- 用小模数主动制造碰撞。
- 比较双哈希概率控制和逐字复核。

**单元测试规格**：
- banana最长重复长度3。
- 所有字符相同。
- 故意碰撞不误判精确版。
- 小串与子串集合参照对拍。

**边界与生成要求**：双哈希仍不是无碰撞证明；逐字复核会改变最坏复杂度。必须分别写出概率与确定性保证。

---

### N120｜回文DP、中心扩展与Manacher

**文件**：`notebooks/14_string_algorithms/120_palindrome_algorithms_manacher.ipynb`

**层级 / 类型**：L4 / advanced_extension；**先修**：N098, N118。

**教学目标**：从对称复用推导线性回文半径算法。

**知识点**：奇偶中心；回文区间DP；镜像中心；右边界；分隔符风险。

**代表 LeetCode 题**：
- 5. Longest Palindromic Substring — 典型应用；生成前核验题面。
- 647. Palindromic Substrings — 典型应用；生成前核验题面。
- 214. Shortest Palindrome — 拓展/替代算法，不声称必需或最优；生成前核验题面。

**必须实现的代码**：
- `longest_palindrome_center(s)`。
- `palindrome_dp(s)`。
- `manacher_radii(s)`。
- `count_palindromic_substrings(s)`。

**可视化**：奇偶半径、镜像中心和已知最右边界。

**练习**：
- 从半径统计全部回文数。
- 说明分隔符可能出现在输入时如何处理。

**单元测试规格**：
- babad返回bab或aba都有效。
- cbbd→bb。
- aaa回文数6。
- 空串。
- 三实现长度与计数对拍。

**边界与生成要求**：代表题用于知识映射；先讲最小问题，再完成本章核心实现。对比与拓展题不强制变成独立完整题解。

---

### N121｜Aho–Corasick多模式匹配

**文件**：`notebooks/14_string_algorithms/121_aho_corasick_automaton.ipynb`

**层级 / 类型**：L5 / advanced_extension；**先修**：N077, N078, N081, N118。

**教学目标**：通过失败链接共享多个模式的扫描工作。

**知识点**：Trie；BFS建fail；输出传播；重叠匹配；流式状态；输出量复杂度。

**代表 LeetCode 题**：
- [1032. Stream of Characters](https://leetcode.com/problems/stream-of-characters/) — 拓展/替代算法，不声称必需或最优；官方页面已核对题号与标题。

**必须实现的代码**：
- `AhoCorasick.build(patterns)`。
- `AhoCorasick.scan(text)`。
- `StreamChecker.query(letter)`。

**可视化**：Trie树边、fail边和流式状态转移。

**练习**：
- 与倒序Trie解1032对照。
- 说明总复杂度必须计入报告匹配数。

**单元测试规格**：
- 模式he/she/hers/his在ushers中的重叠匹配。
- 模式互为后缀。
- 重复模式ID策略。
- 与逐模式朴素匹配对拍。

**边界与生成要求**：复杂度必须计入输出匹配总量；1032可用倒序Trie，本章展示AC作为流式多模式推广。

---

### N122｜后缀数组与LCP

**文件**：`notebooks/14_string_algorithms/122_suffix_array_lcp.ipynb`

**层级 / 类型**：L5 / advanced_extension；**先修**：N118, N037, N040。

**教学目标**：用后缀排序把重复子串问题变成相邻比较。

**知识点**：倍增秩；后缀数组；Kasai；LCP；不同子串计数；排序成本。

**代表 LeetCode 题**：
- 1044. Longest Duplicate Substring — 拓展/替代算法，不声称必需或最优；生成前核验题面。

**必须实现的代码**：
- `suffix_array(s)`。
- `kasai_lcp(s, sa)`。
- `count_distinct_substrings_sa(s)`。

**可视化**：banana后缀排序、秩表与LCP柱形图。

**练习**：
- 从LCP求最长重复子串。
- 区分用比较排序的O(nlog²n)实现与计数排序版复杂度。

**单元测试规格**：
- banana的SA为[5,3,1,0,4,2]。
- 空/单字符。
- 不同子串数与集合穷举一致。
- SA为0..n-1的排列。

**边界与生成要求**：使用Python比较排序的倍增版不能直接声称O(n log n)；应写明每轮排序的成本。

---

### N123｜后缀自动机与子串状态

**文件**：`notebooks/14_string_algorithms/123_suffix_automaton.ipynb`

**层级 / 类型**：L5 / advanced_extension；**先修**：N121, N122, N104。

**教学目标**：用endpos等价类解释状态、克隆与后缀链接。

**知识点**：len/link；clone；子串识别；不同子串计数；最长公共连续段。

**代表 LeetCode 题**：
- [718. Maximum Length of Repeated Subarray](https://leetcode.com/problems/maximum-length-of-repeated-subarray/) — 拓展/替代算法，不声称必需或最优；官方页面已核对题号与标题。
- 1044. Longest Duplicate Substring — 拓展/替代算法，不声称必需或最优；生成前核验题面。

**必须实现的代码**：
- `SuffixAutomaton.extend(symbol)`。
- `count_distinct_substrings_sam(s)`。
- `longest_common_subarray_sam(a, b)`。

**可视化**：新增字符时普通状态与克隆状态的变化。

**练习**：
- 将字符边推广为整数边。
- 比较SAM与平方DP解718，注明并非该题必需算法。

**单元测试规格**：
- [1,2,3,2,1]/[3,2,1,4,7]→3。
- 重复符号。
- 不同子串数与后缀数组和穷举一致。
- link指向更短最大长度状态。

**边界与生成要求**：后缀自动机是拓展工具，718在原约束下可用更简单DP；整数符号的Trie边使用字典。

---

## 15_math_bits_geometry｜数学、位运算与几何

### N124｜位运算与整数表示

**文件**：`notebooks/15_math_bits_geometry/124_bits_integer_representation.ipynb`

**层级 / 类型**：L1 / core；**先修**：N002, N005, N013。

**教学目标**：在明确位宽下操作二进制并区分Python整数语义。

**知识点**：与或异或非；移位；补码；lowbit；清最低1；popcount；掩码。

**代表 LeetCode 题**：
- 191. Number of 1 Bits — 典型应用；生成前核验题面。
- 190. Reverse Bits — 典型应用；生成前核验题面。
- 338. Counting Bits — 典型应用；生成前核验题面。
- 67. Add Binary — 典型应用；生成前核验题面。

**必须实现的代码**：
- `popcount(n)`。
- `reverse_bits32(n)`。
- `add_binary(a, b)`。

**可视化**：固定32位比特格与逐步位操作。

**练习**：
- 说明Python的~x不是有限位按位翻转结果。
- 解释大整数位操作不总是常数成本。

**单元测试规格**：
- 0置位数0。
- 7置位数3。
- 32位反转两次恢复。
- 11+1二进制为100。
- 掩码限制输出位宽。

**边界与生成要求**：Python整数任意精度，不能把固定字长RAM模型下的O(1)位运算无条件推广到任意位长。

---

### N125｜位掩码、异或与二进制Trie

**文件**：`notebooks/15_math_bits_geometry/125_bitmasks_xor_trie.ipynb`

**层级 / 类型**：L3 / core；**先修**：N124, N077, N015。

**教学目标**：把集合操作和按位最优选择转换成整数操作。

**知识点**：子集/子掩码；XOR消去；位分治；二进制Trie；线性基扩展。

**代表 LeetCode 题**：
- 136. Single Number — 典型应用；生成前核验题面。
- 260. Single Number III — 典型应用；生成前核验题面。
- 421. Maximum XOR of Two Numbers in an Array — 典型应用；生成前核验题面。

**必须实现的代码**：
- `enumerate_submasks(mask)`。
- `single_number(nums)`。
- `BinaryTrie`。
- `find_maximum_xor(nums)`。

**可视化**：子掩码遍历与Trie逐位选相反分支。

**练习**：
- 解释遍历所有mask及其submask的总次数。
- 扩展可回滚计数的二进制Trie。

**单元测试规格**：
- [2,2,1]→1。
- [3,10,5,25,2,8]最大异或28。
- 子掩码均为原mask子集且不重复。
- 与两重循环对拍。

**边界与生成要求**：代表题用于知识映射；先讲最小问题，再完成本章核心实现。对比与拓展题不强制变成独立完整题解。

---

### N126｜欧几里得算法与整除结构

**文件**：`notebooks/15_math_bits_geometry/126_gcd_euclid_number_theory.ipynb`

**层级 / 类型**：L1 / core；**先修**：N002, N013, N063。

**教学目标**：从余数不改变公因子推导gcd及应用。

**知识点**：gcd/lcm；扩展欧几里得；丢番图方程；符号与零；约数。

**代表 LeetCode 题**：
- 1979. Find Greatest Common Divisor of Array — 典型应用；生成前核验题面。
- 1071. Greatest Common Divisor of Strings — 典型应用；生成前核验题面。
- 1492. The kth Factor of n — 典型应用；生成前核验题面。

**必须实现的代码**：
- `gcd_euclid(a, b)`。
- `extended_gcd(a, b)`。
- `lcm(a, b)`。
- `gcd_of_strings(a, b)`。

**可视化**：欧几里得余数序列与线性组合系数。

**练习**：
- 求ax+by=gcd(a,b)一组解。
- 解释字符串gcd还需要拼接可交换条件。

**单元测试规格**：
- gcd(54,24)=6。
- gcd(0,0)按契约为0。
- 验证ax+by=g。
- ABCABC/ABC→ABC。
- 与math.gcd对拍。

**边界与生成要求**：代表题用于知识映射；先讲最小问题，再完成本章核心实现。对比与拓展题不强制变成独立完整题解。

---

### N127｜质数筛、最小质因子与分解

**文件**：`notebooks/15_math_bits_geometry/127_primes_sieves_factorization.ipynb`

**层级 / 类型**：L1 / core；**先修**：N126, N011。

**教学目标**：按查询类型选择试除、筛或预处理。

**知识点**：试除到平方根；Eratosthenes；线性筛导览；SPF；因子分解；质因数指数。

**代表 LeetCode 题**：
- 204. Count Primes — 典型应用；生成前核验题面。
- 2523. Closest Prime Numbers in Range — 典型应用；生成前核验题面。
- 2507. Smallest Value After Replacing With Sum of Prime Factors — 典型应用；生成前核验题面。

**必须实现的代码**：
- `sieve(n)`。
- `smallest_prime_factors(n)`。
- `factorize(x, spf)`。

**可视化**：筛中每个质数首次标记的倍数。

**练习**：
- 解释为什么从p²开始筛。
- 批量分解与逐次试除比较。

**单元测试规格**：
- 小于10质数4个。
- n≤2边界。
- 分解因子乘积还原原数。
- 每个因子经试除确认为质数。

**边界与生成要求**：代表题用于知识映射；先讲最小问题，再完成本章核心实现。对比与拓展题不强制变成独立完整题解。

---

### N128｜模运算、快速幂与逆元

**文件**：`notebooks/15_math_bits_geometry/128_modular_arithmetic_fast_power.ipynb`

**层级 / 类型**：L2 / core；**先修**：N126, N124, N063。

**教学目标**：在合法代数条件下化简大数计算。

**知识点**：模同余；快速幂；互素逆元；Fermat前提；CRT扩展；复合模数。

**代表 LeetCode 题**：
- 50. Pow(x, n) — 对照或复用已有题；生成前核验题面。
- 372. Super Pow — 典型应用；生成前核验题面。
- 1922. Count Good Numbers — 典型应用；生成前核验题面。

**必须实现的代码**：
- `mod_pow(a, n, mod)`。
- `mod_inverse(a, mod)`。
- `super_pow(a, digits)`。

**可视化**：指数二进制展开与累乘状态。

**练习**：
- 比较扩展欧几里得求逆和素数模快速幂求逆。
- 构造不可逆元素。

**单元测试规格**：
- mod_pow与pow(a,n,m)一致。
- gcd(a,m)≠1明确拒绝求逆。
- 3模11逆元4。
- 指数0和模1。

**边界与生成要求**：Fermat逆元公式要求合适的素数模与非零元素；复合模数使用互素条件或扩展欧几里得。

---

### N129｜组合计数、容斥与Catalan

**文件**：`notebooks/15_math_bits_geometry/129_combinatorics_counting.ipynb`

**层级 / 类型**：L3 / core；**先修**：N128, N064, N098。

**教学目标**：先确定计数对象和是否有序再写公式。

**知识点**：排列/组合；Pascal；乘加原理；容斥；Catalan；重复对象；模组合。

**代表 LeetCode 题**：
- 118. Pascal's Triangle — 典型应用；生成前核验题面。
- 96. Unique Binary Search Trees — 典型应用；生成前核验题面。
- 62. Unique Paths — 对照或复用已有题；生成前核验题面。
- 920. Number of Music Playlists — 拓展/替代算法，不声称必需或最优；生成前核验题面。

**必须实现的代码**：
- `binomial(n, k)`。
- `catalan(n)`。
- `count_onto_small(n, k)`。

**可视化**：组合格点、括号结构与容斥集合图。

**练习**：
- 推导不同BST数量递推。
- 比较抽球有序和无序计数。

**单元测试规格**：
- C(5,2)=10。
- Catalan(3)=5。
- n<k时组合0。
- 小规模枚举互验。
- 不对复合模数盲用阶乘逆元。

**边界与生成要求**：代表题用于知识映射；先讲最小问题，再完成本章核心实现。对比与拓展题不强制变成独立完整题解。

---

### N130｜线性递推与矩阵快速幂

**文件**：`notebooks/15_math_bits_geometry/130_matrix_exponentiation_recurrences.ipynb`

**层级 / 类型**：L4 / advanced_extension；**先修**：N098, N128, N082。

**教学目标**：把固定维状态递推写成线性变换。

**知识点**：状态向量；转移矩阵；矩阵乘法；单位矩阵；模数；维度成本。

**代表 LeetCode 题**：
- 509. Fibonacci Number — 拓展/替代算法，不声称必需或最优；生成前核验题面。
- 1137. N-th Tribonacci Number — 拓展/替代算法，不声称必需或最优；生成前核验题面。
- 1220. Count Vowels Permutation — 典型应用；生成前核验题面。

**必须实现的代码**：
- `matmul_mod(a, b, mod)`。
- `matpow_mod(a, n, mod)`。
- `fib_matrix(n)`。
- `count_vowel_permutation(n)`。

**可视化**：状态转移图与矩阵幂倍增。

**练习**：
- 从三阶递推构造矩阵。
- 说明复杂度含矩阵维度而不只log n。

**单元测试规格**：
- 矩阵0次幂为单位阵。
- F(0)=0、F(10)=55。
- 元音n=1→5。
- 与线性DP对拍。

**边界与生成要求**：代表题用于知识映射；先讲最小问题，再完成本章核心实现。对比与拓展题不强制变成独立完整题解。

---

### N131｜概率基础与随机采样

**文件**：`notebooks/15_math_bits_geometry/131_randomized_sampling_probability.ipynb`

**层级 / 类型**：L3 / core；**先修**：N042, N031, N124。

**教学目标**：用等概率推导而非直方图宣称无偏。

**知识点**：概率空间；条件概率；期望；Fisher–Yates；蓄水池；加权采样；拒绝采样。

**代表 LeetCode 题**：
- 384. Shuffle an Array — 典型应用；生成前核验题面。
- 398. Random Pick Index — 典型应用；生成前核验题面。
- 528. Random Pick with Weight — 典型应用；生成前核验题面。
- 470. Implement Rand10() Using Rand7() — 典型应用；生成前核验题面。

**必须实现的代码**：
- `fisher_yates(a, rng)`。
- `reservoir_sample(stream, k, rng)`。
- `WeightedSampler`。
- `rand10(rand7)`。

**可视化**：概率树、采样桶与频数诊断图。

**练习**：
- 证明单元素蓄水池每项概率1/n。
- 构造错误全范围交换shuffle的偏差。

**单元测试规格**：
- 固定随机源可复现。
- 枚举n=3所有抽签轨迹验证均匀。
- 加权边界精确覆盖。
- 统计分布检查仅作诊断，不设偶然失败硬门槛。

**边界与生成要求**：频数图仅诊断，不能用一次随机频率接近替代无偏性证明；硬断言优先用可控随机源和小域全枚举。

---

### N132｜组合博弈、Nim与SG函数

**文件**：`notebooks/15_math_bits_geometry/132_impartial_games_sprague_grundy.ipynb`

**层级 / 类型**：L4 / advanced_extension；**先修**：N115, N125, N082。

**教学目标**：在无偏正常玩法条件下用状态异或合并游戏。

**知识点**：必胜/必败；mex；SG递推；Nim和；正常/反常玩法边界。

**代表 LeetCode 题**：
- 292. Nim Game — 典型应用；生成前核验题面。
- 1510. Stone Game IV — 典型应用；生成前核验题面。
- 810. Chalkboard XOR Game — 拓展/替代算法，不声称必需或最优；生成前核验题面。

**必须实现的代码**：
- `can_win_nim(n)`。
- `winner_square_game(n)`。
- `grundy(state, moves)`。

**可视化**：游戏DAG上的SG标签和mex集合。

**练习**：
- 用小状态完整搜索验证Nim规律。
- 给出不满足无偏条件不能直接异或的游戏。

**单元测试规格**：
- 4根石子先手败、5根胜。
- 平方取石n=2败。
- 复合小游戏SG异或与minimax对照。
- 无合法步SG为0。

**边界与生成要求**：代表题用于知识映射；先讲最小问题，再完成本章核心实现。对比与拓展题不强制变成独立完整题解。

---

### N133｜计算几何与凸包

**文件**：`notebooks/15_math_bits_geometry/133_computational_geometry.ipynb`

**层级 / 类型**：L4 / advanced_extension；**先修**：N037, N126, N013。

**教学目标**：用向量关系替代不稳定斜率比较。

**知识点**：点积/叉积；方向；共线；线段相交；面积；矩形/圆；凸包；整数精确判定。

**代表 LeetCode 题**：
- 149. Max Points on a Line — 典型应用；生成前核验题面。
- 587. Erect the Fence — 典型应用；生成前核验题面。
- 836. Rectangle Overlap — 典型应用；生成前核验题面。
- 223. Rectangle Area — 典型应用；生成前核验题面。

**必须实现的代码**：
- `cross(o, a, b)`。
- `segments_intersect(a,b,c,d)`。
- `convex_hull(points)`。
- `max_points(points)`。

**可视化**：点集、方向判断与凸包构建过程。

**练习**：
- 保留所有边界共线点。
- 用规范化gcd方向替代浮点斜率。

**单元测试规格**：
- 竖直线与重复点教学扩展。
- 全共线。
- 矩形仅接触不算正面积重叠。
- 凸包包含全部点且边界策略一致。

**边界与生成要求**：587要求保留围栏边界上的点；不要混同只保留凸包极点的输出契约。

---

## 16_advanced_structures｜高级数据结构

### N134｜坐标压缩与秩

**文件**：`notebooks/16_advanced_structures/134_coordinate_compression_order_statistics.ipynb`

**层级 / 类型**：L2 / core；**先修**：N037, N042。

**教学目标**：保持相对次序而不误保留原始距离。

**知识点**：去重排序；值到秩；离线预处理；相等键；下界查询；秩与差值区别。

**代表 LeetCode 题**：
- 1331. Rank Transform of an Array — 典型应用；生成前核验题面。
- 315. Count of Smaller Numbers After Self — 只作动机预告，不要求提前实现；生成前核验题面。

**必须实现的代码**：
- `coordinate_compress(values)`。
- `rank_transform(arr)`。
- `count_smaller_sorted_list(nums)`。

**可视化**：原始数轴到稠密秩轴的映射。

**练习**：
- 构造压缩后距离改变的例子。
- 明确有序列表插入仍然线性。

**单元测试规格**：
- [40,10,20,30]→[4,1,2,3]。
- 相等值同秩。
- 负数与大整数。
- 所有a<b都满足rank(a)<rank(b)。

**边界与生成要求**：代表题用于知识映射；先讲最小问题，再完成本章核心实现。对比与拓展题不强制变成独立完整题解。

---

### N135｜树状数组与前缀聚合

**文件**：`notebooks/16_advanced_structures/135_fenwick_tree.ipynb`

**层级 / 类型**：L3 / core；**先修**：N124, N134, N031。

**教学目标**：利用lowbit分解前缀并实现动态求和。

**知识点**：一基下标；lowbit；点增量；前缀/区间和；双BIT扩展；逆序计数。

**代表 LeetCode 题**：
- 307. Range Sum Query - Mutable — 典型应用；生成前核验题面。
- 315. Count of Smaller Numbers After Self — 典型应用；生成前核验题面。
- 493. Reverse Pairs — 拓展/替代算法，不声称必需或最优；生成前核验题面。

**必须实现的代码**：
- `Fenwick.add(i, delta)`。
- `Fenwick.prefix_sum(end)`。
- `count_smaller(nums)`。

**可视化**：每个树状节点覆盖的二进制长度区间。

**练习**：
- 实现范围加与点查。
- 更新赋值时先计算增量。

**单元测试规格**：
- [1,3,5]区间和9，更新中间为2后8。
- [5,2,6,1]更小数计数[2,1,1,0]。
- 随机操作与列表对拍。

**边界与生成要求**：代表题用于知识映射；先讲最小问题，再完成本章核心实现。对比与拓展题不强制变成独立完整题解。

---

### N136｜线段树与区间聚合

**文件**：`notebooks/16_advanced_structures/136_segment_tree_monoids.ipynb`

**层级 / 类型**：L3 / core；**先修**：N031, N063, N134。

**教学目标**：把结合律与单位元落实为可组合节点。

**知识点**：建树；点更新；半开区间；幺半群；结合不等于交换；非空与空查询。

**代表 LeetCode 题**：
- 307. Range Sum Query - Mutable — 典型应用；生成前核验题面。
- 2286. Booking Concert Tickets in Groups — 拓展/替代算法，不声称必需或最优；生成前核验题面。

**必须实现的代码**：
- `SegmentTree(values, combine, identity)`。
- `SegmentTree.set(i, value)`。
- `SegmentTree.query(left, right)`。

**可视化**：查询区间分解为树上不交子区间。

**练习**：
- 同时支持sum/min/字符串拼接。
- 解释左右累积顺序对非交换操作的重要性。

**单元测试规格**：
- 单点和全区间。
- 空区间返回单位元。
- 拼接顺序不能颠倒。
- 随机更新查询与朴素切片聚合对拍。

**边界与生成要求**：代表题用于知识映射；先讲最小问题，再完成本章核心实现。对比与拓展题不强制变成独立完整题解。

---

### N137｜懒传播、动态节点与更新复合

**文件**：`notebooks/16_advanced_structures/137_lazy_segment_tree_range_updates.ipynb`

**层级 / 类型**：L4 / advanced_extension；**先修**：N136, N034, N124。

**教学目标**：正确组合懒标记并维护区间统计量。

**知识点**：range add/flip；push/pull；标记复合次序；区间长度；动态开点；赋值扩展。

**代表 LeetCode 题**：
- [2569. Handling Sum Queries After Update](https://leetcode.com/problems/handling-sum-queries-after-update/) — 典型应用；官方页面已核对题号与标题。
- 715. Range Module — 拓展/替代算法，不声称必需或最优；生成前核验题面。
- 732. My Calendar III — 拓展/替代算法，不声称必需或最优；生成前核验题面。

**必须实现的代码**：
- `RangeAddSumTree`。
- `FlipCountTree`。
- `handle_sum_queries(nums1, nums2, queries)`。

**可视化**：节点值和懒标记在下推前后的同步变化。

**练习**：
- 加入赋值标记并说明与加法不可交换。
- 比较离线压缩和动态开点。

**单元测试规格**：
- [1,0,1]翻转中位后1的个数3。
- 同区间翻转两次复原。
- 嵌套更新。
- 与朴素数组随机对拍。

**边界与生成要求**：代表题用于知识映射；先讲最小问题，再完成本章核心实现。对比与拓展题不强制变成独立完整题解。

---

### N138｜Sparse Table与静态RMQ

**文件**：`notebooks/16_advanced_structures/138_sparse_table_rmq.ipynb`

**层级 / 类型**：L4 / advanced_extension；**先修**：N136, N056。

**教学目标**：利用幂区间预处理回答静态幂等查询。

**知识点**：稀疏表；log表；min/max/gcd幂等；重叠块；不可动态更新；Disjoint Sparse Table拓展。

**代表 LeetCode 题**：
- 239. Sliding Window Maximum — 拓展/替代算法，不声称必需或最优；生成前核验题面。
- 1438. Longest Continuous Subarray With Absolute Diff Less Than or Equal to Limit — 拓展/替代算法，不声称必需或最优；生成前核验题面。

**必须实现的代码**：
- `SparseTableMin`。
- `SparseTableMax`。
- `static_window_max(nums, k)`。

**可视化**：长度2^j的区间层和查询覆盖块。

**练习**：
- 构造用重叠两块求sum的错误反例。
- 比较RMQ与单调队列解滑窗。

**单元测试规格**：
- [4,2,5,1]全区间最小1。
- 单点。
- 长度非2幂。
- 所有小区间与min切片一致。
- sum版本不得套重叠公式。

**边界与生成要求**：重叠两块常数时间查询依赖幂等性，不能直接用于求和；Disjoint Sparse Table为可选对照。

---

### N139｜有序集合、Treap与跳表原理

**文件**：`notebooks/16_advanced_structures/139_balanced_trees_treaps_skiplists.ipynb`

**层级 / 类型**：L4 / advanced_extension；**先修**：N073, N057, N134, N131。

**教学目标**：明确有序动态操作需求并实现带秩平衡树。

**知识点**：旋转；AVL/红黑约束导览；Treap；重复键计数；rank/kth；跳表层级。

**代表 LeetCode 题**：
- 220. Contains Duplicate III — 典型应用；生成前核验题面。
- 1206. Design Skiplist — 拓展/替代算法，不声称必需或最优；生成前核验题面。

**必须实现的代码**：
- `OrderStatisticTreap`。
- `contains_nearby_almost_duplicate(nums, index_diff, value_diff)`。

**可选拓展实现**：
- `Skiplist.search/add/erase（拓展实现）`。

**可视化**：旋转前后BST次序、随机优先级与跳表层。

**练习**：
- 说明随机平衡是期望界而非每次保证。
- 比较bisect加列表插入的成本。

**单元测试规格**：
- 每次操作BST与堆优先级都成立。
- 重复键删除一次只减一个。
- rank/kth与排序多重集对拍。
- 固定随机源。

**边界与生成要求**：代表题用于知识映射；先讲最小问题，再完成本章核心实现。对比与拓展题不强制变成独立完整题解。

---

### N140｜带权与可回滚并查集

**文件**：`notebooks/16_advanced_structures/140_weighted_rollback_dsu.ipynb`

**层级 / 类型**：L4 / advanced_extension；**先修**：N083, N019, N080。

**教学目标**：在根关系之外维护相对势能并支持撤销。

**知识点**：相对权值；路径压缩更新；回滚栈；按大小；回滚不直接套压缩；离线删边扩展。

**代表 LeetCode 题**：
- 399. Evaluate Division — 典型应用；生成前核验题面。
- 2092. Find All People With Secret — 拓展/替代算法，不声称必需或最优；生成前核验题面。

**必须实现的代码**：
- `WeightedDSU`。
- `RollbackDSU.union/find/snapshot/rollback`。
- `calc_equation(equations, values, queries)`。

**可视化**：父指针上的相对比例与撤销日志栈。

**练习**：
- 把比值改为差值约束。
- 对同时间秘密传播比较BFS与临时合并，注明不同解法。

**单元测试规格**：
- a/b=2,b/c=3推出a/c=6。
- 未知变量→-1。
- 快照回滚后分量恢复。
- 与图路径连乘参照容差比较。

**边界与生成要求**：回滚并查集默认不用路径压缩；否则必须完整回滚压缩修改，不能只回滚union。

---

## 17_advanced_algorithms｜高级算法

### N141｜Euler序、倍增与树上查询

**文件**：`notebooks/17_advanced_algorithms/141_euler_tour_binary_lifting.ipynb`

**层级 / 类型**：L4 / advanced_extension；**先修**：N075, N124, N135, N080。

**教学目标**：把子树查询变成区间并按二进制跳祖先。

**知识点**：tin/tout；子树连续；up[v][j]；LCA；跳跃上界；树链剖分扩展。

**代表 LeetCode 题**：
- 1483. Kth Ancestor of a Tree Node — 典型应用；生成前核验题面。
- 236. Lowest Common Ancestor of a Binary Tree — 对照或复用已有题；生成前核验题面。

**必须实现的代码**：
- `euler_tour(adj, root)`。
- `BinaryLifting.get_kth_ancestor(v, k)`。
- `BinaryLifting.lca(u, v)`。

**可视化**：DFS进入离开时间与2^j跳表。

**练习**：
- 结合Fenwick处理子树更新查询。
- 区分子树区间和任意路径区间。

**单元测试规格**：
- 根的正数祖先为-1。
- k=0返回自身。
- 子树区间元素恰好对应后代。
- LCA与逐父追溯对拍。

**边界与生成要求**：树链剖分只作拓展概念与练习，不作为Euler序/倍增入门的阻塞。

---

### N142｜折半搜索与指数优化

**文件**：`notebooks/17_advanced_algorithms/142_meet_in_the_middle.ipynb`

**层级 / 类型**：L4 / advanced_extension；**先修**：N125, N042, N101。

**教学目标**：把全集枚举拆成两侧并正确合并。

**知识点**：半集子集和；排序/二分；按元素个数分桶；输出规模；时间空间代价。

**代表 LeetCode 题**：
- 1755. Closest Subsequence Sum — 典型应用；生成前核验题面。
- 2035. Partition Array Into Two Arrays to Minimize Sum Difference — 典型应用；生成前核验题面。
- 805. Split Array With Same Average — 拓展/替代算法，不声称必需或最优；生成前核验题面。

**必须实现的代码**：
- `subset_sums(nums)`。
- `min_abs_difference(nums, goal)`。
- `minimum_difference_equal_size(nums)`。

**可视化**：左右子集和表与互补值配对。

**练习**：
- 等大小划分时按选取数量分桶。
- 比较2^n和2^(n/2)的实际状态数。

**单元测试规格**：
- [5,-7,3,5],goal=6差0。
- 全负与重复值。
- 等大小约束严格满足。
- 小n完整子集枚举对拍。

**边界与生成要求**：代表题用于知识映射；先讲最小问题，再完成本章核心实现。对比与拓展题不强制变成独立完整题解。

---

### N143｜离线查询、扫描线与Mo算法

**文件**：`notebooks/17_advanced_algorithms/143_offline_queries_sweep_mo.ipynb`

**层级 / 类型**：L4 / advanced_extension；**先修**：N036, N057, N083, N135。

**教学目标**：在不改变查询语义的前提下重排计算顺序。

**知识点**：查询编号；按阈值排序；离线DSU；Fenwick；Mo增删；平方分块。

**代表 LeetCode 题**：
- 1851. Minimum Interval to Include Each Query — 典型应用；生成前核验题面。
- 1697. Checking Existence of Edge Length Limited Paths — 典型应用；生成前核验题面。
- 315. Count of Smaller Numbers After Self — 对照或复用已有题；生成前核验题面。

**必须实现的代码**：
- `min_interval(intervals, queries)`。
- `distance_limited_paths_exist(n, edges, queries)`。
- `mo_distinct_counts(nums, queries)`。

**可视化**：查询重排与活跃集合；Mo左右端点路线。

**练习**：
- 证明阈值严格小于与小于等于会改变结果。
- 实现自编离线区间去重计数。

**单元测试规格**：
- 输出恢复原查询顺序。
- 重复查询。
- 边权恰等limit不允许。
- Mo结果与每区间set计数对拍。

**边界与生成要求**：代表题用于知识映射；先讲最小问题，再完成本章核心实现。对比与拓展题不强制变成独立完整题解。

---

### N144｜状态图、双向BFS与A*

**文件**：`notebooks/17_advanced_algorithms/144_state_graph_bidirectional_astar.ipynb`

**层级 / 类型**：L4 / advanced_extension；**先修**：N081, N084, N112, N125。

**教学目标**：把操作作为边并为启发式声明正确性条件。

**知识点**：状态编码；最短步数；双向层扩展；admissible/consistent；过期状态；重开节点。

**代表 LeetCode 题**：
- 752. Open the Lock — 典型应用；生成前核验题面。
- 773. Sliding Puzzle — 典型应用；生成前核验题面。
- 847. Shortest Path Visiting All Nodes — 典型应用；生成前核验题面。

**必须实现的代码**：
- `open_lock(deadends, target)`。
- `sliding_puzzle(board)`。
- `shortest_path_all_nodes(graph)`。
- `astar_puzzle(start, goal)`。

**可视化**：状态图前沿和A*的g/h/f值。

**练习**：
- 用位掩码表达已访问顶点。
- 说明不一致启发式需要谨慎重开节点。

**单元测试规格**：
- 起点被禁→-1。
- 目标为起点→0。
- 不可解滑块。
- A*与BFS小状态空间距离一致。
- 不以首次相遇盲停双向搜索。

**边界与生成要求**：代表题用于知识映射；先讲最小问题，再完成本章核心实现。对比与拓展题不强制变成独立完整题解。

---

### N145｜高级DP优化及其成立条件

**文件**：`notebooks/17_advanced_algorithms/145_advanced_dp_optimization_conditions.ipynb`

**层级 / 类型**：L5 / advanced_extension；**先修**：N108, N107, N137, N013。

**教学目标**：先验证决策单调或线性结构再使用优化。

**知识点**：Monge/四边形不等式；分治优化；Knuth范围；凸包优化；Li Chao树；整数比较。

**代表 LeetCode 题**：
- 1478. Allocate Mailboxes — 拓展/替代算法，不声称必需或最优；生成前核验题面。
- [1000. Minimum Cost to Merge Stones](https://leetcode.com/problems/minimum-cost-to-merge-stones/) — 拓展/替代算法，不声称必需或最优；官方页面已核对题号与标题。
- [2463. Minimum Total Distance Traveled](https://leetcode.com/problems/minimum-total-distance-traveled/) — 对照或复用已有题；官方页面已核对题号与标题。

**必须实现的代码**：
- `partition_dp_quadratic(cost, k)`。
- `divide_conquer_dp(cost, k)`。
- `LiChaoMin.add_line/query`。
- `cht_dp_reference(a, b)`。

**可视化**：最优决策下标单调表与直线下包络。

**练习**：
- Knuth只在满足条件的二路合并模型使用，不推广任意K。
- 寻找不满足Monge的反例。

**单元测试规格**：
- 所有优化版与未优化DP小规模对拍。
- 等斜率直线。
- 大整数交点避免浮点误判。
- 条件不成立时明确不能套用。

**边界与生成要求**：分治优化、Knuth和凸包优化各有不同前提。1000仅在适合的二路合并模型里演示Knuth，禁止泛化到任意K。

---

### N146｜FFT、NTT与卷积拓展

**文件**：`notebooks/17_advanced_algorithms/146_fft_ntt_convolution.ipynb`

**层级 / 类型**：L5 / advanced_extension；**先修**：N063, N128, N130。

**教学目标**：理解卷积和系数乘积并区分浮点与模域结果。

**知识点**：多项式卷积；DFT；分治FFT；补零；舍入误差；NTT模数与单位根。

**代表 LeetCode 题**：
- 43. Multiply Strings — 拓展/替代算法，不声称必需或最优；生成前核验题面。

**必须实现的代码**：
- `convolve_naive(a, b)`。
- `fft(values, invert=False)`。
- `convolve_fft(a, b)`。
- `ntt(values, invert, mod, primitive_root)`。

**可视化**：时域系数、频域点乘与逆变换对照。

**练习**：
- 用小整数多项式对拍。
- 说明LC43先掌握竖式乘法，不把FFT当必需解法。

**单元测试规格**：
- [1,2]*[3,4]卷积[3,10,8]。
- 长度补零足够。
- NTT结果按模比较。
- 浮点FFT在明确误差范围下验证，不声称任意大整数精确。

**边界与生成要求**：FFT/NTT为低频精通拓展，先完成朴素卷积。NTT必须核对模数、原根和长度整除条件；浮点FFT必须讨论误差。

---

## 18_design｜数据结构设计

### N147｜LRU与LFU缓存设计

**文件**：`notebooks/18_design/147_lru_lfu_caches.ipynb`

**层级 / 类型**：L3 / core；**先修**：N045, N050, N019, N014。

**教学目标**：使查询、更新和淘汰规则保持一致。

**知识点**：哈希+双向链表；哨兵；最近使用；频次桶；最小频次；并列规则。

**代表 LeetCode 题**：
- 146. LRU Cache — 典型应用；生成前核验题面。
- 460. LFU Cache — 典型应用；生成前核验题面。

**必须实现的代码**：
- `LRUCache.get/put`。
- `LFUCache.get/put`。

**可视化**：LRU链表重排与LFU频率桶迁移。

**练习**：
- 更新已存在键时正确刷新优先级。
- 用慢速时间戳模型作为参照。

**单元测试规格**：
- 容量1及教学容量0。
- 经典LRU操作序列。
- LFU同频按LRU淘汰。
- 每次操作映射与链表双向一致。

**边界与生成要求**：代表题用于知识映射；先讲最小问题，再完成本章核心实现。对比与拓展题不强制变成独立完整题解。

---

### N148｜随机集合与多重集合设计

**文件**：`notebooks/18_design/148_randomized_set_multiset.ipynb`

**层级 / 类型**：L3 / core；**先修**：N017, N019, N131。

**教学目标**：用交换末尾删除维持稠密数组及反向索引。

**知识点**：数组+哈希；平均O(1)；重复值索引集合；均匀随机索引。

**代表 LeetCode 题**：
- 380. Insert Delete GetRandom O(1) — 典型应用；生成前核验题面。
- 381. Insert Delete GetRandom O(1) - Duplicates allowed — 典型应用；生成前核验题面。

**必须实现的代码**：
- `RandomizedSet`。
- `RandomizedCollection`。

**可视化**：删除目标和末元素交换后的索引修复。

**练习**：
- 解释按不同值均匀与按出现次数均匀的差别。
- 随机数源作为参数注入。

**单元测试规格**：
- 删除末元素及重复值。
- 不存在删除返回False。
- 索引集合和数组始终互为映射。
- 随机输出属于当前集合。

**边界与生成要求**：代表题用于知识映射；先讲最小问题，再完成本章核心实现。对比与拓展题不强制变成独立完整题解。

---

### N149｜迭代器、惰性展开与查看下一项

**文件**：`notebooks/18_design/149_iterators_lazy_evaluation.ipynb`

**层级 / 类型**：L3 / core；**先修**：N009, N053, N069, N014。

**教学目标**：维护迭代状态而不提前物化全部输出。

**知识点**：迭代协议；显式栈；缓存一项；hasNext幂等；摊还；嵌套结构。

**代表 LeetCode 题**：
- 173. Binary Search Tree Iterator — 典型应用；生成前核验题面。
- 284. Peeking Iterator — 典型应用；生成前核验题面。
- 341. Flatten Nested List Iterator — 典型应用；生成前核验题面。

**必须实现的代码**：
- `BSTIterator`。
- `PeekingIterator`。
- `NestedIterator`。

**可视化**：下一项缓存与嵌套栈展开过程。

**练习**：
- 反复调用hasNext不消耗元素。
- 说明next最坏与均摊成本不同。

**单元测试规格**：
- 空嵌套列表和多层空项。
- peek两次值相同。
- 迭代输出与完全展开参照一致。
- 耗尽后行为明确。

**边界与生成要求**：代表题用于知识映射；先讲最小问题，再完成本章核心实现。对比与拓展题不强制变成独立完整题解。

---

### N150｜快照、历史查询与可持久化

**文件**：`notebooks/18_design/150_snapshots_persistent_versions.ipynb`

**层级 / 类型**：L3 / core；**先修**：N042, N005。
**拓展先修**：N136。

**教学目标**：在保存历史版本时复用未变部分且不污染旧结果。

**知识点**：按索引版本历史；二分；稀疏记录；结构共享；路径复制；持久化线段树拓展。

**代表 LeetCode 题**：
- 1146. Snapshot Array — 典型应用；生成前核验题面。

**必须实现的代码**：
- `SnapshotArray.set/snap/get`。

**可选拓展实现**：
- `PersistentSegmentTree.update/query（拓展实现）`。

**可视化**：时间轴历史记录与不同版本共享树节点。

**练习**：
- 合并同一snap前对同一索引的多次set。
- 比较完整拷贝与路径复制。

**单元测试规格**：
- 默认值0。
- 同版本多次set取最后值。
- 旧快照不受后续更新影响。
- 随机序列与深拷贝参照一致。

**边界与生成要求**：代表题用于知识映射；先讲最小问题，再完成本章核心实现。对比与拓展题不强制变成独立完整题解。

---

### N151｜多结构组合与时间序服务

**文件**：`notebooks/18_design/151_composite_service_design.ipynb`

**层级 / 类型**：L3 / core；**先修**：N042, N059, N019。

**教学目标**：从API契约倒推存储结构与查询计划。

**知识点**：时间键值；日志追加；K路归并；关注关系；有序时间；一致性约束。

**代表 LeetCode 题**：
- 981. Time Based Key-Value Store — 典型应用；生成前核验题面。
- 355. Design Twitter — 典型应用；生成前核验题面。

**必须实现的代码**：
- `TimeMap.set/get`。
- `Twitter.postTweet/getNewsFeed/follow/unfollow`。

**可视化**：用户关注图、时间日志与候选堆合并。

**练习**：
- 解释全量扫描慢模型的正确性与局限。
- 限定题目要求而不扩展分布式系统。

**单元测试规格**：
- 时间查询早于首记录返回空。
- 没有关注对象。
- 取消关注后消息消失。
- 时间流与慢速全量排序参照一致。

**边界与生成要求**：代表题用于知识映射；先讲最小问题，再完成本章核心实现。对比与拓展题不强制变成独立完整题解。

---

## 19_specialized_tracks｜SQL、Pandas、Shell 与 JavaScript

### N152｜SQL入门、过滤与NULL

**文件**：`notebooks/19_specialized_tracks/152_sql_select_null_sort.ipynb`

**层级 / 类型**：L1 / specialized；**先修**：N007, N010。

**教学目标**：建立表的行列语义并写出正确过滤条件。

**知识点**：SELECT/WHERE/DISTINCT；ORDER BY/LIMIT；NULL三值逻辑；SQL多重集合。

**代表 LeetCode 题**：
- 1757. Recyclable and Low Fat Products — 典型应用；生成前核验题面。
- 595. Big Countries — 典型应用；生成前核验题面。
- 584. Find Customer Referee — 典型应用；生成前核验题面。

**必须实现的代码**：
- `create_sqlite_fixture()`。
- `query_recyclable_products.sql`。
- `query_big_countries.sql`。
- `query_customer_referee.sql`。

**可视化**：过滤前后表格及True/False/Unknown真值表。

**练习**：
- 解释referee_id<>2会漏掉NULL。
- 比较去重与保留重复行。

**单元测试规格**：
- NULL推荐人仍保留。
- 边界人口/面积条件。
- 空表。
- 仅在题目要求排序时强制顺序。

**边界与生成要求**：SQL本地教学使用sqlite3内存数据库。官方题面中的MySQL或其他方言另列，不把本地SQLite通过标成MySQL已测。

**运行时**：`{"python_packages": [], "external_programs": [], "stdlib_modules": ["sqlite3"]}`。

---

### N153｜SQL聚合、连接与计数语义

**文件**：`notebooks/19_specialized_tracks/153_sql_aggregation_joins.ipynb`

**层级 / 类型**：L2 / specialized；**先修**：N152。

**教学目标**：避免连接放大和错误计数。

**知识点**：GROUP BY/HAVING；COUNT(*)/COUNT(col)；INNER/LEFT/SELF JOIN；多对多。

**代表 LeetCode 题**：
- 175. Combine Two Tables — 典型应用；生成前核验题面。
- 181. Employees Earning More Than Their Managers — 典型应用；生成前核验题面。
- 570. Managers with at Least 5 Direct Reports — 典型应用；生成前核验题面。

**必须实现的代码**：
- `query_people_addresses.sql`。
- `query_employees_gt_manager.sql`。
- `query_managers.sql`。

**可视化**：连接键匹配与行数放大图。

**练习**：
- 构造一对多连接使SUM重复的例子。
- 区分WHERE和HAVING。

**单元测试规格**：
- 缺失地址仍保留Person行。
- 员工无经理按题意处理。
- COUNT(col)不计NULL。
- 正好5名下属满足条件。

**边界与生成要求**：代表题用于知识映射；先讲最小问题，再完成本章核心实现。对比与拓展题不强制变成独立完整题解。

**运行时**：`{"python_packages": [], "external_programs": [], "stdlib_modules": ["sqlite3"]}`。

---

### N154｜SQL子查询、CTE与反连接

**文件**：`notebooks/19_specialized_tracks/154_sql_subqueries_cte_antijoins.ipynb`

**层级 / 类型**：L3 / specialized；**先修**：N153。

**教学目标**：把复杂查询拆成可验证中间关系。

**知识点**：EXISTS/NOT EXISTS；相关子查询；CTE；UNION/UNION ALL；去重；关系除法扩展。

**代表 LeetCode 题**：
- 183. Customers Who Never Order — 典型应用；生成前核验题面。
- 184. Department Highest Salary — 典型应用；生成前核验题面。
- 1045. Customers Who Bought All Products — 典型应用；生成前核验题面。

**必须实现的代码**：
- `query_customers_without_orders.sql`。
- `query_department_max.sql`。
- `query_bought_all.sql`。

**可视化**：CTE中间表和反连接消除过程。

**练习**：
- 用NOT EXISTS避免NOT IN与NULL陷阱。
- 比较最高薪并列处理。

**单元测试规格**：
- 订单表含NULL教学样例。
- 最高薪同部门多人全部保留。
- 重复购买不应抬高品类数。
- 空子表语义明确。

**边界与生成要求**：代表题用于知识映射；先讲最小问题，再完成本章核心实现。对比与拓展题不强制变成独立完整题解。

**运行时**：`{"python_packages": [], "external_programs": [], "stdlib_modules": ["sqlite3"]}`。

---

### N155｜SQL窗口、排名与连续段

**文件**：`notebooks/19_specialized_tracks/155_sql_window_rank_sequences.ipynb`

**层级 / 类型**：L3 / specialized；**先修**：N154。

**教学目标**：区分窗口保留行和聚合折叠行。

**知识点**：ROW_NUMBER/RANK/DENSE_RANK；PARTITION；LAG/LEAD；窗口frame；gaps and islands。

**代表 LeetCode 题**：
- 178. Rank Scores — 典型应用；生成前核验题面。
- 180. Consecutive Numbers — 典型应用；生成前核验题面。
- 185. Department Top Three Salaries — 典型应用；生成前核验题面。
- 601. Human Traffic of Stadium — 典型应用；生成前核验题面。

**必须实现的代码**：
- `query_dense_rank.sql`。
- `query_consecutive_numbers.sql`。
- `query_department_top3.sql`。
- `query_stadium.sql`。

**可视化**：分区、排名并列和连续段标记表。

**练习**：
- 区分ROWS与RANGE的重复排序键效果。
- 给连续ID和连续日期分别建模。

**单元测试规格**：
- 并列分数同dense_rank且不跳号。
- 第三高薪全部并列者保留。
- ID断点不能误连。
- 三连及四连。

**边界与生成要求**：代表题用于知识映射；先讲最小问题，再完成本章核心实现。对比与拓展题不强制变成独立完整题解。

**运行时**：`{"python_packages": [], "external_programs": [], "stdlib_modules": ["sqlite3"]}`。

---

### N156｜SQL日期、留存与移动报表

**文件**：`notebooks/19_specialized_tracks/156_sql_dates_retention_reports.ipynb`

**层级 / 类型**：L3 / specialized；**先修**：N155。

**教学目标**：对齐日期粒度后计算分母和滑窗。

**知识点**：日期运算；日期缺口；日聚合；首日/次日；分母；四舍五入；执行计划导览。

**代表 LeetCode 题**：
- 197. Rising Temperature — 典型应用；生成前核验题面。
- 550. Game Play Analysis IV — 典型应用；生成前核验题面。
- 1321. Restaurant Growth — 典型应用；生成前核验题面。
- 262. Trips and Users — 拓展/替代算法，不声称必需或最优；生成前核验题面。

**必须实现的代码**：
- `query_rising_temperature.sql`。
- `query_next_day_retention.sql`。
- `query_restaurant_growth.sql`。

**可视化**：日期轴、首次登录标记与七日窗口。

**练习**：
- 说明上一条记录不一定是昨天。
- 比较SQLite教学SQL和题目MySQL方言，分别标注。

**单元测试规格**：
- 同日多条消费先聚合。
- 缺失日期不按行数冒充自然日。
- 次日留存分母为玩家。
- 跨月年。
- 仅本地执行过的方言标为已测。

**边界与生成要求**：日期窗口区分自然日和数据行；生成前核对题目是否保证日期连续，不额外假定。

**运行时**：`{"python_packages": [], "external_programs": [], "stdlib_modules": ["sqlite3"]}`。

---

### N157｜Pandas选择、缺失与类型

**文件**：`notebooks/19_specialized_tracks/157_pandas_selection_cleaning.ipynb`

**层级 / 类型**：L1 / specialized；**先修**：N005, N007, N010。

**教学目标**：在保留数据类型和索引语义下清洗表。

**知识点**：DataFrame/Series；loc/iloc；布尔筛选；NA；astype；去重；链式赋值风险。

**代表 LeetCode 题**：
- 2877. Create a DataFrame from List — 典型应用；生成前核验题面。
- 2882. Drop Duplicate Rows — 典型应用；生成前核验题面。
- 2883. Drop Missing Data — 典型应用；生成前核验题面。
- 2886. Change Data Type — 典型应用；生成前核验题面。

**必须实现的代码**：
- `create_dataframe(student_data)`。
- `drop_duplicate_emails(customers)`。
- `drop_missing_names(students)`。
- `change_grade_type(students)`。

**可视化**：每一步的表、索引和dtype对照。

**练习**：
- 解释NaN不能用==比较。
- 区分原地修改和返回新表。

**单元测试规格**：
- 空表保持规定列。
- 重复email保留规则一致。
- 缺失name删除。
- 转换前后dtype验证。
- 使用assert_frame_equal。

**边界与生成要求**：代表题用于知识映射；先讲最小问题，再完成本章核心实现。对比与拓展题不强制变成独立完整题解。

**运行时**：`{"python_packages": ["pandas"], "external_programs": []}`。

---

### N158｜Pandas连接、聚合与宽长变换

**文件**：`notebooks/19_specialized_tracks/158_pandas_aggregation_merge_reshape.ipynb`

**层级 / 类型**：L2 / specialized；**先修**：N157, N154。

**教学目标**：明确连接键、分组键和输出形状。

**知识点**：groupby/agg/transform；merge；concat；pivot/pivot_table；melt；多对多。

**代表 LeetCode 题**：
- [2888. Reshape Data: Concatenate](https://leetcode.com/problems/reshape-data-concatenate/) — 典型应用；官方页面已核对题号与标题。
- [2889. Reshape Data: Pivot](https://leetcode.com/problems/reshape-data-pivot/) — 典型应用；官方页面已核对题号与标题。
- [2890. Reshape Data: Melt](https://leetcode.com/problems/reshape-data-melt/) — 典型应用；官方页面已核对题号与标题。
- 183. Customers Who Never Order — 对照或复用已有题；生成前核验题面。

**必须实现的代码**：
- `concatenate_tables(df1, df2)`。
- `pivot_weather(weather)`。
- `melt_sales(report)`。
- `customers_without_orders(customers, orders)`。

**可视化**：连接前后基数与宽长表转换。

**练习**：
- 构造重复键使pivot报错并解释应否聚合。
- SQL反连接与Pandas结果互验。

**单元测试规格**：
- concat行数为两表之和。
- melt行数为实体数×季度数。
- 重复键按契约处理。
- 保留规定列序且规范化索引后比较。

**边界与生成要求**：代表题用于知识映射；先讲最小问题，再完成本章核心实现。对比与拓展题不强制变成独立完整题解。

**运行时**：`{"python_packages": ["pandas"], "external_programs": []}`。

---

### N159｜Pandas日期、排名与滚动统计

**文件**：`notebooks/19_specialized_tracks/159_pandas_time_rank_rolling.ipynb`

**层级 / 类型**：L3 / specialized；**先修**：N158, N155, N156。

**教学目标**：用矢量化运算表达时间和分组窗口。

**知识点**：to_datetime；dt访问；rank；groupby shift；rolling；字符串str；缺失日期。

**代表 LeetCode 题**：
- 185. Department Top Three Salaries — 对照或复用已有题；生成前核验题面。
- 550. Game Play Analysis IV — 对照或复用已有题；生成前核验题面。
- 1667. Fix Names in a Table — 典型应用；生成前核验题面。

**必须实现的代码**：
- `department_top_three_salaries(employees, departments)`。
- `next_day_retention(activity)`。
- `normalize_names(users)`。
- `daily_rolling_sales(df)`。

**可视化**：排名与日期对齐前后的结果表。

**练习**：
- 区别按行rolling和按时间窗口rolling。
- 避免无必要逐行apply。

**单元测试规格**：
- 并列薪资全部保留。
- 日期跨月。
- 玩家多次同日记录不重复计分母。
- 姓名大小写按题面字符集。
- 与SQL小表结果对照。

**边界与生成要求**：代表题用于知识映射；先讲最小问题，再完成本章核心实现。对比与拓展题不强制变成独立完整题解。

**运行时**：`{"python_packages": ["pandas"], "external_programs": []}`。

---

### N160｜Shell文本流与管道

**文件**：`notebooks/19_specialized_tracks/160_shell_text_processing.ipynb`

**层级 / 类型**：L2 / specialized；**先修**：N006, N010, N023。

**教学目标**：用真实文本工具完成逐行和按列处理。

**知识点**：stdin/stdout；管道；grep/awk/sed；sort/uniq；正则；locale；退出码。

**代表 LeetCode 题**：
- 192. Word Frequency — 典型应用；生成前核验题面。
- 193. Valid Phone Numbers — 典型应用；生成前核验题面。
- 194. Transpose File — 典型应用；生成前核验题面。
- 195. Tenth Line — 典型应用；生成前核验题面。

**必须实现的代码**：
- `word_frequency.sh`。
- `valid_phone_numbers.sh`。
- `transpose_file.sh`。
- `tenth_line.sh`。

**可视化**：管道各阶段的文本与行数。

**练习**：
- 处理不满10行文件。
- 说明sort和locale如何影响排序，不用Python重写题解。

**单元测试规格**：
- 空文件与末行无换行。
- 合法/非法电话边界。
- 词频并列按约定。
- 通过subprocess运行真实bash/awk并检查退出码和stdout。

**边界与生成要求**：必须运行真实bash/awk/sed等程序；缺运行时直接报告环境阻塞，不转换为Python并标为Shell通过。

**运行时**：`{"python_packages": [], "external_programs": ["bash", "awk", "sed", "grep", "sort", "uniq"]}`。

---

### N161｜JavaScript基础、闭包与对象

**文件**：`notebooks/19_specialized_tracks/161_javascript_fundamentals_closures.ipynb`

**层级 / 类型**：L1 / specialized；**先修**：N004, N009, N010。

**教学目标**：理解JS与Python语义差异并保留闭包状态。

**知识点**：let/const；类型与===；undefined/null；数组对象；闭包；this/原型导览。

**代表 LeetCode 题**：
- [2667. Create Hello World Function](https://leetcode.com/problems/create-hello-world-function/) — 典型应用；官方页面已核对题号与标题。
- 2620. Counter — 典型应用；生成前核验题面。
- 2665. Counter II — 典型应用；生成前核验题面。
- 2695. Array Wrapper — 拓展/替代算法，不声称必需或最优；生成前核验题面。

**必须实现的代码**：
- `createHelloWorld()`。
- `createCounter(n)`。
- `createCounterWithReset(init)`。

**可选拓展实现**：
- `ArrayWrapper（拓展）`。

**可视化**：闭包环境、变量绑定与调用后状态。

**练习**：
- 比较重新创建计数器和复用计数器。
- 解释箭头函数的this差异。

**单元测试规格**：
- 任意参数返回Hello World。
- 独立计数器状态互不干扰。
- reset恢复初值。
- 用Node.js assert运行，禁止Python仿真JS语义。

**边界与生成要求**：采用Python内核组织Notebook，通过显式Node子进程运行JS；JS代码在Node执行，不是Python语义模拟。

**运行时**：`{"python_packages": [], "external_programs": ["node"]}`。

---

### N162｜JavaScript函数组合、缓存与事件

**文件**：`notebooks/19_specialized_tracks/162_javascript_functional_events.ipynb`

**层级 / 类型**：L3 / specialized；**先修**：N161。

**教学目标**：用函数对象组合行为并管理订阅生命周期。

**知识点**：map/filter/reduce；函数组合；memoization键；once；事件订阅/取消；对象引用。

**代表 LeetCode 题**：
- 2635. Apply Transform Over Each Element in Array — 典型应用；生成前核验题面。
- 2629. Function Composition — 典型应用；生成前核验题面。
- 2623. Memoize — 典型应用；生成前核验题面。
- [2694. Event Emitter](https://leetcode.com/problems/event-emitter/) — 典型应用；官方页面已核对题号与标题。

**必须实现的代码**：
- `map(arr, fn)`。
- `compose(functions)`。
- `memoize(fn)`。
- `EventEmitter`。

**可视化**：函数流水线与事件监听器集合变化。

**练习**：
- 比较按JSON文本键和对象身份缓存的不同契约。
- 实现unsubscribe。

**单元测试规格**：
- 空组合为恒等函数。
- 同参缓存减少原函数调用。
- 无监听emit返回[]。
- 监听按订阅顺序调用。
- Node断言覆盖取消订阅。

**边界与生成要求**：代表题用于知识映射；先讲最小问题，再完成本章核心实现。对比与拓展题不强制变成独立完整题解。

**运行时**：`{"python_packages": [], "external_programs": ["node"]}`。

---

### N163｜JavaScript异步、定时器与并发限制

**文件**：`notebooks/19_specialized_tracks/163_javascript_promises_timers.ipynb`

**层级 / 类型**：L4 / specialized；**先修**：N161, N162, N053。

**教学目标**：分离Promise结果竞速和底层任务取消。

**知识点**：Promise/async/await；微任务；超时；debounce/throttle；并发池；异常传播。

**代表 LeetCode 题**：
- 2721. Execute Asynchronous Functions in Parallel — 典型应用；生成前核验题面。
- [2637. Promise Time Limit](https://leetcode.com/problems/promise-time-limit/) — 典型应用；官方页面已核对题号与标题。
- 2627. Debounce — 典型应用；生成前核验题面。
- 2636. Promise Pool — 拓展/替代算法，不声称必需或最优；生成前核验题面。

**必须实现的代码**：
- `promiseAll(functions)`。
- `timeLimit(fn, t)`。
- `debounce(fn, t)`。
- `promisePool(functions, n)`。

**可视化**：事件循环与任务开始、完成、超时的时序图。

**练习**：
- 解释超时拒绝不等于取消原任务。
- 用可控时钟测试debounce边界而非脆弱毫秒断言。

**单元测试规格**：
- 空并行列表。
- 任务拒绝传播。
- 输出按输入顺序。
- 活跃任务数不超过n。
- 结束后清理定时器。
- 真实Node执行。

**边界与生成要求**：Promise超时不自动取消底层任务；定时器测试使用受控时钟或稳健事件次序断言，不使用脆弱精确毫秒相等。

**运行时**：`{"python_packages": [], "external_programs": ["node"]}`。

---

## 20_concurrency｜并发

### N164｜线程、互斥与顺序同步

**文件**：`notebooks/20_concurrency/164_threads_ordering_events.ipynb`

**层级 / 类型**：L3 / specialized；**先修**：N009, N053, N013。

**教学目标**：用同步关系保证顺序而不是依靠启动次序。

**知识点**：threading；共享状态；race；Lock/Event；happens-before；GIL非同步契约。

**代表 LeetCode 题**：
- [1114. Print in Order](https://leetcode.com/problems/print-in-order/) — 典型应用；官方页面已核对题号与标题。

**必须实现的代码**：
- `Foo.first/second/third`。
- `run_ordering_case(start_order)`。

**可视化**：线程时间线与事件依赖边。

**练习**：
- 枚举三线程启动排列。
- 构造无同步版本的可能交错，而不要求随机必现错误。

**单元测试规格**：
- 6种启动次序都输出firstsecondthird。
- 每回调一次。
- 子进程超时隔离。
- 线程结束后资源清理。

**边界与生成要求**：线程启动顺序不是执行顺序；不得使用sleep假装实现同步。死锁演示必须放入可终止的子进程。

**运行时**：`{"python_packages": [], "external_programs": [], "stdlib_modules": ["threading", "multiprocessing", "subprocess"]}`。

---

### N165｜信号量、条件变量与交替执行

**文件**：`notebooks/20_concurrency/165_semaphores_conditions_alternation.ipynb`

**层级 / 类型**：L3 / specialized；**先修**：N164, N023。

**教学目标**：维护轮到谁的状态并正确等待谓词。

**知识点**：Semaphore；Condition；while predicate；notify；零奇偶状态机；忙等反例。

**代表 LeetCode 题**：
- 1115. Print FooBar Alternately — 典型应用；生成前核验题面。
- 1116. Print Zero Even Odd — 典型应用；生成前核验题面。

**必须实现的代码**：
- `FooBar`。
- `ZeroEvenOdd`。

**可视化**：许可证流转与条件状态机。

**练习**：
- 分别以信号量和Condition实现交替。
- 解释等待谓词为何使用while。

**单元测试规格**：
- n=1。
- n=3得到foobar重复3次。
- 零奇偶n=3输出010203。
- 无多印少印。
- 外层子进程超时不算成功。

**边界与生成要求**：代表题用于知识映射；先讲最小问题，再完成本章核心实现。对比与拓展题不强制变成独立完整题解。

**运行时**：`{"python_packages": [], "external_programs": [], "stdlib_modules": ["threading", "multiprocessing", "subprocess"]}`。

---

### N166｜屏障、生产消费与有界队列

**文件**：`notebooks/20_concurrency/166_barriers_bounded_queues.ipynb`

**层级 / 类型**：L3 / specialized；**先修**：N165, N053。

**教学目标**：维护容量约束和批次组成而不跨批串线。

**知识点**：Barrier；生产者/消费者；not_empty/not_full；容量不变量；批次同步。

**代表 LeetCode 题**：
- 1117. Building H2O — 典型应用；生成前核验题面。
- 1188. Design Bounded Blocking Queue — 拓展/替代算法，不声称必需或最优；生成前核验题面。

**必须实现的代码**：
- `H2O`。
- `BoundedBlockingQueue.enqueue/dequeue/size`。

**可视化**：生产消费队列占用曲线与HHO批次分组。

**练习**：
- 区分可选输出顺序和每批2H1O组成约束。
- 说明多个条件共享同一锁。

**单元测试规格**：
- 任意输入到达顺序下每组三个原子恰2H1O。
- 队列大小始终在[0,capacity]。
- 所有入队项不丢不重。
- 超时隔离与清理。

**边界与生成要求**：代表题用于知识映射；先讲最小问题，再完成本章核心实现。对比与拓展题不强制变成独立完整题解。

**运行时**：`{"python_packages": [], "external_programs": [], "stdlib_modules": ["threading", "multiprocessing", "subprocess"]}`。

---

### N167｜死锁、饥饿与哲学家问题

**文件**：`notebooks/20_concurrency/167_deadlocks_fairness_philosophers.ipynb`

**层级 / 类型**：L4 / specialized；**先修**：N164, N165, N166, N013。

**教学目标**：区分安全性、无死锁和有条件的无饥饿。

**知识点**：资源顺序；循环等待；FIFO准入；公平调度假设；有限持有时间；活性。

**代表 LeetCode 题**：
- [1226. The Dining Philosophers](https://leetcode.com/problems/the-dining-philosophers/) — 典型应用；官方页面已核对题号与标题。
- 1195. Fizz Buzz Multithreaded — 拓展/替代算法，不声称必需或最优；生成前核验题面。

**必须实现的代码**：
- `DiningPhilosophersFIFO.wantsToEat(...)`。
- `validate_fork_trace(events)`。

**可视化**：资源分配图、FIFO请求与叉子占用时间线。

**练习**：
- 比较统一加锁顺序和FIFO准入：前者无死锁不自动证明无饥饿。
- 为活性明确调度假设。

**单元测试规格**：
- 同一叉子不被并发占用。
- 吃饭前持有两把叉。
- 同一哲学家多次并发请求用不同票号。
- 有界测试完成不替代活性证明。

**边界与生成要求**：FIFO准入按请求票号而非哲学家编号。无饥饿论证必须明确有限回调、有限资源持有和调度假设；有限次压测不是活性证明。

**运行时**：`{"python_packages": [], "external_programs": [], "stdlib_modules": ["threading", "multiprocessing", "subprocess"]}`。

---

## 21_mastery｜综合迁移与结业

### N168｜约束建模与算法选择训练

**文件**：`notebooks/21_mastery/168_modeling_algorithm_selection.ipynb`

**层级 / 类型**：L3 / capstone；**先修**：N016, N029, N056, N103。

**教学目标**：在不看标签时根据结构提出可检验候选。

**知识点**：目标类型；数据性质；约束；状态图；单调性；候选排除；不是关键词套模板。

**代表 LeetCode 题**：
- 209. Minimum Size Subarray Sum — 典型应用；生成前核验题面。
- [862. Shortest Subarray with Sum at Least K](https://leetcode.com/problems/shortest-subarray-with-sum-at-least-k/) — 对照或复用已有题；官方页面已核对题号与标题。
- 300. Longest Increasing Subsequence — 对照或复用已有题；生成前核验题面。

**必须实现的代码**：
- `solve_min_length_positive(nums, target)`。
- `solve_min_length_signed(nums, target)`。
- `compare_candidates(cases)`。

**可视化**：同一题改变负数/有序/在线条件后的方法选择表。

**练习**：
- 去掉题目标签重新建模。
- 写出每种候选算法必须成立的前提。

**单元测试规格**：
- 非负版与负数版各自对拍。
- 给出普通窗口失败反例。
- 不得自动调用通用求解器隐藏错误建模。

**边界与生成要求**：代表题用于知识映射；先讲最小问题，再完成本章核心实现。对比与拓展题不强制变成独立完整题解。

---

### N169｜从暴力到最优的优化阶梯

**文件**：`notebooks/21_mastery/169_optimization_ladder_differential_testing.ipynb`

**层级 / 类型**：L4 / capstone；**先修**：N015, N032, N038, N135, N056。

**教学目标**：在每次优化后保留独立可验证的参照。

**知识点**：重复计算；状态压缩；单调候选；分治统计；操作数；对拍。

**代表 LeetCode 题**：
- 327. Count of Range Sum — 典型应用；生成前核验题面。
- 239. Sliding Window Maximum — 对照或复用已有题；生成前核验题面。

**必须实现的代码**：
- `count_range_sum_bruteforce(nums, lower, upper)`。
- `count_range_sum_merge(nums, lower, upper)`。
- `benchmark_operation_counts()`。

**可视化**：暴力、前缀、归并优化的操作量对照。

**练习**：
- 为范围和同时实现Fenwick替代解。
- 缩减对拍失败样本到最小反例。

**单元测试规格**：
- [-2,5,-1],lower=-2,upper=2→3。
- 0值和重复前缀。
- 下上界相同。
- 小域穷举与两条独立实现一致。

**边界与生成要求**：代表题用于知识映射；先讲最小问题，再完成本章核心实现。对比与拓展题不强制变成独立完整题解。

---

### N170｜正确性证明与反例工作坊

**文件**：`notebooks/21_mastery/170_proofs_and_counterexamples_workshop.ipynb`

**层级 / 类型**：L4 / capstone；**先修**：N013, N043, N084, N093。

**教学目标**：能把直觉改写为完整论证并指出适用边界。

**知识点**：循环不变量；交换论证；归纳；终止性；负例；证明与测试分工。

**代表 LeetCode 题**：
- 410. Split Array Largest Sum — 对照或复用已有题；生成前核验题面。
- [435. Non-overlapping Intervals](https://leetcode.com/problems/non-overlapping-intervals/) — 对照或复用已有题；官方页面已核对题号与标题。
- 743. Network Delay Time — 对照或复用已有题；生成前核验题面。

**必须实现的代码**：
- `feasible_partition(nums, limit, groups)`。
- `verify_witness_partition(nums, cuts, limit)`。
- `find_small_greedy_counterexample()`。

**可视化**：证明步骤—代码行—反例的对应表。

**练习**：
- 分别证明二分单调、区间贪心和Dijkstra。
- 给出撤掉前提后失败的输入。

**单元测试规格**：
- 合法分段证据确实覆盖原数组且不超阈值。
- 小数组枚举最优分段。
- 负权例只用于反驳非负前提缺失。

**边界与生成要求**：代表题用于知识映射；先讲最小问题，再完成本章核心实现。对比与拓展题不强制变成独立完整题解。

---

### N171｜测试、调试与性能回归

**文件**：`notebooks/21_mastery/171_testing_debugging_performance.ipynb`

**层级 / 类型**：L3 / capstone；**先修**：N010, N015, N042, N049, N147。

**教学目标**：用边界、状态性质和复杂度诊断验证实现。

**知识点**：最小复现；多解比较；别名；整数/浮点；缓存污染；操作计数；环境隔离。

**代表 LeetCode 题**：
- 146. LRU Cache — 对照或复用已有题；生成前核验题面。
- 234. Palindrome Linked List — 对照或复用已有题；生成前核验题面。
- 34. Find First and Last Position of Element in Sorted Array — 对照或复用已有题；生成前核验题面。

**必须实现的代码**：
- `normalize_solution_output(x)`。
- `assert_linked_structure(head)`。
- `differential_test_lru(operations)`。
- `count_binary_search_iterations()`。

**可视化**：失败样例缩减与错误定位表。

**练习**：
- 修复刻意注入的链表断链、LRU淘汰和二分边界错误。
- 区分速度噪声与阶数变化。

**单元测试规格**：
- 同一测试重复运行结果一致。
- 多解不强制单一答案。
- 输入恢复。
- 不通过try/except吞掉失败。
- 操作计数符合预期阶。

**边界与生成要求**：代表题用于知识映射；先讲最小问题，再完成本章核心实现。对比与拓展题不强制变成独立完整题解。

---

### N172｜Medium综合题与机制组合

**文件**：`notebooks/21_mastery/172_medium_pattern_combinations.ipynb`

**层级 / 类型**：L3 / capstone；**先修**：N061, N094, N097, N035。

**教学目标**：在两个已知机制之间定义清楚接口。

**知识点**：排序+堆；前缀+哈希；单调结构+贪心；分离状态职责。

**代表 LeetCode 题**：
- 621. Task Scheduler — 典型应用；生成前核验题面。
- 767. Reorganize String — 典型应用；生成前核验题面。
- 1024. Video Stitching — 典型应用；生成前核验题面。

**必须实现的代码**：
- `least_interval(tasks, n)`。
- `reorganize_string(s)`。
- `video_stitching(clips, time)`。

**可视化**：冷却时间线、字符排程和区间覆盖前沿。

**练习**：
- 同题实现计数公式与事件模拟。
- 解释正确组合而非无依据堆叠模板。

**单元测试规格**：
- AAABBB冷却2最短长度8。
- 无法重排返回空。
- 区间无法覆盖→-1。
- 小实例穷举调度/覆盖对拍。

**边界与生成要求**：代表题用于知识映射；先讲最小问题，再完成本章核心实现。对比与拓展题不强制变成独立完整题解。

---

### N173｜Hard序列、字符串与设计综合

**文件**：`notebooks/21_mastery/173_hard_sequences_strings_capstone.ipynb`

**层级 / 类型**：L4 / capstone；**先修**：N029, N056, N107, N170, N171。

**教学目标**：独立推导状态或候选支配并比较两种解法。

**知识点**：最短覆盖；单调队列；前缀；区间合并；状态设计；适用条件。

**代表 LeetCode 题**：
- 76. Minimum Window Substring — 对照或复用已有题；生成前核验题面。
- [862. Shortest Subarray with Sum at Least K](https://leetcode.com/problems/shortest-subarray-with-sum-at-least-k/) — 对照或复用已有题；官方页面已核对题号与标题。
- [1000. Minimum Cost to Merge Stones](https://leetcode.com/problems/minimum-cost-to-merge-stones/) — 对照或复用已有题；官方页面已核对题号与标题。

**必须实现的代码**：
- `min_window_audited(s, t)`。
- `shortest_subarray_audited(nums, k)`。
- `merge_stones_audited(stones, k)`。

**可视化**：关键状态随输入演进及竞争解法失效点。

**练习**：
- 完成一题不看标签的变体。
- 为每题提供一个导致常见错误的最小输入。

**单元测试规格**：
- 覆盖目标重数。
- 含负数无解。
- 合并不满足余数条件。
- 独立暴力参照与规模测试分离。

**边界与生成要求**：代表题用于知识映射；先讲最小问题，再完成本章核心实现。对比与拓展题不强制变成独立完整题解。

---

### N174｜Hard图树、离线与查询综合

**文件**：`notebooks/21_mastery/174_hard_graph_tree_capstone.ipynb`

**层级 / 类型**：L5 / capstone；**先修**：N125, N140, N141, N143, N144, N171。
**拓展先修**：N139, N137。

**教学目标**：将树上路径、动态候选和状态搜索组合为算法。

**知识点**：DFS入退事件；计数Trie；离线查询；状态最短路；恢复；规模约束。

**代表 LeetCode 题**：
- [1938. Maximum Genetic Difference Query](https://leetcode.com/problems/maximum-genetic-difference-query/) — 典型应用；官方页面已核对题号与标题。
- 847. Shortest Path Visiting All Nodes — 典型应用；生成前核验题面。
- [2617. Minimum Number of Visited Cells in a Grid](https://leetcode.com/problems/minimum-number-of-visited-cells-in-a-grid/) — 拓展/替代算法，不声称必需或最优；官方页面已核对题号与标题。

**必须实现的代码**：
- `max_genetic_difference(parents, queries)`。
- `shortest_path_visiting_all(graph)`。

**可选拓展实现**：
- `minimum_visited_cells(grid)（拓展）`。

**可视化**：DFS路径Trie内容与位状态BFS前沿。

**练习**：
- 为树查询实现逐祖先慢参照。
- 比较网格暴力边枚举和候选跳过。

**单元测试规格**：
- parents=[-1,0,1,1],queries=[[0,2],[3,2],[2,5]]→[2,3,7]。
- 兄弟分支不泄漏Trie计数。
- 小图全状态参照。
- 深链避免递归栈溢出。

**边界与生成要求**：代表题用于知识映射；先讲最小问题，再完成本章核心实现。对比与拓展题不强制变成独立完整题解。

---

### N175｜陌生题迁移与结业项目

**文件**：`notebooks/21_mastery/175_unseen_transfer_final_project.ipynb`

**层级 / 类型**：L5 / capstone；**先修**：N168, N169, N170, N171, N172, N173, N174, N108, N059。

**教学目标**：在无标签新变体中完成建模、证明、实现和复盘。

**知识点**：独立分析；强参照；约束变化；复杂度；解释；失败边界；知识迁移。

**代表 LeetCode 题**：
- 42. Trapping Rain Water — 对照或复用已有题；生成前核验题面。
- 1235. Maximum Profit in Job Scheduling — 对照或复用已有题；生成前核验题面。
- [1439. Find the Kth Smallest Sum of a Matrix With Sorted Rows](https://leetcode.com/problems/find-the-kth-smallest-sum-of-a-matrix-with-sorted-rows/) — 对照或复用已有题；官方页面已核对题号与标题。

**必须实现的代码**：
- `job_scheduling(start, end, profit)`。
- `kth_smallest_row_sum(mat, k)`。
- `solve_unseen_variant(instance)`。
- `reference_unseen_variant(instance)`。

**可视化**：候选算法比较表、最终状态图与证据摘要。

**练习**：
- 用自编未展示答案的变体作正式考核，以上题只作热身。
- 改变在线/加权/重复/规模中的一个条件并重新推导。

**单元测试规格**：
- 课程示例与考核数据分离。
- 小域暴力与优化版对拍。
- 性能测试不跑暴力大输入。
- 评分区分正确性、论证和迁移，不以题数毕业。

**边界与生成要求**：官方题仅作综合热身；正式考核使用自编未展示解答的变体。不要把重做已讲过的题标成陌生题能力证据。

---

## 先修拓扑顺序

编号是知识目录，不是强制学习顺序。例如位基础N124需要在部分状态压缩课程之前学习；概率N131需要在概率DP N114之前学习。下面是经依赖校验的一条可执行顺序：

```text
N001 → N002 → N003 → N004 → N005 → N006 → N007 → N008 → N009 → N010 → N011 → N012 → N013 → N014
N015 → N016 → N017 → N018 → N019 → N020 → N021 → N022 → N023 → N024 → N025 → N026 → N027 → N028
N029 → N030 → N031 → N032 → N033 → N034 → N035 → N036 → N037 → N038 → N039 → N040 → N041 → N042
N043 → N044 → N045 → N046 → N047 → N048 → N049 → N050 → N051 → N052 → N053 → N054 → N055 → N056
N057 → N058 → N059 → N060 → N061 → N062 → N063 → N064 → N065 → N066 → N067 → N068 → N069 → N070
N071 → N072 → N073 → N074 → N075 → N076 → N077 → N078 → N079 → N080 → N081 → N082 → N083 → N084
N085 → N086 → N087 → N093 → N094 → N095 → N096 → N097 → N098 → N099 → N100 → N101 → N102 → N103
N104 → N105 → N106 → N107 → N108 → N109 → N110 → N111 → N117 → N118 → N124 → N112 → N125 → N126
N127 → N128 → N129 → N131 → N134 → N135 → N136 → N147 → N148 → N149 → N150 → N151 → N088 → N089
N090 → N091 → N092 → N113 → N114 → N115 → N116 → N119 → N120 → N121 → N122 → N123 → N130 → N132
N133 → N137 → N138 → N139 → N140 → N141 → N142 → N143 → N144 → N145 → N146 → N152 → N153 → N154
N155 → N156 → N157 → N158 → N159 → N160 → N161 → N162 → N163 → N164 → N165 → N166 → N167 → N168
N169 → N170 → N171 → N172 → N173 → N174 → N175
```

## 引用与核验边界

代表题链接只在本轮实际访问官方页面后写入。其他题号标题为待核对映射，不能据此声称已完整阅读题面、题解或核对语言支持。
课程组织、代码接口、练习和测试规格为本包设计；不表示LeetCode官方采用这些章节划分或推荐所有拓展算法。
生成时应基于原题重新表述问题、使用自编教学例子并引用官方题面，避免复制大量题面或题解。
