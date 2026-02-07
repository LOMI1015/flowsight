from datetime import datetime
from config.database import (
    async_engine,
    AsyncSessionLocal,
    Base,
    async_task_engine,
    AsyncTaskSessionLocal,
    TaskBase
)
from config.env import AdminConfig
from utils.log_util import logger
from utils.pwd_util import PwdUtil


async def get_db():
    """
    每一个请求处理完毕后会关闭当前连接，不同的请求使用不同的连接

    :return:
    """
    async with AsyncSessionLocal() as current_db:
        yield current_db


async def get_task_db():
    """
    定时任务数据数据库连接
    """
    async with AsyncTaskSessionLocal() as current_db:
        yield current_db


async def init_create_table():
    """
    应用启动时初始化数据库连接

    :return:
    """
    logger.info('初始化数据库连接...')
    async with async_engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
    logger.info('数据库连接成功')


async def init_admin_user():
    """
    应用启动时初始化超级管理员用户
    如果 sys_user 表中不存在 user_id=1 的用户，则根据配置创建

    :return:
    """
    try:
        from sqlalchemy import select, text
        from module_admin.entity.do.user_do import SysUser, SysUserRole
        from config.env import DataBaseConfig

        async with AsyncSessionLocal() as db:
            # 直接查询数据库，检查是否存在 user_id=1 的用户（不检查状态）
            result = await db.execute(select(SysUser).where(SysUser.user_id == 1))
            admin_user = result.scalars().first()

            if not admin_user:
                logger.info('未找到超级管理员用户，开始创建...')

                # 准备密码哈希
                password_hash = PwdUtil.get_password_hash(AdminConfig.app_super_password)
                current_time = datetime.now()

                # 构建插入 SQL
                if DataBaseConfig.db_type == 'postgresql':
                    # PostgreSQL: 先设置序列，然后插入
                    # 确保序列值至少为 1
                    await db.execute(text("SELECT setval('sys_user_user_id_seq', GREATEST(1, (SELECT COALESCE(MAX(user_id), 0) FROM sys_user) + 1), false)"))

                    # 插入用户数据
                    insert_user_sql = text("""
                        INSERT INTO sys_user 
                        (user_id, dept_id, user_name, nick_name, user_type, email, phonenumber, sex, avatar, password, status, del_flag, create_by, create_time, update_by, update_time, remark)
                        VALUES 
                        (1, :dept_id, :user_name, :nick_name, '00', :email, :phonenumber, :sex, 'boy-blue.png', :password, '0', '0', 'system', :create_time, 'system', :update_time, '系统自动创建的超级管理员')
                    """)
                else:
                    # MySQL: 直接插入，指定 user_id
                    insert_user_sql = text("""
                        INSERT INTO sys_user 
                        (user_id, dept_id, user_name, nick_name, user_type, email, phonenumber, sex, avatar, password, status, del_flag, create_by, create_time, update_by, update_time, remark)
                        VALUES 
                        (1, :dept_id, :user_name, :nick_name, '00', :email, :phonenumber, :sex, 'boy-blue.png', :password, '0', '0', 'system', :create_time, 'system', :update_time, '系统自动创建的超级管理员')
                    """)

                await db.execute(
                    insert_user_sql,
                    {
                        'dept_id': AdminConfig.admin_dept_id,
                        'user_name': AdminConfig.app_super_account,
                        'nick_name': AdminConfig.admin_nick_name,
                        'email': AdminConfig.admin_email,
                        'phonenumber': AdminConfig.admin_phonenumber,
                        'sex': AdminConfig.admin_sex,
                        'password': password_hash,
                        'create_time': current_time,
                        'update_time': current_time,
                    }
                )

                # 添加管理员角色关联（role_id=1）
                # 先检查是否已存在关联
                role_result = await db.execute(
                    select(SysUserRole).where(
                        SysUserRole.user_id == 1, SysUserRole.role_id == AdminConfig.admin_role_id
                    )
                )
                existing_role = role_result.scalars().first()
                if not existing_role:
                    if DataBaseConfig.db_type == 'postgresql':
                        # PostgreSQL: 使用 ON CONFLICT
                        insert_role_sql = text("""
                            INSERT INTO sys_user_role (user_id, role_id)
                            VALUES (1, :role_id)
                            ON CONFLICT DO NOTHING
                        """)
                    else:
                        # MySQL: 使用 INSERT IGNORE
                        insert_role_sql = text("""
                            INSERT IGNORE INTO sys_user_role (user_id, role_id)
                            VALUES (1, :role_id)
                        """)
                    await db.execute(insert_role_sql, {'role_id': AdminConfig.admin_role_id})

                await db.commit()
                logger.info(f'超级管理员创建成功: {AdminConfig.app_super_account} (密码: {AdminConfig.app_super_password})')
            else:
                logger.info('超级管理员用户已存在，跳过创建')
    except Exception as e:
        logger.error(f'初始化超级管理员失败: {str(e)}', exc_info=True)
        # 初始化失败不影响系统启动，只记录日志
