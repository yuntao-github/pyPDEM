import numpy as np

def calc_pooledage4pseudoEDM(data, mineral_type, Zeta, RhoD):
    """
    计算基于EDM方法的池年龄
    
    参数:
    data -- 包含以下列的DataFrame:
        'Ns': 裂变径迹数量
        'Ni': 诱发径迹数量
        
    返回:
    tuple -- (pooled_age, pooled_error) 池年龄(Ma)和误差
    
    计算公式:
    pooled_age = (1/α) * ln(1 + 0.5*(α*ζ*ρD*Ns/Ni)) / 1e6
    """

    
    # 物理常数
    alpha = 1.551E-10   # 衰变常数 (yr^-1)

    # assumed parameters
    if mineral_type == 'apatite':
        # RhoD = 1.322e6  # 单位 cm^-2
        ND = 5000
        # Zeta = 390  # 单位 cm^-2
        Sigma_Zeta = 0.0001
        # etchf = 0.93        # 蚀刻影响因子
        # density=4.7 #zircon density=4.65;apatite density = 3.22 g/cm^3
        # R_FT = 16.2 # average etchable range of a track, um
    elif mineral_type == 'zircon':
        # RhoD = 0.45e6  # 单位 cm^-2
        ND = 1000
        # Zeta = 115  # 单位 cm^-2
        Sigma_Zeta = 0.00001
        # etchf = 1        # 蚀刻影响因子
        # density=3.22 #zircon density=4.65;apatite density = 3.22 g/cm^3
        # R_FT = 10.6 # average etchable range of a track, um
    else:
        print("Mineral type not recognized.")

    
    # 计算总和
    Ns_SUM = data['Ns'].sum()
    Ni_SUM = data['Ni'].sum()
    

    Ns_SUM_weighted = (data['Ns']*data['A']).sum()
    Ni_SUM_weighted = (data['Ni']*data['A']).sum()

    # 计算池年龄
    pooled_age = (1 / alpha) * np.log(1 + 0.5*(alpha * Zeta * RhoD * Ns_SUM/Ni_SUM)) / 1e6
    pooled_age_wighted = (1 / alpha) * np.log(1 + 0.5*(alpha * Zeta * RhoD * Ns_SUM_weighted/Ni_SUM_weighted)) / 1e6
    
    # 计算误差
    # pooled_error = np.sqrt((Sigma_Zeta/Zeta)**2 + (1/Ns_SUM) + (1/Ni_SUM) + (1/ND)) * pooled_age
    # pooled_error_weighted = np.sqrt((Sigma_Zeta/Zeta)**2 + (1/Ns_SUM) + (1/Ni_SUM) + (1/ND)) * pooled_age_wighted
    pooled_error = np.sqrt((1/Ns_SUM) + (1/Ni_SUM)) * pooled_age
    pooled_error_weighted = np.sqrt((1/Ns_SUM) + (1/Ni_SUM)) * pooled_age_wighted
    return pooled_age, pooled_error, pooled_age_wighted, pooled_error_weighted

# 示例用法
if __name__ == "__main__":
    import pandas as pd
    
    # 测试数据
    test_data = pd.DataFrame({
        'Ns': [50, 75, 100],  # 裂变径迹数
        'Ni': [200, 300, 400]  # 诱发径迹数
    })
    
    # 计算池年龄
    age, error = calc_pooledage4pseudoEDM(test_data)
    print(f"池年龄: {age:.2f} ± {error:.2f} Ma")
