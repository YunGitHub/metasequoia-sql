"""
子句（clause）：SQL 语法树的中间节点；通常是由一个关键字引导，用于定义语句中某一部分的功能或逻辑；子句节点的属性通常为表达式节点或元素节点，子句之间允许相互引用，但需要保证子句之间的引用关系满足严格的拓扑关系。
"""

from metasequoia_sql.ast.clause.ddl_partition_by_clause import *
from metasequoia_sql.ast.clause.group_by_clause import *
from metasequoia_sql.ast.clause.index_hint_clause import *
from metasequoia_sql.ast.clause.into_clause import *
from metasequoia_sql.ast.clause.limit_clause import *
from metasequoia_sql.ast.clause.locking_clause import *
from metasequoia_sql.ast.clause.order_by_clause import *
from metasequoia_sql.ast.clause.over_clause import *
from metasequoia_sql.ast.clause.require_clause import *
from metasequoia_sql.ast.clause.with_clause import *
