from course_builder import add
from lessons_06_trees import TREE, POST

ORDER='''def _tree_order(adj,root=0):
    if not adj: return [],[]
    parent=[-1]*len(adj); parent[root]=root; order=[root]
    for u in order:
        for v in adj[u]:
            if v==parent[u]: continue
            if parent[v]!=-1: raise ValueError('tree required')
            parent[v]=u; order.append(v)
    if len(order)!=len(adj): raise ValueError('connected tree required')
    return parent,order
'''
add(109,'树上没有跨子树边，因此给定父节点状态后，各子树可以独立优化。选点问题保存“选当前点/不选当前点”。摄像头把子树压成三种状态：当前未覆盖、当前放相机、已被子节点覆盖；空孩子视为已覆盖，避免在空位置安装相机。',TREE+POST+ORDER+'''
def rob_tree(root):
    dp={None:(0,0)}
    for node in _postorder_nodes(root):
        l0,l1=dp[node.left]; r0,r1=dp[node.right]
        dp[node]=(max(l0,l1)+max(r0,r1),node.val+l0+r0)
    return max(dp[root])

def min_camera_cover(root):
    state={None:2}; count=0
    for node in _postorder_nodes(root):
        left,right=state[node.left],state[node.right]
        if 0 in (left,right): state[node]=1; count+=1
        elif 1 in (left,right): state[node]=2
        else: state[node]=0
    return count+(root is not None and state[root]==0)

def tree_independent_set(adj,weights):
    if len(adj)!=len(weights): raise ValueError('one weight per vertex')
    parent,order=_tree_order(adj); dp=[[0,0] for _ in adj]
    for u in reversed(order):
        dp[u][1]=weights[u]
        for v in adj[u]:
            if parent[v]==u: dp[u][0]+=max(dp[v]); dp[u][1]+=dp[v][0]
    return max(dp[0]) if dp else 0
''',
'''root=tree_from_level([3,2,3,None,3,None,1]); dp={None:(0,0)}; rows=[]
for node in _postorder_nodes(root):
    a,b=dp[node.left]; c,d=dp[node.right]; dp[node]=(max(a,b)+max(c,d),node.val+a+c); rows.append((node.val,*dp[node]))
show_table(['节点值','不选','选'],rows)
print('最少相机',min_camera_cover(root))''',
'''assert rob_tree(tree_from_level([3,2,3,None,3,None,1]))==7
assert min_camera_cover(TreeNode())==1 and min_camera_cover(None)==0
from random import Random
rng=Random(109)
for n in range(1,9):
    for _ in range(20):
        nodes=[TreeNode(rng.randrange(-2,7)) for _ in range(n)]; edges=[]
        available=[0]
        for v in range(1,n):
            p=rng.choice(available); node=nodes[p]
            if node.left is None: node.left=nodes[v]
            else: node.right=nodes[v]; available.remove(p)
            available.append(v); edges.append((p,v))
        adj=[[] for _ in range(n)]
        for u,v in edges: adj[u].append(v); adj[v].append(u)
        best=max(sum(nodes[i].val for i in range(n) if mask>>i&1) for mask in range(1<<n) if all(not(mask>>u&1 and mask>>v&1) for u,v in edges))
        assert rob_tree(nodes[0])==tree_independent_set(adj,[x.val for x in nodes])==best
        cameras=min(mask.bit_count() for mask in range(1<<n) if all(mask>>i&1 or any(mask>>j&1 for j in adj[i]) for i in range(n)))
        assert min_camera_cover(nodes[0])==cameras''',
'独立集转移直接来自父子不能同时选。摄像头若某孩子未覆盖，放在当前点可同时覆盖该孩子、当前点及父点，不劣于在孩子上补装；孩子均已覆盖且无相机时，把是否覆盖当前点的决定留给父点最灵活。根没有父点，最后必须单独补相机。',
'O(n)时间，本实现用字典保存所有子树状态，辅助O(n)，不将其误写为仅O(h)。邻接表接口要求连通无向树；二叉树对象不得含共享孩子或环。')

add(110,'只算一个根的答案不难，重复n遍却浪费了相邻根之间的大量共享信息。从u移根到孩子v，v子树内的size[v]个点距离减1，其余n−size[v]个点距离加1。方向猜测也是局部变化：只有跨越的那条边翻转，其他父子方向不变。',ORDER+'''
def _adj_from_edges(n,edges):
    adj=[[] for _ in range(n)]
    for u,v in edges: adj[u].append(v); adj[v].append(u)
    return adj

def sum_of_distances_in_tree(n,edges):
    if not n: return []
    adj=_adj_from_edges(n,edges); parent,order=_tree_order(adj); size=[1]*n; depth=[0]*n
    for u in order[1:]: depth[u]=depth[parent[u]]+1
    for u in reversed(order[1:]): size[parent[u]]+=size[u]
    answer=[0]*n; answer[0]=sum(depth)
    for u in order[1:]: answer[u]=answer[parent[u]]+n-2*size[u]
    return answer

def root_count(edges,guesses,k):
    n=len(edges)+1; adj=_adj_from_edges(n,edges); parent,order=_tree_order(adj); guesses=set(map(tuple,guesses))
    score=[0]*n; score[0]=sum((parent[u],u) in guesses for u in order[1:])
    for u in order[1:]:
        p=parent[u]; score[u]=score[p]-((p,u) in guesses)+((u,p) in guesses)
    return sum(x>=k for x in score)
''',
'''edges=[(0,1),(1,2),(1,3),(3,4)]; answer=sum_of_distances_in_tree(5,edges)
show_table(['根','距离总和'],list(enumerate(answer)))''',
'''assert sum_of_distances_in_tree(3,[(0,1),(1,2)])==[3,2,3]
assert sum_of_distances_in_tree(1,[])==[0]
from random import Random
from collections import deque
rng=Random(110)
for n in range(1,16):
    edges=[(rng.randrange(v),v) for v in range(1,n)]; adj=_adj_from_edges(n,edges)
    guesses=[(v,u) if rng.randrange(2) else (u,v) for u,v in edges]; reference=[]; scores=[]
    for root in range(n):
        d=[-1]*n; d[root]=0; q=deque([root]); pairs=set()
        while q:
            u=q.popleft()
            for v in adj[u]:
                if d[v]==-1: d[v]=d[u]+1; q.append(v); pairs.add((u,v))
        reference.append(sum(d)); scores.append(len(pairs&set(guesses)))
    assert sum_of_distances_in_tree(n,edges)==reference
    for k in range(n+1): assert root_count(edges,guesses,k)==sum(x>=k for x in scores)''',
'删除边(u,v)将树分成互补两部分，任意点到两个端点的路径必须经过其中一个端点，故距离变化恰为±1。先算根0，再沿树边传播的归纳覆盖全部根。方向得分只扣除旧方向并加入新方向。',
'O(n+|guesses|)平均时间和O(n+|guesses|)空间。guesses按集合解释；编号0..n−1，无向边构成树。')

add(111,'DAG上的最长路可以按拓扑序直接松弛；不需要Dijkstra，因为无环性已经给出了依赖顺序。严格递增矩阵沿数值上升连边，天然没有环。颜色路径值需保存每种颜色的最大频数，而非只保留一个当前最优颜色；不同后继可能需要不同颜色状态。',
'''from collections import deque

def longest_increasing_path(matrix):
    if not matrix or not matrix[0]: return 0
    m,n=len(matrix),len(matrix[0]); indegree=[[0]*n for _ in range(m)]
    def neighbors(r,c):
        for x,y in [(r+1,c),(r-1,c),(r,c+1),(r,c-1)]:
            if 0<=x<m and 0<=y<n: yield x,y
    for r in range(m):
        for c in range(n): indegree[r][c]=sum(matrix[x][y]<matrix[r][c] for x,y in neighbors(r,c))
    q=deque((r,c) for r in range(m) for c in range(n) if indegree[r][c]==0); layers=0
    while q:
        layers+=1
        for _ in range(len(q)):
            r,c=q.popleft()
            for x,y in neighbors(r,c):
                if matrix[x][y]>matrix[r][c]:
                    indegree[x][y]-=1
                    if indegree[x][y]==0: q.append((x,y))
    return layers

def largest_path_value(colors,edges):
    n=len(colors); adj=[[] for _ in range(n)]; degree=[0]*n
    for u,v in edges: adj[u].append(v); degree[v]+=1
    dp=[[0]*26 for _ in range(n)]; q=deque(i for i,d in enumerate(degree) if d==0); visited=best=0
    while q:
        u=q.popleft(); visited+=1; dp[u][ord(colors[u])-97]+=1; best=max(best,max(dp[u]))
        for v in adj[u]:
            for c in range(26): dp[v][c]=max(dp[v][c],dp[u][c])
            degree[v]-=1
            if degree[v]==0: q.append(v)
    return best if visited==n else -1

def minimum_course_time(n,relations,time):
    adj=[[] for _ in range(n)]; degree=[0]*n; end=list(time)
    for u,v in relations: adj[u-1].append(v-1); degree[v-1]+=1
    q=deque(i for i,d in enumerate(degree) if d==0); visited=0
    while q:
        u=q.popleft(); visited+=1
        for v in adj[u]:
            end[v]=max(end[v],end[u]+time[v]); degree[v]-=1
            if degree[v]==0: q.append(v)
    if visited!=n: raise ValueError('cyclic prerequisites')
    return max(end,default=0)
''',
'''matrix=[[9,9,4],[6,6,8],[2,1,1]]
show_table(['行','高度'],list(enumerate(matrix)))
print('严格递增最长路径',longest_increasing_path(matrix))
print('并行课程总时长',minimum_course_time(3,[(1,3),(2,3)],[3,2,5]))''',
'''assert longest_increasing_path([[9,9,4],[6,6,8],[2,1,1]])==4
assert longest_increasing_path([[7,7],[7,7]])==1
assert largest_path_value('abaca',[(0,1),(0,2),(2,3),(3,4)])==3
assert largest_path_value('a',[(0,0)])==-1
assert minimum_course_time(3,[(1,3),(2,3)],[3,2,5])==8
from random import Random
from collections import Counter
rng=Random(111)
for n in range(1,8):
    for _ in range(20):
        edges=[(u,v) for u in range(n) for v in range(u+1,n) if rng.randrange(3)==0]; colors=''.join(rng.choice('abc') for _ in range(n)); times=[rng.randrange(1,5) for _ in range(n)]
        adj=[[] for _ in range(n)]
        for u,v in edges: adj[u].append(v)
        def paths(u):
            yield [u]
            for v in adj[u]:
                for p in paths(v): yield [u]+p
        all_paths=[p for u in range(n) for p in paths(u)]
        assert largest_path_value(colors,edges)==max(max(Counter(colors[u] for u in p).values()) for p in all_paths)
        assert minimum_course_time(n,[(u+1,v+1) for u,v in edges],times)==max(sum(times[u] for u in p) for p in all_paths)''',
'拓扑弹出u时所有前驱已完成，转移可安全取前驱答案的最大值。矩阵Kahn层数等于最长依赖链长度；不是到某个起点的最短距离。课程允许无限并行，开课时间取所有前置完成时间最大值；资源受限调度不是这个模型。',
'矩阵O(mn)时间空间；颜色DP O(26(V+E))时间O(26V+E)空间；课程O(V+E)时间空间。颜色限小写英文字母，课程关系使用1-based编号。')

add(112,'把小集合编码成mask后，“已经覆盖哪些技能”“已经访问哪些顶点”变成可哈希状态。状态必须保留会影响未来的全部信息：旅行问题还需要最后位置；贴纸可把剩余字符计数压成元组。指数复杂度仍然存在，压缩只是让它可控而非变成多项式。',
'''from functools import cache
from collections import Counter

def smallest_sufficient_team(skills,people):
    pos={s:i for i,s in enumerate(skills)}; full=(1<<len(skills))-1; dp={0:()}
    for i,person in enumerate(people):
        mask=0
        for s in person:
            if s in pos: mask|=1<<pos[s]
        for covered,team in list(dp.items()):
            new=covered|mask
            if new not in dp or len(team)+1<len(dp[new]): dp[new]=team+(i,)
    return list(dp[full]) if full in dp else None

def min_stickers(stickers,target):
    letters=sorted(set(target)); wanted=Counter(target); vectors=[tuple(Counter(s)[c] for c in letters) for s in stickers]
    @cache
    def f(state):
        if not any(state): return 0
        first=next(i for i,x in enumerate(state) if x); best=float('inf')
        for v in vectors:
            if not v[first]: continue
            new=tuple(max(0,x-y) for x,y in zip(state,v)); best=min(best,1+f(new))
        return best
    answer=f(tuple(wanted[c] for c in letters))
    return -1 if answer==float('inf') else answer

def hamiltonian_path_dp(cost):
    n=len(cost)
    if not n: return 0
    if any(len(row)!=n for row in cost): raise ValueError('square cost matrix required')
    dp=[[float('inf')]*n for _ in range(1<<n)]
    for u in range(n): dp[1<<u][u]=0
    for mask in range(1<<n):
        for u in range(n):
            if not mask>>u&1: continue
            for v in range(n):
                if not mask>>v&1: dp[mask|1<<v][v]=min(dp[mask|1<<v][v],dp[mask][u]+cost[u][v])
    return min(dp[-1])
''',
'''skills=['python','sql','js']; people=[['python'],['sql'],['sql','js']]
show_table(['人','技能','掩码'],[(i,p,format(sum(1<<skills.index(s) for s in set(p)),'03b')) for i,p in enumerate(people)])
print('最小团队',smallest_sufficient_team(skills,people))''',
'''assert smallest_sufficient_team(['a'],[[],['b']]) is None
assert smallest_sufficient_team([],[])==[]
assert min_stickers(['with','example','science'],'thehat')==3
assert min_stickers(['notice','possible'],'basicbasic')==-1
from itertools import permutations
from random import Random
rng=Random(112)
for n in range(1,8):
    cost=[[rng.randrange(-2,8) for _ in range(n)] for _ in range(n)]
    assert hamiltonian_path_dp(cost)==min(sum(cost[u][v] for u,v in zip(p,p[1:])) for p in permutations(range(n)))
for _ in range(100):
    skills=['a','b','c']; people=[[s for s in skills if rng.randrange(2)] for _ in range(6)]
    team=smallest_sufficient_team(skills,people)
    valid=[mask for mask in range(1<<6) if set().union(*(set(people[i]) for i in range(6) if mask>>i&1))==set(skills)]
    if valid:
        assert len(team)==min(x.bit_count() for x in valid)
        assert set().union(*(set(people[i]) for i in team))==set(skills)
        assert len(team)==len(set(team))
    else: assert team is None''',
'团队每人只处理一轮，读取快照防止本轮重复选择；对同一个覆盖mask，人数更多的方案被支配。贴纸选取顺序无关，可强制下一张覆盖首个未满足字符来剪枝；每次该坐标严格减少，递归终止。Hamiltonian状态按最后一条边追加一个未访问点，既无重复又覆盖所有路径。',
'团队O(P·2^S·S)保守时间（含元组复制），O(S·2^S)空间；贴纸状态数至多∏(字符需求数+1)；Hamiltonian O(n²2^n)时间O(n2^n)空间。缺失边用+∞，无可行Hamiltonian路径返回+∞。')

add(113,'数位DP不是枚举每个整数，而是枚举数字前缀的等价状态。tight表示是否仍受上界相同前缀限制；started区分“尚未开始”的前导零和真正数字0。互异数字用mask记录已使用数字。空构造不代表正整数，所以末态需要排除0。',
'''from functools import cache

def count_special_numbers(n):
    if n<=0: return 0
    digits=list(map(int,str(n)))
    @cache
    def f(i,mask,tight,started):
        if i==len(digits): return int(started)
        limit=digits[i] if tight else 9; total=0
        for d in range(limit+1):
            new_tight=tight and d==digits[i]
            if not started and d==0: total+=f(i+1,mask,new_tight,False)
            elif not mask>>d&1: total+=f(i+1,mask|1<<d,new_tight,True)
        return total
    return f(0,0,True,False)

def count_digit_one(n):
    if n<=0: return 0
    digits=list(map(int,str(n)))
    @cache
    def f(i,tight):
        if i==len(digits): return 1,0
        count=ones=0
        for d in range((digits[i] if tight else 9)+1):
            ways,tail_ones=f(i+1,tight and d==digits[i]); count+=ways; ones+=tail_ones+(d==1)*ways
        return count,ones
    return f(0,True)[1]

def count_from_digit_set(digits,n):
    if n<=0: return 0
    allowed={int(d) for d in digits}
    if not allowed<=set(range(10)): raise ValueError('single decimal digits required')
    bound=list(map(int,str(n)))
    @cache
    def f(i,tight,started):
        if i==len(bound): return int(started)
        limit=bound[i] if tight else 9; total=0
        if not started: total+=f(i+1,tight and bound[i]==0,False)
        for d in sorted(allowed):
            if d>limit or not started and d==0: continue
            total+=f(i+1,tight and d==bound[i],True)
        return total
    return f(0,True,False)
''',
'''show_table(['上界','互异数字正整数个数','数字1出现次数','仅{0,1,3}构成'],[(n,count_special_numbers(n),count_digit_one(n),count_from_digit_set(['0','1','3'],n)) for n in [0,9,20,99,135]])
print('10以内的一层mask状态：',[(d,format(1<<d,'010b')) for d in range(1,5)])''',
'''assert count_special_numbers(20)==19 and count_special_numbers(135)==110
assert count_digit_one(13)==6
assert count_special_numbers(0)==count_digit_one(0)==count_from_digit_set(['0'],20)==0
for n in range(251):
    assert count_special_numbers(n)==sum(len(set(str(x)))==len(str(x)) for x in range(1,n+1))
    assert count_digit_one(n)==sum(str(x).count('1') for x in range(n+1))
    for digits in ([],['0','1'],['1','3','5'],['0','2','9']):
        assert count_from_digit_set(digits,n)==sum(set(str(x))<=set(digits) for x in range(1,n+1))''',
'相同位置、约束状态与mask具有完全相同的后续选择，因此可合并。前导零不占用mask，也不要求属于允许数字集；一旦started为真，零就是实际数字。计数1的转移将“子树已有次数”与“当前为1时每条后缀贡献一次”分开相加。',
'互异数O(D·2^10·10)算术操作；数1 O(D·10)；给定集合O(D·|集合|)，缓存空间为各自状态数。D为十进制位数；此实现假定通常题目整数位数，极长数字需改迭代表。')
