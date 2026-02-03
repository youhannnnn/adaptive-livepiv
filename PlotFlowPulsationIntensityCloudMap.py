import os
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
from scipy.interpolate import griddata


def plot_flow_pulsation_intensity_cloud_map_cylinder(cx, cy, D, save_path):
    r = D / 2  # 半径 = 直径的一半
    # 文件路径
    avg_file_path = os.path.join(os.path.dirname(save_path), '平均结果.xlsx')
    inst_file_path = os.path.join(os.path.dirname(save_path), '分析结果.xlsx')


    # 读取平均速度数据
    avg_data = pd.read_excel(avg_file_path, header=None, names=['x', 'y', 'u_avg', 'v_avg'], engine='openpyxl')
    for col in ['x', 'y', 'u_avg', 'v_avg']:
        avg_data[col] = pd.to_numeric(avg_data[col], errors='coerce')
    avg_data.dropna(inplace=True)

    # 将平均速度从 m/s 转换为 cm/s
    avg_data['u_avg'] *= 100
    avg_data['v_avg'] *= 100

    # 读取分析结果（多组数据）
    inst_data = pd.read_excel(inst_file_path, header=None, engine='openpyxl')

    # 提取所有有效数据组
    groups = []
    col_idx = 0
    while col_idx + 4 <= inst_data.shape[1]:
        chunk = inst_data.iloc[:, col_idx:col_idx + 4]
        if chunk.iloc[:, 0].isnull().all():  # 跳过全为空的列
            col_idx += 1
            continue
        chunk.columns = ['x', 'y', 'u', 'v']
        for col in ['x', 'y', 'u', 'v']:
            chunk[col] = pd.to_numeric(chunk[col], errors='coerce')
        chunk.dropna(inplace=True)

        # 将瞬时速度从 m/s 转换为 cm/s
        chunk['u'] *= 100
        chunk['v'] *= 100

        groups.append(chunk)
        col_idx += 5  # 每四列一组，跳过一个空列

    # 合并所有瞬时数据为一个DataFrame，按(x, y)聚合所有u和v
    points = avg_data[['x', 'y']].values
    us_list = []
    vs_list = []

    for df in groups:
        merged = pd.merge(df, avg_data, on=['x', 'y'], how='inner')
        merged['u_prime'] = merged['u'] - merged['u_avg']  # 已是 cm/s
        merged['v_prime'] = merged['v'] - merged['v_avg']
        us_list.append(merged['u_prime'].values)
        vs_list.append(merged['v_prime'].values)

    # 转换为numpy数组：形状为 (n_points, n_groups)
    us_array = np.array(us_list).T
    vs_array = np.array(vs_list).T

    # 计算脉动强度（RMS），结果单位是 cm/s
    u_rms = np.sqrt(np.mean(us_array ** 2, axis=1))
    v_rms = np.sqrt(np.mean(vs_array ** 2, axis=1))

    # 定义等间距的目标网格
    nx, ny = 200, 200
    x_min, x_max = avg_data['x'].min(), avg_data['x'].max()
    y_min, y_max = avg_data['y'].min(), avg_data['y'].max()

    xi = np.linspace(x_min, x_max, nx)
    yi = np.linspace(y_min, y_max, ny)
    Xi, Yi = np.meshgrid(xi, yi)

    # 插值到新网格
    u_rms_interp = griddata(points, u_rms, (Xi, Yi), method='linear')
    v_rms_interp = griddata(points, v_rms, (Xi, Yi), method='linear')

    # 替换 NaN 为 0
    u_rms_interp = np.nan_to_num(u_rms_interp)
    v_rms_interp = np.nan_to_num(v_rms_interp)

    # 创建遮罩（圆柱内部）
    mask = (Xi - cx) ** 2 + (Yi - cy) ** 2 <= r ** 2
    u_rms_interp[mask] = np.nan
    v_rms_interp[mask] = np.nan

    # 坐标归一化
    Xi_normalized = (Xi - cx) / D
    Yi_normalized = (Yi - cy) / D

    # 绘图设置
    aspect_ratio = (x_max - x_min) / (y_max - y_min)
    fig_width = 8
    fig_height = fig_width / aspect_ratio
    plt.figure(figsize=(fig_width*1.1, fig_height))

    # 绘制脉动强度云图（例如 u 方向）
    contour = plt.contourf(Xi_normalized, Yi_normalized, u_rms_interp, cmap='RdBu_r', levels=150)
    cbar = plt.colorbar(contour, label='Streamwise Fluctuation Intensity (cm/s)')
    # cbar.set_ticks(np.linspace(np.nanmin(u_rms_interp), np.nanmax(u_rms_interp), 6))
    # 修改刻度格式
    ticks = np.linspace(np.nanmin(u_rms_interp), np.nanmax(u_rms_interp), 6)
    cbar.set_ticks(ticks)
    cbar.set_ticklabels([f"{t:.2f}" for t in ticks])

    # 绘制圆柱边界
    circle = plt.Circle((0, 0), 0.5, color='k', fill=False, lw=2, linestyle='--')
    plt.gca().add_patch(circle)

    # 设置坐标轴比例一致
    plt.xlim((x_min - cx) / D, (x_max - cx) / D)
    plt.ylim((y_min - cy) / D, (y_max - cy) / D)
    plt.gca().set_aspect('equal', adjustable='box')

    plt.xlabel('X/D')
    plt.ylabel('Y/D')
    # plt.title('Streamwise Turbulence Intensity')
    plt.tight_layout()

    # 保存图像
    save_file = save_path + '流向脉动强度云图.png'
    plt.savefig(save_file, dpi=300, bbox_inches='tight')
    plt.show()


def plot_flow_pulsation_intensity_cloud_map_rectangle(cx, cy, T, H, save_path):
    # 文件路径
    avg_file_path = os.path.join(os.path.dirname(save_path), '平均结果.xlsx')
    inst_file_path = os.path.join(os.path.dirname(save_path), '分析结果.xlsx')

    # 读取平均速度数据
    avg_data = pd.read_excel(avg_file_path, header=None, names=['x', 'y', 'u_avg', 'v_avg'], engine='openpyxl')
    for col in ['x', 'y', 'u_avg', 'v_avg']:
        avg_data[col] = pd.to_numeric(avg_data[col], errors='coerce')
    avg_data.dropna(inplace=True)

    # 将平均速度从 m/s 转换为 cm/s
    avg_data['u_avg'] *= 100
    avg_data['v_avg'] *= 100

    # 读取分析结果（多组数据）
    inst_data = pd.read_excel(inst_file_path, header=None, engine='openpyxl')

    # 提取所有有效数据组
    groups = []
    col_idx = 0
    while col_idx + 4 <= inst_data.shape[1]:
        chunk = inst_data.iloc[:, col_idx:col_idx + 4]
        if chunk.iloc[:, 0].isnull().all():  # 跳过全为空的列
            col_idx += 1
            continue
        chunk.columns = ['x', 'y', 'u', 'v']
        for col in ['x', 'y', 'u', 'v']:
            chunk[col] = pd.to_numeric(chunk[col], errors='coerce')
        chunk.dropna(inplace=True)

        # 将瞬时速度从 m/s 转换为 cm/s
        chunk['u'] *= 100
        chunk['v'] *= 100

        groups.append(chunk)
        col_idx += 5  # 每四列一组，跳过一个空列

    # 合并所有瞬时数据为一个DataFrame，按(x, y)聚合所有u和v
    points = avg_data[['x', 'y']].values
    us_list = []
    vs_list = []

    for df in groups:
        merged = pd.merge(df, avg_data, on=['x', 'y'], how='inner')
        merged['u_prime'] = merged['u'] - merged['u_avg']  # 已是 cm/s
        merged['v_prime'] = merged['v'] - merged['v_avg']
        us_list.append(merged['u_prime'].values)
        vs_list.append(merged['v_prime'].values)

    # 转换为numpy数组：形状为 (n_points, n_groups)
    us_array = np.array(us_list).T
    vs_array = np.array(vs_list).T

    # 计算脉动强度（RMS），结果单位是 cm/s
    u_rms = np.sqrt(np.mean(us_array ** 2, axis=1))
    v_rms = np.sqrt(np.mean(vs_array ** 2, axis=1))

    # 定义等间距的目标网格
    nx, ny = 200, 200
    x_min, x_max = avg_data['x'].min(), avg_data['x'].max()
    y_min, y_max = avg_data['y'].min(), avg_data['y'].max()

    xi = np.linspace(x_min, x_max, nx)
    yi = np.linspace(y_min, y_max, ny)
    Xi, Yi = np.meshgrid(xi, yi)

    # 插值到新网格
    u_rms_interp = griddata(points, u_rms, (Xi, Yi), method='linear')
    v_rms_interp = griddata(points, v_rms, (Xi, Yi), method='linear')

    # 替换 NaN 为 0
    u_rms_interp = np.nan_to_num(u_rms_interp)
    v_rms_interp = np.nan_to_num(v_rms_interp)

    # 创建遮罩（圆柱内部）
    mask = ((cx - T/2 <= Xi) & (Xi <= cx + T/2)) & ((cy - H/2 <= Yi) & (Yi <= cy + H/2))
    u_rms_interp[mask] = np.nan
    v_rms_interp[mask] = np.nan

    # 坐标归一化
    Xi_normalized = (Xi - cx) / H
    Yi_normalized = (Yi - cy) / H

    # 绘图设置
    aspect_ratio = (x_max - x_min) / (y_max - y_min)
    fig_width = 8
    fig_height = fig_width / aspect_ratio
    plt.figure(figsize=(fig_width*1.1, fig_height))

    # 绘制脉动强度云图（例如 u 方向）
    contour = plt.contourf(Xi_normalized, Yi_normalized, u_rms_interp, cmap='RdBu_r', levels=150)
    cbar = plt.colorbar(contour, label='Streamwise Fluctuation Intensity (cm/s)')
    # cbar.set_ticks(np.linspace(np.nanmin(u_rms_interp), np.nanmax(u_rms_interp), 6))
    # 修改刻度格式
    ticks = np.linspace(np.nanmin(u_rms_interp), np.nanmax(u_rms_interp), 6)
    cbar.set_ticks(ticks)
    cbar.set_ticklabels([f"{t:.2f}" for t in ticks])

    # 绘制平板边界
    # 平板左下角坐标为 (cx - T/2, cy - H/2)，宽度为 T，高度为 H
    plate = plt.Rectangle(( (cx - T/2 - cx)/H, (cy - H/2 - cy)/H ),  # 归一化后的左下角坐标 (X/H, Y/H)
                          T / H,        # 宽度归一化为 H
                          H / H,        # 高度归一化为 H
                          color='k',
                          fill=False,
                          lw=2,
                          linestyle='--')
    plt.gca().add_patch(plate)

    # 设置坐标轴比例一致
    plt.xlim((x_min - cx) / H, (x_max - cx) / H)
    plt.ylim((y_min - cy) / H, (y_max - cy) / H)
    plt.gca().set_aspect('equal', adjustable='box')

    plt.xlabel('X/H')
    plt.ylabel('Y/H')
    # plt.title('Streamwise Turbulence Intensity')
    plt.tight_layout()

    # 保存图像
    save_file = save_path + '流向脉动强度云图.png'
    plt.savefig(save_file, dpi=300, bbox_inches='tight')
    plt.show()