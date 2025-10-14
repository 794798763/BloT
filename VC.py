import secrets
from ecdsa import SECP256k1, SigningKey, VerifyingKey, ellipticcurve, numbertheory
from ecdsa import SECP256k1
import ecdsa.ellipticcurve as ec

class VectorCommitment:
    def __init__(self, curve=SECP256k1):
        self.curve = curve
        self.G = curve.generator
        self.order = curve.order

    def setup(self, n):
        """生成n个随机基点和一个主密钥"""
        # 生成n个随机基点
        H = []
        for _ in range(n):
            # 生成随机数
            random_scalar = secrets.randbelow(self.order)
            # 计算H_i = random_scalar * G
            point = self.G * random_scalar
            H.append(point)

        # 生成主密钥
        master_secret = secrets.randbelow(self.order)

        return H, master_secret

    def commit(self, H, vector, master_secret):
        """对向量进行承诺"""
        if len(H) != len(vector):
            raise ValueError("向量长度与基点数量不匹配")

        # 计算承诺 C = sum(v_i * H_i) + s * G
        commitment = self.G * 0  # 初始化为无穷远点

        for v, h in zip(vector, H):
            # 确保v是整数
            if not isinstance(v, int):
                v = int(v)
            # 计算v_i * H_i并累加到承诺中
            commitment += h * v

        # 加上主密钥对应的点
        commitment += self.G * master_secret

        return commitment

    def proof(self, H, vector, index, master_secret):
        """打开向量的特定位置"""
        if index < 0 or index >= len(vector):
            raise IndexError("索引超出范围")

        # 计算除index外其他位置的承诺
        opening = self.G * 0  # 初始化为无穷远点

        for i, (v, h) in enumerate(zip(vector, H)):
            if i != index:
                # 确保v是整数
                if not isinstance(v, int):
                    v = int(v)
                # 计算v_i * H_i并累加到opening中
                opening += h * v

        # 加上主密钥对应的点
        opening += self.G * master_secret

        return opening

    def verify(self, commitment, H, index, value, opening):
        """验证特定位置的值"""
        # 计算 H_index * value + opening
        verification = H[index] * value + opening

        # 检查计算结果是否等于承诺
        return verification == commitment


    def verify_point_on_curve(point: ec.PointJacobi) -> bool:
        """验证点是否在SECP256k1曲线上"""
        x = point.x()
        y = point.y()
        curve = SECP256k1.curve
        p = curve.p()

        # 计算 y² 和 x³ + 7 (mod p)
        y_squared = (y * y) % p
        x_cubed_plus_7 = (pow(x, 3, p) + 7) % p

        return y_squared == x_cubed_plus_7
def point_to_compressed_string(point):
    """将PointJacobi对象转换为压缩格式字符串"""
    x = point.x()
    y = point.y()
    # 确定y的奇偶性（0为偶数，1为奇数）
    parity = y % 2
    # 压缩格式：前缀 + x坐标的十六进制
    prefix = "02" if parity == 0 else "03"
    return f"{prefix}{x:064x}"  # 64是因为256位/4=64个十六进制字符

def points_to_compressed_string(points):
    re=[]
    for point in points:
        """将PointJacobi对象转换为压缩格式字符串"""
        x = point.x()
        y = point.y()
        # 确定y的奇偶性（0为偶数，1为奇数）
        parity = y % 2
        # 压缩格式：前缀 + x坐标的十六进制
        prefix = "02" if parity == 0 else "03"
        re.append(f"{prefix}{x:064x}")   # 64是因为256位/4=64个十六进制字符
    return re

def compressed_string_to_point(compressed_str):
    """将压缩格式字符串还原为PointJacobi对象"""
    if not compressed_str.startswith(('02', '03')):
        raise ValueError("无效的压缩格式前缀")

    # 提取前缀和x坐标
    prefix = compressed_str[:2]
    x = int(compressed_str[2:], 16)

    # 获取曲线参数
    curve = SECP256k1.curve  # y² = x³ + 7
    p = curve.p()  # 曲线的模数

    # 计算 y² = x³ + 7 (mod p)
    y_squared = (pow(x, 3, p) + 7) % p

    # 计算平方根 y = √(y²) mod p
    # 使用Tonelli-Shanks算法（SECP256k1的p ≡ 1 mod 4，有高效解法）
    y = pow(y_squared, (p + 1) // 4, p)

    # 根据前缀选择正确的y（偶数或奇数）
    required_parity = 0 if prefix == '02' else 1
    actual_parity = y % 2

    if actual_parity != required_parity:
        y = p - y  # 另一个解

    # 创建PointJacobi对象
    return ec.PointJacobi(
        curve=curve,
        x=x,
        y=y,
        z=1,  # Jacobi坐标中的z=1表示仿射坐标
        order=SECP256k1.order
    )


def compressed_string_to_points(compressed_strs):
    re=[]
    for i in compressed_strs:
        re.append(compressed_string_to_point(i))
    return re

# 使用示例
if __name__ == "__main__":
    # 初始化向量承诺方案
    vc = VectorCommitment()
    # 待承诺的向量
    vector = [123, 456, 789, 1011, 1213]
    # 设置：生成基点和主密钥
    H, master_secret = vc.setup(len(vector))
    # 生成承诺
    commitment = vc.commit(H, vector, master_secret)
    print(point_to_compressed_string(commitment))
    # 打开特定位置（例如，索引2）
    index_to_open = 3
    value, proof = vc.proof(H, vector, index_to_open, master_secret)
    print(points_to_compressed_string(H))
    print(master_secret)
    print(point_to_compressed_string(proof))
    # 验证打开的值
    valid1 = vc.verify(commitment, H, index_to_open, value, proof)
    print(valid1)

    s_commitment=point_to_compressed_string(commitment)
    s_proof=point_to_compressed_string(proof)
    print(s_commitment)
    print(s_proof)
    n_commitment=compressed_string_to_point(s_commitment)
    n_proof=compressed_string_to_point(s_proof)
    valid2 = vc.verify(n_commitment, H, index_to_open, value, n_proof)
    print(valid2)
