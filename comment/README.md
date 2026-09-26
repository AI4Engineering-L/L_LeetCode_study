# 说人话详解注释 · 总索引

本目录为 `notebooks/` 下全部 175 个课程 notebook（N001–N175）配套的"说人话"详解注释。每份文件与 notebook 同名（`.ipynb` → `.md`），固定八节结构：

1. **这章要解决什么问题？**（大白话重述 + 具体数字例子）
2. **关键概念**（每个术语 1–3 句大白话定义）
3. **解决思路**（Step 1→N 一步步推导 + 手算演示）
4. **代码逐段讲解**（逐字照抄 notebook 代码，逐行解释）
5. **为什么是对的？复杂度是多少？**（原文压缩论证的口语化翻译）
6. **测试用例在测什么**（逐条 assert 解读）
7. **练习思路提示**（只给方向不给答案）
8. **对应 LeetCode 题目**（题号与本章知识点的映射）

用法：先读 notebook 的推导区，卡住或觉得跳跃时，打开同名 md 对应小节看展开讲解；每份文件开头都标注了对应的 notebook 路径。

## 目录

### 00_foundations · 基础与工具（N001–N010）

- [001 Notebook 与判题接口](001_jupyter_and_judge.md) — 单元格/内核/执行顺序；print 给人看、return 给判题器看
- [002 值、类型与运算符](002_values_types_operators.md) — Python 的值、类型系统与运算符行为
- [003 分支与循环](003_branching_loops.md) — 条件分支与循环的写法及边界
- [004 函数、作用域与契约](004_functions_scope_contracts.md) — 函数定义、作用域规则、输入输出契约
- [005 列表、可变性与别名](005_lists_mutation_aliasing.md) — 列表原地修改、别名陷阱与共享引用
- [006 字符串、Unicode 与解析](006_strings_unicode_parsing.md) — 字符串不可变性、Unicode 与格式解析
- [007 字典、集合、元组](007_dict_set_tuple.md) — 三大内置容器的选型与用法
- [008 标准库工具箱](008_standard_library_toolbox.md) — Counter 频次统计、deque 队列等常用工具
- [009 类、节点与协议](009_classes_nodes_protocols.md) — ListNode/TreeNode 定义、类与实例
- [010 调试与可复现 Notebook](010_debugging_reproducible_notebooks.md) — traceback 读法、断言固化修复

### 01_reasoning · 复杂度与推理（N011–N016）

- [011 时间与空间复杂度](011_time_space_complexity.md) — Two Sum 暴力法的 n(n−1)/2 推导与 O(n²) 分析
- [012 从约束推算法](012_constraints_to_algorithms.md) — 状态数 × 每状态代价 × 机器预算的选型流程
- [013 不变量、归纳与终止](013_invariants_induction_termination.md) — "初始化—保持—终止"三段式证明
- [014 均摊复杂度](014_amortized_analysis.md) — 两栈队列：单次最贵 O(n) 但总账 O(1)
- [015 暴力参照与差分测试](015_bruteforce_oracles_properties.md) — 用暴力解当裁判、小域穷举验证
- [016 问题建模与反例](016_problem_modeling_and_counterexamples.md) — 子数组 vs 子序列的建模差异与构造反例

### 02_array_string_hash · 数组字符串哈希（N017–N024）

- [017 数组扫描与原地覆盖](017_array_scans_inplace.md) — 读写双指针压缩，Remove/Move Zeroes
- [018 矩阵遍历与边界模拟](018_matrix_traversal_simulation.md) — 螺旋遍历与原地旋转
- [019 哈希查找与索引映射](019_hash_lookup_index.md) — 两数之和：值→下标账本 + 补数查询
- [020 频率统计与等价类分组](020_hash_frequency_grouping.md) — 判异位词、排序签名分组
- [021 集合、去重与连续序列](021_hash_sets_sequence_dedup.md) — 只从链首延伸的最长连续序列
- [022 字符串同构与模式](022_string_mapping_order.md) — 双向字典判双射及单向检查反例
- [023 字符串解析与状态机](023_string_parsing_fsm.md) — atoi 四阶段与有效数字三开关
- [024 数组结构变换](024_array_string_transformations.md) — 三次反转右旋、游程压缩

### 03_pointers_windows · 双指针与滑窗（N025–N030）

- [025 相向双指针](025_opposite_two_pointers.md) — 有序两数和的单调排除、回文判断
- [026 同向快慢指针](026_same_direction_fast_slow.md) — `nums[write-k]` 统一原地去重
- [027 k 数和与消元法](027_k_sum_and_geometric_elimination.md) — 三数和 + 盛水容器同骨架对照
- [028 固定长度窗口](028_fixed_windows.md) — 窗口和增量更新、频次表判排列
- [029 可变长度窗口](029_variable_windows.md) — 最小覆盖子串的收缩扩张
- [030 恰好 k 个的窗口计数](030_window_counting_exactly_k.md) — "至多 k"相减技巧

### 04_prefix_intervals · 前缀和与区间（N031–N036）

- [031 前缀和/异或/积](031_prefix_sums_xor_products.md) — 一维前缀家族与除自身乘积
- [032 前缀+哈希计数](032_prefix_hash_counting.md) — 连续子数组和被整除
- [033 二维前缀和](033_prefix_sum_2d.md) — 容斥原理与矩阵块和
- [034 差分数组](034_difference_arrays.md) — 区间加一次搞定、拼车问题
- [035 区间并交](035_interval_union_intersection.md) — 排序扫描的区间运算
- [036 扫描线与事件](036_sweep_line_events.md) — +1/−1 事件求最大重叠

### 05_sort_binary_search · 排序与二分（N037–N044）

- [037 基础排序](037_elementary_sorts.md) — 插入/选择/冒泡的不变量与稳定性
- [038 归并排序与逆序对](038_merge_sort_and_inversions.md) — 分治合并 + factor 单调扫描
- [039 快速排序与划分](039_quicksort_partition.md) — 三路划分不变量、显式栈
- [040 堆排/计数/桶/基数](040_heapsort_counting_bucket_radix.md) — 数组藏树与非比较排序
- [041 快速选择](041_quickselect_order_statistics.md) — 第 k 大：只追一侧的期望 O(n)
- [042 二分查找与边界](042_binary_search_bounds.md) — lower/upper_bound 半开区间统一框架
- [043 二分答案](043_binary_search_on_answer.md) — 求最优转判可行的 first_true 模板
- [044 结构化数据二分](044_binary_search_structured_data.md) — 旋转数组/矩阵/峰值

### 06_linked_lists · 链表（N045–N050）

- [045 哨兵节点](045_linked_list_sentinels.md) — dummy 消灭头节点特例
- [046 链表反转](046_linked_list_reversal.md) — 整链与区间反转
- [047 快慢指针](047_linked_list_fast_slow.md) — Floyd 判环/找入口、中点、倒数第 n
- [048 链表归并](048_linked_list_merge_sort.md) — 有序合并与断链分段
- [049 重排与回文](049_linked_list_reordering_palindrome.md) — 中点+反转+穿插组合拳
- [050 高级链表结构](050_linked_list_advanced_structures.md) — K 组反转、交点、随机指针深拷贝

### 07_stack_queue · 栈与队列（N051–N056）

- [051 栈匹配与路径](051_stack_matching_paths.md) — 括号/Unix 路径/相邻消除统一视角
- [052 表达式解析栈](052_expression_parsing_stacks.md) — 逆波兰 + 递归下降三层文法
- [053 队列与双端队列实现](053_queue_deque_implementations.md) — 环形数组取模回绕、两栈队列
- [054 单调栈找邻居](054_monotonic_stack_neighbors.md) — 下一个更大元素、循环数组扫两圈
- [055 单调栈贡献法](055_monotonic_stack_contributions.md) — 直方图最大矩形、子数组最小值和
- [056 单调队列窗口](056_monotonic_queue_windows.md) — 滑窗最大值、前缀和递增队列

### 08_heaps · 堆（N057–N061）

- [057 堆基础](057_heap_fundamentals.md) — 手写 MinHeap：上浮/下沉/自底建堆
- [058 堆 Top-K](058_heap_top_k.md) — 大小 k 小根堆当准入门槛
- [059 K 路归并](059_heap_k_way_merge.md) — 每路一个堆头、弹一个补一个
- [060 双堆与惰性删除](060_two_heaps_lazy_deletion.md) — 中位数维护 + delayed 计数清理
- [061 堆事件调度](061_heap_event_scheduling.md) — 就绪堆 + 时间跳转的任务调度

### 09_recursion_backtracking · 递归与回溯（N062–N068）

- [062 递归契约](062_recursion_contracts.md) — 契约+基例+规模递减，trace 暴露重复子问题
- [063 分治模式](063_divide_and_conquer_patterns.md) — 快速幂与多数元素的合并花样
- [064 子集/排列/组合](064_subsets_permutations_combinations.md) — choose–explore–undo 骨架
- [065 去重与剪枝](065_backtracking_dedup_pruning.md) — 排序+同层跳过
- [066 划分与搜索约束](066_partitioning_and_search_constraints.md) — 回文切分、复原 IP
- [067 网格回溯](067_grid_backtracking.md) — 棋盘当 visited、try/finally 恢复
- [068 皇后与数独](068_constraint_satisfaction_queens_sudoku.md) — 对角线标识、三集合登记簿、MRV

### 10_trees_tries · 树与字典树（N069–N078）

- [069 树的 DFS 遍历](069_tree_dfs_traversals.md) — 前中后序的递归与显式栈翻译
- [070 层序与视图](070_tree_bfs_views.md) — 层大小快照切层、锯齿与右视图
- [071 自底向上聚合](071_tree_bottom_up_aggregation.md) — 一套骨架求深度/平衡/直径
- [072 树路径问题](072_tree_path_problems.md) — 根到叶、任意路径最大和、前缀计数
- [073 BST 不变量与操作](073_bst_invariants_operations.md) — 范围不变量、中序、删除
- [074 建树与序列化](074_tree_construction_serialization.md) — 前序+中序重建、槽结构校验
- [075 最近公共祖先](075_lowest_common_ancestor.md) — 父指针祖先集 vs BST 区间分叉
- [076 Morris 与原地变换](076_tree_transformations_morris.md) — 建线/拆线纪律的线索遍历
- [077 Trie 前缀树](077_trie_prefix_dictionary.md) — 前缀状态与词尾分离、词根替换
- [078 Trie+回溯+通配符](078_trie_backtracking_wildcards.md) — WordDictionary 与网格搜词

### 11_graphs · 图（N079–N092）

- [079 图的表示](079_graph_representations.md) — 邻接表/矩阵/边表与入出度
- [080 DFS/连通分量/环](080_graph_dfs_components_cycles.md) — 三色法判环、洪泛数岛
- [081 BFS 与多源扩散](081_graph_bfs_multisource.md) — 烂橘子扩散、01 矩阵反向视角
- [082 拓扑排序](082_topological_sort_dag.md) — Kahn 入度法、输出不足判环
- [083 并查集](083_disjoint_set_union.md) — 路径减半+按大小合并、找冗余边
- [084 Dijkstra 与 0-1 BFS](084_dijkstra_zero_one_bfs.md) — 松弛、过期堆项、双端队列调度
- [085 Bellman-Ford 与 Floyd](085_bellman_ford_floyd.md) — 分轮松弛、K 站限制、全源
- [086 最小生成树](086_minimum_spanning_trees.md) — Kruskal/Prim 与割环性质
- [087 二分图与匹配](087_bipartite_graphs_matching.md) — 二染色判定、增广路扩匹配
- [088 强连通分量](088_strongly_connected_components.md) — Kosaraju/Tarjan 与缩点
- [089 桥与割点](089_bridges_articulation_points.md) — disc/low-link 的严格/非严格不等式
- [090 欧拉路径](090_eulerian_paths.md) — 度条件、Hierholzer 后序构造
- [091 函数图](091_functional_graphs.md) — ρ 形结构、时间戳找环、入度剥离
- [092 最大流最小割](092_max_flow_min_cut.md) — Dinic 层次图/阻塞流/当前弧

### 12_greedy · 贪心（N093–N097）

- [093 区间交换贪心](093_greedy_exchange_intervals.md) — 最早结束优先 + 交换论证
- [094 可达性分层](094_greedy_reachability_layers.md) — 跳跃游戏的前沿右边界
- [095 平衡两遍扫描](095_greedy_balance_two_pass.md) — 加油站与分糖果
- [096 堆替换贪心](096_greedy_heap_replacement.md) — 超时弹最长、IPO 门槛解锁
- [097 字典序构造](097_greedy_lexicographic_construction.md) — 单调栈删位、去重、冷却重排

### 13_dynamic_programming · 动态规划（N098–N117）

- [098 从递归到表格](098_dp_from_recursion_to_tables.md) — 爬楼梯三步进化：递归→记忆化→表格
- [099 线性 DP 与 Kadane](099_linear_dp_and_kadane.md) — 打家劫舍（含环形）与最大子数组
- [100 网格 DP](100_grid_dp.md) — 路径计数、最小路径和、地牢倒推
- [101 0/1 背包](101_zero_one_knapsack.md) — 逆序容量原理、位集判等和分割
- [102 完全/多重/分组背包](102_unbounded_bounded_group_knapsack.md) — 循环顺序决定组合还是排列
- [103 LIS 与有序序列](103_lis_and_ordered_sequences.md) — 平方 DP→tails 二分、套娃信封
- [104 双序列对齐](104_sequence_alignment_dp.md) — LCS/编辑距离/不同子序列
- [105 字符串切分与匹配](105_string_segmentation_matching_dp.md) — 单词拆分、解码、两种星号语义
- [106 状态机 DP（股票）](106_finite_state_dp_stocks.md) — 持有/不持有状态机四变体
- [107 区间 DP](107_interval_dp.md) — 戳气球最后一步决策、合并石头
- [108 划分 DP](108_partition_dp.md) — 最后一段切分与最大分块和
- [109 树形 DP](109_tree_dp_selection_matching.md) — 选/不选二元组、摄像头三状态
- [110 换根 DP](110_rerooting_dp.md) — 两遍扫描与距离和公式
- [111 DAG DP](111_dag_dp_and_longest_paths.md) — 拓扑分层 + 状态向量合并
- [112 状态压缩 DP](112_bitmask_dp.md) — mask 当集合、贴纸、哈密顿
- [113 数位 DP](113_digit_dp.md) — tight/started 逐位统计
- [114 概率期望 DP](114_probability_expectation_dp.md) — 骑士撒概率、21 点滑窗
- [115 博弈 DP](115_game_dp_minimax.md) — 我方差 = 收获 − 对手差
- [116 轮廓 DP](116_profile_dp_grid_states.md) — 行掩码排座、三色染网格
- [117 DP 优化基础](117_dp_optimization_basics.md) — 单调队列优化、支配关系

### 14_string_algorithms · 字符串算法（N118–N123）

- [118 KMP 与 Z 函数](118_kmp_and_z_function.md) — 失配链接与 Z-box 抄写
- [119 滚动哈希](119_rolling_hash_substrings.md) — 多项式前缀哈希 + 精确复核
- [120 Manacher](120_palindrome_algorithms_manacher.md) — 三档回文解法与镜像复用
- [121 AC 自动机](121_aho_corasick_automaton.md) — fail 链与流式多模式匹配
- [122 后缀数组与 LCP](122_suffix_array_lcp.md) — 倍增排序、Kasai、不同子串计数
- [123 后缀自动机](123_suffix_automaton.md) — endpos 等价类与克隆

### 15_math_bits_geometry · 数学位运算几何（N124–N133）

- [124 位与整数表示](124_bits_integer_representation.md) — n&(n−1) 清位、32 位翻转
- [125 位掩码/异或/XOR Trie](125_bitmasks_xor_trie.md) — 子掩码枚举、高位贪心
- [126 GCD 与数论](126_gcd_euclid_number_theory.md) — 扩展欧几里得、lcm 先除后乘
- [127 素数筛与分解](127_primes_sieves_factorization.md) — 埃氏筛、SPF 查表分解
- [128 模运算与快速幂](128_modular_arithmetic_fast_power.md) — 快速幂、逆元、超长指数
- [129 组合计数](129_combinatorics_counting.md) — 组合数、Catalan、容斥
- [130 矩阵快速幂](130_matrix_exponentiation_recurrences.md) — 状态向量与转移矩阵
- [131 随机与概率](131_randomized_sampling_probability.md) — 洗牌、蓄水池、拒绝采样
- [132 SG 函数与博弈](132_impartial_games_sprague_grundy.md) — mex、Nim 异或
- [133 计算几何](133_computational_geometry.md) — 叉积方向、凸包单调链

### 16_advanced_structures · 高级数据结构（N134–N140）

- [134 坐标压缩与第 k 小](134_coordinate_compression_order_statistics.md) — 值→秩保序映射
- [135 树状数组](135_fenwick_tree.md) — lowbit 分块、点增区间查
- [136 线段树（幺半群）](136_segment_tree_monoids.md) — combine+identity 泛化接口
- [137 懒标记线段树](137_lazy_segment_tree_range_updates.md) — 标记复合与 push/pull 时机
- [138 稀疏表 RMQ](138_sparse_table_rmq.md) — 倍增建表、幂等重叠查询
- [139 Treap 与跳表](139_balanced_trees_treaps_skiplists.md) — 期望平衡与 rank/kth
- [140 带权/可回滚并查集](140_weighted_rollback_dsu.md) — 连乘比值、历史栈还原

### 17_advanced_algorithms · 高级算法（N141–N146）

- [141 Euler 序与倍增](141_euler_tour_binary_lifting.md) — tin/tout 子树区间、k 级祖先
- [142 折半搜索](142_meet_in_the_middle.md) — 子集最近和、整数二倍防失精度
- [143 离线查询与 Mo](143_offline_queries_sweep_mo.md) — 候选堆扫描线、离线 DSU、Mo 排序
- [144 状态图/双向 BFS/A*](144_state_graph_bidirectional_astar.md) — 开锁/华容道建模、启发式
- [145 DP 优化条件](145_advanced_dp_optimization_conditions.md) — 四边形不等式、分治优化、Li Chao
- [146 FFT/NTT 卷积](146_fft_ntt_convolution.md) — 位反转蝶形、模域精确卷积

### 18_design · 设计题（N147–N151）

- [147 LRU/LFU 缓存](147_lru_lfu_caches.md) — 哨兵双向链表+哈希、频次桶
- [148 随机集合](148_randomized_set_multiset.md) — 数组+反向索引+交换删除
- [149 惰性迭代器](149_iterators_lazy_evaluation.md) — 显式栈 BST 迭代器、Peeking
- [150 快照与版本](150_snapshots_persistent_versions.md) — 稀疏版本账本+二分查时间前驱
- [151 组合服务设计](151_composite_service_design.md) — TimeMap 与 Twitter 消息流

### 19_specialized_tracks · 专项轨道（N152–N163）

- [152 SQL 基础与 NULL](152_sql_select_null_sort.md) — 投影过滤、三值逻辑陷阱
- [153 SQL 聚合与连接](153_sql_aggregation_joins.md) — LEFT JOIN、GROUP BY+HAVING
- [154 SQL 子查询/CTE/反连接](154_sql_subqueries_cte_antijoins.md) — NOT EXISTS 对 NOT IN 的 NULL 免疫
- [155 SQL 窗口函数](155_sql_window_rank_sequences.md) — 三个 rank 兄弟、gaps and islands
- [156 SQL 日期与留存](156_sql_dates_retention_reports.md) — 次日留养分母口径、RANGE 滑窗
- [157 pandas 选择与清洗](157_pandas_selection_cleaning.md) — dropna/drop_duplicates、可空 Int64
- [158 pandas 聚合与变形](158_pandas_aggregation_merge_reshape.md) — pivot/melt 宽长互逆
- [159 pandas 时间与滚动](159_pandas_time_rank_rolling.md) — groupby+rank、rolling('7D')
- [160 shell 文本处理](160_shell_text_processing.md) — awk 词频、正则验电话、转置
- [161 JS 基础与闭包](161_javascript_fundamentals_closures.md) — 词法绑定、共享私有状态
- [162 JS 函数式与事件](162_javascript_functional_events.md) — compose、memoize、EventEmitter
- [163 JS Promise 与定时器](163_javascript_promises_timers.md) — promiseAll 归位、debounce、并发池

### 20_concurrency · 并发（N164–N167）

- [164 线程顺序与 Event](164_threads_ordering_events.md) — happens-before 链、门闩语义
- [165 信号量与条件变量](165_semaphores_conditions_alternation.md) — turn 状态机、许可证接力
- [166 屏障与有界队列](166_barriers_bounded_queues.md) — H2O 成分+批次、满/空双 while
- [167 死锁/公平/哲学家](167_deadlocks_fairness_philosophers.md) — FIFO 票号 + 一锁预留双叉

### 21_mastery · 大师课（N168–N175）

- [168 建模与算法选型](168_modeling_algorithm_selection.md) — 同题异构：非负滑窗 vs 含负队列
- [169 优化阶梯与对拍](169_optimization_ladder_differential_testing.md) — 暴力→分治阶梯 + 差分验证
- [170 证明与反例工作坊](170_proofs_and_counterexamples_workshop.md) — 交换论证、见证 cuts、撤前提反例
- [171 测试调试与性能](171_testing_debugging_performance.md) — 差分测试、结构断言、轮数计数
- [172 Medium 组合](172_medium_pattern_combinations.md) — 机制组合与接口定义三连
- [173 Hard 序列字符串](173_hard_sequences_strings_capstone.md) — 前提被破坏的三道 Hard
- [174 Hard 图树](174_hard_graph_tree_capstone.md) — 路径计数 Trie、状态最短路
- [175 结业迁移项目](175_unseen_transfer_final_project.md) — 复习主线 + 陌生变体 + 强参照
