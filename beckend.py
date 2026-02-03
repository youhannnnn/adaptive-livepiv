from openpiv import windef  # <---- see windef.py for details
from openpiv import tools, scaling, validation, filters, preprocess
import openpiv.pyprocess as process
from openpiv import pyprocess
import numpy as np
import pathlib
import glob
import os.path
import importlib_resources
from skimage.io import imread
import utils
from PIL import Image
from time import time
import warnings
import matplotlib.pyplot as plt
from matplotlib import cm
from matplotlib.colors import Normalize
from PIL import Image
import os


def beckend_calculation(image_path, save_path, frame_a_name, frame_b_name, scaling_factor, mask_shapes, display_area, cloud_chart):
    settings = windef.Settings()
    path = importlib_resources.files('openpiv')
    '图片相关基础设置'
    settings.filepath_images = image_path       # 指定待处理图像文件所在的文件夹路径。
    settings.save_path = save_path              # 指定处理结果（如速度场文件、图像）的保存路径。
    settings.save_folder_suffix = 'Test'        # 输出文件夹后缀，用于区分不同结果。
    settings.frame_pattern_a = frame_a_name         # 第一帧和第二帧图像。
    settings.frame_pattern_b = frame_b_name         # 'a*bmp.bmp'表示第一帧的一系列图像，'b*bmp.bmp'表示第二帧的一系列图像
    settings.invert = False                         # 反转输入图像的强度范围。正负反转，一般情况不用使用。
    settings.ROI = 'full'                           # 处理的区域,可用元组(xmin, xmax, ymin, ymax)指定矩形区域。x是纵轴，y是横轴。
    settings.scaling_factor = scaling_factor        # 单位转换因子：（像素/米）*两帧之间的时间间隔。前端写一个输入，输入像素转化单位和两帧间隔。
    '掩膜设置'
    settings.image_mask = False                     # windef中第76行的dynamic_masking函数实现有问题，生成的mask_a、mask_b是全为0的一维数组，掩膜操作还未实现。
    settings.dynamic_masking_method = 'None'        # 掩模方法去除无关区域，'None'不应用掩模，'edge'用于有可见边缘的物体，'intensity'用于高亮或高暗的物体。
    settings.dynamic_masking_threshold = 0.005      # 掩模阈值，配合'intensity'使用，掩模低于阈值的阴暗或无效区域，值越小灵敏度越高、掩模区域越大。
    settings.dynamic_masking_filter_size = 7        # 动态掩模滤波器的尺寸，影响掩模的平滑度。奇数整数（如 7），确保滤波器有明确的中心点，较大的值使掩模更平滑。
    '互相关计算设置'
    settings.correlation_method = 'circular'        # 互相关计算方法。'circular': 窗口循环互相关。'linear': 线性互相关。循环相关适合均匀流场，线性相关更通用。
    settings.normalized_correlation = True          # 是否对互相关进行归一化。适合光照不均、对比度不高的图像。将全部计算域的相关性归一化，提高相对对比度。
    settings.subpixel_method = 'gaussian'           # 亚像素插值方法，计算粒子光点的实际位置，可以精确到0.几个像素，用于提高位移精度。'gaussian': 高斯拟合（默认，适合正相关峰）。'centroid': 质心法（适合宽平峰）。'parabolic': 抛物线拟合。
    settings.deformation_method = 'symmetric'       # 图像变形方法，通过前一次迭代的位移场对图像进行变形，用于多通道迭代中提高精度。'symmetric': 对称变形，两帧图像均被变形。'second image': 仅变形第二帧图像。
    settings.interpolation_order = 3                # 图像变形时的插值阶数。多通道迭代中，图像会根据位移场进行变形。阶数越高精度越高但计算量越大。
    settings.use_vectorized = True                  # 在extended_search_area_piv函数中是否启用向量化操作加速PIV计算。
    '信噪比计算设置'
    settings.num_iterations = 2                     # PIV处理的迭代次数。
    settings.validation_first_pass = True           # 是否在第一次迭代后进行向量验证。第一次迭代计算后，剔除超出最大最小位移场值的向量。
    settings.windowsizes = utils.settings_windowsizes_option(settings)          # 每次迭代的窗口大小（像素），逐步减小以提高分辨率。第一次迭代用64x64窗口，第二次用32x32，依此类推。和图像变形方法结合，通过每一轮计算大窗口的位移场，补偿已计算的位移，使粒子在后续计算中更接近对齐。
    settings.overlap = utils.settings_overlap_option(settings)                  # 窗口之间的重叠区域，一般为windowsize的一半。
    settings.sig2noise_method = 'peak2peak'         # 信噪比计算方法。'peak2peak': 主峰与次高峰的比值。'peak2mean': 主峰与平均背景的比值。None: 不计算信噪比。
    settings.sig2noise_threshold = 1.2              # 信噪比阈值
    settings.sig2noise_mask = 2                     # 主峰周围掩模的宽度，配合'peak2peak'使用，计算次高峰时会排除主峰周围sig2noise_mask个像素。
    '过滤异常值设置'
    settings.MinMax_U_disp = utils.settings_minmax_uv_disp_option(settings)     # 位移的合理范围（像素），超出范围的向量被标记为无效。
    settings.MinMax_V_disp = utils.settings_minmax_uv_disp_option(settings)
    settings.std_threshold = 4                      # 基于全局标准差过滤异常值。(ui-uu)<std_threshold*标准差。4表示不能超过4倍标准差，正态函数中涵盖了99.994%。
    settings.median_threshold = 3                   # 基于中心矢量与邻居矢量中位数来比较过滤异常值。配合median_size使用，median_size表示中心矢量与邻居矢量的最大距离。(ui-um)<median_threshold个像素。um是查询窗口周围区域的速度中值。
    settings.median_size = 1                        # median_threshold过低，或者median_size过高，都会影响障碍物掩膜区域。因为障碍物掩膜区域的速度接近于0，障碍物边缘计算邻居矢量中心值时，很容易超过median_threshold。
    '替换异常值设置'
    settings.replace_vectors = True                 # 是否替换被标记为无效的向量。只对迭代一次的情况起效。因为迭代多次的情况下，是必须替换无效向量的，不能有无效值传递给下一次迭代。
    settings.filter_method = 'localmean'            # 异常值替换方法。'localmean':用局部均值替换。'disk':用圆形邻域均值替换。'distance':用最近有效向量的距离加权替换。
    settings.max_filter_iteration = 4               # 异常值替换的最大迭代次数。迭代替换异常值，直到没有新异常值。迭代越多替换越彻底。
    settings.filter_kernel_size = 2                 # 异常值替换的核半径，也就是网格间距。核越大替换范围越广，但越大，就越影响掩膜区域。
    settings.smoothn = True                         # 启用基于Tikhonov正则化的位移场平滑，通过最小化目标函数实现平滑。抑制噪声，填补空缺区域，但同时削弱涡旋等小尺度结构。
    settings.smoothn_p = 0.5                        # 平滑强度参数，在最小化强度函数中使用。越大，平滑程度越强。
    '图片生成设置'
    settings.save_plot = True                       # 是否保存向量场图像。
    settings.show_plot = True                       # 是否显示向量场图像。
    settings.show_all_plots = False                 # 是否要每一个步骤都生成一个图片。
    # settings.scale_plot = utils.settings_scale_plot_option(settings)          # 要先提取速度最大值，再乘以一个特点系数。在windef里面直接更改了。

    windef.piv(settings)
    result_path = settings.save_path + "/" + "Open_PIV_results_" + str(settings.windowsizes[settings.num_iterations-1]) + "_" + settings.save_folder_suffix
    result_figure_name = "Image_A000.png"
    result_text_name = "field_A000.txt"
    frame_a = Image.open(os.path.join(settings.filepath_images, frame_a_name))
    figure_width, figure_height = frame_a.size
    image_name = str(settings.filepath_images + '/' + settings.frame_pattern_a)
    if len(mask_shapes) > 0:
        for shape in mask_shapes:
            beckend_mask(shape, display_area, figure_width, figure_height, result_path, result_figure_name, result_text_name, settings.scaling_factor, settings.scale_plot, settings.windowsizes[settings.num_iterations - 1], image_name)

    if cloud_chart:
        make_cloud_chart(result_path, result_text_name, settings.filepath_images, settings.frame_pattern_a)

    return result_path, result_figure_name


def beckend_mask(shape, display_area, figure_width, figure_height, result_path, result_figure_name, result_text_name, scaling_factor, scale_plot, window_size, image_name):
    if shape["type"] == "矩形":
        rect = shape["rect"]
        # 获取左上角和右下角坐标
        top_left = rect.topLeft()  # QPoint
        bottom_right = rect.bottomRight()  # QPoint
        x1, y1 = top_left.x(), top_left.y()
        x2, y2 = bottom_right.x(), bottom_right.y()

        display_width = display_area[0]
        display_height = display_area[1]

        if figure_width/figure_height > display_width/display_height:
            text_x1 = x1/display_width*figure_width/scaling_factor/30*100          # （*figure_width/scaling_factor）前面的是相对图片的xy长，乘以这个数之后得到text文件中的xy
            text_x2 = x2/display_width*figure_width/scaling_factor/30*100
            text_y1 = figure_height/scaling_factor/30*100 - (y1 - (display_height - figure_height*display_width/figure_width)/2)/figure_height*figure_width/display_width*figure_height/scaling_factor/30*100
            text_y2 = figure_height/scaling_factor/30*100 - (y2 - (display_height - figure_height*display_width/figure_width)/2)/figure_height*figure_width/display_width*figure_height/scaling_factor/30*100
        else:
            text_x1 = (x1 - (display_width - figure_width*display_height/figure_height)/2)/figure_width*figure_height/display_height*figure_width/scaling_factor/30*100
            text_x2 = (x2 - (display_width - figure_width*display_height/figure_height)/2)/figure_width*figure_height/display_height*figure_width/scaling_factor/30*100
            text_y1 = figure_height/scaling_factor/30*100 - y1/display_height*figure_height/scaling_factor/30*100     # y轴调换过来了，所以要前面用一个总长来减
            text_y2 = figure_height/scaling_factor/30*100 - y2/display_height*figure_height/scaling_factor/30*100

        # 构建完整文件路径
        file_path = result_path + "/" + result_text_name
        # 读取文件内容
        with open(file_path, 'r') as f:
            lines = f.readlines()
        # 处理每一行数据
        modified_lines = []
        for line in lines:
            # 保留注释行
            if line.startswith('#'):
                modified_lines.append(line)
                continue
            # 分割数据列
            parts = line.strip().split()
            if len(parts) != 5:
                continue  # 跳过格式错误行
            try:
                x = float(parts[0])/30*100  #将xy坐标转换为cm
                y = float(parts[1])/30*100
                u = float(parts[2])
                v = float(parts[3])
                mask = float(parts[4])
            except ValueError:
                continue  # 跳过数据转换错误行
            # 应用条件判断
            if text_x2 > x > text_x1 and text_y1 > y > text_y2:
                u = 0.0001
                v = 0.0001
                mask = 1.0000
            # 重新格式化行（保持原始小数位数）
            modified_line = f"{x:8.4f}  {y:8.4f}  {u:8.4f}  {v:8.4f}  {mask:8.4f}\n"
            modified_lines.append(modified_line)
        # 写回文件（覆盖原文件）
        with open(file_path, 'w') as f:
            f.writelines(modified_lines)

        # 重新出图
        os.remove(result_path + "/" + result_figure_name)
        Name = os.path.join(result_path, "Image_A000.png")
        fig, _ = windef.display_vector_field(
            os.path.join(result_path, "field_A000.txt"),
            on_img=True,
            scale=scale_plot,
            scaling_factor=scaling_factor,
            window_size=window_size,
            image_name=image_name
        )
        fig.savefig(Name)


    if shape["type"] == "圆形":
        rect = shape["rect"]
        # 获取圆形掩膜在显示区域中的信息
        x1 = rect.center().x()  # 圆心x
        y1 = rect.center().y()  # 圆心y
        radius_width = rect.width() / 2  # 水平半径
        radius_height = rect.height() / 2  # 垂直半径

        display_width = display_area[0]
        display_height = display_area[1]

        if figure_width/figure_height > display_width/display_height:
            text_x1 = x1/display_width*figure_width/scaling_factor/30*100
            text_y1 = figure_height/scaling_factor/30*100 - (y1 - (display_height - figure_height*display_width/figure_width)/2)/figure_height*figure_width/display_width*figure_height/scaling_factor/30*100
            text_radius_width = radius_width/display_width*figure_width/scaling_factor/30*100
            text_radius_height = radius_height/display_width*figure_width/scaling_factor/30*100
        else:
            text_x1 = (x1 - (display_width - figure_width*display_height/figure_height)/2)/figure_width*figure_height/display_height*figure_width/scaling_factor/30*100
            text_y1 = figure_height/scaling_factor/30*100 - y1/display_height*figure_height/scaling_factor/30*100     # y轴调换过来了，所以要前面用一个总长来减
            text_radius_width = radius_width/display_height*figure_height/scaling_factor/30*100
            text_radius_height = radius_height/display_height*figure_height/scaling_factor/30*100

        # 构建完整文件路径
        file_path = result_path + "/" + result_text_name
        # 读取文件内容
        with open(file_path, 'r') as f:
            lines = f.readlines()
        # 处理每一行数据
        modified_lines = []
        for line in lines:
            # 保留注释行
            if line.startswith('#'):
                modified_lines.append(line)
                continue
            # 分割数据列
            parts = line.strip().split()
            if len(parts) != 5:
                continue  # 跳过格式错误行
            try:
                x = float(parts[0])/30*100
                y = float(parts[1])/30*100
                u = float(parts[2])
                v = float(parts[3])
                mask = float(parts[4])
            except ValueError:
                continue  # 跳过数据转换错误行
            # 应用条件判断
            if (x-text_x1)**2/text_radius_width**2 + (y-text_y1)**2/text_radius_height**2 < 1:
                u = 0.0000
                v = 0.0000
                mask = 1.0000
            # 重新格式化行（保持原始小数位数）
            modified_line = f"{x:8.4f}  {y:8.4f}  {u:8.4f}  {v:8.4f}  {mask:8.4f}\n"
            modified_lines.append(modified_line)
        # 写回文件（覆盖原文件）
        with open(file_path, 'w') as f:
            f.writelines(modified_lines)

        # 重新出图
        os.remove(result_path + "/" + result_figure_name)
        Name = os.path.join(result_path, "Image_A000.png")
        fig, _ = windef.display_vector_field(
            os.path.join(result_path, "field_A000.txt"),
            on_img=True,
            scale=scale_plot,
            scaling_factor=scaling_factor,
            window_size=window_size,
            image_name=image_name
        )
        fig.savefig(Name)

def make_cloud_chart(result_path, result_text_name, filepath_images, frame_pattern_a):
    # 构建文件路径
    txt_file = os.path.join(result_path, result_text_name)
    image_file = os.path.join(filepath_images, frame_pattern_a)
    output_file = os.path.join(result_path, "Image_cloud_chart_A000.png")

    # 读取PIV结果文件
    x, y, u, v = [], [], [], []
    with open(txt_file, 'r') as f:
        for line in f:
            if line.startswith('#'):
                continue
            data = line.strip().split()
            if len(data) != 5:
                continue
            xi, yi, ui, vi, _ = map(float, data)
            x.append(xi)
            y.append(yi)
            u.append(ui)
            v.append(vi)

    x = np.array(x)
    y = np.array(y)
    speed = np.sqrt(np.array(u)**2 + np.array(v)**2)

    # 加载原始图像作为背景
    img = Image.open(image_file).convert('L')  # 转换为灰度图
    img = np.array(img)

    # 设置绘图区域
    fig, ax = plt.subplots(figsize=(10, 8))
    ax.imshow(img, cmap='gray', extent=[x.min(), x.max(), y.min(), y.max()], origin='lower')

    # 绘制速度云图
    sc = ax.tricontourf(x, y, speed, levels=50, cmap='viridis')
    cbar = fig.colorbar(sc, ax=ax)
    cbar.set_label('Velocity (m/s)', fontsize=12)
    ax.set_title("Cloud Chart - PIV Result")
    ax.set_aspect('equal')

    # 保存图片
    fig.savefig(output_file, dpi=300, bbox_inches='tight')
    plt.close(fig)

    return output_file  # 返回云图文件名

