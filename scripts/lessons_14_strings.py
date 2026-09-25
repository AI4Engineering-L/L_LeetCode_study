from course_builder import add

add(118,'朴素匹配失败后把文本指针退回，重复比较已经相等的前缀。KMP用前缀函数记录“当前匹配前缀的最长真前后缀”，失败时只回退模式长度。Z函数问的是每个位置与整个串前缀能匹配多长；二者都通过复用已知相等区间避免重做比较。',
'''def prefix_function(s):
    pi=[0]*len(s)
    for i in range(1,len(s)):
        j=pi[i-1]
        while j and s[i]!=s[j]: j=pi[j-1]
        if s[i]==s[j]: j+=1
        pi[i]=j
    return pi

def kmp_find_all(text,pattern):
    if not pattern: return list(range(len(text)+1))
    pi=prefix_function(pattern); j=0; out=[]
    for i,c in enumerate(text):
        while j and c!=pattern[j]: j=pi[j-1]
        if c==pattern[j]: j+=1
        if j==len(pattern): out.append(i-j+1); j=pi[j-1]
    return out

def kmp_find(text,pattern):
    if not pattern: return 0
    pi=prefix_function(pattern); j=0
    for i,c in enumerate(text):
        while j and c!=pattern[j]: j=pi[j-1]
        if c==pattern[j]: j+=1
        if j==len(pattern): return i-j+1
    return -1

def z_function(s):
    z=[0]*len(s); left=right=0
    for i in range(1,len(s)):
        if i<right: z[i]=min(right-i,z[i-left])
        while i+z[i]<len(s) and s[z[i]]==s[i+z[i]]: z[i]+=1
        if i+z[i]>right: left,right=i,i+z[i]
    return z

def sum_scores(s): return len(s)+sum(z_function(s))
''',
'''s='ababab'; pi=prefix_function(s); z=z_function(s)
show_table(['下标','字符','最长真前后缀','Z值'],[(i,c,pi[i],z[i]) for i,c in enumerate(s)])
print('重叠匹配位置',kmp_find_all(s,'abab'))''',
'''assert kmp_find_all('ababab','abab')==[0,2]
assert kmp_find('abc','d')==-1 and kmp_find('abc','')==0
assert sum_scores('babab')==9
from itertools import product
words=[''.join(p) for n in range(6) for p in product('ab',repeat=n)]
for s in words:
    pi=prefix_function(s); z=z_function(s)
    for i in range(len(s)):
        assert pi[i]==max((k for k in range(1,i+1) if s[:k]==s[i-k+1:i+1]),default=0)
        if i: assert z[i]==max(k for k in range(len(s)-i+1) if s[:k]==s[i:i+k])
    for p in words[:15]:
        assert kmp_find(s,p)==s.find(p)
        assert kmp_find_all(s,p)==[i for i in range(len(s)+1) if s.startswith(p,i)]''',
'KMP状态j表示模式前缀等于已读文本的最长后缀，失配时只有它的真前后缀仍可能匹配。j每次成功至多增加1，失败只下降，摊还比较次数线性。Z盒内复用结果不能越过右边界，越界后才逐字符扩展；右边界总共前进O(n)次。',
'前缀函数/Z各O(n)时间空间；KMP O(|text|+|pattern|)时间、O(|pattern|)辅助（全部匹配另加输出空间）。约定Z[0]=0，总评分另加串长；空模式匹配所有n+1个边界。')

add(119,'多项式前缀哈希把子串比较先压为整数比较：H(l,r)=P[r]−P[l]·B^(r−l)。但哈希相等不是字符串相等，必须说明碰撞风险。本章采用“哈希分桶＋原串精确比较”，因此即使故意制造碰撞也不误判，只会变慢。重复子串长度具有单调可行性，可二分答案。',
'''class RollingHash:
    def __init__(self,s,base=911382323,mod=1000000007):
        if mod<=0: raise ValueError('positive modulus required')
        self.s=s; self.base=base; self.mod=mod; self.prefix=[0]; self.power=[1]
        for c in s:
            self.prefix.append((self.prefix[-1]*base+ord(c)+1)%mod)
            self.power.append(self.power[-1]*base%mod)
    def query(self,left,right):
        if not 0<=left<=right<=len(self.s): raise ValueError('invalid half-open range')
        return (self.prefix[right]-self.prefix[left]*self.power[right-left])%self.mod

def find_duplicate_length(s,length,*,base=911382323,mod=1000000007):
    if length<0: raise ValueError('nonnegative length required')
    if length==0: return ''
    if length>len(s): return None
    rh=RollingHash(s,base,mod); buckets={}
    for i in range(len(s)-length+1):
        key=rh.query(i,i+length)
        for j in buckets.get(key,[]):
            if s[i:i+length]==s[j:j+length]: return s[i:i+length]
        buckets.setdefault(key,[]).append(i)
    return None

def longest_duplicate_substring(s):
    low,high=0,len(s); best=''
    while low<=high:
        mid=(low+high)//2; found=find_duplicate_length(s,mid)
        if found is None: high=mid-1
        else: best=found; low=mid+1
    return best
''',
'''s='banana'; rh=RollingHash(s)
show_table(['起点','三字符子串','哈希'],[(i,s[i:i+3],rh.query(i,i+3)) for i in range(len(s)-2)])
print('最长重复',longest_duplicate_substring(s))''',
'''assert longest_duplicate_substring('banana')=='ana'
assert longest_duplicate_substring('aaaa')=='aaa'
# 模1让所有哈希值碰撞，但精确版仍不误判。
assert find_duplicate_length('abcd',2,base=1,mod=1) is None
assert find_duplicate_length('abca',1,base=1,mod=1)=='a'
from itertools import product
for n in range(7):
    for chars in product('ab',repeat=n):
        s=''.join(chars); best=0
        for length in range(n+1):
            parts=[s[i:i+length] for i in range(n-length+1)]
            exists=length==0 or len(set(parts))<len(parts)
            found=find_duplicate_length(s,length,base=1,mod=2)
            assert (found is not None)==exists
            if exists: best=length
        answer=longest_duplicate_substring(s)
        assert len(answer)==best
        if answer: assert sum(s.startswith(answer,i) for i in range(n))>=2''',
'前缀相减抵消区间外字符，乘幂对齐指数。哈希仅是必要条件，原串比较提供充分条件，所以碰撞不会影响正确性。长度L存在重复，则取其前L−1字符也重复，因此二分判定满足单调性；重复允许重叠。',
'预处理O(n)，单次哈希查询O(1)固定字长模运算。碰撞桶内精确比较会增加字符代价；常见无恶意碰撞时二分接近O(n log n)，但不保证该最坏界。保守最坏O(n³ log n)，辅助O(n)。固定双哈希也不能替代一般性精确保证。')

add(120,'回文可用三种状态理解：区间DP依赖去掉两端后的内部区间；中心扩展逐个中心比较对称字符；Manacher复用当前最右回文内部的镜像半径，只在越过已知右边界时继续比较。奇偶中心分开表示，比插入特殊字符更容易明确边界。',
'''def longest_palindrome_center(s):
    best=(0,0)
    for center in range(len(s)):
        for l,r in [(center,center),(center,center+1)]:
            while l>=0 and r<len(s) and s[l]==s[r]: l-=1; r+=1
            if r-l-1>best[1]-best[0]: best=(l+1,r)
    return s[best[0]:best[1]]

def palindrome_dp(s):
    n=len(s); dp=[[False]*n for _ in range(n)]
    for l in range(n-1,-1,-1):
        for r in range(l,n): dp[l][r]=s[l]==s[r] and (r-l<2 or dp[l+1][r-1])
    return dp

def manacher_radii(s):
    n=len(s); odd=[0]*n; left=0; right=-1
    for i in range(n):
        radius=1 if i>right else min(odd[left+right-i],right-i+1)
        while i-radius>=0 and i+radius<n and s[i-radius]==s[i+radius]: radius+=1
        odd[i]=radius
        if i+radius-1>right: left,right=i-radius+1,i+radius-1
    even=[0]*n; left=0; right=-1
    for i in range(n):
        radius=0 if i>right else min(even[left+right-i+1],right-i+1)
        while i-radius-1>=0 and i+radius<n and s[i-radius-1]==s[i+radius]: radius+=1
        even[i]=radius
        if i+radius-1>right: left,right=i-radius,i+radius-1
    return odd,even

def count_palindromic_substrings(s):
    odd,even=manacher_radii(s); return sum(odd)+sum(even)
''',
'''s='abacabba'; odd,even=manacher_radii(s)
show_table(['中心下标','奇半径(含中心)','偶半径(中心在i前)','最长奇回文','最长偶回文'],[(i,odd[i],even[i],s[i-odd[i]+1:i+odd[i]],s[i-even[i]:i+even[i]]) for i in range(len(s))])''',
'''assert longest_palindrome_center('babad') in ('bab','aba')
assert longest_palindrome_center('cbbd')=='bb' and count_palindromic_substrings('aaa')==6
assert longest_palindrome_center('')=='' and manacher_radii('')==([],[])
from itertools import product
for n in range(8):
    for chars in product('ab',repeat=n):
        s=''.join(chars); all_pal=[s[l:r] for l in range(n) for r in range(l+1,n+1) if s[l:r]==s[l:r][::-1]]
        odd,even=manacher_radii(s); table=palindrome_dp(s)
        assert count_palindromic_substrings(s)==len(all_pal)==sum(sum(row) for row in table)
        longest=max([0]+[len(p) for p in all_pal])
        assert len(longest_palindrome_center(s))==longest==max([0]+[2*x-1 for x in odd]+[2*x for x in even])
        for l in range(n):
            for r in range(l,n): assert table[l][r]==(s[l:r+1]==s[l:r+1][::-1])''',
'镜像回文在当前大回文右界以内的部分由对称性保证，超过右界的字符尚未知，必须显式比较。每次真正扩展使全局最右边界前进，累计O(n)。每个奇中心半径r贡献r个非空回文，每个偶中心同理，所以求和得到按位置计数而非去重字符串数。',
'中心扩展O(n²)时间O(1)辅助；区间DP O(n²)时间空间；Manacher O(n)时间空间。odd[i]包含中心字符，even[i]以i−1与i之间为中心。')

AC='''from collections import deque

class AhoCorasick:
    def __init__(self,patterns=None):
        self.build([] if patterns is None else patterns)
    def build(self,patterns):
        self.patterns=list(patterns); self.next=[{}]; self.fail=[0]; self.output=[[]]
        for pid,pattern in enumerate(self.patterns):
            if not pattern: raise ValueError('empty patterns are excluded')
            node=0
            for c in pattern:
                if c not in self.next[node]:
                    self.next[node][c]=len(self.next); self.next.append({}); self.fail.append(0); self.output.append([])
                node=self.next[node][c]
            self.output[node].append(pid)
        queue=deque(self.next[0].values())
        while queue:
            u=queue.popleft()
            for c,v in self.next[u].items():
                f=self.fail[u]
                while f and c not in self.next[f]: f=self.fail[f]
                self.fail[v]=self.next[f].get(c,0)
                self.output[v].extend(self.output[self.fail[v]]); queue.append(v)
        return self
    def step(self,state,letter):
        while state and letter not in self.next[state]: state=self.fail[state]
        return self.next[state].get(letter,0)
    def scan(self,text):
        state=0; matches=[]
        for i,c in enumerate(text):
            state=self.step(state,c)
            matches.extend((i,pid) for pid in self.output[state])
        return matches

class StreamChecker:
    def __init__(self,words): self.automaton=AhoCorasick(words); self.state=0
    def query(self,letter):
        if len(letter)!=1: raise ValueError('one character per query')
        self.state=self.automaton.step(self.state,letter)
        return bool(self.automaton.output[self.state])
'''
add(121,'多模式搜索不能为每个词重新扫描整个文本。Trie把公共前缀合并；失败指针把当前文本后缀转移到仍可能匹配的最长模式前缀。一个状态可能同时结束多个模式，例如she也以he结尾，所以输出必须包含失败链上的终止模式。',AC,
'''patterns=['he','she','hers','his']; automaton=AhoCorasick(patterns)
show_table(['状态','Trie出边','失败指针','模式ID'],[(i,automaton.next[i],automaton.fail[i],automaton.output[i]) for i in range(len(automaton.next))])
print('ushers的(结束下标,模式ID)',automaton.scan('ushers'))''',
'''patterns=['he','she','hers','his']; ac=AhoCorasick(patterns)
assert sorted(ac.scan('ushers'))==[(3,0),(3,1),(5,2)]
ac=AhoCorasick(['a','a','ba'])
assert sorted(ac.scan('ba'))==[(1,0),(1,1),(1,2)]
from itertools import product
patterns=['a','ab','bab','b','aba']; ac=AhoCorasick(patterns)
for n in range(8):
    for chars in product('ab',repeat=n):
        text=''.join(chars)
        expected=[(i,pid) for i in range(n) for pid,p in enumerate(patterns) if text[:i+1].endswith(p)]
        assert sorted(ac.scan(text))==sorted(expected)
        stream=StreamChecker(patterns)
        assert [stream.query(c) for c in text]==[any(text[:i+1].endswith(p) for p in patterns) for i in range(n)]''',
'状态表示已经读取文本的最长后缀，且该后缀是某模式前缀。失败链依次枚举更短候选，找到转移即恢复不变量。沿失败链继承输出保留后缀匹配和重叠匹配；重复模式保留不同ID，不能无意去重。',
'扫描O(T+匹配输出数)平均字典操作；单次query最坏可沿长失败链，总流式回退可摊还。这个稀疏实现构建保守O(M·L+输出列表复制量)，M为Trie节点数、L最长模式；复制后缀输出可能增大空间，拓展可用输出链接避免复制。')

SUFFIX='''def suffix_array(s):
    n=len(s); sa=list(range(n)); ranks=[ord(c) for c in s]; width=1
    while width<n:
        sa.sort(key=lambda i:(ranks[i],ranks[i+width] if i+width<n else -1))
        new=[0]*n
        for j in range(1,n):
            a,b=sa[j-1],sa[j]
            left=(ranks[a],ranks[a+width] if a+width<n else -1)
            right=(ranks[b],ranks[b+width] if b+width<n else -1)
            new[b]=new[a]+(left!=right)
        ranks=new
        if not n or ranks[sa[-1]]==n-1: break
        width*=2
    return sa

def kasai_lcp(s,sa):
    n=len(s)
    if len(sa)!=n or set(sa)!=set(range(n)): raise ValueError('sa must be a permutation')
    rank=[0]*n
    for r,i in enumerate(sa): rank[i]=r
    lcp=[0]*max(0,n-1); height=0
    for i in range(n):
        r=rank[i]
        if r==n-1: height=0; continue
        j=sa[r+1]
        while i+height<n and j+height<n and s[i+height]==s[j+height]: height+=1
        lcp[r]=height; height=max(0,height-1)
    return lcp

def count_distinct_substrings_sa(s):
    sa=suffix_array(s); return len(s)*(len(s)+1)//2-sum(kasai_lcp(s,sa))
'''
add(122,'把所有后缀按字典序排序后，每个不同子串都可以看成某个后缀的前缀。相邻后缀的最长公共前缀LCP告诉我们新后缀有多少前缀已经出现。倍增法每轮比较两个长度2^k块的排名，而不是反复比较整段字符串。',SUFFIX,
'''s='banana'; sa=suffix_array(s); lcp=kasai_lcp(s,sa)
show_table(['排名','后缀起点','后缀','与下一后缀LCP'],[(r,i,s[i:],lcp[r] if r<len(lcp) else '-') for r,i in enumerate(sa)])
print('不同非空子串',count_distinct_substrings_sa(s))''',
'''assert suffix_array('banana')==[5,3,1,0,4,2]
assert suffix_array('')==[] and kasai_lcp('',[])==[]
from itertools import product
for n in range(8):
    for chars in product('ab',repeat=n):
        s=''.join(chars); sa=suffix_array(s); lc=kasai_lcp(s,sa)
        assert sa==sorted(range(n),key=lambda i:s[i:])
        assert count_distinct_substrings_sa(s)==len({s[i:j] for i in range(n) for j in range(i+1,n+1)})
        for r,h in enumerate(lc):
            a,b=s[sa[r]:],s[sa[r+1]:]
            assert h==max(k for k in range(min(len(a),len(b))+1) if a[:k]==b[:k])''',
'两个长度2w片段的顺序由其前后两块长度w的排名决定，归纳得到完整后缀顺序。加入字典序下一后缀时，和所有旧后缀共享的最长前缀由相邻前驱给出；扣除相邻LCP总和即可去重。Kasai把前一匹配长度减1作为下一次下界，累计字符扩展线性。',
'Python比较排序倍增O(n log² n)时间O(n)辅助，不误称O(n log n)。给定合法SA的Kasai O(n)时间空间；本实现额外线性验证排列，但不重新验证SA排序。非空不同子串数量为n(n+1)/2−∑LCP。')

SAM='''class SuffixAutomaton:
    def __init__(self): self.next=[{}]; self.link=[-1]; self.length=[0]; self.last=0
    def extend(self,symbol):
        cur=len(self.next); self.next.append({}); self.length.append(self.length[self.last]+1); self.link.append(0); p=self.last
        while p!=-1 and symbol not in self.next[p]: self.next[p][symbol]=cur; p=self.link[p]
        if p==-1: self.link[cur]=0
        else:
            q=self.next[p][symbol]
            if self.length[p]+1==self.length[q]: self.link[cur]=q
            else:
                clone=len(self.next); self.next.append(self.next[q].copy()); self.length.append(self.length[p]+1); self.link.append(self.link[q])
                while p!=-1 and self.next[p].get(symbol)==q: self.next[p][symbol]=clone; p=self.link[p]
                self.link[q]=self.link[cur]=clone
        self.last=cur; return cur

def count_distinct_substrings_sam(s):
    sam=SuffixAutomaton()
    for c in s: sam.extend(c)
    return sum(sam.length[v]-sam.length[sam.link[v]] for v in range(1,len(sam.next)))

def longest_common_subarray_sam(a,b):
    sam=SuffixAutomaton()
    for x in a: sam.extend(x)
    state=matched=best=0
    for x in b:
        while state and x not in sam.next[state]: state=sam.link[state]; matched=min(matched,sam.length[state])
        if x in sam.next[state]: state=sam.next[state][x]; matched+=1
        else: state=matched=0
        best=max(best,matched)
    return best
'''
add(123,'后缀自动机把具有相同出现结束位置集合的子串合并为状态。一个状态代表一段连续长度，而不是唯一字符串。追加符号时，若原状态长度范围过宽，需要克隆状态拆分；克隆复制转移，但最大长度缩短。后缀链接指向更短的结束位置等价类。',SAM,
'''s='ababa'; sam=SuffixAutomaton()
for c in s: sam.extend(c)
show_table(['状态','最短长度','最长长度','后缀链接','转移'],[(v,sam.length[sam.link[v]]+1 if v else 0,sam.length[v],sam.link[v],sam.next[v]) for v in range(len(sam.next))])
print('不同子串',count_distinct_substrings_sam(s))''',
'''assert longest_common_subarray_sam([1,2,3,2,1],[3,2,1,4,7])==3
from itertools import product
words=[''.join(p) for n in range(7) for p in product('ab',repeat=n)]
for s in words:
    sam=SuffixAutomaton()
    for c in s: sam.extend(c)
    assert all(sam.length[sam.link[v]]<sam.length[v] for v in range(1,len(sam.next)))
    brute={s[i:j] for i in range(len(s)) for j in range(i+1,len(s)+1)}
    sa=sorted(range(len(s)),key=lambda i:s[i:]); duplicate=0
    for i,j in zip(sa,sa[1:]):
        h=0
        while i+h<len(s) and j+h<len(s) and s[i+h]==s[j+h]: h+=1
        duplicate+=h
    assert count_distinct_substrings_sam(s)==len(brute)==len(s)*(len(s)+1)//2-duplicate
for a in words[:31]:
    for b in words[:31]:
        want=max((k for i in range(len(a)) for j in range(len(b)) for k in range(1,min(len(a)-i,len(b)-j)+1) if a[i:i+k]==b[j:j+k]),default=0)
        assert longest_common_subarray_sam(a,b)==want''',
'状态v代表长度在length[link[v]]+1到length[v]之间且endpos相同的子串，因此贡献两长度之差。克隆把旧类划分为应接受较短后缀与保留较长后缀两部分，维持转移所代表的子串集合。扫描第二序列时，失败沿suffix link缩短当前匹配，保留仍可能延伸的最长后缀。',
'固定字母表下SAM状态与转移数线性，构建与匹配O(n+m)。本Python版本用字典并复制克隆转移，字典操作按平均代价分析；对任意大字母表复制成本需计入。输出非空不同子串数；符号必须可哈希。')
