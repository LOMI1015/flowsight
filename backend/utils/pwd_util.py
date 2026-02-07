from passlib.context import CryptContext

# 使用 argon2 作为密码哈希算法
# 同时支持 bcrypt 以兼容旧密码（deprecated='auto' 会自动标记为已弃用）
# argon2 参数说明：
# - memory_cost: 内存成本（KB），默认 65536 (64MB)
# - time_cost: 迭代次数，默认 3
# - parallelism: 并行度，默认 4
pwd_context = CryptContext(
    schemes=['argon2', 'bcrypt'],
    default='argon2',
    deprecated='auto',
    argon2__memory_cost=65536,  # 64MB 内存
    argon2__time_cost=3,        # 3 次迭代
    argon2__parallelism=4       # 4 个并行线程
)


class PwdUtil:
    """
    密码工具类
    """

    @classmethod
    def verify_password(cls, plain_password, hashed_password):
        """
        工具方法：校验当前输入的密码与数据库存储的密码是否一致

        :param plain_password: 当前输入的密码
        :param hashed_password: 数据库存储的密码
        :return: 校验结果
        """
        return pwd_context.verify(plain_password, hashed_password)

    @classmethod
    def get_password_hash(cls, input_password):
        """
        工具方法：对当前输入的密码进行加密

        :param input_password: 输入的密码
        :return: 加密成功的密码
        """
        return pwd_context.hash(input_password)
