from course_builder import add

TREE='''class TreeNode:
    def __init__(self,val=0,left=None,right=None):
        self.val,self.left,self.right=val,left,right

def tree_from_level(values):
    """Construct a finite binary tree from level order with None placeholders."""
    from collections import deque
    if not values or values[0] is None: return None
    root=TreeNode(values[0]); queue=deque([root]); i=1
    while queue and i<len(values):
        node=queue.popleft()
        if values[i] is not None: node.left=TreeNode(values[i]); queue.append(node.left)
        i+=1
        if i<len(values):
            if values[i] is not None: node.right=TreeNode(values[i]); queue.append(node.right)
            i+=1
    return root
'''

add(69, '树遍历由“何时处理根节点”区分：前序在孩子之前，中序在两个孩子之间，后序在孩子之后。递归隐含的调用栈可改为显式栈：后序用展开标记，首次遇到节点先安排子树，再安排真正访问。N叉树前序同样在入栈时反转孩子顺序。',
TREE+'''
def preorder(root):
    if not root: return []
    answer=[]; stack=[root]
    while stack:
        node=stack.pop(); answer.append(node.val)
        if node.right: stack.append(node.right)
        if node.left: stack.append(node.left)
    return answer

def inorder(root):
    answer=[]; stack=[]; node=root
    while node or stack:
        while node: stack.append(node); node=node.left
        node=stack.pop(); answer.append(node.val); node=node.right
    return answer

def postorder_iterative(root):
    out=[]; stack=[(root,False)]
    while stack:
        node,expanded=stack.pop()
        if not node: continue
        if expanded: out.append(node.val)
        else:
            stack.append((node,True)); stack.append((node.right,False)); stack.append((node.left,False))
    return out

class NaryNode:
    def __init__(self,val,children=None): self.val=val; self.children=[] if children is None else children

def nary_preorder(root):
    out=[]; stack=[root] if root else []
    while stack:
        node=stack.pop(); out.append(node.val); stack.extend(reversed(node.children))
    return out
''',
'''r=tree_from_level([1,2,3,4,5])
show_table(['遍历','输出顺序'], [('前序',preorder(r)),('中序',inorder(r)),('后序',postorder_iterative(r))])''',
'''r=tree_from_level([1,2,3,4,5])
assert preorder(r)==[1,2,4,5,3]
assert inorder(r)==[4,2,5,1,3]
assert postorder_iterative(r)==[4,5,2,3,1]
assert preorder(None)==inorder(None)==postorder_iterative(None)==[]
def reference(node):
    if not node: return [],[],[]
    a,b,c=reference(node.left); d,e,f=reference(node.right)
    return [node.val]+a+d,b+[node.val]+e,c+f+[node.val]
assert (preorder(r),inorder(r),postorder_iterative(r))==reference(r)
r=TreeNode(0); node=r
for i in range(1,1500): node.right=TreeNode(i); node=node.right
assert preorder(r)==inorder(r)==list(range(1500))
assert postorder_iterative(r)==list(range(1499,-1,-1))
n=NaryNode(1,[NaryNode(2),NaryNode(3,[NaryNode(4)])]); assert nary_preorder(n)==[1,2,3,4]''',
'显式栈中的节点或展开标记表示尚未完成的递归调用。后入先出配合右孩子先入栈，使左子树先访问；展开标记只在两个子树处理之后弹出。','O(n)时间；二叉树工作栈O(h)，输出O(n)。N叉树显式前序栈最坏O(n)。实现不依赖Python递归深度。')

add(70, '层序遍历在处理当前层之前固定队列长度，恰好取出这一层节点；处理中新增的是下一层，不能混入当前层。锯齿遍历只改变每层展示方向，不改变图搜索语义；右视图是每层最右节点，不一定是不断沿right走得到的链。',
TREE+'''
from collections import deque

def level_order(root):
    if not root: return []
    queue=deque([root]); result=[]
    while queue:
        level=[]
        for _ in range(len(queue)):
            node=queue.popleft(); level.append(node.val)
            if node.left: queue.append(node.left)
            if node.right: queue.append(node.right)
        result.append(level)
    return result

def zigzag_level_order(root):
    return [row if depth%2==0 else row[::-1] for depth,row in enumerate(level_order(root))]

def right_side_view(root):
    return [row[-1] for row in level_order(root)]
''',
'''r=tree_from_level([3,9,20,None,None,15,7])
show_table(['深度','层节点','右侧可见'],[(d,row,row[-1]) for d,row in enumerate(level_order(r))])''',
'''r=tree_from_level([3,9,20,None,None,15,7])
assert level_order(r)==[[3],[9,20],[15,7]]
assert right_side_view(r)==[3,20,7]
assert zigzag_level_order(r)==[[3],[20,9],[15,7]]
assert level_order(None)==right_side_view(None)==[]
r=tree_from_level([1,2,None,3]); assert right_side_view(r)==[1,2,3]''',
'开始处理第d层时队列恰好包含该层节点，按左到右次序排列；每个节点的孩子追加到尾部，构成第d+1层的同样不变量。','O(n)时间；level_order队列O(w)、输出O(n)。本章right_side_view复用全部层，额外保存O(n)，可用单独BFS优化到O(w)工作空间。')

POST='''def _postorder_nodes(root):
    stack=[(root,False)]
    while stack:
        node,done=stack.pop()
        if not node: continue
        if done: yield node
        else:
            stack.append((node,True)); stack.append((node.right,False)); stack.append((node.left,False))
'''
add(71, '自底向上聚合把每个子树压缩成父节点需要的少量信息。深度取左右最大值加一；平衡性要求两边深度差不超过一；经过当前节点的最长路径长度是左右高度之和。直径以边计数，单节点为0，不能与高度的节点数混淆。',
TREE+POST+'''
def max_depth(root):
    heights={None:0}
    for node in _postorder_nodes(root): heights[node]=1+max(heights[node.left],heights[node.right])
    return heights[root]

def is_balanced(root):
    heights={None:0}
    for node in _postorder_nodes(root):
        left,right=heights[node.left],heights[node.right]
        if abs(left-right)>1: return False
        heights[node]=1+max(left,right)
    return True

def diameter(root):
    heights={None:0}; best=0
    for node in _postorder_nodes(root):
        left,right=heights[node.left],heights[node.right]
        best=max(best,left+right); heights[node]=1+max(left,right)
    return best
''',
'''r=tree_from_level([1,2,3,4,5]); heights={None:0}; rows=[]
for node in _postorder_nodes(r):
    left,right=heights[node.left],heights[node.right]
    heights[node]=1+max(left,right); rows.append((node.val,left,right,heights[node],left+right))
show_table(['节点','左高','右高','本树高','经过本点的直径候选'],rows)''',
'''assert diameter(TreeNode(1))==0
r=TreeNode(1,TreeNode(2,TreeNode(3))); assert diameter(r)==2 and not is_balanced(r)
assert max_depth(None)==0 and is_balanced(None)
from collections import deque
from random import Random
rng=Random(71)
for n in range(1,30):
    nodes=[TreeNode(i) for i in range(n)]; slots=[(nodes[0],'left'),(nodes[0],'right')]
    adj={x:[] for x in nodes}
    for node in nodes[1:]:
        parent,side=slots.pop(rng.randrange(len(slots))); setattr(parent,side,node)
        slots.extend([(node,'left'),(node,'right')]); adj[parent].append(node); adj[node].append(parent)
    longest=0
    for start in nodes:
        q=deque([(start,0)]); seen={start}
        while q:
            u,d=q.popleft(); longest=max(longest,d)
            for v in adj[u]:
                if v not in seen: seen.add(v); q.append((v,d+1))
    assert diameter(nodes[0])==longest''',
'任意简单树路径有唯一最高节点；其两段分别落在该节点左右子树。每个最高节点的最优两段就是最大向下高度，因此取全局最大完备。','O(n)时间；显式后序与高度字典O(n)辅助空间，避免深树递归溢出。')

add(72, '树路径题首先区分根到叶、任意端点、以及只能向下三种路径。最大路径和向父节点只能返回一条分支，否则会分叉而不再是路径；但全局候选可同时接左右两条正贡献。向下路径计数用当前根路径的前缀频率，离开子树时必须撤销，避免把不同分支拼成假路径。',
TREE+POST+'''
from collections import Counter

def has_path_sum(root,target):
    stack=[(root,0)] if root else []
    while stack:
        node,prefix=stack.pop(); total=prefix+node.val
        if not node.left and not node.right and total==target: return True
        if node.right: stack.append((node.right,total))
        if node.left: stack.append((node.left,total))
    return False

def max_path_sum(root):
    if not root: raise ValueError('nonempty tree required')
    gain={None:0}; best=float('-inf')
    for node in _postorder_nodes(root):
        left=max(0,gain[node.left]); right=max(0,gain[node.right])
        best=max(best,node.val+left+right)
        gain[node]=node.val+max(left,right)
    return best

def path_sum_count(root,target):
    counts=Counter({0:1}); answer=0; stack=[(root,0,False)]
    while stack:
        node,prefix,leaving=stack.pop()
        if not node: continue
        if leaving:
            counts[prefix]-=1
            if counts[prefix]==0: del counts[prefix]
            continue
        total=prefix+node.val; answer+=counts[total-target]; counts[total]+=1
        stack.append((node,total,True)); stack.append((node.right,total,False)); stack.append((node.left,total,False))
    return answer
''',
'''r=tree_from_level([-10,9,20,None,None,15,7]); gain={None:0}; rows=[]
for n in _postorder_nodes(r):
    l=max(0,gain[n.left]); rr=max(0,gain[n.right]); gain[n]=n.val+max(l,rr)
    rows.append((n.val,gain[n],n.val+l+rr))
show_table(['节点','可向上传的单支贡献','在此结束的双支候选'],rows)''',
'''r=tree_from_level([-10,9,20,None,None,15,7]); assert max_path_sum(r)==42
assert max_path_sum(tree_from_level([-3,-2,-5]))==-2
assert not has_path_sum(TreeNode(1,TreeNode(2)),1)
r=tree_from_level([10,5,-3,3,2,None,11,3,-2,None,1]); assert path_sum_count(r,8)==3
def from_start(node,target):
    if not node: return 0
    return int(node.val==target)+from_start(node.left,target-node.val)+from_start(node.right,target-node.val)
for target in range(-5,16):
    assert path_sum_count(r,target)==sum(from_start(n,target) for n in _postorder_nodes(r))
assert path_sum_count(None,0)==0''',
'最大路径按唯一最高节点分类，向上返回值与全局候选承担不同语义；全负树仍至少取一个节点。前缀频率只含当前祖先路径，进入加一、退出减一维持范围。','O(n)平均时间；最大和高度表O(n)空间；前缀计数工作空间O(h)，极端h=n。')

add(73, 'BST不变量是整棵左子树小于根、整棵右子树大于根，不只是父子局部比较。中序应严格递增。本章采用唯一键集合语义，重复插入不创建新节点。删除有两个孩子的节点时，用右子树最小键替换，再删除该后继节点；这会修改原节点值，接口不承诺保留被删除键所在对象。',
TREE+'''
def _inorder_nodes(root):
    stack=[]; node=root
    while stack or node:
        while node: stack.append(node); node=node.left
        node=stack.pop(); yield node; node=node.right

def is_valid_bst(root):
    previous=None; first=True
    for node in _inorder_nodes(root):
        if not first and node.val<=previous: return False
        previous=node.val; first=False
    return True

def kth_smallest(root,k):
    if k<1: raise ValueError('positive rank required')
    for i,node in enumerate(_inorder_nodes(root),1):
        if i==k: return node.val
    raise ValueError('k exceeds number of nodes')

def insert_bst(root,x):
    if root is None: return TreeNode(x)
    node=root
    while True:
        if x==node.val: return root
        side='left' if x<node.val else 'right'
        child=getattr(node,side)
        if child is None: setattr(node,side,TreeNode(x)); return root
        node=child

def delete_bst(root,x):
    parent=None; node=root
    while node and node.val!=x:
        parent=node; node=node.left if x<node.val else node.right
    if not node: return root
    if node.left and node.right:
        successor_parent=node; successor=node.right
        while successor.left: successor_parent=successor; successor=successor.left
        node.val=successor.val; parent,node=successor_parent,successor
    child=node.left if node.left else node.right
    if parent is None: return child
    if parent.left is node: parent.left=child
    else: parent.right=child
    return root
''',
'''r=None; rows=[]
for x in [5,3,6,2,4,7]:
    r=insert_bst(r,x); rows.append((f'插入{x}',[n.val for n in _inorder_nodes(r)]))
r=delete_bst(r,5); rows.append(('删除根5',[n.val for n in _inorder_nodes(r)]))
show_table(['操作','中序'],rows)''',
'''assert not is_valid_bst(tree_from_level([5,1,4,None,None,3,6]))
from random import Random
rng=Random(73); r=None; ref=set()
for _ in range(200):
    x=rng.randrange(30)
    if rng.randrange(2): r=insert_bst(r,x); ref.add(x)
    else: r=delete_bst(r,x); ref.discard(x)
    assert is_valid_bst(r) and [n.val for n in _inorder_nodes(r)]==sorted(ref)
    for k,x in enumerate(sorted(ref),1): assert kth_smallest(r,k)==x''',
'中序严格递增等价于唯一键BST的全局区间约束。右子树最小值大于全部左子树值且不大于剩余右子树值，替换后仍维持BST次序。','查询插删O(h)，最坏O(n)，不能当成平衡树O(log n)；验证O(n)，第k小O(h+k)，遍历栈O(h)。')

add(74, '遍历序列重建需要节点值唯一，否则仅靠前序和中序一般不唯一。迭代重建把尚未匹配中序的祖先放入栈：下一前序值要么是当前左孩子，要么是在若干祖先完成中序后接上的右孩子。序列化必须显式记录空指针，单纯输出值无法恢复形状；这里使用带#的前序文本，不使用eval。',
TREE+'''
def build_tree(preorder,inorder):
    if len(preorder)!=len(inorder) or len(set(preorder))!=len(preorder) or set(preorder)!=set(inorder):
        raise ValueError('matching traversals with distinct keys required')
    if not preorder: return None
    root=TreeNode(preorder[0]); stack=[root]; index=0
    for value in preorder[1:]:
        node=TreeNode(value)
        if stack[-1].val!=inorder[index]: stack[-1].left=node
        else:
            parent=None
            while stack and index<len(inorder) and stack[-1].val==inorder[index]: parent=stack.pop(); index+=1
            parent.right=node
        stack.append(node)
    while stack and index<len(inorder) and stack[-1].val==inorder[index]: stack.pop(); index+=1
    if stack or index!=len(inorder): raise ValueError('inconsistent traversals')
    return root

def serialize(root):
    tokens=[]; stack=[root]
    while stack:
        node=stack.pop()
        if node is None: tokens.append('#')
        else: tokens.append(str(node.val)); stack.append(node.right); stack.append(node.left)
    return ','.join(tokens)

def deserialize(data):
    tokens=data.split(',')
    def node_from(token): return None if token=='#' else TreeNode(int(token))
    root=node_from(tokens[0]); stack=[[root,0]] if root else []
    for token in tokens[1:]:
        if not stack: raise ValueError('extra tokens')
        child=node_from(token); parent,side=stack[-1]
        if side==0: parent.left=child; stack[-1][1]=1
        else: parent.right=child; stack.pop()
        if child is not None: stack.append([child,0])
    if stack: raise ValueError('truncated tree')
    return root
''',
'''r=tree_from_level([1,-2,3,None,4]); text=serialize(r)
show_table(['token索引','前序token'],list(enumerate(text.split(','))))
show_table(['原编码','往返编码'],[(text,serialize(deserialize(text)))])''',
'''r=build_tree([3,9,20,15,7],[9,3,15,20,7])
assert serialize(r)=='3,9,#,#,20,15,#,#,7,#,#'
for values in [[],[0],[-1,2,3,None,4],[1,None,2,None,3]]:
    text=serialize(tree_from_level(values)); assert serialize(deserialize(text))==text
assert deserialize('#') is None
for bad in ['1,#','#,#','1,#,#,2','']:
    try: deserialize(bad)
    except ValueError: pass
    else: raise AssertionError('malformed encoding must fail')
try: build_tree([1,2,3],[3,1,2])
except ValueError: pass
else: raise AssertionError('inconsistent traversals must fail')
a=list(range(1500)); r=build_tree(a,a); assert serialize(deserialize(serialize(r)))==serialize(r)''',
'前序确定新节点出现次序，中序匹配确定何时结束一个祖先的左侧并转向右侧。序列化中每个非空节点消费一个槽、产生两个子槽，#消费一个槽，因此完整槽结构唯一解码。','O(n)时间与O(n)辅助空间；文本长度还依赖整数位数。迭代实现可处理深链，不受递归限制。')

add(75, '最近公共祖先是同时位于两条根路径上且最深的节点。先记录每个节点的父节点，再从p向上建立祖先集合，从q向上首次命中的节点就是答案。这个版本明确处理目标缺失：返回None。BST版本可用键的分布直接定位分叉，但要求两目标确实属于树。',
TREE+'''
def lowest_common_ancestor(root,p,q):
    if root is None: return None
    parent={root:None}; stack=[root]
    while stack and (p not in parent or q not in parent):
        node=stack.pop()
        for child in (node.left,node.right):
            if child is not None: parent[child]=node; stack.append(child)
    if p not in parent or q not in parent: return None
    ancestors=set(); node=p
    while node is not None: ancestors.add(node); node=parent[node]
    node=q
    while node not in ancestors: node=parent[node]
    return node

def lca_bst(root,p,q):
    low,high=sorted((p.val,q.val)); node=root
    while node:
        if node.val<low: node=node.right
        elif node.val>high: node=node.left
        else: return node
    return None
''',
'''r=tree_from_level([6,2,8,0,4,7,9,None,None,3,5])
p=r.left; q=r.left.right
show_table(['p','q','一般树LCA','BST LCA'],[(p.val,q.val,lowest_common_ancestor(r,p,q).val,lca_bst(r,p,q).val)])''',
'''r=tree_from_level([6,2,8,0,4,7,9,None,None,3,5])
assert lowest_common_ancestor(r,r.left,r.right) is r
assert lowest_common_ancestor(r,r.left,r.left.right) is r.left
assert lowest_common_ancestor(r,TreeNode(2),r.left) is None
nodes=[]; parent={r:None}; stack=[r]
while stack:
    n=stack.pop(); nodes.append(n)
    for c in (n.left,n.right):
        if c: parent[c]=n; stack.append(c)
def path(n):
    out=[]
    while n: out.append(n); n=parent[n]
    return out[::-1]
for p in nodes:
    for q in nodes:
        common=[a for a,b in zip(path(p),path(q)) if a is b]
        assert lowest_common_ancestor(r,p,q) is common[-1]
        assert lca_bst(r,p,q) is common[-1]''',
'从q向上首次进入p的祖先集合，不可能有更低的公共祖先；所有公共祖先都在该节点以上。BST两目标位于同侧时祖先必在该侧，否则当前节点是最低分叉。','一般树O(n)时间空间；BST单次O(h)时间/O(1)辅助空间。比较身份而非值，一般树允许相同值节点。')

add(76, '原地树变换的验收应检查指针结构。展开树要求右链是原前序，所有left必须清空。Morris遍历临时把中序前驱的空right指向当前节点，借这条线索返回祖先；第二次遇到线索时立即拆除，遍历结束必须完全恢复原树。不能为了提前拿到第k项直接中断而遗留线程。',
TREE+'''
def flatten(root):
    stack=[root] if root else []; previous=None
    while stack:
        node=stack.pop()
        if node.right: stack.append(node.right)
        if node.left: stack.append(node.left)
        if previous: previous.left=None; previous.right=node
        previous=node
    if previous: previous.left=None; previous.right=None

def invert_tree(root):
    stack=[root] if root else []
    while stack:
        node=stack.pop(); node.left,node.right=node.right,node.left
        if node.left: stack.append(node.left)
        if node.right: stack.append(node.right)
    return root

def morris_inorder(root):
    answer=[]; current=root
    while current:
        if current.left is None: answer.append(current.val); current=current.right
        else:
            predecessor=current.left
            while predecessor.right and predecessor.right is not current: predecessor=predecessor.right
            if predecessor.right is None: predecessor.right=current; current=current.left
            else: predecessor.right=None; answer.append(current.val); current=current.right
    return answer
''',
'''r=tree_from_level([1,2,5,3,4,None,6]); before=morris_inorder(r); flatten(r)
chain=[]; n=r
while n: chain.append(n.val); n=n.right
show_table(['对象','次序'],[('原中序',before),('展开后前序右链',chain)])''',
'''r=tree_from_level([1,2,5,3,4,None,6]); snapshot={}; preorder=[]; stack=[r]
while stack:
    n=stack.pop(); snapshot[n]=(n.left,n.right); preorder.append(n)
    if n.right: stack.append(n.right)
    if n.left: stack.append(n.left)
assert morris_inorder(r)==[3,2,4,1,5,6]
assert all((n.left,n.right)==edges for n,edges in snapshot.items())
invert_tree(invert_tree(r)); assert all((n.left,n.right)==edges for n,edges in snapshot.items())
flatten(r); after=[]; n=r
while n:
    assert n.left is None and n not in after; after.append(n); n=n.right
assert after==preorder''',
'展开时先保存原孩子再修改前一节点，不会失去待访问子树。Morris每个临时线索只建立一次、拆除一次，结束时原本为空的前驱right恢复为空。','均O(n)时间；本章flatten/invert显式栈O(h)，Morris辅助空间O(1)，输出O(n)。')

TRIE='''class TrieNode:
    def __init__(self): self.children={}; self.terminal=False

class Trie:
    def __init__(self): self.root=TrieNode()
    def insert(self,word):
        node=self.root
        for c in word:
            if c not in node.children: node.children[c]=TrieNode()
            node=node.children[c]
        node.terminal=True
    def _walk(self,text):
        node=self.root
        for c in text:
            if c not in node.children: return None
            node=node.children[c]
        return node
    def search(self,word):
        node=self._walk(word); return node is not None and node.terminal
    def startsWith(self,prefix): return self._walk(prefix) is not None
'''
add(77, 'Trie节点表示一个前缀状态，不是单个完整单词。沿字符边走到某节点说明前缀存在，但只有terminal标记才能说明单词在字典中。替换词根时沿单词逐字符走，第一次遇到terminal就得到最短根，不需要枚举全部字典词。',
TRIE+'''
def replace_words(dictionary,sentence):
    trie=Trie()
    for word in dictionary:
        if not word: raise ValueError('replacement roots must be nonempty')
        trie.insert(word)
    def replace(word):
        node=trie.root
        for i,c in enumerate(word):
            if c not in node.children: return word
            node=node.children[c]
            if node.terminal: return word[:i+1]
        return word
    return ' '.join(replace(word) for word in sentence.split())
''',
'''trie=Trie()
for word in ['app','apple','apt']: trie.insert(word)
rows=[]; stack=[('',trie.root)]
while stack:
    prefix,node=stack.pop(); rows.append((prefix or 'ε',node.terminal,sorted(node.children)))
    for c,child in sorted(node.children.items(),reverse=True): stack.append((prefix+c,child))
show_table(['前缀状态','完整单词','出边字符'],rows)''',
'''trie=Trie(); trie.insert('apple')
assert trie.search('apple') and not trie.search('app') and trie.startsWith('app')
trie.insert('app'); trie.insert('app'); assert trie.search('app')
assert trie.startsWith('') and not trie.search('')
trie.insert(''); assert trie.search('')
assert replace_words(['cat','bat','rat'],'the cattle was rattled by the battery')=='the cat was rat by the bat' ''',
'每条根到节点路径唯一编码一个前缀，terminal独立记录是否有词在此结束。第一次遇到terminal对应沿该单词的最短字典前缀。','长度L的插入/查询平均O(L)；总节点数至多所有插入单词长度之和加1。替换总扫描字符数线性。')

add(78, 'Trie与回溯结合时，状态同时包含网格位置、当前路径已访问格和词典前缀。不存在相应前缀就立即剪枝，比对每个单词单独搜索更早共享失败信息。找到词后移除终止标记以去重；没有孩子也没有终止标记的分支可删除，但棋盘必须恢复。通配符`.`匹配恰好一个字符，不是任意长度。',
TRIE+'''
class WordDictionary:
    def __init__(self): self.trie=Trie()
    def addWord(self,word): self.trie.insert(word)
    def search(self,word):
        def visit(node,i):
            if i==len(word): return node.terminal
            if word[i]=='.': return any(visit(child,i+1) for child in node.children.values())
            child=node.children.get(word[i]); return child is not None and visit(child,i+1)
        return visit(self.trie.root,0)

def find_words(board,words):
    if not board or not board[0]: return []
    root={}
    for word in words:
        if not word: raise ValueError('nonempty dictionary words required')
        node=root
        for c in word: node=node.setdefault(c,{})
        node[None]=word
    rows,cols=len(board),len(board[0]); result=[]
    def visit(r,c,parent):
        char=board[r][c]
        if char is None or char not in parent: return
        node=parent[char]; found=node.pop(None,None)
        if found is not None: result.append(found)
        board[r][c]=None
        try:
            for dr,dc in [(1,0),(-1,0),(0,1),(0,-1)]:
                nr,nc=r+dr,c+dc
                if 0<=nr<rows and 0<=nc<cols: visit(nr,nc,node)
        finally: board[r][c]=char
        if not node: del parent[char]
    for r in range(rows):
        for c in range(cols): visit(r,c,root)
    return result
''',
'''board=[list('oaan'),list('etae'),list('ihkr'),list('iflv')]
show_table(['行','字符'],list(enumerate(board)))
show_table(['词典','找到的词'],[(['oath','pea','eat','rain'],sorted(find_words(board,['oath','pea','eat','rain'])))])''',
'''from copy import deepcopy
wd=WordDictionary()
for w in ['bad','dad','mad']: wd.addWord(w)
assert wd.search('.a.') and wd.search('b..') and not wd.search('..')
b=[list('oaan'),list('etae'),list('ihkr'),list('iflv')]; before=deepcopy(b)
assert set(find_words(b,['oath','pea','eat','rain','eat']))=={'oath','eat'} and b==before
def slow_exist(board,word):
    def dfs(r,c,i,used):
        if board[r][c]!=word[i]: return False
        if i+1==len(word): return True
        for nr,nc in [(r+1,c),(r-1,c),(r,c+1),(r,c-1)]:
            if 0<=nr<len(board) and 0<=nc<len(board[0]) and (nr,nc) not in used:
                if dfs(nr,nc,i+1,used|{(nr,nc)}): return True
        return False
    return any(dfs(r,c,0,{(r,c)}) for r in range(len(board)) for c in range(len(board[0])))
from itertools import product
words=[''.join(x) for n in range(1,4) for x in product('ab',repeat=n)]
for values in product('ab',repeat=4):
    b=[list(values[:2]),list(values[2:])]; before=deepcopy(b)
    assert set(find_words(b,words))=={w for w in words if slow_exist(b,w)} and b==before''',
'前缀不存在时任何继续延伸都不可能变成字典词，剪枝安全。找到终止词不等于终止整个分支，因为该词可能仍是其他词的前缀。','词典构建O(总词长)；网格搜索最坏仍指数，粗界O(RC·4ᴸ)，Trie共享与剪枝改善实际工作；额外Trie空间O(总词长)、路径栈O(L)。')
