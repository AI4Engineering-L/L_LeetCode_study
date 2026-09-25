from course_builder import add

TREAP='''from random import Random

class _TreapNode:
    def __init__(self,key,priority):
        self.key=key; self.priority=priority; self.count=1; self.size=1; self.left=self.right=None

def _size(node): return node.size if node else 0

def _pull(node):
    if node: node.size=node.count+_size(node.left)+_size(node.right)
    return node

def _rotate_left(node):
    root=node.right; node.right=root.left; root.left=node; _pull(node); return _pull(root)

def _rotate_right(node):
    root=node.left; node.left=root.right; root.right=node; _pull(node); return _pull(root)

class OrderStatisticTreap:
    def __init__(self,rng=None): self.root=None; self.rng=Random(139) if rng is None else rng; self.serial=0
    def __len__(self): return _size(self.root)
    def __contains__(self,key):
        node=self.root
        while node:
            if node.key==key: return True
            node=node.left if key<node.key else node.right
        return False
    def insert(self,key):
        self.serial+=1; priority=(self.rng.getrandbits(64),self.serial)
        def put(node):
            if node is None: return _TreapNode(key,priority)
            if key==node.key: node.count+=1
            elif key<node.key:
                node.left=put(node.left)
                if node.left.priority<node.priority: node=_rotate_right(node)
            else:
                node.right=put(node.right)
                if node.right.priority<node.priority: node=_rotate_left(node)
            return _pull(node)
        self.root=put(self.root)
    def _merge(self,left,right):
        if not left: return right
        if not right: return left
        if left.priority<right.priority: left.right=self._merge(left.right,right); return _pull(left)
        right.left=self._merge(left,right.left); return _pull(right)
    def discard(self,key):
        if key not in self: return False
        def erase(node):
            if key<node.key: node.left=erase(node.left)
            elif key>node.key: node.right=erase(node.right)
            elif node.count>1: node.count-=1
            else: return self._merge(node.left,node.right)
            return _pull(node)
        self.root=erase(self.root); return True
    def rank(self,key):
        node=self.root; answer=0
        while node:
            if key<=node.key: node=node.left
            else: answer+=_size(node.left)+node.count; node=node.right
        return answer
    def kth(self,k):
        if not 0<=k<len(self): raise IndexError('zero-based rank outside multiset')
        node=self.root
        while node:
            left=_size(node.left)
            if k<left: node=node.left
            elif k<left+node.count: return node.key
            else: k-=left+node.count; node=node.right
    def lower_bound(self,key):
        node=self.root; answer=None
        while node:
            if node.key>=key: answer=node.key; node=node.left
            else: node=node.right
        return answer

def contains_nearby_almost_duplicate(nums,index_diff,value_diff):
    if index_diff<=0 or value_diff<0: return False
    tree=OrderStatisticTreap()
    for i,x in enumerate(nums):
        candidate=tree.lower_bound(x-value_diff)
        if candidate is not None and candidate<=x+value_diff: return True
        tree.insert(x)
        if i>=index_diff: tree.discard(nums[i-index_diff])
    return False
'''
add(139,'普通BST可能退化为链。Treap同时维护按key的BST顺序和随机priority的堆顺序，插入后用旋转恢复堆性质；子树size让rank与kth成为沿树下降的查询。重复值用count保存，不创建相同key节点。AVL/红黑树提供最坏高度保证，Treap与跳表则依赖随机化的期望分析。',TREAP,
'''tree=OrderStatisticTreap(Random(139))
for x in [5,2,8,2,6,1]: tree.insert(x)
rows=[]; stack=[tree.root]
while stack:
    node=stack.pop()
    if not node: continue
    rows.append((node.key,node.count,node.size,node.left.key if node.left else None,node.right.key if node.right else None))
    stack.extend([node.right,node.left])
show_table(['key','重复次数','子树size','左孩子','右孩子'],rows)
print('全部顺序统计',[tree.kth(i) for i in range(len(tree))])''',
'''from bisect import bisect_left,insort
rng=Random(139); tree=OrderStatisticTreap(Random(5)); reference=[]
def audit(node,low=None,high=None):
    if not node: return 0
    assert (low is None or low<node.key) and (high is None or node.key<high)
    for child in (node.left,node.right):
        if child: assert node.priority<child.priority
    total=node.count+audit(node.left,low,node.key)+audit(node.right,node.key,high)
    assert node.count>=1 and node.size==total
    return total
for _ in range(700):
    x=rng.randrange(-12,13)
    if rng.randrange(2): tree.insert(x); insort(reference,x)
    else:
        found=x in reference; assert tree.discard(x)==found
        if found: reference.remove(x)
    assert audit(tree.root)==len(reference)==len(tree)
    assert [tree.kth(i) for i in range(len(tree))]==reference
    assert tree.rank(x)==bisect_left(reference,x)
    candidates=[y for y in reference if y>=x]
    assert tree.lower_bound(x)==(candidates[0] if candidates else None)
for _ in range(180):
    a=[rng.randrange(-20,21) for _ in range(12)]; k=rng.randrange(6); t=rng.randrange(-1,8)
    want=any(j-i<=k and abs(a[j]-a[i])<=t for i in range(len(a)) for j in range(i+1,len(a)))
    assert contains_nearby_almost_duplicate(a,k,t)==want''',
'旋转不改变中序顺序，只改变父子关系，因此BST不变量保持；按优先级旋转使随机优先级最小的点成为子树根。rank累加已确定小于目标的左子树与重复数；kth根据左子树大小排除不含答案的一侧。滑窗树只保存最近index_diff个先前元素，再查询[value−t,value+t]。',
'独立随机优先级下树高与操作期望O(log n)，最坏仍可O(n)；递归实现也受最坏树高限制。空间O(不同key数)。固定随机源仅保证测试复现，不把期望保证写成最坏保证；跳表/AVL/红黑树只作结构对照，未伪装为本章已实现。')

WEIGHTED='''from math import isclose

class WeightedDSU:
    def __init__(self): self.parent={}; self.weight={}; self.size={}
    def add(self,x):
        if x not in self.parent: self.parent[x]=x; self.weight[x]=1.0; self.size[x]=1
    def find(self,x):
        if x not in self.parent: raise KeyError(x)
        path=[]; node=x
        while self.parent[node]!=node: path.append(node); node=self.parent[node]
        ratio=1.0
        for v in reversed(path): ratio*=self.weight[v]; self.weight[v]=ratio; self.parent[v]=node
        return node
    def union(self,x,y,value):
        if value==0: raise ValueError('nonzero ratio required')
        self.add(x); self.add(y); rx=self.find(x); ry=self.find(y); wx=self.weight[x]; wy=self.weight[y]
        if rx==ry:
            if not isclose(wx/wy,value,rel_tol=1e-9,abs_tol=1e-12): raise ValueError('inconsistent equation')
            return False
        if self.size[rx]<self.size[ry]:
            self.parent[rx]=ry; self.weight[rx]=value*wy/wx; self.size[ry]+=self.size[rx]
        else:
            self.parent[ry]=rx; self.weight[ry]=wx/(value*wy); self.size[rx]+=self.size[ry]
        return True
    def ratio(self,x,y):
        if x not in self.parent or y not in self.parent: return -1.0
        if self.find(x)!=self.find(y): return -1.0
        return self.weight[x]/self.weight[y]

def calc_equation(equations,values,queries):
    if len(equations)!=len(values): raise ValueError('one value per equation required')
    dsu=WeightedDSU()
    for (x,y),value in zip(equations,values): dsu.union(x,y,value)
    return [dsu.ratio(x,y) for x,y in queries]

class RollbackDSU:
    def __init__(self,n): self.parent=list(range(n)); self.size=[1]*n; self.components=n; self.history=[]
    def find(self,x):
        if not 0<=x<len(self.parent): raise IndexError('vertex outside DSU')
        while self.parent[x]!=x: x=self.parent[x]
        return x
    def union(self,a,b):
        a,b=self.find(a),self.find(b)
        if a==b: self.history.append(None); return False
        if self.size[a]<self.size[b]: a,b=b,a
        self.history.append((a,b,self.size[a])); self.parent[b]=a; self.size[a]+=self.size[b]; self.components-=1
        return True
    def snapshot(self): return len(self.history)
    def rollback(self,snapshot):
        if not 0<=snapshot<=len(self.history): raise ValueError('snapshot outside active history')
        while len(self.history)>snapshot:
            change=self.history.pop()
            if change is None: continue
            a,b,old_size=change; self.parent[b]=b; self.size[a]=old_size; self.components+=1
'''
add(140,'带权并查集中的weight[x]不是节点绝对值，而是x/parent[x]。路径压缩时必须同时乘上沿途比例，否则根虽找对，数值关系已损坏。回滚DSU解决另一种需求：恢复历史状态。为使修改数量可控，采用按大小合并而不做路径压缩，每次合并只记录常数个被改字段。',WEIGHTED,
'''dsu=WeightedDSU(); dsu.union('a','b',2); dsu.union('b','c',3)
for x in dsu.parent: dsu.find(x)
show_table(['变量','根','变量/根'],[(x,dsu.parent[x],dsu.weight[x]) for x in dsu.parent])
print('a/c=',dsu.ratio('a','c'))
r=RollbackDSU(4); r.union(0,1); saved=r.snapshot(); r.union(1,2); print('回滚前分量',r.components); r.rollback(saved); print('回滚后分量',r.components)''',
'''assert calc_equation([['a','b'],['b','c']],[2,3],[['a','c'],['c','a'],['x','x']])==[6.0,1/6,-1.0]
from random import Random
from collections import deque
rng=Random(140)
for _ in range(100):
    values=[rng.randrange(1,10) for _ in range(6)]; edges=[(rng.randrange(6),rng.randrange(6)) for _ in range(8)]; d=WeightedDSU(); adj={}
    for a,b in edges:
        ratio=values[a]/values[b]; d.union(a,b,ratio); adj.setdefault(a,[]).append((b,ratio)); adj.setdefault(b,[]).append((a,1/ratio))
    for a in range(7):
        for b in range(7):
            q=deque([(a,1.0)]) if a in adj else deque(); seen={a}; expected=-1.0
            while q:
                u,p=q.popleft()
                if u==b: expected=p; break
                for v,w in adj[u]:
                    if v not in seen: seen.add(v); q.append((v,p*w))
            assert isclose(d.ratio(a,b),expected,rel_tol=1e-9,abs_tol=1e-12)
r=RollbackDSU(8); edges=[]
for _ in range(300):
    if edges and rng.randrange(3)==0:
        target=rng.randrange(len(edges)+1); r.rollback(target); edges=edges[:target]
    else:
        a,b=rng.randrange(8),rng.randrange(8); r.union(a,b); edges.append((a,b))
    reach=[[i==j for j in range(8)] for i in range(8)]
    for a,b in edges: reach[a][b]=reach[b][a]=True
    for k in range(8):
        for i in range(8):
            for j in range(8): reach[i][j]|=reach[i][k] and reach[k][j]
    before=r.parent[:]
    for i in range(8):
        for j in range(8): assert (r.find(i)==r.find(j))==reach[i][j]
    assert r.parent==before and r.snapshot()==len(edges)
    assert r.components==len({r.find(i) for i in range(8)})''',
'设wx=x/rx，wy=y/ry，已知x/y=v，则rx/ry=v·wy/wx；反方向连接时取倒数。沿路径的比例相乘后仍等于节点对根的比值。回滚按相反顺序恢复父指针、旧size与分量数，正好逆转此前修改；无效union也记录占位，使快照对应操作边界。',
'带权DSU按大小加路径压缩，均摊近O(α(n))次结构操作；浮点误差按容差解释。回滚find/union O(log n)最坏，撤销t次union O(t)，空间O(n+历史长度)。快照只能回到当前历史祖先，回滚后被舍弃分支不能凭旧编号恢复。')
