from course_builder import add, NODES

add(1, '把程序看成一个从输入到输出的映射。`print`只是展示副作用；判题器读取函数的返回值。先调用普通函数，再让 `Solution` 方法委托给同一实现。单元格可以被乱序运行，但可靠的教程必须在清空内核后按顺序运行。',
'''def sum_two(a: int, b: int) -> int:
    return a + b

class Solution:
    def sum(self, num1: int, num2: int) -> int:
        return sum_two(num1, num2)
''',
'''show_table(['输入 a', '输入 b', '返回值'], [(a,b, sum_two(a,b)) for a,b in [(2,3),(-4,4),(0,0)]])''',
'''assert sum_two(2,3) == 5
assert sum_two(-4,4) == 0
assert Solution().sum(7,-2) == 5''',
'函数没有外部状态：每次调用只计算两个参数的和。用方法封装不改变该映射。', '固定字长模型下时间、额外空间均为 O(1)；Python 大整数加法随位数增长。')

add(2, '最小正偶数倍要同时满足“是 n 的倍数”和“是 2 的倍数”。正整数 n 已经是偶数时答案就是 n，否则为 2n。温度转换则是固定仿射变换；浮点数是有限二进制表示，测试用容差而不是要求十进制逐位完全相等。',
'''def smallest_even_multiple(n: int) -> int:
    if n < 1:
        raise ValueError('n must be a positive integer')
    return n if n % 2 == 0 else 2*n

def convert_temperature(celsius: float) -> list[float]:
    return [celsius + 273.15, celsius*1.8 + 32]
''',
'''show_table(['a', 'a // 3', 'a % 3', '验证 a=q×3+r'], [(a,a//3,a%3,(a//3)*3+a%3) for a in range(-4,5)])''',
'''import math
assert smallest_even_multiple(5) == 10
assert smallest_even_multiple(6) == 6
kelvin, fahrenheit = convert_temperature(0)
assert math.isclose(kelvin,273.15,abs_tol=1e-9)
assert math.isclose(fahrenheit,32,abs_tol=1e-9)
assert -4//3 == -2 and int(-4/3) == -1''',
'奇数 n 的奇数倍仍是奇数，因此至少乘 2；偶数 n 自身可行。Python 整除向负无穷取整，与向零截断不同。','固定字长下 O(1) 时间与空间。')

add(3, '用循环逐个覆盖区间 1 到 n。FizzBuzz 的条件有交集：15 的倍数同时满足 3 与 5，所以先判断更严格的交集，不能让较宽条件提前截走它。枚举并不低级；当每个输出都必须产生时，线性扫描已经匹配输出下界。',
'''def fizz_buzz(n: int) -> list[str]:
    answer = []
    for i in range(1,n+1):
        if i % 15 == 0:
            answer.append('FizzBuzz')
        elif i % 3 == 0:
            answer.append('Fizz')
        elif i % 5 == 0:
            answer.append('Buzz')
        else:
            answer.append(str(i))
    return answer

def sum_even(n: int) -> int:
    total = 0
    for i in range(2,n+1,2):
        total += i
    return total
''',
'''show_table(['i', '3整除', '5整除', '输出'], [(i,i%3==0,i%5==0,x) for i,x in enumerate(fizz_buzz(15),1)])''',
'''assert fizz_buzz(3) == ['1','2','Fizz']
assert fizz_buzz(15)[-1] == 'FizzBuzz'
assert fizz_buzz(1) == ['1']
assert sum_even(8) == 20
assert fizz_buzz(0) == []''',
'循环第 i 次结束后，答案恰好包含 1…i 的正确输出。初始化为空；互斥分支覆盖全部整数；终止后得到完整答案。','按整数转字符串代价细计，输出总字符数 O(n log n)；忽略位数时扫描 O(n)，额外辅助空间 O(1)。')

add(4, '把“直到变成零”定义成循环契约：正偶数除以 2，正奇数减 1。每次操作严格减小非负整数，因此会终止。计数器必须是函数局部变量，不能把上次调用的步骤数带进下一次。',
'''def is_even(num: int) -> bool:
    return num % 2 == 0

def number_of_steps(num: int) -> int:
    if num < 0:
        raise ValueError('num must be nonnegative')
    steps = 0
    while num:
        num = num//2 if is_even(num) else num-1
        steps += 1
    return steps
''',
'''x=14
rows=[]
while x:
    nxt=x//2 if is_even(x) else x-1
    rows.append((x,'除2' if is_even(x) else '减1',nxt))
    x=nxt
show_table(['当前值','动作','新值'],rows)''',
'''assert number_of_steps(14) == 6
assert number_of_steps(0) == 0
assert number_of_steps(1) == 1
assert [number_of_steps(14) for _ in range(3)] == [6,6,6]''',
'步骤计数等于已经执行的合法转换数。非负值严格下降保证终止；每一步是题意指定动作，不存在选择歧义。','单位字长模型下 O(log(num+1)) 时间、O(1) 辅助空间。')

add(5, '列表存放对象引用，不是一个个对象的深复制。`[[0]*cols]*rows`重复同一行引用，修改一行会影响其他行。列表推导式每次创建新行，才得到独立行。数组拼接应返回新列表，同时保留输入不变。',
'''def get_concatenation(nums: list[int]) -> list[int]:
    return nums + nums

def build_matrix(rows: int, cols: int) -> list[list[int]]:
    if rows < 0 or cols < 0:
        raise ValueError('dimensions must be nonnegative')
    return [[0 for _ in range(cols)] for _ in range(rows)]
''',
'''good=build_matrix(2,3)
bad=[[0]*3]*2
good[0][0]=7
bad[0][0]=7
show_table(['构造','第0行','第1行','行是否同一对象'], [('推导式',good[0],good[1],good[0] is good[1]),('重复引用',bad[0],bad[1],bad[0] is bad[1])])''',
'''a=[1,2,1]
b=get_concatenation(a)
assert b == [1,2,1,1,2,1] and a == [1,2,1] and b is not a
m=build_matrix(2,2)
m[0][0]=1
assert m[1][0] == 0 and m[0] is not m[1]
assert build_matrix(0,3) == []''',
'每个循环迭代新建一个内层列表，因此各行身份不同。拼接按原序各复制一次引用；对整数列表这满足无意外修改输入的契约。','拼接 O(n) 时间及输出空间；矩阵 O(rows×cols) 时间及输出空间。')

add(6, '字符串不可变。IP 字符转义是局部替换；Goal Parser 是按合法 token 扫描：`G`、`()`、`(al)`分别映射到固定输出。索引必须一次跳过整个 token，不能误把括号内部重新识别。这里明确限定输入为这三种 token 的串联，非法 token 抛错。',
'''def defang_ip(address: str) -> str:
    return address.replace('.', '[.]')

def interpret(command: str) -> str:
    pieces=[]
    i=0
    while i<len(command):
        if command.startswith('G',i):
            pieces.append('G'); i+=1
        elif command.startswith('()',i):
            pieces.append('o'); i+=2
        elif command.startswith('(al)',i):
            pieces.append('al'); i+=4
        else:
            raise ValueError(f'invalid token at index {i}')
    return ''.join(pieces)
''',
'''show_table(['输入 token','输出','消费字符数'], [(token,interpret(token),len(token)) for token in ['G','()','(al)']])''',
'''assert defang_ip('1.1.1.1') == '1[.]1[.]1[.]1'
assert interpret('G()(al)') == 'Goal'
assert interpret('') == ''
assert interpret('(al)G(al)()()G') == 'alGalooG'
try:
    interpret('(bad)')
except ValueError:
    pass
else:
    raise AssertionError('invalid token must fail explicitly')''',
'扫描指针前的字符都已被恰好一个合法 token 消费，pieces 是它们的正确翻译。三种 token 的起始结构可区分，每步前进保证终止。','时间 O(n)，输出与暂存片段 O(n)；join 避免反复拼接造成的复制。')

add(7, '重复检测只关心“是否出现过”，用集合；计数则要保留“出现多少次”，用字典。键必须可哈希：整数、字符串和元素可哈希的元组可以；可变列表不能直接作键。哈希查找复杂度通常谈平均情况，不保证对抗碰撞下严格常数。',
'''def contains_duplicate(nums: list[int]) -> bool:
    seen=set()
    for x in nums:
        if x in seen:
            return True
        seen.add(x)
    return False

def count_values(nums: list[int]) -> dict[int,int]:
    counts={}
    for x in nums:
        counts[x]=counts.get(x,0)+1
    return counts
''',
'''a=[2,1,2,3,2]
show_table(['已读前缀','频次'], [(a[:i],count_values(a[:i])) for i in range(len(a)+1)])''',
'''assert contains_duplicate([1,2,1]) is True
assert contains_duplicate([1,2,3]) is False
assert contains_duplicate([]) is False
assert sum(count_values([2,1,2,3]).values()) == 4
assert count_values([]) == {}''',
'处理新元素前，seen 恰好是已读元素的集合；counts[x] 恰好是该前缀中 x 的出现次数。查询再更新避免把当前元素与自己重复匹配。','平均 O(n) 时间，O(u) 空间，u 为不同值数量。')

add(8, '算法工具不是替代理解，而是表达操作意图。Counter负责计数，deque负责两端队列操作，heapq维护堆，bisect查询有序列表边界；deque 的 popleft 避免列表头删的整体搬移。本章用两遍扫描找第一个唯一字符，保留原始位置次序。',
'''from collections import Counter, deque

def first_unique_char(s: str) -> int:
    counts=Counter(s)
    for i,c in enumerate(s):
        if counts[c]==1:
            return i
    return -1

def deque_queue_demo(items):
    queue=deque(items)
    result=[]
    while queue:
        result.append(queue.popleft())
    return result
''',
'''q=deque()
rows=[]
for x in [4,1,7]:
    q.append(x); rows.append(('append',x,list(q)))
while q:
    x=q.popleft(); rows.append(('popleft',x,list(q)))
show_table(['操作','元素','队列状态'],rows)''',
'''assert first_unique_char('leetcode') == 0
assert first_unique_char('aabb') == -1
assert first_unique_char('') == -1
assert deque_queue_demo([3,1,2]) == [3,1,2]
c=Counter('ab'); before=dict(c); assert c['z']==0; assert dict(c)==before''',
'首遍得到完整频次；第二遍从左至右扫描，首次频次为 1 的位置必然是最左合法答案。deque按一端入、一端出保持FIFO。','两个实现均为 O(n) 时间，分别需 O(u) 计数空间和 O(n) 队列/输出空间。')

add(9, '链表节点同时包含值和下一节点引用，树节点包含两个子引用。节点值相同不表示对象相同。二进制链表从高位向低位读取：原值乘2再加新位；这就是位置记数法，不需要先变成字符串。',
NODES+'''
def binary_list_to_int(head):
    value=0
    while head:
        if head.val not in (0,1):
            raise ValueError('only binary digits are allowed')
        value=value*2+head.val
        head=head.next
    return value
''',
'''head=list_to_nodes([1,0,1])
rows=[]
value=0
while head:
    previous=value; value=2*value+head.val
    rows.append((head.val,previous,value)); head=head.next
show_table(['当前位','旧值','新值=2×旧值+位'],rows)''',
'''h=list_to_nodes([1,0,1])
assert binary_list_to_int(h)==5
assert binary_list_to_int(list_to_nodes([0]))==0
assert h is not h.next and h.next is not h.next.next
assert h.next.next.next is None
assert nodes_to_list(h)==[1,0,1]
assert binary_list_to_int(None)==0''',
'处理前 k 位后，value 等于这 k 位表示的整数。追加一位相当于左移一位再加0/1，归纳保持该不变量。','节点遍历 O(n) 次；固定字长按 O(n) 计，Python 大整数的逐步位操作需额外考虑位数。')

add(10, '调试先固定最小输入和期望输出，再定位第一个错误状态。前缀累加比“每次重新 sum 一个前缀”少了重复计算。函数内部重新初始化 total 和输出列表，才能保证重跑Notebook不会把上次状态叠加。',
'''def running_sum(nums: list[int]) -> list[int]:
    total=0
    output=[]
    for x in nums:
        total+=x
        output.append(total)
    return output

def test_running_sum():
    assert running_sum([1,2,3])==[1,3,6]
    assert running_sum([7])==[7]
    assert running_sum([])==[]
    assert running_sum([-2,5,-1])==[-2,3,2]
''',
'''a=[1,-2,4]
show_table(['i','输入值','前缀和'], [(i,x,y) for i,(x,y) in enumerate(zip(a,running_sum(a)))])''',
'''test_running_sum()
assert running_sum([1,2,3]) == running_sum([1,2,3])
a=[3,4]; running_sum(a); assert a==[3,4]''',
'扫描到 i 时，total 等于 nums[0:i+1] 的和；每次只新增当前元素，因此与逐前缀求和一致。','O(n) 时间，O(n) 输出空间，O(1) 辅助状态。')

add(11, '复杂度描述输入规模变化时操作数如何增长，不是给某台机器测一组毫秒数。两数和暴力法枚举 i<j，从而不漏任何不同索引对，也不重复枚举交换次序。外层各次内层长度分别为 n−1、n−2、…、0。\n\n$$\n\\sum_{i=0}^{n-1}(n-1-i)=\\frac{n(n-1)}2.\n$$',
'''def two_sum_bruteforce(nums,target):
    for i in range(len(nums)):
        for j in range(i+1,len(nums)):
            if nums[i]+nums[j]==target:
                return [i,j]
    return None

def count_pair_checks(n):
    return n*(n-1)//2
''',
'''show_table(['n','无序对次数','n²'],[(n,count_pair_checks(n),n*n) for n in [0,1,2,4,8,16]])''',
'''assert count_pair_checks(0)==count_pair_checks(1)==0
for n in range(12):
    assert count_pair_checks(n)==sum(1 for i in range(n) for j in range(i+1,n))
assert two_sum_bruteforce([2,7,11,15],9)==[0,1]
assert two_sum_bruteforce([1,2],8) is None''',
'任何两个不同索引经排序后唯一写成 i<j，因此双循环完备且不重复。找到即返回会缩短某些输入的时间，但不改变最坏二次界。','最坏 O(n²) 时间，O(1) 辅助空间，不计常数大小答案。')

add(12, '约束是筛选算法的线索，不是性能保证。n=20 的子集枚举有约百万个状态，但每状态还可能做 O(n) 工作；n=10⁵ 也可能因输入特别稀疏而使用依赖其他参数的算法。先精确统计组合数量，再乘每状态工作量，最后才考虑机器预算。',
'''def count_naive_operations(n):
    if n<0:
        raise ValueError('n must be nonnegative')
    return {'linear':n,'pairs':n*(n-1)//2,'subsets':1<<n}

def compare_growth(ns):
    return [(n,count_naive_operations(n)) for n in ns]
''',
'''show_table(['n','线性','索引对','子集'],[(n,d['linear'],d['pairs'],d['subsets']) for n,d in compare_growth([4,8,12,16,20])])''',
'''assert count_naive_operations(8)['subsets']==256
assert count_naive_operations(10)['pairs']==45
assert count_naive_operations(0)=={'linear':0,'pairs':0,'subsets':1}
for n in range(8):
    assert count_naive_operations(n)['subsets']==len(range(1<<n))''',
'每个索引独立选择取或不取，共 2ⁿ 种选择；无序对数来自上章求和。这里是操作模型，不承诺某规模一定能通过在线评测。','表格含 k 个输入规模时需要 O(k) 条记录；精确大整数表示还依赖数值位数。')

add(13, '循环不变量应同时说明“已处理部分正确”和“未处理部分仍有哪些候选”。有序数组线性插入位置：指针之前所有元素都小于 target，停止时首次遇到不小于 target 的元素。前缀最大值同样用一个变量总结已处理部分。',
'''def linear_insert_position(nums,target):
    i=0
    while i<len(nums) and nums[i]<target:
        i+=1
    return i

def prefix_max(nums):
    result=[]
    current=None
    for x in nums:
        current=x if current is None else max(current,x)
        result.append(current)
    return result
''',
'''a=[3,1,4,2,5]
show_table(['前缀','最大值'],[(a[:i+1],m) for i,m in enumerate(prefix_max(a))])''',
'''assert linear_insert_position([1,3,5],4)==2
assert linear_insert_position([1,3,5],0)==0
assert linear_insert_position([1,3,5],9)==3
assert linear_insert_position([],3)==0
a=[-4,0,-2,5]
assert prefix_max(a)==[max(a[:i+1]) for i in range(len(a))]
assert prefix_max([])==[]''',
'循环初始时已处理前缀为空，性质真；每次合法推进保留性质；有限索引严格增加保证终止。停止条件联合不变量给出第一个可插入位置。','两个算法 O(n) 时间；插入位置 O(1) 辅助空间，前缀最大值 O(n) 输出空间。')

add(14, '两个栈实现队列时不能每次出队都倒腾全部元素。仅当输出栈为空才把输入栈整体反转：最早入队的元素出现在输出栈顶。单次转移可能线性，但每个元素一生最多转移一次，所以长操作序列均摊常数。',
'''class TwoStackQueue:
    def __init__(self):
        self.incoming=[]
        self.outgoing=[]
        self.transfers=0
    def push(self,x):
        self.incoming.append(x)
    def pop(self):
        if not self.outgoing:
            while self.incoming:
                self.outgoing.append(self.incoming.pop())
                self.transfers+=1
        if not self.outgoing:
            raise IndexError('pop from empty queue')
        return self.outgoing.pop()
    def empty(self):
        return not (self.incoming or self.outgoing)

def instrumented_push_pop(ops):
    queue=TwoStackQueue()
    popped=[]
    trace=[]
    for op,value in ops:
        if op=='push': queue.push(value)
        elif op=='pop': popped.append(queue.pop())
        else: raise ValueError('unknown operation')
        trace.append((op,list(queue.incoming),list(queue.outgoing),queue.transfers))
    return popped,queue.transfers,trace
''',
'''_,_,trace=instrumented_push_pop([('push',1),('push',2),('pop',None),('push',3),('pop',None),('pop',None)])
show_table(['操作','输入栈','输出栈','累计迁移'],trace)''',
'''a,moves,_=instrumented_push_pop([('push',1),('push',2),('push',3),('pop',None),('pop',None),('pop',None)])
assert a==[1,2,3] and moves==3
q=TwoStackQueue()
for i in range(20):
    q.push(i); assert q.pop()==i
assert q.transfers==20 and q.empty()''',
'逻辑队列顺序始终是 reversed(outgoing) 接 incoming。一次批量反转后顺序不变。给每次push预付其未来迁移成本，总迁移次数不超过push次数。','m次合法操作总 O(m)，单次pop最坏 O(n)、均摊 O(1)；存储 O(n)。')

add(15, '独立参照要尽量采用不同写法。最大非空子数组的主暴力法固定左端点后逐步累计；参照用每一段切片求和。它们复杂度都很慢，却适合小输入穷举，用来发现优化算法中的边界错误。全负数组必须选一个负数，不能擅自把空数组的零加入候选。',
'''from itertools import product

def max_subarray_bruteforce(nums):
    if not nums:
        raise ValueError('requires a nonempty array')
    best=nums[0]
    for left in range(len(nums)):
        total=0
        for right in range(left,len(nums)):
            total+=nums[right]
            best=max(best,total)
    return best

def enumerate_small_arrays(values,max_len):
    for n in range(max_len+1):
        for row in product(values,repeat=n):
            yield list(row)
''',
'''a=[-2,3,-1]
show_table(['left','right（含）','区间','和'],[(l,r,a[l:r+1],sum(a[l:r+1])) for l in range(len(a)) for r in range(l,len(a))])''',
'''assert max_subarray_bruteforce([-2,-1])==-1
assert max_subarray_bruteforce([0])==0
for a in enumerate_small_arrays([-1,0,1],4):
    if a:
        ref=max(sum(a[l:r]) for l in range(len(a)) for r in range(l+1,len(a)+1))
        assert max_subarray_bruteforce(a)==ref''',
'每个非空连续区间唯一对应一组 left≤right，枚举覆盖所有候选；累计和只复用同一起点的前一段和，不改变候选值。','主暴力 O(n²) 时间、O(1) 辅助空间；切片参照 O(n³)，只用于小规模验证。')

add(16, '子数组要求连续，子序列只要求索引递增。两者可拥有同样的值序列，却对应不同索引选择。建模时先确定对象，再决定枚举空间；否则很容易把“所有连续片段”误写成“任意子集”。本章用索引保留重复元素的不同身份。',
'''def enumerate_subarrays(nums):
    return [nums[left:right] for left in range(len(nums)) for right in range(left+1,len(nums)+1)]

def enumerate_subsequences(nums):
    result=[]
    for mask in range(1<<len(nums)):
        result.append([x for i,x in enumerate(nums) if mask>>i & 1])
    return result
''',
'''a=[1,2,1]
show_table(['对象','数量','候选值序列'], [('非空子数组',len(enumerate_subarrays(a)),enumerate_subarrays(a)),('含空子序列',len(enumerate_subsequences(a)),enumerate_subsequences(a))])''',
'''for n in range(7):
    a=[1]*n
    assert len(enumerate_subarrays(a))==n*(n+1)//2
    assert len(enumerate_subsequences(a))==1<<n
assert [1,1] in enumerate_subsequences([1,2,1])
assert [1,1] not in enumerate_subarrays([1,2,1])''',
'子数组由两个端点确定；子序列由每个索引的二元选择确定。输出中保留重复值列表是有意的，因为计数按索引而不是按值去重。','显式复制全部子数组总 O(n³) 元素输出；全部子序列 O(n2ⁿ) 时间和输出空间。')
