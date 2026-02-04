import pandas as pd
import os

xlsx_files = 'mmc2.xlsx'

# 读取Excel文件中的所有工作表
xls = pd.ExcelFile(xlsx_files)
sheet_names = xls.sheet_names  # 获取所有工作表名称

for sheet in sheet_names:
    df = pd.read_excel(xlsx_files, sheet_name=sheet, header=7)
    # 查找Ketcham行
    target_row = df[df.iloc[:, 0].astype(str).str.contains('Standard deviation of mean', na=False)].index[0]
    # 删除Ketcham行前一行及之后所有行
    df = df.iloc[:target_row-1]
    # Convert row 2 to numeric before multiplication
    df = df.iloc[:, [0,1, 2, 4, 6]]
    df.columns = ['GrainID','Ns', 'A', 'U1', 'U1err']
    df['A'] = df['A'] * 1E8
    filename = f"{sheet}.csv"
    df.to_csv(filename, index=False)
    print(f"已导出: {filename}")



samples = sheet_names