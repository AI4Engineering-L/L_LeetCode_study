from course_builder import add

DSU_CODE='''class DSU:
    def __init__(self,n): self.parent=list(range(n)); self.size=[1]*n; self.components=n
    def find(self,x):
        while self.parent[x]!=x:
            self.parent[x]=self.parent[self.parent[x]]; x=self.parent[x]
        return x
    def union(self,a,b):
        a=self.find(a); b=self.find(b)
        if a==b: return False
        if self.size[a]<self.size[b]: a,b=b,a
        self.parent[b]=a; self.size[a]+=self.size[b]; self.components-=1
        return True
'''

add(79, '图建模先明确顶点、边、方向和标签范围。邻接表适合稀疏图，必须保留孤立顶点；无向边要双向存储。邻接矩阵转无向边表只取上三角（含自环），否则每条边会重复。法官问题只需入度与出度，不必搜索图。',
'''def build_adj_list(n,edges,directed=False):
    adj=[[] for _ in range(n)]
    for u,v in edges:
        if not (0<=u<n and 0<=v<n): raise ValueError('vertex outside 0..n-1')
        adj[u].append(v)
        if not directed and u!=v: adj[v].append(u)
    return adj

def adj_matrix_to_edges(matrix,directed=False):
    n=len(matrix)
    if any(len(row)!=n for row in matrix): raise ValueError('square matrix required')
    if not directed and any(bool(matrix[i][j])!=bool(matrix[j][i]) for i in range(n) for j in range(n)):
        raise ValueError('undirected adjacency matrix must be symmetric')
    return [(i,j) for i in range(n) for j in range(n) if matrix[i][j] and (directed or i<=j)]

def find_judge(n,trust):
    incoming=[0]*(n+1); outgoing=[0]*(n+1)
    for u,v in set(map(tuple,trust)): outgoing[u]+=1; incoming[v]+=1
    return next((i for i in range(1,n+1) if incoming[i]==n-1 and outgoing[i]==0),-1)
''',
'''edges=[(0,1),(1,2)]; adj=build_adj_list(4,edges,False)
show_table(['顶点','邻接顶点','度数'],[(i,a,len(a)) for i,a in enumerate(adj)])''',
'''assert build_adj_list(4,[(0,1)],False)==[[1],[0],[],[]]
assert build_adj_list(3,[(0,1)],True)==[[1],[],[]]
assert adj_matrix_to_edges([[0,1,0],[1,0,1],[0,1,0]])==[(0,1),(1,2)]
assert find_judge(2,[[1,2]])==2
assert find_judge(1,[])==1
assert find_judge(3,[[1,3],[2,3],[3,1]])==-1''',
'顶点集合独立于边集合创建，所以没有边的点也不会丢失。法官条件等价于“其他所有人都信任它，且它不信任任何人”，分别由入度n−1与出度0表达。','邻接表O(V+E)构建与存储；矩阵转换O(V²)扫描；法官O(n+E)平均时间。法官标签为1..n，与一般图0..n−1不同。')

add(80, '无向连通分量可从每个未访问顶点启动DFS。判断有向环不能仅看“是否访问过”，必须区分正在当前路径上的灰点与已完成的黑点；只有指向灰点的边才直接证明回到祖先。克隆图先创建节点映射，再复制边，才能处理环和共享邻居。',
'''from collections import deque

def count_components(n,edges):
    adj=[[] for _ in range(n)]
    for u,v in edges: adj[u].append(v); adj[v].append(u)
    seen=set(); count=0
    for start in range(n):
        if start in seen: continue
        count+=1; seen.add(start); stack=[start]
        while stack:
            for v in adj[stack.pop()]:
                if v not in seen: seen.add(v); stack.append(v)
    return count

def num_islands(grid):
    if not grid or not grid[0]: return 0
    rows,cols=len(grid),len(grid[0]); seen=set(); count=0
    for r in range(rows):
        for c in range(cols):
            if grid[r][c]!='1' or (r,c) in seen: continue
            count+=1; stack=[(r,c)]; seen.add((r,c))
            while stack:
                x,y=stack.pop()
                for nx,ny in [(x+1,y),(x-1,y),(x,y+1),(x,y-1)]:
                    if 0<=nx<rows and 0<=ny<cols and grid[nx][ny]=='1' and (nx,ny) not in seen:
                        seen.add((nx,ny)); stack.append((nx,ny))
    return count

def has_directed_cycle(adj):
    color=[0]*len(adj)
    for start in range(len(adj)):
        if color[start]: continue
        color[start]=1; stack=[(start,iter(adj[start]))]
        while stack:
            u,neighbors=stack[-1]
            try: v=next(neighbors)
            except StopIteration:
                color[u]=2; stack.pop(); continue
            if color[v]==1: return True
            if color[v]==0: color[v]=1; stack.append((v,iter(adj[v])))
    return False

class GraphNode:
    def __init__(self,val=0,neighbors=None): self.val=val; self.neighbors=[] if neighbors is None else neighbors

def clone_graph(node):
    if node is None: return None
    mapping={node:GraphNode(node.val)}; queue=deque([node])
    while queue:
        u=queue.popleft()
        for v in u.neighbors:
            if v not in mapping: mapping[v]=GraphNode(v.val); queue.append(v)
            mapping[u].neighbors.append(mapping[v])
    return mapping[node]
''',
'''show_table(['邻接表','是否有向环'],[([[1],[2],[]],has_directed_cycle([[1],[2],[]])),([[1],[2],[0]],has_directed_cycle([[1],[2],[0]]))])
show_table(['图顶点数','边','连通分量'],[(5,[(0,1),(1,2),(3,4)],count_components(5,[(0,1),(1,2),(3,4)]))])''',
'''assert count_components(0,[])==0 and count_components(4,[])==4
assert has_directed_cycle([[0]]) and not has_directed_cycle([[1,2],[2],[]])
assert num_islands([list('110'),list('001')])==2
x,y=GraphNode(7),GraphNode(7); x.neighbors=[x,y]; y.neighbors=[x]
a=clone_graph(x)
assert a is not x and a.val==7 and a.neighbors[0] is a
assert a.neighbors[1] is not y and a.neighbors[1].neighbors[0] is a
from itertools import combinations
n=4; pairs=list(combinations(range(n),2))
for mask in range(1<<len(pairs)):
    edges=[e for i,e in enumerate(pairs) if mask>>i&1]
    reach=[[i==j for j in range(n)] for i in range(n)]
    for u,v in edges: reach[u][v]=reach[v][u]=True
    for k in range(n):
        for i in range(n):
            for j in range(n): reach[i][j]|=reach[i][k] and reach[k][j]
    groups={tuple(j for j in range(n) if reach[i][j]) for i in range(n)}
    assert count_components(n,edges)==len(groups)''',
'一次搜索到达且仅到达起点所在分量。灰点仍在DFS祖先链，回到灰点闭合有向环；到黑点可能只是两条路径汇合，不能据此判环。映射按对象身份区分值相同的不同节点。','O(V+E)时间、O(V)访问状态；克隆输出O(V+E)，岛屿O(RC)。迭代DFS支持深图。')

add(81, '单位边权最短路按距离分层扩张。顶点首次入队时距离已经最短，所以应当入队时标记，而不是出队后才标记。多源BFS等价于所有源同时处于距离0层；它求最近源，不是从任意一个源开始。网格默认只有上下左右，不含对角线。',
'''from collections import deque

def bfs_distances(adj,sources):
    distance=[-1]*len(adj); queue=deque()
    for s in sources:
        if distance[s]==-1: distance[s]=0; queue.append(s)
    while queue:
        u=queue.popleft()
        for v in adj[u]:
            if distance[v]==-1: distance[v]=distance[u]+1; queue.append(v)
    return distance

def oranges_rotting(grid):
    if not grid or not grid[0]: return 0
    a=[row[:] for row in grid]; rows,cols=len(a),len(a[0]); queue=deque(); fresh=0
    for r in range(rows):
        for c in range(cols):
            if a[r][c]==2: queue.append((r,c,0))
            if a[r][c]==1: fresh+=1
    time=0
    while queue:
        r,c,time=queue.popleft()
        for nr,nc in [(r+1,c),(r-1,c),(r,c+1),(r,c-1)]:
            if 0<=nr<rows and 0<=nc<cols and a[nr][nc]==1:
                a[nr][nc]=2; fresh-=1; queue.append((nr,nc,time+1))
    return -1 if fresh else time

def update_matrix(mat):
    if not mat or not mat[0]: return []
    rows,cols=len(mat),len(mat[0]); d=[[-1]*cols for _ in range(rows)]; queue=deque()
    for r in range(rows):
        for c in range(cols):
            if mat[r][c]==0: d[r][c]=0; queue.append((r,c))
    while queue:
        r,c=queue.popleft()
        for nr,nc in [(r+1,c),(r-1,c),(r,c+1),(r,c-1)]:
            if 0<=nr<rows and 0<=nc<cols and d[nr][nc]==-1:
                d[nr][nc]=d[r][c]+1; queue.append((nr,nc))
    return d
''',
'''mat=[[0,0,0],[0,1,0],[1,1,1]]; distance=update_matrix(mat)
show_table(['行','原网格','最近0距离'],[(i,mat[i],distance[i]) for i in range(len(mat))])''',
'''assert oranges_rotting([[1,1]])==-1
assert oranges_rotting([[0,2]])==0
assert oranges_rotting([[2,1,1],[1,1,0],[0,1,1]])==4
assert update_matrix([[0,1],[1,1]])==[[0,1],[1,2]]
assert update_matrix([[1]])==[[-1]]
adj=[[1],[0,2],[1,3],[2],[]]
assert bfs_distances(adj,[0,3])==[0,1,1,0,-1]
from random import Random
rng=Random(81)
for _ in range(60):
    n=7; adj=[[j for j in range(n) if i!=j and rng.randrange(4)==0] for i in range(n)]; sources=[0,3,5]
    singles=[bfs_distances(adj,[s]) for s in sources]
    ref=[min([d[v] for d in singles if d[v]>=0],default=-1) for v in range(n)]
    assert bfs_distances(adj,sources)==ref''',
'队列距离非递减。若某顶点首次发现距离d却有更短路径，则该路径前驱应更早出队并提前发现它，矛盾。多源只是改变初始层，不改变证明。','图O(V+E)时间/O(V)空间；网格O(RC)。全1无0的矩阵是教学扩展，返回−1而非伪造有限距离。')

add(82, '依赖边u→v表示u必须先完成。入度0顶点没有尚未满足的前置条件，可以安全输出；删除它的出边后可能解锁新顶点。若最终仍有未输出顶点，则剩余子图每点都有前驱，沿前驱回溯必形成环。拓扑次序可能不唯一，测试检查每条边顺序而不是强行匹配一份列表。',
'''from collections import deque

def topological_sort(n,edges):
    adj=[[] for _ in range(n)]; indegree=[0]*n
    for u,v in edges: adj[u].append(v); indegree[v]+=1
    queue=deque(i for i in range(n) if indegree[i]==0); order=[]
    while queue:
        u=queue.popleft(); order.append(u)
        for v in adj[u]:
            indegree[v]-=1
            if indegree[v]==0: queue.append(v)
    return order if len(order)==n else None

def can_finish(n,prerequisites):
    return topological_sort(n,[(required,course) for course,required in prerequisites]) is not None

def find_order(n,prerequisites):
    order=topological_sort(n,[(required,course) for course,required in prerequisites])
    return [] if order is None else order
''',
'''edges=[(0,1),(0,2),(1,3),(2,3)]; order=topological_sort(4,edges)
show_table(['位置','顶点','必须在它前面的顶点'],[(i,v,[u for u,w in edges if w==v]) for i,v in enumerate(order)])''',
'''assert can_finish(2,[[1,0]]) and not can_finish(2,[[1,0],[0,1]])
assert topological_sort(0,[])==[] and topological_sort(1,[(0,0)]) is None
from random import Random
rng=Random(82)
for n in range(1,25):
    permutation=list(range(n)); rng.shuffle(permutation)
    edges=[(permutation[i],permutation[j]) for i in range(n) for j in range(i+1,n) if rng.randrange(5)==0]
    order=topological_sort(n,edges); position={x:i for i,x in enumerate(order)}
    assert len(order)==n and all(position[u]<position[v] for u,v in edges)
assert set(find_order(4,[]))==set(range(4))''',
'当前入度精确等于来自未输出顶点的前驱数。每次取零入度点不会违反任何边；无法继续且未结束则证明存在有向环。','O(V+E)时间与空间。prerequisites使用[course,required]输入顺序，构图时需反转。')

add(83, '并查集维护等价类，而不是完整图。find返回连通分量代表，union仅在代表不同的时候连接，重复union不能减少分量数。按大小挂接控制树高，路径压缩缩短后续查找路径。账户合并以共享邮箱为连接证据，同名本身不足以证明同一账户。',
DSU_CODE+'''
def find_redundant_connection(edges):
    dsu=DSU(max((max(e) for e in edges),default=0)+1); answer=[]
    for u,v in edges:
        if not dsu.union(u,v): answer=[u,v]
    return answer

def accounts_merge(accounts):
    dsu=DSU(len(accounts)); owner={}
    for i,account in enumerate(accounts):
        for email in account[1:]:
            if email in owner: dsu.union(i,owner[email])
            else: owner[email]=i
    groups={}
    for i,account in enumerate(accounts): groups.setdefault(dsu.find(i),set()).update(account[1:])
    return [[accounts[root][0],*sorted(emails)] for root,emails in sorted(groups.items())]
''',
'''dsu=DSU(5); rows=[]
for u,v in [(0,1),(1,2),(3,4),(0,2),(2,4)]:
    changed=dsu.union(u,v); rows.append(((u,v),changed,dsu.components,[dsu.find(i) for i in range(5)]))
show_table(['合并','是否新连接','分量数','各顶点代表'],rows)''',
'''d=DSU(3); assert d.union(0,1) and not d.union(1,0) and d.components==2
assert find_redundant_connection([[1,2],[1,3],[2,3]])==[2,3]
accounts=[['John','a@x','b@x'],['John','b@x','c@x'],['John','z@x']]
out=accounts_merge(accounts); assert sorted(out)==[['John','a@x','b@x','c@x'],['John','z@x']]
from random import Random
rng=Random(83); d=DSU(8); adj=[set() for _ in range(8)]
for _ in range(100):
    u,v=rng.randrange(8),rng.randrange(8); d.union(u,v); adj[u].add(v); adj[v].add(u)
    for s in range(8):
        seen={s}; stack=[s]
        while stack:
            for t in adj[stack.pop()]:
                if t not in seen: seen.add(t); stack.append(t)
        assert all((d.find(s)==d.find(t))==(t in seen) for t in range(8))''',
'代表不同表示当前没有连接路径，新边连接两个分量；代表相同表示边闭合了一条已有路径。压缩只把节点改挂同一根，不改变分量划分。','按大小合并加路径压缩的m次操作总O(mα(n))均摊界，空间O(n)。账户结果还需邮箱排序。普通DSU不支持任意删除边。')

add(84, '边权不再统一时，FIFO队列不能保证最早出队者距离最短。Dijkstra取当前最小暂定距离，并依赖非负边保证这个距离不会再被绕远路改善。0/1边权可用双端队列把0代价松弛放前端、1代价松弛放后端。负边应明确拒绝，而非照跑后侥幸得到答案。',
'''import heapq
from collections import deque

def dijkstra(n,adj,source):
    if any(w<0 for row in adj for _,w in row): raise ValueError('Dijkstra requires nonnegative weights')
    distance=[float('inf')]*n; distance[source]=0; heap=[(0,source)]
    while heap:
        dist,u=heapq.heappop(heap)
        if dist!=distance[u]: continue
        for v,w in adj[u]:
            if dist+w<distance[v]:
                distance[v]=dist+w; heapq.heappush(heap,(distance[v],v))
    return distance

def zero_one_bfs(n,adj,source):
    if any(w not in (0,1) for row in adj for _,w in row): raise ValueError('only 0/1 weights supported')
    distance=[float('inf')]*n; distance[source]=0; queue=deque([(0,source)])
    while queue:
        dist,u=queue.popleft()
        if dist!=distance[u]: continue
        for v,w in adj[u]:
            if dist+w<distance[v]:
                distance[v]=dist+w
                if w==0: queue.appendleft((distance[v],v))
                else: queue.append((distance[v],v))
    return distance

def network_delay_time(times,n,k):
    adj=[[] for _ in range(n)]
    for u,v,w in times: adj[u-1].append((v-1,w))
    maximum=max(dijkstra(n,adj,k-1))
    return -1 if maximum==float('inf') else maximum
''',
'''adj=[[(1,1),(2,4)],[(2,1),(3,5)],[(3,1)],[]]
show_table(['顶点','从0的最短距离'],list(enumerate(dijkstra(4,adj,0))))''',
'''assert network_delay_time([[2,1,1],[2,3,1],[3,4,1]],4,2)==2
assert network_delay_time([[1,2,1]],2,2)==-1
from random import Random
rng=Random(84)
for _ in range(150):
    n=6; edges=[(u,v,rng.randrange(2)) for u in range(n) for v in range(n) if rng.randrange(5)==0]
    adj=[[] for _ in range(n)]
    for u,v,w in edges: adj[u].append((v,w))
    ref=[float('inf')]*n; ref[0]=0
    for _ in range(n-1):
        old=ref[:]
        for u,v,w in edges: ref[v]=min(ref[v],old[u]+w)
    assert dijkstra(n,adj,0)==zero_one_bfs(n,adj,0)==ref
try: dijkstra(2,[[(1,-1)],[]],0)
except ValueError: pass
else: raise AssertionError('negative edge must be rejected')''',
'假设取出的最小暂定距离仍非最优，则更短路径上第一个未确定顶点的前驱已经确定，应已给它不更大的候选，矛盾。非负性保证后缀不能把路径变短。','二叉堆版O((V+E)log(V+E))时间/O(V+E)空间；0-1 BFS为O(V+E)时间。堆中旧条目用距离检查丢弃，不视为新的有效扩展。')

add(85, 'Bellman-Ford把“允许使用多少条边”当作逐轮放宽的限制。若第n轮仍可从源可达地改进，存在可达负环，此时不能把当前数值当有限最短路。限制中转的航班题每轮必须读取上一轮快照，禁止一次轮次内连用多条新边。Floyd则逐个放开中间顶点。',
'''def bellman_ford(n,edges,source):
    distance=[float('inf')]*n; distance[source]=0
    for _ in range(n-1):
        changed=False
        for u,v,w in edges:
            if distance[u]+w<distance[v]: distance[v]=distance[u]+w; changed=True
        if not changed: break
    negative_cycle=any(distance[u]+w<distance[v] for u,v,w in edges)
    return distance,negative_cycle

def cheapest_flights(n,flights,src,dst,k):
    distance=[float('inf')]*n; distance[src]=0
    for _ in range(k+1):
        new=distance[:]
        for u,v,w in flights: new[v]=min(new[v],distance[u]+w)
        distance=new
    return -1 if distance[dst]==float('inf') else distance[dst]

def floyd_warshall(n,edges,directed=True):
    distance=[[float('inf')]*n for _ in range(n)]
    for i in range(n): distance[i][i]=0
    for u,v,w in edges:
        distance[u][v]=min(distance[u][v],w)
        if not directed: distance[v][u]=min(distance[v][u],w)
    for k in range(n):
        for i in range(n):
            if distance[i][k]==float('inf'): continue
            for j in range(n): distance[i][j]=min(distance[i][j],distance[i][k]+distance[k][j])
    return distance

def find_the_city(n,edges,threshold):
    distance=floyd_warshall(n,edges,False)
    return min(range(n),key=lambda i:(sum(i!=j and distance[i][j]<=threshold for j in range(n)),-i))
''',
'''flights=[(0,1,100),(1,2,100),(0,2,500)]
show_table(['最多中转k','最多边数','0到2最低票价'],[(k,k+1,cheapest_flights(3,flights,0,2,k)) for k in range(3)])''',
'''f=[(0,1,100),(1,2,100),(0,2,500)]
assert cheapest_flights(3,f,0,2,0)==500 and cheapest_flights(3,f,0,2,1)==200
assert cheapest_flights(3,f,2,0,2)==-1
assert floyd_warshall(2,[(0,1,5),(0,1,2)])[0][1]==2
assert bellman_ford(3,[(0,1,1),(1,2,-3),(2,1,1)],0)[1]
assert not bellman_ford(3,[(1,2,-3),(2,1,1)],0)[1]
assert find_the_city(4,[(0,1,3),(1,2,1),(1,3,4),(2,3,1)],4)==3
from random import Random
rng=Random(85)
for _ in range(80):
    n=5; edges=[(u,v,rng.randrange(6)) for u in range(n) for v in range(n) if rng.randrange(4)==0]
    allpairs=floyd_warshall(n,edges)
    for source in range(n):
        dist,negative=bellman_ford(n,edges,source)
        assert not negative and dist==allpairs[source]''',
'无负环时最短简单路径最多n−1条边，因此足够松弛后稳定。Floyd最优路径要么不经k，要么分为i到k和k到j两段；外层k不能随意与i/j调换。','Bellman-Ford O(VE)、O(V)空间；限边路径O((k+1)E)、O(V)空间；Floyd O(V³)时间/O(V²)空间。负环时Floyd对角线可用于检测，但本函数不标记所有负无穷影响对。')

add(86, '最小生成树连接所有顶点且无环，不等同于从某源的最短路径树。割性质说明：跨越某个割的最轻边，可以加入某棵MST。Kruskal按边权连接不同分量；Prim维护已经连接的一侧与外侧之间的最轻边。断开图不存在生成树，应明确报错而不是返回一片森林成本。',
DSU_CODE+'''
import heapq

def kruskal(n,edges):
    dsu=DSU(n); chosen=[]; total=0
    for u,v,w in sorted(edges,key=lambda e:e[2]):
        if dsu.union(u,v): chosen.append((u,v,w)); total+=w
    if n and len(chosen)!=n-1: raise ValueError('graph is disconnected')
    return total,chosen

def prim(n,adj):
    if n==0: return 0,[]
    seen=set(); heap=[(0,0,-1)]; total=0; chosen=[]
    while heap and len(seen)<n:
        weight,u,parent=heapq.heappop(heap)
        if u in seen: continue
        seen.add(u); total+=weight
        if parent!=-1: chosen.append((parent,u,weight))
        for v,w in adj[u]:
            if v not in seen: heapq.heappush(heap,(w,v,u))
    if len(seen)!=n: raise ValueError('graph is disconnected')
    return total,chosen

def min_cost_connect_points(points):
    n=len(points)
    if not n: return 0
    best=[float('inf')]*n; best[0]=0; used=[False]*n; total=0
    for _ in range(n):
        u=min((i for i in range(n) if not used[i]),key=lambda i:best[i])
        total+=best[u]; used[u]=True
        for v in range(n):
            if not used[v]: best[v]=min(best[v],abs(points[u][0]-points[v][0])+abs(points[u][1]-points[v][1]))
    return total
''',
'''edges=[(0,1,1),(1,2,2),(0,2,3)]; total,chosen=kruskal(3,edges)
show_table(['选择次序','边','成本'],[(i,(u,v),w) for i,(u,v,w) in enumerate(chosen)])
show_table(['总成本'],[(total,)])''',
'''assert kruskal(1,[])[0]==0
assert kruskal(3,[(0,1,1),(1,2,2),(0,2,3)])[0]==3
assert min_cost_connect_points([[0,0],[2,2],[3,10],[5,2],[7,0]])==20
from itertools import combinations
from random import Random
rng=Random(86)
for n in range(2,6):
    for _ in range(12):
        edges=[(u,v,rng.randrange(-2,6)) for u,v in combinations(range(n),2)]
        adj=[[] for _ in range(n)]
        for u,v,w in edges: adj[u].append((v,w)); adj[v].append((u,w))
        ref=float('inf')
        for subset in combinations(edges,n-1):
            reach={0}
            for _ in range(n):
                for u,v,_ in subset:
                    if u in reach or v in reach: reach.update([u,v])
            if len(reach)==n: ref=min(ref,sum(w for _,_,w in subset))
        assert kruskal(n,edges)[0]==prim(n,adj)[0]==ref''',
'若MST不含选定割的最轻边，加入它会形成环，环上另一条跨割边不轻于它；交换不会增大成本。反复交换说明贪心选择可嵌入某棵MST。','Kruskal O(E log E)，堆Prim O(E log E)；完全点图的本章稠密Prim O(n²)时间/O(n)空间，避免显式保存全部O(n²)边。')
