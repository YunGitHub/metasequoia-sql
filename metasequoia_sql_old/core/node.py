# pylint: disable=C0302

"""
抽象语法树（AST）节点

节点命名规范：
1. 非语句层级的抽象类统一使用 Base 后缀，语句层级的抽象类可以不使用 Base 后缀
2. 抽象语法树节点包含语句（Statement）、子句（Clause）、表达式（Expression）、元素共 4 个层级：
  - 语句层级：是可以执行运行的 SQL 语句，节点统一使用 Statement 后缀
  - 子句层级：是包括 FROM、WHERE 等在内的子句，是语句的组成部分，节点统一使用 Clause 后缀
  - 表达式层级：是子句的组成部分，相对于元素来说，表达式更加通用一些，会在不同场景中使用，节点统一使用 Expression 后缀
  - 元素层级：是表达式或在子句的组成部分，相对于表达式来说，元素层级往往仅在少数特定场景下使用，仅用于封装多个元素或用于封装枚举类，节点没有后缀

在设计上，要求每个节点都是不可变节点，从而保证节点是可哈希的。同时，我们提供专门的修改方法：
- 当前，我们使用复制并返回新元素的方法，且不提供 inplace 参数
- 未来，我们为每个元素提供 .changeable() 方法，返回该元素的可变节点形式

其中：
- 诸如函数调用、CASE、窗口等最终返回一个普通值或布尔值，且在当前层级下可以视作一个任意值节点的元素，均称为元素表达式
- 诸如比较运算符、BETWEEN、LIKE 等最终返回一个布尔值，且在当前层级下可以视作一个布尔值节点的元素，均称为布尔表达式
- 第 5 层级到第 8 层级的表达式，可以统称为布尔表达式
"""

import abc
import dataclasses
from typing import Any, Dict, Optional, Tuple, Union

from metasequoia_sql_old.common.basic import is_bool_literal, is_float_literal, is_int_literal, is_null_literal
from metasequoia_sql_old.core import static
from metasequoia_sql_old.core.sql_type import SQLType
from metasequoia_sql_old.errors import NotSupportError, SqlParseError

__all__ = [
    # ------------------------------ 抽象语法树（AST）节点的抽象类 ------------------------------
    "ASTBase",  # 所有语法树节点的抽象基类
    "ASTStatementBase",  # 语句的抽象基类
    "ASTStatementHasWithClauseBase",  # 包含 WITH 子句的语句的抽象基类
    "ASTExpressionBase",  # 一般表达式的抽象基类

    # ------------------------------ 抽象语法树（AST）节点的枚举类元素节点 ------------------------------
    "ASTEnumListBase",  # 抽象语法树枚举类型的基类（枚举值为字符串列表）
    "ASTEnumElementBase",  # 抽象语法树枚举类型的基类（枚举值为字符串）
    "ASTInsertType",  # 插入类型
    "ASTJoinType",  # 关联类型
    "ASTOrderType",  # 排序类型
    "ASTUnionType",  # 组合类型
    "ASTCastDataType",  # CAST 函数中的字段类型枚举类
    "ASTCompareOperator",  # 比较运算符
    "ASTComputeOperator",  # 计算运算符
    "ASTLogicalOperator",  # 逻辑运算符

    # ------------------------------ 抽象语法树（AST）节点的基础表达式节点 ------------------------------
    "ASTTableNameExpression",  # 表名节点
    "ASTFunctionNameExpression",  # 函数名节点
    "ASTAlisaExpression",  # 别名节点
    "ASTMultiAlisaExpression",  # 多个别名节点（用于在 LATERAL VIEW 子句中配合返回多个字段使用）

    # ------------------------------ 抽象语法树（AST）节点的一般表达式节点 ------------------------------
    # 运算表达式中的单元素表达式
    "ASTBinaryExpressionBase",  # 二元表达式的抽象基类
    "ASTColumnNameExpression",  # 【元素表达式层级】列名表达式节点
    "ASTLiteralExpression",  # 【元素表达式层级】字面值表达式节点
    "ASTWildcardExpression",  # 【元素表达式层级】通配符表达式节点
    "ASTFunctionExpressionBase",  # 【元素表达式层级】函数表达式：函数表达式的抽象类
    "ASTNormalFunctionExpression",  # 【元素表达式层级】函数表达式：普通函数表达式
    "ASTAggregationFunction",  # 【元素表达式层级】函数表达式：聚集函数表达式
    "ASTCastFunctionExpression",  # 【元素表达式层级】函数表达式：CAST 函数表达式
    "ASTExtractFunctionExpression",  # 【元素表达式层级】函数表达式：EXTRACT 函数表达式
    "ASTWindowRowItem",  # 窗口函数中的行限制
    "ASTWindowRow",  # 窗口函数的行数限制表达式
    "ASTWindowExpression",  # 【元素表达式层级】窗口表达式
    "ASTCaseConditionExpression",  # 【元素表达式层级】CASE 表达式：CASE 之后没有变量，WHEN 中为条件语句的 CASE 表达式
    "ASTCaseConditionItem",  # CASE 表达式元素：WHEN ... CASE ... 表达式
    "ASTCaseValueExpression",  # 【元素表达式层级】CASE 表达式：CASE 之后有变量，WHEN 中为该变量的枚举值的 CASE 表达式
    "ASTCaseValueItem",  # CASE 表达式元素：WHEN ... CASE ... 表达式
    "ASTSubQueryExpression",  # 【元素表达式层级】插入语表达式：子查询表达式
    "ASTSubValueExpression",  # 【元素表达式层级】插入语表达式：值表达式
    "ASTIndexExpression",  # 【下标表达式层级】下标表达式
    "ASTUnaryExpression",  # 【一元表达式层级】一元表达式

    # 运算表达式中的组合表达式
    "ASTComputeExpression",  # 使用计算运算符的二元表达式：包含异或表达式、单项表达式、多项表达式、移位表达式、按位与表达式和按位或表达式

    # 条件表达式中的元素表达式
    "ASTOperatorExpressionBase",  # 【关键字条件表达式层级】通过运算符或关键字比较运算符前后两个表达式的抽象类
    "ASTIsExpression",  # 【关键字条件表达式层级】使用 IS 的布尔值表达式
    "ASTInExpression",  # 【关键字条件表达式层级】使用 IN 的布尔值表达式
    "ASTLikeExpression",  # 【关键字条件表达式层级】使用 LIKE 的布尔值表达式
    "ASTExistsExpression",  # 【关键字条件表达式层级】使用 EXISTS 的布尔值表达式
    "ASTBetweenExpression",  # 【关键字条件表达式层级】使用 BETWEEN 的布尔值表达式
    "ASTRlikeExpression",  # 【关键字条件表达式层级】使用 RLIKE 的布尔值表达式
    "ASTRegexpExpression",  # 【关键字条件表达式层级】使用 REGEXP 的布尔值表达式

    # 条件表达式中的组合表达式
    "ASTOperatorConditionExpression",  # 【运算符条件表达式层级】运算符条件表达式
    "ASTLogicalNotExpression",  # 【逻辑否表达式层级】逻辑否表达式
    "ASTLogicalAndExpression",  # 【逻辑与表达式层级】逻辑与表达式
    "ASTLogicalXorExpression",  # 【逻辑异或表达式层级】逻辑异或表达式节点
    "ASTLogicalOrExpression",  # 【逻辑或表达式层级】逻辑或表达式节点

    # ------------------------------ 抽象语法树（AST）节点的子句节点 ------------------------------
    "ASTSelectColumn",  # SELECT 子句元素：包含别名的列表达式
    "ASTSelectClause",  # SELECT 子句
    "ASTFromTable",  # FROM 和 JOIN 子句元素：包含别名的表表达式
    "ASTFromClause",  # FROM 子句
    "ASTLateralViewClause",  # LATERAL VIEW 子句
    "ASTJoinOnExpression",  # JOIN 子句元素：使用 ON 关键字的关联表达式
    "ASTJoinUsingExpression",  # JOIN 子句元素：使用 USING 函数的关联表达式
    "ASTJoinClause",  # JOIN 子句
    "ASTWhereClause",  # WHERE 子句
    "ASTGroupingSets",  # GROUP BY 子句元素：GROUPING SETS 表达式
    "ASTGroupByClause",  # GROUP BY 子句
    "ASTHavingClause",  # HAVING 子句
    "ASTOrderByColumn",  # ORDER BY 子句元素：包含排序字段及排序顺序的表达式
    "ASTOrderByClause",  # ORDER BY 子句
    "ASTSortByClause",  # SORT BY 子句【Hive】
    "ASTDistributeByClause",  # DISTRIBUTE BY 子句【Hive】
    "ASTClusterByClause",  # CLUSTER BY 子句【Hive】
    "ASTLimitClause",  # LIMIT 子句
    "ASTWithClause",  # WITH 子句
    "ASTWithTable",  # WITH 子句元素：WITH 语句中的每个表

    # ------------------------------ 抽象语法树（AST）节点的 SELECT 语句节点 ------------------------------
    "ASTSelectStatement",  # SELECT 语句的抽象类
    "ASTSingleSelectStatement",  # SELECT 语句：没有 UNION 多个 SELECT 语句的 SELECT 语句
    "ASTUnionSelectStatement",  # SELECT 语句：UNION 了多个 SELECT 语句的组合后的 SELECT 语句

    # ------------------------------ 抽象语法树（AST）节点的 INSERT 语句节点 ------------------------------
    "ASTPartitionExpression",  # 分区表达式
    "ASTInsertStatement",  # INSERT 语句
    "ASTInsertValuesStatement",  # INSERT ... VALUES ... 语句
    "ASTInsertSelectStatement",  # INSERT ... SELECT ... 语句

    # ------------------------------ 抽象语法树（AST）节点的 CREATE TABLE 语句节点 ------------------------------
    "ASTConfigStringExpression",  # 配置值为字符串的配置表达式
    "ASTColumnTypeExpression",  # 字段类型表达式
    "ASTGeneratedColumn",  # 字段定义表达式中的计算字段
    "ASTDefineColumnExpression",  # 字段定义表达式
    "ASTIndexColumn",  # 索引声明表达式元素：索引声明表达式中的字段
    "ASTIndexExpressionBase",  # 索引声明表达式（抽象类）
    "ASTPrimaryIndexExpression",  # 主键索引声明表达式
    "ASTUniqueIndexExpression",  # 唯一键索引声明表达式
    "ASTNormalIndexExpression",  # 普通索引声明表达式
    "ASTFulltextIndexExpression",  # 全文本索引声明表达式
    "ASTForeignKeyExpression",  # 声明外键表达式
    "ASTCreateTableStatement",  # CREATE TABLE 语句
    "ASTCreateTableAsStatement",  # CREATE TABLE ... AS ... 语句

    # ------------------------------ 抽象语法树（AST）节点的 DROP TABLE 语句节点 ------------------------------
    "ASTDropTableStatement",  # DROP TABLE 语句

    # ------------------------------ 抽象语法树（AST）节点的 SET 语句节点 ------------------------------
    "ASTSetStatement",  # SET 语句

    # ------------------------------ 抽象语法树（AST）节点的 ANALYZE TABLE 语句节点 ------------------------------
    "ASTAnalyzeTableStatement",  # ANALYZE TABLE 语句

    # ------------------------------ 抽象语法树（AST）节点的 ALTER TABLE 语句节点 ------------------------------
    "ASTAlterExpressionBase",  # ALTER TABLE 语句的子句表达式的抽象基类
    "ASTAlterAddPartitionExpression",  # ALTER TABLE 语句的 ADD PARTITION 子句
    "ASTAlterAddExpression",  # ALTER TABLE 语句的 ADD 子句
    "ASTAlterModifyExpression",  # ALTER TABLE 语句的 MODIFY 子句
    "ASTAlterChangeExpression",  # ALTER TABLE 语句的 CHANGE 子句
    "ASTAlterDropColumnExpression",  # ALTER TABLE 语句的 DROP COLUMN 子句
    "ASTAlterDropPartitionExpression",  # ALTER TABLE 语句的 DROP PARTITION 子句
    "ASTAlterRenameColumnExpression",  # ALTER TABLE 语句的 RENAME ... TO ... 子句
    "ASTAlterTableStatement",  # ALTER TABLE 语句

    # ------------------------------ 抽象语法树（AST）节点的 MSCK REPAIR TABLE 语句节点 ------------------------------
    "ASTMsckRepairTableStatement",  # MSCK REPAIR TABLE 语句

    # ------------------------------ 抽象语法树（AST）节点的 USE 语句节点 ------------------------------
    "ASTUseStatement",  # USE 语句

    # ------------------------------ 抽象语法树（AST）节点的 TRUNCATE TABLE 语句节点 ------------------------------
    "ASTTruncateTable",  # TRUNCATE TABLE 语句

    # ------------------------------ 抽象语法树（AST）节点的 UPDATE 语句节点 ------------------------------
    "ASTUpdateSetColumn",  # SET 子句元素：SET 的列
    "ASTUpdateSetClause",  # UPDATE 语句中的 SET 子句
    "ASTUpdateStatement",  # UPDATE 语句

    # ------------------------------ 抽象语法树（AST）节点的 DELETE 语句节点 ------------------------------
    "ASTDeleteStatement",  # DELETE 语句

    # ------------------------------ 抽象语法树（AST）节点的 SHOW 语句节点 ------------------------------
    "ASTShowDatabasesStatement",  # SHOW DATABASES 语句
    "ASTShowTablesStatement",  # SHOW TABLES 语句
    "ASTShowColumnsStatement"  # SHOW COLUMNS 语句
]


# ---------------------------------------- 抽象基类 ----------------------------------------


@dataclasses.dataclass(slots=True, frozen=True, eq=True)
class ASTBase(abc.ABC):
    """抽象语法树（AST）节点的抽象基类"""

    @abc.abstractmethod
    def source(self, sql_type: SQLType = SQLType.DEFAULT) -> str:
        """返回语法节点的 SQL 源码"""

    def __str__(self) -> str:
        return self.__repr__()

    def __repr__(self) -> str:
        return f"<{self.__class__.__name__} source={self.source()}>"

    def get_params_dict(self):
        """获取当前节点的所有参数（用于复制）"""
        return {field.name: getattr(self, field.name) for field in dataclasses.fields(self)}


@dataclasses.dataclass(slots=True, frozen=True, eq=True)
class ASTStatementBase(ASTBase, abc.ABC):
    """抽象语法树（AST）语句节点的抽象基类"""


@dataclasses.dataclass(slots=True, frozen=True, eq=True)
class ASTExpressionBase(ASTBase, abc.ABC):
    """抽象语法树（AST）一般表达式节点的抽象基类"""

    @classmethod
    def node_name(cls):
        """节点名称：因为括号可以调整计算优先级，所以一般表达式节点的元素没有明确类型，需要允许获取节点类型的类方法"""
        return cls.__name__


# ---------------------------------------- 枚举类的抽象语法树节点 ----------------------------------------


@dataclasses.dataclass(slots=True, frozen=True, eq=True)
class ASTEnumListBase(ASTBase):
    """抽象语法树枚举类型的基类（枚举类值为列表）"""

    enum: Any = dataclasses.field(kw_only=True)

    def source(self, sql_type: SQLType = SQLType.DEFAULT) -> str:
        """返回语法节点的 SQL 源码"""
        return " ".join(self.enum.value)


@dataclasses.dataclass(slots=True, frozen=True, eq=True)
class ASTEnumElementBase(ASTBase):
    """抽象语法树枚举类型的基类（枚举类值为元素）"""

    enum: Any = dataclasses.field(kw_only=True)

    def source(self, sql_type: SQLType = SQLType.DEFAULT) -> str:
        """返回语法节点的 SQL 源码"""
        return self.enum.value


@dataclasses.dataclass(slots=True, frozen=True, eq=True)
class ASTInsertType(ASTEnumListBase):
    """插入类型"""

    enum: static.EnumInsertType = dataclasses.field(kw_only=True)  # 插入类型的枚举类


@dataclasses.dataclass(slots=True, frozen=True, eq=True)
class ASTJoinType(ASTEnumListBase):
    """关联类型"""

    enum: static.EnumJoinType = dataclasses.field(kw_only=True)  # 关联类型的枚举类


@dataclasses.dataclass(slots=True, frozen=True, eq=True)
class ASTOrderType(ASTEnumListBase):
    """排序类型"""

    enum: static.EnumOrderType = dataclasses.field(kw_only=True)  # 排序类型的枚举类


@dataclasses.dataclass(slots=True, frozen=True, eq=True)
class ASTUnionType(ASTEnumListBase):
    """组合类型"""

    enum: static.EnumUnionType = dataclasses.field(kw_only=True)  # 组合类型的枚举类


@dataclasses.dataclass(slots=True, frozen=True, eq=True)
class ASTCompareOperator(ASTEnumListBase):
    """比较运算符"""

    enum: static.EnumCompareOperator = dataclasses.field(kw_only=True)  # 比较运算符的枚举类


@dataclasses.dataclass(slots=True, frozen=True, eq=True)
class ASTComputeOperator(ASTEnumElementBase):
    """计算运算符"""

    enum: static.EnumComputeOperator = dataclasses.field(kw_only=True)  # 计算运算符的枚举类

    def source(self, sql_type: SQLType = SQLType.DEFAULT) -> str:
        # pylint: disable=R1725
        """返回语法节点的 SQL 源码"""
        if (self.enum == static.EnumComputeOperator.MOD
                and sql_type not in {SQLType.DEFAULT, SQLType.MYSQL, SQLType.SQL_SERVER, SQLType.HIVE}):
            raise NotSupportError(f"{sql_type} 不支持使用 % 运算符")
        return super(ASTComputeOperator, self).source(sql_type)


@dataclasses.dataclass(slots=True, frozen=True, eq=True)
class ASTLogicalOperator(ASTEnumListBase):
    """逻辑运算符"""

    enum: static.EnumLogicalOperator = dataclasses.field(kw_only=True)  # 逻辑运算符的枚举类


# ---------------------------------------- CASE 函数中的字段类型表达式 ----------------------------------------


@dataclasses.dataclass(slots=True, frozen=True, eq=True)
class ASTCastDataType(ASTBase):
    """CAST 语句中的数据类型"""

    signed: bool = dataclasses.field(kw_only=True)  # 是否包含 SIGNED 关键字
    type: static.EnumCastDataType = dataclasses.field(kw_only=True)  # 目标转换的数据类型
    params: Optional[Tuple[int, ...]] = dataclasses.field(kw_only=True)  # 目标转换的数据类型的参数列表

    def source(self, sql_type: SQLType = SQLType.DEFAULT) -> str:
        """返回语法节点的 SQL 源码"""
        result = []
        if self.signed is True:
            result.append("SIGNED")
        result.append(self.type.value)
        if self.params is not None:
            param_str = ", ".join(str(param) for param in self.params)
            result.append(f"({param_str})")
        return " ".join(result)


# ---------------------------------------- 表名表达式 ----------------------------------------


@dataclasses.dataclass(slots=True, frozen=True, eq=True)
class ASTTableNameExpression(ASTBase):
    """表名表达式"""

    schema_name: Optional[str] = dataclasses.field(kw_only=True, default=None)
    table_name: str = dataclasses.field(kw_only=True)

    def source(self, sql_type: SQLType = SQLType.DEFAULT) -> str:
        """返回语法节点的 SQL 源码"""
        return f"`{self.schema_name}.{self.table_name}`" if self.schema_name is not None else f"`{self.table_name}`"


# ---------------------------------------- 函数名表达式 ----------------------------------------


@dataclasses.dataclass(slots=True, frozen=True, eq=True)
class ASTFunctionNameExpression(ASTBase):
    """函数名表达式"""

    schema_name: Optional[str] = dataclasses.field(kw_only=True, default=None)
    function_name: str = dataclasses.field(kw_only=True)

    @staticmethod
    def by_name(function_name: str) -> "ASTFunctionNameExpression":
        """使用函数名构造"""
        return ASTFunctionNameExpression(function_name=function_name)

    def source(self, sql_type: SQLType = SQLType.DEFAULT) -> str:
        """返回语法节点的 SQL 源码"""
        return f"`{self.schema_name}`.{self.function_name}" if self.schema_name is not None else f"{self.function_name}"


# ---------------------------------------- 别名表达式 ----------------------------------------


@dataclasses.dataclass(slots=True, frozen=True, eq=True)
class ASTAlisaExpression(ASTBase):
    """别名表达式，例如：AS name"""

    name: str = dataclasses.field(kw_only=True)

    def source(self, sql_type: SQLType = SQLType.DEFAULT) -> str:
        """返回语法节点的 SQL 源码"""
        return f"AS {self.name}"


@dataclasses.dataclass(slots=True, frozen=True, eq=True)
class ASTMultiAlisaExpression(ASTBase):
    """多个别名表达式，例如：AS name1, name2, name3（在 Hive 的 LATERAL VIEW 语句中配合 json_tuple 等返回多个值的函数使用）"""

    names: Tuple[str, ...] = dataclasses.field(kw_only=True)

    def source(self, sql_type: SQLType = SQLType.DEFAULT) -> str:
        """返回语法节点的 SQL 源码"""
        names_str = ", ".join(self.names)
        return f"AS {names_str}"


# ---------------------------------------- 抽象语法树的一般表达式节点 ----------------------------------------


@dataclasses.dataclass(slots=True, frozen=True, eq=True)
class ASTBinaryExpressionBase(ASTExpressionBase):
    """二元表达式的抽象基类"""

    before_value: ASTExpressionBase = dataclasses.field(kw_only=True)
    operator = None
    after_value: ASTExpressionBase = dataclasses.field(kw_only=True)

    def source(self, sql_type: SQLType = SQLType.DEFAULT) -> str:
        """返回语法节点的 SQL 源码"""
        return (f"{self.before_value.source(sql_type)} {self.operator.source(sql_type)} "
                f"{self.after_value.source(sql_type)}")


@dataclasses.dataclass(slots=True, frozen=True, eq=True)
class ASTColumnNameExpression(ASTExpressionBase):
    """列名表达式"""

    table_name: Optional[str] = dataclasses.field(kw_only=True, default=None)  # 表名称
    column_name: str = dataclasses.field(kw_only=True)  # 字段名称

    def source(self, sql_type: SQLType = SQLType.DEFAULT) -> str:
        """返回语法节点的 SQL 源码"""
        if self.column_name not in {"*", "CURRENT_DATE", "CURRENT_TIME", "CURRENT_TIMESTAMP"}:
            result = (f"`{self.table_name}`.`{self.column_name}`" if self.table_name is not None
                      else f"`{self.column_name}`")
        else:
            result = f"`{self.table_name}`.{self.column_name}" if self.table_name is not None else f"{self.column_name}"
        if sql_type == SQLType.DB2:
            # 兼容 DB2 的 CURRENT DATE、CURRENT TIME、CURRENT TIMESTAMP 语法
            result = result.replace("CURRENT_DATE", "CURRENT DATE")
            result = result.replace("CURRENT_TIME", "CURRENT TIME")
            result = result.replace("CURRENT_TIMESTAMP", "CURRENT TIMESTAMP")
        return result


@dataclasses.dataclass(slots=True, frozen=True, eq=True)
class ASTLiteralExpression(ASTExpressionBase):
    """字面值表达式"""

    value: str = dataclasses.field(kw_only=True)  # 字面值

    def source(self, sql_type: SQLType = SQLType.DEFAULT) -> str:
        """返回语法节点的 SQL 源码"""
        return self.value

    def as_int(self) -> int:
        """将字面值作为整形返回"""
        if is_int_literal(self.value):
            return int(self.value)
        raise SqlParseError(f"无法字面值 {self.value} 转化为整型")

    def as_string(self) -> str:
        """将字面值作为字符串返回"""
        return self.value

    def get_value(self) -> Any:
        """返回当前字面值类型的返回值"""
        if is_int_literal(self.value):
            return int(self.value)
        if is_bool_literal(self.value):
            return self.value.upper() == "TRUE"
        if is_float_literal(self.value):
            return float(self.value)
        if is_null_literal(self.value):
            return None
        return self.value.strip("'")  # 字符串类型


@dataclasses.dataclass(slots=True, frozen=True, eq=True)
class ASTWildcardExpression(ASTExpressionBase):
    """通配符表达式"""

    table_name: Optional[str] = dataclasses.field(kw_only=True, default=None)

    def source(self, sql_type: SQLType = SQLType.DEFAULT) -> str:
        """返回语法节点的 SQL 源码"""
        return f"{self.table_name}.*" if self.table_name is not None else "*"


@dataclasses.dataclass(slots=True, frozen=True, eq=True)
class ASTFunctionExpressionBase(ASTExpressionBase, abc.ABC):
    """函数表达式的抽象基类"""

    name: ASTFunctionNameExpression = dataclasses.field(kw_only=True)


@dataclasses.dataclass(slots=True, frozen=True, eq=True)
class ASTNormalFunctionExpression(ASTFunctionExpressionBase):
    """包含一般参数的函数表达式"""

    params: Tuple[ASTExpressionBase, ...] = dataclasses.field(kw_only=True)  # 函数表达式的参数

    def source(self, sql_type: SQLType = SQLType.DEFAULT) -> str:
        """返回语法节点的 SQL 源码"""
        return f"{self.name.source()}({self._get_param_str(sql_type)})"

    def _get_param_str(self, sql_type: SQLType) -> str:
        return ", ".join(param.source(sql_type) for param in self.params)


@dataclasses.dataclass(slots=True, frozen=True, eq=True)
class ASTAggregationFunction(ASTNormalFunctionExpression):
    """聚合函数表达式"""

    is_distinct: bool = dataclasses.field(kw_only=True)  # 是否包含 DISTINCT 关键字

    def source(self, sql_type: SQLType = SQLType.DEFAULT) -> str:
        """返回语法节点的 SQL 源码"""
        is_distinct = "DISTINCT " if self.is_distinct is True else ""
        return f"{self.name.source()}({is_distinct}{self._get_param_str(sql_type)})"


@dataclasses.dataclass(slots=True, frozen=True, eq=True)
class ASTCastFunctionExpression(ASTFunctionExpressionBase):
    """Cast 函数表达式"""

    name: ASTFunctionNameExpression = dataclasses.field(init=False, default=ASTFunctionNameExpression.by_name("CAST"))
    column_expression: ASTExpressionBase = dataclasses.field(kw_only=True)  # CAST 表达式中要转换的列表达式
    cast_type: ASTCastDataType = dataclasses.field(kw_only=True)  # CAST 参数中目标要转换的函数类型

    def source(self, sql_type: SQLType = SQLType.DEFAULT) -> str:
        """返回语法节点的 SQL 源码"""
        return (f"{self.name.source()}"
                f"({self.column_expression.source(sql_type)} AS {self.cast_type.source(sql_type)})")


@dataclasses.dataclass(slots=True, frozen=True, eq=True)
class ASTExtractFunctionExpression(ASTFunctionExpressionBase):
    """Extract 函数表达式"""

    name: ASTFunctionNameExpression = dataclasses.field(init=False,
                                                        default=ASTFunctionNameExpression.by_name("EXTRACT"))
    extract_name: ASTExpressionBase = dataclasses.field(kw_only=True)  # FROM 关键字之前的提取名称
    column_expression: ASTExpressionBase = dataclasses.field(kw_only=True)  # FROM 关键字之后的一般表达式

    def source(self, sql_type: SQLType = SQLType.DEFAULT) -> str:
        """返回语法节点的 SQL 源码"""
        return (f"{self.name.source()}({self.extract_name.source(sql_type)} "
                f"FROM {self.column_expression.source(sql_type)})")


@dataclasses.dataclass(slots=True, frozen=True, eq=True)
class ASTWindowRowItem(ASTBase):
    """窗口函数中的行限制

    unbounded preceding = 当前行的所有行
    n preceding = 当前行之前的 n 行
    current row = 当前行
    n following = 当前行之后的 n行
    unbounded following = 当前行之后的所有行
    """

    row_type: static.EnumWindowRowType = dataclasses.field(kw_only=True)
    is_unbounded: bool = dataclasses.field(kw_only=True, default=False)
    row_num: Optional[int] = dataclasses.field(kw_only=True, default=None)

    def source(self, sql_type: SQLType = SQLType.DEFAULT) -> str:
        """返回语法节点的 SQL 源码"""
        if self.row_type == static.EnumWindowRowType.CURRENT_ROW:
            return "CURRENT ROW"
        row_type_str = self.row_type.value
        if self.is_unbounded is True:
            return f"UNBOUNDED {row_type_str}"
        return f"{self.row_num} {row_type_str}"


@dataclasses.dataclass(slots=True, frozen=True, eq=True)
class ASTWindowRow(ASTBase):
    """窗口函数中的行限制表达式

    ROWS BETWEEN {SQLWindowRow} AND {SQLWindowRow}
    """

    from_row: ASTWindowRowItem = dataclasses.field(kw_only=True)
    to_row: ASTWindowRowItem = dataclasses.field(kw_only=True)

    def source(self, sql_type: SQLType = SQLType.DEFAULT) -> str:
        """返回语法节点的 SQL 源码"""
        return f"ROWS BETWEEN {self.from_row.source(sql_type)} AND {self.to_row.source(sql_type)}"


@dataclasses.dataclass(slots=True, frozen=True, eq=True)
class ASTWindowExpression(ASTExpressionBase):
    """【元素表达式】窗口表达式"""

    window_function: Union[ASTNormalFunctionExpression, "ASTIndexExpression"] = dataclasses.field(kw_only=True)
    partition_by_columns: Tuple[ASTExpressionBase, ...] = dataclasses.field(kw_only=True)
    order_by_columns: Tuple["ASTOrderByColumn", ...] = dataclasses.field(kw_only=True)
    row_expression: Optional[ASTWindowRow] = dataclasses.field(kw_only=True)

    def source(self, sql_type: SQLType = SQLType.DEFAULT) -> str:
        """返回语法节点的 SQL 源码"""
        result = f"{self.window_function.source(sql_type)} OVER ("
        parenthesis = []
        if len(self.partition_by_columns) > 0:
            partition_by_str = ", ".join([column.source(sql_type) for column in self.partition_by_columns])
            parenthesis.append(f"PARTITION BY {partition_by_str}")
        if len(self.order_by_columns) > 0:
            order_by_str = ", ".join([column.source(sql_type) for column in self.order_by_columns])
            parenthesis.append(f"ORDER BY {order_by_str}")
        if self.row_expression is not None:
            parenthesis.append(self.row_expression.source(sql_type))
        result += " ".join(parenthesis) + ")"
        return result


@dataclasses.dataclass(slots=True, frozen=True, eq=True)
class ASTCaseConditionItem(ASTBase):
    """第 1 种格式的 CASE 表达式的 WHEN ... THEN ... 语句节点"""

    when: ASTExpressionBase = dataclasses.field(kw_only=True)
    then: ASTExpressionBase = dataclasses.field(kw_only=True)

    def source(self, sql_type: SQLType = SQLType.DEFAULT) -> str:
        """返回语法节点的 SQL 源码"""
        return f"WHEN {self.when.source(sql_type)} THEN {self.then.source(sql_type)}"


@dataclasses.dataclass(slots=True, frozen=True, eq=True)
class ASTCaseConditionExpression(ASTExpressionBase):
    """第 1 种格式的 CASE 表达式

    CASE
        WHEN {条件表达式} THEN {一般表达式}
        ELSE {一般表达式}
    END
    """

    cases: Tuple[ASTCaseConditionItem, ...] = dataclasses.field(kw_only=True)
    else_value: Optional[ASTExpressionBase] = dataclasses.field(kw_only=True)

    def source(self, sql_type: SQLType = SQLType.DEFAULT) -> str:
        """返回语法节点的 SQL 源码"""
        result = ["CASE"]
        for item in self.cases:
            result.append(item.source(sql_type))
        if self.else_value is not None:
            result.append(f"ELSE {self.else_value.source(sql_type)}")
        result.append("END")
        return " ".join(result)


@dataclasses.dataclass(slots=True, frozen=True, eq=True)
class ASTCaseValueItem(ASTBase):
    """第 2 种格式的 CASE 表达式的 WHEN ... THEN ... 语句节点"""

    when: ASTExpressionBase = dataclasses.field(kw_only=True)
    then: ASTExpressionBase = dataclasses.field(kw_only=True)

    def source(self, sql_type: SQLType = SQLType.DEFAULT) -> str:
        """返回语法节点的 SQL 源码"""
        return f"WHEN {self.when.source(sql_type)} THEN {self.then.source(sql_type)}"


@dataclasses.dataclass(slots=True, frozen=True, eq=True)
class ASTCaseValueExpression(ASTExpressionBase):
    """第 2 种格式的 CASE 表达式

    CASE {一般表达式}
        WHEN {一般表达式} THEN {一般表达式}
        ELSE {一般表达式}
    END
    """

    case_value: ASTExpressionBase = dataclasses.field(kw_only=True)
    cases: Tuple[ASTCaseValueItem, ...] = dataclasses.field(kw_only=True)
    else_value: Optional[ASTExpressionBase] = dataclasses.field(kw_only=True)

    def source(self, sql_type: SQLType = SQLType.DEFAULT) -> str:
        """返回语法节点的 SQL 源码"""
        result = ["CASE", self.case_value.source(sql_type)]
        for item in self.cases:
            result.append(f"    {item.source(sql_type)}")
        if self.else_value is not None:
            result.append(f"    ELSE {self.else_value.source(sql_type)}")
        result.append("END")
        return "\n".join(result)


@dataclasses.dataclass(slots=True, frozen=True, eq=True)
class ASTSubQueryExpression(ASTExpressionBase):
    """【元素表达式】子查询表达式"""

    statement: "ASTSelectStatement" = dataclasses.field(kw_only=True)

    def source(self, sql_type: SQLType = SQLType.DEFAULT) -> str:
        """返回语法节点的 SQL 源码"""
        return f"({self.statement.source(sql_type)})"


@dataclasses.dataclass(slots=True, frozen=True, eq=True)
class ASTSubValueExpression(ASTExpressionBase):
    """【元素表达式】值表达式：INSERT INTO 表达式中，VALUES 里的表达式"""

    values: Tuple[ASTExpressionBase, ...] = dataclasses.field(kw_only=True)

    def source(self, sql_type: SQLType = SQLType.DEFAULT) -> str:
        """返回语法节点的 SQL 源码"""
        values_str = ", ".join(value.source(sql_type) for value in self.values)
        return f"({values_str})"


@dataclasses.dataclass(slots=True, frozen=True, eq=True)
class ASTIndexExpression(ASTExpressionBase):
    """下标表达式"""

    array: ASTExpressionBase = dataclasses.field(kw_only=True)
    idx: ASTExpressionBase = dataclasses.field(kw_only=True)

    def source(self, sql_type: SQLType = SQLType.DEFAULT) -> str:
        """返回语法节点的 SQL 源码"""
        if sql_type != SQLType.HIVE:
            raise NotSupportError(f"数组下标不支持SQL类型:{sql_type}")
        return f"{self.array.source(sql_type)}"


@dataclasses.dataclass(slots=True, frozen=True, eq=True)
class ASTUnaryExpression(ASTExpressionBase):
    """一元表达式

    样例：~1、+1、-1
    """

    operator: ASTComputeOperator = dataclasses.field(kw_only=True)  # 一元运算符
    expression: ASTExpressionBase = dataclasses.field(kw_only=True)  # 表达式

    def source(self, sql_type: SQLType = SQLType.DEFAULT) -> str:
        """返回语法节点的 SQL 源码"""
        return f"{self.operator.source(sql_type=sql_type)}{self.expression.source(sql_type=sql_type)}"


@dataclasses.dataclass(slots=True, frozen=True, eq=True)
class ASTComputeExpression(ASTBinaryExpressionBase):
    """运算表达式"""

    operator: ASTComputeOperator = dataclasses.field(kw_only=True)


@dataclasses.dataclass(slots=True, frozen=True, eq=True)
class ASTOperatorExpressionBase(ASTExpressionBase, abc.ABC):
    """【一般表达式：关键字条件表达式层级】包含前后两个元素的关键字条件表达式"""

    is_not: bool = dataclasses.field(kw_only=True)
    before_value: ASTExpressionBase = dataclasses.field(kw_only=True)
    after_value: ASTExpressionBase = dataclasses.field(kw_only=True)


@dataclasses.dataclass(slots=True, frozen=True, eq=True)
class ASTIsExpression(ASTOperatorExpressionBase):
    """【一般表达式：关键字条件表达式层级】IS 运算符布尔值表达式"""

    def source(self, sql_type: SQLType = SQLType.DEFAULT) -> str:
        """返回语法节点的 SQL 源码"""
        keyword = "IS NOT" if self.is_not else "IS"
        return f"{self.before_value.source(sql_type)} {keyword} {self.after_value.source(sql_type)}"


@dataclasses.dataclass(slots=True, frozen=True, eq=True)
class ASTInExpression(ASTOperatorExpressionBase):
    """【一般表达式：关键字条件表达式层级】IN 关键字的布尔值表达式"""

    def source(self, sql_type: SQLType = SQLType.DEFAULT) -> str:
        """返回语法节点的 SQL 源码"""
        keyword = "NOT IN " if self.is_not else "IN"
        return f"{self.before_value.source(sql_type)} {keyword} {self.after_value.source(sql_type)}"


@dataclasses.dataclass(slots=True, frozen=True, eq=True)
class ASTLikeExpression(ASTOperatorExpressionBase):
    """【一般表达式：关键字条件表达式层级】LIKE 运算符关联表达式"""

    def source(self, sql_type: SQLType = SQLType.DEFAULT) -> str:
        """返回语法节点的 SQL 源码"""
        keyword = "NOT LIKE" if self.is_not else "LIKE"
        return f"{self.before_value.source(sql_type)} {keyword} {self.after_value.source(sql_type)}"


@dataclasses.dataclass(slots=True, frozen=True, eq=True)
class ASTRlikeExpression(ASTOperatorExpressionBase):
    """【一般表达式：关键字条件表达式层级】RLIKE 运算符关联表达式"""

    def source(self, sql_type: SQLType = SQLType.DEFAULT) -> str:
        """返回语法节点的 SQL 源码"""
        keyword = "NOT RLIKE" if self.is_not else "RLIKE"
        return f"{self.before_value.source(sql_type)} {keyword} {self.after_value.source(sql_type)}"


@dataclasses.dataclass(slots=True, frozen=True, eq=True)
class ASTRegexpExpression(ASTOperatorExpressionBase):
    """【一般表达式：关键字条件表达式层级】REGEXP 运算符关联表达式"""

    def source(self, sql_type: SQLType = SQLType.DEFAULT) -> str:
        """返回语法节点的 SQL 源码"""
        keyword = "NOT REGEXP" if self.is_not else "REGEXP"
        return f"{self.before_value.source(sql_type)} {keyword} {self.after_value.source(sql_type)}"


@dataclasses.dataclass(slots=True, frozen=True, eq=True)
class ASTExistsExpression(ASTExpressionBase):
    """【一般表达式：关键字条件表达式层级】Exists 运算符关联表达式"""

    value: ASTExpressionBase = dataclasses.field(kw_only=True)  # 子查询

    def source(self, sql_type: SQLType = SQLType.DEFAULT) -> str:
        """返回语法节点的 SQL 源码"""
        return f"EXISTS {self.value.source(sql_type)}"


@dataclasses.dataclass(slots=True, frozen=True, eq=True)
class ASTBetweenExpression(ASTExpressionBase):
    """【一般表达式：关键字条件表达式层级】BETWEEN 关联表达式"""

    is_not: bool = dataclasses.field(kw_only=True)  # 一元表达式
    before_value: ASTExpressionBase = dataclasses.field(kw_only=True)
    from_value: ASTExpressionBase = dataclasses.field(kw_only=True)
    to_value: ASTExpressionBase = dataclasses.field(kw_only=True)

    def source(self, sql_type: SQLType = SQLType.DEFAULT) -> str:
        """返回语法节点的 SQL 源码"""
        if_not_str = "NOT " if self.is_not else ""
        return (f"{self.before_value.source(sql_type)} {if_not_str}"
                f"BETWEEN {self.from_value.source(sql_type)} AND {self.to_value.source(sql_type)}")


@dataclasses.dataclass(slots=True, frozen=True, eq=True)
class ASTOperatorConditionExpression(ASTBinaryExpressionBase):
    """运算符条件表达式"""

    operator: ASTCompareOperator = dataclasses.field(kw_only=True)


@dataclasses.dataclass(slots=True, frozen=True, eq=True)
class ASTLogicalNotExpression(ASTExpressionBase):
    """逻辑否表达式"""

    operator = ASTLogicalOperator(enum=static.EnumLogicalOperator.LOGICAL_NOT)
    expression: ASTExpressionBase = dataclasses.field(kw_only=True)

    def source(self, sql_type: SQLType = SQLType.DEFAULT) -> str:
        """返回语法节点的 SQL 源码"""
        return f"{self.operator.source(sql_type)} {self.expression.source(sql_type)}"


@dataclasses.dataclass(slots=True, frozen=True, eq=True)
class ASTLogicalAndExpression(ASTBinaryExpressionBase):
    """逻辑与表达式"""

    operator = ASTLogicalOperator(enum=static.EnumLogicalOperator.LOGICAL_AND)


@dataclasses.dataclass(slots=True, frozen=True, eq=True)
class ASTLogicalXorExpression(ASTBinaryExpressionBase):
    """逻辑异或表达式"""

    operator = ASTLogicalOperator(enum=static.EnumLogicalOperator.LOGICAL_XOR)


@dataclasses.dataclass(slots=True, frozen=True, eq=True)
class ASTLogicalOrExpression(ASTBinaryExpressionBase):
    """逻辑或表达式"""

    operator = ASTLogicalOperator(enum=static.EnumLogicalOperator.LOGICAL_OR)


# ---------------------------------------- 表表达式 ----------------------------------------


@dataclasses.dataclass(slots=True, frozen=True, eq=True)
class ASTFromTable(ASTBase):
    """表表达式"""

    name: Union[ASTTableNameExpression, ASTSubQueryExpression] = dataclasses.field(kw_only=True)
    alias: Optional[ASTAlisaExpression] = dataclasses.field(kw_only=True, default=None)

    def source(self, sql_type: SQLType = SQLType.DEFAULT) -> str:
        """返回语法节点的 SQL 源码"""
        if self.alias is not None:
            return f"{self.name.source(sql_type)} {self.alias.source(sql_type)}"
        return f"{self.name.source(sql_type)}"


# ---------------------------------------- SELECT 子句 ----------------------------------------


@dataclasses.dataclass(slots=True, frozen=True, eq=True)
class ASTSelectColumn(ASTBase):
    """在 SELECT 语句中的每一列的表达式"""

    value: ASTExpressionBase = dataclasses.field(kw_only=True)
    alias: Optional[ASTAlisaExpression] = dataclasses.field(kw_only=True, default=None)

    def source(self, sql_type: SQLType = SQLType.DEFAULT) -> str:
        """返回语法节点的 SQL 源码"""
        if self.alias is not None:
            return f"{self.value.source(sql_type)} {self.alias.source(sql_type)}"
        return f"{self.value.source(sql_type)}"


@dataclasses.dataclass(slots=True, frozen=True, eq=True)
class ASTSelectClause(ASTBase):
    """SELECT 子句"""

    distinct: bool = dataclasses.field(kw_only=True)
    columns: Tuple[ASTSelectColumn, ...] = dataclasses.field(kw_only=True)

    def source(self, sql_type: SQLType = SQLType.DEFAULT) -> str:
        """返回语法节点的 SQL 源码"""
        result = ["SELECT"]
        if self.distinct is True:
            result.append("DISTINCT")
        result.append(", ".join(column.source(sql_type) for column in self.columns))
        return " ".join(result)


# ---------------------------------------- FROM 子句 ----------------------------------------

@dataclasses.dataclass(slots=True, frozen=True, eq=True)
class ASTFromClause(ASTBase):
    """FROM 子句"""

    tables: Tuple[ASTFromTable, ...] = dataclasses.field(kw_only=True)

    def source(self, sql_type: SQLType = SQLType.DEFAULT) -> str:
        """返回语法节点的 SQL 源码"""
        return "FROM " + ", ".join(table.source(sql_type) for table in self.tables)


# ---------------------------------------- LATERAL VIEW 子句 ----------------------------------------


@dataclasses.dataclass(slots=True, frozen=True, eq=True)
class ASTLateralViewClause(ASTBase):
    """LATERAL VIEW 子句"""

    outer: bool = dataclasses.field(kw_only=True)
    function: ASTFunctionExpressionBase = dataclasses.field(kw_only=True)
    view_name: str = dataclasses.field(kw_only=True)
    alias: ASTMultiAlisaExpression = dataclasses.field(kw_only=True)

    def source(self, sql_type: SQLType = SQLType.DEFAULT) -> str:
        """返回语法节点的 SQL 源码"""
        outer_str = "OUT " if self.outer is True else ""
        return (f"LATERAL VIEW {outer_str}{self.function.source(sql_type)} "
                f"{self.view_name} {self.alias.source(sql_type)}")


# ---------------------------------------- JOIN 子句 ----------------------------------------

@dataclasses.dataclass(slots=True, frozen=True, eq=True)
class ASTJoinOnExpression(ASTBase):
    """ON 关联表达式"""

    condition: ASTLogicalOrExpression = dataclasses.field(kw_only=True)

    def source(self, sql_type: SQLType = SQLType.DEFAULT) -> str:
        """返回语法节点的 SQL 源码"""
        return f"ON {self.condition.source(sql_type)}"


@dataclasses.dataclass(slots=True, frozen=True, eq=True)
class ASTJoinUsingExpression(ASTBase):
    """USING 关联表达式"""

    using_function: ASTFunctionExpressionBase = dataclasses.field(kw_only=True)

    def source(self, sql_type: SQLType = SQLType.DEFAULT) -> str:
        """返回语法节点的 SQL 源码"""
        return f"{self.using_function.source(sql_type)}"


@dataclasses.dataclass(slots=True, frozen=True, eq=True)
class ASTJoinClause(ASTBase):
    """JOIN 子句"""

    type: ASTJoinType = dataclasses.field(kw_only=True)
    table: ASTFromTable = dataclasses.field(kw_only=True)
    rule: Optional[Union[ASTJoinOnExpression, ASTJoinUsingExpression]] = dataclasses.field(kw_only=True)

    def source(self, sql_type: SQLType = SQLType.DEFAULT) -> str:
        """返回语法节点的 SQL 源码"""
        if self.rule is not None:
            return (f"{self.type.source(sql_type)} {self.table.source(sql_type)} "
                    f"{self.rule.source(sql_type)}")
        return f"{self.type.source(sql_type)} {self.table.source(sql_type)}"


# ---------------------------------------- WHERE 子句 ----------------------------------------


@dataclasses.dataclass(slots=True, frozen=True, eq=True)
class ASTWhereClause(ASTBase):
    """WHERE 子句"""

    condition: ASTLogicalOrExpression = dataclasses.field(kw_only=True)

    def source(self, sql_type: SQLType = SQLType.DEFAULT) -> str:
        """返回语法节点的 SQL 源码"""
        return f"WHERE {self.condition.source(sql_type)}"


# ---------------------------------------- GROUP BY 子句 ----------------------------------------

@dataclasses.dataclass(slots=True, frozen=True, eq=True)
class ASTGroupingSets(ASTBase):
    """使用 GROUPING SETS 语法的 GROUP BY 子句"""

    grouping_list: Tuple[Tuple[ASTExpressionBase, ...], ...] = dataclasses.field(kw_only=True)

    def source(self, sql_type: SQLType = SQLType.DEFAULT) -> str:
        """返回语法节点的 SQL 源码"""
        grouping_str_list = []
        for grouping in self.grouping_list:
            if len(grouping) > 1:
                grouping_str_list.append("(" + ", ".join(column.source(sql_type) for column in grouping) + ")")
            else:
                grouping_str_list.append(grouping[0].source(sql_type))
        return "GROUPING SETS (" + ", ".join(grouping_str_list) + ")"


@dataclasses.dataclass(slots=True, frozen=True, eq=True)
class ASTGroupByClause(ASTBase):
    """GROUP BY 子句"""

    columns: Tuple[ASTExpressionBase, ...] = dataclasses.field(kw_only=True)
    grouping_sets: ASTGroupingSets = dataclasses.field(kw_only=True)
    with_cube: bool = dataclasses.field(kw_only=True)
    with_rollup: bool = dataclasses.field(kw_only=True)

    def source(self, sql_type: SQLType = SQLType.DEFAULT) -> str:
        """返回语法节点的 SQL 源码"""
        columns_str = ", ".join(column.source(sql_type) for column in self.columns)
        grouping_sets_str = f" {self.grouping_sets.source(sql_type)}" if self.grouping_sets is not None else ""
        with_cube_str = " WITH CUBE" if self.with_cube is True else ""
        with_rollup_str = " WITH ROLLUP" if self.with_rollup is True else ""
        return f"GROUP BY {columns_str}{grouping_sets_str}{with_cube_str}{with_rollup_str}"


# ---------------------------------------- HAVING 子句 ----------------------------------------


@dataclasses.dataclass(slots=True, frozen=True, eq=True)
class ASTHavingClause(ASTBase):
    """HAVING 子句"""

    condition: ASTLogicalOrExpression = dataclasses.field(kw_only=True)

    def source(self, sql_type: SQLType = SQLType.DEFAULT) -> str:
        """返回语法节点的 SQL 源码"""
        return f"HAVING {self.condition.source(sql_type)}"


# ---------------------------------------- ORDER BY 子句 ----------------------------------------


@dataclasses.dataclass(slots=True, frozen=True, eq=True)
class ASTOrderByColumn(ASTBase):
    """ORDER BY 子句中每一个字段及排序顺序的节点"""

    column: ASTExpressionBase = dataclasses.field(kw_only=True)  # 排序字段
    order: ASTOrderType = dataclasses.field(kw_only=True)  # 排序类型
    nulls_first: bool = dataclasses.field(kw_only=True)  # 是否包含 NULLS FIRST 关键字（将 NULL 值放到开头）
    nulls_last: bool = dataclasses.field(kw_only=True)  # 是否包含 NULLS LAST 关键字（将 NULL 值放到末尾）

    def source(self, sql_type: SQLType = SQLType.DEFAULT) -> str:
        """返回语法节点的 SQL 源码"""
        nulls_first_str = " NULLS FIRST" if self.nulls_first else ""
        nulls_last_str = " NULLS LAST" if self.nulls_last else ""
        if self.order.source(sql_type) == "ASC":
            return f"{self.column.source(sql_type)}{nulls_first_str}{nulls_last_str}"
        return f"{self.column.source(sql_type)} DESC{nulls_first_str}{nulls_last_str}"


@dataclasses.dataclass(slots=True, frozen=True, eq=True)
class ASTOrderByClause(ASTBase):
    """ORDER BY 子句"""

    columns: Tuple[ASTOrderByColumn, ...] = dataclasses.field(kw_only=True)

    def source(self, sql_type: SQLType = SQLType.DEFAULT) -> str:
        """返回语法节点的 SQL 源码"""
        result = [column.source(sql_type) for column in self.columns]
        return "ORDER BY " + ", ".join(result)


# ---------------------------------------- SORT BY 子句 ----------------------------------------


@dataclasses.dataclass(slots=True, frozen=True, eq=True)
class ASTSortByClause(ASTBase):
    """SORT BY 子句（Hive）"""

    columns: Tuple[ASTOrderByColumn, ...] = dataclasses.field(kw_only=True)

    def source(self, sql_type: SQLType = SQLType.DEFAULT) -> str:
        """返回语法节点的 SQL 源码"""
        result = [column.source(sql_type) for column in self.columns]
        return "SORT BY " + ", ".join(result)


# ---------------------------------------- DISTRIBUTE BY 子句 ----------------------------------------


@dataclasses.dataclass(slots=True, frozen=True, eq=True)
class ASTDistributeByClause(ASTBase):
    """DISTRIBUTE BY 子句（Hive）"""

    columns: Tuple[ASTExpressionBase, ...] = dataclasses.field(kw_only=True)

    def source(self, sql_type: SQLType = SQLType.DEFAULT) -> str:
        """返回语法节点的 SQL 源码"""
        return "DISTRIBUTE BY " + ", ".join(column.source(sql_type) for column in self.columns)


# ---------------------------------------- CLUSTER BY 子句 ----------------------------------------


@dataclasses.dataclass(slots=True, frozen=True, eq=True)
class ASTClusterByClause(ASTBase):
    """CLUSTER BY 子句（Hive）"""

    columns: Tuple[ASTExpressionBase, ...] = dataclasses.field(kw_only=True)

    def source(self, sql_type: SQLType = SQLType.DEFAULT) -> str:
        """返回语法节点的 SQL 源码"""
        return "CLUSTER BY " + ", ".join(column.source(sql_type) for column in self.columns)


# ---------------------------------------- LIMIT 子句 ----------------------------------------


@dataclasses.dataclass(slots=True, frozen=True, eq=True)
class ASTLimitClause(ASTBase):
    """LIMIT 子句"""

    limit: int = dataclasses.field(kw_only=True)
    offset: Optional[int] = dataclasses.field(kw_only=True)

    def source(self, sql_type: SQLType = SQLType.DEFAULT) -> str:
        """返回语法节点的 SQL 源码"""
        return f"LIMIT {self.offset}, {self.limit}"


# ---------------------------------------- WITH 子句 ----------------------------------------


@dataclasses.dataclass(slots=True, frozen=True, eq=True)
class ASTWithTable(ASTBase):
    """WITH 子句中的表元素"""

    name: str = dataclasses.field(kw_only=True)
    statement: "ASTSelectStatement" = dataclasses.field(kw_only=True)

    def source(self, sql_type: SQLType = SQLType.DEFAULT) -> str:
        """返回语法节点的 SQL 源码"""
        return f"{self.name}({self.statement.source(sql_type)})"


@dataclasses.dataclass(slots=True, frozen=True, eq=True)
class ASTWithClause(ASTBase):
    """WITH 子句"""

    tables: Tuple[ASTWithTable, ...] = dataclasses.field(kw_only=True)

    @staticmethod
    def empty():
        """空 WITH 子句"""
        return ASTWithClause(tables=tuple())

    def source(self, sql_type: SQLType = SQLType.DEFAULT) -> str:
        """返回语法节点的 SQL 源码"""
        if not self.tables:
            return ""
        table_str = ", \n".join(table.source(sql_type) for table in self.tables)
        return f"WITH {table_str}"

    def is_empty(self):
        """返回 WITH 语句是否为空"""
        return len(self.tables) == 0


# ---------------------------------------- SELECT 语句 ----------------------------------------


@dataclasses.dataclass(slots=True, frozen=True, eq=True)
class ASTStatementHasWithClauseBase(ASTStatementBase, abc.ABC):
    """包含 WITH 语句的语句的抽象基类"""

    with_clause: Optional[ASTWithClause] = dataclasses.field(kw_only=True, default=None)


@dataclasses.dataclass(slots=True, frozen=True, eq=True)
class ASTSelectStatement(ASTStatementHasWithClauseBase, abc.ABC):
    """SELECT 语句"""

    @abc.abstractmethod
    def set_with_clauses(self, with_clause: Optional[ASTWithClause]) -> "ASTSelectStatement":
        """设置 WITH 语句"""


@dataclasses.dataclass(slots=True, frozen=True, eq=True)
class ASTSingleSelectStatement(ASTSelectStatement):
    # pylint: disable=R0902 忽略对象属性过多的问题
    """单个 SELECT 表达式"""

    with_clause: Optional[ASTWithClause] = dataclasses.field(kw_only=True)
    select_clause: ASTSelectClause = dataclasses.field(kw_only=True)
    from_clause: Optional[ASTFromClause] = dataclasses.field(kw_only=True)
    lateral_view_clauses: Tuple[ASTLateralViewClause, ...] = dataclasses.field(kw_only=True)
    join_clauses: Tuple[ASTJoinClause, ...] = dataclasses.field(kw_only=True)
    where_clause: Optional[ASTWhereClause] = dataclasses.field(kw_only=True)
    group_by_clause: Optional[ASTGroupByClause] = dataclasses.field(kw_only=True)
    having_clause: Optional[ASTHavingClause] = dataclasses.field(kw_only=True)
    order_by_clause: Optional[ASTOrderByClause] = dataclasses.field(kw_only=True)
    sort_by_clause: Optional[ASTSortByClause] = dataclasses.field(kw_only=True, default=None)
    distribute_by_clause: Optional[ASTDistributeByClause] = dataclasses.field(kw_only=True, default=None)
    cluster_by_clause: Optional[ASTClusterByClause] = dataclasses.field(kw_only=True, default=None)
    limit_clause: Optional[ASTLimitClause] = dataclasses.field(kw_only=True)

    def source(self, sql_type: SQLType = SQLType.DEFAULT) -> str:
        """返回语法节点的 SQL 源码"""
        with_clause_str = self.with_clause.source(sql_type) + "\n" if not self.with_clause.is_empty() else ""
        result = [self.select_clause.source(sql_type)]

        # 构造子句的顺序列表
        if sql_type == SQLType.HIVE:
            clauses = [self.from_clause, *self.lateral_view_clauses, *self.join_clauses, self.where_clause,
                       self.group_by_clause, self.having_clause, self.order_by_clause, self.sort_by_clause,
                       self.distribute_by_clause, self.cluster_by_clause, self.limit_clause]
        else:
            clauses = [self.from_clause, *self.lateral_view_clauses, *self.join_clauses, self.where_clause,
                       self.group_by_clause, self.having_clause, self.order_by_clause, self.limit_clause]

        # 按顺序构造子句
        for clause in clauses:
            if clause is not None:
                result.append(clause.source(sql_type))
        return with_clause_str + "\n".join(result)

    def set_with_clauses(self, with_clause: Optional[ASTWithClause]) -> ASTSelectStatement:
        params = self.get_params_dict()
        params["with_clause"] = with_clause
        return ASTSingleSelectStatement(**params)


@dataclasses.dataclass(slots=True, frozen=True, eq=True)
class ASTUnionSelectStatement(ASTSelectStatement):
    """复合查询语句，使用 UNION、EXCEPT、INTERSECT 进行组合"""

    elements: Tuple[Union[ASTUnionType, ASTSingleSelectStatement], ...] = dataclasses.field(kw_only=True)

    def source(self, sql_type: SQLType = SQLType.DEFAULT) -> str:
        """返回语法节点的 SQL 源码"""
        with_clause_str = self.with_clause.source(sql_type) + "\n" if not self.with_clause.is_empty() else ""
        return with_clause_str + "\n".join(element.source(sql_type) for element in self.elements)

    def set_with_clauses(self, with_clause: Optional[ASTWithClause]) -> ASTSelectStatement:
        params = self.get_params_dict()
        params["with_clause"] = with_clause
        return ASTUnionSelectStatement(**params)


# ---------------------------------------- 分区表达式 ----------------------------------------


@dataclasses.dataclass(slots=True, frozen=True, eq=True)
class ASTPartitionExpression(ASTBase):
    """分区表达式：PARTITION (<partition_expression>)"""

    partitions: Tuple[ASTExpressionBase, ...] = dataclasses.field(kw_only=True)

    def source(self, sql_type: SQLType = SQLType.DEFAULT) -> str:
        """返回语法节点的 SQL 源码"""
        partition_list_str = ", ".join(partition.source(sql_type) for partition in self.partitions)
        return f"PARTITION ({partition_list_str})"


# ---------------------------------------- INSERT 语句 ----------------------------------------


@dataclasses.dataclass(slots=True, frozen=True, eq=True)
class ASTInsertStatement(ASTStatementHasWithClauseBase, abc.ABC):
    """INSERT 表达式

    两个子类包含 VALUES 和 SELECT 两种方式

    INSERT {INTO|OVERWRITE} [TABLE] <table_name_expression> [PARTITION (<partition_expression>)]
    [(<colum_name_expression [,<column_name_expression> ...]>)]
    {VALUES <value_expression> [,<value_expression> ...] | <select_statement>}
    """

    insert_type: ASTInsertType = dataclasses.field(kw_only=True)
    table_name: ASTTableNameExpression = dataclasses.field(kw_only=True)
    partition: Optional[ASTPartitionExpression] = dataclasses.field(kw_only=True)
    columns: Optional[Tuple[ASTColumnNameExpression, ...]] = dataclasses.field(kw_only=True)

    def _insert_str(self, sql_type: SQLType) -> str:
        insert_type_str = self.insert_type.source(sql_type)
        table_keyword_str = "TABLE " if sql_type == SQLType.HIVE else ""
        partition_str = f"{self.partition.source(sql_type)} " if self.partition is not None else ""
        if self.columns is not None:
            columns_str = "(" + ", ".join(column.source(sql_type) for column in self.columns) + ") "
        else:
            columns_str = ""
        return (f"{insert_type_str} {table_keyword_str}{self.table_name.source(sql_type)} "
                f"{partition_str}{columns_str}")


@dataclasses.dataclass(slots=True, frozen=True, eq=True)
class ASTInsertValuesStatement(ASTInsertStatement):
    """INSERT ... VALUES ... 语句"""

    values: Tuple[ASTSubValueExpression, ...] = dataclasses.field(kw_only=True)

    def source(self, sql_type: SQLType = SQLType.DEFAULT) -> str:
        """返回语法节点的 SQL 源码"""
        values_str = ", ".join(value.source(sql_type) for value in self.values)
        return f"{self._insert_str(sql_type)}VALUES {values_str}"


@dataclasses.dataclass(slots=True, frozen=True, eq=True)
class ASTInsertSelectStatement(ASTInsertStatement):
    """INSERT ... SELECT ... 语句"""

    select_statement: ASTSelectStatement = dataclasses.field(kw_only=True)

    def source(self, sql_type: SQLType = SQLType.DEFAULT) -> str:
        """返回语法节点的 SQL 源码"""
        return f"{self._insert_str(sql_type)} {self.select_statement.source(sql_type)}"


# ---------------------------------------- 配置表达式 ----------------------------------------

@dataclasses.dataclass(slots=True, frozen=True, eq=True)
class ASTConfigStringExpression(ASTBase):
    """配置值为字符窜的配置表达式"""

    name: str = dataclasses.field(kw_only=True)
    value: str = dataclasses.field(kw_only=True)

    def source(self, sql_type: SQLType = SQLType.DEFAULT) -> str:
        return f"{self.name}={self.value}"


# ---------------------------------------- 字段类型表达式 ----------------------------------------

@dataclasses.dataclass(slots=True, frozen=True, eq=True)
class ASTColumnTypeExpression(ASTBase):
    """字段类型表达式"""

    name: str = dataclasses.field(kw_only=True)
    params: Optional[Tuple[ASTExpressionBase, ...]] = dataclasses.field(kw_only=True, default=None)

    def source(self, sql_type: SQLType = SQLType.DEFAULT) -> str:
        """返回语法节点的 SQL 源码
        
        TODO：后续计划将类型的处理，移动到翻译器中，而不是放置在 Node 节点中，因为这并不是一个适用于所有应用场景的功能，可能会引发特殊的 Bug
        """
        # 如果没有参数，则不添加参数
        if self.params is None:
            return self.name
        # 如果为 Hive 中没有参数的类型，也不添加参数
        if sql_type == SQLType.HIVE and self.name.upper() not in {"DECIMAL", "VARCHAR", "CHAR"}:
            return self.name
        # MySQL 标准导出逗号间没有空格
        type_params = "(" + ",".join([param.source(sql_type) for param in self.params]) + ")"
        return f"{self.name}{type_params}"


# ---------------------------------------- 声明字段表达式 ----------------------------------------


@dataclasses.dataclass(slots=True, frozen=True, eq=True)
class ASTGeneratedColumn(ASTBase):
    """计算字段"""

    expression: ASTExpressionBase = dataclasses.field(kw_only=True)
    save_mode: static.EnumGenerateColumnSaveMode = dataclasses.field(kw_only=True)

    def source(self, sql_type: SQLType = SQLType.DEFAULT) -> str:
        """返回语法节点的 SQL 源码"""
        return f"GENERATED ALWAYS AS ({self.expression.source(sql_type)}) {self.save_mode.name}"


@dataclasses.dataclass(slots=True, frozen=True, eq=True)
class ASTDefineColumnExpression(ASTBase):
    # pylint: disable=R0902 忽略对象属性过多的问题
    """声明字段表达式"""

    column_name: str = dataclasses.field(kw_only=True)
    column_type: ASTColumnTypeExpression = dataclasses.field(kw_only=True)
    is_unsigned: bool = dataclasses.field(kw_only=True, default=False)
    is_zerofill: bool = dataclasses.field(kw_only=True, default=False)
    character_set: Optional[str] = dataclasses.field(kw_only=True, default=None)
    collate: Optional[str] = dataclasses.field(kw_only=True, default=None)
    generated_always_as: Optional[ASTGeneratedColumn] = dataclasses.field(kw_only=True, default=None)
    is_allow_null: bool = dataclasses.field(kw_only=True, default=False)
    is_not_null: bool = dataclasses.field(kw_only=True, default=False)
    is_auto_increment: bool = dataclasses.field(kw_only=True, default=False)
    default: Optional[ASTExpressionBase] = dataclasses.field(kw_only=True, default=None)
    on_update: Optional[ASTExpressionBase] = dataclasses.field(kw_only=True, default=None)
    comment: Optional[str] = dataclasses.field(kw_only=True, default=None)

    @property
    def column_name_without_quote(self) -> str:
        """返回没有被引号框柱的列名"""
        return self.column_name

    def source(self, sql_type: SQLType = SQLType.DEFAULT) -> str:
        """返回语法节点的 SQL 源码"""
        res = f"`{self.column_name}` {self.column_type.source(sql_type)}"
        res += " UNSIGNED" if self.is_unsigned is True and sql_type == SQLType.MYSQL else ""
        if self.is_zerofill is True and sql_type == SQLType.MYSQL:
            res += " ZEROFILL"
        if self.character_set is not None and sql_type == SQLType.MYSQL:
            res += f" CHARACTER SET {self.character_set}"
        if self.collate is not None and sql_type == SQLType.MYSQL:
            res += f" COLLATE {self.collate}"
        if self.generated_always_as is not None and sql_type == SQLType.MYSQL:
            res += f" {self.generated_always_as.source(sql_type)}"
        if self.is_allow_null is True and sql_type == SQLType.MYSQL:
            res += " NULL"
        if self.is_not_null is True and sql_type == SQLType.MYSQL:
            res += " NOT NULL"
        if self.is_auto_increment is True and sql_type == SQLType.MYSQL:
            res += " AUTO_INCREMENT"
        if self.default is not None and sql_type == SQLType.MYSQL:
            res += f" DEFAULT {self.default.source(sql_type)}"
        if self.on_update is not None and sql_type == SQLType.MYSQL:
            res += f" ON UPDATE {self.on_update.source(sql_type)}"
        if self.comment is not None:
            res += f" COMMENT {self.comment}"
        return res


# ---------------------------------------- 声明索引表达式 ----------------------------------------


@dataclasses.dataclass(slots=True, frozen=True, eq=True)
class ASTIndexColumn(ASTBase):
    """索引声明表达式中的字段"""

    name: str = dataclasses.field(kw_only=True)  # 字段名
    max_length: Optional[int] = dataclasses.field(kw_only=True, default=None)  # 最大长度

    def source(self, sql_type: SQLType = SQLType.DEFAULT) -> str:
        """返回语法节点的 SQL 源码"""
        if self.max_length is None:
            return f"`{self.name}`"
        return f"`{self.name}`({self.max_length})"


@dataclasses.dataclass(slots=True, frozen=True, eq=True)
class ASTIndexExpressionBase(ASTBase, abc.ABC):
    """声明索引表达式"""

    name: Optional[str] = dataclasses.field(kw_only=True, default=None)
    columns: Tuple[ASTIndexColumn, ...] = dataclasses.field(kw_only=True)
    using: Optional[str] = dataclasses.field(kw_only=True, default=None)
    comment: Optional[str] = dataclasses.field(kw_only=True, default=None)
    key_block_size: Optional[int] = dataclasses.field(kw_only=True, default=None)

    def _source(self, sql_type: SQLType, index_type: str):
        if self.columns is None:
            return ""
        name_str = f" {self.name}" if self.name is not None else ""
        columns_str = ",".join([f"{column.source(sql_type)}" for column in self.columns])
        using_str = f" USING {self.using}" if self.using is not None else ""
        comment_str = f" COMMENT {self.comment}" if self.comment is not None else ""
        config_str = f" KEY_BLOCK_SIZE={self.key_block_size}" if self.key_block_size is not None else ""
        return f"{index_type}{name_str} ({columns_str}){using_str}{comment_str}{config_str}"


@dataclasses.dataclass(slots=True, frozen=True, eq=True)
class ASTPrimaryIndexExpression(ASTIndexExpressionBase):
    """主键索引声明表达式"""

    def source(self, sql_type: SQLType = SQLType.DEFAULT) -> str:
        """返回语法节点的 SQL 源码"""
        return self._source(sql_type, "PRIMARY KEY")


@dataclasses.dataclass(slots=True, frozen=True, eq=True)
class ASTUniqueIndexExpression(ASTIndexExpressionBase):
    """唯一键索引声明表达式"""

    def source(self, sql_type: SQLType = SQLType.DEFAULT) -> str:
        """返回语法节点的 SQL 源码"""
        return self._source(sql_type, "UNIQUE KEY")


@dataclasses.dataclass(slots=True, frozen=True, eq=True)
class ASTNormalIndexExpression(ASTIndexExpressionBase):
    """普通索引声明表达式"""

    def source(self, sql_type: SQLType = SQLType.DEFAULT) -> str:
        """返回语法节点的 SQL 源码"""
        return self._source(sql_type, "KEY")


@dataclasses.dataclass(slots=True, frozen=True, eq=True)
class ASTFulltextIndexExpression(ASTIndexExpressionBase):
    """全文本索引声明表达式"""

    def source(self, sql_type: SQLType = SQLType.DEFAULT) -> str:
        """返回语法节点的 SQL 源码"""
        return self._source(sql_type, "FULLTEXT KEY")


# ---------------------------------------- 声明外键表达式 ----------------------------------------


@dataclasses.dataclass(slots=True, frozen=True, eq=True)
class ASTForeignKeyExpression(ASTBase):
    """声明外键表达式"""

    constraint_name: str = dataclasses.field(kw_only=True)
    slave_columns: Tuple[str, ...] = dataclasses.field(kw_only=True)
    master_table_name: str = dataclasses.field(kw_only=True)
    master_columns: Tuple[str, ...] = dataclasses.field(kw_only=True)
    on_delete: Optional[str] = dataclasses.field(kw_only=True)
    on_update: Optional[str] = dataclasses.field(kw_only=True)

    def source(self, sql_type: SQLType = SQLType.DEFAULT) -> str:
        """返回语法节点的 SQL 源码"""
        slave_columns_str = ", ".join([f"{column}" for column in self.slave_columns])
        master_columns_str = ", ".join([f"{column}" for column in self.master_columns])
        on_delete_str = f" ON DELETE {self.on_delete}" if self.on_delete is not None else ""
        on_update_str = f" ON UPDATE {self.on_delete}" if self.on_update is not None else ""
        return (f"CONSTRAINT {self.constraint_name} FOREIGN KEY ({slave_columns_str}) "
                f"REFERENCES {self.master_table_name} ({master_columns_str}){on_delete_str}{on_update_str}")


AliasColumnOrIndex = Union[ASTDefineColumnExpression, ASTIndexExpressionBase, ASTForeignKeyExpression]  # DDL 的字段或索引类型


# ---------------------------------------- CREATE TABLE 语句 ----------------------------------------


@dataclasses.dataclass(slots=True, frozen=True, eq=True)
class ASTCreateTableStatement(ASTStatementBase):
    # pylint: disable=R0902 忽略对象属性过多的问题

    """【DDL】CREATE TABLE 语句"""

    table_name: ASTTableNameExpression = dataclasses.field(kw_only=True)
    if_not_exists: bool = dataclasses.field(kw_only=True)
    columns: Optional[Tuple[ASTDefineColumnExpression, ...]] = dataclasses.field(kw_only=True)
    primary_key: Optional[ASTPrimaryIndexExpression] = dataclasses.field(kw_only=True)  # MySQL
    unique_key: Optional[Tuple[ASTUniqueIndexExpression, ...]] = dataclasses.field(kw_only=True)  # MySQL
    key: Optional[Tuple[ASTNormalIndexExpression, ...]] = dataclasses.field(kw_only=True)  # MySQL
    fulltext_key: Optional[Tuple[ASTFulltextIndexExpression, ...]] = dataclasses.field(kw_only=True)  # MySQL
    foreign_key: Tuple[ASTForeignKeyExpression, ...] = dataclasses.field(kw_only=True)  # MySQL
    partitioned_by: Tuple[ASTDefineColumnExpression, ...] = dataclasses.field(kw_only=True)  # Hive
    comment: Optional[str] = dataclasses.field(kw_only=True)  # MySQL
    engine: Optional[str] = dataclasses.field(kw_only=True)  # MySQL
    auto_increment: Optional[int] = dataclasses.field(kw_only=True)  # MySQL
    default_charset: Optional[str] = dataclasses.field(kw_only=True)  # MySQL
    collate: Optional[str] = dataclasses.field(kw_only=True)  # MySQL
    row_format: Optional[str] = dataclasses.field(kw_only=True)  # MySQL
    states_persistent: Optional[str] = dataclasses.field(kw_only=True)  # MySQL
    row_format_serde: Optional[str] = dataclasses.field(kw_only=True, default=None)  # Hive
    row_format_delimited_fields_terminated_by: Optional[str] = dataclasses.field(kw_only=True, default=None)  # Hive
    stored_as_inputformat: Optional[str] = dataclasses.field(kw_only=True, default=None)  # Hive
    stored_as_textfile: bool = dataclasses.field(kw_only=True, default=False)  # Hive
    outputformat: Optional[str] = dataclasses.field(kw_only=True, default=None)  # Hive
    location: Optional[str] = dataclasses.field(kw_only=True, default=None)  # Hive
    tblproperties: Optional[Tuple[ASTConfigStringExpression, ...]] = dataclasses.field(
        kw_only=True, default=None)  # Hive

    def set_table_name(self, table_name_expression: ASTTableNameExpression) -> "ASTCreateTableStatement":
        """设置表名并返回新对象"""
        params = self.get_params_dict()
        params["table_name"] = table_name_expression
        return ASTCreateTableStatement(**params)

    def change_type(self, hashmap: Dict[str, str], remove_param: bool = True):
        """更新每个字段的变量类型"""
        params = self.get_params_dict()
        new_columns = []
        for old_column in self.columns:
            column_params = old_column.get_params_dict()
            column_params["column_type"] = ASTColumnTypeExpression(
                name=hashmap[old_column.column_type.name.upper()],
                params=None if remove_param else old_column.column_type.params)
            new_columns.append(ASTDefineColumnExpression(**column_params))
        params["columns"] = new_columns
        return ASTCreateTableStatement(**params)

    def append_column(self, column: ASTDefineColumnExpression):
        """添加字段"""
        params = self.get_params_dict()
        params["columns"] += (column,)
        return ASTCreateTableStatement(**params)

    def append_partition_by_column(self, column: ASTDefineColumnExpression):
        """添加分区字段"""
        params = self.get_params_dict()
        params["partitioned_by"] += (column,)
        return ASTCreateTableStatement(**params)

    def source(self, sql_type: SQLType = SQLType.DEFAULT, n_indent: int = 2) -> str:
        """返回语法节点的 SQL 源码"""
        if sql_type == SQLType.MYSQL:
            return self._source_mysql(n_indent=n_indent)
        if sql_type == SQLType.HIVE:
            return self._source_hive(n_indent=n_indent)
        raise SqlParseError(f"暂不支持的数据类型: {sql_type}")

    def _source_mysql(self, n_indent: int):
        indentation = " " * n_indent  # 缩进字符串
        result = f"{self._title_str(SQLType.MYSQL)} (\n"
        columns_and_keys = []
        for column in self.columns:
            columns_and_keys.append(f"{indentation}{column.source(SQLType.MYSQL)}")
        if self.primary_key is not None:
            columns_and_keys.append(f"{indentation}{self.primary_key.source(SQLType.MYSQL)}")
        for unique_key in self.unique_key:
            columns_and_keys.append(f"{indentation}{unique_key.source(SQLType.MYSQL)}")
        for key in self.key:
            columns_and_keys.append(f"{indentation}{key.source(SQLType.MYSQL)}")
        for fulltext_key in self.fulltext_key:
            columns_and_keys.append(f"{indentation}{fulltext_key.source(SQLType.MYSQL)}")
        for foreign_key in self.foreign_key:
            columns_and_keys.append(f"{indentation}{foreign_key.source(SQLType.MYSQL)}")
        result += ",\n".join(columns_and_keys)
        result += "\n)"
        result += f" ENGINE={self.engine}" if self.engine is not None else ""
        result += f" AUTO_INCREMENT={self.auto_increment}" if self.auto_increment is not None else ""
        result += f" DEFAULT CHARSET={self.default_charset}" if self.default_charset is not None else ""
        result += f" COLLATE={self.collate}" if self.collate is not None else ""
        result += f" ROW_FORMAT={self.row_format}" if self.row_format is not None else ""
        result += f" STATS_PERSISTENT={self.states_persistent}" if self.states_persistent is not None else ""
        result += f" COMMENT={self.comment}" if self.comment is not None else ""
        return result

    def _source_hive(self, n_indent: int):
        indentation = " " * n_indent  # 缩进字符串
        result = f" {self._title_str(SQLType.HIVE)}(\n"
        columns_and_keys = []
        for column in self.columns:
            columns_and_keys.append(f"{indentation}{column.source(SQLType.HIVE)}")
        result += ",\n".join(columns_and_keys)
        result += "\n)"
        if self.comment is not None:
            result += f" COMMENT {self.comment}"
        if len(self.partitioned_by) > 0:
            partition_columns = []
            for column in self.partitioned_by:
                partition_columns.append(column.source(SQLType.HIVE))
            partition_str = ", ".join(partition_columns)
            result += f" PARTITIONED BY ({partition_str})"
        result += f" ROW FORMAT SERDE {self.row_format_serde}" if self.row_format_serde is not None else ""
        result += (f" ROW FORMAT DELIMITED FIELDS TERMINATED BY {self.row_format_delimited_fields_terminated_by}"
                   if self.row_format_delimited_fields_terminated_by is not None else "")
        result += (f" STORED AS INPUTFORMAT {self.stored_as_inputformat}"
                   if self.stored_as_inputformat is not None else "")
        result += " STORED AS TEXTFILE" if self.stored_as_textfile is True else ""
        result += f" OUTPUTFORMAT {self.outputformat}" if self.outputformat is not None else ""
        result += f" LOCATION {self.location}" if self.location is not None else ""
        if len(self.tblproperties) > 0:
            tblproperties_str = ", ".join([config.source(SQLType.HIVE) for config in self.tblproperties])
            result += f"TBLPROPERTIES ({tblproperties_str})"
        return result

    def _title_str(self, sql_type: SQLType) -> str:
        is_not_exists_str = " IF NOT EXISTS" if self.if_not_exists is True else ""
        return f"CREATE TABLE{is_not_exists_str} {self.table_name.source(sql_type)}"


@dataclasses.dataclass(slots=True, frozen=True, eq=True)
class ASTCreateTableAsStatement(ASTStatementBase):
    """CREATE TABLE ... AS ... 语句"""

    table_name: ASTTableNameExpression = dataclasses.field(kw_only=True)
    select_statement: ASTSelectStatement = dataclasses.field(kw_only=True)

    def source(self, sql_type: SQLType = SQLType.DEFAULT) -> str:
        """返回语法节点的 SQL 源码"""
        return f"CREATE TABLE {self.table_name.source(sql_type)} AS {self.select_statement.source(sql_type)}"


@dataclasses.dataclass(slots=True, frozen=True, eq=True)
class ASTDropTableStatement(ASTStatementBase):
    """DROP TABLE 语句"""

    if_exists: bool = dataclasses.field(kw_only=True, default=False)  # 是否包含 IF EXISTS 关键字
    table_name: ASTTableNameExpression = dataclasses.field(kw_only=True)  # 表名

    def source(self, sql_type: SQLType = SQLType.DEFAULT) -> str:
        """返回语法节点的 SQL 源码"""
        if_exists_str = "IF EXISTS " if self.if_exists is True else ""
        return f"DROP TABLE {if_exists_str}{self.table_name.source(sql_type)}"


@dataclasses.dataclass(slots=True, frozen=True, eq=True)
class ASTSetStatement(ASTStatementBase):
    """SET 语句"""

    config: ASTConfigStringExpression = dataclasses.field(kw_only=True)

    def source(self, sql_type: SQLType = SQLType.DEFAULT) -> str:
        """返回语法节点的 SQL 源码"""
        return f"SET {self.config.source(sql_type)}"


@dataclasses.dataclass(slots=True, frozen=True, eq=True)
class ASTAnalyzeTableStatement(ASTStatementBase):
    """ANALYZE TABLE 语句"""

    table_name: ASTTableNameExpression = dataclasses.field(kw_only=True)
    partition: Optional[ASTPartitionExpression] = dataclasses.field(kw_only=True, default=None)
    for_columns: bool = dataclasses.field(kw_only=True, default=False)  # [Hive]
    cache_metadata: bool = dataclasses.field(kw_only=True, default=False)  # [Hive]
    noscan: bool = dataclasses.field(kw_only=True, default=False)  # [Hive]

    def source(self, sql_type: SQLType = SQLType.DEFAULT) -> str:
        """返回语法节点的 SQL 源码"""
        if sql_type == SQLType.HIVE:
            partition_str = f"{self.partition.source(sql_type)} " if self.partition is not None else ""
            for_columns_str = " FOR COLUMNS" if self.for_columns else ""
            cache_metadata_str = " CACHE METADATA" if self.cache_metadata else ""
            noscan_str = " NOSCAN" if self.noscan else ""
            return (f"ANALYZE TABLE {self.table_name.source(sql_type)} {partition_str} "
                    f"COMPUTE STATISTICS{for_columns_str}{cache_metadata_str}{noscan_str}")
        if sql_type == SQLType.MYSQL:
            return f"ANALYZE TABLE {self.table_name.source(sql_type)}"
        raise NotSupportError(f"ANALYZE TABLE 语句不支持数据类型: {sql_type}")


@dataclasses.dataclass(slots=True, frozen=True, eq=True)
class ASTAlterExpressionBase(ASTBase, abc.ABC):
    """ALTER TABLE 更新语句的抽象基类"""


@dataclasses.dataclass(slots=True, frozen=True, eq=True)
class ASTAlterAddPartitionExpression(ASTAlterExpressionBase):
    """ALTER TABLE 语句的 ADD PARTITION 子句"""

    if_not_exists: bool = dataclasses.field(kw_only=True)
    partition: ASTPartitionExpression = dataclasses.field(kw_only=True)

    def source(self, sql_type: SQLType = SQLType.DEFAULT) -> str:
        """返回语法节点的 SQL 源码"""
        if_exists_str = " IF NOT EXISTS" if self.if_not_exists else ""
        return f"DROP{if_exists_str} {self.partition.source(sql_type)}"


@dataclasses.dataclass(slots=True, frozen=True, eq=True)
class ASTAlterAddExpression(ASTAlterExpressionBase):
    """ALTER TABLE 语句的 ADD 子句"""

    expression: AliasColumnOrIndex = dataclasses.field(kw_only=True)

    def source(self, sql_type: SQLType = SQLType.DEFAULT) -> str:
        """返回语法节点的 SQL 源码"""
        return f"ADD {self.expression.source(sql_type)}"


@dataclasses.dataclass(slots=True, frozen=True, eq=True)
class ASTAlterModifyExpression(ASTAlterExpressionBase):
    """ALTER TABLE 语句的 MODIFY 子句"""

    expression: AliasColumnOrIndex = dataclasses.field(kw_only=True)

    def source(self, sql_type: SQLType = SQLType.DEFAULT) -> str:
        """返回语法节点的 SQL 源码"""
        return f"MODIFY {self.expression.source(sql_type)}"


@dataclasses.dataclass(slots=True, frozen=True, eq=True)
class ASTAlterChangeExpression(ASTAlterExpressionBase):
    """ALTER TABLE 语句的 CHANGE 子句"""

    from_column_name: str = dataclasses.field(kw_only=True)
    to_expression: AliasColumnOrIndex = dataclasses.field(kw_only=True)

    def source(self, sql_type: SQLType = SQLType.DEFAULT) -> str:
        """返回语法节点的 SQL 源码"""
        return f"CHANGE {self.from_column_name} {self.to_expression.source(sql_type)}"


@dataclasses.dataclass(slots=True, frozen=True, eq=True)
class ASTAlterRenameColumnExpression(ASTAlterExpressionBase):
    """ALTER TABLE 语句的 RENAME COLUMN 子句"""

    from_column_name: str = dataclasses.field(kw_only=True)
    to_column_name: str = dataclasses.field(kw_only=True)

    def source(self, sql_type: SQLType = SQLType.DEFAULT) -> str:
        """返回语法节点的 SQL 源码"""
        return f"RENAME COLUMN {self.from_column_name} TO {self.to_column_name}"


@dataclasses.dataclass(slots=True, frozen=True, eq=True)
class ASTAlterDropColumnExpression(ASTAlterExpressionBase):
    """ALTER TABLE 语句的 DROP COLUMN 子句"""

    column_name: str = dataclasses.field(kw_only=True)

    def source(self, sql_type: SQLType = SQLType.DEFAULT) -> str:
        """返回语法节点的 SQL 源码"""
        return f"DROP COLUMN {self.column_name}"


@dataclasses.dataclass(slots=True, frozen=True, eq=True)
class ASTAlterDropPartitionExpression(ASTAlterExpressionBase):
    """ALTER TABLE 语句的 DROP PARTITION 子句"""

    if_exists: bool = dataclasses.field(kw_only=True)
    partition: ASTPartitionExpression = dataclasses.field(kw_only=True)

    def source(self, sql_type: SQLType = SQLType.DEFAULT) -> str:
        """返回语法节点的 SQL 源码"""
        if_exists_str = " IF EXISTS" if self.if_exists else ""
        return f"DROP{if_exists_str} {self.partition.source(sql_type)}"


@dataclasses.dataclass(slots=True, frozen=True, eq=True)
class ASTAlterTableStatement(ASTStatementBase):
    """ALTER TABLE 语句"""

    table_name: ASTTableNameExpression = dataclasses.field(kw_only=True)
    expressions: Tuple[ASTAlterExpressionBase, ...] = dataclasses.field(kw_only=True)

    def source(self, sql_type: SQLType = SQLType.DEFAULT) -> str:
        """返回语法节点的 SQL 源码"""
        expressions_str = ",\n".join(expression.source(sql_type) for expression in self.expressions)
        return f"ALTER TABLE {self.table_name.source(sql_type)} \n{expressions_str}"


@dataclasses.dataclass(slots=True, frozen=True, eq=True)
class ASTMsckRepairTableStatement(ASTStatementBase):
    """MSCK REPAIR TABLE 语句：扫描 HDFS 上的文件并更新元数据的分区信息"""

    table_name: ASTTableNameExpression = dataclasses.field(kw_only=True)

    def source(self, sql_type: SQLType = SQLType.DEFAULT) -> str:
        """返回语法节点的 SQL 源码"""
        return f"MSCK REPAIR TABLE {self.table_name.source(sql_type)}"


@dataclasses.dataclass(slots=True, frozen=True, eq=True)
class ASTUseStatement(ASTStatementBase):
    """USE 语句"""

    schema_name: str = dataclasses.field(kw_only=True)

    def source(self, sql_type: SQLType = SQLType.DEFAULT) -> str:
        """返回语法节点的 SQL 源码"""
        return f"USE {self.schema_name}"


@dataclasses.dataclass(slots=True, frozen=True, eq=True)
class ASTTruncateTable(ASTStatementBase):
    """TRUNCATE TABLE 语句"""

    table_name: ASTTableNameExpression = dataclasses.field(kw_only=True)

    def source(self, sql_type: SQLType = SQLType.DEFAULT) -> str:
        """返回语法节点的 SQL 源码"""
        return f"TRUNCATE TABLE {self.table_name.source(sql_type)}"


@dataclasses.dataclass(slots=True, frozen=True, eq=True)
class ASTUpdateSetColumn(ASTBase):
    """UPDATE 语句的 SET 子句中的元素"""

    column_name: str = dataclasses.field(kw_only=True)
    column_value: ASTLogicalOrExpression = dataclasses.field(kw_only=True)

    def source(self, sql_type: SQLType = SQLType.DEFAULT) -> str:
        """返回语法节点的 SQL 源码"""
        return f"{self.column_name} = {self.column_value.source(sql_type)}"


@dataclasses.dataclass(slots=True, frozen=True, eq=True)
class ASTUpdateSetClause(ASTBase):
    """UPDATE 语句的 SET 子句"""

    columns: Tuple[ASTUpdateSetColumn, ...] = dataclasses.field(kw_only=True)

    def source(self, sql_type: SQLType = SQLType.DEFAULT) -> str:
        """返回语法节点的 SQL 源码"""
        columns_str = ", ".join(column.source(sql_type) for column in self.columns)
        return f"SET {columns_str}"


@dataclasses.dataclass(slots=True, frozen=True, eq=True)
class ASTUpdateStatement(ASTStatementHasWithClauseBase):
    """UPDATE 语句"""

    table_name: ASTTableNameExpression = dataclasses.field(kw_only=True)
    set_clause: ASTUpdateSetClause = dataclasses.field(kw_only=True)
    where_clause: Optional[ASTWhereClause] = dataclasses.field(kw_only=True)
    order_by_clause: Optional[ASTOrderByClause] = dataclasses.field(kw_only=True)
    limit_clause: Optional[ASTLimitClause] = dataclasses.field(kw_only=True)

    def source(self, sql_type: SQLType = SQLType.DEFAULT) -> str:
        """返回语法节点的 SQL 源码"""
        with_clause_str = self.with_clause.source(sql_type) + "\n\n" if not self.with_clause.is_empty() else ""
        result = f"{with_clause_str}UPDATE {self.table_name.source(sql_type)} {self.set_clause.source(sql_type)}"
        if self.where_clause is not None:
            result += f" {self.where_clause.source(sql_type)}"
        if self.order_by_clause is not None:
            result += f" {self.order_by_clause.source(sql_type)}"
        if self.limit_clause is not None:
            result += f" {self.limit_clause.source(sql_type)}"
        return result


@dataclasses.dataclass(slots=True, frozen=True, eq=True)
class ASTDeleteStatement(ASTStatementBase):
    """DELETE 语句"""

    table_name: ASTTableNameExpression = dataclasses.field(kw_only=True)
    where_clause: Optional[ASTWhereClause] = dataclasses.field(kw_only=True)
    order_by_clause: Optional[ASTOrderByClause] = dataclasses.field(kw_only=True)
    limit_clause: Optional[ASTLimitClause] = dataclasses.field(kw_only=True)

    def source(self, sql_type: SQLType = SQLType.DEFAULT) -> str:
        """返回语法节点的 SQL 源码"""
        result = f"DELETE FROM {self.table_name.source(sql_type)} "
        if self.where_clause is not None:
            result += f" {self.where_clause.source(sql_type)}"
        if self.order_by_clause is not None:
            result += f" {self.order_by_clause.source(sql_type)}"
        if self.limit_clause is not None:
            result += f" {self.limit_clause.source(sql_type)}"
        return result


@dataclasses.dataclass(slots=True, frozen=True, eq=True)
class ASTShowDatabasesStatement(ASTStatementBase):
    """SHOW DATABASES 语句"""

    def source(self, sql_type: SQLType = SQLType.DEFAULT) -> str:
        """返回语法节点的 SQL 源码"""
        return "SHOW DATABASES"


@dataclasses.dataclass(slots=True, frozen=True, eq=True)
class ASTShowTablesStatement(ASTStatementBase):
    """SHOW TABLES 语句"""

    def source(self, sql_type: SQLType = SQLType.DEFAULT) -> str:
        """返回语法节点的 SQL 源码"""
        return "SHOW TABLES"


@dataclasses.dataclass(slots=True, frozen=True, eq=True)
class ASTShowColumnsStatement(ASTStatementBase):
    """SHOW COLUMNS 语句"""

    from_clause: ASTFromClause = dataclasses.field(kw_only=True)
    where_clause: Optional[ASTWhereClause] = dataclasses.field(kw_only=True)

    def source(self, sql_type: SQLType = SQLType.DEFAULT) -> str:
        """返回语法节点的 SQL 源码"""
        where_clause_str = f" {self.where_clause.source(sql_type)}" if self.where_clause is not None else ""
        return f"SHOW COLUMNS {self.from_clause.source(sql_type)}{where_clause_str}"
