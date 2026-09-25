from course_builder import add

add(62, '递归先定义函数的数学含义，再考虑调用顺序。factorial(n)返回前n个正整数乘积；fib(n)返回第n项。每条递归路径都必须接近基本情形。朴素Fibonacci会重复计算相同参数，用真实调用树统计这种重复，为后续记忆化作动机；不要用很大的n把教学内核卡住。',
'''def factorial(n):
    if n<0: raise ValueError('n must be nonnegative')
    return 1 if n==0 else n*factorial(n-1)

def fib_recursive(n):
    if n<0: raise ValueError('n must be nonnegative')
    return n if n<2 else fib_recursive(n-1)+fib_recursive(n-2)

def trace_calls(n):
    if n<0: raise ValueError('n must be nonnegative')
    calls=[]
    def visit(k,depth):
        calls.append((k,depth))
        if k<2: return k
        return visit(k-1,depth+1)+visit(k-2,depth+1)
    visit(n,0)
    return calls
''',
'''from collections import Counter
calls=trace_calls(5)
show_table(['调用序号','参数','调用深度'],[(i,k,d) for i,(k,d) in enumerate(calls)])
show_table(['子问题参数','重复次数'],sorted(Counter(k for k,_ in calls).items()))''',
'''import math
assert factorial(0)==1 and factorial(5)==120
assert fib_recursive(0)==0 and fib_recursive(1)==1
assert len(trace_calls(4))==9
for n in range(9):
    assert factorial(n)==math.factorial(n)
    assert len(trace_calls(n))==2*fib_recursive(n+1)-1
for fn in [factorial,fib_recursive,trace_calls]:
    try: fn(-1)
    except ValueError: pass
    else: raise AssertionError('negative arguments must be rejected')''',
'在基本情形正确的前提下，假设更小参数的调用正确，由递推定义立即得到当前结果。参数严格下降保证有限非负n终止。','阶乘O(n)次乘法、O(n)栈深；朴素fib O(φⁿ)时间/O(n)栈深；大整数乘法另有位代价。')

add(63, '分治不一定把结果相加。快速幂把指数减半，先求x的n//2次方，再平方；奇数指数再乘一个x。负指数转成倒数。多数元素若在整体中超过一半，则至少在一半子区间中也占多数，否则两半相加不可能过半。必须把“保证存在多数”与“需要验证存在”分开。',
'''def fast_pow(x,n):
    if n<0:
        if x==0: raise ZeroDivisionError('zero cannot have a negative power')
        return 1/fast_pow(x,-n)
    if n==0: return 1
    half=fast_pow(x,n//2)
    return half*half*(x if n%2 else 1)

def majority_divide(nums):
    if not nums: raise ValueError('nonempty input required')
    def candidate(lo,hi):
        if hi-lo==1: return nums[lo]
        mid=(lo+hi)//2; a=candidate(lo,mid); b=candidate(mid,hi)
        if a==b: return a
        ca=sum(nums[i]==a for i in range(lo,hi)); cb=sum(nums[i]==b for i in range(lo,hi))
        return a if ca>=cb else b
    answer=candidate(0,len(nums))
    if sum(x==answer for x in nums)<=len(nums)//2: raise ValueError('strict majority does not exist')
    return answer
''',
'''n=13; rows=[]
while n:
    rows.append((n,n//2,bool(n%2))); n//=2
show_table(['指数','子问题指数','是否多乘一次x'],rows)''',
'''import math
assert fast_pow(2,10)==1024
assert math.isclose(fast_pow(2,-2),.25)
assert fast_pow(9,0)==1
assert majority_divide([2,2,1,1,1,2,2])==2
from itertools import product
from collections import Counter
for n in range(1,8):
    for a in product([0,1,2],repeat=n):
        candidate,count=Counter(a).most_common(1)[0]
        if count>n//2: assert majority_divide(a)==candidate
try: majority_divide([1,2,3])
except ValueError: pass
else: raise AssertionError('must verify majority existence')''',
'快速幂使用n=2q或2q+1的恒等式；多数分治的候选只需来自两半候选，因为整体严格多数不可能在两半都不是多数。最终计数排除无多数输入。','快速幂O(log|n|)乘法及栈空间；多数分治O(n log n)时间/O(log n)栈空间。')

add(64, '回溯把答案构建成选择树。子集每个位置选或不选；排列每层选一个尚未使用的元素；组合只选择递增索引以避免顺序重复。加入答案时必须复制path，否则所有输出都引用同一个后来被清空的列表。先假设输入元素互不相同，下一章才处理值重复。',
'''def subsets(nums):
    result=[]; path=[]
    def visit(i):
        if i==len(nums): result.append(path[:]); return
        visit(i+1)
        path.append(nums[i]); visit(i+1); path.pop()
    visit(0); return result

def permute(nums):
    result=[]; path=[]; used=[False]*len(nums)
    def visit():
        if len(path)==len(nums): result.append(path[:]); return
        for i,x in enumerate(nums):
            if used[i]: continue
            used[i]=True; path.append(x)
            visit()
            path.pop(); used[i]=False
    visit(); return result

def combine(n,k):
    if n<0 or k<0: raise ValueError('nonnegative n,k required')
    result=[]; path=[]
    def visit(start):
        if len(path)==k: result.append(path[:]); return
        remaining=k-len(path)
        for x in range(start,n-remaining+2):
            path.append(x); visit(x+1); path.pop()
    if k<=n: visit(1)
    return result
''',
'''show_table(['叶节点序号','子集'],list(enumerate(subsets([1,2,3]))))
show_table(['组合序号','从1..4选2'],list(enumerate(combine(4,2))))''',
'''import math
assert len(subsets([1,2,3]))==8
assert len(permute([1,2,3]))==6
for n in range(7):
    for k in range(n+1):
        out=combine(n,k)
        assert len(out)==math.comb(n,k)==len(set(map(tuple,out)))
        assert all(len(x)==k and x==sorted(x) for x in out)
out=subsets([1,2]); assert len({id(x) for x in out})==len(out)
assert permute([])==[[]] and combine(2,3)==[]''',
'每个答案对应唯一根到叶的选择序列。撤销步骤恢复父状态，使兄弟分支互不污染；组合严格递增索引给每个无序集合唯一编码。','子集O(n2ⁿ)、排列O(n·n!)、组合O(k·C(n,k))输出规模；工作栈与path为O(n)，不计输出。')

add(65, '值重复时，“索引不同”不再意味着答案不同。排序后在同一层跳过相同值，防止不同兄弟分支生成同一答案；排列还要保证相同值按固定索引顺序使用。组合和允许同一候选多次使用，但必须要求候选严格正，否则递归可能不终止。',
'''def subsets_with_dup(nums):
    a=sorted(nums); out=[]; path=[]
    def visit(start):
        out.append(path[:])
        for i in range(start,len(a)):
            if i>start and a[i]==a[i-1]: continue
            path.append(a[i]); visit(i+1); path.pop()
    visit(0); return out

def permute_unique(nums):
    a=sorted(nums); used=[False]*len(a); out=[]; path=[]
    def visit():
        if len(path)==len(a): out.append(path[:]); return
        for i,x in enumerate(a):
            if used[i] or (i>0 and x==a[i-1] and not used[i-1]): continue
            used[i]=True; path.append(x); visit(); path.pop(); used[i]=False
    visit(); return out

def combination_sum(candidates,target):
    a=sorted(set(candidates))
    if any(x<=0 for x in a) or target<0: raise ValueError('positive candidates and nonnegative target required')
    out=[]; path=[]
    def visit(start,remaining):
        if remaining==0: out.append(path[:]); return
        for i in range(start,len(a)):
            if a[i]>remaining: break
            path.append(a[i]); visit(i,remaining-a[i]); path.pop()
    visit(0,target); return out
''',
'''a=[1,2,2]
show_table(['对象','去重答案'],[('子集',subsets_with_dup(a)),('排列',permute_unique(a)),('组合和 target=5',combination_sum([1,2],5))])''',
'''from itertools import combinations,permutations,product
assert len(subsets_with_dup([1,2,2]))==6
assert len(permute_unique([1,1,2]))==3
assert combination_sum([2,3],0)==[[]]
for a in product([1,2],repeat=5):
    out=subsets_with_dup(a); ref={tuple(sorted(t)) for k in range(6) for t in combinations(a,k)}
    assert set(map(tuple,out))==ref and len(out)==len(ref)
    out=permute_unique(a); ref=set(permutations(a))
    assert set(map(tuple,out))==ref and len(out)==len(ref)
assert {tuple(x) for x in combination_sum([2,3,6,7],7)}=={(2,2,3),(7,)}''',
'同层相同值的分支在剩余可选值上等价，保留一个代表不会漏掉不同值答案；不同深度可继续使用同一值。正候选使remaining严格下降，保证终止。','输出敏感的指数算法；排序O(n log n)，工作空间为最大递归深度，组合和深度最多target/min(candidates)。')

add(66, '切分问题的状态是“已经处理到哪个下标”，每次选择下一段的结束位置。回文切分先预计算任意区间是否回文，避免同一段反复判断。恢复IP地址必须同时满足四段、每段0..255、无多余前导零，剩余字符长度还可用作剪枝。',
'''def partition_palindromes(s):
    n=len(s); palindrome=[[False]*n for _ in range(n)]
    for left in range(n-1,-1,-1):
        for right in range(left,n):
            palindrome[left][right]=s[left]==s[right] and (right-left<2 or palindrome[left+1][right-1])
    out=[]; path=[]
    def visit(start):
        if start==n: out.append(path[:]); return
        for end in range(start,n):
            if palindrome[start][end]:
                path.append(s[start:end+1]); visit(end+1); path.pop()
    visit(0); return out

def restore_ip_addresses(s):
    if any(c not in '0123456789' for c in s): raise ValueError('ASCII decimal digits required')
    out=[]; path=[]
    def visit(start):
        needed=4-len(path); remaining=len(s)-start
        if not needed<=remaining<=3*needed: return
        if needed==0:
            out.append('.'.join(path)); return
        for length in range(1,4):
            if start+length>len(s): break
            part=s[start:start+length]
            if len(part)>1 and part[0]=='0': break
            if int(part)>255: break
            path.append(part); visit(start+length); path.pop()
    visit(0); return out
''',
'''show_table(['切分','段长','全为回文'],[(p,list(map(len,p)),all(x==x[::-1] for x in p)) for p in partition_palindromes('aab')])
show_table(['输入','合法IP'],[('25525511135',restore_ip_addresses('25525511135')),('0000',restore_ip_addresses('0000'))])''',
'''assert sorted(partition_palindromes('aab'))==[['a','a','b'],['aa','b']]
assert set(restore_ip_addresses('25525511135'))=={'255.255.11.135','255.255.111.35'}
assert restore_ip_addresses('0000')==['0.0.0.0']
for s in ['','a','abba','aabaa']:
    for parts in partition_palindromes(s): assert ''.join(parts)==s and all(x==x[::-1] for x in parts)
from itertools import combinations
for s in ['101023','1111','00000','1234567']:
    ref=[]
    for cuts in combinations(range(1,len(s)),3):
        bounds=(0,*cuts,len(s)); parts=[s[bounds[i]:bounds[i+1]] for i in range(4)]
        if all(len(x)<=3 and (len(x)==1 or x[0]!='0') and int(x)<=255 for x in parts): ref.append('.'.join(parts))
    assert sorted(restore_ip_addresses(s))==sorted(ref)''',
'任意切分有唯一递增切点序列，枚举所有合法下一段即可完备。IP长度剪枝只删除不可能把剩余字符放入剩余1..3位段的状态。','回文预处理O(n²)，输出最坏指数；IP至多3⁴条深度4路径，输入长度超过12时可立即排除。')

add(67, '网格回溯的visited只属于当前路径，不是全局永久访问。失败分支离开格子时必须恢复，使其他路线还能使用它。单词搜索只检查指定长度；Unique Paths III则要求从起点到终点访问每个可走格恰好一次，提前碰到终点不能继续绕行。',
'''def exist(board,word):
    if not word: return True
    if not board or not board[0]: return False
    rows,cols=len(board),len(board[0])
    def visit(r,c,i):
        if not (0<=r<rows and 0<=c<cols) or board[r][c]!=word[i]: return False
        if i==len(word)-1: return True
        saved=board[r][c]; board[r][c]=None
        try:
            return any(visit(r+dr,c+dc,i+1) for dr,dc in [(1,0),(-1,0),(0,1),(0,-1)])
        finally:
            board[r][c]=saved
    return any(visit(r,c,0) for r in range(rows) for c in range(cols))

def unique_paths_iii(grid):
    if not grid or not grid[0]: return 0
    rows,cols=len(grid),len(grid[0]); start=None; count=0
    for r in range(rows):
        for c in range(cols):
            if grid[r][c]!=-1: count+=1
            if grid[r][c]==1: start=(r,c)
    if start is None: raise ValueError('a start cell is required')
    def visit(r,c,used):
        if not (0<=r<rows and 0<=c<cols) or grid[r][c]==-1: return 0
        if grid[r][c]==2: return int(used==count)
        saved=grid[r][c]; grid[r][c]=-1
        try:
            return sum(visit(r+dr,c+dc,used+1) for dr,dc in [(1,0),(-1,0),(0,1),(0,-1)])
        finally:
            grid[r][c]=saved
    return visit(*start,1)
''',
'''b=[list('ABCE'),list('SFCS'),list('ADEE')]
show_table(['网格行','字符'],list(enumerate(b)))
show_table(['目标词','能否找到','查找后首行'],[(w,exist(b,w),''.join(b[0])) for w in ['ABCCED','SEE','ABCB']])''',
'''from copy import deepcopy
b=[list('ABCE'),list('SFCS'),list('ADEE')]; old=deepcopy(b)
assert exist(b,'ABCCED') and exist(b,'SEE') and not exist(b,'ABCB')
assert b==old
assert not exist([['A']],'AA')
g=[[1,0,0,0],[0,0,0,0],[0,0,2,-1]]; old=deepcopy(g)
assert unique_paths_iii(g)==2 and g==old
from functools import cache
for mask in range(16):
    g=[[1,0,0],[0,0,2]]; inner=[(0,1),(0,2),(1,0),(1,1)]
    for i,(r,c) in enumerate(inner):
        if mask>>i&1: g[r][c]=-1
    vertices=[(r,c) for r in range(2) for c in range(3) if g[r][c]!=-1]
    index={v:i for i,v in enumerate(vertices)}; end=index[(1,2)]
    @cache
    def ref(v,seen):
        if v==end: return int(seen==(1<<len(vertices))-1)
        r,c=vertices[v]; total=0
        for dr,dc in [(1,0),(-1,0),(0,1),(0,-1)]:
            nxt=(r+dr,c+dc)
            if nxt in index and not (seen>>index[nxt]&1): total+=ref(index[nxt],seen|(1<<index[nxt]))
        return total
    old=deepcopy(g); assert unique_paths_iii(g)==ref(index[(0,0)],1<<index[(0,0)]) and g==old''',
'每层路径标记排除已使用格子，回溯恢复让搜索树覆盖所有简单路径。终点仅在已用格数等于可走格数时计1，不把提前到达算解。','单词搜索粗界O(RC·4ᴸ)、O(L)栈；全格路径搜索最坏指数、O(RC)深度。try/finally用于恢复资源，不吞掉异常。')

add(68, '约束满足问题的关键是尽早拒绝部分不合法解。N皇后每行只放一个，列与两条对角线集合足以检查冲突。数独采用最少候选格优先，减少分支；这是搜索顺序优化，不改变可解性。求解器必须区分“找到真实解”和“无解”，不能返回填满却违反约束的表格。',
'''def solve_n_queens(n):
    if n<0: raise ValueError('n must be nonnegative')
    out=[]; columns=set(); diagonal1=set(); diagonal2=set(); chosen=[]
    def visit(row):
        if row==n:
            out.append(['.'*c+'Q'+'.'*(n-c-1) for c in chosen]); return
        for col in range(n):
            if col in columns or row-col in diagonal1 or row+col in diagonal2: continue
            columns.add(col); diagonal1.add(row-col); diagonal2.add(row+col); chosen.append(col)
            visit(row+1)
            chosen.pop(); columns.remove(col); diagonal1.remove(row-col); diagonal2.remove(row+col)
    visit(0); return out

def solve_sudoku(board):
    if len(board)!=9 or any(len(row)!=9 for row in board): raise ValueError('9 by 9 board required')
    rows=[set() for _ in range(9)]; cols=[set() for _ in range(9)]; boxes=[set() for _ in range(9)]; empty=[]
    digits=set('123456789')
    for r in range(9):
        for c in range(9):
            value=board[r][c]; box=(r//3)*3+c//3
            if value=='.': empty.append((r,c)); continue
            if value not in digits: raise ValueError('invalid cell')
            if value in rows[r] or value in cols[c] or value in boxes[box]: return False
            rows[r].add(value); cols[c].add(value); boxes[box].add(value)
    def candidates(r,c): return digits-rows[r]-cols[c]-boxes[(r//3)*3+c//3]
    def visit(position):
        if position==len(empty): return True
        best=min(range(position,len(empty)),key=lambda i:len(candidates(*empty[i])))
        empty[position],empty[best]=empty[best],empty[position]
        r,c=empty[position]; box=(r//3)*3+c//3
        for value in sorted(candidates(r,c)):
            board[r][c]=value; rows[r].add(value); cols[c].add(value); boxes[box].add(value)
            if visit(position+1): return True
            rows[r].remove(value); cols[c].remove(value); boxes[box].remove(value); board[r][c]='.'
        empty[position],empty[best]=empty[best],empty[position]
        return False
    return visit(0)
''',
'''solutions=solve_n_queens(4)
show_table(['解编号','棋盘行','布局'],[(i,r,line) for i,b in enumerate(solutions,1) for r,line in enumerate(b)])''',
'''from copy import deepcopy
assert len(solve_n_queens(4))==2 and len(solve_n_queens(1))==1
for n in range(1,7):
    for board in solve_n_queens(n):
        pos=[row.index('Q') for row in board]
        assert len(set(pos))==n and len({r-c for r,c in enumerate(pos)})==n and len({r+c for r,c in enumerate(pos)})==n
puzzle=['53..7....','6..195...','.98....6.','8...6...3','4..8.3..1','7...2...6','.6....28.','...419..5','....8..79']
b=[list(row) for row in puzzle]; assert solve_sudoku(b)
want=set('123456789')
assert all(set(row)==want for row in b)
assert all({b[r][c] for r in range(9)}==want for c in range(9))
assert all({b[r][c] for r in range(br,br+3) for c in range(bc,bc+3)}==want for br in [0,3,6] for bc in [0,3,6])
assert all(puzzle[r][c]=='.' or puzzle[r][c]==b[r][c] for r in range(9) for c in range(9))
unsolved=[list('.12345678')]+[['.']*9 for _ in range(8)]; unsolved[3][0]='9'; old=deepcopy(unsolved)
assert solve_sudoku(unsolved) is False and unsolved==old''',
'维护集合恰好反映已放置数字或皇后的约束；候选只删去当前已违反约束的分支，因此不漏解。失败时撤销全部本层修改，无解返回后原题保持不变。','N皇后最坏O(n!)级搜索；有E个空格的数独粗界O(9ᴱ)，MRV降低实际搜索但不改变指数最坏性质。')
