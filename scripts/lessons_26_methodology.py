"""Model boundaries, independent references, constructive witnesses and regression checks."""
from course_builder import add, NODES
from lessons_21_design import LINKED, LRU_CODE

MIN_LENGTH = '''from collections import deque

def solve_min_length_positive(nums, target):
    """Nonnegative values, positive target; return -1 when no nonempty window works."""
    if target <= 0 or any(x < 0 for x in nums):
        raise ValueError('Requires nonnegative elements and positive target')
    left = total = 0
    answer = len(nums)+1
    for right,value in enumerate(nums):
        total += value
        while total >= target:
            answer = min(answer,right-left+1)
            total -= nums[left]
            left += 1
    return -1 if answer > len(nums) else answer

def solve_min_length_signed(nums, target):
    if target <= 0:
        raise ValueError('Positive target required')
    prefix = [0]
    for value in nums:
        prefix.append(prefix[-1]+value)
    candidates = deque()
    answer = len(nums)+1
    for right,current in enumerate(prefix):
        while candidates and current-prefix[candidates[0]] >= target:
            answer = min(answer,right-candidates.popleft())
        while candidates and prefix[candidates[-1]] >= current:
            candidates.pop()
        candidates.append(right)
    return -1 if answer > len(nums) else answer

def compare_candidates(cases):
    rows = []
    for nums,target in cases:
        positive_result = solve_min_length_positive(nums,target) if all(x>=0 for x in nums) else 'inapplicable: negative element'
        rows.append((nums,target,positive_result,solve_min_length_signed(nums,target)))
    return rows
'''
add(168,
'''同一个“最短连续区间和至少为 target”的问题，删除“非负”约束就改变了解法。非负数组扩张右端不会降低和，缩短左端不会增大和，才允许普通滑动窗口单向排除答案。

含负数时改用前缀和：寻找最小的 j−i，使 `P[j]−P[i]≥target`。若较新的 i 有不大的前缀值，它比更老、更大的前缀同时更易达标且更短，旧候选因此被支配。单调双端队列保存未被支配的候选。

两个公开函数都要求正 target，无解统一返回 −1。比较表明确标记不适用，不自动调用更强求解器替一个前提错误的方法“兜底”。''',
MIN_LENGTH,
'''show_table(['nums','target','nonnegative window','signed deque'], compare_candidates([
    ([2,3,1,2,4,3],7),([1,-1,3],3),([0,0,1],2),([],1)]))
''',
'''import itertools
def brute(nums,target):
    valid=[j-i for i in range(len(nums)) for j in range(i+1,len(nums)+1) if sum(nums[i:j])>=target]
    return min(valid,default=-1)
for n in range(6):
    for nums in itertools.product([-1,0,2],repeat=n):
        for target in [1,2,3,5]:
            expected=brute(nums,target)
            assert solve_min_length_signed(nums,target)==expected
            if all(x>=0 for x in nums):assert solve_min_length_positive(nums,target)==expected
assert solve_min_length_signed([1,-1,3],3)==1
try:solve_min_length_positive([1,-1,3],3)
except ValueError:pass
else:raise AssertionError('Missing nonnegative precondition')
# Deliberately incorrect outside its domain: run only to expose the counterexample.
def invalid_plain_window(nums,target):
    left=total=0;answer=len(nums)+1
    for right,value in enumerate(nums):
        total+=value
        while total>=target:
            answer=min(answer,right-left+1);total-=nums[left];left+=1
    return -1 if answer>len(nums) else answer
assert invalid_plain_window([1,-1,3],3)==3
assert brute([1,-1,3],3)==1
''',
'''非负窗口依赖左右变化的单调性；负数反例直接否定该前提缺失时的推导。前缀队列的尾部删除基于支配关系，头部删除基于已找到该起点最短的当前终点，未来终点只会更长。每个下标最多入队、出队各一次。''',
'''普通窗口时间 O(n)、辅助空间 O(1)；前缀单调队列时间 O(n)、空间 O(n)。独立穷举只用于小规模核验。''')

RANGE_COUNT = '''def count_range_sum_bruteforce(nums, lower, upper, stats=None):
    if lower>upper:
        raise ValueError('lower must not exceed upper')
    answer = 0
    if stats is not None:
        stats['extensions']=0
    for left in range(len(nums)):
        total=0
        for right in range(left,len(nums)):
            total+=nums[right]
            answer += lower<=total<=upper
            if stats is not None:stats['extensions']+=1
    return answer

def count_range_sum_merge(nums, lower, upper, stats=None):
    if lower>upper:
        raise ValueError('lower must not exceed upper')
    prefix=[0]
    for value in nums:prefix.append(prefix[-1]+value)
    operations=0
    def sort_count(values):
        nonlocal operations
        if len(values)<=1:return values,0
        middle=len(values)//2
        left,a=sort_count(values[:middle])
        right,b=sort_count(values[middle:])
        answer=a+b
        lo=hi=0
        for value in left:
            while lo<len(right):
                operations+=1
                if right[lo]-value>=lower:break
                lo+=1
            while hi<len(right):
                operations+=1
                if right[hi]-value>upper:break
                hi+=1
            answer+=hi-lo
        merged=[];i=j=0
        while i<len(left) and j<len(right):
            operations+=1
            if left[i]<=right[j]:merged.append(left[i]);i+=1
            else:merged.append(right[j]);j+=1
        merged.extend(left[i:]);merged.extend(right[j:])
        return merged,answer
    answer=sort_count(prefix)[1]
    if stats is not None:stats['comparisons']=operations
    return answer

def benchmark_operation_counts():
    rows=[]
    for n in [16,32,64,128,256]:
        nums=[(i*17)%11-5 for i in range(n)]
        slow={};fast={}
        a=count_range_sum_bruteforce(nums,-3,4,slow)
        b=count_range_sum_merge(nums,-3,4,fast)
        assert a==b
        rows.append((n,slow['extensions'],fast['comparisons']))
    return rows
'''
add(169,
'''优化前先固定计数对象：每个区间对应一对不同位置的前缀 `(i,j)`，i<j。重复的前缀数值不能去重，因为它们代表不同区间。

直接累加枚举是 O(n²)。改成前缀和只能省掉每个区间的求和，还没有减少区间对数。真正的改进是按原下标分治：左右半边内部递归统计，跨半边的所有左前缀都天然早于右前缀；再按数值排序，用两个单向边界计数。

左前缀 p 增大时，右前缀合法区间 `[p+lower,p+upper]` 也右移，所以两个边界都不用回退。演示统计实际比较次数，不用一次毫秒曲线冒充复杂度证明。''',
RANGE_COUNT,
'''show_table(['n','brute extensions','merge comparisons'],benchmark_operation_counts())
show_table(['nums','range','count'],[([-2,5,-1],[-2,2],count_range_sum_merge([-2,5,-1],-2,2)),([0,0],[0,0],count_range_sum_merge([0,0],0,0))])
''',
'''import itertools,math
assert count_range_sum_merge([-2,5,-1],-2,2)==3
assert count_range_sum_merge([0,0,0],0,0)==6
for n in range(6):
    for nums in itertools.product([-1,0,1],repeat=n):
        for lower,upper in [(-2,2),(0,0),(-1,0),(1,2)]:
            assert count_range_sum_merge(nums,lower,upper)==count_range_sum_bruteforce(nums,lower,upper)
for n,brute_ops,merge_ops in benchmark_operation_counts():
    assert brute_ops==n*(n+1)//2
    assert merge_ops<=10*(n+1)*math.ceil(math.log2(n+1))
assert count_range_sum_merge([10**30,-10**30],0,0)==1
''',
'''每一对前缀恰在最小的、将二者分入不同半边的递归节点被统计一次。右边界条件 `<lower` 和 `<=upper` 分别对应闭区间两端；重复值保留位置重数。分治合并没有遗漏或重复。''',
'''递推 T(n)=2T(n/2)+O(n)，时间 O(n log n)，本实现峰值辅助空间 O(n)，递归深度 O(log n)。Python 大整数算术成本还取决于整数位长；这里的 n 复杂度采用字长算术模型。''')

PARTITION = '''def feasible_partition(nums, limit, groups):
    """Nonnegative values; return (feasible, exclusive_end_cuts)."""
    if limit<0 or groups<1 or any(x<0 for x in nums):
        raise ValueError('Nonnegative values/limit and positive groups required')
    if not nums:return True,[]
    if max(nums)>limit:return False,[]
    cuts=[];total=0
    for i,value in enumerate(nums):
        if total+value>limit:
            cuts.append(i)
            total=0
        total+=value
    cuts.append(len(nums))
    return (True,cuts) if len(cuts)<=groups else (False,[])

def verify_witness_partition(nums, cuts, limit):
    """Witness validator also accepts signed values; no greedy inference is made."""
    if not nums:return cuts==[]
    if not cuts or cuts[-1]!=len(nums):return False
    previous=0
    for end in cuts:
        if not isinstance(end,int) or not previous<end<=len(nums):return False
        if sum(nums[previous:end])>limit:return False
        previous=end
    return previous==len(nums)

def find_small_greedy_counterexample():
    from itertools import product
    # The nonnegative proof uses 'a too-large singleton makes the task impossible'.
    # Negative neighbors can invalidate that inference, even with just one group.
    for n in range(1,4):
        for nums in product(range(-2,4),repeat=n):
            for limit in range(4):
                if any(x<0 for x in nums) and max(nums)>limit and sum(nums)<=limit:
                    return {'nums':list(nums),'limit':limit,'groups':1,
                            'invalid_greedy_claim':False,'valid_cuts':[n]}
    raise AssertionError('The enumerated domain should contain a counterexample')
'''
add(170,
'''正确性主张应该配一个可检查的证据。判断能否分成至多 groups 段时，成功不只返回 True，还给出每段的右开端点 cuts。验证器独立检查覆盖、非空、顺序和每段阈值。

非负数组的贪心让当前段尽量长。若另一个合法分段第一刀更早，可以把该刀右移到贪心位置：前段仍合法，被移走元素非负，所以后段负担不会增大。重复交换得到贪心所用段数最少。

加入负数后，“单个元素大于阈值必定无解”已经不成立。反例搜索只用来反驳缺少前提的推理，不把含负数数组传给不适用的生产函数再宣称算法正确。''',
PARTITION,
'''nums=[7,2,5,10,8]
ok,cuts=feasible_partition(nums,18,2)
start=0;rows=[]
for end in cuts:
    rows.append((start,end,nums[start:end],sum(nums[start:end])))
    start=end
show_table(['start','exclusive end','segment','sum'],rows)
show_table(['counterexample field','value'],list(find_small_greedy_counterexample().items()))
''',
'''import itertools
ok,cuts=feasible_partition([7,2,5,10,8],18,2)
assert ok and len(cuts)<=2 and verify_witness_partition([7,2,5,10,8],cuts,18)
def brute_partition(nums,limit,groups):
    if not nums:return True
    for count in range(1,min(groups,len(nums))+1):
        for middle in itertools.combinations(range(1,len(nums)),count-1):
            cuts=list(middle)+[len(nums)]
            if verify_witness_partition(nums,cuts,limit):return True
    return False
for n in range(5):
    for nums in itertools.product(range(3),repeat=n):
        for limit in range(5):
            for groups in range(1,4):
                actual,cuts=feasible_partition(nums,limit,groups)
                assert actual==brute_partition(nums,limit,groups)
                if actual:assert len(cuts)<=groups and verify_witness_partition(nums,cuts,limit)
assert not verify_witness_partition([1,2],[0,2],3)
assert not verify_witness_partition([1,2],[1],3)
assert not verify_witness_partition([1,2],[2,2],3)
case=find_small_greedy_counterexample()
assert verify_witness_partition(case['nums'],case['valid_cuts'],case['limit'])
assert max(case['nums'])>case['limit']
try:feasible_partition(case['nums'],case['limit'],1)
except ValueError:pass
else:raise AssertionError('Signed array should be explicitly rejected')
''',
'''交换论证的关键不是“选最长看起来好”，而是右移分割不会增加后续段的和，恰好用到了非负性。证据检查器只检查给定分段是否成立，不推断最少段数；因此可以用于独立核验，包括含负数的反例。''',
'''贪心与证据验证时间 O(n)，cuts 空间 O(groups)（构造阶段最坏 O(n)）。穷举检查只运行小数组，不放进正式求解路径。''')

REGRESSION = NODES + '\n' + LINKED + LRU_CODE + '''
from collections import OrderedDict

def normalize_solution_output(x):
    """For unordered collections of unordered integer combinations only.
    Multiplicity is preserved so duplicate answers remain detectable.
    """
    return tuple(sorted(tuple(sorted(row)) for row in x))

def assert_linked_structure(head):
    nodes=[];seen=set()
    while head is not None:
        assert id(head) not in seen, 'Cycle found'
        seen.add(id(head));nodes.append(head);head=head.next
    return nodes

def differential_test_lru(operations, capacity=2):
    cache=LRUCache(capacity);reference=OrderedDict();results=[]
    for op in operations:
        if op[0]=='put':
            _,key,value=op
            cache.put(key,value)
            if capacity:
                if key in reference:del reference[key]
                elif len(reference)==capacity:reference.popitem(last=False)
                reference[key]=value
        elif op[0]=='get':
            _,key=op
            expected=reference.get(key,-1)
            if key in reference:reference.move_to_end(key)
            actual=cache.get(key)
            assert actual==expected
            results.append(actual)
        else:raise ValueError('Unknown cache operation')
        nodes=[];node=cache.order.head.next;previous=cache.order.head
        while node is not cache.order.tail:
            assert node.prev is previous and node not in nodes
            nodes.append(node);previous,node=node,node.next
        assert cache.order.tail.prev is previous
        assert [(node.key,node.value) for node in nodes]==list(reference.items())
        assert set(nodes)==set(cache.nodes.values()) and cache.order.size==len(nodes)
    return results

def count_binary_search_iterations():
    rows=[]
    for n in [0,1,2,4,8,16,64,256,1024]:
        maximum=0
        for target in range(-1,n+1):
            left,right=0,n;count=0
            while left<right:
                middle=(left+right)//2;count+=1
                if middle<target:left=middle+1
                else:right=middle
            assert left==min(n,max(0,target))
            maximum=max(maximum,count)
        rows.append((n,maximum))
    return rows
'''
add(171,
'''测试规范化只能消除题意允许的无关差异，不能抹掉错误。组合题允许答案顺序不同，但重复答案通常是错的，所以规范化保留重数；路径题的节点顺序有意义，不能拿同一个排序函数处理。

链表测试要保留节点引用，检查无环、身份和 next 是否恢复；缓存测试除了 get 返回值，还核对每次操作后的完整 LRU 顺序与双向连接。这样才能抓到“暂时输出相同，但内部状态已错”的实现。

性能回归优先统计真正执行的比较或状态数。二分区间每轮至少近似减半，可以导出对数上界；固定硬件上的毫秒门槛既不能证明复杂度，也容易产生偶然失败。''',
REGRESSION,
'''show_table(['array length','maximum lower-bound loop iterations'],count_binary_search_iterations())
ops=[('put',1,10),('put',2,20),('get',1),('put',3,30),('get',2),('get',3)]
show_table(['operation trace','get results'],[(ops,differential_test_lru(ops))])
''',
'''import math,random
assert normalize_solution_output([[1,2],[3,4]])==normalize_solution_output([[4,3],[2,1]])
assert normalize_solution_output([[1,2],[1,2]])!=normalize_solution_output([[1,2]])
head=list_to_nodes([1,2,3]);before=assert_linked_structure(head)
links=[node.next for node in before]
def reverse(head):
    previous=None
    while head:
        nxt=head.next;head.next=previous;previous=head;head=nxt
    return previous
restored=reverse(reverse(head))
assert restored is head and assert_linked_structure(restored)==before
assert all(node.next is nxt for node,nxt in zip(before,links))
before[-1].next=head
try:assert_linked_structure(head)
except AssertionError:pass
else:raise AssertionError('Cycle went undetected')
before[-1].next=None
assert all(node.next is nxt for node,nxt in zip(before,links))
rng=random.Random(171)
operations=[('put',rng.randrange(7),rng.randrange(50)) if rng.randrange(2) else ('get',rng.randrange(7)) for _ in range(500)]
for capacity in [0,1,3]:
    assert differential_test_lru(operations,capacity)==differential_test_lru(operations,capacity)
for n,iterations in count_binary_search_iterations():
    assert iterations<=math.ceil(math.log2(n+1)) if n else iterations==0
''',
'''独立参照实现维护同一接口但不同内部机制：OrderedDict 对比手写双链表；结构断言检查映射与链表一一对应。恢复测试比较对象引用而非仅比较值。二分的循环不变量是答案始终位于当前半开候选区间的边界范围内。''',
'''普通 LRU 操作仍期望 O(1)；本章诊断每一步扫描缓存，测试开销 O(操作数×容量)，不把诊断器的开销误称为算法开销。二分正式查询 O(log n)。''')
