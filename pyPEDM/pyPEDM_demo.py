from pseudo_Ni_simulator import NIfromUnA
from pooledage_clc4pseudoEDM import calc_pooledage4pseudoEDM
# from single_grain_age_clc4LAICPMS import calc_singleage4LAICPMS
from pooledage_clc4LAICPMS import calc_pooledage4LAICPMS
# from central_clc import central
import numpy as np
import os
# os.environ['R_HOME'] = 'C:\Program Files\R\R-4.5.0'
import pandas as pd
import matplotlib.pyplot as plt
from rpy2.robjects.packages import importr
import rpy2.robjects as ro
import tkinter as tk
from tkinter import ttk
from tkinter import filedialog
isoplotR = importr('IsoplotR')

def read_csv_files_from_folder(folder_path):
    """
    读取指定文件夹中的所有CSV文件
    参数:
    folder_path -- 文件夹路径
    返回:
    dict -- 包含所有CSV文件的字典, 键为文件名, 值为DataFrame
    """
    csv_files = {}
    
    # 检查文件夹是否存在
    if not os.path.exists(folder_path):
        raise FileNotFoundError(f"文件夹 {folder_path} 不存在")
    
    # 遍历文件夹中的所有文件
    for file in os.listdir(folder_path):
        if file.endswith('.csv'):
            file_path = os.path.join(folder_path, file)
            try:
                # 读取CSV文件
                df = pd.read_csv(file_path)
                csv_files[file] = df
                print(f"成功读取文件: {file}")
            except Exception as e:
                print(f"读取文件 {file} 时出错: {str(e)}")
    
    return csv_files


# 创建自定义下拉选择窗口
def select_mineral():
    """创建下拉选择窗口并返回选择的矿物类型和参数"""
    # 创建一个根窗口
    root = tk.Tk()
    root.title("Set parameters")
    
    # 强制窗口置顶，确保出现在VSCode前面
    root.attributes('-topmost', True)
    
    # 设置窗口大小并居中显示
    root.geometry("260x200")  # 设置窗口大小为600x300像素
    root.update_idletasks()
    x = (root.winfo_screenwidth() - root.winfo_width()) // 2
    y = (root.winfo_screenheight() - root.winfo_height()) // 2
    root.geometry(f"+{x}+{y}")
    
    # 创建结果变量
    result = {
        'folder': tk.StringVar(value=os.getcwd()),  # 默认当前目录
        'mineral': tk.StringVar(value="apatite"),
        'zeta': tk.StringVar(value="390"),
        'rho_d': tk.StringVar(value="1.322E6")
    }
    
    # 创建主框架 - 减少内边距以适应小窗口
    main_frame = ttk.Frame(root, padding="5")
    main_frame.pack(fill=tk.BOTH, expand=True)
    
    # 配置列权重，使内容整体左移
    main_frame.columnconfigure(0, weight=0)
    main_frame.columnconfigure(1, weight=1)
    
    # 文件夹选择功能 - 将Browse按钮移到Select data folder标签后面
    tk.Label(main_frame, text="Select data folder:", 
             font=("Arial", 9)).grid(row=0, column=0, pady=(3, 0), sticky="e", padx=(20, 5))
    
    folder_var = tk.StringVar(value=os.getcwd())
    
    def browse_folder():
        """浏览选择文件夹"""
        folder_path = filedialog.askdirectory(initialdir=os.getcwd(), title="Select data folder")
        if folder_path:
            folder_var.set(folder_path)
            print(f"\033[94mBrowse selected folder: {folder_path}\033[0m")  # 蓝色输出
    
    browse_button = tk.Button(main_frame, text="Browse", command=browse_folder, width=6, font=("Arial", 10))
    browse_button.grid(row=0, column=1, pady=(3, 0), sticky="w", padx=(0, 20))
    
    # 地址展示框居中显示
    folder_entry = ttk.Entry(main_frame, textvariable=folder_var, font=("Arial", 8), width=65)
    folder_entry.grid(row=1, column=0, columnspan=2, pady=(0, 5), padx=(10, 10))
    
    tk.Label(main_frame, text="Mineral:", 
             font=("Arial", 9)).grid(row=2, column=0, pady=(3, 2), sticky="w", padx=(35, 5))
    
    mineral_var = tk.StringVar(value="apatite")
    mineral_menu = ttk.Combobox(main_frame, textvariable=mineral_var, 
                               values=["apatite", "zircon"], 
                               state="readonly", font=("Arial", 9), width=8, justify="center")
    mineral_menu.grid(row=2, column=1, pady=(3, 2), sticky="w", padx=(0, 20))
    
    # zeta参数输入 - 整体右移一点
    tk.Label(main_frame, text="Zeta:", 
             font=("Arial", 9)).grid(row=3, column=0, pady=(2, 2), sticky="w", padx=(35, 5))
    
    zeta_var = tk.StringVar(value="390")
    zeta_entry = ttk.Entry(main_frame, textvariable=zeta_var, font=("Arial", 9), width=8, justify="center")
    zeta_entry.grid(row=3, column=1, pady=(2, 2), sticky="w", padx=(0, 20))
    
    # rho-d参数输入 - 整体右移一点
    tk.Label(main_frame, text="Rho-d:", 
             font=("Arial", 9)).grid(row=4, column=0, pady=(2, 2), sticky="w", padx=(35, 5))
    
    rho_d_var = tk.StringVar(value="1.322E6")
    rho_d_entry = ttk.Entry(main_frame, textvariable=rho_d_var, font=("Arial", 9), width=8, justify="center")
    rho_d_entry.grid(row=4, column=1, pady=(2, 2), sticky="w", padx=(0, 20))
    
    # 状态标签 - 减少间距
    status_label = tk.Label(main_frame, text="", font=("Arial", 8), fg="red")
    status_label.grid(row=5, column=0, columnspan=2, pady=(2, 2), padx=(35, 20))
    
    def update_defaults(*args):
        """根据矿物类型更新默认值"""
        mineral_type = mineral_var.get()
        if mineral_type == "zircon":
            zeta_var.set("112")
            rho_d_var.set("0.45E6")
        else:  # apatite
            zeta_var.set("390")
            rho_d_var.set("1.322E6")
    
    # 绑定矿物类型变化事件
    mineral_var.trace('w', update_defaults)
    
    def validate_parameters():
        """验证参数范围"""
        mineral_type = mineral_var.get()
        zeta_value = zeta_var.get()
        rho_d_value = rho_d_var.get()
        
        try:
            zeta = float(zeta_value)
            rho_d = float(rho_d_value.replace('E', 'e'))
            
            if mineral_type == "zircon":
                if zeta < 100 or zeta > 130:
                    status_label.config(text="Please use a reasonable zeta value (100-130)")
                    return False
                if rho_d < 0.1e6 or rho_d > 1e6:
                    status_label.config(text="Please use a reasonable rho-d value (0.1E6 - 1E6)")
                    return False
            else:  # apatite
                if zeta < 340 or zeta > 400:
                    status_label.config(text="Please use a reasonable zeta value (340-400)")
                    return False
                if rho_d < 0.8e6 or rho_d > 1.8e6:
                    status_label.config(text="Please use a reasonable rho-d value (0.8E6 - 1.8E6)")
                    return False
            
            status_label.config(text="")
            return True
        except ValueError:
            status_label.config(text="Please enter valid numeric values")
            return False
    
    def confirm_selection():
        """确认选择并禁用所有输入控件"""
        if validate_parameters():
            result['folder'].set(folder_var.get())
            result['mineral'].set(mineral_var.get())
            result['zeta'].set(zeta_var.get())
            result['rho_d'].set(rho_d_var.get())
             
            # 退出主循环，让程序继续执行，但窗口保持打开
            root.quit()  # 恢复退出主循环
            root.destroy()  # 保持注释，不销毁窗口
    
    # 创建OK按钮 - 减少间距
    ok_button = ttk.Button(main_frame, text="OK", command=confirm_selection)
    ok_button.grid(row=6, column=0, columnspan=2, pady=(3, 0), padx=(25, 20))
    
    # 设置焦点到下拉菜单
    mineral_menu.focus_set()
    
    # 绑定回车键到确认按钮
    root.bind('<Return>', lambda event: confirm_selection())
    
    # 绑定窗口关闭事件
    root.protocol("WM_DELETE_WINDOW", confirm_selection)
    
    # 启动主循环
    # 启动主循环
    root.mainloop()
    
    return {
        'folder': result['folder'].get(),
        'mineral': result['mineral'].get(),
        'zeta': float(result['zeta'].get()),
        'rho_d': float(result['rho_d'].get().replace('E', 'e'))
    }

# 调用下拉选择窗口
mineral_params = select_mineral()
foldername1 = mineral_params['folder']
mineral = mineral_params['mineral']
zeta = mineral_params['zeta']
rho_d = mineral_params['rho_d']
print(f"Selected folder: {foldername1}")
print(f"Selected mineral type: {mineral}")
print(f"Zeta value: {zeta}")
print(f"Rho-d value: {rho_d}")

# read data from selected folder
spotsize = 25
radialplot_width = 300
radialplot_height = 300
radialplot_res = 100
csv_files1 = read_csv_files_from_folder(foldername1)
file_count = len(csv_files1)
print(f"共读取到 {file_count} 个CSV文件")

# 初始化参数为NaN值
nan_array = [np.nan] * file_count
mediumNS = nan_array.copy()
totalNS = nan_array.copy()
ngrains = nan_array.copy()
pooledage4LAICPMS = nan_array.copy()
pooledage_err4LAICPMS = nan_array.copy()
pooledU4LAICPMS = nan_array.copy()
pooledU_err4LAICPMS = nan_array.copy()
U_mean4LAICPMS = nan_array.copy()
U_std4LAICPMS = nan_array.copy()
pooledage4pseudoEDM = nan_array.copy()
pooledage_err4pseudoEDM = nan_array.copy()
pooledage4pseudoEDM_wighted = nan_array.copy()
pooledage_err4pseudoEDM_wighted = nan_array.copy()
Samples = [None] * file_count

dispers = nan_array.copy()
dispers_se = nan_array.copy()
mswds = nan_array.copy()
centerages = nan_array.copy()
centerages_se = nan_array.copy()
pooled_age = nan_array.copy()
pooled_age_se = nan_array.copy()
pvalues = nan_array.copy()
BH_used = [None] * file_count

pooled_age2 = nan_array.copy()
pooled_age_se2 = nan_array.copy()
dispers2 = nan_array.copy()
dispers_se2 = nan_array.copy()
mswds2 = nan_array.copy()
centerages2 = nan_array.copy()
centerages_se2 = nan_array.copy()
pvalues2 = nan_array.copy()
BH_used2 = [None] * file_count
minerals = nan_array.copy()

i=0
for j in csv_files1:
    print(f"processing file: {j}")
    minerals[i] = mineral
    df = csv_files1[j]
    if 'Area' in df.columns:
        df = df.rename(columns={'Area': 'A'})
    u_cols = [col for col in df.columns if (col.startswith('U') and 
                                          col[1:].isdigit() and 
                                          not any(s in col.lower() for s in ['err']))]
    if u_cols:
        df['U_log_mean'] = df[u_cols].apply(lambda x: np.log(x.dropna())).mean(axis=1)
        df['U_log_std'] = df[u_cols].apply(lambda x: np.log(x.dropna())).std(axis=1)
        df['U_mean'] = np.exp(df['U_log_mean'])
        df['U_std'] = np.exp(df['U_log_std'])
        # print(df['U_mean'])
    df['U_std'] = df['U_std'].fillna(df['U1err'])
    df['U_mean'] = df['U_mean']
    df['U_std'] = df['U_std']
    df['A'] = df['A']  # in micrometer square
    # 去除Sample列
    if 'GrainID' in df.columns:
        df = df.drop(columns=['GrainID'])
    df = df[['Ns', 'A', 'U_mean', 'U_std']]
    df.columns = ['Ns', 'A', 'U1', 'U1err']
    mediumNS[i] = np.median(df['Ns'])
    totalNS[i] = np.sum(df['Ns'])
    ngrains[i] = len(df)
    pooledage4LAICPMS_i, pooledage_err4LAICPMS_i, pooled_U_i, pooled_U_err_i, U_mean_i, U_std_i = calc_pooledage4LAICPMS(df, mineral_type=mineral)
    # print(pooledage4LAICPMS_i, pooledage_err4LAICPMS_i)
    # single_ages, single_error = calc_singleage4LAICPMS(df, mineral_type=mineral)
    # print(single_ages, single_error)
    pooledage4LAICPMS[i] = pooledage4LAICPMS_i
    pooledage_err4LAICPMS[i] = pooledage_err4LAICPMS_i
    pooledU4LAICPMS[i] = pooled_U_i
    pooledU_err4LAICPMS[i] = pooled_U_err_i
    U_mean4LAICPMS[i] = U_mean_i
    U_std4LAICPMS[i] = U_std_i    
    df2 = df.copy()
    df2['Ni'] = NIfromUnA(df2['U1'].values, df2['A'].values, mineral_type=mineral,Zeta=zeta,RhoD=rho_d)
    # 去除Sample列
    df2 = df2.drop(columns=['U1','U1err'])
    # print(df2)
    pooledage4pseudoEDM_i, pooledage_err4pseudoEDM_i, pooledage4pseudoEDM_wighted_i, pooledage_err4pseudoEDM_wighted_i = calc_pooledage4pseudoEDM(df2, mineral_type=mineral,Zeta=zeta,RhoD=rho_d)
    pooledage4pseudoEDM[i] = pooledage4pseudoEDM_i
    pooledage_err4pseudoEDM[i] = pooledage_err4pseudoEDM_i
    pooledage4pseudoEDM_wighted[i] = pooledage4pseudoEDM_wighted_i
    pooledage_err4pseudoEDM_wighted[i] = pooledage_err4pseudoEDM_wighted_i
    Samples[i] = j

    csv_file = 'temp.csv'
                # 写入表头数据
    with open(csv_file, 'w') as f:
        # 写入表头
        f.write(f"mineral,,,\n")
        f.write(f"{mineral},,,\n")
        f.write(f"spotsize,,,\n")
        f.write(f"{spotsize},,,\n")
        f.write(f"Ns,A,U1,U1err\n")
        # 写入数据行
        for _, row in df.iterrows():
            f.write(f"{row['Ns']},{row['A']},{row['U1']},{row['U1err']}\n")
    #打开R图形设备
    radiaplot_pic_name = f'{foldername1}/{j}.png'
    ro.r(f'png(file = "{radiaplot_pic_name}", width = {radialplot_width}, height = {radialplot_height}, res = {radialplot_res})')
    data = isoplotR.read_data(csv_file,method='fissiontracks',format=3)
    
    isoplotR.radialplot(x=data,oerr = 1)
    centralages = isoplotR.central(x=data,oerr = 1)
    # 关闭R图形设备
    ro.r('dev.off()')
    
    # 删除临时文件csv_file
    if os.path.exists(csv_file):
        os.remove(csv_file)
        print(f"已删除临时文件: {csv_file}")

    # print(df)
    # data22 = np.column_stack((single_ages, single_error))
    # print(data22)
    # centralages3 = central(x=data22,oerr = 1)
    # print("this is the centralage2: ",centralages3)
    mswd = centralages[1][0]
    pvalue = centralages[2][0]
    centerage = centralages[3][0]
    centerage_se = centralages[3][1]
    disper = centralages[-1][0]*100
    disper_se = centralages[-1][1]*100
    dispers[i] = disper
    dispers_se[i] = disper_se
    mswds[i] = mswd
    centerages[i] = centerage
    centerages_se[i] = centerage_se
    pvalues[i] = pvalue
    BH_used[i] = Samples

    csv_file2 = 'temp2.csv'
                # 写入表头数据
    with open(csv_file2, 'w') as f:
        if mineral == 'apatite':
            # 写入表头
            f.write(f"zeta,err\n")
            f.write(f"{zeta},{0.0001}\n")
            f.write(f"rhoD,err\n")
            f.write(f"{rho_d},{10000}\n")
            f.write(f"Ns,Ni\n")
        elif mineral == 'zircon':
             # 写入表头
            f.write(f"zeta,err\n")
            f.write(f"{zeta},{2.5}\n")
            f.write(f"rhoD,err\n")
            f.write(f"{rho_d},{1000}\n")
            f.write(f"Ns,Ni\n")
        # 写入数据行
        for _, row in df2.iterrows():
            f.write(f"{row['Ns']},{row['Ni']}\n")
    #打开R图形设备
    radiaplot_pic_name2 = f'{foldername1}/{j}_pseudoEDM.png'
    try:
        ro.r(f'png(file = "{radiaplot_pic_name2}", width = {radialplot_width}, height = {radialplot_height}, res = {radialplot_res})')
        data2 = isoplotR.read_data(csv_file2,method='fissiontracks',format=1)
        centralages2 = isoplotR.central(x=data2,oerr = 1)
        # print(centralages2)
        # print(df2)
        isoplotR.radialplot(x=data2,oerr = 1)
        mswd2 = centralages2[1][0]
        pvalue2 = centralages2[2][0]
        centerage2 = centralages2[3][0]
        centerage_se2 = centralages2[3][1]
        disper2 = centralages2[-1][0]*100
        disper_se2 = centralages2[-1][1]*100
        # pooled_age2[i] = pooled2)  # 修改为使用pooled2
        # pooled_age_se2[i] = pooledsigma2)  # 修改为使用pooledsigma2
        dispers2[i] = disper2
        dispers_se2[i] = disper_se2
        mswds2[i] = mswd2
        centerages2[i] = centerage2
        centerages_se2[i] = centerage_se2
        pvalues2[i] = pvalue2
        # BH_used2[i] = item)
        i = i +1
        # 删除临时文件csv_file2
        if os.path.exists(csv_file2):
            os.remove(csv_file2)
            print(f"已删除临时文件: {csv_file2}")
    except Exception as e:
        print(f"处理文件 {i} 时出错: {str(e)}")
        i = i +1
        continue  # 跳过当前循环进入下一个
    finally:
        ro.r('dev.off()')
age_results = pd.DataFrame({'ID':Samples,'Pooled_ICPMS_age':pooledage4LAICPMS,'Pooled_ICPMS_age_1se':pooledage_err4LAICPMS,
                            'pooledU4LAICPMS':pooledU4LAICPMS, 'pooledU_err4LAICPMS':pooledU_err4LAICPMS,'U_mean4LAICPMS':U_mean4LAICPMS,
                            'U_std4LAICPMS':U_std4LAICPMS,
                            'pooledage4pseudoEDM':pooledage4pseudoEDM,'pooledage_err4pseudoEDM':pooledage_err4pseudoEDM,
                            'central_ICPMSage':centerages,'central_ICPMSage_err':centerages_se,
                            'central_pseudoEDMage':centerages2,'central_pseudoEDMage_err':centerages_se2,
                            'p_value_ICPMS':pvalues,'Dispersion_ICPMS %':dispers,'Dispersion_1se_ICPMS %':dispers_se,
                            'p_value_pseudoEDM':pvalues2,'Dispersion_pseudoEDM %':dispers2,'Dispersion_1se_pseudoEDM %':dispers_se2,'mediumNS':mediumNS,'totalNS':totalNS,'ngrains':ngrains,'mineral':minerals})
age_results.to_excel(f'{foldername1}/ages_results.xlsx',index=False)

# 绘制LA-ICPMS与pseudo-EDM方法对比图
plt.figure(figsize=(10, 9))
plt.subplot(3, 3, 1)

# 绘制散点图
plt.errorbar(pooledage4LAICPMS, pooledage4pseudoEDM, 
             xerr=pooledage_err4LAICPMS, yerr=pooledage_err4pseudoEDM,
             fmt='o', color='blue', ecolor='lightgray',
             capsize=0, alpha=0.5)
# plt.errorbar(pooledage4LAICPMS, pooledage4pseudoEDM_wighted, 
#              xerr=pooledage_err4LAICPMS, yerr=pooledage_err4pseudoEDM_wighted,
#              fmt='o', color='red', ecolor='lightgray',
#              capsize=0, alpha=0.5)

# 添加1:1参考线
max_age = max(max(pooledage4LAICPMS), max(pooledage4pseudoEDM)) * 1.1
plt.plot([0, max_age], [0, max_age], 'r--')

# 图表装饰
plt.xlabel('LA-ICPMS pooled age (Ma)')
plt.ylabel('pseudo-EDM pooled age (Ma)')
# plt.legend()
plt.grid(True, linestyle='--', alpha=0.5)


# 计算百分比差异
differences = [100*(edm-la)/la for edm, la in zip(pooledage4pseudoEDM, pooledage4LAICPMS)]
differences2 = [100*(edm-la)/la for edm, la in zip(pooledage4pseudoEDM_wighted, pooledage4LAICPMS)]
# print(differences)

plt.subplot(3, 3, 2)
plt.scatter(pooledage4LAICPMS, differences, color='blue', alpha=0.5)
# plt.scatter(pooledage4LAICPMS, differences2, color='red', alpha=0.5)
plt.xlabel('LA-ICPMS pooled age (Ma)')
plt.ylabel('Percentage difference (%)')
plt.grid(True, linestyle='--', alpha=0.5)

plt.subplot(3, 3, 4)
# 绘制散点图
plt.errorbar(pooledage4LAICPMS,centerages, 
             xerr=pooledage_err4LAICPMS, yerr=centerages_se,
             fmt='o', color='blue', ecolor='lightgray',
             capsize=0, alpha=0.5)
plt.plot([0, max_age], [0, max_age], 'r--')
plt.xlabel('LA-ICPMS pooled age (Ma)')
plt.ylabel('LA-ICPMS central age (Ma)')

differences = 100*(np.array(centerages) - np.array(pooledage4LAICPMS))/np.array(pooledage4LAICPMS)
max_disp = max(dispers)
plt.subplot(3, 3, 5)
plt.scatter(pooledage4LAICPMS, differences, color='blue', alpha=0.5)
plt.xlabel('LA-ICPMS age (Ma)')
plt.ylabel('Age diff (%)')
plt.grid(True, linestyle='--', alpha=0.5)
plt.plot([0, max_age], [0, 0], 'r--')

plt.subplot(3, 3, 6)
plt.scatter(dispers, differences, color='blue', alpha=0.5)
plt.xlabel('Dispersion (%)')
plt.ylabel('Age diff (%)')
plt.grid(True, linestyle='--', alpha=0.5)
plt.plot([0, max_disp], [0, 0], 'r--')

plt.subplot(3, 3, 7)
# 绘制散点图
plt.errorbar(pooledage4pseudoEDM,centerages2, 
             xerr=pooledage_err4pseudoEDM, yerr=centerages_se2,
             fmt='o', color='blue', ecolor='lightgray',
             capsize=0, alpha=0.5)
plt.plot([0, max_age], [0, max_age], 'r--')
plt.xlabel('pseudo-EDM pooled age (Ma)')
plt.ylabel('pseudo-EDM central age (Ma)')

differences2 = 100*(np.array(centerages2) - np.array(pooledage4pseudoEDM))/np.array(pooledage4pseudoEDM)
max_disp = max(dispers2)
plt.subplot(3, 3, 8)
plt.scatter(pooledage4pseudoEDM, differences2, color='blue', alpha=0.5)
plt.xlabel('pseudo-EDM pooled age (Ma)')
plt.ylabel('Age diff (%)')
plt.grid(True, linestyle='--', alpha=0.5)
plt.plot([0, max_age], [0, 0], 'r--')

plt.subplot(3, 3, 9)
plt.scatter(dispers2, differences2, color='blue', alpha=0.5)
plt.xlabel('Dispersion (%)')
plt.ylabel('Age diff (%)')
plt.grid(True, linestyle='--', alpha=0.5)
plt.plot([0, max_disp], [0, 0], 'r--')
plt.tight_layout()

# plt.savefig('LAICPMS_vs_pseudoEDM_comparison.png', dpi=300, bbox_inches='tight')
plt.show()
