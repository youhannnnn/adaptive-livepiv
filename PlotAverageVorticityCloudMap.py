import os
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt


def plot_vorticity_cloud_cylinder(cx, cy, D, save_path):
    # 设置圆柱参数
    r = D / 2  # 半径
    # 文件路径
    file_path = os.path.join(os.path.dirname(save_path), '分析结果.xlsx')
    # 读取Excel文件（注意 header=None）
    data_all = pd.read_excel(file_path, header=None, engine='openpyxl')

    # 提取所有列名索引（以数字命名列）
    num_cols = data_all.shape[1]

    # 存储所有涡量矩阵
    vorticity_list = []

    # 存储网格信息（假设所有组的网格一致）
    X, Y = None, None

    # 遍历每组数据（每组4列，间隔一个空列）
    i = 0
    while i < num_cols:
        # 检查是否为有效数据组（至少有4列）
        if i + 3 >= num_cols:
            break

        # 获取当前组四列数据
        group_df = data_all.iloc[:, i:i + 4]

        # 检查是否为空列（全为NaN）
        if group_df.isna().all().all():
            i += 1
            continue

        # 重命名列
        group_df.columns = ['x', 'y', 'u', 'v']

        # 强制转换所有列为数值型
        for col in ['x', 'y', 'u', 'v']:
            group_df[col] = pd.to_numeric(group_df[col], errors='coerce')
        group_df.dropna(inplace=True)

        # 数据按照x和y排序
        group_df.sort_values(['y', 'x'], inplace=True)

        # 提取x,y,u,v的2D数组
        u = group_df.pivot(index='y', columns='x', values='u').values
        v = group_df.pivot(index='y', columns='x', values='v').values

        # 获取唯一x和y值
        unique_x = group_df['x'].unique()
        unique_y = group_df['y'].unique()

        # 计算dx和dy
        dx = unique_x[1] - unique_x[0]
        dy = unique_y[1] - unique_y[0]

        # 计算涡量
        vorticity = np.gradient(v, axis=1) / dx - np.gradient(u, axis=0) / dy

        # 保存涡量
        vorticity_list.append(vorticity)

        # 构建网格（只需一次）
        if X is None or Y is None:
            X, Y = np.meshgrid(unique_x, unique_y)

        # 移动到下一组（跳过空列）
        i += 5  # 跳过本组4列 + 1个空列

    # 计算平均涡量
    average_vorticity = np.mean(vorticity_list, axis=0)

    # 创建遮罩，标记圆柱范围
    mask = (X - cx) ** 2 + (Y - cy) ** 2 <= r ** 2
    vorticity_masked = np.ma.masked_where(mask, average_vorticity)

    # 计算宽高比用于图像比例调整
    x_min, x_max = X.min(), X.max()
    y_min, y_max = Y.min(), Y.max()
    aspect_ratio = (x_max - x_min) / (y_max - y_min)
    fig_width = 8
    fig_height = fig_width / aspect_ratio

    # 无量纲化坐标
    Xi_normalized = (X - cx) / D
    Yi_normalized = (Y - cy) / D

    # 绘图
    plt.figure(figsize=(fig_width * 1.1, fig_height))
    contourf_ = plt.contourf(Xi_normalized, Yi_normalized, vorticity_masked, levels=150, cmap='RdBu_r')
    cbar = plt.colorbar(contourf_, label='Vorticity (s-1)')  # ticks=np.arange(-0.08, 0.08, 0.02)
    # cbar.set_ticks(np.linspace(np.nanmin(vorticity_masked), np.nanmax(vorticity_masked), 6))
    # 修改刻度格式
    ticks = np.linspace(np.nanmin(vorticity_masked), np.nanmax(vorticity_masked), 6)
    cbar.set_ticks(ticks)
    cbar.set_ticklabels([f"{t:.3f}" for t in ticks])

    # 绘制圆柱边界
    circle = plt.Circle((0, 0), 0.5, color='black', fill=False, lw=2, linestyle='--')
    plt.gca().add_patch(circle)

    # 设置等比例显示
    plt.xlim((x_min - cx) / D, (x_max - cx) / D)
    plt.ylim((y_min - cy) / D, (y_max - cy) / D)
    plt.gca().set_aspect('equal', adjustable='box')

    plt.xlabel('X/D')
    plt.ylabel('Y/D')
    # plt.title('Averaged Vorticity Field')
    plt.tight_layout()

    # 保存图像为PNG格式
    save_file = save_path + '平均涡量场云图.png'
    plt.savefig(save_file, dpi=300, bbox_inches='tight')

    plt.show()



# # 设置圆柱参数
# cx, cy = 7.19, 7.78  # 圆心坐标
# D = 2.2  # 圆柱直径
# r = D / 2  # 半径
#
# # 文件路径
# file_path = 'E:\\覃嘉昇研二下学期\\piv实验小论文\\圆柱绕流与平板绕流实验视频-第二次\\圆柱绕流\\1\\分析结果.xlsx'
# save_path = 'E:\\覃嘉昇研二下学期\\piv实验小论文\\圆柱绕流与平板绕流实验视频-第二次\\圆柱绕流\\1\\'
#
# # 读取Excel文件（注意 header=None）
# data_all = pd.read_excel(file_path, header=None, engine='openpyxl')
#
# # 提取所有列名索引（以数字命名列）
# num_cols = data_all.shape[1]
#
# # 存储所有涡量矩阵
# vorticity_list = []
#
# # 存储网格信息（假设所有组的网格一致）
# X, Y = None, None
#
# # 遍历每组数据（每组4列，间隔一个空列）
# i = 0
# while i < num_cols:
#     # 检查是否为有效数据组（至少有4列）
#     if i + 3 >= num_cols:
#         break
#
#     # 获取当前组四列数据
#     group_df = data_all.iloc[:, i:i + 4]
#
#     # 检查是否为空列（全为NaN）
#     if group_df.isna().all().all():
#         i += 1
#         continue
#
#     # 重命名列
#     group_df.columns = ['x', 'y', 'u', 'v']
#
#     # 强制转换所有列为数值型
#     for col in ['x', 'y', 'u', 'v']:
#         group_df[col] = pd.to_numeric(group_df[col], errors='coerce')
#     group_df.dropna(inplace=True)
#
#     # 数据按照x和y排序
#     group_df.sort_values(['y', 'x'], inplace=True)
#
#     # 提取x,y,u,v的2D数组
#     u = group_df.pivot(index='y', columns='x', values='u').values
#     v = group_df.pivot(index='y', columns='x', values='v').values
#
#     # 获取唯一x和y值
#     unique_x = group_df['x'].unique()
#     unique_y = group_df['y'].unique()
#
#     # 计算dx和dy
#     dx = unique_x[1] - unique_x[0]
#     dy = unique_y[1] - unique_y[0]
#
#     # 计算涡量
#     vorticity = np.gradient(v, axis=1) / dx - np.gradient(u, axis=0) / dy
#
#     # 保存涡量
#     vorticity_list.append(vorticity)
#
#     # 构建网格（只需一次）
#     if X is None or Y is None:
#         X, Y = np.meshgrid(unique_x, unique_y)
#
#     # 移动到下一组（跳过空列）
#     i += 5  # 跳过本组4列 + 1个空列
#
# # 计算平均涡量
# average_vorticity = np.mean(vorticity_list, axis=0)
#
# # 创建遮罩，标记圆柱范围
# mask = (X - cx) ** 2 + (Y - cy) ** 2 <= r ** 2
# vorticity_masked = np.ma.masked_where(mask, average_vorticity)
#
# # 计算宽高比用于图像比例调整
# x_min, x_max = X.min(), X.max()
# y_min, y_max = Y.min(), Y.max()
# aspect_ratio = (x_max - x_min) / (y_max - y_min)
# fig_width = 8
# fig_height = fig_width / aspect_ratio
#
# # 无量纲化坐标
# Xi_normalized = (X - cx) / D
# Yi_normalized = (Y - cy) / D
#
# # 绘图
# plt.figure(figsize=(fig_width*1.1, fig_height))
# contourf_ = plt.contourf(Xi_normalized, Yi_normalized, vorticity_masked, levels=150, cmap='RdBu_r')
# cbar = plt.colorbar(contourf_, label='Vorticity (s-1)')    # ticks=np.arange(-0.08, 0.08, 0.02)
# # cbar.set_ticks(np.linspace(np.nanmin(vorticity_masked), np.nanmax(vorticity_masked), 6))
# # 修改刻度格式
# ticks = np.linspace(np.nanmin(vorticity_masked), np.nanmax(vorticity_masked), 6)
# cbar.set_ticks(ticks)
# cbar.set_ticklabels([f"{t:.3f}" for t in ticks])
#
# # 绘制圆柱边界
# circle = plt.Circle((0, 0), 0.5, color='black', fill=False, lw=2, linestyle='--')
# plt.gca().add_patch(circle)
#
# # 设置等比例显示
# plt.xlim((x_min - cx) / D, (x_max - cx) / D)
# plt.ylim((y_min - cy) / D, (y_max - cy) / D)
# plt.gca().set_aspect('equal', adjustable='box')
#
# plt.xlabel('X/D')
# plt.ylabel('Y/D')
# # plt.title('Averaged Vorticity Field')
# plt.tight_layout()
#
# # 保存图像为PNG格式
# save_file = save_path + '平均涡量场云图.png'
# plt.savefig(save_file, dpi=300, bbox_inches='tight')
#
# plt.show()


def plot_vorticity_cloud_rectangle(cx, cy, T, H, save_path):
    file_path = os.path.join(os.path.dirname(save_path), '分析结果.xlsx')
    # 读取Excel文件（注意 header=None）
    data_all = pd.read_excel(file_path, header=None, engine='openpyxl')

    # 提取所有列名索引（以数字命名列）
    num_cols = data_all.shape[1]

    # 存储所有涡量矩阵
    vorticity_list = []

    # 存储网格信息（假设所有组的网格一致）
    X, Y = None, None

    # 遍历每组数据（每组4列，间隔一个空列）
    i = 0
    while i < num_cols:
        # 检查是否为有效数据组（至少有4列）
        if i + 3 >= num_cols:
            break

        # 获取当前组四列数据
        group_df = data_all.iloc[:, i:i + 4]

        # 检查是否为空列（全为NaN）
        if group_df.isna().all().all():
            i += 1
            continue

        # 重命名列
        group_df.columns = ['x', 'y', 'u', 'v']

        # 强制转换所有列为数值型
        for col in ['x', 'y', 'u', 'v']:
            group_df[col] = pd.to_numeric(group_df[col], errors='coerce')
        group_df.dropna(inplace=True)

        # 数据按照x和y排序
        group_df.sort_values(['y', 'x'], inplace=True)

        # 提取x,y,u,v的2D数组
        u = group_df.pivot(index='y', columns='x', values='u').values
        v = group_df.pivot(index='y', columns='x', values='v').values

        # 获取唯一x和y值
        unique_x = group_df['x'].unique()
        unique_y = group_df['y'].unique()

        # 计算dx和dy
        dx = unique_x[1] - unique_x[0]
        dy = unique_y[1] - unique_y[0]

        # 计算涡量
        vorticity = np.gradient(v, axis=1) / dx - np.gradient(u, axis=0) / dy

        # 保存涡量
        vorticity_list.append(vorticity)

        # 构建网格（只需一次）
        if X is None or Y is None:
            X, Y = np.meshgrid(unique_x, unique_y)

        # 移动到下一组（跳过空列）
        i += 5  # 跳过本组4列 + 1个空列

    # 计算平均涡量
    average_vorticity = np.mean(vorticity_list, axis=0)

    # 创建一个遮罩，标记平板内的点
    mask = ((cx - T/2 <= X) & (X <= cx + T/2)) & ((cy - H/2 <= Y) & (Y <= cy + H/2))
    vorticity_masked = np.ma.masked_where(mask, average_vorticity)

    # 计算宽高比用于图像比例调整
    x_min, x_max = X.min(), X.max()
    y_min, y_max = Y.min(), Y.max()
    aspect_ratio = (x_max - x_min) / (y_max - y_min)
    fig_width = 8
    fig_height = fig_width / aspect_ratio

    # 无量纲化坐标
    Xi_normalized = (X - cx) / H
    Yi_normalized = (Y - cy) / H

    # 绘图
    plt.figure(figsize=(fig_width*1.1, fig_height))
    contourf_ = plt.contourf(Xi_normalized, Yi_normalized, vorticity_masked, levels=150, cmap='RdBu_r')
    cbar = plt.colorbar(contourf_, label='Vorticity (s-1)')    # ticks=np.arange(-0.08, 0.08, 0.02)
    # cbar.set_ticks(np.linspace(np.nanmin(vorticity_masked), np.nanmax(vorticity_masked), 6))
    # 修改刻度格式
    ticks = np.linspace(np.nanmin(vorticity_masked), np.nanmax(vorticity_masked), 6)
    cbar.set_ticks(ticks)
    cbar.set_ticklabels([f"{t:.3f}" for t in ticks])

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

    # 设置等比例显示
    plt.xlim((x_min - cx) / H, (x_max - cx) / H)
    plt.ylim((y_min - cy) / H, (y_max - cy) / H)
    plt.gca().set_aspect('equal', adjustable='box')

    plt.xlabel('X/H')
    plt.ylabel('Y/H')
    # plt.title('Averaged Vorticity Field')
    plt.tight_layout()

    # 保存图像为PNG格式
    save_file = save_path + '平均涡量场云图.png'
    plt.savefig(save_file, dpi=300, bbox_inches='tight')

    plt.show()

