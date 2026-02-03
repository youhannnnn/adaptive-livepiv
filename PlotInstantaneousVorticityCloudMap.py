# import pandas as pd
# import numpy as np
# import matplotlib.pyplot as plt
#
# # 设置圆柱参数
# cx, cy = 7.19, 7.78  # 圆心坐标
# D = 2.2              # 圆柱直径
# r = D / 2            # 半径
#
# # 读取Excel文件
# file_path = 'E:\\覃嘉昇研二下学期\\piv实验小论文\\圆柱绕流与平板绕流实验视频-第二次\\圆柱绕流\\5\\平均结果.xlsx'
# data = pd.read_excel(file_path, header=None, names=['x', 'y', 'u', 'v'], engine='openpyxl')
#
# # 强制转换所有列为数值型
# for col in ['x', 'y', 'u', 'v']:
#     data[col] = pd.to_numeric(data[col], errors='coerce')
# data.dropna(inplace=True)
#
# # 数据按照x和y排序
# data.sort_values(['y', 'x'], inplace=True)
#
# # 提取data中的u和v的2D数组
# u = data.pivot(index='y', columns='x', values='u').values
# v = data.pivot(index='y', columns='x', values='v').values
#
# # 获取数据边界
# unique_x = data['x'].unique()
# unique_y = data['y'].unique()
# x_min = unique_x.min()
# x_max = unique_x.max()
# y_min = unique_y.min()
# y_max = unique_y.max()
#
# # 计算dx和dy
# dx = unique_x[1] - unique_x[0]
# dy = unique_y[1] - unique_y[0]
#
# # 计算涡量
# vorticity = np.gradient(v, axis=1)/dx - np.gradient(u, axis=0)/dy
#
# # 创建XY的网格
# X, Y = np.meshgrid(unique_x, unique_y)
#
# # 创建遮罩，标记圆柱范围：在圆柱内的点设为 True
# mask = (X - cx)**2 + (Y - cy)**2 <= r**2
#
# # 应用遮罩，遮盖圆柱范围内的涡量
# vorticity_masked = np.ma.masked_where(mask, vorticity)
#
# # 计算宽高比用于图像比例调整
# aspect_ratio = (x_max - x_min) / (y_max - y_min)
# fig_width = 8
# fig_height = fig_width / aspect_ratio
#
# # 调整坐标轴和速度单位
# Xi_normalized = (X - cx) / D
# Yi_normalized = (Y - cy) / D
#
# # 绘图
# plt.figure(figsize=(fig_width, fig_height))
# contourf_ = plt.contourf(Xi_normalized, Yi_normalized, vorticity_masked, levels=150, cmap='RdBu')
# plt.colorbar(contourf_, label='Vorticity ( /s)', ticks=np.arange(-0.08, 0.08, 0.02))
#
# # 绘制圆柱边界（以无量纲形式绘制）
# circle = plt.Circle((0, 0), 0.5, color='black', fill=False, lw=2, linestyle='--')
# plt.gca().add_patch(circle)
#
# # 设置等比例显示
# plt.axis('equal')
# # 将坐标轴改为 X/D, Y/D 形式
# plt.xlim((x_min - cx) / D, (x_max - cx) / D)
# plt.ylim((y_min - cy) / D, (y_max - cy) / D)
# plt.gca().set_aspect('equal', adjustable='box')
#
# plt.xlabel('X/D')
# plt.ylabel('Y/D')
# plt.title('2D Vorticity Field')
# plt.tight_layout()
# plt.show()


# import os
# import pandas as pd
# import numpy as np
# import matplotlib.pyplot as plt
#
#
# def plot_velocity_vector_cylinder(cx, cy, D, save_path, skip=1):
#     """
#     绘制圆柱绕流的瞬时速度矢量图（使用分析结果.xlsx的第一组数据）
#
#     Parameters:
#     - cx, cy: 圆柱中心坐标
#     - D: 圆柱直径
#     - save_path: 图像保存路径（不含文件名）
#     - skip: 矢量图下采样步长，控制箭头密度（例如每 skip 行/列取一个点）
#     """
#     r = D / 2  # 半径
#     file_path = os.path.join(os.path.dirname(save_path), '分析结果.xlsx')
#
#     # 读取Excel（第一组数据）
#     data_all = pd.read_excel(file_path, header=None, engine='openpyxl')
#
#     # 提取第一组四列数据
#     if data_all.shape[1] < 4:
#         raise ValueError("Excel文件中没有足够的列来构成第一组数据 (x, y, u, v)")
#
#     group_df = data_all.iloc[:, 0:4].copy()
#     group_df.columns = ['x', 'y', 'u', 'v']
#
#     # 转换为数值，去除无效行
#     for col in ['x', 'y', 'u', 'v']:
#         group_df[col] = pd.to_numeric(group_df[col], errors='coerce')
#     group_df.dropna(inplace=True)
#
#     # 排序以构建规则网格
#     group_df.sort_values(['y', 'x'], inplace=True)
#
#     # 创建网格
#     X = group_df.pivot(index='y', columns='x', values='u').columns.values
#     Y = group_df.pivot(index='y', columns='x', values='u').index.values
#     X_mesh, Y_mesh = np.meshgrid(X, Y)
#
#     # 提取 u, v 并填充到网格
#     u_grid = group_df.pivot(index='y', columns='x', values='u').values
#     v_grid = group_df.pivot(index='y', columns='x', values='v').values
#
#     # 计算速度大小用于颜色映射
#     speed = np.sqrt(u_grid ** 2 + v_grid ** 2) * 100
#
#     # 无量纲化坐标
#     Xi_normalized = (X_mesh - cx) / D
#     Yi_normalized = (Y_mesh - cy) / D
#
#     # 创建圆柱遮罩
#     mask = (X_mesh - cx) ** 2 + (Y_mesh - cy) ** 2 <= r ** 2
#     u_masked = np.ma.masked_where(mask, u_grid)
#     v_masked = np.ma.masked_where(mask, v_grid)
#     speed_masked = np.ma.masked_where(mask, speed)
#
#     # 下采样以避免箭头过于密集
#     u_plot = u_masked[::skip, ::skip]
#     v_plot = v_masked[::skip, ::skip]
#     speed_plot = speed_masked[::skip, ::skip]
#     X_plot = Xi_normalized[::skip, ::skip]
#     Y_plot = Yi_normalized[::skip, ::skip]
#
#     # 设置图形比例
#     x_min, x_max = Xi_normalized.min(), Xi_normalized.max()
#     y_min, y_max = Yi_normalized.min(), Yi_normalized.max()
#     aspect_ratio = (x_max - x_min) / (y_max - y_min)
#     fig_width = 8
#     fig_height = fig_width / aspect_ratio
#
#     # 绘图
#     plt.figure(figsize=(fig_width * 1.1, fig_height))
#     quiver = plt.quiver(X_plot, Y_plot, u_plot, v_plot,
#                         color='black', angles='xy', scale_units='xy',
#                         scale=0.022,  # 控制箭头长度（减小值 → 更长） 初始为0.06
#                         width=0.002,  # 箭头线宽（增大）
#                         headwidth=3.0,  # 箭头头部宽度
#                         headlength=4.0,  # 箭头头部长度
#                         headaxislength=5.0,  # 头部在轴上的长度
#                         pivot='mid',  # 箭头中心对齐
#                         minlength=0.1  # 最小箭头长度，避免太短的箭头变成点
#                         )
#     # 彩色刻度
#     # quiver = plt.quiver(X_plot, Y_plot, u_plot, v_plot, speed_plot,
#     #                     cmap='RdBu_r', angles='xy', scale_units='xy',
#     #                     scale=0.022,           # 控制箭头长度（减小值 → 更长） 初始为0.06
#     #                     width=0.002,         # 箭头线宽（增大）
#     #                     headwidth=3.0,       # 箭头头部宽度
#     #                     headlength=4.0,      # 箭头头部长度
#     #                     headaxislength=5.0,  # 头部在轴上的长度
#     #                     pivot='mid',         # 箭头中心对齐
#     #                     minlength=0.1        # 最小箭头长度，避免太短的箭头变成点
#     #                     )
#     # cbar = plt.colorbar(quiver, label='Velocity (cm/s)')
#     # ticks = np.linspace(np.nanmin(speed_masked), np.nanmax(speed_masked), 6)
#     # cbar.set_ticks(ticks)
#     # cbar.set_ticklabels([f"{t:.2f}" for t in ticks])
#
#     # 绘制圆柱边界（在无量纲坐标系中是圆心(0,0)，半径0.5）
#     circle = plt.Circle((0, 0), 0.5, color='black', fill=False, lw=2, linestyle='--')
#     plt.gca().add_patch(circle)
#
#     # 设置坐标轴
#     plt.xlim(x_min, x_max)
#     plt.ylim(y_min, y_max)
#     plt.gca().set_aspect('equal', adjustable='box')
#     plt.xlabel('X/D')
#     plt.ylabel('Y/D')
#     # plt.title('Instantaneous Velocity Vector Field')
#     plt.tight_layout()
#
#     # 保存图像
#     save_file = save_path + '瞬时速度矢量图.png'
#     plt.savefig(save_file, dpi=300, bbox_inches='tight')
#     plt.show()
#
# # 示例调用
# plot_velocity_vector_cylinder(cx=5.62450303, cy=5.054212818, D=0.9104411381*2, save_path='E:/覃嘉昇研三上学期/piv软件中文核心论文/圆柱绕流实验数据/vivo拍摄Re=100/Open_PIV_results_76_Test')


import os
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt


def plot_velocity_vector_cylinder(cx, cy, D, save_path, skip=1):
    """
    绘制圆柱绕流的瞬时速度矢量图（使用分析结果.xlsx的第一组数据）

    Parameters:
    - cx, cy: 圆柱中心坐标
    - D: 圆柱直径
    - save_path: 图像保存路径（不含文件名）
    - skip: 矢量图下采样步长，控制箭头密度（例如每 skip 行/列取一个点）
    """
    r = D / 2  # 半径
    file_path = os.path.join(os.path.dirname(save_path), '平均结果.xlsx')

    # 查找流场图像路径（在save_path的上一个文件夹中）
    parent_dir = os.path.dirname(save_path.rstrip('/').rstrip('\\'))
    background_image_path = None

    # 查找可能的图像文件
    for file in os.listdir(parent_dir):
        if file.lower().endswith(('.png', '.jpg', '.jpeg', '.tiff', '.bmp')):
            background_image_path = os.path.join(parent_dir, file)
            break

    # 读取Excel（第一组数据）
    data_all = pd.read_excel(file_path, header=None, engine='openpyxl')

    # 提取第一组四列数据
    if data_all.shape[1] < 4:
        raise ValueError("Excel文件中没有足够的列来构成第一组数据 (x, y, u, v)")

    group_df = data_all.iloc[:, 0:4].copy()
    group_df.columns = ['x', 'y', 'u', 'v']

    # 转换为数值，去除无效行
    for col in ['x', 'y', 'u', 'v']:
        group_df[col] = pd.to_numeric(group_df[col], errors='coerce')
    group_df.dropna(inplace=True)

    # 排序以构建规则网格
    group_df.sort_values(['y', 'x'], inplace=True)

    # 创建网格
    X = group_df.pivot(index='y', columns='x', values='u').columns.values
    Y = group_df.pivot(index='y', columns='x', values='u').index.values
    X_mesh, Y_mesh = np.meshgrid(X, Y)

    # 提取 u, v 并填充到网格
    u_grid = group_df.pivot(index='y', columns='x', values='u').values
    v_grid = group_df.pivot(index='y', columns='x', values='v').values

    # 计算速度大小用于颜色映射
    speed = np.sqrt(u_grid ** 2 + v_grid ** 2) * 100

    # 无量纲化坐标
    Xi_normalized = (X_mesh - cx) / D
    Yi_normalized = (Y_mesh - cy) / D

    # 创建圆柱遮罩
    mask = (X_mesh - cx) ** 2 + (Y_mesh - cy) ** 2 <= r ** 2
    u_masked = np.ma.masked_where(mask, u_grid)
    v_masked = np.ma.masked_where(mask, v_grid)
    speed_masked = np.ma.masked_where(mask, speed)

    # 下采样以避免箭头过于密集
    u_plot = u_masked[::skip, ::skip]
    v_plot = v_masked[::skip, ::skip]
    speed_plot = speed_masked[::skip, ::skip]
    X_plot = Xi_normalized[::skip, ::skip]
    Y_plot = Yi_normalized[::skip, ::skip]

    # 设置图形比例
    x_min, x_max = Xi_normalized.min(), Xi_normalized.max()
    y_min, y_max = Yi_normalized.min(), Yi_normalized.max()
    aspect_ratio = (x_max - x_min) / (y_max - y_min)
    fig_width = 8
    fig_height = fig_width / aspect_ratio

    # 绘图
    plt.figure(figsize=(fig_width * 1.1, fig_height))

    # 如果有背景图像，先绘制背景
    if background_image_path and os.path.exists(background_image_path):
        # 读取背景图像
        background_img = plt.imread(background_image_path)

        # 假设背景图像覆盖了整个测量区域
        # 计算背景图像应该显示的范围
        # 这里假设背景图像的坐标范围与无量纲化后的坐标范围相同
        plt.imshow(background_img,
                   extent=[x_min, x_max, y_min, y_max],
                   alpha=0.3,  # 设置透明度，值越小背景越浅
                   cmap='gray',  # 使用灰度图
                   aspect='auto')

    # 绘制速度矢量
    quiver = plt.quiver(X_plot, Y_plot, u_plot, v_plot,
                        color='black', angles='xy', scale_units='xy',
                        scale=0.025,  # 控制箭头长度（减小值 → 更长） 初始为0.025
                        width=0.002,  # 箭头线宽（增大）
                        headwidth=3.0,  # 箭头头部宽度
                        headlength=4.0,  # 箭头头部长度
                        headaxislength=5.0,  # 头部在轴上的长度
                        pivot='mid',  # 箭头中心对齐
                        minlength=0.1  # 最小箭头长度，避免太短的箭头变成点
                        )

    # 绘制圆柱边界（在无量纲坐标系中是圆心(0,0)，半径0.5）
    circle = plt.Circle((0, 0), 0.5, color='black', fill=False, lw=2, linestyle='--')
    plt.gca().add_patch(circle)

    # 假设你想表示的速度值是0.01（你可以根据需要调整）
    ref_speed = 0.01
    # 根据scale调整箭头长度，这里假设scale=0.06, 如果改变了scale，请相应调整此值
    # 箭头的实际长度（相对于X轴和Y轴）将为 ref_speed / scale
    qk = plt.quiverkey(quiver, X=1.05, Y=0.5, U=ref_speed, label=f'{ref_speed*100} cm/s',
                       coordinates='axes', color='black', labelcolor='black', fontproperties={'size': 'small'})

    # 设置坐标轴
    plt.xlim(x_min, x_max)
    plt.ylim(y_min, y_max)
    plt.gca().set_aspect('equal', adjustable='box')
    plt.xlabel('X/D')
    plt.ylabel('Y/D')
    # plt.title('Instantaneous Velocity Vector Field')
    plt.tight_layout()

    # 保存图像
    save_file = save_path + '瞬时速度矢量图.png'
    plt.savefig(save_file, dpi=300, bbox_inches='tight')
    plt.show()


# 示例调用
# plot_velocity_vector_cylinder(cx=5.551450303, cy=4.804212818, D=0.9204411381 * 2, save_path='E:/覃嘉昇研三上学期/piv软件中文核心论文/圆柱绕流实验数据/vivo拍摄Re=100/Open_PIV_results_76_Test')
# plot_velocity_vector_cylinder(cx=5.55450303, cy=4.874212818, D=0.9084411381 * 2, save_path='E:/覃嘉昇研三上学期/piv软件中文核心论文/圆柱绕流实验数据/vivo拍摄Re=200/Open_PIV_results_76_Test')
# plot_velocity_vector_cylinder(cx=5.51450303, cy=4.684212818, D=0.9204411381 * 2, save_path='E:/覃嘉昇研三上学期/piv软件中文核心论文/圆柱绕流实验数据/vivo拍摄Re=300/Open_PIV_results_76_Test')
# plot_velocity_vector_cylinder(cx=5.51450303, cy=4.714212818, D=0.9204411381 * 2, save_path='E:/覃嘉昇研三上学期/piv软件中文核心论文/圆柱绕流实验数据/vivo拍摄Re=400/Open_PIV_results_76_Test')
# plot_velocity_vector_cylinder(cx=705.1450303, cy=205.4212818, D=58.54411381 * 2, save_path='E:/覃嘉昇研二下学期/piv实验小论文/论文/标准PIV数据集/test9')

# plot_velocity_vector_cylinder(cx=0.449, cy=0.4105, D=0.0714 * 2, save_path='E:/覃嘉昇研二下学期/piv实验小论文/论文/返修第一版/Re=200，分为4组/4/Open_PIV_results_76_Test')







