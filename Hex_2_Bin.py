import os

def parse_hex_file(file_path):
    data = bytearray()

    with open(file_path, "r") as file:
        for line in file:
            # 去除换行符并解析每一行
            line = line.strip()
            if line.startswith(":"):
                # 解析每个字段
                byte_count = int(line[1:3], 16)
                address = int(line[3:7], 16)
                record_type = int(line[7:9], 16)
                data_bytes = line[9:-2]

                # 根据记录类型处理数据
                if record_type == 0x00:
                    # 数据记录，将数据字节添加到结果中
                    data.extend(bytearray.fromhex(data_bytes))

                # 这里可以根据需要处理其他记录类型，如扩展线性地址记录、结束记录等

    return data

# 获取当前工作目录
current_dir = os.getcwd()

# 要打开的文件名
file_name = "BPC_CAN.hex"

# 拼接文件路径
file_path = os.path.join(current_dir, file_name)

# 解析 .hex 文件
hex_data = parse_hex_file(file_path)

file_name = "example.bin"

# 拼接文件路径
file_path = os.path.join(current_dir, file_name)

# 以二进制写入模式打开文件
with open(file_path, "wb") as file:
    # 写入二进制数据
    file.write(hex_data)