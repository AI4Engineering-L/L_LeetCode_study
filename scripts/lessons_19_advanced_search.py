from course_builder import add
from lessons_07_graphs_basic import DSU_CODE

LIFT='''def euler_tour(adj,root=0):
    n=len(adj)
    if not n: return [],[],[]
    if not 0<=root<n: raise IndexError('invalid root')
    tin=[-1]*n; tout=[-1]*n; order=[]; stack=[(root,-1,False)]
    while stack:
        u,parent,exiting=stack.pop()
        if exiting: tout[u]=len(order); continue
        if tin[u]!=-1: raise ValueError('tree required')
        tin[u]=len(order); order.append(u); stack.append((u,parent,True))
        for v in reversed(adj[u]):
            if v!=parent: stack.append((v,u,False))
    if len(order)!=n: raise ValueError('connected tree required')
    return tin,tout,order

class BinaryLifting:
    def __init__(self,adj,root=0):
        self.tin,self.tout,self.order=euler_tour(adj,root); self.n=len(adj); self.depth=[0]*self.n
        parent=[-1]*self.n
        for u in self.order:
            for v in adj[u]:
                if self.tin[v]>self.tin[u]: parent[v]=u; self.depth[v]=self.depth[u]+1
        self.up=[parent]
        for _ in range(1,max(1,self.n.bit_length())):
            old=self.up[-1]; self.up.append([-1 if p==-1 else old[p] for p in old])
    def get_kth_ancestor(self,v,k):
        if not 0<=v<self.n or k<0: raise ValueError('valid vertex and nonnegative k required')
        if k>self.depth[v]: return -1
        bit=0
        while k:
            if k&1: v=self.up[bit][v]
            bit+=1; k>>=1
        return v
    def lca(self,u,v):
        if not 0<=u<self.n or not 0<=v<self.n: raise IndexError('vertex outside tree')
        if self.depth[u]<self.depth[v]: u,v=v,u
        u=self.get_kth_ancestor(u,self.depth[u]-self.depth[v])
        if u==v: return u
        for j in range(len(self.up)-1,-1,-1):
            if self.up[j][u]!=self.up[j][v]: u,v=self.up[j][u],self.up[j][v]
        return self.up[0][u]
'''
add(141,'DFS进入序把每棵子树变成连续区间[tin,tout)，注意这不是BFS顺序，也不是把每次回边都写入的完整Euler walk。倍增保存2^j步祖先，把k分解为二进制；LCA先对齐深度，再一起向上跳到最近公共祖先的下一层。',LIFT,
'''adj=[[1,2],[0,3,4],[0],[1],[1]]; tree=BinaryLifting(adj)
show_table(['顶点','tin','tout','深度','2^j祖先'],[(u,tree.tin[u],tree.tout[u],tree.depth[u],[row[u] for row in tree.up]) for u in range(len(adj))])
print('DFS进入序',tree.order,'LCA(3,4)',tree.lca(3,4))''',
'''from random import Random
from collections import deque
rng=Random(141)
for n in range(1,28):
    adj=[[] for _ in range(n)]
    for v in range(1,n):
        p=rng.randrange(v); adj[p].append(v); adj[v].append(p)
    root=rng.randrange(n); lift=BinaryLifting(adj,root); parent=[-1]*n; parent[root]=root; q=deque([root])
    while q:
        u=q.popleft()
        for v in adj[u]:
            if parent[v]==-1: parent[v]=u; q.append(v)
    def chain(v):
        out=[v]
        while v!=root: v=parent[v]; out.append(v)
        return out
    for u in range(n):
        c=chain(u)
        for k in range(n+2): assert lift.get_kth_ancestor(u,k)==(c[k] if k<len(c) else -1)
        expected={v for v in range(n) if u in chain(v)}
        assert set(lift.order[lift.tin[u]:lift.tout[u]])==expected
        for v in range(n): assert lift.lca(u,v)==next(x for x in chain(v) if x in set(c))
    assert lift.get_kth_ancestor(root,1<<100)==-1
n=1500; adj=[[] for _ in range(n)]
for i in range(n-1): adj[i].append(i+1); adj[i+1].append(i)
assert BinaryLifting(adj).get_kth_ancestor(n-1,n-1)==0''',
'DFS只有完成一个子树后才进入外部节点，所以进入时刻到退出时刻之间恰为该子树全部点。up[j][v]=up[j−1][up[j−1][v]]归纳得到2^j祖先。LCA同步提升时始终保持两点在公共祖先下方且祖先不同，最后父节点必相同且最近。',
'Euler序O(n)时间空间；倍增预处理O(n log n)时间空间，祖先/LCA查询O(log n)。不存在祖先用−1，k=0返回自身；k超过深度立即返回−1而不访问越界层。')

add(142,'当n约40时，完整2^n枚举可能太大，而2^(n/2)仍可存储。折半法枚举左右半部，随后把两半匹配问题交给排序与二分。若要求两组大小相同，只按和排序不够，还要按选中元素个数分桶，确保左右数量相加为n/2。',
'''from bisect import bisect_left

def subset_sums(nums):
    sums=[0]
    for x in nums: sums += [s+x for s in sums]
    return sums

def min_abs_difference(nums,goal):
    mid=len(nums)//2; left=subset_sums(nums[:mid]); right=sorted(subset_sums(nums[mid:])); answer=abs(goal)
    for a in left:
        p=bisect_left(right,goal-a)
        for j in (p-1,p):
            if 0<=j<len(right): answer=min(answer,abs(a+right[j]-goal))
        if answer==0: return 0
    return answer

def _sums_by_size(nums):
    buckets=[[] for _ in range(len(nums)+1)]; buckets[0]=[0]
    for i,x in enumerate(nums):
        for count in range(i+1,0,-1): buckets[count].extend(s+x for s in buckets[count-1])
    return buckets

def minimum_difference_equal_size(nums):
    if len(nums)%2: raise ValueError('even input length required')
    half=len(nums)//2; left=_sums_by_size(nums[:half]); right=_sums_by_size(nums[half:]); total=sum(nums); answer=float('inf')
    for count,values in enumerate(left):
        candidates=sorted(right[half-count])
        for a in values:
            target=(total-2*a+1)//2; p=bisect_left(candidates,target)
            for j in (p-1,p):
                if 0<=j<len(candidates): answer=min(answer,abs(total-2*(a+candidates[j])))
    return answer
''',
'''a=[3,9,7,3]; half=len(a)//2; left=_sums_by_size(a[:half]); right=_sums_by_size(a[half:])
show_table(['左侧选取数量','左和候选','对应右侧数量','右和候选'],[(k,left[k],half-k,right[half-k]) for k in range(half+1)])
print('等大小最小差',minimum_difference_equal_size(a))''',
'''assert min_abs_difference([5,-7,3,5],6)==0
assert minimum_difference_equal_size([3,9,7,3])==2
assert minimum_difference_equal_size([-36,36])==72
assert minimum_difference_equal_size([])==0
from random import Random
from itertools import combinations
rng=Random(142)
for n in range(11):
    for _ in range(20):
        a=[rng.randrange(-20,21) for _ in range(n)]; goal=rng.randrange(-30,31)
        sums=[sum(a[i] for i in range(n) if mask>>i&1) for mask in range(1<<n)]
        assert sorted(subset_sums(a))==sorted(sums)
        assert min_abs_difference(a,goal)==min(abs(x-goal) for x in sums)
        if n%2==0:
            want=min(abs(sum(a)-2*sum(a[i] for i in ids)) for ids in combinations(range(n),n//2))
            assert minimum_difference_equal_size(a)==want
assert minimum_difference_equal_size([10**30,10**30+1])==1''',
'每个完整子集唯一分解为左右两个子集；二分目标的前驱或后继必有距离目标最近的右和。等大小问题只组合count与half−count桶，精确排除数量不合法的方案。比较目标使用整数二倍表达式，不把巨大整数转换为浮点。',
'折半后时间通常O(n·2^(n/2))（含排序/二分），空间O(2^(n/2))；仍是指数算法。subset_sums保留不同子集导致的重复和，不能把它误当作不同和集合。')

add(143,'离线允许先知道所有查询并改变处理顺序，最后按原查询ID恢复结果。最短覆盖区间按左端点加入候选堆；限边权连通性按阈值逐步union；Mo算法则让查询左右端点缓慢移动，以可逆增删维护窗口统计。离线算法不适用于必须立即返回、且未来查询未知的接口。',DSU_CODE+'''
from heapq import heappush,heappop
from math import isqrt

def min_interval(intervals,queries):
    intervals=sorted(intervals); heap=[]; index=0; answer=[-1]*len(queries)
    for q,original in sorted((q,i) for i,q in enumerate(queries)):
        while index<len(intervals) and intervals[index][0]<=q:
            l,r=intervals[index]; heappush(heap,(r-l+1,r)); index+=1
        while heap and heap[0][1]<q: heappop(heap)
        if heap: answer[original]=heap[0][0]
    return answer

def distance_limited_paths_exist(n,edges,queries):
    edges=sorted(edges,key=lambda e:e[2]); ordered=sorted(enumerate(queries),key=lambda x:x[1][2]); dsu=DSU(n); index=0; answer=[False]*len(queries)
    for original,(u,v,limit) in ordered:
        while index<len(edges) and edges[index][2]<limit:
            a,b,w=edges[index]; dsu.union(a,b); index+=1
        answer[original]=dsu.find(u)==dsu.find(v)
    return answer

def mo_distinct_counts(nums,queries):
    n=len(nums); block=max(1,isqrt(n)); answer=[0]*len(queries)
    if any(not 0<=l<=r<=n for l,r in queries): raise IndexError('half-open query outside array')
    order=sorted(range(len(queries)),key=lambda i:(queries[i][0]//block,queries[i][1] if queries[i][0]//block%2==0 else -queries[i][1]))
    counts={}; left=right=0; distinct=0
    def add(i):
        nonlocal distinct
        x=nums[i]; counts[x]=counts.get(x,0)+1
        if counts[x]==1: distinct+=1
    def remove(i):
        nonlocal distinct
        x=nums[i]; counts[x]-=1
        if counts[x]==0: distinct-=1; del counts[x]
    for i in order:
        l,r=queries[i]
        while left>l: left-=1; add(left)
        while right<r: add(right); right+=1
        while left<l: remove(left); left+=1
        while right>r: right-=1; remove(right)
        answer[i]=distinct
    return answer
''',
'''nums=[1,2,1,3,2,4]; queries=[(2,6),(0,3),(1,5),(0,3),(4,4)]; answers=mo_distinct_counts(nums,queries)
show_table(['原查询ID','半开区间','不同数个数'],[(i,q,answers[i]) for i,q in enumerate(queries)])''',
'''assert min_interval([[1,4],[2,4],[3,6],[4,4]],[2,3,4,5])==[3,3,1,4]
assert distance_limited_paths_exist(2,[(0,1,2)],[(0,1,2),(0,1,3)])==[False,True]
assert mo_distinct_counts([],[(0,0)])==[0]
from random import Random
from collections import deque
rng=Random(143)
for _ in range(100):
    nums=[rng.randrange(7) for _ in range(20)]; queries=[]
    for _ in range(25):
        l=rng.randrange(21); r=rng.randrange(l,21); queries.append((l,r))
    assert mo_distinct_counts(nums,queries)==[len(set(nums[l:r])) for l,r in queries]
    intervals=[sorted(rng.sample(range(15),2)) for _ in range(8)]; qs=[rng.randrange(15) for _ in range(12)]
    assert min_interval(intervals,qs)==[min((r-l+1 for l,r in intervals if l<=q<=r),default=-1) for q in qs]
for _ in range(80):
    n=6; edges=[(rng.randrange(n),rng.randrange(n),rng.randrange(8)) for _ in range(12)]; queries=[(rng.randrange(n),rng.randrange(n),rng.randrange(9)) for _ in range(12)]; ref=[]
    for s,t,limit in queries:
        seen={s}; q=deque([s])
        while q:
            u=q.popleft()
            for a,b,w in edges:
                if w>=limit: continue
                v=b if a==u else a if b==u else None
                if v is not None and v not in seen: seen.add(v); q.append(v)
        ref.append(t in seen)
    assert distance_limited_paths_exist(n,edges,queries)==ref''',
'扫描到阈值q时，数据结构恰好包含符合阈值的对象。堆中允许保留非顶端过期区间，只要每次读答案前清除堆顶过期项。Mo每次增删准确更新元素频次与distinct，处理顺序只影响代价，不改变目标窗口统计。',
'区间与限边权查询O((N+Q)log(N+Q))级排序加堆/DSU；Mo O((N+Q)√N+QlogQ)平均字典操作，空间O(N+Q)。区间覆盖端点闭合；限边权严格小于limit；Mo内部统一半开区间。')

STATE_SEARCH='''from collections import deque
from heapq import heappush,heappop

def _bidirectional_distance(start,goal,neighbors,blocked=frozenset()):
    if start in blocked or goal in blocked: return -1
    if start==goal: return 0
    front=[{start},{goal}]; distance=[{start:0},{goal:0}]; depth=[0,0]; best=float('inf')
    while front[0] and front[1]:
        side=0 if len(front[0])<=len(front[1]) else 1; other=side^1; nxt=set()
        for u in front[side]:
            if u in distance[other]: best=min(best,distance[side][u]+distance[other][u])
            for v in neighbors(u):
                if v in blocked: continue
                value=distance[side][u]+1
                if v in distance[other]: best=min(best,value+distance[other][v])
                if v not in distance[side]: distance[side][v]=value; nxt.add(v)
        front[side]=nxt; depth[side]+=1
        if best<float('inf') and depth[0]+depth[1]>=best: return best
    return -1 if best==float('inf') else best

def open_lock(deadends,target):
    if len(target)!=4 or any(c not in '0123456789' for c in target): raise ValueError('four decimal digits required')
    def neighbors(s):
        for i,c in enumerate(s):
            for delta in (-1,1): yield s[:i]+str((int(c)+delta)%10)+s[i+1:]
    return _bidirectional_distance('0000',target,neighbors,set(deadends))

def _puzzle_neighbors(state,cols=3):
    zero=state.index(0); rows=len(state)//cols; r,c=divmod(zero,cols)
    for x,y in [(r+1,c),(r-1,c),(r,c+1),(r,c-1)]:
        if 0<=x<rows and 0<=y<cols:
            pos=x*cols+y; out=list(state); out[zero],out[pos]=out[pos],out[zero]; yield tuple(out)

def sliding_puzzle(board):
    if len(board)!=2 or any(len(row)!=3 for row in board): raise ValueError('2x3 board required')
    start=tuple(x for row in board for x in row)
    if sorted(start)!=list(range(6)): raise ValueError('tiles must be 0..5 exactly once')
    return _bidirectional_distance(start,(1,2,3,4,5,0),_puzzle_neighbors)

def shortest_path_all_nodes(graph):
    n=len(graph)
    if n<=1: return 0
    full=(1<<n)-1; q=deque((i,1<<i,0) for i in range(n)); seen={(i,1<<i) for i in range(n)}
    while q:
        u,mask,steps=q.popleft()
        for v in graph[u]:
            new=mask|1<<v
            if new==full: return steps+1
            if (v,new) not in seen: seen.add((v,new)); q.append((v,new,steps+1))
    return -1

def astar_puzzle(start,goal):
    start,goal=tuple(start),tuple(goal)
    if len(start) not in (6,9) or sorted(start)!=list(range(len(start))) or sorted(goal)!=sorted(start): raise ValueError('matching 2x3 or 3x3 permutations required')
    positions={x:divmod(i,3) for i,x in enumerate(goal)}
    def heuristic(state):
        return sum(abs(i//3-positions[x][0])+abs(i%3-positions[x][1]) for i,x in enumerate(state) if x)
    distance={start:0}; heap=[(heuristic(start),0,start)]
    while heap:
        bound,g,u=heappop(heap)
        if g!=distance[u]: continue
        if u==goal: return g
        for v in _puzzle_neighbors(u):
            candidate=g+1
            if candidate<distance.get(v,float('inf')):
                distance[v]=candidate; heappush(heap,(candidate+heuristic(v),candidate,v))
    return -1
'''
add(144,'操作序列题可以转成状态图：完整配置是顶点，一次合法操作是单位权边。双向搜索必须按整层扩展并维护已知路径上界与未扩展深度下界，而非随意在两队列第一次碰到时返回。A*把已走代价g与剩余代价下界h相加；目标首次入堆不代表最优，应在合法最小优先级弹出时终止。',STATE_SEARCH,
'''start=(1,2,3,4,0,5); goal=(1,2,3,4,5,0)
show_table(['状态','距目标最短步数'],[(s,astar_puzzle(s,goal)) for s in [start]+list(_puzzle_neighbors(start))])
print('锁0000到0009',open_lock([],'0009'))''',
'''assert open_lock(['0000'],'0000')==-1
assert open_lock([],'0000')==0 and open_lock([],'0009')==1
assert open_lock(['0201','0101','0102','1212','2002'],'0202')==6
assert sliding_puzzle([[1,2,3],[5,4,0]])==-1
assert shortest_path_all_nodes([[1,2,3],[0],[0],[0]])==4
assert shortest_path_all_nodes([[],[]])==-1
from itertools import permutations
# 一次完整反向BFS提供独立的全部2x3真值。
goal=(1,2,3,4,5,0); dist={goal:0}; q=deque([goal])
while q:
    u=q.popleft()
    for v in _puzzle_neighbors(u):
        if v not in dist: dist[v]=dist[u]+1; q.append(v)
for p in permutations(range(6)):
    expected=dist.get(p,-1)
    assert sliding_puzzle([list(p[:3]),list(p[3:])])==expected
    assert astar_puzzle(p,goal)==expected
from random import Random
rng=Random(144)
for _ in range(100):
    adj=[[] for _ in range(8)]
    for u in range(8):
        for v in range(u+1,8):
            if rng.randrange(4)==0: adj[u].append(v); adj[v].append(u)
    for s in range(8):
        distance={s:0}; q=deque([s])
        while q:
            u=q.popleft()
            for v in adj[u]:
                if v not in distance: distance[v]=distance[u]+1; q.append(v)
        for t in range(8): assert _bidirectional_distance(s,t,lambda u:adj[u])==distance.get(t,-1)''',
'单位权BFS按距离层发现状态。双向算法维护两个完整前沿，所有尚未连接的更短路径若存在，就必须在当前已发现范围形成连接；当两前沿深度之和达到已有上界后可停止。曼哈顿距离不计空格，每次移动只把一个数字移动一格，因此不高估且满足一致性；A*仍保留更小g更新和过期项过滤。',
'搜索代价按可达状态图O(V+E)或带堆O((V+E)log V)衡量，不按棋盘格子数线性计算。全节点访问状态至多n·2^n；拼图最坏为阶乘状态。双向helper要求无向可逆操作；有向图反向侧必须使用反图。')
