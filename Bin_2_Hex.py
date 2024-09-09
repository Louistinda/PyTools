def create_hex_record(address, data):
    # 计算字节总和校验
    checksum = (-(sum(data) + (address >> 8) + (address & 0xFF) + len(data))) & 0xFF

    # 构建 Intel HEX 记录
    hex_record = ":"
    hex_record += "{:02X}".format(len(data))
    hex_record += "{:04X}".format(address)
    hex_record += "00"
    hex_record += "".join("{:02X}".format(byte) for byte in data)
    hex_record += "{:02X}".format(checksum)

    return hex_record

def bin_to_hex(bin_file_path, hex_file_path, start_address):
    # 打开二进制文件
    with open(bin_file_path, "rb") as bin_file:
        # 读取文件内容
        bin_data = bin_file.read()

    # 每个记录中数据字节数
    record_data_size = 16

    # 计算记录数量
    num_records = (len(bin_data) + record_data_size - 1) // record_data_size

    # 打开 HEX 文件
    with open(hex_file_path, "w") as hex_file:
        hex_file.write(":02000004"+str(format((start_address>>16)&0xFFFF, '04X'))+"F2\n")
        
        for record_index in range(num_records):
            # 计算记录的起始地址
            address = start_address - 0x08000000 + record_index * record_data_size

            # 提取数据
            data = bin_data[record_index * record_data_size : (record_index + 1) * record_data_size]

            # 创建 HEX 记录
            hex_record = create_hex_record(address, data)

            # 写入记录到 HEX 文件
            hex_file.write(hex_record + "\n")

        # 写入结束记录
        hex_file.write(":00000001FF")

# 示例用法
bin_to_hex("example.bin", "output.hex", 0x08002800)
