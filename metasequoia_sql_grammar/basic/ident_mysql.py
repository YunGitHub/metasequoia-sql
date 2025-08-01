"""
MySQL 特有的标识符语义组
"""

import metasequoia_parser as ms_parser

from metasequoia_sql import ast
from metasequoia_sql.terminal import SqlTerminalType as TType

__all__ = [
    "MYSQL_IDENT_KEYWORDS_UNAMBIGUOUS",
    "MYSQL_IDENT_KEYWORDS_AMBIGUOUS_1_ROLES_AND_LABELS",
    "MYSQL_IDENT_KEYWORDS_AMBIGUOUS_2_LABELS",
    "MYSQL_IDENT_KEYWORDS_AMBIGUOUS_3_ROLES",
    "MYSQL_IDENT_KEYWORDS_AMBIGUOUS_4_SYSTEM_VARIABLES",
    "MYSQL_IDENT_KEYWORD",
    "MYSQL_LABEL_KEYWORD",
    "MYSQL_ROLE_KEYWORD",
    "MYSQL_VARIABLE_KEYWORD",
    "MYSQL_IDENT",
    "MYSQL_LABEL_IDENT",
    "MYSQL_ROLE_IDENT",
    "MYSQL_VARIABLE_IDENT",
]

# [MySQL | Terminal Set] 非保留关键字，可以在任何位置用作未见引号的标识符，而不会引入语法冲突
MYSQL_TERMINAL_SET_KEYWORDS_UNAMBIGUOUS = {
    TType.KEYWORD_ACTION,
    TType.KEYWORD_ACCOUNT,
    TType.KEYWORD_ACTIVE,
    TType.KEYWORD_ADDDATE,
    TType.KEYWORD_ADMIN,
    TType.KEYWORD_AFTER,
    TType.KEYWORD_AGAINST,
    TType.KEYWORD_AGGREGATE,
    TType.KEYWORD_ALGORITHM,
    TType.KEYWORD_ALWAYS,
    TType.KEYWORD_ANY,
    TType.KEYWORD_ARRAY,
    TType.KEYWORD_AT,
    TType.KEYWORD_ATTRIBUTE,
    TType.KEYWORD_AUTHENTICATION,
    TType.KEYWORD_AUTOEXTEND_SIZE,
    TType.KEYWORD_AUTO_INC,
    TType.KEYWORD_AVG_ROW_LENGTH,
    TType.KEYWORD_AVG,
    TType.KEYWORD_BACKUP,
    TType.KEYWORD_BINLOG,
    TType.KEYWORD_BIT,
    TType.KEYWORD_BLOCK,
    TType.KEYWORD_BOOLEAN,
    TType.KEYWORD_BOOL,
    TType.KEYWORD_BTREE,
    TType.KEYWORD_BUCKETS,
    TType.KEYWORD_BULK,
    TType.KEYWORD_CASCADED,
    TType.KEYWORD_CATALOG_NAME,
    TType.KEYWORD_CHAIN,
    TType.KEYWORD_CHALLENGE_RESPONSE,
    TType.KEYWORD_CHANGED,
    TType.KEYWORD_CHANNEL,
    TType.KEYWORD_CIPHER,
    TType.KEYWORD_CLASS_ORIGIN,
    TType.KEYWORD_CLIENT,
    TType.KEYWORD_CLOSE,
    TType.KEYWORD_COALESCE,
    TType.KEYWORD_CODE,
    TType.KEYWORD_COLLATION,
    TType.KEYWORD_COLUMNS,
    TType.KEYWORD_COLUMN_FORMAT,
    TType.KEYWORD_COLUMN_NAME,
    TType.KEYWORD_COMMITTED,
    TType.KEYWORD_COMPACT,
    TType.KEYWORD_COMPLETION,
    TType.KEYWORD_COMPONENT,
    TType.KEYWORD_COMPRESSED,
    TType.KEYWORD_COMPRESSION,
    TType.KEYWORD_CONCURRENT,
    TType.KEYWORD_CONNECTION,
    TType.KEYWORD_CONSISTENT,
    TType.KEYWORD_CONSTRAINT_CATALOG,
    TType.KEYWORD_CONSTRAINT_NAME,
    TType.KEYWORD_CONSTRAINT_SCHEMA,
    TType.KEYWORD_CONTEXT,
    TType.KEYWORD_CPU,
    TType.KEYWORD_CURRENT,
    TType.KEYWORD_CURSOR_NAME,
    TType.KEYWORD_DATAFILE,
    TType.KEYWORD_DATA,
    TType.KEYWORD_DATETIME,
    TType.KEYWORD_DATE,
    TType.KEYWORD_DAY,
    TType.KEYWORD_DEFAULT_AUTH,
    TType.KEYWORD_DEFINER,
    TType.KEYWORD_DEFINITION,
    TType.KEYWORD_DELAY_KEY_WRITE,
    TType.KEYWORD_DESCRIPTION,
    TType.KEYWORD_DIAGNOSTICS,
    TType.KEYWORD_DIRECTORY,
    TType.KEYWORD_DISABLE,
    TType.KEYWORD_DISCARD,
    TType.KEYWORD_DISK,
    TType.KEYWORD_DUMPFILE,
    TType.KEYWORD_DUPLICATE,
    TType.KEYWORD_DYNAMIC,
    TType.KEYWORD_ENABLE,
    TType.KEYWORD_ENCRYPTION,
    TType.KEYWORD_ENDS,
    TType.KEYWORD_ENFORCED,
    TType.KEYWORD_ENGINES,
    TType.KEYWORD_ENGINE,
    TType.KEYWORD_ENGINE_ATTRIBUTE,
    TType.KEYWORD_ENUM,
    TType.KEYWORD_ERRORS,
    TType.KEYWORD_ERROR,
    TType.KEYWORD_ESCAPE,
    TType.KEYWORD_EVENTS,
    TType.KEYWORD_EVERY,
    TType.KEYWORD_EXCHANGE,
    TType.KEYWORD_EXCLUDE,
    TType.KEYWORD_EXPANSION,
    TType.KEYWORD_EXPIRE,
    TType.KEYWORD_EXPORT,
    TType.KEYWORD_EXTENDED,
    TType.KEYWORD_EXTENT_SIZE,
    TType.KEYWORD_FACTOR,
    TType.KEYWORD_FAILED_LOGIN_ATTEMPTS,
    TType.KEYWORD_FAST,
    TType.KEYWORD_FAULTS,
    TType.KEYWORD_FILE_BLOCK_SIZE,
    TType.KEYWORD_FILTER,
    TType.KEYWORD_FINISH,
    TType.KEYWORD_FIRST,
    TType.KEYWORD_FIXED,
    TType.KEYWORD_FOLLOWING,
    TType.KEYWORD_FORMAT,
    TType.KEYWORD_FOUND,
    TType.KEYWORD_FULL,
    TType.KEYWORD_GENERAL,
    TType.KEYWORD_GENERATE,
    TType.KEYWORD_GEOMETRYCOLLECTION,
    TType.KEYWORD_GEOMETRY,
    TType.KEYWORD_GET_FORMAT,
    TType.KEYWORD_GET_MASTER_PUBLIC_KEY,
    TType.KEYWORD_GET_SOURCE_PUBLIC_KEY,
    TType.KEYWORD_GRANTS,
    TType.KEYWORD_GROUP_REPLICATION,
    TType.KEYWORD_GTIDS,
    TType.KEYWORD_GTID_ONLY,
    TType.KEYWORD_HASH,
    TType.KEYWORD_HISTOGRAM,
    TType.KEYWORD_HISTORY,
    TType.KEYWORD_HOSTS,
    TType.KEYWORD_HOST,
    TType.KEYWORD_HOUR,
    TType.KEYWORD_IDENTIFIED,
    TType.KEYWORD_IGNORE_SERVER_IDS,
    TType.KEYWORD_INACTIVE,
    TType.KEYWORD_INDEXES,
    TType.KEYWORD_INITIAL_SIZE,
    TType.KEYWORD_INITIAL,
    TType.KEYWORD_INITIATE,
    TType.KEYWORD_INSERT_METHOD,
    TType.KEYWORD_INSTANCE,
    TType.KEYWORD_INVISIBLE,
    TType.KEYWORD_INVOKER,
    TType.KEYWORD_IO,
    TType.KEYWORD_IPC,
    TType.KEYWORD_ISOLATION,
    TType.KEYWORD_ISSUER,
    TType.KEYWORD_JSON,
    TType.KEYWORD_JSON_VALUE,
    TType.KEYWORD_KEY_BLOCK_SIZE,
    TType.KEYWORD_KEYRING,
    TType.KEYWORD_LAST,
    TType.KEYWORD_LEAVES,
    TType.KEYWORD_LESS,
    TType.KEYWORD_LEVEL,
    TType.KEYWORD_LINESTRING,
    TType.KEYWORD_LIST,
    TType.KEYWORD_LOCKED,
    TType.KEYWORD_LOCKS,
    TType.KEYWORD_LOGFILE,
    TType.KEYWORD_LOGS,
    TType.KEYWORD_LOG,
    TType.KEYWORD_MASTER_AUTO_POSITION,
    TType.KEYWORD_MASTER_COMPRESSION_ALGORITHM,
    TType.KEYWORD_MASTER_CONNECT_RETRY,
    TType.KEYWORD_MASTER_DELAY,
    TType.KEYWORD_MASTER_HEARTBEAT_PERIOD,
    TType.KEYWORD_MASTER_HOST,
    TType.KEYWORD_NETWORK_NAMESPACE,
    TType.KEYWORD_MASTER_LOG_FILE,
    TType.KEYWORD_MASTER_LOG_POS,
    TType.KEYWORD_MASTER_PASSWORD,
    TType.KEYWORD_MASTER_PORT,
    TType.KEYWORD_MASTER_PUBLIC_KEY_PATH,
    TType.KEYWORD_MASTER_RETRY_COUNT,
    TType.KEYWORD_MASTER_SSL_CAPATH,
    TType.KEYWORD_MASTER_SSL_CA,
    TType.KEYWORD_MASTER_SSL_CERT,
    TType.KEYWORD_MASTER_SSL_CIPHER,
    TType.KEYWORD_MASTER_SSL_CRLPATH,
    TType.KEYWORD_MASTER_SSL_CRL,
    TType.KEYWORD_MASTER_SSL_KEY,
    TType.KEYWORD_MASTER_SSL,
    TType.KEYWORD_MASTER,
    TType.KEYWORD_MASTER_TLS_CIPHERSUITES,
    TType.KEYWORD_MASTER_TLS_VERSION,
    TType.KEYWORD_MASTER_USER,
    TType.KEYWORD_MASTER_ZSTD_COMPRESSION_LEVEL,
    TType.KEYWORD_MAX_CONNECTIONS_PER_HOUR,
    TType.KEYWORD_MAX_QUERIES_PER_HOUR,
    TType.KEYWORD_MAX_ROWS,
    TType.KEYWORD_MAX_SIZE,
    TType.KEYWORD_MAX_UPDATES_PER_HOUR,
    TType.KEYWORD_MAX_USER_CONNECTIONS,
    TType.KEYWORD_MEDIUM,
    TType.KEYWORD_MEMBER,
    TType.KEYWORD_MEMORY,
    TType.KEYWORD_MERGE,
    TType.KEYWORD_MESSAGE_TEXT,
    TType.KEYWORD_MICROSECOND,
    TType.KEYWORD_MIGRATE,
    TType.KEYWORD_MINUTE,
    TType.KEYWORD_MIN_ROWS,
    TType.KEYWORD_MODE,
    TType.KEYWORD_MODIFY,
    TType.KEYWORD_MONTH,
    TType.KEYWORD_MULTILINESTRING,
    TType.KEYWORD_MULTIPOINT,
    TType.KEYWORD_MULTIPOLYGON,
    TType.KEYWORD_MUTEX,
    TType.KEYWORD_MYSQL_ERRNO,
    TType.KEYWORD_NAMES,
    TType.KEYWORD_NAME,
    TType.KEYWORD_NATIONAL,
    TType.KEYWORD_NCHAR,
    TType.KEYWORD_NDBCLUSTER,
    TType.KEYWORD_NESTED,
    TType.KEYWORD_NEVER,
    TType.KEYWORD_NEW,
    TType.KEYWORD_NEXT,
    TType.KEYWORD_NODEGROUP,
    TType.KEYWORD_NOWAIT,
    TType.KEYWORD_NO_WAIT,
    TType.KEYWORD_NULLS,
    TType.KEYWORD_NUMBER,
    TType.KEYWORD_NVARCHAR,
    TType.KEYWORD_OFF,
    TType.KEYWORD_OFFSET,
    TType.KEYWORD_OJ,
    TType.KEYWORD_OLD,
    TType.KEYWORD_ONE,
    TType.KEYWORD_ONLY,
    TType.KEYWORD_OPEN,
    TType.KEYWORD_OPTIONAL,
    TType.KEYWORD_OPTIONS,
    TType.KEYWORD_ORDINALITY,
    TType.KEYWORD_ORGANIZATION,
    TType.KEYWORD_OTHERS,
    TType.KEYWORD_OWNER,
    TType.KEYWORD_PACK_KEYS,
    TType.KEYWORD_PAGE,
    TType.KEYWORD_PARSER,
    TType.KEYWORD_PARSE_TREE,
    TType.KEYWORD_PARTIAL,
    TType.KEYWORD_PARTITIONING,
    TType.KEYWORD_PARTITIONS,
    TType.KEYWORD_PASSWORD,
    TType.KEYWORD_PASSWORD_LOCK_TIME,
    TType.KEYWORD_PATH,
    TType.KEYWORD_PHASE,
    TType.KEYWORD_PLUGINS,
    TType.KEYWORD_PLUGIN_DIR,
    TType.KEYWORD_PLUGIN,
    TType.KEYWORD_POINT,
    TType.KEYWORD_POLYGON,
    TType.KEYWORD_PORT,
    TType.KEYWORD_PRECEDING,
    TType.KEYWORD_PRESERVE,
    TType.KEYWORD_PREV,
    TType.KEYWORD_PRIVILEGES,
    TType.KEYWORD_PRIVILEGE_CHECKS_USER,
    TType.KEYWORD_PROCESSLIST,
    TType.KEYWORD_PROFILES,
    TType.KEYWORD_PROFILE,
    TType.KEYWORD_QUARTER,
    TType.KEYWORD_QUERY,
    TType.KEYWORD_QUICK,
    TType.KEYWORD_RANDOM,
    TType.KEYWORD_READ_ONLY,
    TType.KEYWORD_REBUILD,
    TType.KEYWORD_RECOVER,
    TType.KEYWORD_REDO_BUFFER_SIZE,
    TType.KEYWORD_REDUNDANT,
    TType.KEYWORD_REFERENCE,
    TType.KEYWORD_REGISTRATION,
    TType.KEYWORD_RELAY,
    TType.KEYWORD_RELAYLOG,
    TType.KEYWORD_RELAY_LOG_FILE,
    TType.KEYWORD_RELAY_LOG_POS,
    TType.KEYWORD_RELAY_THREAD,
    TType.KEYWORD_REMOVE,
    TType.KEYWORD_ASSIGN_GTIDS_TO_ANONYMOUS_TRANSACTIONS,
    TType.KEYWORD_REORGANIZE,
    TType.KEYWORD_REPEATABLE,
    TType.KEYWORD_REPLICAS,
    TType.KEYWORD_REPLICATE_DO_DB,
    TType.KEYWORD_REPLICATE_DO_TABLE,
    TType.KEYWORD_REPLICATE_IGNORE_DB,
    TType.KEYWORD_REPLICATE_IGNORE_TABLE,
    TType.KEYWORD_REPLICATE_REWRITE_DB,
    TType.KEYWORD_REPLICATE_WILD_DO_TABLE,
    TType.KEYWORD_REPLICATE_WILD_IGNORE_TABLE,
    TType.KEYWORD_REPLICA,
    TType.KEYWORD_REQUIRE_ROW_FORMAT,
    TType.KEYWORD_REQUIRE_TABLE_PRIMARY_KEY_CHECK,
    # TType.KEYWORD_RESOURCES,  TODO 待放出
    TType.KEYWORD_RESPECT,
    TType.KEYWORD_RESTORE,
    TType.KEYWORD_RESUME,
    TType.KEYWORD_RETAIN,
    TType.KEYWORD_RETURNED_SQLSTATE,
    TType.KEYWORD_RETURNING,
    TType.KEYWORD_RETURNS,
    TType.KEYWORD_REUSE,
    TType.KEYWORD_REVERSE,
    TType.KEYWORD_ROLE,
    TType.KEYWORD_ROLLUP,
    TType.KEYWORD_ROTATE,
    TType.KEYWORD_ROUTINE,
    TType.KEYWORD_ROW_COUNT,
    TType.KEYWORD_ROW_FORMAT,
    TType.KEYWORD_RTREE,
    TType.KEYWORD_S3,
    TType.KEYWORD_SCHEDULE,
    TType.KEYWORD_SCHEMA_NAME,
    TType.KEYWORD_SECONDARY_ENGINE,
    TType.KEYWORD_SECONDARY_ENGINE_ATTRIBUTE,
    TType.KEYWORD_SECONDARY_LOAD,
    TType.KEYWORD_SECONDARY,
    TType.KEYWORD_SECONDARY_UNLOAD,
    TType.KEYWORD_SECOND,
    TType.KEYWORD_SECURITY,
    TType.KEYWORD_SERIALIZABLE,
    TType.KEYWORD_SERIAL,
    TType.KEYWORD_SERVER,
    TType.KEYWORD_SHARE,
    TType.KEYWORD_SIMPLE,
    TType.KEYWORD_SKIP,
    TType.KEYWORD_SLOW,
    TType.KEYWORD_SNAPSHOT,
    TType.KEYWORD_SOCKET,
    TType.KEYWORD_SONAME,
    TType.KEYWORD_SOUNDS,
    TType.KEYWORD_SOURCE_AUTO_POSITION,
    TType.KEYWORD_SOURCE_BIND,
    TType.KEYWORD_SOURCE_COMPRESSION_ALGORITHM,
    TType.KEYWORD_SOURCE_CONNECTION_AUTO_FAILOVER,
    TType.KEYWORD_SOURCE_CONNECT_RETRY,
    TType.KEYWORD_SOURCE_DELAY,
    TType.KEYWORD_SOURCE_HEARTBEAT_PERIOD,
    TType.KEYWORD_SOURCE_HOST,
    TType.KEYWORD_SOURCE_LOG_FILE,
    TType.KEYWORD_SOURCE_LOG_POS,
    TType.KEYWORD_SOURCE_PASSWORD,
    TType.KEYWORD_SOURCE_PORT,
    TType.KEYWORD_SOURCE_PUBLIC_KEY_PATH,
    TType.KEYWORD_SOURCE_RETRY_COUNT,
    TType.KEYWORD_SOURCE_SSL_CAPATH,
    TType.KEYWORD_SOURCE_SSL_CA,
    TType.KEYWORD_SOURCE_SSL_CERT,
    TType.KEYWORD_SOURCE_SSL_CIPHER,
    TType.KEYWORD_SOURCE_SSL_CRLPATH,
    TType.KEYWORD_SOURCE_SSL_CRL,
    TType.KEYWORD_SOURCE_SSL_KEY,
    TType.KEYWORD_SOURCE_SSL,
    TType.KEYWORD_SOURCE_SSL_VERIFY_SERVER_CERT,
    TType.KEYWORD_SOURCE,
    TType.KEYWORD_SOURCE_TLS_CIPHERSUITES,
    TType.KEYWORD_SOURCE_TLS_VERSION,
    TType.KEYWORD_SOURCE_USER,
    TType.KEYWORD_SOURCE_ZSTD_COMPRESSION_LEVEL,
    TType.KEYWORD_SQL_AFTER_GTIDS,
    TType.KEYWORD_SQL_AFTER_MTS_GAPS,
    TType.KEYWORD_SQL_BEFORE_GTIDS,
    TType.KEYWORD_SQL_BUFFER_RESULT,
    TType.KEYWORD_SQL_NO_CACHE,
    TType.KEYWORD_SQL_THREAD,
    TType.KEYWORD_SRID,
    TType.KEYWORD_STACKED,
    TType.KEYWORD_STARTS,
    TType.KEYWORD_STATS_AUTO_RECALC,
    TType.KEYWORD_STATS_PERSISTENT,
    TType.KEYWORD_STATS_SAMPLE_PAGES,
    TType.KEYWORD_STATUS,
    TType.KEYWORD_STORAGE,
    TType.KEYWORD_STREAM,
    TType.KEYWORD_STRING,
    TType.KEYWORD_ST_COLLECT,
    TType.KEYWORD_SUBCLASS_ORIGIN,
    TType.KEYWORD_SUBDATE,
    TType.KEYWORD_SUBJECT,
    TType.KEYWORD_SUBPARTITIONS,
    TType.KEYWORD_SUBPARTITION,
    TType.KEYWORD_SUSPEND,
    TType.KEYWORD_SWAPS,
    TType.KEYWORD_SWITCHES,
    TType.KEYWORD_TABLES,
    TType.KEYWORD_TABLESPACE,
    TType.KEYWORD_TABLE_CHECKSUM,
    TType.KEYWORD_TABLE_NAME,
    TType.KEYWORD_TEMPORARY,
    TType.KEYWORD_TEMPTABLE,
    TType.KEYWORD_TEXT,
    TType.KEYWORD_THAN,
    TType.KEYWORD_THREAD_PRIORITY,
    TType.KEYWORD_TIES,
    TType.KEYWORD_TIMESTAMP_ADD,
    TType.KEYWORD_TIMESTAMP_DIFF,
    TType.KEYWORD_TIMESTAMP,
    TType.KEYWORD_TIME,
    TType.KEYWORD_TLS,
    TType.KEYWORD_TRANSACTION,
    TType.KEYWORD_TRIGGERS,
    TType.KEYWORD_TYPES,
    TType.KEYWORD_TYPE,
    TType.KEYWORD_UNBOUNDED,
    TType.KEYWORD_UNCOMMITTED,
    TType.KEYWORD_UNDEFINED,
    TType.KEYWORD_UNDOFILE,
    TType.KEYWORD_UNDO_BUFFER_SIZE,
    TType.KEYWORD_UNKNOWN,
    TType.KEYWORD_UNREGISTER,
    TType.KEYWORD_UNTIL,
    TType.KEYWORD_UPGRADE,
    TType.KEYWORD_URL,
    TType.KEYWORD_USER,
    TType.KEYWORD_USE_FRM,
    TType.KEYWORD_VALIDATION,
    TType.KEYWORD_VALUE,
    TType.KEYWORD_VARIABLES,
    TType.KEYWORD_VCPU,
    TType.KEYWORD_VIEW,
    TType.KEYWORD_VISIBLE,
    TType.KEYWORD_WAIT,
    TType.KEYWORD_WARNINGS,
    TType.KEYWORD_WEEK,
    TType.KEYWORD_WEIGHT_STRING,
    TType.KEYWORD_WITHOUT,
    TType.KEYWORD_WORK,
    TType.KEYWORD_WRAPPER,
    TType.KEYWORD_X509,
    TType.KEYWORD_XID,
    TType.KEYWORD_XML,
    TType.KEYWORD_YEAR,
    TType.KEYWORD_ZONE
}

# [MySQL | Terminal Set] 需要使用 KEYWORD_USED_AS_IDENT 优先级的终结符类型的结合
MYSQL_TERMINAL_SET_KEYWORD_USED_AS_IDENT = {
    TType.KEYWORD_BIT,
    TType.KEYWORD_DATE,
    TType.KEYWORD_NAMES,
    TType.KEYWORD_PASSWORD,
    TType.KEYWORD_TIMESTAMP,
    TType.KEYWORD_TIME,
}

# [MySQL | Grammar Group] 非保留关键字，可以在任何位置用作未见引号的标识符，而不会引入语法冲突
# 对应 MySQL 语义组：ident_keywords_unambiguous
MYSQL_IDENT_KEYWORDS_UNAMBIGUOUS = ms_parser.create_group(
    name="ident_keywords_unambiguous",
    rules=[
        ms_parser.create_rule(
            symbols=[terminal_type],
            action=lambda x: ast.Ident(x[0]),
            sr_priority_as=(TType.KEYWORD_USED_AS_IDENT
                            if terminal_type in MYSQL_TERMINAL_SET_KEYWORD_USED_AS_IDENT
                            else None)
        )
        for terminal_type in MYSQL_TERMINAL_SET_KEYWORDS_UNAMBIGUOUS
    ]
)

# [MySQL | Terminal Set] 非保留关键字，不能用作角色名称（role name）和存储过程标签名称（SP label name）
MYSQL_TERMINAL_SET_KEYWORDS_AMBIGUOUS_1_ROLES_AND_LABELS = {
    TType.KEYWORD_EXECUTE,
    TType.KEYWORD_RESTART,
    TType.KEYWORD_SHUTDOWN
}

# [MySQL | Grammar Group] 非保留关键字，不能用作角色名称（role name）和存储过程标签名称（SP label name）
# 对应 MySQL 语义组：ident_keywords_ambiguous_1_roles_and_labels
MYSQL_IDENT_KEYWORDS_AMBIGUOUS_1_ROLES_AND_LABELS = ms_parser.create_group(
    name="ident_keywords_ambiguous_1_roles_and_labels",
    rules=[
        ms_parser.create_rule(
            symbols=[terminal_type],
            action=lambda x: ast.Ident(x[0])
        )
        for terminal_type in MYSQL_TERMINAL_SET_KEYWORDS_AMBIGUOUS_1_ROLES_AND_LABELS
    ]
)

# [MySQL | Terminal Set] 非保留关键字，不能用作存储过程标签名称（SP label name）
MYSQL_TERMINAL_SET_KEYWORDS_AMBIGUOUS_2_LABELS = {
    TType.KEYWORD_ASCII,
    TType.KEYWORD_BEGIN,
    TType.KEYWORD_BYTE,
    TType.KEYWORD_CACHE,
    TType.KEYWORD_CHARSET,
    TType.KEYWORD_CHECKSUM,
    TType.KEYWORD_CLONE,
    TType.KEYWORD_COMMENT,
    TType.KEYWORD_COMMIT,
    TType.KEYWORD_CONTAINS,
    TType.KEYWORD_DEALLOCATE,
    TType.KEYWORD_DO,
    TType.KEYWORD_END,
    TType.KEYWORD_FLUSH,
    TType.KEYWORD_FOLLOWS,
    TType.KEYWORD_HANDLER,
    TType.KEYWORD_HELP,
    TType.KEYWORD_IMPORT,
    TType.KEYWORD_INSTALL,
    TType.KEYWORD_LANGUAGE,
    TType.KEYWORD_NO,
    TType.KEYWORD_PRECEDES,
    TType.KEYWORD_PREPARE,
    TType.KEYWORD_REPAIR,
    TType.KEYWORD_RESET,
    TType.KEYWORD_ROLLBACK,
    TType.KEYWORD_SAVEPOINT,
    TType.KEYWORD_SIGNED,
    TType.KEYWORD_SLAVE,
    TType.KEYWORD_START,
    TType.KEYWORD_STOP,
    TType.KEYWORD_TRUNCATE,
    TType.KEYWORD_UNICODE,
    TType.KEYWORD_UNINSTALL,
    TType.KEYWORD_XA
}

# [MySQL | Grammar Group] 非保留关键字，不能用作存储过程标签名称（SP label name）
# 对应 MySQL 语义组：ident_keywords_ambiguous_2_labels
MYSQL_IDENT_KEYWORDS_AMBIGUOUS_2_LABELS = ms_parser.create_group(
    name="ident_keywords_ambiguous_2_labels",
    rules=[
        ms_parser.create_rule(
            symbols=[terminal_type],
            action=lambda x: ast.Ident(x[0])
        )
        for terminal_type in MYSQL_TERMINAL_SET_KEYWORDS_AMBIGUOUS_2_LABELS
    ]
)

# [MySQL | Terminal Set] 非保留关键字，不能用作角色名称（role name）
MYSQL_TERMINAL_SET_KEYWORDS_AMBIGUOUS_3_ROLES = {
    TType.KEYWORD_EVENT,
    TType.KEYWORD_FILE,
    TType.KEYWORD_NONE,
    TType.KEYWORD_PROCESS,
    TType.KEYWORD_PROXY,
    TType.KEYWORD_RELOAD,
    TType.KEYWORD_REPLICATION,
    TType.KEYWORD_RESOURCE,
    TType.KEYWORD_SUPER,
}

# [MySQL | Grammar Group] 非保留关键字，不能用作角色名称（role name）
# 对应 MySQL 语义组：ident_keywords_ambiguous_3_roles
MYSQL_IDENT_KEYWORDS_AMBIGUOUS_3_ROLES = ms_parser.create_group(
    name="ident_keywords_ambiguous_3_roles",
    rules=[
        ms_parser.create_rule(
            symbols=[terminal_type],
            action=lambda x: ast.Ident(x[0])
        )
        for terminal_type in MYSQL_TERMINAL_SET_KEYWORDS_AMBIGUOUS_3_ROLES
    ]
)

# [MySQL | Terminal Set] 非保留关键字，不能用作 SET 语句中赋值操作左侧的变量名以及变量前缀
MYSQL_TERMINAL_SET_KEYWORDS_AMBIGUOUS_4_SYSTEM_VARIABLES = {
    TType.KEYWORD_GLOBAL,
    TType.KEYWORD_LOCAL,
    TType.KEYWORD_PERSIST,
    TType.KEYWORD_PERSIST_ONLY,
    TType.KEYWORD_SESSION
}

# [MySQL | Grammar Group] 非保留关键字，不能用作 SET 语句中赋值操作左侧的变量名以及变量前缀
# 对应 MySQL 语义组：ident_keywords_ambiguous_4_system_variables
MYSQL_IDENT_KEYWORDS_AMBIGUOUS_4_SYSTEM_VARIABLES = ms_parser.create_group(
    name="ident_keywords_ambiguous_4_system_variables",
    rules=[
        ms_parser.create_rule(
            symbols=[terminal_type],
            action=lambda x: ast.Ident(x[0])
        )
        for terminal_type in MYSQL_TERMINAL_SET_KEYWORDS_AMBIGUOUS_4_SYSTEM_VARIABLES
    ]
)

# [MySQL | Grammar Group] 非保留关键字，在一般场景下可以直接使用
# 对应 MySQL 语义组：ident_keyword
MYSQL_IDENT_KEYWORD = ms_parser.create_group(
    name="ident_general_keyword",
    rules=[
        ms_parser.create_rule(
            symbols=["ident_keywords_unambiguous"]
        ),
        ms_parser.create_rule(
            symbols=["ident_keywords_ambiguous_1_roles_and_labels"]
        ),
        ms_parser.create_rule(
            symbols=["ident_keywords_ambiguous_2_labels"]
        ),
        ms_parser.create_rule(
            symbols=["ident_keywords_ambiguous_3_roles"]
        ),
        ms_parser.create_rule(
            symbols=["ident_keywords_ambiguous_4_system_variables"]
        )
    ]
)

# [MySQL | Grammar Group] 非保留关键字，可以用作存储过程标签名称（label name）
# 对应 MySQL 语义组：label_keyword
MYSQL_LABEL_KEYWORD = ms_parser.create_group(
    name="ident_label_keyword",
    rules=[
        ms_parser.create_rule(
            symbols=["ident_keywords_unambiguous"]
        ),
        ms_parser.create_rule(
            symbols=["ident_keywords_ambiguous_3_roles"]
        ),
        ms_parser.create_rule(
            symbols=["ident_keywords_ambiguous_4_system_variables"]
        )
    ]
)

# [MySQL | Grammar Group] 非保留关键字，可以用作角色名称（role name）
# 对应 MySQL 语义组：role_keyword
MYSQL_ROLE_KEYWORD = ms_parser.create_group(
    name="ident_role_keyword",
    rules=[
        ms_parser.create_rule(
            symbols=["ident_keywords_unambiguous"]
        ),
        ms_parser.create_rule(
            symbols=["ident_keywords_ambiguous_2_labels"]
        ),
        ms_parser.create_rule(
            symbols=["ident_keywords_ambiguous_4_system_variables"]
        )
    ]
)

# [MySQL | Grammar Group] 非保留关键字，可以作为 SET 语句中赋值操作左侧的变量名以及变量前缀
# 对应 MySQL 语义组：lvalue_keyword
MYSQL_VARIABLE_KEYWORD = ms_parser.create_group(
    name="ident_variable_keyword",
    rules=[
        ms_parser.create_rule(
            symbols=["ident_keywords_unambiguous"]
        ),
        ms_parser.create_rule(
            symbols=["ident_keywords_ambiguous_1_roles_and_labels"]
        ),
        ms_parser.create_rule(
            symbols=["ident_keywords_ambiguous_2_labels"]
        ),
        ms_parser.create_rule(
            symbols=["ident_keywords_ambiguous_3_roles"]
        )
    ]
)

# 单个标识符（`ident`）
MYSQL_IDENT = ms_parser.create_group(
    name="ident",
    rules=[
        ms_parser.create_rule(
            symbols=["ident_sys"]
        ),
        ms_parser.create_rule(
            symbols=["ident_general_keyword"]
        )
    ]
)

# [MySQL | Grammar Group] 表示存储过程名称的标识符
# 对应 MySQL 语义组：label_ident
MYSQL_LABEL_IDENT = ms_parser.create_group(
    name="label_ident",
    rules=[
        ms_parser.create_rule(
            symbols=["ident_sys"]
        ),
        ms_parser.create_rule(
            symbols=["ident_label_keyword"]
        )
    ]
)

# [MySQL | Grammar Group] 表示角色的标识符
# 对应 MySQL 语义组：role_ident
MYSQL_ROLE_IDENT = ms_parser.create_group(
    name="role_ident",
    rules=[
        ms_parser.create_rule(
            symbols=["ident_sys"]
        ),
        ms_parser.create_rule(
            symbols=["ident_role_keyword"]
        )
    ]
)

# [MySQL | Grammar Group] 表示变量名或变量名前缀的标识符
# 对应 MySQL 语义组：lvalue_ident
MYSQL_VARIABLE_IDENT = ms_parser.create_group(
    name="variable_ident",
    rules=[
        ms_parser.create_rule(
            symbols=["ident_sys"]
        ),
        ms_parser.create_rule(
            symbols=["ident_variable_keyword"]
        )
    ]
)
