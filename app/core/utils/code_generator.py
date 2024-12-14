import re
import datetime
import random
import string


def generate_code(prefix: str, raw_code: str = None) -> str:
    """生成编码

    Args:
        prefix: 编码前缀
        raw_code: 用户输入的编码

    Returns:
        str: 生成的编码
    """
    if raw_code:
        # 检查是否符合规范
        if not re.match(r'^[a-zA-Z0-9-_]+$', raw_code):
            raise ValueError(
                "Code can only contain letters, numbers, dash and underscore")
        return raw_code

    # 系统自动生成
    current_time = datetime.datetime.now().strftime('%Y%m%d%H%M%S')  # 获取当前时间
    random_letters = ''.join(random.choices(
        string.ascii_letters, k=4))  # 生成4个随机字母
    return f"{prefix}-{current_time}-{random_letters}"
