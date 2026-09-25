from course_builder import add

add(134,'坐标压缩保留的是相等关系与大小顺序，不保留数值差。把巨大、稀疏或负坐标映射为连续秩，可以用数组数据结构处理。右侧更小数先用排序列表和二分写清楚查询含义：lower_bound位置是严格小于当前值的个数，后续再用Fenwick消除列表插入的线性代价。',
'''from bisect import bisect_left,insort

def coordinate_compress(values):
    ordered=sorted(set(values)); rank={v:i for i,v in enumerate(ordered)}
    return ordered,[rank[v] for v in values]

def rank_transform(arr):
    ordered,ranks=coordinate_compress(arr); return [r+1 for r in ranks]

def count_smaller_sorted_list(nums):
    ordered=[]; answer=[]
    for x in reversed(nums): answer.append(bisect_left(ordered,x)); insort(ordered,x)
    return answer[::-1]
''',
'''a=[10**12,-7,20,-7]; ordered,ranks=coordinate_compress(a)
show_table(['原值','零基秩'],list(zip(a,ranks)))
print('秩不能保持差值：',ordered[-1]-ordered[0],'≠',len(ordered)-1)''',
'''assert rank_transform([40,10,20,30])==[4,1,2,3]
assert rank_transform([7,7,-2])==[2,2,1]
assert count_smaller_sorted_list([5,2,6,1])==[2,1,1,0]
from itertools import product
for n in range(7):
    for a in product((-100,0,10**12),repeat=n):
        ordered,ranks=coordinate_compress(a)
        assert [ordered[r] for r in ranks]==list(a)
        assert all((a[i]<a[j])==(ranks[i]<ranks[j]) for i in range(n) for j in range(n))
        assert count_smaller_sorted_list(a)==[sum(y<x for y in a[i+1:]) for i,x in enumerate(a)]''',
'排序去重产生严格递增的一一映射，故比较关系保持不变；重复值共享同一秩。右向左处理时排序列表恰包含当前位置右侧所有值，二分左界排除了等值元素。',
'压缩O(n log n)时间O(n)空间；列表计数基线最坏O(n²)时间，因为insort插入要移动元素，二分O(log n)不代表整个操作O(log n)。返回(排序原值表,与输入对应的零基秩)。')

BIT='''class Fenwick:
    def __init__(self,values):
        values=[0]*values if isinstance(values,int) else list(values)
        self.n=len(values); self.bit=[0]+values
        for i in range(1,self.n+1):
            parent=i+(i&-i)
            if parent<=self.n: self.bit[parent]+=self.bit[i]
    def add(self,i,delta):
        if not 0<=i<self.n: raise IndexError('point index outside tree')
        i+=1
        while i<=self.n: self.bit[i]+=delta; i+=i&-i
    def prefix_sum(self,end):
        if not 0<=end<=self.n: raise IndexError('prefix boundary outside tree')
        answer=0
        while end: answer+=self.bit[end]; end-=end&-end
        return answer
    def range_sum(self,left,right):
        if left>right: raise ValueError('invalid range')
        return self.prefix_sum(right)-self.prefix_sum(left)

def count_smaller(nums):
    ordered=sorted(set(nums)); ranks={x:i for i,x in enumerate(ordered)}; tree=Fenwick(len(ordered)); answer=[]
    for x in reversed(nums):
        r=ranks[x]; answer.append(tree.prefix_sum(r)); tree.add(r,1)
    return answer[::-1]
'''
add(135,'Fenwick把前缀切成若干长度为lowbit(i)的块。内部采用一基下标，bit[i]保存原数组区间[i−lowbit(i),i)的和。查询不断清除最低1，把前缀分成不重叠块；更新不断加lowbit，走过所有覆盖该位置的块。公共接口仍使用零基下标与半开边界。',BIT,
'''a=[1,3,5,7,9,11]; tree=Fenwick(a)
show_table(['内部下标','覆盖原数组半开区间','块和'],[(i,(i-(i&-i),i),tree.bit[i]) for i in range(1,len(a)+1)])''',
'''tree=Fenwick([1,3,5]); assert tree.range_sum(0,3)==9
tree.add(1,-1); assert tree.range_sum(0,3)==8
assert count_smaller([5,2,6,1])==[2,1,1,0]
from random import Random
rng=Random(135)
for n in range(1,25):
    a=[rng.randrange(-5,6) for _ in range(n)]; tree=Fenwick(a)
    for _ in range(80):
        if rng.randrange(2):
            i=rng.randrange(n); delta=rng.randrange(-5,6); a[i]+=delta; tree.add(i,delta)
        else:
            l=rng.randrange(n+1); r=rng.randrange(l,n+1)
            assert tree.range_sum(l,r)==sum(a[l:r])
    assert count_smaller(a)==[sum(y<x for y in a[i+1:]) for i,x in enumerate(a)]
assert Fenwick(0).prefix_sum(0)==0''',
'bit[i]的覆盖块是二进制下标分解决定的。查询沿i−lowbit(i)得到互不重叠且恰覆盖目标前缀的块；点增量更新所有包含该点的祖先块，维持块和不变量。较小数查询用prefix_sum(rank)，不包含等值秩。',
'线性建树O(n)；更新和前缀/区间查询O(log n)；计数含压缩O(n log n)，空间O(n)。add是增量而非赋值；修改旧值3到新值2应传−1。')

SEG='''class SegmentTree:
    def __init__(self,values,combine,identity):
        self.n=len(values); self.combine=combine; self.identity=identity; self.size=1
        while self.size<self.n: self.size*=2
        self.tree=[identity]*(2*self.size)
        self.tree[self.size:self.size+self.n]=list(values)
        for i in range(self.size-1,0,-1): self.tree[i]=combine(self.tree[2*i],self.tree[2*i+1])
    def set(self,i,value):
        if not 0<=i<self.n: raise IndexError('point outside tree')
        i+=self.size; self.tree[i]=value
        while i>1:
            i//=2; self.tree[i]=self.combine(self.tree[2*i],self.tree[2*i+1])
    def query(self,left,right):
        if not 0<=left<=right<=self.n: raise IndexError('invalid half-open range')
        left+=self.size; right+=self.size; a=b=self.identity
        while left<right:
            if left&1: a=self.combine(a,self.tree[left]); left+=1
            if right&1: right-=1; b=self.combine(self.tree[right],b)
            left//=2; right//=2
        return self.combine(a,b)
'''
add(136,'线段树只要求合并运算满足结合律并有单位元，不要求交换律。求和、最小值、字符串拼接都符合这一接口。区间查询从两端收集块时，左侧按从左到右追加，右侧必须向前插入；否则求和测试会通过，但字符串拼接会反序。',SEG,
'''tree=SegmentTree(list('abcdef'),lambda a,b:a+b,'')
show_table(['半开区间','聚合字符串'],[((l,r),tree.query(l,r)) for l,r in [(0,6),(1,5),(2,2),(5,6)]])
show_table(['内部节点','节点聚合'],list(enumerate(tree.tree[1:],1)))''',
'''import operator
from random import Random
rng=Random(136)
for n in range(1,25):
    a=[rng.randrange(-9,10) for _ in range(n)]; tree=SegmentTree(a,operator.add,0)
    letters=list('x'*n); text=SegmentTree(letters,operator.add,'')
    for _ in range(70):
        i=rng.randrange(n); a[i]=rng.randrange(-9,10); tree.set(i,a[i]); letters[i]=rng.choice('abc'); text.set(i,letters[i])
        l=rng.randrange(n+1); r=rng.randrange(l,n+1)
        assert tree.query(l,r)==sum(a[l:r])
        assert text.query(l,r)==''.join(letters[l:r])
assert SegmentTree([],operator.add,0).query(0,0)==0''',
'每个节点保持其区间按原顺序的聚合。查询把区间拆成不重叠有序块；结合律允许改变括号，不能允许改变顺序。左右双累加器分别维护已取前缀与后缀，最终combine(a,b)恢复整体顺序。',
'建树O(n)次combine，更新与查询O(log n)次combine，空间O(n)。这些上界以combine为O(1)为前提；字符串拼接自身复制字符，真实字节代价不能忽略。identity应不可变，combine应无副作用。')

LAZY='''class RangeAddSumTree:
    def __init__(self,values):
        values=list(values); self.n=len(values); self.total=[0]*(4*max(1,self.n)); self.lazy=[0]*len(self.total)
        def build(node,l,r):
            if r-l==1: self.total[node]=values[l]; return
            mid=(l+r)//2; build(node*2,l,mid); build(node*2+1,mid,r); self.total[node]=self.total[node*2]+self.total[node*2+1]
        if self.n: build(1,0,self.n)
    def _apply(self,node,l,r,delta): self.total[node]+=(r-l)*delta; self.lazy[node]+=delta
    def _push(self,node,l,r):
        if self.lazy[node] and r-l>1:
            mid=(l+r)//2; tag=self.lazy[node]
            self._apply(node*2,l,mid,tag); self._apply(node*2+1,mid,r,tag); self.lazy[node]=0
    def add(self,left,right,delta):
        if not 0<=left<=right<=self.n: raise IndexError('invalid half-open range')
        if left==right: return
        def update(node,l,r):
            if right<=l or r<=left: return
            if left<=l and r<=right: self._apply(node,l,r,delta); return
            self._push(node,l,r); mid=(l+r)//2; update(node*2,l,mid); update(node*2+1,mid,r)
            self.total[node]=self.total[node*2]+self.total[node*2+1]
        update(1,0,self.n)
    def query(self,left,right):
        if not 0<=left<=right<=self.n: raise IndexError('invalid half-open range')
        if left==right: return 0
        def get(node,l,r):
            if right<=l or r<=left: return 0
            if left<=l and r<=right: return self.total[node]
            self._push(node,l,r); mid=(l+r)//2
            return get(node*2,l,mid)+get(node*2+1,mid,r)
        return get(1,0,self.n)

class FlipCountTree(RangeAddSumTree):
    def __init__(self,values):
        values=list(values)
        if any(x not in (0,1) for x in values): raise ValueError('binary values required')
        super().__init__(values)
    def _apply(self,node,l,r,delta):
        if delta&1: self.total[node]=r-l-self.total[node]; self.lazy[node]^=1
    def flip(self,left,right): self.add(left,right,1)
    def count(self,left,right): return self.query(left,right)

def handle_sum_queries(nums1,nums2,queries):
    tree=FlipCountTree(nums1); total=sum(nums2); out=[]
    for kind,a,b in queries:
        if kind==1: tree.flip(a,b+1)
        elif kind==2: total+=a*tree.total[1]
        elif kind==3: out.append(total)
        else: raise ValueError('unknown query type')
    return out
'''
add(137,'区间加法不需要立即更新每片叶子：节点和加上delta×长度，并保存尚未下传的增量。翻转二进制区间则把ones改为长度−ones；两次翻转抵消，标记按异或复合。只有准备访问子区间时才push，子节点变化后再pull。',LAZY,
'''tree=RangeAddSumTree([1,2,3,4]); rows=[('初始',[tree.query(i,i+1) for i in range(4)])]
for l,r,x in [(0,4,2),(1,3,-1),(2,4,5)]:
    tree.add(l,r,x); rows.append((f'[{l},{r})加{x}',[tree.query(i,i+1) for i in range(4)]))
show_table(['操作','实际逐点值'],rows)''',
'''flip=FlipCountTree([1,0,1]); flip.flip(1,2); assert flip.count(0,3)==3
flip.flip(0,3); flip.flip(0,3); assert flip.count(0,3)==3
assert handle_sum_queries([1,0,1],[0,0,0],[[1,1,1],[2,1,0],[3,0,0]])==[3]
from random import Random
rng=Random(137)
for n in range(1,20):
    a=[rng.randrange(-3,4) for _ in range(n)]; bits=[rng.randrange(2) for _ in range(n)]; st=RangeAddSumTree(a); ft=FlipCountTree(bits)
    for _ in range(100):
        l=rng.randrange(n+1); r=rng.randrange(l,n+1); delta=rng.randrange(-4,5)
        st.add(l,r,delta); ft.flip(l,r)
        for i in range(l,r): a[i]+=delta; bits[i]^=1
        x=rng.randrange(n+1); y=rng.randrange(x,n+1)
        assert st.query(x,y)==sum(a[x:y]) and ft.count(x,y)==sum(bits[x:y])
assert RangeAddSumTree([]).query(0,0)==0''',
'节点聚合值包含自身所有待下传更新，lazy仅表示孩子尚缺的部分，因此整段查询无需push。加法标记可相加，翻转标记按奇偶性合并。赋值后加法与加法后赋值不交换，不能把本章相加标记直接用于赋值拓展。',
'静态树建树O(n)时间空间；区间更新与查询O(log n)。查询1的输入区间闭合，转为内部半开区间；类型2、3只读根计数或总和为O(1)。这里实现静态节点；极大坐标域的动态开点与赋值标记属于拓展，不宣称已实现。')

add(138,'静态RMQ没有更新时，可以预存所有2^k长度块。查询长度L取两个长度2^floor(log2 L)块覆盖区间，允许重叠，因为min/max满足幂等性：重复合并同一元素不改变结果。求和不满足这个性质，不能照搬两块重叠公式。',
'''class _SparseTable:
    def __init__(self,values,combine):
        self.n=len(values); self.combine=combine; self.table=[list(values)]; width=2
        while width<=self.n:
            half=width//2; old=self.table[-1]
            self.table.append([combine(old[i],old[i+half]) for i in range(self.n-width+1)]); width*=2
    def query(self,left,right):
        if not 0<=left<right<=self.n: raise IndexError('nonempty half-open interval required')
        k=(right-left).bit_length()-1; width=1<<k
        return self.combine(self.table[k][left],self.table[k][right-width])

class SparseTableMin(_SparseTable):
    def __init__(self,values): super().__init__(values,min)

class SparseTableMax(_SparseTable):
    def __init__(self,values): super().__init__(values,max)

def static_window_max(nums,k):
    if k<=0: raise ValueError('positive window length required')
    tree=SparseTableMax(nums)
    return [tree.query(i,i+k) for i in range(len(nums)-k+1)]
''',
'''a=[4,2,5,1,7]; st=SparseTableMin(a)
show_table(['块长','各起点块最小值'],[(1<<k,row) for k,row in enumerate(st.table)])
print('长度5由[0,4)与[1,5)两块覆盖：',st.query(0,5))''',
'''assert SparseTableMin([4,2,5,1]).query(0,4)==1
assert static_window_max([1,3,-1,-3,5,3,6,7],3)==[3,3,5,5,6,7]
from random import Random
rng=Random(138)
for n in range(1,35):
    a=[rng.randrange(-9,10) for _ in range(n)]; small=SparseTableMin(a); big=SparseTableMax(a)
    for l in range(n):
        for r in range(l+1,n+1): assert small.query(l,r)==min(a[l:r]) and big.query(l,r)==max(a[l:r])
assert static_window_max([1,2],3)==[]
# 对和使用重叠公式会重复计入中间元素。
a=[1,2,3]; assert sum(a[:2])+sum(a[1:])!=sum(a)''',
'两个选定块的并集恰好覆盖查询区间，交集可能非空。结合律与幂等性保证重复元素不影响min/max，因此答案正确。若需要一般结合运算，可用不相交分块或Disjoint Sparse Table，不能仅修改combine就声称本算法通用。',
'预处理O(n log n)时间空间，查询O(1)次整数索引与聚合。数组静态；更新后原表失效。固定窗口一次性最大值通常用单调队列O(n)更省，不因学过稀疏表就强行使用。')
