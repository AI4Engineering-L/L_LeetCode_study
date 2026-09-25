from course_builder import add, NODES

add(51, '栈保存尚未被后续输入解释完的前缀。括号右端只能匹配最近尚未闭合的左端；路径中的`..`取消最近一级目录；相邻重复删除可以不断取消栈顶。它们共同点是“最近未完成对象优先”，但输入契约不同，不能混用字符规则。',
'''def is_valid_parentheses(s):
    stack=[]; pairs={')':'(',']':'[','}':'{'}
    for c in s:
        if c in '([{': stack.append(c)
        elif c in pairs:
            if not stack or stack.pop()!=pairs[c]: return False
        else: return False
    return not stack

def simplify_path(path):
    if not path.startswith('/'): raise ValueError('absolute Unix path required')
    stack=[]
    for part in path.split('/'):
        if part in ('','.'): continue
        if part=='..':
            if stack: stack.pop()
        else: stack.append(part)
    return '/'+ '/'.join(stack)

def remove_adjacent_duplicates(s):
    stack=[]
    for c in s:
        if stack and stack[-1]==c: stack.pop()
        else: stack.append(c)
    return ''.join(stack)
''',
'''s='abbaca'; stack=[]; rows=[]
for c in s:
    if stack and stack[-1]==c: stack.pop()
    else: stack.append(c)
    rows.append((c,''.join(stack)))
show_table(['新字符','归约后前缀'],rows)''',
'''assert is_valid_parentheses('()[]{}')
assert not is_valid_parentheses('([)]')
assert is_valid_parentheses('') and not is_valid_parentheses('(')
assert simplify_path('/a/./b/../../c/')=='/c'
assert simplify_path('////../')=='/'
assert simplify_path('/.../a/..')=='/...'
assert remove_adjacent_duplicates('abbaca')=='ca'
assert remove_adjacent_duplicates('aaaa')=='' ''',
'栈始终代表已读前缀中不能再直接归约的部分；新的闭合或取消操作只可能影响栈顶。括号最终栈空才表示每个左端都有匹配右端。','O(n)时间、O(n)最坏辅助空间。路径处理是字符串规范化，不访问文件系统或符号链接。')

add(52, '表达式解析应先定义语法：expression处理加减，term处理乘除，factor处理一元正负、整数和括号。这样优先级由调用结构保证，不依赖碰巧的扫描顺序。逆波兰表达式则把子表达式结果压栈。整数除法向零截断，不能直接用Python的负数整除，也不要转float以免大整数精度损失。',
'''def trunc_div(a,b):
    if b==0: raise ZeroDivisionError('division by zero')
    value=abs(a)//abs(b)
    return -value if (a<0) != (b<0) else value

def eval_rpn(tokens):
    stack=[]
    for token in tokens:
        if token not in ('+','-','*','/'):
            stack.append(int(token)); continue
        b=stack.pop(); a=stack.pop()
        stack.append(a+b if token=='+' else a-b if token=='-' else a*b if token=='*' else trunc_div(a,b))
    if len(stack)!=1: raise ValueError('malformed expression')
    return stack[0]

class _Parser:
    def __init__(self,s,allow_mul): self.s=s; self.i=0; self.allow_mul=allow_mul
    def peek(self):
        while self.i<len(self.s) and self.s[self.i].isspace(): self.i+=1
        return self.s[self.i] if self.i<len(self.s) else None
    def factor(self):
        c=self.peek()
        if c in ('+','-'):
            self.i+=1; value=self.factor(); return -value if c=='-' else value
        if c=='(':
            self.i+=1; value=self.expression()
            if self.peek()!=')': raise ValueError('missing closing parenthesis')
            self.i+=1; return value
        if c is None or not '0'<=c<='9': raise ValueError('expected integer')
        value=0
        while self.i<len(self.s) and '0'<=self.s[self.i]<='9':
            value=value*10+int(self.s[self.i]); self.i+=1
        return value
    def term(self):
        value=self.factor()
        while self.allow_mul and self.peek() in ('*','/'):
            op=self.peek(); self.i+=1; other=self.factor()
            value=value*other if op=='*' else trunc_div(value,other)
        return value
    def expression(self):
        value=self.term()
        while self.peek() in ('+','-'):
            op=self.peek(); self.i+=1; other=self.term()
            value=value+other if op=='+' else value-other
        return value
    def parse(self):
        value=self.expression()
        if self.peek() is not None: raise ValueError('unconsumed input')
        return value

def calculate_basic(s): return _Parser(s,False).parse()
def calculate_precedence(s): return _Parser(s,True).parse()
''',
'''tokens=['2','1','+','3','*']; stack=[]; rows=[]
for t in tokens:
    if t not in ('+','*'): stack.append(int(t))
    else:
        b=stack.pop(); a=stack.pop(); stack.append(a+b if t=='+' else a*b)
    rows.append((t,stack[:]))
show_table(['token','值栈'],rows)''',
'''assert eval_rpn(['2','1','+','3','*'])==9
assert calculate_precedence('3+2*2')==7
assert calculate_precedence('-3/2')==-1
assert calculate_basic('1-(2-(3+4))')==6
assert calculate_precedence('(12+8)/3*2')==12
assert trunc_div(-(10**30+1),3)==-((10**30+1)//3)
for a in range(-4,5):
    for b in range(-4,5):
        assert calculate_basic(f'({a})-({b})')==a-b
        assert calculate_precedence(f'({a})*({b})+3')==a*b+3''',
'每个解析函数消费且仅消费其语法层级的一个合法表达式；factor保证括号成为不可分的操作数，term先完成乘除，expression再合并加减。','O(n)字符扫描；值大小固定时O(n)时间，嵌套或一元链最坏O(n)递归空间。深度极大时应改为显式栈。')

add(53, '循环缓冲区用固定数组和模运算复用已释放位置，避免每次出队整体搬移。必须额外记录size或留空槽来区分“头尾相同”的空与满；这里选择size。双端队列允许从两端插删，普通队列只是限制其中两种操作。容量必须为正。',
'''class CircularDeque:
    def __init__(self,k):
        if k<1: raise ValueError('positive capacity required')
        self.data=[None]*k; self.head=0; self.size=0
    def isEmpty(self): return self.size==0
    def isFull(self): return self.size==len(self.data)
    def insertFront(self,value):
        if self.isFull(): return False
        self.head=(self.head-1)%len(self.data)
        self.data[self.head]=value; self.size+=1; return True
    def insertLast(self,value):
        if self.isFull(): return False
        self.data[(self.head+self.size)%len(self.data)]=value
        self.size+=1; return True
    def deleteFront(self):
        if self.isEmpty(): return False
        self.data[self.head]=None; self.head=(self.head+1)%len(self.data)
        self.size-=1; return True
    def deleteLast(self):
        if self.isEmpty(): return False
        self.size-=1; self.data[(self.head+self.size)%len(self.data)]=None; return True
    def getFront(self): return -1 if self.isEmpty() else self.data[self.head]
    def getRear(self): return -1 if self.isEmpty() else self.data[(self.head+self.size-1)%len(self.data)]

class CircularQueue(CircularDeque):
    enQueue=CircularDeque.insertLast
    deQueue=CircularDeque.deleteFront
    Front=CircularDeque.getFront
    Rear=CircularDeque.getRear

class TwoStackQueue:
    def __init__(self): self.incoming=[]; self.outgoing=[]
    def push(self,x): self.incoming.append(x)
    def pop(self):
        if not self.outgoing:
            while self.incoming: self.outgoing.append(self.incoming.pop())
        if not self.outgoing: raise IndexError('empty queue')
        return self.outgoing.pop()
''',
'''q=CircularQueue(3); rows=[]
for op,value in [('put',1),('put',2),('get',None),('put',3),('put',4),('get',None)]:
    if op=='put': q.enQueue(value)
    else: q.deQueue()
    rows.append((op,value,q.head,q.size,q.data[:]))
show_table(['操作','值','head','size','物理数组'],rows)''',
'''from collections import deque
from random import Random
q=CircularQueue(1); assert q.enQueue(7) and not q.enQueue(8)
assert q.Front()==q.Rear()==7 and q.deQueue() and not q.deQueue()
rng=Random(53); q=CircularDeque(5); ref=deque()
for _ in range(1000):
    op=rng.randrange(4); x=rng.randrange(20)
    if op<2:
        expected=len(ref)<5
        actual=q.insertFront(x) if op==0 else q.insertLast(x)
        if expected:
            if op==0: ref.appendleft(x)
            else: ref.append(x)
    else:
        expected=bool(ref); actual=q.deleteFront() if op==2 else q.deleteLast()
        if expected:
            if op==2: ref.popleft()
            else: ref.pop()
    assert actual==expected
    assert q.size==len(ref) and q.getFront()==(ref[0] if ref else -1) and q.getRear()==(ref[-1] if ref else -1)
t=TwoStackQueue()
for x in range(5): t.push(x)
assert [t.pop() for _ in range(5)]==list(range(5))''',
'第i个逻辑元素总位于(head+i) mod capacity。四种操作只改变端点位置与size，按这个映射核对即可证明顺序不变。','循环队列各操作最坏O(1)，空间O(capacity)；双栈队列单次最坏O(n)、均摊O(1)。')

add(54, '单调栈保存“还没找到答案”的索引，而不是所有历史值。新温度更高时，它就是所有被弹出日子的第一个更暖日：如果中间曾经更暖，那个索引早已被弹出。环形数组扫描两圈模拟跨尾，但只在第一圈入栈，避免同一索引重复入栈。',
'''def daily_temperatures(t):
    stack=[]; answer=[0]*len(t)
    for i,x in enumerate(t):
        while stack and t[stack[-1]]<x:
            j=stack.pop(); answer[j]=i-j
        stack.append(i)
    return answer

def next_greater_circular(nums):
    n=len(nums); answer=[-1]*n; stack=[]
    for i in range(2*n):
        x=nums[i%n]
        while stack and nums[stack[-1]]<x: answer[stack.pop()]=x
        if i<n: stack.append(i)
    return answer
''',
'''t=[73,74,75,71,69,72,76,73]; stack=[]; rows=[]
for i,x in enumerate(t):
    popped=[]
    while stack and t[stack[-1]]<x: popped.append(stack.pop())
    stack.append(i); rows.append((i,x,popped,stack[:]))
show_table(['i','温度','本次解决的索引','尚待解决栈'],rows)''',
'''assert daily_temperatures([73,74,75,71,69,72,76,73])==[1,1,4,2,1,1,0,0]
assert daily_temperatures([5,5,5])==[0,0,0]
assert next_greater_circular([1,2,1])==[2,-1,2]
from itertools import product
for n in range(6):
    for a in product([0,1,2],repeat=n):
        ref=[]
        for i in range(n): ref.append(next((a[(i+d)%n] for d in range(1,n) if a[(i+d)%n]>a[i]),-1))
        assert next_greater_circular(a)==ref''',
'栈值非递增，栈内索引递增。弹出的每个元素此前没有更大值，现在首次遇到；每索引仅入栈一次、出栈至多一次。','O(n)时间、O(n)空间；严格更大不能写成大于等于。')

add(55, '直方图中把每根柱作为最低高度，最大可延伸边界由左右最近更矮柱确定。弹栈时右边界刚刚出现。子数组最小值和则按“哪个索引负责这个区间的最小值”分摊贡献；重复值必须在左右边界一侧严格、一侧非严格，才能既不重计也不漏计。',
'''def largest_rectangle(heights):
    stack=[]; best=0
    for i,h in enumerate([*heights,0]):
        while stack and heights[stack[-1]]>h:
            j=stack.pop(); left=stack[-1] if stack else -1
            best=max(best,heights[j]*(i-left-1))
        stack.append(i)
    return best

def sum_subarray_mins(nums,mod=10**9+7):
    stack=[]; total=0
    for i in range(len(nums)+1):
        while stack and (i==len(nums) or nums[stack[-1]]>=nums[i]):
            j=stack.pop(); left=stack[-1] if stack else -1
            total+=nums[j]*(j-left)*(i-j)
        stack.append(i)
    return total%mod
''',
'''a=[3,1,2,4]; stack=[]; rows=[]
for i in range(len(a)+1):
    while stack and (i==len(a) or a[stack[-1]]>=a[i]):
        j=stack.pop(); left=stack[-1] if stack else -1
        rows.append((j,a[j],left,i,(j-left)*(i-j),a[j]*(j-left)*(i-j)))
    stack.append(i)
show_table(['负责索引','值','左严格小边界','右小于等于边界','区间数','贡献'],rows)''',
'''assert largest_rectangle([2,1,5,6,2,3])==10
assert sum_subarray_mins([3,1,2,4])==17
from itertools import product
for n in range(7):
    for a in product([0,1,2],repeat=n):
        best=max((min(a[l:r])*(r-l) for l in range(n) for r in range(l+1,n+1)),default=0)
        total=sum(min(a[l:r]) for l in range(n) for r in range(l+1,n+1))
        assert largest_rectangle(a)==best and sum_subarray_mins(a)==total''',
'每个弹出索引的左右障碍界定了它可担任最低值的最大范围。最小值计数规则把重复最小值交给最右出现者，左端有j−left种、右端有i−j种选择。','O(n)时间、O(n)栈空间；直方图高度非负；最小值和默认按10⁹+7取模。')

add(56, '滑窗最大值保留可能成为未来最大值的索引：一个更早且不更大的值可永久删除，因为它先过期且不占优势。含负数的最短区间不能靠“和太小就右扩”的普通窗口；改看前缀差，在递增前缀队列上分别处理“已经达到阈值”和“被新前缀支配”。',
'''from collections import deque

def max_sliding_window(nums,k):
    if not nums: return []
    if not 1<=k<=len(nums): raise ValueError('invalid window size')
    queue=deque(); answer=[]
    for i,x in enumerate(nums):
        while queue and queue[0]<=i-k: queue.popleft()
        while queue and nums[queue[-1]]<=x: queue.pop()
        queue.append(i)
        if i>=k-1: answer.append(nums[queue[0]])
    return answer

def shortest_subarray(nums,k):
    prefix=[0]
    for x in nums: prefix.append(prefix[-1]+x)
    queue=deque(); best=len(nums)+1
    for i,value in enumerate(prefix):
        while queue and value-prefix[queue[0]]>=k: best=min(best,i-queue.popleft())
        while queue and prefix[queue[-1]]>=value: queue.pop()
        queue.append(i)
    return best if best<=len(nums) else -1
''',
'''a=[2,-1,2]; p=[0]
for x in a: p.append(p[-1]+x)
q=deque(); rows=[]
for i,v in enumerate(p):
    solved=[]
    while q and v-p[q[0]]>=3: solved.append((q[0],i,i-q[0])); q.popleft()
    while q and p[q[-1]]>=v: q.pop()
    q.append(i); rows.append((i,v,list(q),solved))
show_table(['i','P[i]','候选左前缀','本次可行区间'],rows)''',
'''assert max_sliding_window([1,3,-1,-3,5,3,6,7],3)==[3,3,5,5,6,7]
assert shortest_subarray([2,-1,2],3)==3
assert shortest_subarray([1,2],9)==-1
from itertools import product
for n in range(6):
    for a in product([-1,0,2],repeat=n):
        for k in range(1,5):
            lengths=[r-l for l in range(n) for r in range(l+1,n+1) if sum(a[l:r])>=k]
            assert shortest_subarray(a,k)==(min(lengths) if lengths else -1)
        for k in range(1,n+1): assert max_sliding_window(a,k)==[max(a[i:i+k]) for i in range(n-k+1)]''',
'更晚且前缀更小的索引，对任意未来右端都给出不更难满足的和与更短长度，支配旧索引。队首一旦已可行，其最短可用右端已检查，未来只会更长。','两个算法 O(n)时间；窗口最大O(k)辅助空间，前缀最短区间O(n)。')

HEAP='''def heapify_bottom_up(a):
    def sift(i):
        while 2*i+1<len(a):
            child=2*i+1
            if child+1<len(a) and a[child+1]<a[child]: child+=1
            if a[i]<=a[child]: break
            a[i],a[child]=a[child],a[i]; i=child
    for i in range(len(a)//2-1,-1,-1): sift(i)
    return a

class MinHeap:
    def __init__(self,values=()): self.data=heapify_bottom_up(list(values))
    def push(self,x):
        self.data.append(x); i=len(self.data)-1
        while i and self.data[i]<self.data[(i-1)//2]:
            p=(i-1)//2; self.data[i],self.data[p]=self.data[p],self.data[i]; i=p
    def pop(self):
        if not self.data: raise IndexError('empty heap')
        answer=self.data[0]; last=self.data.pop()
        if self.data:
            self.data[0]=last; i=0
            while 2*i+1<len(self.data):
                c=2*i+1
                if c+1<len(self.data) and self.data[c+1]<self.data[c]: c+=1
                if self.data[i]<=self.data[c]: break
                self.data[i],self.data[c]=self.data[c],self.data[i]; i=c
        return answer
'''
add(57, '完全二叉树按数组顺序存储，i的孩子是2i+1与2i+2。插入只可能破坏祖先链，删除堆顶只可能破坏向下路径。自底向上建堆比逐个插入更便宜，因为多数节点靠近叶子，实际下沉距离很短。',
HEAP+'''
def last_stone_weight(stones):
    heap=MinHeap(-x for x in stones)
    while len(heap.data)>1:
        a=-heap.pop(); b=-heap.pop()
        if a!=b: heap.push(-(a-b))
    return -heap.pop() if heap.data else 0
''',
'''h=MinHeap(); rows=[]
for x in [5,2,7,1,3]:
    h.push(x); rows.append((x,h.data[:]))
show_table(['插入值','堆数组'],rows)
show_table(['数组索引','父索引','值'],[(i,(i-1)//2 if i else None,v) for i,v in enumerate(h.data)])''',
'''import heapq
from random import Random
rng=Random(57); h=MinHeap(); ref=[]
for _ in range(1000):
    if not ref or rng.randrange(3):
        x=rng.randrange(-50,51); h.push(x); heapq.heappush(ref,x)
    else: assert h.pop()==heapq.heappop(ref)
    assert all(h.data[(i-1)//2]<=h.data[i] for i in range(1,len(h.data)))
assert [h.pop() for _ in range(len(h.data))]==sorted(ref)
assert last_stone_weight([2,7,4,1,8,1])==1
assert last_stone_weight([3])==3''',
'子堆先合法，sift选择较小孩子交换，只需继续修复被替换的子树。高度h的节点数量约n/2^(h+1)，总下沉工作Σh·n/2^(h+1)=O(n)。','建堆O(n)，push/pop最坏O(log n)，空间O(n)；石头模拟O(n log n)。')

add(58, '维护最大的k个值时，最需要知道的是这k个候选中最小的那个，因此使用大小k的最小堆。新值不大于堆顶就不可能挤进前k。高频元素先计数再选k个键，不能把相同频次误认为答案唯一。本章为稳定展示，频次并列时取数值较小者。',
'''import heapq
from collections import Counter

def kth_largest_heap(nums,k):
    if not 1<=k<=len(nums): raise ValueError('invalid rank')
    heap=[]
    for x in nums:
        if len(heap)<k: heapq.heappush(heap,x)
        elif x>heap[0]: heapq.heapreplace(heap,x)
    return heap[0]

def top_k_frequent(nums,k):
    counts=Counter(nums)
    if not 0<=k<=len(counts): raise ValueError('invalid number of distinct keys')
    return heapq.nlargest(k,counts,key=lambda x:(counts[x],-x))

class KthLargest:
    def __init__(self,k,nums):
        if k<1: raise ValueError('positive k required')
        self.k=k; self.heap=[]
        for x in nums: self.add(x)
    def add(self,value):
        heapq.heappush(self.heap,value)
        if len(self.heap)>self.k: heapq.heappop(self.heap)
        return self.heap[0]
''',
'''stream=KthLargest(3,[4,5,8,2]); rows=[]
for x in [3,5,10,9,4]:
    result=stream.add(x); rows.append((x,sorted(stream.heap),result))
show_table(['新值','保留的Top3','第3大'],rows)''',
'''assert kth_largest_heap([3,2,1,5,6,4],2)==5
assert set(top_k_frequent([1,1,1,2,2,3],2))=={1,2}
stream=KthLargest(3,[4,5,8,2]); assert [stream.add(x) for x in [3,5,10,9,4]]==[4,5,5,8,8]
from random import Random
rng=Random(58)
for k in range(1,8):
    seen=[]; stream=KthLargest(k,[])
    for _ in range(40):
        x=rng.randrange(20); seen.append(x)
        answer=stream.add(x)
        assert answer==sorted(seen)[-min(k,len(seen))]''',
'对输入前缀归纳：堆保存其最大的min(k,t)个元素；插入后删除最小者仍保留该集合。流长度不足k时本章返回当前最小值，并不称它为已存在的“第k大”。','Top-k扫描O(n log k)、O(k)空间；频次版O(n+u log k)、O(u)空间。')

add(59, '多个有序流的全局最小值一定在某个流的当前头部。堆只需放每个流一个候选，取走后从同一流补充。两个有序数组的数对和可以把每个a[i]与整个b配对看成一条有序流。相同优先级要加可比较的索引，不能让Python继续比较节点对象。',
NODES+'''
import heapq

def merge_k_lists(lists):
    heap=[(node.val,i,node) for i,node in enumerate(lists) if node]
    heapq.heapify(heap); dummy=tail=ListNode()
    while heap:
        _,i,node=heapq.heappop(heap)
        following=node.next
        tail.next=node; tail=node
        if following: heapq.heappush(heap,(following.val,i,following))
    if tail is not dummy: tail.next=None
    return dummy.next

def k_smallest_pairs(a,b,k):
    if not a or not b or k<=0: return []
    heap=[(a[i]+b[0],i,0) for i in range(min(k,len(a)))]; heapq.heapify(heap)
    out=[]
    while heap and len(out)<k:
        _,i,j=heapq.heappop(heap); out.append([a[i],b[j]])
        if j+1<len(b): heapq.heappush(heap,(a[i]+b[j+1],i,j+1))
    return out
''',
'''a=[1,7,11]; b=[2,4,6]; pairs=k_smallest_pairs(a,b,6)
show_table(['弹出次序','数对','和'],[(i,p,sum(p)) for i,p in enumerate(pairs,1)])''',
'''h=merge_k_lists([list_to_nodes([1,4,5]),None,list_to_nodes([1,3,4]),list_to_nodes([2,6])])
assert nodes_to_list(h)==[1,1,2,3,4,4,5,6]
assert merge_k_lists([]) is None
from itertools import combinations_with_replacement
for a in combinations_with_replacement([0,1,2],3):
    for b in combinations_with_replacement([0,1,2],2):
        all_sums=sorted(x+y for x in a for y in b)
        for k in range(8):
            out=k_smallest_pairs(a,b,k)
            assert [sum(p) for p in out]==all_sums[:k]
            assert all(x in a and y in b for x,y in out)''',
'每条流中未暴露元素不小于当前头部，因此堆顶是所有未输出候选中的最小值。只初始化前k行已经足够：更后行首不小于前k行首，无法成为严格更优的前k项。','K路归并总N节点需O(N log K)时间/O(K)堆空间；数对输出q=min(k,mn)，时间O(q log min(k,m))。')

add(60, '中位数只需要分隔较小一半与较大一半：小半用最大堆，大半用最小堆。滑动窗口删除的元素可能不在堆顶，不能用线性查找假装O(log k)。延迟删除按值计数，并分别维护逻辑有效大小；访问或移动堆顶前清理失效项。物理堆含过期元素，本实现最坏空间可达O(n)，不是无条件O(k)。',
'''import heapq
from collections import Counter

class MedianFinder:
    def __init__(self): self.low=[]; self.high=[]
    def addNum(self,x):
        heapq.heappush(self.low,-x)
        heapq.heappush(self.high,-heapq.heappop(self.low))
        if len(self.high)>len(self.low): heapq.heappush(self.low,-heapq.heappop(self.high))
    def findMedian(self):
        if not self.low: raise ValueError('no observations')
        return -self.low[0] if len(self.low)>len(self.high) else (-self.low[0]+self.high[0])/2

class _WindowMedian:
    def __init__(self):
        self.low=[]; self.high=[]; self.delayed=Counter(); self.nl=self.nh=0
    def prune(self,heap,sign):
        while heap and self.delayed[sign*heap[0]]:
            x=sign*heapq.heappop(heap); self.delayed[x]-=1
            if not self.delayed[x]: del self.delayed[x]
    def balance(self):
        if self.nl>self.nh+1:
            heapq.heappush(self.high,-heapq.heappop(self.low)); self.nl-=1; self.nh+=1
            self.prune(self.low,-1)
        elif self.nl<self.nh:
            heapq.heappush(self.low,-heapq.heappop(self.high)); self.nl+=1; self.nh-=1
            self.prune(self.high,1)
    def add(self,x):
        if not self.low or x<=-self.low[0]: heapq.heappush(self.low,-x); self.nl+=1
        else: heapq.heappush(self.high,x); self.nh+=1
        self.balance()
    def remove(self,x):
        self.delayed[x]+=1
        if x<=-self.low[0]:
            self.nl-=1
            if x==-self.low[0]: self.prune(self.low,-1)
        else:
            self.nh-=1
            if self.high and x==self.high[0]: self.prune(self.high,1)
        self.balance()
    def median(self):
        return -self.low[0] if self.nl>self.nh else (-self.low[0]+self.high[0])/2

def sliding_window_median(nums,k):
    if not 1<=k<=len(nums): raise ValueError('invalid window size')
    state=_WindowMedian(); out=[]
    for x in nums[:k]: state.add(x)
    out.append(state.median())
    for i in range(k,len(nums)):
        state.add(nums[i]); state.remove(nums[i-k]); out.append(state.median())
    return out
''',
'''m=MedianFinder(); rows=[]
for x in [1,2,3,9,0,5]:
    m.addNum(x); rows.append((x,sorted(-v for v in m.low),sorted(m.high),m.findMedian()))
show_table(['新值','较小一半','较大一半','中位数'],rows)''',
'''from statistics import median
from random import Random
m=MedianFinder(); m.addNum(1); m.addNum(2); assert m.findMedian()==1.5
m.addNum(3); assert m.findMedian()==2
rng=Random(60)
for n in range(1,35):
    for a in [[3]*n,list(range(n)),list(range(n,0,-1)),[rng.randrange(-3,4) for _ in range(n)]]:
        for k in range(1,n+1): assert sliding_window_median(a,k)==[median(a[i:i+k]) for i in range(n-k+1)]''',
'两半有效元素保持low≤high且大小差为0或1，中位数由边界直接决定。失效元素只在到达顶端时移除，逻辑大小先减，不能拿物理len代替逻辑计数。','在线插入O(log n)时间/O(n)空间。延迟滑窗每项入出堆至多常数次，本实现保守界O(n log n)时间/O(n)空间；定期重建可进一步约束空间。')

add(61, '调度题区分“当前可用资源”和“未来释放事件”。单线程CPU把已到达任务按处理时间、原索引入堆；没有可运行任务时直接跳到下次到达时刻，不逐秒模拟。服务器分配用两个堆：可用堆按权重与索引排序，忙碌堆按释放时间排序。',
'''import heapq

def single_threaded_order(tasks):
    pending=sorted((start,duration,i) for i,(start,duration) in enumerate(tasks))
    ready=[]; i=0; now=0; out=[]
    while i<len(pending) or ready:
        if not ready: now=max(now,pending[i][0])
        while i<len(pending) and pending[i][0]<=now:
            start,duration,index=pending[i]; heapq.heappush(ready,(duration,index)); i+=1
        duration,index=heapq.heappop(ready); out.append(index); now+=duration
    return out

def assign_tasks(servers,tasks):
    if not servers and tasks: raise ValueError('at least one server required')
    available=[(weight,i) for i,weight in enumerate(servers)]; heapq.heapify(available)
    busy=[]; now=0; out=[]
    for arrival,duration in enumerate(tasks):
        now=max(now,arrival)
        if not available and busy: now=max(now,busy[0][0])
        while busy and busy[0][0]<=now:
            _,weight,index=heapq.heappop(busy); heapq.heappush(available,(weight,index))
        weight,index=heapq.heappop(available); out.append(index)
        heapq.heappush(busy,(now+duration,weight,index))
    return out
''',
'''tasks=[[1,2],[2,4],[3,2],[4,1]]; order=single_threaded_order(tasks)
show_table(['执行次序','任务索引','到达','处理时长'],[(j,i,*tasks[i]) for j,i in enumerate(order)])
show_table(['任务到达时刻','分配服务器'],list(enumerate(assign_tasks([3,3,2],[1,2,3,2,1,2]))))''',
'''assert single_threaded_order([[1,2],[2,4],[3,2],[4,1]])==[0,2,3,1]
assert single_threaded_order([[100,2],[1000,1]])==[0,1]
assert assign_tasks([3,3,2],[1,2,3,2,1,2])==[2,2,0,2,1,2]
from random import Random
rng=Random(61)
for _ in range(200):
    weights=[rng.randrange(1,5) for _ in range(rng.randrange(1,5))]
    tasks=[rng.randrange(1,8) for _ in range(15)]; free=[0]*len(weights); now=0; ref=[]
    for arrival,duration in enumerate(tasks):
        now=max(now,arrival)
        if all(t>now for t in free): now=min(free)
        i=min((i for i,t in enumerate(free) if t<=now),key=lambda i:(weights[i],i))
        ref.append(i); free[i]=now+duration
    assert assign_tasks(weights,tasks)==ref''',
'事件时刻之间没有候选集合变化，直接跳跃不会改变决策。每次分配前释放所有已到期资源，再用完整并列规则取堆顶，与逐资源扫描定义一致。','CPU调度O(n log n)时间/O(n)空间；服务器调度O((n+m)log m)时间/O(m)工作空间，不计输出。')
