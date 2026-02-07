from sqlalchemy import text
from config.get_db import AsyncSessionLocal
from config.env import DataBaseConfig
from module_bi.entity.vo.console_vo import ConsoleDataModel, ChartDataModel, ChartDataItem
from utils.log_util import logger
from datetime import datetime, date, timedelta


class ConsoleService:
    """
    工作台数据服务层
    """

    @staticmethod
    async def get_console_data():
        """
        获取工作台数据service

        :return: 工作台数据
        """
        # 初始化变量
        console_data = ConsoleDataModel()

        # 使用数据库连接查询数据
        async with AsyncSessionLocal() as db:
            try:
                # 查询最新一天的数据
                result = await db.execute(text("""
                    SELECT 
                        day,
                        robot_count,
                        agent_count,
                        robot_rate,
                        b_agent_count,
                        create_return_count,
                        create_complain_count,
                        create_one_line_count,
                        create_two_line_count,
                        create_b_line_count,
                        approve_return_count,
                        approve_complain_count,
                        approve_one_line_count,
                        approve_two_line_count,
                        approve_b_line_count,
                        return_24_count,
                        return_24_rate,
                        call_out_count,
                        call_in_count,
                        chat_5eval_count,
                        call_5eval_count,
                        chat_eval_count,
                        call_eval_count
                    FROM dm.dm_group_count_by_day
                    ORDER BY day DESC
                    LIMIT 1
                """))
                
                row = result.first()
                if row:
                    # 将 date 类型转换为 datetime 类型（设置为当天的 00:00:00）
                    if row[0] is not None:
                        from datetime import date, datetime
                        if isinstance(row[0], datetime):
                            console_data.date = row[0]
                        elif isinstance(row[0], date):
                            # 如果是 date 类型，转换为 datetime
                            console_data.date = datetime.combine(row[0], datetime.min.time())
                        else:
                            console_data.date = None
                    else:
                        console_data.date = None
                    console_data.robot_count = row[1] if row[1] is not None else 0
                    console_data.agent_count = row[2] if row[2] is not None else 0
                    console_data.robot_rate = float(row[3]) if row[3] is not None else 0.0
                    console_data.b_agent_count = row[4] if row[4] is not None else 0
                    console_data.create_return_count = row[5] if row[5] is not None else 0
                    console_data.create_complain_count = row[6] if row[6] is not None else 0
                    console_data.create_one_line_count = row[7] if row[7] is not None else 0
                    console_data.create_two_line_count = row[8] if row[8] is not None else 0
                    console_data.create_b_line_count = row[9] if row[9] is not None else 0
                    console_data.approve_return_count = row[10] if row[10] is not None else 0
                    console_data.approve_complain_count = row[11] if row[11] is not None else 0
                    console_data.approve_one_line_count = row[12] if row[12] is not None else 0
                    console_data.approve_two_line_count = row[13] if row[13] is not None else 0
                    console_data.approve_b_line_count = row[14] if row[14] is not None else 0
                    console_data.return_24_count = row[15] if row[15] is not None else 0
                    console_data.return_24_rate = float(row[16]) if row[16] is not None else 0.0
                    console_data.call_out_count = row[17] if row[17] is not None else 0
                    console_data.call_in_count = row[18] if row[18] is not None else 0
                    console_data.chat_5eval_count = row[19] if row[19] is not None else 0
                    console_data.call_5eval_count = row[20] if row[20] is not None else 0
                    console_data.chat_eval_count = row[21] if row[21] is not None else 0
                    console_data.call_eval_count = row[22] if row[22] is not None else 0

                logger.info('获取工作台数据成功')
            except Exception as e:
                logger.error(f'查询工作台数据失败: {str(e)}', exc_info=True)

        return console_data

    @staticmethod
    async def get_chart_data():
        """
        获取折线图数据service（最近12天）

        :return: 折线图数据
        """
        chart_data = ChartDataModel(dates=[], data=[])

        # 使用数据库连接查询数据
        async with AsyncSessionLocal() as db:
            try:
                # 根据数据库类型构建SQL查询
                if DataBaseConfig.db_type == 'postgresql':
                    # PostgreSQL语法
                    sql_query = """
                        SELECT 
                            day,
                            COALESCE(robot_count, 0) as robot_count,
                            COALESCE(agent_count, 0) as agent_count,
                            COALESCE(call_out_count, 0) as call_out_count,
                            COALESCE(call_in_count, 0) as call_in_count,
                            COALESCE(create_return_count, 0) as create_return_count,
                            COALESCE(create_complain_count, 0) as create_complain_count,
                            COALESCE(create_one_line_count, 0) as create_one_line_count,
                            COALESCE(create_two_line_count, 0) as create_two_line_count,
                            COALESCE(create_b_line_count, 0) as create_b_line_count,
                            COALESCE(approve_return_count, 0) as approve_return_count,
                            COALESCE(approve_complain_count, 0) as approve_complain_count
                        FROM dm.dm_group_count_by_day
                        WHERE day >= CURRENT_DATE - INTERVAL '11 days'
                        ORDER BY day ASC
                        LIMIT 12
                    """
                else:
                    # MySQL语法
                    sql_query = """
                        SELECT 
                            day,
                            COALESCE(robot_count, 0) as robot_count,
                            COALESCE(agent_count, 0) as agent_count,
                            COALESCE(call_out_count, 0) as call_out_count,
                            COALESCE(call_in_count, 0) as call_in_count,
                            COALESCE(create_return_count, 0) as create_return_count,
                            COALESCE(create_complain_count, 0) as create_complain_count,
                            COALESCE(create_one_line_count, 0) as create_one_line_count,
                            COALESCE(create_two_line_count, 0) as create_two_line_count,
                            COALESCE(create_b_line_count, 0) as create_b_line_count,
                            COALESCE(approve_return_count, 0) as approve_return_count,
                            COALESCE(approve_complain_count, 0) as approve_complain_count
                        FROM dm.dm_group_count_by_day
                        WHERE day >= DATE_SUB(CURRENT_DATE, INTERVAL 11 DAY)
                        ORDER BY day ASC
                        LIMIT 12
                    """
                
                result = await db.execute(text(sql_query))
                
                rows = result.fetchall()
                
                dates = []
                data_items = []
                
                for row in rows:
                    day_value = row[0]
                    robot_count = row[1] if row[1] is not None else 0
                    agent_count = row[2] if row[2] is not None else 0
                    call_out_count = row[3] if row[3] is not None else 0
                    call_in_count = row[4] if row[4] is not None else 0
                    create_return_count = row[5] if row[5] is not None else 0
                    create_complain_count = row[6] if row[6] is not None else 0
                    create_one_line_count = row[7] if row[7] is not None else 0
                    create_two_line_count = row[8] if row[8] is not None else 0
                    create_b_line_count = row[9] if row[9] is not None else 0
                    approve_return_count = row[10] if row[10] is not None else 0
                    approve_complain_count = row[11] if row[11] is not None else 0
                    
                    # 格式化日期为字符串（MM-DD格式）
                    if isinstance(day_value, datetime):
                        date_str = day_value.strftime('%m-%d')
                        date_obj = day_value
                    elif isinstance(day_value, date):
                        date_str = day_value.strftime('%m-%d')
                        # 将date转换为datetime（设置为当天的00:00:00）
                        date_obj = datetime.combine(day_value, datetime.min.time())
                    else:
                        continue
                    
                    dates.append(date_str)
                    data_items.append(ChartDataItem(
                        date=date_obj,
                        robot_count=robot_count,
                        agent_count=agent_count,
                        call_out_count=call_out_count,
                        call_in_count=call_in_count,
                        create_return_count=create_return_count,
                        create_complain_count=create_complain_count,
                        create_one_line_count=create_one_line_count,
                        create_two_line_count=create_two_line_count,
                        create_b_line_count=create_b_line_count,
                        approve_return_count=approve_return_count,
                        approve_complain_count=approve_complain_count
                    ))
                
                chart_data.dates = dates
                chart_data.data = data_items

                logger.info('获取折线图数据成功')
            except Exception as e:
                logger.error(f'查询折线图数据失败: {str(e)}', exc_info=True)

        return chart_data

