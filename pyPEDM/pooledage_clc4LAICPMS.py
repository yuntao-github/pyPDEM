import numpy as np

def calc_pooledage4LAICPMS(data, mineral_type):
    """
    计算基于LA-ICPMS数据的池年龄
    
    参数:
    data -- 包含以下列的DataFrame:
        'U1': U含量 (ppm)
        'U1err': U含量误差 (ppm)
        'A': 面积 (μm²)
        'Ns': 裂变径迹数量
        
    返回:
    tuple -- (pooled_age, pooled_error) 池年龄(Ma)和误差
    
    计算公式:
    pooled_age = (1/alpha) * ln(1 + (alpha*Ns*M*1e6) / (fission*Na*U*A*d*R*g*l*etchf)) / 1e6
    """
    # 检查输入数据是否包含所需列
    required_columns = ['U1', 'U1err', 'A', 'Ns']
    required_columns2 = ['U_mean', 'U_std', 'A', 'Ns']
    if not all(col in data.columns for col in required_columns) and not all(col in data.columns for col in required_columns2):
        raise ValueError(f"输入数据必须包含以下列: {required_columns} 或 {required_columns2}")
    
    if mineral_type == 'apatite':
        d = 3.22            # 矿物密度 (g/cm^3)
        R = 0.00081         # 径迹长度 (cm)
        etchf = 0.93        # 蚀刻影响因子
    elif mineral_type == 'zircon':
        d = 4.7             # 矿物密度 (g/cm^3)
        R = 0.00053         # 径迹长度 (cm)
        etchf = 1           # 蚀刻影响因子
    else:
        print("Mineral type not recognized.")
        
    # 物理常数
    fission = 8.5E-17  # #fission decay constant#
    alpha = 1.55125E-10   # 衰变常数 (yr^-1)
    Na = 6.022E+23      # 阿伏伽德罗常数 (atoms/mol)
    l = 1               # 长度单位转换因子
    M = 238.029         # U-238的摩尔质量 (g/mol)
    g = 1               # 几何影响因子
    q = 1               # 观察因子
    U238_235ratio = 137.818  # 238U/235U比值

    
    # 预处理面积数据 (转换为cm²)
    
    data2 = data.copy()
    data2.columns = ['Ns', 'A', 'U', 'U_err']
    # 计算加权平均U含量和误差
    UA = (data2['U']* U238_235ratio/(U238_235ratio+1) * data2['A']).sum()/ 1e8
    A_SUM = data2['A'].sum()/ 1e8
    errorSUM = ((data2['U_err']* U238_235ratio/(U238_235ratio+1) * data2['A'] / 1e8/ A_SUM) ** 2).sum()
    pooled_U = UA / A_SUM
    pooled_U_err = np.sqrt(errorSUM)
    U_mean = np.exp(np.mean(np.log(data2['U']* U238_235ratio/(U238_235ratio+1))))
    U_std = np.exp(np.std(np.log(data2['U']* U238_235ratio/(U238_235ratio+1))))
    # 总裂变径迹数
    Ns_SUM = data2['Ns'].sum()
    
    # 计算池年龄
    F3 = 1 / alpha
    pooled_age = F3 * np.log(1 + (alpha * (Ns_SUM / q) * M * 1e6) / 
                  (fission * Na * UA * d * R * g * l * etchf)) / 1e6
    
    # 计算误差
    pooled_error = np.sqrt((1 / Ns_SUM + (pooled_U_err / pooled_U) ** 2)) * pooled_age
    
    return pooled_age, pooled_error, pooled_U, pooled_U_err, U_mean, U_std

# 示例用法
if __name__ == "__main__":
    import pandas as pd
    
    # 测试数据
    test_data = pd.DataFrame({
        'U1': [10, 15, 20],       # ppm
        'U1err': [0.5, 0.7, 1.0], # ppm
        'A': [100, 150, 200],     # μm²
        'Ns': [50, 75, 100]       # 裂变径迹数
    })
    
    # 计算池年龄
    age, error = calc_pooledage4LAICPMS(test_data, 'apatite')
    print(f"池年龄: {age:.2f} ± {error:.2f} Ma")
