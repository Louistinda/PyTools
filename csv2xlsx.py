import os
import pandas as pd

# 获取当前文件夹中的所有.csv文件
csv_files = [filename for filename in os.listdir() if filename.endswith('.csv')]

# 创建一个Excel文件
output_file = '测试数据.xlsx'
writer = pd.ExcelWriter(output_file, engine='xlsxwriter')

# 遍历每个.csv文件并将其内容写入不同的sheet
for csv_file in csv_files:
    sheet_name = os.path.splitext(csv_file)[0]  # 使用文件名作为sheet名称
    df = pd.read_csv(csv_file)
    df.to_excel(writer, sheet_name=sheet_name, index=False)

# 保存Excel文件
writer._save()
print(f"已将所有.csv文件的内容保存到'{output_file}'中。")
