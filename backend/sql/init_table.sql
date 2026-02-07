-- PostgreSQL 建表脚本

create table apscheduler_jobs
(
    id            varchar(191) not null primary key,
    next_run_time double precision null,
    job_state     bytea        not null
);

create index ix_apscheduler_jobs_next_run_time on apscheduler_jobs (next_run_time);

create table gen_table
(
    table_id          serial primary key,
    table_name        varchar(200)  null,
    table_comment     varchar(500)  null,
    sub_table_name    varchar(64)   null,
    sub_table_fk_name varchar(64)   null,
    class_name        varchar(100)  null,
    tpl_category      varchar(200)  null,
    tpl_web_type      varchar(30)   null,
    package_name      varchar(100)  null,
    module_name       varchar(30)   null,
    business_name     varchar(30)   null,
    function_name     varchar(100)  null,
    function_author   varchar(100)  null,
    gen_type          varchar(1)    null,
    gen_path          varchar(200)  null,
    options           varchar(1000) null,
    create_by         varchar(64)   null,
    create_time       timestamp(0)  null,
    update_by         varchar(64)   null,
    update_time       timestamp(0)  null,
    remark            varchar(500)  null
);

comment on column gen_table.table_id is '编号';
comment on column gen_table.table_name is '表名称';
comment on column gen_table.table_comment is '表描述';
comment on column gen_table.sub_table_name is '关联子表的表名';
comment on column gen_table.sub_table_fk_name is '子表关联的外键名';
comment on column gen_table.class_name is '实体类名称';
comment on column gen_table.tpl_category is '使用的模板（crud单表操作 tree树表操作）';
comment on column gen_table.tpl_web_type is '前端模板类型（element-ui模版 element-plus模版）';
comment on column gen_table.package_name is '生成包路径';
comment on column gen_table.module_name is '生成模块名';
comment on column gen_table.business_name is '生成业务名';
comment on column gen_table.function_name is '生成功能名';
comment on column gen_table.function_author is '生成功能作者';
comment on column gen_table.gen_type is '生成代码方式（0zip压缩包 1自定义路径）';
comment on column gen_table.gen_path is '生成路径（不填默认项目路径）';
comment on column gen_table.options is '其它生成选项';
comment on column gen_table.create_by is '创建者';
comment on column gen_table.create_time is '创建时间';
comment on column gen_table.update_by is '更新者';
comment on column gen_table.update_time is '更新时间';
comment on column gen_table.remark is '备注';
comment on table gen_table is '代码生成业务表';

create table gen_table_column
(
    column_id    bigserial primary key,
    table_id     bigint         null,
    column_name  varchar(200)   null,
    column_comment varchar(500) null,
    column_type  varchar(100)   null,
    python_type varchar(500)   null,
    python_field varchar(200)   null,
    is_pk       char(1)        null,
    is_increment char(1)       null,
    is_required  char(1)        null,
    is_unique   char(1)        null,
    is_insert   char(1)        null,
    is_edit     char(1)        null,
    is_list     char(1)        null,
    is_query    char(1)        null,
    query_type  varchar(200)  default 'EQ' null,
    html_type   varchar(200)   null,
    dict_type   varchar(200)   default '' null,
    sort        int            null,
    create_by   varchar(64)    default '' null,
    create_time timestamp(0)   null,
    update_by   varchar(64)    default '' null,
    update_time timestamp(0)  null
);

comment on column gen_table_column.column_id is '编号';
comment on column gen_table_column.table_id is '归属表编号';
comment on column gen_table_column.column_name is '列名称';
comment on column gen_table_column.column_comment is '列描述';
comment on column gen_table_column.column_type is '列类型';
comment on column gen_table_column.python_type is 'PYTHON类型';
comment on column gen_table_column.python_field is 'PYTHON字段名';
comment on column gen_table_column.is_pk is '是否主键（1是）';
comment on column gen_table_column.is_increment is '是否自增（1是）';
comment on column gen_table_column.is_required is '是否必填（1是）';
comment on column gen_table_column.is_unique is '是否唯一（1是）';
comment on column gen_table_column.is_insert is '是否为插入字段（1是）';
comment on column gen_table_column.is_edit is '是否编辑字段（1是）';
comment on column gen_table_column.is_list is '是否列表字段（1是）';
comment on column gen_table_column.is_query is '是否查询字段（1是）';
comment on column gen_table_column.query_type is '查询方式（等于、不等于、大于、小于、范围）';
comment on column gen_table_column.html_type is '显示类型（文本框、文本域、下拉框、复选框、单选框、日期控件）';
comment on column gen_table_column.dict_type is '字典类型';
comment on column gen_table_column.sort is '排序';
comment on column gen_table_column.create_by is '创建者';
comment on column gen_table_column.create_time is '创建时间';
comment on column gen_table_column.update_by is '更新者';
comment on column gen_table_column.update_time is '更新时间';
comment on table gen_table_column is '代码生成业务表字段';

create table sys_config
(
    config_id    serial primary key,
    config_name  varchar(100) default '' null,
    config_key   varchar(100) default '' null,
    config_value varchar(500) default '' null,
    config_type  char(1)      default 'N' null,
    create_by    varchar(64) default '' null,
    create_time  timestamp(0) null,
    update_by    varchar(64) default '' null,
    update_time  timestamp(0) null,
    remark       varchar(500) null
);

comment on column sys_config.config_id is '参数主键';
comment on column sys_config.config_name is '参数名称';
comment on column sys_config.config_key is '参数键名';
comment on column sys_config.config_value is '参数键值';
comment on column sys_config.config_type is '系统内置（Y是 N否）';
comment on column sys_config.create_by is '创建者';
comment on column sys_config.create_time is '创建时间';
comment on column sys_config.update_by is '更新者';
comment on column sys_config.update_time is '更新时间';
comment on column sys_config.remark is '备注';
comment on table sys_config is '参数配置表';

create table sys_dept
(
    dept_id     bigserial primary key,
    parent_id   bigint      default 0 null,
    ancestors   varchar(50) default '' null,
    dept_name   varchar(30) default '' null,
    order_num   int         default 0 null,
    leader      varchar(20) null,
    phone       varchar(11) null,
    email       varchar(50) null,
    status      char(1)     default '0' null,
    del_flag    char(1)     default '0' null,
    create_by   varchar(64) default '' null,
    create_time timestamp(0) null,
    update_by   varchar(64) default '' null,
    update_time timestamp(0) null
);

comment on column sys_dept.dept_id is '部门id';
comment on column sys_dept.parent_id is '父部门id';
comment on column sys_dept.ancestors is '祖级列表';
comment on column sys_dept.dept_name is '部门名称';
comment on column sys_dept.order_num is '显示顺序';
comment on column sys_dept.leader is '负责人';
comment on column sys_dept.phone is '联系电话';
comment on column sys_dept.email is '邮箱';
comment on column sys_dept.status is '部门状态（0正常 1停用）';
comment on column sys_dept.del_flag is '删除标志（0代表存在 2代表删除）';
comment on column sys_dept.create_by is '创建者';
comment on column sys_dept.create_time is '创建时间';
comment on column sys_dept.update_by is '更新者';
comment on column sys_dept.update_time is '更新时间';
comment on table sys_dept is '部门表';

create table sys_dict_data
(
    dict_code   bigserial primary key,
    dict_sort   int          default 0 null,
    dict_label  varchar(100) default '' null,
    dict_value  varchar(100) default '' null,
    dict_type   varchar(100) default '' null,
    css_class   varchar(100) null,
    list_class  varchar(100) null,
    is_default  char(1)      default 'N' null,
    status      char(1)      default '0' null,
    create_by   varchar(64)  default '' null,
    create_time timestamp(0) null,
    update_by   varchar(64)  default '' null,
    update_time timestamp(0) null,
    remark      varchar(500) null
);

comment on column sys_dict_data.dict_code is '字典编码';
comment on column sys_dict_data.dict_sort is '字典排序';
comment on column sys_dict_data.dict_label is '字典标签';
comment on column sys_dict_data.dict_value is '字典键值';
comment on column sys_dict_data.dict_type is '字典类型';
comment on column sys_dict_data.css_class is '样式属性（其他样式扩展）';
comment on column sys_dict_data.list_class is '表格回显样式';
comment on column sys_dict_data.is_default is '是否默认（Y是 N否）';
comment on column sys_dict_data.status is '状态（0正常 1停用）';
comment on column sys_dict_data.create_by is '创建者';
comment on column sys_dict_data.create_time is '创建时间';
comment on column sys_dict_data.update_by is '更新者';
comment on column sys_dict_data.update_time is '更新时间';
comment on column sys_dict_data.remark is '备注';
comment on table sys_dict_data is '字典数据表';

create table sys_dict_type
(
    dict_id     bigserial primary key,
    dict_name   varchar(100) default '' null,
    dict_type   varchar(100) default '' null,
    status      char(1)      default '0' null,
    create_by   varchar(64)  default '' null,
    create_time timestamp(0) null,
    update_by   varchar(64)  default '' null,
    update_time timestamp(0) null,
    remark      varchar(500) null,
    constraint dict_type unique (dict_type)
);

comment on column sys_dict_type.dict_id is '字典主键';
comment on column sys_dict_type.dict_name is '字典名称';
comment on column sys_dict_type.dict_type is '字典类型';
comment on column sys_dict_type.status is '状态（0正常 1停用）';
comment on column sys_dict_type.create_by is '创建者';
comment on column sys_dict_type.create_time is '创建时间';
comment on column sys_dict_type.update_by is '更新者';
comment on column sys_dict_type.update_time is '更新时间';
comment on column sys_dict_type.remark is '备注';
comment on table sys_dict_type is '字典类型表';

create table sys_job
(
    job_id          bigserial,
    job_name        varchar(64)  default ''        not null,
    job_group       varchar(64)  default 'default' not null,
    job_executor    varchar(64)  default 'default' null,
    invoke_target   varchar(500)                   not null,
    job_args        varchar(255) default ''        null,
    job_kwargs      varchar(255) default ''        null,
    cron_expression varchar(255) default ''        null,
    misfire_policy  varchar(20)  default '3'       null,
    concurrent      char(1)      default '1'       null,
    status          char(1)      default '0'       null,
    create_by       varchar(64)  default ''       null,
    create_time     timestamp(0) null,
    update_by       varchar(64)  default ''        null,
    update_time     timestamp(0) null,
    remark          varchar(500) default ''       null,
    primary key (job_id, job_name, job_group)
);

comment on column sys_job.job_id is '任务ID';
comment on column sys_job.job_name is '任务名称';
comment on column sys_job.job_group is '任务组名';
comment on column sys_job.job_executor is '任务执行器';
comment on column sys_job.invoke_target is '调用目标字符串';
comment on column sys_job.job_args is '位置参数';
comment on column sys_job.job_kwargs is '关键字参数';
comment on column sys_job.cron_expression is 'cron执行表达式';
comment on column sys_job.misfire_policy is '计划执行错误策略（1立即执行 2执行一次 3放弃执行）';
comment on column sys_job.concurrent is '是否并发执行（0允许 1禁止）';
comment on column sys_job.status is '状态（0正常 1暂停）';
comment on column sys_job.create_by is '创建者';
comment on column sys_job.create_time is '创建时间';
comment on column sys_job.update_by is '更新者';
comment on column sys_job.update_time is '更新时间';
comment on column sys_job.remark is '备注信息';
comment on table sys_job is '定时任务调度表';

create table sys_job_log
(
    job_log_id     bigserial primary key,
    job_id         bigint         null,
    job_name       varchar(64)    not null,
    job_group      varchar(64)    not null,
    job_executor   varchar(64)    not null,
    invoke_target  varchar(500)   null,
    job_args       varchar(255)  default '' null,
    job_kwargs     varchar(255)  default '' null,
    job_trigger    varchar(255)  default '' null,
    job_message    varchar(500)   null,
    status         char(1)       default '0' null,
    exception_info varchar(2000) default '' null,
    job_result     varchar(2000) default '' null,
    start_time     timestamp(0)  null,
    end_time       timestamp(0)  null,
    create_time    timestamp(0)  null
);

comment on column sys_job_log.job_log_id is '任务日志ID';
comment on column sys_job_log.job_id is '任务ID';
comment on column sys_job_log.job_name is '任务名称';
comment on column sys_job_log.job_group is '任务组名';
comment on column sys_job_log.job_executor is '任务执行器';
comment on column sys_job_log.invoke_target is '调用目标字符串';
comment on column sys_job_log.job_args is '位置参数';
comment on column sys_job_log.job_kwargs is '关键字参数';
comment on column sys_job_log.job_trigger is '任务触发器';
comment on column sys_job_log.job_message is '日志信息';
comment on column sys_job_log.status is '执行状态（0正常 1失败）';
comment on column sys_job_log.exception_info is '异常信息';
comment on column sys_job_log.job_result is '执行结果';
comment on column sys_job_log.start_time is '开始时间';
comment on column sys_job_log.end_time is '结束时间';
comment on column sys_job_log.create_time is '创建时间';
comment on table sys_job_log is '定时任务调度日志表';

create table sys_logininfor
(
    info_id        bigserial primary key,
    user_name      varchar(50)  default '' null,
    ipaddr         varchar(128) default '' null,
    login_location varchar(255) default '' null,
    browser        varchar(50) default '' null,
    os             varchar(50) default '' null,
    status         char(1)      default '0' null,
    msg            varchar(255) default '' null,
    login_time     timestamp(0) null
);

create index idx_sys_logininfor_lt on sys_logininfor (login_time);
create index idx_sys_logininfor_s on sys_logininfor (status);

comment on column sys_logininfor.info_id is '访问ID';
comment on column sys_logininfor.user_name is '用户账号';
comment on column sys_logininfor.ipaddr is '登录IP地址';
comment on column sys_logininfor.login_location is '登录地点';
comment on column sys_logininfor.browser is '浏览器类型';
comment on column sys_logininfor.os is '操作系统';
comment on column sys_logininfor.status is '登录状态（0成功 1失败）';
comment on column sys_logininfor.msg is '提示消息';
comment on column sys_logininfor.login_time is '访问时间';
comment on table sys_logininfor is '系统访问记录';

create table sys_menu
(
    menu_id     bigserial primary key,
    menu_name   varchar(50)             not null,
    parent_id   bigint       default 0  null,
    order_num   int          default 0  null,
    path        varchar(200) default '' null,
    component   varchar(255) null,
    query       varchar(255) null,
    route_name  varchar(50)  default '' null,
    is_frame    int          default 1  null,
    is_cache    int          default 0  null,
    menu_type   char(1)      default '' null,
    visible     char(1)      default '0' null,
    status      char(1)      default '0' null,
    perms       varchar(100) null,
    icon        varchar(100) default '#' null,
    create_by   varchar(64)  default '' null,
    create_time timestamp(0) null,
    update_by   varchar(64)  default '' null,
    update_time timestamp(0) null,
    remark      varchar(500) default '' null
);

comment on column sys_menu.menu_id is '菜单ID';
comment on column sys_menu.menu_name is '菜单名称';
comment on column sys_menu.parent_id is '父菜单ID';
comment on column sys_menu.order_num is '显示顺序';
comment on column sys_menu.path is '路由地址';
comment on column sys_menu.component is '组件路径';
comment on column sys_menu.query is '路由参数';
comment on column sys_menu.route_name is '路由名称';
comment on column sys_menu.is_frame is '是否为外链（0是 1否）';
comment on column sys_menu.is_cache is '是否缓存（0缓存 1不缓存）';
comment on column sys_menu.menu_type is '菜单类型（M目录 C菜单 F按钮）';
comment on column sys_menu.visible is '菜单状态（0显示 1隐藏）';
comment on column sys_menu.status is '菜单状态（0正常 1停用）';
comment on column sys_menu.perms is '权限标识';
comment on column sys_menu.icon is '菜单图标';
comment on column sys_menu.create_by is '创建者';
comment on column sys_menu.create_time is '创建时间';
comment on column sys_menu.update_by is '更新者';
comment on column sys_menu.update_time is '更新时间';
comment on column sys_menu.remark is '备注';
comment on table sys_menu is '菜单权限表';

create table sys_notice
(
    notice_id      serial primary key,
    notice_title   varchar(50)    not null,
    notice_type    char(1)        not null,
    notice_content text           null,
    status         char(1)        default '0' null,
    create_by      varchar(64)   default '' null,
    create_time    timestamp(0)  null,
    update_by      varchar(64)   default '' null,
    update_time    timestamp(0)  null,
    remark         varchar(255)   null
);

comment on column sys_notice.notice_id is '公告ID';
comment on column sys_notice.notice_title is '公告标题';
comment on column sys_notice.notice_type is '公告类型（1通知 2公告）';
comment on column sys_notice.notice_content is '公告内容';
comment on column sys_notice.status is '公告状态（0正常 1关闭）';
comment on column sys_notice.create_by is '创建者';
comment on column sys_notice.create_time is '创建时间';
comment on column sys_notice.update_by is '更新者';
comment on column sys_notice.update_time is '更新时间';
comment on column sys_notice.remark is '备注';
comment on table sys_notice is '通知公告表';

create table sys_oper_log
(
    oper_id        bigserial primary key,
    title          varchar(50)   default '' null,
    business_type  int           default 0 null,
    method         varchar(100)  default '' null,
    request_method varchar(10)  default '' null,
    operator_type int           default 0 null,
    oper_name      varchar(50)   default '' null,
    dept_name      varchar(50)   default '' null,
    oper_url       varchar(255) default '' null,
    oper_ip        varchar(128) default '' null,
    oper_location  varchar(255) default '' null,
    oper_param     varchar(2000) default '' null,
    json_result    varchar(2000) default '' null,
    status         int           default 0 null,
    error_msg      varchar(2000) default '' null,
    oper_time      timestamp(0) null,
    cost_time      bigint        default 0 null
);

create index idx_sys_oper_log_bt on sys_oper_log (business_type);
create index idx_sys_oper_log_ot on sys_oper_log (oper_time);
create index idx_sys_oper_log_s on sys_oper_log (status);

comment on column sys_oper_log.oper_id is '日志主键';
comment on column sys_oper_log.title is '模块标题';
comment on column sys_oper_log.business_type is '业务类型（0其它 1新增 2修改 3删除）';
comment on column sys_oper_log.method is '方法名称';
comment on column sys_oper_log.request_method is '请求方式';
comment on column sys_oper_log.operator_type is '操作类别（0其它 1后台用户 2手机端用户）';
comment on column sys_oper_log.oper_name is '操作人员';
comment on column sys_oper_log.dept_name is '部门名称';
comment on column sys_oper_log.oper_url is '请求URL';
comment on column sys_oper_log.oper_ip is '主机地址';
comment on column sys_oper_log.oper_location is '操作地点';
comment on column sys_oper_log.oper_param is '请求参数';
comment on column sys_oper_log.json_result is '返回参数';
comment on column sys_oper_log.status is '操作状态（0正常 1异常）';
comment on column sys_oper_log.error_msg is '错误消息';
comment on column sys_oper_log.oper_time is '操作时间';
comment on column sys_oper_log.cost_time is '消耗时间';
comment on table sys_oper_log is '操作日志记录';

create table sys_post
(
    post_id     bigserial primary key,
    post_code   varchar(64)  not null,
    post_name   varchar(50)  not null,
    post_sort   int          not null,
    status      char(1)      not null,
    create_by   varchar(64)  default '' null,
    create_time timestamp(0) null,
    update_by   varchar(64)  default '' null,
    update_time timestamp(0) null,
    remark      varchar(500) null
);

comment on column sys_post.post_id is '岗位ID';
comment on column sys_post.post_code is '岗位编码';
comment on column sys_post.post_name is '岗位名称';
comment on column sys_post.post_sort is '显示顺序';
comment on column sys_post.status is '状态（0正常 1停用）';
comment on column sys_post.create_by is '创建者';
comment on column sys_post.create_time is '创建时间';
comment on column sys_post.update_by is '更新者';
comment on column sys_post.update_time is '更新时间';
comment on column sys_post.remark is '备注';
comment on table sys_post is '岗位信息表';

create table sys_role
(
    role_id             bigserial primary key,
    role_name           varchar(30)  not null,
    role_key            varchar(100) not null,
    role_sort           int          not null,
    data_scope         char(1)      default '1' null,
    menu_check_strictly smallint     default 1 null,
    dept_check_strictly smallint    default 1 null,
    status              char(1)      not null,
    del_flag            char(1)      default '0' null,
    create_by           varchar(64)  default '' null,
    create_time         timestamp(0) null,
    update_by           varchar(64)  default '' null,
    update_time         timestamp(0) null,
    remark              varchar(500) null
);

comment on column sys_role.role_id is '角色ID';
comment on column sys_role.role_name is '角色名称';
comment on column sys_role.role_key is '角色权限字符串';
comment on column sys_role.role_sort is '显示顺序';
comment on column sys_role.data_scope is '数据范围（1：全部数据权限 2：自定数据权限 3：本部门数据权限 4：本部门及以下数据权限）';
comment on column sys_role.menu_check_strictly is '菜单树选择项是否关联显示';
comment on column sys_role.dept_check_strictly is '部门树选择项是否关联显示';
comment on column sys_role.status is '角色状态（0正常 1停用）';
comment on column sys_role.del_flag is '删除标志（0代表存在 2代表删除）';
comment on column sys_role.create_by is '创建者';
comment on column sys_role.create_time is '创建时间';
comment on column sys_role.update_by is '更新者';
comment on column sys_role.update_time is '更新时间';
comment on column sys_role.remark is '备注';
comment on table sys_role is '角色信息表';

create table sys_role_dept
(
    role_id bigint not null,
    dept_id bigint not null,
    primary key (role_id, dept_id)
);

comment on column sys_role_dept.role_id is '角色ID';
comment on column sys_role_dept.dept_id is '部门ID';
comment on table sys_role_dept is '角色和部门关联表';

create table sys_role_menu
(
    role_id bigint not null,
    menu_id bigint not null,
    primary key (role_id, menu_id)
);

comment on column sys_role_menu.role_id is '角色ID';
comment on column sys_role_menu.menu_id is '菜单ID';
comment on table sys_role_menu is '角色和菜单关联表';

create table sys_user
(
    user_id     bigserial primary key,
    dept_id     bigint         null,
    user_name   varchar(30)    not null,
    nick_name   varchar(30)    not null,
    user_type   varchar(2)     default '00' null,
    email       varchar(50)    null,
    phonenumber varchar(11)    null,
    sex         char(1)        null,
    avatar      varchar(100)   null,
    password    varchar(100)   null,
    status      char(1)        null,
    del_flag    char(1)        null,
    login_ip    varchar(128)   null,
    login_date  timestamp(0)   null,
    create_by   varchar(64)    null,
    create_time timestamp(0)   null,
    update_by   varchar(64)    null,
    update_time timestamp(0)   null,
    remark      varchar(500)   null
);

comment on column sys_user.user_id is '用户ID';
comment on column sys_user.dept_id is '部门ID';
comment on column sys_user.user_name is '用户账号';
comment on column sys_user.nick_name is '用户昵称';
comment on column sys_user.user_type is '用户类型（00系统用户）';
comment on column sys_user.email is '用户邮箱';
comment on column sys_user.phonenumber is '手机号码';
comment on column sys_user.sex is '用户性别（0男 1女 2未知）';
comment on column sys_user.avatar is '头像地址';
comment on column sys_user.password is '密码';
comment on column sys_user.status is '帐号状态（0正常 1停用）';
comment on column sys_user.del_flag is '删除标志（0代表存在 2代表删除）';
comment on column sys_user.login_ip is '最后登录IP';
comment on column sys_user.login_date is '最后登录时间';
comment on column sys_user.create_by is '创建者';
comment on column sys_user.create_time is '创建时间';
comment on column sys_user.update_by is '更新者';
comment on column sys_user.update_time is '更新时间';
comment on column sys_user.remark is '备注';
comment on table sys_user is '用户信息表';

create table sys_upload
(
    id                bigserial primary key,
    upload_starttime  timestamp(0) null,
    upload_endtime    timestamp(0) null,
    upload_userid     bigint       null,
    upload_status     int         null,
    original_filename text        null,
    new_file_name     text        null,
    file_path         text        null,
    file_size         bigint      null,
    file_url          text        null,
    constraint sys_upload_upload_userid_fkey foreign key (upload_userid) references sys_user (user_id)
);

create index upload_userid on sys_upload (upload_userid);

comment on column sys_upload.id is '唯一标识';
comment on column sys_upload.upload_starttime is '开始上传时间';
comment on column sys_upload.upload_endtime is '上传结束时间';
comment on column sys_upload.upload_userid is '上传用户id';
comment on column sys_upload.upload_status is '上传状态（0失败 1成功）';
comment on column sys_upload.original_filename is '原始文件名';
comment on column sys_upload.new_file_name is '新文件名（服务器存储的文件名）';
comment on column sys_upload.file_path is '文件路径（相对路径）';
comment on column sys_upload.file_size is '文件大小（字节）';
comment on column sys_upload.file_url is '文件访问URL';
comment on table sys_upload is '上传记录表';

create table sys_user_post
(
    user_id bigint not null,
    post_id bigint not null,
    primary key (user_id, post_id)
);

comment on column sys_user_post.user_id is '用户ID';
comment on column sys_user_post.post_id is '岗位ID';
comment on table sys_user_post is '用户与岗位关联表';

create table sys_user_role
(
    user_id bigint not null,
    role_id bigint not null,
    primary key (user_id, role_id)
);

comment on column sys_user_role.user_id is '用户ID';
comment on column sys_user_role.role_id is '角色ID';
comment on table sys_user_role is '用户和角色关联表';
