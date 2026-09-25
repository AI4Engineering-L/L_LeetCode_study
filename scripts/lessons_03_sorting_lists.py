from course_builder import add, NODES

add(37, '排序的第一步不是背交换语句，而是定义每轮已完成的部分。插入排序维护有序前缀，把新元素插入其中；选择排序每轮选择剩余最小值；冒泡排序让当前最大值逐步到达末尾。稳定性要求相等键保留原来先后顺序，所以插入和冒泡只在严格大于时移动。',
'''def insertion_sort(a,key=lambda x:x):
    for i in range(1,len(a)):
        value=a[i]; j=i
        while j>0 and key(a[j-1])>key(value):
            a[j]=a[j-1]; j-=1
        a[j]=value
    return a

def selection_sort(a,key=lambda x:x):
    for i in range(len(a)):
        best=i
        for j in range(i+1,len(a)):
            if key(a[j])<key(a[best]): best=j
        a[i],a[best]=a[best],a[i]
    return a

def bubble_sort(a,key=lambda x:x):
    for end in range(len(a)-1,0,-1):
        changed=False
        for i in range(end):
            if key(a[i])>key(a[i+1]):
                a[i],a[i+1]=a[i+1],a[i]; changed=True
        if not changed: break
    return a
''',
'''a=[4,2,3,1]; rows=[('初始',a[:])]
for i in range(1,len(a)):
    value=a[i]; j=i
    while j>0 and a[j-1]>value: a[j]=a[j-1]; j-=1
    a[j]=value; rows.append((f'插入第{i}项',a[:]))
show_table(['阶段','数组'],rows)''',
'''from itertools import product
for n in range(7):
    for a in product([-1,0,1],repeat=n):
        for fn in [insertion_sort,selection_sort,bubble_sort]: assert fn(list(a))==sorted(a)
a=[(2,'a'),(1,'b'),(2,'c'),(1,'d')]
for fn in [insertion_sort,bubble_sort]:
    assert fn(a[:],key=lambda x:x[0])==[(1,'b'),(1,'d'),(2,'a'),(2,'c')]''',
'每轮保持已排序区域不变量并扩大一区域；最终覆盖全数组。选择排序交换远距离元素，通常不稳定；不要因为样例未暴露就称其稳定。','最坏均 O(n²)，辅助空间 O(1)；插入与优化冒泡在已排序输入上 O(n)。比较排序一般下界为 Ω(n log n)，是对所有输入的最坏情形而言。')

add(38, '归并排序先递归排序两半，再用两个指针线性合并。若右值先被取走，则尚未取走的左半值都比它大，一次贡献左半剩余长度个逆序对。翻转对条件是 a[i]>2a[j]，不能直接复用普通逆序数量；在合并前单独做单调扫描。',
'''def merge_sort(a):
    if len(a)<2: return list(a)
    mid=len(a)//2; left=merge_sort(a[:mid]); right=merge_sort(a[mid:])
    out=[]; i=j=0
    while i<len(left) and j<len(right):
        if left[i]<=right[j]: out.append(left[i]); i+=1
        else: out.append(right[j]); j+=1
    return out+left[i:]+right[j:]

def _count_pairs(a,factor):
    if len(a)<2: return list(a),0
    mid=len(a)//2
    left,count1=_count_pairs(a[:mid],factor)
    right,count2=_count_pairs(a[mid:],factor)
    count=count1+count2; j=0
    for x in left:
        while j<len(right) and x>factor*right[j]: j+=1
        count+=j
    out=[]; i=j=0
    while i<len(left) and j<len(right):
        if left[i]<=right[j]: out.append(left[i]); i+=1
        else: out.append(right[j]); j+=1
    return out+left[i:]+right[j:],count

def count_inversions(a): return _count_pairs(a,1)[1]
def reverse_pairs(a): return _count_pairs(a,2)[1]
''',
'''a=[1,3,2,3,1]
show_table(['i','j','a[i]','a[j]','普通逆序','翻转对'],[(i,j,a[i],a[j],a[i]>a[j],a[i]>2*a[j]) for i in range(len(a)) for j in range(i+1,len(a))])''',
'''assert count_inversions([3,1,2])==2
assert reverse_pairs([1,3,2,3,1])==2
from itertools import product
for n in range(6):
    for a in product([-2,-1,0,1,2],repeat=n):
        assert merge_sort(a)==sorted(a)
        assert count_inversions(a)==sum(a[i]>a[j] for i in range(n) for j in range(i+1,n))
        assert reverse_pairs(a)==sum(a[i]>2*a[j] for i in range(n) for j in range(i+1,n))''',
'索引对唯一分为左半内部、右半内部、跨两半三类。因factor为正，右半有序使满足x>factor*y的y构成前缀；x递增时此前缀不缩短。','三种主算法 O(n log n) 时间、O(n) 峰值辅助空间及 O(log n) 递归深度。')

add(39, '重复值会让朴素二路快排产生不必要递归。三路划分维护“小于pivot、等于pivot、尚未处理、大于pivot”四段。遇到大值与未处理区末尾交换后，当前位置的新元素仍未分类，不能递增扫描指针。本章显式栈避免Python递归深度问题。',
'''def partition3(a,lo,hi):
    """Partition half-open [lo, hi); return equal block [lt, gt)."""
    if not 0<=lo<hi<=len(a): raise ValueError('requires nonempty valid range')
    pivot=a[lo]; lt=i=lo; gt=hi
    while i<gt:
        if a[i]<pivot:
            a[lt],a[i]=a[i],a[lt]; lt+=1; i+=1
        elif a[i]>pivot:
            gt-=1; a[gt],a[i]=a[i],a[gt]
        else: i+=1
    return lt,gt

def quicksort(a,rng):
    stack=[(0,len(a))]
    while stack:
        lo,hi=stack.pop()
        if hi-lo<2: continue
        p=rng.randrange(lo,hi); a[lo],a[p]=a[p],a[lo]
        lt,gt=partition3(a,lo,hi)
        stack.append((lo,lt)); stack.append((gt,hi))
    return a
''',
'''a=[3,1,3,5,2,3,4]; original=a[:]; lt,gt=partition3(a,0,len(a))
show_table(['原数组','<pivot','=pivot','>pivot'],[(original,a[:lt],a[lt:gt],a[gt:])])''',
'''from random import Random
from collections import Counter
rng=Random(39)
for n in range(80):
    a=[rng.randrange(-3,4) for _ in range(n)]
    assert quicksort(a[:],Random(7))==sorted(a)
    if a:
        b=a[:]; pivot=b[0]; lt,gt=partition3(b,0,n)
        assert all(x<pivot for x in b[:lt]) and all(x==pivot for x in b[lt:gt]) and all(x>pivot for x in b[gt:])
        assert Counter(a)==Counter(b)
assert quicksort([2]*1000,Random(1))==[2]*1000''',
'每次循环使未处理区长度减少1，并维持已分类区关系；划分后只需排序小于和大于两段。随机pivot不改变正确性，只影响复杂度分布。','随机独立pivot下期望 O(n log n)，最坏 O(n²)；显式栈最坏 O(n)，原地划分 O(1)。')

add(40, '堆排序只要求父节点不小于子节点，不要求整段有序。建好最大堆后，把堆顶交换到末尾，再修复缩小的堆。非比较排序利用额外值域结构：计数排序依赖值域R；基数排序按低位到高位做稳定分桶。禁止对巨大稀疏值域无条件分配数组。',
'''def heap_sort(a):
    def sift(root,size):
        while 2*root+1<size:
            child=2*root+1
            if child+1<size and a[child+1]>a[child]: child+=1
            if a[root]>=a[child]: break
            a[root],a[child]=a[child],a[root]; root=child
    for i in range(len(a)//2-1,-1,-1): sift(i,len(a))
    for end in range(len(a)-1,0,-1):
        a[0],a[end]=a[end],a[0]; sift(0,end)
    return a

def counting_sort(a,key=lambda x:x,max_range=1000000):
    if not a: return []
    low=min(map(key,a)); high=max(map(key,a)); width=high-low+1
    if width>max_range: raise ValueError('value range too large for counting sort')
    counts=[0]*width
    for x in a: counts[key(x)-low]+=1
    for i in range(1,width): counts[i]+=counts[i-1]
    out=[None]*len(a)
    for x in reversed(a):
        i=key(x)-low; counts[i]-=1; out[counts[i]]=x
    return out

def radix_sort_nonnegative(a):
    if any(x<0 for x in a): raise ValueError('nonnegative integers required')
    out=list(a); place=1; maximum=max(out,default=0)
    while place<=maximum:
        buckets=[[] for _ in range(10)]
        for x in out: buckets[x//place%10].append(x)
        out=[x for bucket in buckets for x in bucket]; place*=10
    return out
''',
'''a=[170,45,75,90,802,24,2,66]; rows=[]; out=a[:]
for place in [1,10,100]:
    buckets=[[] for _ in range(10)]
    for x in out: buckets[x//place%10].append(x)
    out=[x for b in buckets for x in b]; rows.append((place,out[:]))
show_table(['当前位权','稳定分桶后'],rows)''',
'''from random import Random
rng=Random(40)
for n in range(50):
    a=[rng.randrange(1000) for _ in range(n)]
    assert heap_sort(a[:])==counting_sort(a)==radix_sort_nonnegative(a)==sorted(a)
a=[(2,'a'),(1,'b'),(2,'c')]
assert counting_sort(a,key=lambda x:x[0])==[(1,'b'),(2,'a'),(2,'c')]
for fn,values in [(radix_sort_nonnegative,[1,-1]),(counting_sort,[0,10**9])]:
    try: fn(values)
    except ValueError: pass
    else: raise AssertionError('unsupported domain must fail explicitly')''',
'堆顶为剩余最大值，逐个放入已排序后缀保持归纳关系。基数分桶稳定，使新位相同的元素保持低位已排好的次序，逐位归纳得到整体有序。','堆 O(n log n)时间/O(1)辅助空间；计数 O(n+R)时间空间；d位十进制基数 O(d(n+10))时间/O(n+10)空间。')

add(41, '快速选择不必把两边都排好，只追踪目标秩所在的一侧。划分后等于pivot的块覆盖一段最终秩，k落在其中即可直接返回。接口 `quickselect` 使用零基第k小；对外第k大转为零基第 n−k 小。注意平均线性不代表每个输入都线性。',
'''from random import Random

def quickselect(a,k,rng):
    if not 0<=k<len(a): raise ValueError('k must be a valid zero-based rank')
    lo,hi=0,len(a)
    while True:
        pivot=a[rng.randrange(lo,hi)]; lt=i=lo; gt=hi
        while i<gt:
            if a[i]<pivot: a[lt],a[i]=a[i],a[lt]; lt+=1; i+=1
            elif a[i]>pivot: gt-=1; a[i],a[gt]=a[gt],a[i]
            else: i+=1
        if k<lt: hi=lt
        elif k>=gt: lo=gt
        else: return a[k]

def kth_largest(nums,k):
    if not 1<=k<=len(nums): raise ValueError('k is one-based')
    return quickselect(list(nums),len(nums)-k,Random(41))
''',
'''a=[3,2,1,5,6,4]
show_table(['第k大','对应零基小秩','答案'],[(k,len(a)-k,kth_largest(a,k)) for k in range(1,len(a)+1)])''',
'''assert kth_largest([3,2,1,5,6,4],2)==5
rng=Random(11)
for n in range(1,60):
    a=[rng.randrange(-4,5) for _ in range(n)]
    for k in range(n): assert quickselect(a[:],k,rng)==sorted(a)[k]
assert kth_largest([7]*100,100)==7''',
'被丢弃的区间所有元素都严格位于目标秩另一侧；未处理区始终包含第k小值。等值块的位置范围确定后，任一块内元素都是该秩值。','随机pivot期望 O(n)，最坏 O(n²)；原地选择 O(1)辅助状态，kth_largest为保护输入复制 O(n)。')

add(42, '二分首先确定区间约定。本章采用半开 [lo,hi)，寻找第一个使谓词成立的位置。lower_bound 的谓词是 a[i]≥x，upper_bound 是 a[i]>x。所有未排除答案都在闭候选位置范围 [lo,hi]；中点两侧的单调关系允许每步丢弃约一半元素。',
'''def lower_bound(a,x):
    lo,hi=0,len(a)
    while lo<hi:
        mid=(lo+hi)//2
        if a[mid]<x: lo=mid+1
        else: hi=mid
    return lo

def upper_bound(a,x):
    lo,hi=0,len(a)
    while lo<hi:
        mid=(lo+hi)//2
        if a[mid]<=x: lo=mid+1
        else: hi=mid
    return lo

def search_range(a,x):
    left=lower_bound(a,x)
    if left==len(a) or a[left]!=x: return [-1,-1]
    return [left,upper_bound(a,x)-1]
''',
'''a=[1,2,2,4]; lo=0; hi=len(a); rows=[]
while lo<hi:
    mid=(lo+hi)//2; rows.append((lo,hi,mid,a[mid]))
    if a[mid]<2: lo=mid+1
    else: hi=mid
show_table(['lo','hi（不含）','mid','a[mid]'],rows)''',
'''from bisect import bisect_left,bisect_right
from itertools import combinations_with_replacement
assert lower_bound([1,2,2,4],2)==1 and upper_bound([1,2,2,4],2)==3
assert lower_bound([],2)==0
for n in range(8):
    for a in combinations_with_replacement([0,1,2],n):
        for x in range(-1,4):
            assert lower_bound(a,x)==bisect_left(a,x)
            assert upper_bound(a,x)==bisect_right(a,x)
            indices=[i for i,v in enumerate(a) if v==x]
            assert search_range(a,x)==([indices[0],indices[-1]] if indices else [-1,-1])''',
'lower_bound维持lo前所有元素<x、hi起所有元素≥x。更新规则保留该性质，长度严格下降，lo=hi时就是分界位置。','O(log(n+1))时间、O(1)辅助空间。测试验证结果；复杂度结论来自区间收缩，不来自固定计时门槛。')

add(43, '把求最优值转换为判断给定答案是否可行，再证明可行性随答案单调。吃香蕉速度越快，所需小时数不增加；船容量越大，所需天数不增加。边界必须覆盖一个可行答案；整数天数用整除向上取整，避免浮点误差。',
'''def first_true(lo,hi,feasible):
    """Smallest feasible integer in inclusive [lo,hi]; hi must be feasible."""
    if lo>hi or not feasible(hi): raise ValueError('upper bound must be feasible')
    while lo<hi:
        mid=(lo+hi)//2
        if feasible(mid): hi=mid
        else: lo=mid+1
    return lo

def min_eating_speed(piles,h):
    if not piles or h<len(piles): raise ValueError('positive piles and enough hours required')
    return first_true(1,max(piles),lambda speed:sum((p+speed-1)//speed for p in piles)<=h)

def ship_within_days(weights,days):
    if not weights or days<1: raise ValueError('nonempty positive weights and positive days required')
    def feasible(capacity):
        used=1; load=0
        for w in weights:
            if load+w>capacity: used+=1; load=0
            load+=w
        return used<=days
    return first_true(max(weights),sum(weights),feasible)
''',
'''p=[3,6,7,11]
show_table(['速度','总小时','≤8可行'],[(v,sum((x+v-1)//v for x in p),sum((x+v-1)//v for x in p)<=8) for v in range(1,12)])''',
'''assert min_eating_speed([3,6,7,11],8)==4
assert ship_within_days([1,2,3,4],1)==10
assert ship_within_days([1,2,3,4],4)==4
from itertools import product
for a in product([1,2,3],repeat=4):
    for h in range(4,9):
        ref=next(v for v in range(1,max(a)+1) if sum((x+v-1)//v for x in a)<=h)
        assert min_eating_speed(a,h)==ref
for boundary in range(21):
    assert first_true(0,20,lambda x:x>=boundary)==boundary''',
'吃香蕉判定可分离求和。装船判定中每一天尽量装到容量上限，不会让以后剩余前缀更多；对天数做“领先”归纳即可证明这是最少天数。单调可行集合的首个元素就是最优解。','每次判定 O(n)，二分次数 O(log U)，总 O(n log U)、O(1)辅助空间；U为答案搜索跨度。')

add(44, '旋转数组至少有一半有序，可用目标是否落在有序半区确定方向；有重复时端点相等可能无法判断，只能缩小边界，因此最坏退化线性。矩阵二分需要跨行也递增，不能只凭每行有序。峰值搜索依赖相邻不相等和边界视为负无穷的契约。',
'''def search_rotated_unique(nums,target):
    lo,hi=0,len(nums)-1
    while lo<=hi:
        mid=(lo+hi)//2
        if nums[mid]==target: return mid
        if nums[lo]<=nums[mid]:
            if nums[lo]<=target<nums[mid]: hi=mid-1
            else: lo=mid+1
        else:
            if nums[mid]<target<=nums[hi]: lo=mid+1
            else: hi=mid-1
    return -1

def search_rotated_with_duplicates(nums,target):
    lo,hi=0,len(nums)-1
    while lo<=hi:
        mid=(lo+hi)//2
        if nums[mid]==target: return True
        if nums[lo]==nums[mid]==nums[hi]: lo+=1; hi-=1
        elif nums[lo]<=nums[mid]:
            if nums[lo]<=target<nums[mid]: hi=mid-1
            else: lo=mid+1
        else:
            if nums[mid]<target<=nums[hi]: lo=mid+1
            else: hi=mid-1
    return False

def search_matrix(matrix,target):
    if not matrix or not matrix[0]: return False
    rows,cols=len(matrix),len(matrix[0]); lo,hi=0,rows*cols
    while lo<hi:
        mid=(lo+hi)//2; value=matrix[mid//cols][mid%cols]
        if value<target: lo=mid+1
        else: hi=mid
    return lo<rows*cols and matrix[lo//cols][lo%cols]==target

def find_peak(nums):
    if not nums: raise ValueError('requires a nonempty sequence without equal neighbors')
    lo,hi=0,len(nums)-1
    while lo<hi:
        mid=(lo+hi)//2
        if nums[mid]<nums[mid+1]: lo=mid+1
        else: hi=mid
    return lo
''',
'''base=[0,1,2,3,4]
show_table(['旋转量','数组','目标2的位置'],[(k,base[k:]+base[:k],search_rotated_unique(base[k:]+base[:k],2)) for k in range(5)])''',
'''from itertools import combinations_with_replacement,product
for n in range(1,7):
    base=list(range(n))
    for k in range(n):
        a=base[k:]+base[:k]
        for t in range(-1,n+1): assert search_rotated_unique(a,t)==(a.index(t) if t in a else -1)
    for base in combinations_with_replacement([0,1,2],n):
        for k in range(n):
            a=base[k:]+base[:k]
            for t in range(4): assert search_rotated_with_duplicates(a,t)==(t in a)
for a in product(range(3),repeat=5):
    if all(a[i]!=a[i+1] for i in range(4)):
        p=find_peak(a); assert (p==0 or a[p]>a[p-1]) and (p==4 or a[p]>a[p+1])
assert search_matrix([[1,3,5],[7,9,11]],9)''',
'无重复旋转数组的一半保有整体次序，区间成员测试可安全排除另一半；重复版本只在确实无法判别时去端点。峰值若中部上升，右半必在某处转降或在右边界形成峰。','无重复搜索、矩阵查找、峰值 O(log n)；重复搜索最坏 O(n)。均O(1)辅助空间。')

REVERSE='''def reverse_list(head):
    previous=None
    while head:
        following=head.next
        head.next=previous
        previous,head=head,following
    return previous
'''

add(45, '链表修改先找到“待修改节点的前驱”。删除头节点没有自然前驱，哨兵将其变成普通删除。课程实现用size记录长度，get越界返回−1；负插入位置按0处理，超过长度的插入不执行。节点身份和next结构比打印出的值更重要。',
NODES+'''
def remove_elements(head,val):
    dummy=ListNode(0,head); previous=dummy
    while previous.next:
        if previous.next.val==val: previous.next=previous.next.next
        else: previous=previous.next
    return dummy.next

class MyLinkedList:
    def __init__(self): self.dummy=ListNode(); self.size=0
    def get(self,index):
        if not 0<=index<self.size: return -1
        node=self.dummy.next
        for _ in range(index): node=node.next
        return node.val
    def addAtHead(self,val): self.addAtIndex(0,val)
    def addAtTail(self,val): self.addAtIndex(self.size,val)
    def addAtIndex(self,index,val):
        index=max(index,0)
        if index>self.size: return
        before=self.dummy
        for _ in range(index): before=before.next
        before.next=ListNode(val,before.next); self.size+=1
    def deleteAtIndex(self,index):
        if not 0<=index<self.size: return
        before=self.dummy
        for _ in range(index): before=before.next
        before.next=before.next.next; self.size-=1
''',
'''a=[6,1,6,2,6]
show_table(['原值','删除值','剩余链'],[(a,6,nodes_to_list(remove_elements(list_to_nodes(a),6)))])
linked=MyLinkedList(); rows=[]
for index,value in [(0,1),(1,3),(1,2)]:
    linked.addAtIndex(index,value); rows.append((index,value,nodes_to_list(linked.dummy.next)))
show_table(['插入位置','插入值','链'],rows)''',
'''assert nodes_to_list(remove_elements(list_to_nodes([6,1,6,2,6]),6))==[1,2]
assert remove_elements(list_to_nodes([6,6]),6) is None
assert remove_elements(None,6) is None
x=MyLinkedList(); x.addAtHead(1); x.addAtTail(3); x.addAtIndex(1,2)
assert x.get(1)==2; x.deleteAtIndex(1); assert x.get(1)==3
assert nodes_to_list(x.dummy.next)==[1,3] and x.size==2
x.deleteAtIndex(9); assert x.size==2''',
'previous前面的节点都已完成过滤，previous.next是下一个未处理节点。删除时不推进previous，防止漏掉连续待删节点。','删除 O(n)；按索引操作 O(n)，头插 O(1)；哨兵与指针辅助空间 O(1)。')

add(46, '反转链表要先保存next，再修改当前指向，否则会失去未处理后缀。局部反转先固定区间前驱，将区间中后续节点逐个摘出并头插到区间开头。参数使用一基闭区间，且要求区间在链表范围内。',
NODES+REVERSE+'''
def reverse_between(head,left,right):
    if not 1<=left<=right: raise ValueError('requires 1 <= left <= right')
    dummy=ListNode(0,head); before=dummy
    for _ in range(left-1): before=before.next
    tail=before.next
    for _ in range(right-left):
        moved=tail.next; tail.next=moved.next
        moved.next=before.next; before.next=moved
    return dummy.next
''',
'''h=list_to_nodes([1,2,3,4]); previous=None; rows=[]
while h:
    following=h.next; h.next=previous; previous,h=h,following
    rows.append((nodes_to_list(previous),nodes_to_list(h)))
show_table(['已反转前缀','未处理后缀'],rows)''',
'''assert nodes_to_list(reverse_list(list_to_nodes([1,2,3])))==[3,2,1]
assert nodes_to_list(reverse_between(list_to_nodes([1,2,3,4,5]),2,4))==[1,4,3,2,5]
h=list_to_nodes([1,2,3,4]); original=[]; p=h
while p: original.append(p); p=p.next
h=reverse_list(reverse_list(h)); restored=[]; p=h
while p: restored.append(p); p=p.next
assert restored==original
for n in range(1,8):
    for l in range(1,n+1):
        for r in range(l,n+1):
            a=list(range(n)); assert nodes_to_list(reverse_between(list_to_nodes(a),l,r))==a[:l-1]+a[l-1:r][::-1]+a[r:]''',
'previous指向原前缀的逆序链，head指向尚未处理后缀，二者节点不交且并集不变。局部头插保留区间尾tail，不改变区间外连接。','整链与局部反转 O(n)时间、O(1)辅助空间；不创建新数据节点，只有局部哨兵。')

add(47, '快慢指针速度差为1。进入环后，相对位移每轮增加1，因此有限轮内相遇；无环则快指针先到None。设头到入口长度为μ、环长为λ，相遇时慢指针走过的步数是λ的倍数；一指针回到头，两者同速前进会在入口相遇。偶数长度的中点返回第二个中点。',
NODES+'''
def has_cycle(head):
    slow=fast=head
    while fast and fast.next:
        slow=slow.next; fast=fast.next.next
        if slow is fast: return True
    return False

def detect_cycle(head):
    slow=fast=head
    while fast and fast.next:
        slow=slow.next; fast=fast.next.next
        if slow is fast:
            slow=head
            while slow is not fast: slow=slow.next; fast=fast.next
            return slow
    return None

def middle_node(head):
    slow=fast=head
    while fast and fast.next: slow=slow.next; fast=fast.next.next
    return slow

def remove_nth_from_end(head,n):
    if n<1: raise ValueError('n must be positive')
    dummy=ListNode(0,head); fast=slow=dummy
    for _ in range(n):
        fast=fast.next
        if fast is None: raise ValueError('n exceeds length')
    while fast.next: fast=fast.next; slow=slow.next
    slow.next=slow.next.next
    return dummy.next
''',
'''show_table(['长度','第二中点值'],[(n,middle_node(list_to_nodes(list(range(n)))).val) for n in range(1,9)])''',
'''h=list_to_nodes([1,2,3,4]); entry=h.next; h.next.next.next.next=entry
assert has_cycle(h) and detect_cycle(h) is entry
h=ListNode(9); h.next=h; assert detect_cycle(h) is h
assert not has_cycle(list_to_nodes([1,2])) and detect_cycle(None) is None
assert middle_node(list_to_nodes([1,2,3,4])).val==3
assert nodes_to_list(remove_nth_from_end(list_to_nodes([1,2,3]),3))==[2,3]
assert nodes_to_list(remove_nth_from_end(list_to_nodes([1,2,3]),1))==[1,2]
assert remove_nth_from_end(ListNode(1),1) is None''',
'入口定位使用模λ的距离关系，不依赖节点值。倒数删除保持fast比slow领先n个next边；fast到末节点时slow恰是删除目标前驱。','均 O(n)时间、O(1)辅助空间；有环时n表示可达不同节点数。中点与删除要求无环输入。')

MERGE='''def merge_two_lists(a,b):
    dummy=tail=ListNode()
    while a and b:
        if a.val<=b.val: tail.next=a; a=a.next
        else: tail.next=b; b=b.next
        tail=tail.next
    tail.next=a if a else b
    return dummy.next
'''
add(48, '链表不能O(1)随机访问中点，但快慢指针可以线性找到切分点。归并排序递归排序两条更短链，再复用原节点线性合并。相等时优先取左链节点，保留原始次序。本章实现是自顶向下版：递归空间O(log n)，不能声称严格O(1)。',
NODES+MERGE+'''
def sort_list(head):
    if head is None or head.next is None: return head
    slow=head; fast=head.next
    while fast and fast.next: slow=slow.next; fast=fast.next.next
    second=slow.next; slow.next=None
    return merge_two_lists(sort_list(head),sort_list(second))
''',
'''a=[4,2,1,3,2]
show_table(['阶段','链值'],[('输入',a),('排序',nodes_to_list(sort_list(list_to_nodes(a))))])''',
'''assert nodes_to_list(merge_two_lists(None,list_to_nodes([1,2])))==[1,2]
from random import Random
rng=Random(48)
for n in range(40):
    a=[rng.randrange(5) for _ in range(n)]; h=list_to_nodes(a); before=[]; p=h
    while p: before.append(p); p=p.next
    h=sort_list(h); after=[]; p=h
    while p:
        assert p not in after; after.append(p); p=p.next
    assert [p.val for p in after]==sorted(a)
    assert set(after)==set(before)
    for value in set(a): assert [p for p in after if p.val==value]==[p for p in before if p.val==value]''',
'两个子链长度均严格减小；合并每次取两有序链头较小者，就是全局剩余最小值。链尾仅接剩余链一次，节点集合完整保持。','O(n log n)时间、O(log n)递归辅助空间；链表重连不另建数据节点。')

add(49, '链表重排分成三步：找第一半末节点、反转第二半、交替穿插。判断回文只需反转后半并比较对应值；但检查不应该悄悄破坏调用者的数据，所以restore=True时还要反转回来并恢复原next关系。奇数长度的中间节点无需参与比较。',
NODES+REVERSE+'''
def _first_half_end(head):
    slow=fast=head
    while fast.next and fast.next.next: slow=slow.next; fast=fast.next.next
    return slow

def reorder_list(head):
    if head is None or head.next is None: return
    middle=_first_half_end(head); second=reverse_list(middle.next); middle.next=None
    first=head
    while second:
        following1,following2=first.next,second.next
        first.next=second; second.next=following1
        first,second=following1,following2

def is_palindrome_list(head,restore=True):
    if head is None or head.next is None: return True
    middle=_first_half_end(head); second=reverse_list(middle.next); middle.next=second
    left,right=head,second; answer=True
    while right:
        if left.val!=right.val: answer=False
        left=left.next; right=right.next
    if restore: middle.next=reverse_list(second)
    return answer
''',
'''rows=[]
for a in [[1,2,3,4],[1,2,3,4,5],[1,2,2,1]]:
    h=list_to_nodes(a); palindrome=is_palindrome_list(h); reorder_list(h)
    rows.append((a,palindrome,nodes_to_list(h)))
show_table(['原链','是否回文','重排链'],rows)''',
'''assert is_palindrome_list(list_to_nodes([1,2,2,1]))
assert not is_palindrome_list(list_to_nodes([1,2]))
from itertools import product
for n in range(7):
    for a in product([0,1],repeat=n):
        h=list_to_nodes(a); old={}; p=h
        while p: old[p]=p.next; p=p.next
        assert is_palindrome_list(h,restore=True)==(list(a)==list(a)[::-1])
        assert all(node.next is nxt for node,nxt in old.items())
        reorder_list(h)
        ref=[]; l=0; r=n-1
        while l<=r:
            ref.append(a[l]); l+=1
            if l<=r: ref.append(a[r]); r-=1
        assert nodes_to_list(h)==ref''',
'后半反转后，其第i项对应原链倒数第i项。比较完整后再反转是原变换的逆操作，且保留中点前驱连接，因此恢复的是节点拓扑而非仅值。','O(n)时间、O(1)辅助空间。restore=False明确允许后半次序改变。')

add(50, 'K组反转先确认还有完整k个节点，再反转这段并接回，否则不足一组的尾部必须保持原序。相交检测比较节点身份，两指针在走完自己链后切换到另一链，抵消长度差。随机指针复制则先建“原节点→新节点”映射，再复制next和random边，避免共享原节点。',
NODES+'''
def reverse_k_group(head,k):
    if k<1: raise ValueError('k must be positive')
    dummy=ListNode(0,head); before=dummy
    while True:
        end=before
        for _ in range(k):
            end=end.next
            if end is None: return dummy.next
        after=end.next; previous=after; current=before.next
        while current is not after:
            following=current.next; current.next=previous
            previous,current=current,following
        old_start=before.next; before.next=end; before=old_start

def get_intersection_node(a,b):
    p,q=a,b
    while p is not q:
        p=p.next if p else b
        q=q.next if q else a
    return p

class RandomNode:
    def __init__(self,val=0,next=None,random=None):
        self.val,self.next,self.random=val,next,random

def copy_random_list(head):
    mapping={None:None}; node=head
    while node:
        mapping[node]=RandomNode(node.val); node=node.next
    node=head
    while node:
        mapping[node].next=mapping[node.next]
        mapping[node].random=mapping[node.random]
        node=node.next
    return mapping[head]
''',
'''a=[1,2,3,4,5]
show_table(['k','重连后'],[(k,nodes_to_list(reverse_k_group(list_to_nodes(a),k))) for k in [1,2,3,6]])''',
'''assert nodes_to_list(reverse_k_group(list_to_nodes([1,2,3,4,5]),2))==[2,1,4,3,5]
assert nodes_to_list(reverse_k_group(list_to_nodes([1,2]),3))==[1,2]
shared=list_to_nodes([8,9]); a=ListNode(1,shared); b=ListNode(2,ListNode(3,shared))
assert get_intersection_node(a,b) is shared
assert get_intersection_node(list_to_nodes([1,2]),list_to_nodes([1,2])) is None
x,y,z=RandomNode(7),RandomNode(13),RandomNode(11); x.next=y; y.next=z
x.random=z; y.random=x; z.random=z
clone=copy_random_list(x); originals=[x,y,z]; clones=[clone,clone.next,clone.next.next]
assert not set(originals)&set(clones)
assert [n.val for n in clones]==[7,13,11]
assert clones[0].random is clones[2] and clones[1].random is clones[0] and clones[2].random is clones[2]
assert copy_random_list(None) is None''',
'整组确认后反转保持区间外边，组间前驱更新到旧组头。相交指针各走过A+B的长度，最终同步进入公共尾段或同到None。复制映射是一一对应，边的像保持拓扑。','K组反转 O(n)时间/O(1)空间；相交 O(n+m)/O(1)；随机复制 O(n)时间空间。本章next链必须有限无环，random指向链内节点或None。')
