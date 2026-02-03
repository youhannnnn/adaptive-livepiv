import os
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
from scipy.interpolate import griddata

def plot_average_velocity_streamline_cylinder(cx, cy, D, save_path):
    r = D / 2  # 半径 = 直径的一半
    # 读取Excel文件
    file_path = os.path.join(os.path.dirname(save_path), '平均结果.xlsx')

    data = pd.read_excel(file_path, header=None, names=['x', 'y', 'u', 'v'], engine='openpyxl')

    # 强制转换所有列为数值型
    for col in ['x', 'y', 'u', 'v']:
        data[col] = pd.to_numeric(data[col], errors='coerce')
    data.dropna(inplace=True)

    # 计算速度大小
    data['speed'] = np.sqrt(data['u']**2 + data['v']**2)

    # 提取原始坐标和速度分量
    points = data[['x', 'y']].values
    us = data['u'].values
    vs = data['v'].values
    speeds = data['speed'].values

    # 定义等间距的目标网格
    nx, ny = 200, 200  # 网格分辨率（更高分辨率使遮罩更平滑）
    x_min, x_max = data['x'].min(), data['x'].max()
    y_min, y_max = data['y'].min(), data['y'].max()

    xi = np.linspace(x_min, x_max, nx)
    yi = np.linspace(y_min, y_max, ny)
    Xi, Yi = np.meshgrid(xi, yi)

    # 使用线性插值到新网格
    Ui = griddata(points, us, (Xi, Yi), method='linear')
    Vi = griddata(points, vs, (Xi, Yi), method='linear')
    Speedi = griddata(points, speeds, (Xi, Yi), method='linear')

    # 替换 NaN 为 0（对于插值边界）
    Ui = np.nan_to_num(Ui)
    Vi = np.nan_to_num(Vi)

    # 创建一个遮罩，标记圆柱内的点
    mask = (Xi - cx)**2 + (Yi - cy)**2 <= r**2

    # 将圆柱内部的速度设为 0
    Ui[mask] = 0
    Vi[mask] = 0

    # 调整坐标轴和速度单位
    Xi_normalized = (Xi - cx) / D
    Yi_normalized = (Yi - cy) / D
    Ui_cm_s = Ui * 100  # 将 m/s 转换为 cm/s
    Vi_cm_s = Vi * 100
    Speedi_cm_s = Speedi * 100

    # 绘图
    aspect_ratio = (x_max - x_min) / (y_max - y_min)
    fig_width = 8
    fig_height = fig_width / aspect_ratio
    plt.figure(figsize=(fig_width*1.1, fig_height))

    # 流速云图（使用遮罩）
    Speedi_masked = np.ma.masked_where(mask, Speedi_cm_s)
    contour = plt.contourf(Xi_normalized, Yi_normalized, Speedi_masked, cmap='RdBu_r', levels=150)
    cbar = plt.colorbar(contour, label='Velocity (cm/s)')  #ticks=np.arange(0, 3.80, 0.5)
    # cbar.set_ticks(np.linspace(np.nanmin(Speedi_masked), np.nanmax(Speedi_masked), 6))
    # 修改刻度格式
    ticks = np.linspace(np.nanmin(Speedi_masked), np.nanmax(Speedi_masked), 6)
    cbar.set_ticks(ticks)
    cbar.set_ticklabels([f"{t:.2f}" for t in ticks])

    # 流线图
    stream = plt.streamplot(Xi_normalized, Yi_normalized, Ui_cm_s, Vi_cm_s,
                            color='black',
                            density=1.5,
                            linewidth=1.2,
                            arrowsize=1,
                            arrowstyle='-|>',
                            minlength=0.3,  # 减少最小长度
                            maxlength=10.0,  # 增加最大长度
                            integration_direction='both')

    # 绘制圆柱边界
    circle = plt.Circle((0, 0), 0.5, color='k', fill=False, lw=2, linestyle='--')
    plt.gca().add_patch(circle)

    # 设置坐标轴比例一致
    plt.xlim((x_min - cx) / D, (x_max - cx) / D)
    plt.ylim((y_min - cy) / D, (y_max - cy) / D)
    plt.gca().set_aspect('equal', adjustable='box')

    plt.xlabel('X/D')
    plt.ylabel('Y/D')
    # plt.title('Average Velocity Field')
    plt.tight_layout()

    # 保存图像为PNG格式
    save_file = save_path + '速度流线图.png'
    plt.savefig(save_file, dpi=300, bbox_inches='tight')

    plt.show()

def plot_average_velocity_streamline_rectangle(cx, cy, T, H, save_path):
    # 读取Excel文件
    file_path = os.path.join(os.path.dirname(save_path), '平均结果.xlsx')
    data = pd.read_excel(file_path, header=None, names=['x', 'y', 'u', 'v'], engine='openpyxl')

    # 强制转换所有列为数值型
    for col in ['x', 'y', 'u', 'v']:
        data[col] = pd.to_numeric(data[col], errors='coerce')
    data.dropna(inplace=True)

    # 计算速度大小
    data['speed'] = np.sqrt(data['u']**2 + data['v']**2)

    # 提取原始坐标和速度分量
    points = data[['x', 'y']].values
    us = data['u'].values
    vs = data['v'].values
    speeds = data['speed'].values

    # 定义等间距的目标网格
    nx, ny = 200, 200  # 网格分辨率（更高分辨率使遮罩更平滑）
    x_min, x_max = data['x'].min(), data['x'].max()
    y_min, y_max = data['y'].min(), data['y'].max()

    xi = np.linspace(x_min, x_max, nx)
    yi = np.linspace(y_min, y_max, ny)
    Xi, Yi = np.meshgrid(xi, yi)

    # 使用线性插值到新网格
    Ui = griddata(points, us, (Xi, Yi), method='linear')
    Vi = griddata(points, vs, (Xi, Yi), method='linear')
    Speedi = griddata(points, speeds, (Xi, Yi), method='linear')

    # 替换 NaN 为 0（对于插值边界）
    Ui = np.nan_to_num(Ui)
    Vi = np.nan_to_num(Vi)

    # 创建一个遮罩，标记平板内的点
    mask = ((cx - T/2 <= Xi) & (Xi <= cx + T/2)) & ((cy - H/2 <= Yi) & (Yi <= cy + H/2))

    # 将平板内部的速度设为 0
    Ui[mask] = 0
    Vi[mask] = 0

    # 调整坐标轴和速度单位
    Xi_normalized = (Xi - cx) / H
    Yi_normalized = (Yi - cy) / H
    Ui_cm_s = Ui * 100  # 将 m/s 转换为 cm/s
    Vi_cm_s = Vi * 100
    Speedi_cm_s = Speedi * 100

    # 绘图
    aspect_ratio = (x_max - x_min) / (y_max - y_min)
    fig_width = 8
    fig_height = fig_width / aspect_ratio
    plt.figure(figsize=(fig_width*1.1, fig_height))

    # 流速云图（使用遮罩）
    Speedi_masked = np.ma.masked_where(mask, Speedi_cm_s)
    contour = plt.contourf(Xi_normalized, Yi_normalized, Speedi_masked, cmap='RdBu_r', levels=150)
    cbar = plt.colorbar(contour, label='Velocity (cm/s)')  #ticks=np.arange(0, 3.80, 0.5)
    # cbar.set_ticks(np.linspace(np.nanmin(Speedi_masked), np.nanmax(Speedi_masked), 6))
    # 修改刻度格式
    ticks = np.linspace(np.nanmin(Speedi_masked), np.nanmax(Speedi_masked), 6)
    cbar.set_ticks(ticks)
    cbar.set_ticklabels([f"{t:.2f}" for t in ticks])

    # 流线图
    stream = plt.streamplot(Xi_normalized, Yi_normalized, Ui_cm_s, Vi_cm_s, color='black', density=1.5, linewidth=1)

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
    # plt.title('Average Velocity Field')
    plt.tight_layout()

    # 保存图像为PNG格式
    save_file = save_path + '速度流线图.png'
    plt.savefig(save_file, dpi=300, bbox_inches='tight')

    plt.show()

# 示例调用
# plot_average_velocity_streamline_cylinder(cx=5.551450303, cy=4.804212818, D=0.9204411381 * 2, save_path='E:/覃嘉昇研三上学期/piv软件中文核心论文/圆柱绕流实验数据/vivo拍摄Re=100/Open_PIV_results_76_Test')
# plot_average_velocity_streamline_cylinder(cx=5.55450303, cy=4.874212818, D=0.9084411381 * 2, save_path='E:/覃嘉昇研三上学期/piv软件中文核心论文/圆柱绕流实验数据/vivo拍摄Re=200/Open_PIV_results_76_Test')
# plot_average_velocity_streamline_cylinder(cx=5.51450303, cy=4.684212818, D=0.9204411381 * 2, save_path='E:/覃嘉昇研三上学期/piv软件中文核心论文/圆柱绕流实验数据/vivo拍摄Re=300/Open_PIV_results_76_Test')
# plot_average_velocity_streamline_cylinder(cx=5.51450303, cy=4.714212818, D=0.9204411381 * 2, save_path='E:/覃嘉昇研三上学期/piv软件中文核心论文/圆柱绕流实验数据/vivo拍摄Re=400/Open_PIV_results_76_Test')



