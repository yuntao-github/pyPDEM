import numpy as np

def NIfromUnA(Uppm_matrix, A_um2,mineral_type,Zeta,RhoD):
    """
    根据U含量和表面面积计算裂变径迹数量
    
    参数:
    Uppm_matrix -- U含量矩阵 (ppm), 可以是单个数值、列表或numpy数组
    A_um2 -- 表面面积矩阵 (μm²),可以是单个数值、列表或numpy数组
    
    返回:
    NI -- 裂变径迹数量数组 (numpy数组)
    
    计算公式:
    NI = round((Uppm/138.818) * RhoD * RhoI_C * A_um2 * 1e-4)
    其中:
    RhoD = 1.322e6 cm^-2
    RhoI_C = 1.495e-3
    """
    # 假设参数
    if mineral_type == 'apatite':
        # RhoD = 1.322e6  # 单位 cm^-2
        ND = 5000
        # Zeta = 390  # 单位 cm^-2
        Sigma_Zeta = 0.0001
        density=3.22 #zircon density=4.65;apatite density = 3.22 g/cm^3
        R_FT = 16.2 # average etchable range of a track, um
        etchf = 0.93   # 蚀刻影响因子
    elif mineral_type == 'zircon':
        # RhoD = 0.45E6  # 单位 cm^-2
        ND = 1000
        # Zeta = 115  # 单位 cm^-2
        Sigma_Zeta = 0.00001
        density=4.7 #zircon density=4.65;apatite density = 3.22 g/cm^3
        R_FT = 10.6 # average etchable range of a track, um
        etchf = 1   # 蚀刻影响因子
    else:
        print("Mineral type not recognized.")

    # other parameters
    Flambda=8.5e-17 #fission decay constant#
    NA=6.022e23 #Avogadro�s number
    UM=238.051 #Mole mass of 238U
    gi = 0.25  # geometric factor
    de = 1 #is the detection efficiency

    # 输入参数标准化处理
    if isinstance(Uppm_matrix, (int, float)):
        Uppm_matrix = np.array([Uppm_matrix])
    if isinstance(A_um2, (int, float)):
        A_um2 = np.array([[A_um2]])
    
    # 常数参数
    
    NIper_unitvolume_perppm = Flambda *Zeta * RhoD *density * 1e-6 / UM * NA; # ni per unit volume per ppm, N/cm^3/ppm
    # print('NIper_unitvolume_perppm:', NIper_unitvolume_perppm)
    # 计算裂变径迹数量
    NI = Uppm_matrix*137.818/138.818*NIper_unitvolume_perppm * gi * R_FT/(1e4) * de * A_um2 / (1e8) * etchf 
    NI = np.where(np.isfinite(NI), np.round(NI), np.nan)
    NI[NI == 0] = 1  # 将0值改为1
    return NI.reshape(-1, 1)

# 示例用法
if __name__ == "__main__":
    # 测试数据
    U_content = [10, 20, 30]  # ppm
    surface_area = [1000, 2000, 3000]  # μm²
    
    # 计算裂变径迹数量
    result = NIfromUnA(U_content, surface_area,'apatite')
    print("计算的裂变径迹数量:")
    print(result)
