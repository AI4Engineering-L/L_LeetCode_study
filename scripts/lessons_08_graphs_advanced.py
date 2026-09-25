from course_builder import add

add(87, '二分图的约束是每条边两端颜色相反。匹配则要求每个点至多参加一条选定边。遇到已占用的右点不能立即放弃：沿“未匹配边、匹配边”交替行走，若到达空闲右点，就翻转整条路径，把匹配数增加1。这里用显式队列和前驱重建，避免长增广链递归溢出。',
'''from collections import deque

def is_bipartite(adj):
    color=[-1]*len(adj)
    for s in range(len(adj)):
        if color[s]!=-1: continue
        color[s]=0; q=deque([s])
        while q:
            u=q.popleft()
            for v in adj[u]:
                if color[v]==color[u]: return False
                if color[v]==-1: color[v]=1-color[u]; q.append(v)
    return True

def maximum_bipartite_matching(left_adj,right_size):
    left=[-1]*len(left_adj); right=[-1]*right_size
    for start in range(len(left)):
        q=deque([start]); seen={start}; prev={}; end=-1
        while q and end==-1:
            u=q.popleft()
            for v in left_adj[u]:
                if v in prev: continue
                prev[v]=u
                if right[v]==-1: end=v; break
                nxt=right[v]
                if nxt not in seen: seen.add(nxt); q.append(nxt)
        while end!=-1:
            u=prev[end]; old=left[u]
            left[u]=end; right[end]=u; end=old
    return sum(v!=-1 for v in left),left
''',
'''adj=[[0,1],[0],[1,2]]; size,match=maximum_bipartite_matching(adj,3)
show_table(['左点','候选右点','最终匹配'],[(u,a,match[u]) for u,a in enumerate(adj)])''',
'''assert not is_bipartite([[1,2],[0,2],[0,1]])
assert is_bipartite([[1,3],[0,2],[1,3],[0,2]])
assert maximum_bipartite_matching([[0,1],[0]],2)[0]==2
from itertools import product

def brute(adj,m,u=0,used=0):
    if u==len(adj): return 0
    return max([brute(adj,m,u+1,used)]+[1+brute(adj,m,u+1,used|(1<<v)) for v in adj[u] if not used>>v&1])
for bits in product(range(2),repeat=9):
    adj=[[v for v in range(3) if bits[u*3+v]] for u in range(3)]
    size,match=maximum_bipartite_matching(adj,3)
    assert size==brute(adj,3)
    assert len({v for v in match if v!=-1})==size
    assert all(v==-1 or v in adj[u] for u,v in enumerate(match))''',
'交替路径翻转后，内部点仍各配一条边，两个端点从空闲变为已配。若不存在增广路，却有更大匹配，两匹配的对称差必含一个增广路径，矛盾。因此逐次增广至不能增广即为最大匹配。染色时同色边正好违反二分约束。',
'染色O(V+E)；本实现每个左点一次O(V+E)搜索，总O(L(V+E))，辅助O(V)。邻接表的右点编号为0..right_size−1；匹配数组−1表示未匹配。')

SCC='''def kosaraju_scc(adj):
    n=len(adj); seen=set(); order=[]
    for s in range(n):
        if s in seen: continue
        seen.add(s); stack=[(s,iter(adj[s]))]
        while stack:
            u,it=stack[-1]
            try: v=next(it)
            except StopIteration: order.append(u); stack.pop(); continue
            if v not in seen: seen.add(v); stack.append((v,iter(adj[v])))
    rev=[[] for _ in range(n)]
    for u,a in enumerate(adj):
        for v in a: rev[v].append(u)
    component=[-1]*n; label=0
    for s in reversed(order):
        if component[s]!=-1: continue
        component[s]=label; stack=[s]
        while stack:
            for v in rev[stack.pop()]:
                if component[v]==-1: component[v]=label; stack.append(v)
        label+=1
    return component

def tarjan_scc(adj):
    n=len(adj); disc=[-1]*n; low=[0]*n; active=[]; on=[False]*n; comp=[-1]*n; clock=label=0
    for s in range(n):
        if disc[s]!=-1: continue
        disc[s]=low[s]=clock; clock+=1; active.append(s); on[s]=True
        frames=[(s,iter(adj[s]),-1)]
        while frames:
            u,it,parent=frames[-1]
            try: v=next(it)
            except StopIteration:
                frames.pop()
                if parent!=-1: low[parent]=min(low[parent],low[u])
                if low[u]==disc[u]:
                    while True:
                        v=active.pop(); on[v]=False; comp[v]=label
                        if v==u: break
                    label+=1
                continue
            if disc[v]==-1:
                disc[v]=low[v]=clock; clock+=1; active.append(v); on[v]=True
                frames.append((v,iter(adj[v]),u))
            elif on[v]: low[u]=min(low[u],disc[v])
    return comp

def condensation_graph(adj,component):
    result=[set() for _ in range(max(component,default=-1)+1)]
    for u,a in enumerate(adj):
        for v in a:
            if component[u]!=component[v]: result[component[u]].add(component[v])
    return [sorted(a) for a in result]
'''
add(88,'强连通分量是相互可达的最大顶点集合。Kosaraju通过完成时间与反图分离分量；Tarjan把尚未归属的点放在活动栈中，用low记录能回到的活动祖先。注意：访问过但已经离开活动栈的点，不可用于降低low。两种实现都用显式DFS帧。',SCC,
'''adj=[[1],[2,3],[0],[4],[3],[]]; comp=tarjan_scc(adj)
show_table(['顶点','邻居','分量'],[(i,a,comp[i]) for i,a in enumerate(adj)])
print('缩点图：',condensation_graph(adj,comp))''',
'''from itertools import product
for bits in product(range(2),repeat=9):
    adj=[[v for v in range(3) if bits[u*3+v]] for u in range(3)]
    reach=[[i==j or j in adj[i] for j in range(3)] for i in range(3)]
    for k in range(3):
        for i in range(3):
            for j in range(3): reach[i][j]|=reach[i][k] and reach[k][j]
    a=kosaraju_scc(adj); b=tarjan_scc(adj)
    for i in range(3):
        for j in range(3): assert (a[i]==a[j])==(b[i]==b[j])==(reach[i][j] and reach[j][i])
    dag=condensation_graph(adj,b)
    def walk(u,path):
        assert u not in path
        for v in dag[u]: walk(v,path|{u})
    for u in range(len(dag)): walk(u,set())
chain=[[i+1] for i in range(1499)]+[[]]
assert len(set(tarjan_scc(chain)))==1500
assert tarjan_scc([])==kosaraju_scc([])==[]''',
'Tarjan在low[u]=disc[u]时，从活动栈顶到u恰构成一个SCC：它们可沿DFS树到达，且未能到达更早的活动祖先。缩点图若有环，则环上分量相互可达，本应合并，故缩点图必为DAG。分量编号只是标签，不比较具体编号。',
'两算法O(V+E)时间、O(V+E)辅助空间（Kosaraju保存反图）；缩点去重平均O(V+E)，排序输出另加各分量出边排序代价。')

LOWLINK='''def _undirected_lowlink(n,edges):
    adj=[[] for _ in range(n)]
    for eid,(u,v) in enumerate(edges): adj[u].append((v,eid)); adj[v].append((u,eid))
    disc=[-1]*n; low=[0]*n; parent=[-1]*n; pe=[-1]*n; children=[0]*n
    bridges=[]; cuts=set(); clock=0
    for s in range(n):
        if disc[s]!=-1: continue
        disc[s]=low[s]=clock; clock+=1; stack=[(s,iter(adj[s]))]
        while stack:
            u,it=stack[-1]
            try: v,eid=next(it)
            except StopIteration:
                stack.pop(); p=parent[u]
                if p==-1:
                    if children[u]>1: cuts.add(u)
                else:
                    low[p]=min(low[p],low[u])
                    if low[u]>disc[p]: bridges.append(pe[u])
                    if parent[p]!=-1 and low[u]>=disc[p]: cuts.add(p)
                continue
            if eid==pe[u]: continue
            if disc[v]==-1:
                parent[v]=u; pe[v]=eid; children[u]+=1
                disc[v]=low[v]=clock; clock+=1; stack.append((v,iter(adj[v])))
            else: low[u]=min(low[u],disc[v])
    return bridges,cuts,disc,low

def find_bridges(n,edges):
    ids,_,_,_=_undirected_lowlink(n,edges)
    return sorted(tuple(sorted(edges[i])) for i in ids)

def articulation_points(n,edges):
    return sorted(_undirected_lowlink(n,edges)[1])
'''
add(89,'树边的孩子若能绕路到祖先，删掉这条树边不会断开。桥用严格条件low[child]>disc[parent]；割点用low[child]≥disc[parent]，但DFS根要单独检查孩子数。多重边必须按边ID跳过父边，否则第二条平行边会被错删。',LOWLINK,
'''edges=[(0,1),(1,2),(2,0),(1,3)]; _,_,disc,low=_undirected_lowlink(4,edges)
show_table(['顶点','发现时间','low'],[(i,disc[i],low[i]) for i in range(4)])
print('桥',find_bridges(4,edges),'割点',articulation_points(4,edges))''',
'''from random import Random
rng=Random(89)
def components(n,edges,removed=None):
    seen=set(); count=0
    for s in range(n):
        if s==removed or s in seen: continue
        count+=1; stack=[s]; seen.add(s)
        while stack:
            u=stack.pop()
            for a,b in edges:
                if removed in (a,b): continue
                v=b if a==u else a if b==u else None
                if v is not None and v not in seen: seen.add(v); stack.append(v)
    return count
for _ in range(180):
    n=rng.randrange(1,7); edges=[(rng.randrange(n),rng.randrange(n)) for _ in range(rng.randrange(10))]
    base=components(n,edges)
    want=sorted(tuple(sorted(e)) for i,e in enumerate(edges) if components(n,edges[:i]+edges[i+1:])>base)
    assert find_bridges(n,edges)==want
    assert articulation_points(n,edges)==[u for u in range(n) if components(n,edges,u)>base]
assert find_bridges(2,[(0,1),(0,1)])==[]
assert articulation_points(2,[(0,1)])==[]''',
'low值概括DFS子树经至多一条回边可触达的最早发现时间。桥的严格不等式表示子树只能经过父边离开；割点允许回到父点本身，但这在删除父点后无效，所以采用非严格不等式。根的子树间没有祖先可连，孩子数大于1才是割点。',
'O(V+E)搜索与空间；对输出排序另有O(E log E+V log V)上界。支持断开图、平行边和自环。')

add(90,'欧拉路径要求每条边恰好使用一次，而不是每个顶点一次。沿未用边一直走，无路可走时才把顶点加入逆序答案，相当于把局部回路插入完整行程。机票使用多重边；重复机票不能去重。字典序要求对出边排序，终局还必须检查确实消耗了全部机票。',
'''from collections import defaultdict,Counter

def _hierholzer(edges,start):
    adj=defaultdict(list)
    for u,v in edges: adj[u].append(v)
    for a in adj.values(): a.sort(reverse=True)
    stack=[start]; out=[]
    while stack:
        if adj[stack[-1]]: stack.append(adj[stack[-1]].pop())
        else: out.append(stack.pop())
    path=out[::-1]
    if len(path)!=len(edges)+1 or Counter(zip(path,path[1:]))!=Counter(map(tuple,edges)): return None
    return path

def eulerian_path(edges):
    if not edges: return []
    delta=Counter()
    for u,v in edges: delta[u]+=1; delta[v]-=1
    starts=[u for u,d in delta.items() if d==1]; ends=[u for u,d in delta.items() if d==-1]
    if any(abs(d)>1 for d in delta.values()) or not (len(starts)==len(ends)==1 or not starts and not ends): return None
    start=starts[0] if starts else min(u for u,v in edges)
    return _hierholzer(edges,start)

def find_itinerary(tickets):
    path=_hierholzer(tickets,'JFK')
    if path is None: raise ValueError('no itinerary using all tickets from JFK')
    return path
''',
'''tickets=[('JFK','KUL'),('JFK','NRT'),('NRT','JFK')]; path=find_itinerary(tickets)
show_table(['步骤','起点','终点'],[(i,u,v) for i,(u,v) in enumerate(zip(path,path[1:]),1)])''',
'''assert find_itinerary([('JFK','KUL'),('JFK','NRT'),('NRT','JFK')])==['JFK','NRT','JFK','KUL']
assert eulerian_path([(0,1),(0,1),(1,0)])==[0,1,0,1]
assert eulerian_path([(0,1),(2,3)]) is None
assert eulerian_path([])==[]
from itertools import permutations
edges=[('JFK','A'),('A','JFK'),('JFK','B'),('B','JFK'),('JFK','A')]
valid=[]
for perm in permutations(edges):
    path=['JFK']
    for u,v in perm:
        if path[-1]!=u: break
        path.append(v)
    if len(path)==len(edges)+1: valid.append(path)
assert find_itinerary(edges)==min(valid)''',
'逆序退出将闭合支路拼到恰当顶点；出边每弹出一次只消耗该条边。可行欧拉条件下，按字典序尝试的闭合支路可以先拼接，无法提前闭合的终止支路被留到末尾，得到字典序最小的完整行程。最终Counter校验排除不连通和非法拼接。',
'排序出边O(E log E)，遍历O(E)，辅助O(V+E)。通用接口要求顶点标签可排序且可哈希；返回None表示无完整欧拉路径。')

add(91,'函数图每个点至多一条出边，因此每个连通块最终要么终止，要么进入一个环。找最长环只需区分本次路径和旧路径。会议座位中，长度≥3的环不能再接入链；互相喜欢的二元环两端却各能接一条最长入链，且不同二元环可以拼接。',
'''from collections import deque

def longest_cycle(edges):
    visited=[False]*len(edges); answer=-1
    for s in range(len(edges)):
        position={}; u=s
        while u!=-1 and not visited[u]:
            visited[u]=True; position[u]=len(position); u=edges[u]
        if u in position: answer=max(answer,len(position)-position[u])
    return answer

def maximum_invitations(favorite):
    n=len(favorite); degree=[0]*n; depth=[1]*n
    for v in favorite: degree[v]+=1
    q=deque(i for i,d in enumerate(degree) if d==0)
    while q:
        u=q.popleft(); v=favorite[u]; depth[v]=max(depth[v],depth[u]+1); degree[v]-=1
        if degree[v]==0: q.append(v)
    paired=best=0; seen=set()
    for s in range(n):
        if not degree[s] or s in seen: continue
        cycle=[]; u=s
        while u not in seen: seen.add(u); cycle.append(u); u=favorite[u]
        if len(cycle)==2: paired+=sum(depth[v] for v in cycle)
        else: best=max(best,len(cycle))
    return max(paired,best)
''',
'''favorite=[1,0,1,2,5,4]; print('可邀请人数',maximum_invitations(favorite))
show_table(['员工','喜欢的人'],list(enumerate(favorite)))''',
'''assert longest_cycle([3,3,4,2,3])==3
assert longest_cycle([2,-1,3,1])==-1
assert longest_cycle([0])==1
assert maximum_invitations([1,0,3,2])==4
from itertools import permutations
from random import Random
rng=Random(91)
def brute(f):
    n=len(f); best=0
    for k in range(2,n+1):
        for p in permutations(range(n),k):
            if p[0]!=min(p): continue
            if all(f[p[i]] in (p[i-1],p[(i+1)%k]) for i in range(k)): best=k; break
    return best
for n in range(2,7):
    for _ in range(12):
        f=[rng.choice([j for j in range(n) if j!=i]) for i in range(n)]
        assert maximum_invitations(f)==brute(f)''',
'入度剥离消除所有树枝，depth[v]保留到达v的最长链长；残余顶点恰为环。二元环两端各有一个可用邻座，因此可以接链，其余环每个点的两个邻座均已占满。取所有二元环链之和与单个长环最大值，即覆盖所有可行结构。',
'O(n)时间与空间。longest_cycle允许−1和教学自环；maximum_invitations要求n≥2且favorite[i]≠i，符合本章座位契约。')

FLOW='''from collections import deque

class Dinic:
    def __init__(self,n): self.adj=[[] for _ in range(n)]; self.original=[]
    def add_edge(self,u,v,capacity):
        if capacity<0: raise ValueError('nonnegative capacity required')
        i,j=len(self.adj[u]),len(self.adj[v])
        self.adj[u].append([v,j+(u==v),capacity])
        self.adj[v].append([u,i,0]); self.original.append((u,i,capacity))
    def _levels(self,s):
        level=[-1]*len(self.adj); level[s]=0; q=deque([s])
        while q:
            u=q.popleft()
            for v,rev,cap in self.adj[u]:
                if cap>0 and level[v]==-1: level[v]=level[u]+1; q.append(v)
        return level
    def _send_one(self,s,t,level,ptr):
        vertices=[s]; path=[]; bottleneck=[float('inf')]
        while vertices:
            u=vertices[-1]
            if u==t:
                amount=bottleneck[-1]
                for a,i in path:
                    edge=self.adj[a][i]; edge[2]-=amount
                    self.adj[edge[0]][edge[1]][2]+=amount
                return amount
            while ptr[u]<len(self.adj[u]):
                v,rev,cap=self.adj[u][ptr[u]]
                if cap>0 and level[v]==level[u]+1: break
                ptr[u]+=1
            if ptr[u]==len(self.adj[u]):
                vertices.pop(); bottleneck.pop()
                if path: parent,_=path.pop(); ptr[parent]+=1
            else:
                i=ptr[u]; v,rev,cap=self.adj[u][i]
                path.append((u,i)); vertices.append(v); bottleneck.append(min(bottleneck[-1],cap))
        return 0
    def max_flow(self,source,sink):
        if source==sink: raise ValueError('source and sink must differ')
        total=0
        while True:
            level=self._levels(source)
            if level[sink]==-1: return total
            ptr=[0]*len(self.adj)
            while True:
                amount=self._send_one(source,sink,level,ptr)
                if not amount: break
                total+=amount
    def min_cut_reachable(self,source):
        return {i for i,d in enumerate(self._levels(source)) if d!=-1}
    def edges_with_flow(self):
        return [(u,self.adj[u][i][0],cap,cap-self.adj[u][i][2]) for u,i,cap in self.original]

def min_cut_reachable(network,source): return network.min_cut_reachable(source)

def matching_via_flow(left_adj,right_size):
    left_size=len(left_adj); source=left_size+right_size; sink=source+1; net=Dinic(sink+1)
    for u,a in enumerate(left_adj):
        net.add_edge(source,u,1)
        for v in set(a): net.add_edge(u,left_size+v,1)
    for v in range(right_size): net.add_edge(left_size+v,sink,1)
    return net.max_flow(source,sink)
'''
add(92,'最大流同时受容量上界和中间点守恒约束。反向残量边表示撤销先前选择的能力，而非原图真的多了一条运输路线。Dinic先构建最短层次图，再在当前层次图中发送阻塞流。下面使用显式路径栈替代递归DFS；当前弧指针避免反复扫描已无用的边。',FLOW,
'''net=Dinic(4)
for edge in [(0,1,3),(0,2,2),(1,2,1),(1,3,2),(2,3,3)]: net.add_edge(*edge)
print('最大流',net.max_flow(0,3),'源侧最小割',net.min_cut_reachable(0))
show_table(['起点','终点','容量','流量'],net.edges_with_flow())''',
'''from random import Random
rng=Random(92)
for n in range(2,7):
    for _ in range(25):
        edges=[(rng.randrange(n),rng.randrange(n),rng.randrange(5)) for _ in range(12)]
        net=Dinic(n)
        for e in edges: net.add_edge(*e)
        value=net.max_flow(0,n-1)
        cuts=[]
        for mask in range(1<<n):
            if not mask&1 or mask>>(n-1)&1: continue
            cuts.append(sum(c for u,v,c in edges if mask>>u&1 and not mask>>v&1))
        assert value==min(cuts)
        balance=[0]*n
        for u,v,cap,f in net.edges_with_flow():
            assert 0<=f<=cap; balance[u]-=f; balance[v]+=f
        assert balance[0]==-value and balance[-1]==value and all(x==0 for x in balance[1:-1])
        reach=net.min_cut_reachable(0)
        assert sum(c for u,v,c in edges if u in reach and v not in reach)==value
        assert net.max_flow(0,n-1)==0 # 第二次调用返回新增流量
assert matching_via_flow([[0,1],[0]],2)==2
assert matching_via_flow([[],[]],3)==0''',
'每次增广保持容量可行与守恒，反向边保持可撤销性。残量图中源无法到达汇时，从可达集到不可达集的正向边已饱和、反向净流为0，割容量等于流量；任何流都不超过任何割，因此同时得到最大流和最小割证明。',
'一般图Dinic的标准上界O(V²E)，辅助O(V+E)；本实现阻塞流采用逐路径发送和当前弧。容量使用非负整数，重复max_flow返回在当前残量网络上新增加的流量。支持平行边和自环。')
