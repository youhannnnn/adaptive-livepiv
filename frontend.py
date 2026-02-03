import sys  # 导入sys模块，用于访问与Python解释器相关的变量和函数，如sys.argv用于获取命令行参数
import os  # 导入os模块，用于进行操作系统交互，比如路径处理、文件遍历等
from PyQt5.QtWidgets import (QApplication, QWidget, QVBoxLayout, QHBoxLayout, QDialog,
                             QPushButton, QListWidget, QLabel, QFileDialog, QComboBox,
                             QMessageBox, QSizePolicy, QSplitter, QDialogButtonBox,
                             QLineEdit, QFormLayout, QRadioButton)
# 从PyQt5.QtWidgets模块导入多个GUI组件和布局控件，用于构建图形界面，如应用窗口、按钮、列表、对话框、输入框等
from PyQt5.QtCore import Qt, QDir, QPoint, QRect, QSize
# 从PyQt5.QtCore模块导入核心类，Qt用于定义常量（如对齐方式、鼠标按钮等），QDir处理目录操作，QPoint处理坐标点，QRect处理矩形区域
from PyQt5.QtGui import QPixmap, QPainter, QPen, QColor, QCursor, QIcon
# 从PyQt5.QtGui模块导入图形处理相关的类，QPixmap用于图像显示，QPainter用于绘图，QPen设置画笔，QColor设置颜色，QCursor设置光标
import beckend
from PIL import Image
import glob
import os
import pandas as pd


#以下是图像设置的 操作
class ImageParamsDialog(QDialog):   # 定义一个图像参数设置的对话框类，继承自QDialog（模态对话框）
    def __init__(self, parent=None):  # 构造函数，初始化对话框，可以接受一个父窗口对象
        super().__init__(parent)  # 调用父类的构造方法，确保对话框正确初始化
        self.setWindowTitle("Image Parameters Settings")  # 设置对话框标题为“图像参数设置”
        layout = QVBoxLayout(self)  # 创建一个垂直布局管理器，并将其设为当前对话框的主布局
        # 移除帮助按钮（问号）
        self.setWindowFlags(self.windowFlags() & ~Qt.WindowContextHelpButtonHint)
        # 创建表单布局
        form_layout = QFormLayout()  # 创建一个表单布局对象（label + 控件形式）
        self.pixels_input = QLineEdit()  # 创建一个文本输入框，用于输入“像素每米”的数值
        self.time_input = QLineEdit()  # 创建一个文本输入框，用于输入“时间差”的数值
        form_layout.addRow("Pixels Per Meter：", self.pixels_input)  # 向表单中添加一行标签和输入框，提示用户输入像素密度
        form_layout.addRow("Frame Interval(s)：", self.time_input)  # 添加第二行标签和输入框，提示用户输入帧之间的时间差
        layout.addLayout(form_layout)  # 将表单布局添加到主垂直布局中

        # 按钮组
        self.btn_box = QDialogButtonBox(QDialogButtonBox.Ok | QDialogButtonBox.Cancel)  # 创建标准的对话框按钮组，包含“确定”和“取消”按钮
        layout.addWidget(self.btn_box)  # 将按钮组添加到主布局中
        self.btn_box.accepted.connect(self.accept)  # 将“确定”按钮的点击事件连接到QDialog自带的accept()槽函数（关闭对话框并返回Accepted）
        self.btn_box.rejected.connect(self.reject)  # 将“取消”按钮的点击事件连接到reject()槽函数（关闭对话框并返回Rejected）

    def get_params(self):                       # 定义一个公共方法，用于获取用户输入的两个参数
        """返回输入参数的元组（像素每米, 时间差）"""  # 方法说明文档，说明返回值为一个包含两个文本值的元组
        return (self.pixels_input.text(), self.time_input.text())  # 获取两个输入框中的文本并返回为元组
#以下是掩膜的操作
class MaskDialog(QDialog):  # 定义一个名为 MaskDialog 的类，用于设置掩膜形状，继承自 QDialog（对话框类）
    def __init__(self, parent=None):  # 构造函数，接受一个可选的父窗口对象
        super().__init__(parent)  # 调用父类构造函数，初始化对话框
        self.setWindowTitle("Image Mask")  # 设置对话框窗口的标题为“掩膜设置”
        self.layout = QVBoxLayout(self)  # 创建一个垂直布局管理器作为主布局，并设置给该对话框
        # 移除帮助按钮（问号）
        self.setWindowFlags(self.windowFlags() & ~Qt.WindowContextHelpButtonHint)
        # 形状选择
        self.shape_combo = QComboBox()  # 创建一个下拉框组件，用于选择掩膜的形状（例如矩形、圆形）
        self.shape_combo.addItems(["Rect", "Circle"])  # 将可选项“矩形”和“圆形”添加到下拉框中
        self.layout.addWidget(self.shape_combo)  # 将下拉框控件添加到垂直布局中
        # 操作按钮
        self.btn_box = QDialogButtonBox()  # 创建一个按钮盒子（用于容纳多个按钮），这里不使用标准按钮类型
        self.btn_apply = QPushButton("Apply Mask")  # 创建一个普通按钮，文本为“执行掩膜”
        self.btn_clear = QPushButton("Clear Mask")  # 创建另一个普通按钮，文本为“清除掩膜”
        self.btn_box.addButton(self.btn_apply, QDialogButtonBox.ActionRole)  # 将“执行掩膜”按钮添加到按钮盒子中，指定角色为自定义操作
        self.btn_box.addButton(self.btn_clear, QDialogButtonBox.ActionRole)  # 将“清除掩膜”按钮也添加到按钮盒子中
        self.layout.addWidget(self.btn_box)  # 将按钮盒子添加到垂直主布局中

class DrawLabel(QLabel):  # 定义一个自定义标签类 DrawLabel，继承自 QLabel，用于图像显示与掩膜绘制
    def __init__(self, main_window):  # 构造函数，接收主窗口作为参数，便于访问全局状态和数据
        super().__init__(main_window)  # 调用父类构造函数，并将主窗口设置为父对象
        self.main_window = main_window  # 保存主窗口的引用，用于访问掩膜数据、当前形状等
        self.drawing_enabled = False  # 初始化绘图模式标志，默认不启用绘图
        self.start_point = QPoint()  # 初始化起始点为QPoint对象，用于记录绘图起点
        self.current_shape = {"type": None, "rect": QRect()}  # 当前正在绘制的形状信息，包含类型和矩形区域
        self.setMouseTracking(True)  # 启用鼠标跟踪，即使没有按下按钮也能触发 mouseMoveEvent
        self.drag_mode = False  # 初始化拖动模式标志，默认不启用拖动
        self.drag_start_pos = QPoint()  # 拖动起始位置，用于计算偏移量
    def mousePressEvent(self, event):  # 重写鼠标按下事件，用于开始绘图或拖动图形
        if self.drawing_enabled and event.button() == Qt.LeftButton:  # 如果当前启用了绘图模式，且按下的是鼠标左键
            self.start_point = event.pos()  # 记录鼠标按下的起始位置（绘图起点）
            self.current_shape["type"] = self.main_window.current_mask_shape  # 设置当前绘制图形的类型（矩形或圆形）
            self.current_shape["rect"] = QRect(self.start_point, self.start_point)  # 初始化一个起点到自身的矩形区域
            self.update()  # 请求重绘，触发 paintEvent()，绘制当前形状预览
        else:  # 若未启用绘图模式，或不是左键点击，进入图形选择/拖动判断流程
            # 检查是否点击现有图形
            for i, shape in enumerate(self.main_window.mask_shapes):  # 遍历所有已绘制的图形
                if self.check_point_in_shape(event.pos(), shape):  # 如果点击位置在该图形内
                    self.main_window.selected_shape_index = i  # 设置为当前选中的图形索引
                    self.drag_start_pos = event.pos()  # 记录拖动起始位置
                    self.drag_mode = True  # 启用拖动模式
                    break  # 只选择第一个命中的图形

    def mouseMoveEvent(self, event):  # 重写鼠标移动事件
        if self.drawing_enabled and event.buttons() & Qt.LeftButton:  # 如果处于绘图模式并按住鼠标左键
            self.current_shape["rect"] = QRect(  # 更新当前绘制图形的矩形区域
                self.start_point, event.pos()).normalized()  # 使用起点和当前位置构造矩形，并调用normalized保证方向一致（左上到右下）
            self.update()  # 请求重绘，实时显示正在绘制的形状
        elif self.drag_mode:  # 如果处于拖动模式
            offset = event.pos() - self.drag_start_pos  # 计算当前位置相对于拖动起始点的偏移量
            shape = self.main_window.mask_shapes[self.main_window.selected_shape_index]  # 获取当前选中的图形对象
            shape["rect"].translate(offset)  # 将图形矩形区域平移指定的偏移量
            self.drag_start_pos = event.pos()  # 更新拖动起始位置为当前鼠标位置，便于连续拖动
            self.update()  # 重绘，显示图形的新位置

    def mouseReleaseEvent(self, event):  # 重写鼠标释放事件
        if self.drawing_enabled:  # 如果处于绘图模式
            if self.current_shape["type"]:  # 如果当前形状类型不为空（已经设置过）
                self.main_window.mask_shapes.append(self.current_shape.copy())  # 将当前绘制完成的图形添加到主窗口的图形列表中
                self.current_shape["type"] = None  # 重置当前图形类型为空，表示绘图结束
                self.drawing_enabled = False  # 禁用绘图模式
                self.setCursor(Qt.ArrowCursor)  # 设置光标恢复为默认箭头
        self.drag_mode = False  # 不管是否绘图，释放后都关闭拖动模式

    def mouseDoubleClickEvent(self, event):  # 重写鼠标双击事件
        if event.button() == Qt.RightButton:  # 如果是鼠标右键双击
            for i, shape in enumerate(self.main_window.mask_shapes):  # 遍历所有已绘制图形
                if self.check_point_in_shape(event.pos(), shape):  # 如果当前双击位置在图形内
                    del self.main_window.mask_shapes[i]  # 从图形列表中删除该图形
                    self.update()  # 请求重绘，更新画面
                    break  # 删除第一个命中的图形后就退出循环

    def check_point_in_shape(self, point, shape):  # 自定义函数，检查某个坐标点point是否落在shape图形内部
        if shape["type"] == "矩形":  # 如果图形类型是矩形
            return shape["rect"].contains(point)  # 使用QRect的contains方法判断点是否在矩形内，返回True/False
        elif shape["type"] == "圆形":  # 如果图形类型是圆形
            center = shape["rect"].center()  # 获取图形矩形区域的中心点，作为圆心
            radius = shape["rect"].width() / 2  # 以矩形宽度的一半作为半径（默认圆为正方形内切）
            return (point - center).manhattanLength() <= radius  # 使用曼哈顿距离近似判断点是否在圆形范围内

    def paintEvent(self, event):  # 重写 paintEvent 函数，负责绘制背景图和掩膜图形
        super().paintEvent(event)  # 调用父类的绘图事件，确保基础图像被正常绘制
        if self.pixmap():  # 如果当前 QLabel 有图像（QPixmap）
            scaled_pixmap = self.pixmap().scaled(  # 将图像缩放到适应窗口大小
                self.size(),  # 当前窗口大小
                Qt.KeepAspectRatio,  # 保持图像宽高比
                Qt.SmoothTransformation  # 使用平滑变换提高图像质量
            )
            self.setPixmap(scaled_pixmap)  # 设置缩放后的图像回标签中进行显示

        super().paintEvent(event)  # 再次调用父类绘图方法（这一行是多余的重复，通常只需调用一次）
        qp = QPainter(self)  # 创建一个 QPainter 绘图对象，绑定到当前标签组件上
        qp.setPen(QPen(QColor(255, 0, 0, 150), 2))  # 设置画笔为红色半透明，线宽为2像素
        qp.setBrush(QColor(255, 0, 0, 50))  # 设置填充颜色为红色透明（遮罩效果）

        # 绘制已有图形
        for shape in self.main_window.mask_shapes:  # 遍历所有已经保存的掩膜图形
            if shape["type"] == "矩形":  # 如果是矩形
                qp.drawRect(shape["rect"])  # 使用QPainter绘制矩形
            elif shape["type"] == "圆形":  # 如果是圆形
                qp.drawEllipse(shape["rect"])  # 使用QPainter绘制圆形（以矩形边界为外接框）

        # 绘制当前正在绘制的图形
        if self.current_shape["type"]:  # 如果当前有正在绘制的图形
            if self.current_shape["type"] == "矩形":  # 判断类型是否为矩形
                qp.drawRect(self.current_shape["rect"])  # 绘制当前矩形
            elif self.current_shape["type"] == "圆形":  # 判断类型是否为圆形
                qp.drawEllipse(self.current_shape["rect"])  # 绘制当前圆形

class ImageBrowser(QWidget):  # 定义一个图像浏览器类，继承自 QWidget，用于构建主应用窗口
    def __init__(self):  # 构造函数，初始化主窗口及相关组件
        super().__init__()      # 调用 QWidget 的父类构造函数
        self.initParameter()    # 初始化跟后端连接需要传递的各个参数
        self.initUI()           # 调用初始化界面方法，创建布局与控件

    def initParameter(self):
        self.image_paths = []  # 初始化图像路径列表，用于保存所有导入图像的完整路径
        self.output_dir = None  # 初始化输出目录为 None，用于后续保存输出路径
        self.result_path = None         # 结果文件夹
        self.result_figure_name = None      # 结果图像名称
        self.mask_shapes = []  # 存储所有掩膜图形的列表（包含类型
        self.drawing = False  # 是否处于绘图模式和矩形位置）
        self.current_shape = None  # 当前正在绘制的掩膜形状（暂时未使用，可扩展）（备用变量）
        self.drag_mode = False  # 是否处于拖动图形模式
        self.selected_shape_index = -1  # 当前选中的图形索引（默认无选中）
        self.pixels_per_meter = None  # 初始化像素密度参数（单位 px/m）
        self.time_interval = None  # 初始化时间间隔参数（单位 s）
        self.display_area = []  # 显示框的宽度和高度
        self.theoretical_calculation_init_speed = None  # 为了理论计算所输入的入口流速
        self.theoretical_calculation_method = None  # 理论计算的方法

    def initUI(self):  # 初始化主界面的方法，设置所有控件和布局
        self.setWindowTitle('EduFlow PIV Analyzer')  # 设置窗口标题
        self.setWindowIcon(QIcon('E:\覃嘉昇研二下学期\piv实验小论文\项目文件\Icon\窗口标识.png'))  # 设置窗口图标
        self.setGeometry(100, 100, 1100, 600)  # 设置窗口初始位置和大小（x=100, y=100, 宽=1000，高=600）

        # 左侧面板
        left_panel = QWidget()  # 创建左侧控制面板容器
        left_layout = QVBoxLayout(left_panel)  # 为左侧面板创建垂直布局
        left_layout.setContentsMargins(5, 5, 5, 5)  # 设置边距为5
        left_layout.setSpacing(10)  # 设置控件之间的垂直间距为10像素

        # 右侧面板
        right_container = QWidget()  # 创建右侧容器控件，用于包含图像显示区与按钮面板
        right_layout = QVBoxLayout(right_container)  # 创建垂直布局用于右侧容器
        right_layout.setContentsMargins(5, 5, 5, 5)  # 设置布局边距为0
        right_layout.setSpacing(10)  # 设置控件之间的间距为5像素

        # 主布局使用水平分割器
        main_splitter = QSplitter(Qt.Horizontal)  # 创建水平分割器，将窗口分为左右两部分
        main_splitter.addWidget(left_panel)  # 将左侧控制面板加入水平分割器
        main_splitter.addWidget(right_container)  # 将右侧容器加入水平分割器
        main_splitter.setSizes([250, 750])  # 设置左右分割初始比例：左 250px，右 750px（大约 1:3）

        # 左侧面板的图像列表框
        self.left_list_widget = QListWidget()  # 创建图像文件列表控件
        left_layout.addWidget(self.left_list_widget)  # 将图像列表添加到左侧布局中
        # 左侧面板的按钮
        left_btn_layout = QHBoxLayout()  # 创建一个水平布局，用于排列添加和清空按钮
        self.btn_add = QPushButton()  # 创建一个“添加图像”按钮
        self.btn_add.setIcon(QIcon('E:\覃嘉昇研二下学期\piv实验小论文\项目文件\Icon\import.png'))  # 设置图标
        self.btn_add.setIconSize(QSize(80, 24))  # 图标大小略小于按钮，留出边距
        self.btn_add.setFixedHeight(30)  # 设置按钮高度为35像素
        self.btn_clear = QPushButton()  # 创建一个“清空列表”按钮
        self.btn_clear.setIcon(QIcon('E:\覃嘉昇研二下学期\piv实验小论文\项目文件\Icon\clear.png'))
        self.btn_clear.setIconSize(QSize(80, 24))
        self.btn_clear.setFixedHeight(30)  # 设置按钮高度为35像素
        left_btn_layout.addWidget(self.btn_add)  # 将“添加图像”按钮添加到按钮水平布局中
        left_btn_layout.addWidget(self.btn_clear)  # 将“清空列表”按钮添加到按钮水平布局中
        left_layout.addLayout(left_btn_layout)  # 将按钮布局添加到左侧主布局

        # 右侧显示区域
        self.right_show_panel = DrawLabel(self)  # 创建自定义的图像显示组件 DrawLabel（支持绘制掩膜），并将主窗口作为参数传入
        self.right_show_panel.setAlignment(Qt.AlignCenter)  # 设置图像居中显示
        self.right_show_panel.setFixedSize(850, 530)  # 固定大小
        self.right_show_panel.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)  # 设置自动伸缩策略，填满剩余空间
        self.right_show_panel.setStyleSheet("""
            border: 1px solid #999999;
            background-color: #FFFFFF;
            padding: 2px;
        """)
        right_layout.addWidget(self.right_show_panel, 1)  # 将右侧图像显示组件添加到右侧垂直布局中，占用主空间

        # 右侧面板的按钮
        right_btn_layout = QHBoxLayout()  # 创建一个水平布局用于容纳按钮
        right_btn_layout.setContentsMargins(0, 0, 0, 0)  # 设置内边距为 5 像素
        self.btn_output = QPushButton()  # 创建“输出路径”按钮
        self.btn_output.setIcon(QIcon('E:\覃嘉昇研二下学期\piv实验小论文\项目文件\Icon\output.png'))  # 设置图标
        self.btn_output.setIconSize(QSize(110, 24))  # 图标大小略小于按钮，留出边距
        self.btn_output.setFixedHeight(30)  # 设置按钮高度为30像素
        self.btn_mask = QPushButton()  # 创建“掩膜操作”按钮（用于绘制和清除掩膜）
        self.btn_mask.setIcon(QIcon('E:\覃嘉昇研二下学期\piv实验小论文\项目文件\Icon\mask.png'))
        self.btn_mask.setIconSize(QSize(110, 24))
        self.btn_mask.setFixedHeight(30)  # 设置按钮高度为30像素
        self.btn_size = QPushButton()  # 创建“图像尺寸”按钮（用于设置像素密度与时间差）
        self.btn_size.setIcon(QIcon('E:\覃嘉昇研二下学期\piv实验小论文\项目文件\Icon\parameters.png'))
        self.btn_size.setIconSize(QSize(145, 24))
        self.btn_size.setFixedHeight(30)  # 设置按钮高度为30像素
        # self.btn_method = QPushButton("理论计算")  # 创建“图像尺寸”按钮（用于设置像素密度与时间差）
        # self.btn_method.setFixedHeight(30)  # 设置按钮高度为30像素
        self.btn_process = QPushButton()  # 创建“执行计算”按钮（执行分析或演示操作）
        self.btn_process.setIcon(QIcon('E:\覃嘉昇研二下学期\piv实验小论文\项目文件\Icon\PIVanalyze.png'))
        self.btn_process.setIconSize(QSize(110, 24))
        self.btn_process.setFixedHeight(30)  # 设置按钮高度为30像素
        btn_style = """
            QPushButton {
                padding: 5px;
                font-size: 12px;
                min-width: 120px;  /* 设置最小宽度 */
                max-width: 120px;  /* 设置最大宽度 */
                height: 30px;      /* 固定高度 */
                text-align: center;/* 文本居中 */
            }
        """
        btn_parameters_style = """
            QPushButton {
                padding: 5px;
                font-size: 12px;
                min-width: 145px;  /* 设置最小宽度 */
                max-width: 145px;  /* 设置最大宽度 */
                height: 30px;      /* 固定高度 */
                text-align: center;/* 文本居中 */
            }
        """
        self.btn_output.setStyleSheet(btn_style)  # 应用样式
        self.btn_mask.setStyleSheet(btn_style)
        self.btn_size.setStyleSheet(btn_parameters_style)
        # self.btn_method.setStyleSheet(btn_style)
        self.btn_process.setStyleSheet(btn_style)
        right_btn_layout.addWidget(self.btn_output)  # 添加“输出路径”按钮
        right_btn_layout.addWidget(self.btn_mask)  # 添加“掩膜操作”按钮
        right_btn_layout.addWidget(self.btn_size)  # 添加“图像尺寸”按钮
        # right_btn_layout.addWidget(self.btn_method)  # 添加“理论计算”按钮
        right_btn_layout.addWidget(self.btn_process)  # 添加“执行计算”按钮
        right_btn_layout.addStretch(1)  # 添加弹性空白项，使按钮靠左排列，右侧留白
        right_layout.addLayout(right_btn_layout)  # 将控制面板添加到底部的右侧垂直布局中

        # 主窗口布局
        main_layout = QHBoxLayout(self)  # 设置主窗口为水平布局（实际上只放一个 main_splitter）
        main_layout.addWidget(main_splitter)  # 添加左右分割器

        # 连接信号
        self.btn_add.clicked.connect(self.show_selection_dialog)  # “添加图像”按钮连接到图像添加对话框方法
        self.btn_clear.clicked.connect(self.clear_list)  # “清空列表”按钮连接到清空方法
        self.left_list_widget.currentRowChanged.connect(self.show_image)  # 图像列表选择项改变时，显示对应图像
        self.btn_output.clicked.connect(self.select_output_dir)  # 连接按钮点击信号到选择输出目录的方法
        self.btn_mask.clicked.connect(self.show_mask_dialog)  # 将“掩膜操作”按钮与 show_mask_dialog 方法连接
        self.btn_size.clicked.connect(self.show_image_params_dialog)  # “图像尺寸”按钮连接到图像参数对话框
        # self.btn_method.clicked.connect(self.select_theoretical_calculate_method)
        self.btn_process.clicked.connect(self.execute_calculation)  # “执行计算”按钮连接到计算执行方法

    def show_selection_dialog(self):  # 显示添加图像的方式选择对话框（图像对 or 批量添加）
        if len(self.image_paths) == 2:      # 判断显示区域是否已经有两个图像
            QMessageBox.warning(self, "选择错误", "请先清除列表")  # 弹出警告提示
            return
        # 第一步：显示选择对话框
        choice = QMessageBox.question(  # 弹出一个问题对话框，询问用户添加图像的方式
            self,
            '添加图像',
            '请依次添加第一帧、第二帧图片\n一次只能导入一张图片',
            QMessageBox.Yes | QMessageBox.Cancel  # 三个选项：是、否、取消
        )
        if choice == QMessageBox.Yes:  # 用户选择“是” → 添加图像对（两帧）
            self.add_image_pair()  # 调用添加图像对方法
        # Cancel则不执行任何操作

    def clear_list(self):  # 清空图像列表的方法
        self.image_paths.clear()  # 清空图像路径列表
        self.left_list_widget.clear()  # 清空左侧图像文件名列表
        self.right_show_panel.clear()  # 清空图像显示区域

    def show_image(self, index):  # 显示当前选中的图像（列表中第 index 项）
        if 0 <= index < len(self.image_paths):  # 检查索引是否有效
            try:
                pixmap = QPixmap(self.image_paths[index])  # 使用路径加载图像为 QPixmap 对象
                if pixmap.isNull():  # 如果图像无效或加载失败
                    raise ValueError("无效的图像文件")  # 抛出异常
                # 自适应显示
                scaled_pixmap = pixmap.scaled(  # 将图像缩放至适配窗口大小
                    self.right_show_panel.size(),  # 缩放目标为右侧面板大小
                    Qt.KeepAspectRatio,  # 保持原始宽高比
                    Qt.SmoothTransformation  # 平滑缩放，提高质量
                )
                self.right_show_panel.setPixmap(scaled_pixmap)  # 设置缩放后的图像到右侧显示区域
            except Exception as e:  # 捕获异常
                QMessageBox.critical(self, "错误", f"无法加载图像：\n{str(e)}")  # 弹出错误提示框

    def select_output_dir(self):  # 选择输出路径的对话框
        """选择输出路径"""
        dir_path = QFileDialog.getExistingDirectory(  # 打开文件夹选择对话框
            self,
            "选择输出文件夹",
            QDir.homePath(),  # 默认路径为用户主目录
            QFileDialog.ShowDirsOnly  # 仅允许选择文件夹
        )
        if dir_path:  # 如果用户选择了路径
            self.output_dir = dir_path  # 保存路径
            QMessageBox.information(  # 弹出提示框确认路径设置成功
                self,
                "路径设置成功",
                f"输出路径已设置为：\n{dir_path}",
                QMessageBox.Ok
            )

    def show_mask_dialog(self):  # 显示掩膜设置对话框（选择图形 + 清除）
        dialog = MaskDialog(self)  # 创建掩膜对话框对象，主窗口为父窗口
        dialog.btn_apply.clicked.connect(  # 连接“执行掩膜”按钮点击事件
            lambda: self._handle_apply_mask(dialog)  # 使用 lambda 表达式调用处理函数并传入当前对话框
        )
        dialog.btn_clear.clicked.connect(self.clear_masks)  # 连接“清除掩膜”按钮点击事件
        dialog.exec_()  # 显示对话框，阻塞主界面，等待用户操作

    def show_image_params_dialog(self):  # 显示图像参数设置对话框的方法
        """显示图像参数设置对话框"""  # 方法说明：用于打开像素密度和时间间隔设置窗口
        dialog = ImageParamsDialog(self)  # 创建图像参数设置对话框对象，父窗口为当前主窗口
        if dialog.exec_() == QDialog.Accepted:  # 执行对话框并等待用户操作，若点击“确定”
            px_str, time_str = dialog.get_params()  # 从对话框中获取两个输入值（返回字符串）
            try:
                self.pixels_per_meter = float(px_str)  # 将输入的像素密度转换为浮点数
                self.time_interval = float(time_str)  # 将输入的时间间隔转换为浮点数
                QMessageBox.information(  # 弹出信息框，显示设置成功的参数
                    self,
                    "参数已保存",
                    f"参数设置成功：\n像素每米 = {self.pixels_per_meter} px/m\n时间间隔 = {self.time_interval} s",
                    QMessageBox.Ok
                )
            except ValueError:  # 若输入无法转换为数字（非法字符）
                QMessageBox.critical(  # 弹出错误提示框
                    self,
                    "输入错误",
                    "请输入有效的数字参数！",
                    QMessageBox.Ok
                )

    def select_theoretical_calculate_method(self):
        # 第一步：判断前面的步骤是否全部完成
        if not self.check_preconditions_of_theoretical_calculation():
            QMessageBox.warning(self, "前置条件未输入", "图像未引入或图像特征未输入")  # 弹出警告提示
            return
        # 第二步：弹出理论计算输入框，输入理论计算所需要的信息
        dialog = QDialog(self)
        dialog.setWindowTitle("理论计算")
        # 创建布局
        theoretical_calculate_layout = QVBoxLayout()
        # 添加入口流速输入框
        speed_label = QLabel("入口流速:")
        theoretical_calculate_layout.addWidget(speed_label)
        speed_input = QLineEdit()
        theoretical_calculate_layout.addWidget(speed_input)
        # 添加计算方法选项
        calculate_method_layout = QHBoxLayout()
        mlp_method = QRadioButton("格子玻尔兹曼法")
        potential_flow_method = QRadioButton("势流理论法")
        calculate_method_layout.addWidget(mlp_method)
        calculate_method_layout.addWidget(potential_flow_method)
        theoretical_calculate_layout.addLayout(calculate_method_layout)
        # 添加确定和取消按钮
        button_layout = QHBoxLayout()
        ok_button = QPushButton("确定")
        cancel_button = QPushButton("取消")
        button_layout.addWidget(ok_button)
        button_layout.addWidget(cancel_button)
        theoretical_calculate_layout.addLayout(button_layout)
        dialog.setLayout(theoretical_calculate_layout)
        # 连接按钮事件
        def on_ok_clicked():
            try:
                speed = float(speed_input.text())
            except ValueError:
                QMessageBox.warning(dialog, "输入错误", "入口流速必须是一个有效的数字")
                return
            if speed <= 0:
                QMessageBox.warning(dialog, "输入错误", "入口流速必须为正数")
                return
            self.theoretical_calculation_init_speed = speed
            if mlp_method.isChecked():
                self.theoretical_calculation_method = "格子玻尔兹曼法"
            elif potential_flow_method.isChecked():
                self.theoretical_calculation_method = "势流理论法"
            else:
                QMessageBox.warning(dialog, "选择错误", "请选择一种计算方法")
                return
            dialog.close()
        def on_cancel_clicked():
            dialog.close()
        ok_button.clicked.connect(on_ok_clicked)
        cancel_button.clicked.connect(on_cancel_clicked)
        # 显示对话框
        dialog.exec_()

    def execute_calculation(self):  # 执行计算的方法，受“执行计算”按钮触发
        """执行计算按钮功能"""
        if self.pixels_per_meter is None or self.time_interval is None:  # 如果参数未设置
            QMessageBox.warning(  # 弹出警告框提醒用户先设置参数
                self,
                "参数未设置",
                "请先设置图像参数！",
                QMessageBox.Ok
            )
            return  # 中止函数执行

        if len(self.image_paths) % 2 == 0:
            for i in range(0, len(self.image_paths), 2):
                image_path = os.path.dirname(self.image_paths[i])
                save_path = self.output_dir
                frame_a = os.path.basename(self.image_paths[i])
                frame_b = os.path.basename(self.image_paths[i + 1])
                scaling_factor = self.pixels_per_meter * self.time_interval
                self.display_area = [self.right_show_panel.width(), self.right_show_panel.height()]

                # 调用 backend 计算
                self.result_path, self.result_figure_name = beckend.beckend_calculation(
                    image_path, save_path, frame_a, frame_b, scaling_factor,
                    self.mask_shapes, self.display_area, cloud_chart=True
                )

                self.show_result_figure()

                # 将txt文件中的数据导入excel
                self.output_to_excel()

                # 此处进行理论计算
                if self.theoretical_calculation_method is not None:
                    self.theoretical_calculate()
        else:
            QMessageBox.warning(self, "数据量错误", "请导入偶数张图像！")

        # 此处添加实际计算逻辑
        QMessageBox.information(  # 当前为演示用途，仅弹窗提示“执行成功”
            self,
            "计算完成",
            "执行成功！\n\n（当前为演示功能）",
            QMessageBox.Ok
        )

    def add_image_pair(self):  # 添加图像对的方法（用户选择两帧图像用于配对处理），选择一对图像 用于之后piv分析
        # 获取初始目录（使用最近访问的目录或默认目录）
        init_dir = QDir.homePath() if not self.image_paths else os.path.dirname(self.image_paths[-1])
        # 如果尚未导入图像，则使用用户主目录；否则使用上一次导入图像的路径

        # 选择两个文件
        files, _ = QFileDialog.getOpenFileNames(  # 打开文件选择对话框，允许多选文件
            self,
            "添加图像",  # 对话框标题
            init_dir,  # 初始路径
            "图像文件 (*.jpg *.jpeg *.png *.tif *.tiff *.bmp)"  # 文件类型过滤器
        )
        if len(files) == 1:  # 如果用户刚好选择了1个文件
            self._add_files(files)  # 调用通用添加方法，将两个文件加入图像列表
        elif files:  # 用户选了文件但不是1个（1个以上）# QMessageBox.warning(self, "选择错误", "请仅选择一张图片！")  # 弹出警告提示-------------------------这里改了一遍，改成不是一个也能显示
            self._add_files(files)

    def show_result_figure(self):
        image_path = os.path.join(self.result_path, self.result_figure_name)
        pixmap = QPixmap(image_path)  # 将结果加载为 QPixmap 对象
        if pixmap.isNull():  # 如果图像无效或加载失败
            print(f"Error: Unable to load image from path: {image_path}")
            raise ValueError("无效的图像文件")  # 抛出异常
        # 自适应显示
        scaled_pixmap = pixmap.scaled(  # 将图像缩放至适配窗口大小
            self.right_show_panel.size(),  # 缩放目标为右侧面板大小
            Qt.KeepAspectRatio,  # 保持原始宽高比
            Qt.SmoothTransformation  # 平滑缩放，提高质量
        )
        self.right_show_panel.setPixmap(scaled_pixmap)  # 设置缩放后的图像到右侧显示区域

    def _add_files(self, files):  # 将文件路径添加到列表中显示，同时保存路径数据
        self.image_paths.extend(files)  # 将新导入的文件路径追加到 image_paths 列表
        self.left_list_widget.addItems([os.path.basename(f) for f in files])  # 在左侧列表中显示每个图像的文件名（不含路径）

    def resizeEvent(self, event):  # 重写窗口大小变动事件
        if self.left_list_widget.currentRow() >= 0:  # 如果当前有选中的图像
            self.show_image(self.left_list_widget.currentRow())  # 刷新图像显示，重新缩放
        super().resizeEvent(event)  # 保留父类的默认行为

    def _handle_apply_mask(self, dialog):  # 处理用户点击“执行掩膜”后的操作
        shape_type = dialog.shape_combo.currentText()  # 获取下拉框中当前选中的掩膜形状
        self.enable_drawing(shape_type)  # 启用绘图模式，并设置形状类型
        dialog.accept()  # 关闭对话框

    def enable_drawing(self, shape_type):  # 启用绘图模式的方法，接受形状类型（矩形或圆形）
        self.current_mask_shape = shape_type  # 保存当前掩膜形状类型
        self.right_show_panel.drawing_enabled = True  # 启用右侧图像区域的绘图模式
        self.right_show_panel.current_shape["type"] = shape_type  # 设置当前绘制形状的类型
        self.right_show_panel.setCursor(Qt.CrossCursor)  # 设置鼠标为十字准星光标（提示绘图状态）
        print(f"已启用绘图模式，当前形状：{shape_type}")  # 控制台打印调试信息

    def clear_masks(self):  # 清除所有已绘制掩膜的方法
        self.mask_shapes.clear()  # 清空掩膜图形列表
        self.right_show_panel.update()  # 刷新右侧绘图区域

    def check_preconditions_of_theoretical_calculation(self):
        if self.image_paths and self.output_dir is not None and self.pixels_per_meter is not None and self.time_interval is not None:
            return True
        else:
            return False

    def output_to_excel(self):
        # 步骤1：查找包含 "Open_PIV_results" 的文件夹
        search_path = os.path.join(self.output_dir, 'Open_PIV_results*')
        result_folders = glob.glob(search_path)

        if not result_folders:
            print("未找到以 'Open_PIV_results' 开头的文件夹")
            return

        # 假设我们只处理找到的第一个符合条件的文件夹
        target_folder = result_folders[0]

        # 步骤2：查找目标文件夹内的 field_A000.txt 文件
        txt_file_path = os.path.join(target_folder, 'field_A000.txt')
        if not os.path.exists(txt_file_path):
            print(f"未找到 {txt_file_path} 文件")
            return

        # 读取 txt 文件的数据
        data = []
        with open(txt_file_path, 'r') as file:
            next(file)  # 跳过第一行
            for line in file:
                values = line.split()
                if len(values) >= 4:  # 确保至少有四个值可以提取
                    data.append([float(v) for v in values[:4]])  # 只提取前四个数据 x, y, u, v

        # 步骤3：准备写入 Excel 文件
        excel_file_path = os.path.join(self.output_dir, '分析结果.xlsx')
        df_new = pd.DataFrame(data, columns=['x', 'y', 'u', 'v'])

        try:
            # 如果文件已存在，则加载并找到下一个空列
            df_existing = pd.read_excel(excel_file_path, sheet_name='Sheet1', engine='openpyxl')
            start_col = len(df_existing.columns) + (1 if len(df_existing.columns) % 5 == 0 else 0) + 1 # 计算起始列位置
        except FileNotFoundError:
            # 文件不存在时创建新文件
            df_existing = pd.DataFrame()
            start_col = 0  # 从第0列开始

        with pd.ExcelWriter(excel_file_path, mode='w', engine='openpyxl') as writer:
            # 如果文件已经存在，则先写入现有数据
            if not df_existing.empty:
                df_existing.to_excel(writer, sheet_name='Sheet1', index=False, startrow=0, startcol=0)

            # 写入新的数据
            df_new.to_excel(writer, sheet_name='Sheet1', index=False, startrow=0, startcol=start_col, header=True)

            # 添加表头
            workbook = writer.book
            worksheet = writer.sheets['Sheet1']
            for col_num, value in enumerate(['x', 'y', 'u', 'v'], start=start_col):
                worksheet.cell(row=1, column=col_num + 1, value=value)

    def theoretical_calculate(self):
        # 第一步，先拿到拍摄区域的宽高，还有障碍物的大小位置
        area_width, area_height, obstacle, x1, y1, x2, y2 = self.get_obstacle_location()


    def get_obstacle_location(self):
        image_path = os.path.dirname(self.image_paths[0])
        frame_a = os.path.basename(self.image_paths[0])
        frame_a = Image.open(os.path.join(image_path, frame_a))
        figure_width, figure_height = frame_a.size
        area_width = figure_width/self.pixels_per_meter
        area_height = figure_height/self.pixels_per_meter

        obstacle = "矩形"
        for shape in self.mask_shapes:
            if shape["type"] == "圆形":
                obstacle = "圆形"
                rect = self.mask_shapes[0]["rect"]
                x1 = rect.center().x()  # 圆心x
                y1 = rect.center().y()  # 圆心y
                radius_width = rect.width() / 2  # 水平半径
                radius_height = rect.height() / 2  # 垂直半径
                display_width = self.display_area[0]
                display_height = self.display_area[1]
                if figure_width / figure_height > display_width / display_height:
                    text_x1 = x1 / display_width * figure_width / self.pixels_per_meter
                    text_y1 = figure_height / self.pixels_per_meter - (y1 - (
                                display_height - figure_height * display_width / figure_width) / 2) / figure_height * figure_width / display_width * figure_height / self.pixels_per_meter
                    text_radius_width = radius_width / display_width * figure_width / self.pixels_per_meter
                    text_radius_height = radius_height / display_width * figure_width / self.pixels_per_meter
                else:
                    text_x1 = (x1 - (
                                display_width - figure_width * display_height / figure_height) / 2) / figure_width * figure_height / display_height * figure_width / self.pixels_per_meter
                    text_y1 = figure_height / self.pixels_per_meter - y1 / display_height * figure_height / self.pixels_per_meter  # y轴调换过来了，所以要前面用一个总长来减
                    text_radius_width = radius_width / display_height * figure_height / self.pixels_per_meter
                    text_radius_height = radius_height / display_height * figure_height / self.pixels_per_meter
                return area_width, area_height, obstacle, text_x1, text_y1, text_radius_width, text_radius_height

        rect = self.mask_shapes[0]["rect"]
        # 获取左上角和右下角坐标
        top_left = rect.topLeft()  # QPoint
        bottom_right = rect.bottomRight()  # QPoint
        x1, y1 = top_left.x(), top_left.y()
        x2, y2 = bottom_right.x(), bottom_right.y()
        display_width = self.display_area[0]
        display_height = self.display_area[1]
        if figure_width/figure_height > display_width/display_height:
            text_x1 = x1/display_width*figure_width/self.pixels_per_meter          # （*figure_width/self.pixels_per_meter）前面的是相对图片的xy长，乘以这个数之后得到text文件中的xy
            text_x2 = x2/display_width*figure_width/self.pixels_per_meter
            text_y1 = figure_height/self.pixels_per_meter - (y1 - (display_height - figure_height*display_width/figure_width)/2)/figure_height*figure_width/display_width*figure_height/self.pixels_per_meter
            text_y2 = figure_height/self.pixels_per_meter - (y2 - (display_height - figure_height*display_width/figure_width)/2)/figure_height*figure_width/display_width*figure_height/self.pixels_per_meter
        else:
            text_x1 = (x1 - (display_width - figure_width*display_height/figure_height)/2)/figure_width*figure_height/display_height*figure_width/self.pixels_per_meter
            text_x2 = (x2 - (display_width - figure_width*display_height/figure_height)/2)/figure_width*figure_height/display_height*figure_width/self.pixels_per_meter
            text_y1 = figure_height/self.pixels_per_meter - y1/display_height*figure_height/self.pixels_per_meter     # y轴调换过来了，所以要前面用一个总长来减
            text_y2 = figure_height/self.pixels_per_meter - y2/display_height*figure_height/self.pixels_per_meter
        return area_width, area_height, obstacle, text_x1, text_y1, text_x2, text_y2


if __name__ == '__main__':  # 判断当前模块是否为主程序入口（被直接运行而非作为模块导入）
    app = QApplication(sys.argv)  # 创建一个应用程序对象 app，传入命令行参数 sys.argv（用于支持控制台参数传递）
    ex = ImageBrowser()  # 创建 ImageBrowser 类的实例，也就是我们开发的主窗口对象
    ex.show()  # 显示主窗口，使其可见
    sys.exit(app.exec_())  # 启动 Qt 事件主循环，直到应用退出。返回退出码，传给系统





# import sys  # 导入sys模块，用于访问与Python解释器相关的变量和函数，如sys.argv用于获取命令行参数
# import os  # 导入os模块，用于进行操作系统交互，比如路径处理、文件遍历等
# from PyQt5.QtWidgets import (QApplication, QWidget, QVBoxLayout, QHBoxLayout, QDialog,
#                              QPushButton, QListWidget, QLabel, QFileDialog, QComboBox,
#                              QMessageBox, QSizePolicy, QSplitter, QDialogButtonBox,
#                              QLineEdit, QFormLayout, QRadioButton)
# # 从PyQt5.QtWidgets模块导入多个GUI组件和布局控件，用于构建图形界面，如应用窗口、按钮、列表、对话框、输入框等
# from PyQt5.QtCore import Qt, QDir, QPoint, QRect
# # 从PyQt5.QtCore模块导入核心类，Qt用于定义常量（如对齐方式、鼠标按钮等），QDir处理目录操作，QPoint处理坐标点，QRect处理矩形区域
# from PyQt5.QtGui import QPixmap, QPainter, QPen, QColor, QCursor
# # 从PyQt5.QtGui模块导入图形处理相关的类，QPixmap用于图像显示，QPainter用于绘图，QPen设置画笔，QColor设置颜色，QCursor设置光标
# import beckend
# from PIL import Image
# import glob
# import os
# import pandas as pd
#
#
# #以下是图像设置的 操作
# class ImageParamsDialog(QDialog):   # 图像参数设置对话框
#     def __init__(self, parent=None):  # 构造函数，初始化对话框，可以接受一个父窗口对象
#         super().__init__(parent)  # 调用父类的构造方法，确保对话框正确初始化
#         self.setWindowTitle("图像参数设置")  # 设置对话框标题为“图像参数设置”
#         layout = QVBoxLayout(self)  # 创建一个垂直布局管理器，并将其设为当前对话框的主布局
#         # 创建表单布局
#         form_layout = QFormLayout()  # 创建一个表单布局对象（label + 控件形式）
#         self.pixels_input = QLineEdit()  # 创建一个文本输入框，用于输入“像素每米”的数值
#         self.time_input = QLineEdit()  # 创建一个文本输入框，用于输入“时间差”的数值
#         form_layout.addRow("像素每米（px/m）：", self.pixels_input)  # 向表单中添加一行标签和输入框，提示用户输入像素密度
#         form_layout.addRow("时间差（s）：", self.time_input)  # 添加第二行标签和输入框，提示用户输入帧之间的时间差
#         layout.addLayout(form_layout)  # 将表单布局添加到主垂直布局中
#
#         # 按钮组
#         self.btn_box = QDialogButtonBox(QDialogButtonBox.Ok | QDialogButtonBox.Cancel)  # 创建标准的对话框按钮组，包含“确定”和“取消”按钮
#         layout.addWidget(self.btn_box)  # 将按钮组添加到主布局中
#         self.btn_box.accepted.connect(self.accept)  # 将“确定”按钮的点击事件连接到QDialog自带的accept()槽函数（关闭对话框并返回Accepted）
#         self.btn_box.rejected.connect(self.reject)  # 将“取消”按钮的点击事件连接到reject()槽函数（关闭对话框并返回Rejected）
#
#     def get_params(self):                       # 定义一个公共方法，用于获取用户输入的两个参数
#         """返回输入参数的元组（像素每米, 时间差）"""  # 方法说明文档，说明返回值为一个包含两个文本值的元组
#         return (self.pixels_input.text(), self.time_input.text())  # 获取两个输入框中的文本并返回为元组
# #以下是掩膜的操作
# class MaskDialog(QDialog):  # 点击掩膜后设置掩膜的对话框，继承自 QDialog（对话框类）
#     def __init__(self, parent=None):  # 构造函数，接受一个可选的父窗口对象
#         super().__init__(parent)  # 调用父类构造函数，初始化对话框
#         self.setWindowTitle("掩膜设置")  # 设置对话框窗口的标题为“掩膜设置”
#         self.layout = QVBoxLayout(self)  # 创建一个垂直布局管理器作为主布局，并设置给该对话框
#
#         # 形状选择
#         self.shape_combo = QComboBox()  # 创建一个下拉框组件，用于选择掩膜的形状（例如矩形、圆形）
#         self.shape_combo.addItems(["矩形", "圆形"])  # 将可选项“矩形”和“圆形”添加到下拉框中
#         self.layout.addWidget(self.shape_combo)  # 将下拉框控件添加到垂直布局中
#         # 操作按钮
#         self.btn_box = QDialogButtonBox()  # 创建一个按钮盒子（用于容纳多个按钮），这里不使用标准按钮类型
#         self.btn_apply = QPushButton("执行掩膜")  # 创建一个普通按钮，文本为“执行掩膜”
#         self.btn_clear = QPushButton("清除掩膜")  # 创建另一个普通按钮，文本为“清除掩膜”
#         self.btn_box.addButton(self.btn_apply, QDialogButtonBox.ActionRole)  # 将“执行掩膜”按钮添加到按钮盒子中，指定角色为自定义操作
#         self.btn_box.addButton(self.btn_clear, QDialogButtonBox.ActionRole)  # 将“清除掩膜”按钮也添加到按钮盒子中
#         self.layout.addWidget(self.btn_box)  # 将按钮盒子添加到垂直主布局中
#
# class DrawLabel(QLabel):  # 定义一个自定义标签类 DrawLabel，继承自 QLabel，用于图像显示与掩膜绘制
#     def __init__(self, main_window):  # 构造函数，接收主窗口作为参数，便于访问全局状态和数据
#         super().__init__(main_window)  # 调用父类构造函数，并将主窗口设置为父对象
#         self.main_window = main_window  # 保存主窗口的引用，用于访问掩膜数据、当前形状等
#         self.drawing_enabled = False  # 初始化绘图模式标志，默认不启用绘图
#         self.start_point = QPoint()  # 初始化起始点为QPoint对象，用于记录绘图起点
#         self.current_shape = {"type": None, "rect": QRect()}  # 当前正在绘制的形状信息，包含类型和矩形区域
#         self.setMouseTracking(True)  # 启用鼠标跟踪，即使没有按下按钮也能触发 mouseMoveEvent
#         self.drag_mode = False  # 初始化拖动模式标志，默认不启用拖动
#         self.drag_start_pos = QPoint()  # 拖动起始位置，用于计算偏移量
#     def mousePressEvent(self, event):  # 重写鼠标按下事件，用于开始绘图或拖动图形
#         if self.drawing_enabled and event.button() == Qt.LeftButton:  # 如果当前启用了绘图模式，且按下的是鼠标左键
#             self.start_point = event.pos()  # 记录鼠标按下的起始位置（绘图起点）
#             self.current_shape["type"] = self.main_window.current_mask_shape  # 设置当前绘制图形的类型（矩形或圆形）
#             self.current_shape["rect"] = QRect(self.start_point, self.start_point)  # 初始化一个起点到自身的矩形区域
#             self.update()  # 请求重绘，触发 paintEvent()，绘制当前形状预览
#         else:  # 若未启用绘图模式，或不是左键点击，进入图形选择/拖动判断流程
#             # 检查是否点击现有图形
#             for i, shape in enumerate(self.main_window.mask_shapes):  # 遍历所有已绘制的图形
#                 if self.check_point_in_shape(event.pos(), shape):  # 如果点击位置在该图形内
#                     self.main_window.selected_shape_index = i  # 设置为当前选中的图形索引
#                     self.drag_start_pos = event.pos()  # 记录拖动起始位置
#                     self.drag_mode = True  # 启用拖动模式
#                     break  # 只选择第一个命中的图形
#
#     def mouseMoveEvent(self, event):  # 重写鼠标移动事件
#         if self.drawing_enabled and event.buttons() & Qt.LeftButton:  # 如果处于绘图模式并按住鼠标左键
#             self.current_shape["rect"] = QRect(  # 更新当前绘制图形的矩形区域
#                 self.start_point, event.pos()).normalized()  # 使用起点和当前位置构造矩形，并调用normalized保证方向一致（左上到右下）
#             self.update()  # 请求重绘，实时显示正在绘制的形状
#         elif self.drag_mode:  # 如果处于拖动模式
#             offset = event.pos() - self.drag_start_pos  # 计算当前位置相对于拖动起始点的偏移量
#             shape = self.main_window.mask_shapes[self.main_window.selected_shape_index]  # 获取当前选中的图形对象
#             shape["rect"].translate(offset)  # 将图形矩形区域平移指定的偏移量
#             self.drag_start_pos = event.pos()  # 更新拖动起始位置为当前鼠标位置，便于连续拖动
#             self.update()  # 重绘，显示图形的新位置
#
#     def mouseReleaseEvent(self, event):  # 重写鼠标释放事件
#         if self.drawing_enabled:  # 如果处于绘图模式
#             if self.current_shape["type"]:  # 如果当前形状类型不为空（已经设置过）
#                 self.main_window.mask_shapes.append(self.current_shape.copy())  # 将当前绘制完成的图形添加到主窗口的图形列表中
#                 self.current_shape["type"] = None  # 重置当前图形类型为空，表示绘图结束
#                 self.drawing_enabled = False  # 禁用绘图模式
#                 self.setCursor(Qt.ArrowCursor)  # 设置光标恢复为默认箭头
#         self.drag_mode = False  # 不管是否绘图，释放后都关闭拖动模式
#
#     def mouseDoubleClickEvent(self, event):  # 重写鼠标双击事件
#         if event.button() == Qt.RightButton:  # 如果是鼠标右键双击
#             for i, shape in enumerate(self.main_window.mask_shapes):  # 遍历所有已绘制图形
#                 if self.check_point_in_shape(event.pos(), shape):  # 如果当前双击位置在图形内
#                     del self.main_window.mask_shapes[i]  # 从图形列表中删除该图形
#                     self.update()  # 请求重绘，更新画面
#                     break  # 删除第一个命中的图形后就退出循环
#
#     def check_point_in_shape(self, point, shape):  # 自定义函数，检查某个坐标点point是否落在shape图形内部
#         if shape["type"] == "矩形":  # 如果图形类型是矩形
#             return shape["rect"].contains(point)  # 使用QRect的contains方法判断点是否在矩形内，返回True/False
#         elif shape["type"] == "圆形":  # 如果图形类型是圆形
#             center = shape["rect"].center()  # 获取图形矩形区域的中心点，作为圆心
#             radius = shape["rect"].width() / 2  # 以矩形宽度的一半作为半径（默认圆为正方形内切）
#             return (point - center).manhattanLength() <= radius  # 使用曼哈顿距离近似判断点是否在圆形范围内
#
#     def paintEvent(self, event):  # 重写 paintEvent 函数，负责绘制背景图和掩膜图形
#         super().paintEvent(event)  # 调用父类的绘图事件，确保基础图像被正常绘制
#         if self.pixmap():  # 如果当前 QLabel 有图像（QPixmap）
#             scaled_pixmap = self.pixmap().scaled(  # 将图像缩放到适应窗口大小
#                 self.size(),  # 当前窗口大小
#                 Qt.KeepAspectRatio,  # 保持图像宽高比
#                 Qt.SmoothTransformation  # 使用平滑变换提高图像质量
#             )
#             self.setPixmap(scaled_pixmap)  # 设置缩放后的图像回标签中进行显示
#
#         super().paintEvent(event)  # 再次调用父类绘图方法（这一行是多余的重复，通常只需调用一次）
#         qp = QPainter(self)  # 创建一个 QPainter 绘图对象，绑定到当前标签组件上
#         qp.setPen(QPen(QColor(255, 0, 0, 150), 2))  # 设置画笔为红色半透明，线宽为2像素
#         qp.setBrush(QColor(255, 0, 0, 50))  # 设置填充颜色为红色透明（遮罩效果）
#
#         # 绘制已有图形
#         for shape in self.main_window.mask_shapes:  # 遍历所有已经保存的掩膜图形
#             if shape["type"] == "矩形":  # 如果是矩形
#                 qp.drawRect(shape["rect"])  # 使用QPainter绘制矩形
#             elif shape["type"] == "圆形":  # 如果是圆形
#                 qp.drawEllipse(shape["rect"])  # 使用QPainter绘制圆形（以矩形边界为外接框）
#
#         # 绘制当前正在绘制的图形
#         if self.current_shape["type"]:  # 如果当前有正在绘制的图形
#             if self.current_shape["type"] == "矩形":  # 判断类型是否为矩形
#                 qp.drawRect(self.current_shape["rect"])  # 绘制当前矩形
#             elif self.current_shape["type"] == "圆形":  # 判断类型是否为圆形
#                 qp.drawEllipse(self.current_shape["rect"])  # 绘制当前圆形
#
# class ImageBrowser(QWidget):  # 定义一个图像浏览器类，继承自 QWidget，用于构建主应用窗口
#     def __init__(self):  # 构造函数，初始化主窗口及相关组件
#         super().__init__()      # 调用 QWidget 的父类构造函数
#         self.initParameter()    # 初始化跟后端连接需要传递的各个参数
#         self.initUI()           # 调用初始化界面方法，创建布局与控件
#
#     def initParameter(self):
#         self.image_paths = []  # 初始化图像路径列表，用于保存所有导入图像的完整路径
#         self.output_dir = None  # 初始化输出目录为 None，用于后续保存输出路径
#         self.result_path = None         # 结果文件夹
#         self.result_figure_name = None      # 结果图像名称
#         self.mask_shapes = []  # 存储所有掩膜图形的列表（包含类型
#         self.drawing = False  # 是否处于绘图模式和矩形位置）
#         self.current_shape = None  # 当前正在绘制的掩膜形状（暂时未使用，可扩展）（备用变量）
#         self.drag_mode = False  # 是否处于拖动图形模式
#         self.selected_shape_index = -1  # 当前选中的图形索引（默认无选中）
#         self.pixels_per_meter = None  # 初始化像素密度参数（单位 px/m）
#         self.time_interval = None  # 初始化时间间隔参数（单位 s）
#         self.display_area = []  # 显示框的宽度和高度
#         self.theoretical_calculation_init_speed = None  # 为了理论计算所输入的入口流速
#         self.theoretical_calculation_method = None  # 理论计算的方法
#
#     def initUI(self):  # 初始化主界面的方法，设置所有控件和布局
#         self.setWindowTitle('图像浏览器')  # 设置窗口标题
#         self.setGeometry(100, 100, 1000, 600)  # 设置窗口初始位置和大小（x=100, y=100, 宽=1000，高=600）
#
#         # 左侧面板
#         left_panel = QWidget()  # 创建左侧控制面板容器
#         left_layout = QVBoxLayout(left_panel)  # 为左侧面板创建垂直布局
#         left_layout.setContentsMargins(5, 5, 5, 5)  # 设置边距为5
#         left_layout.setSpacing(10)  # 设置控件之间的垂直间距为10像素
#
#         # 右侧面板
#         right_container = QWidget()  # 创建右侧容器控件，用于包含图像显示区与按钮面板
#         right_layout = QVBoxLayout(right_container)  # 创建垂直布局用于右侧容器
#         right_layout.setContentsMargins(0, 0, 0, 0)  # 设置布局边距为0
#         right_layout.setSpacing(5)  # 设置控件之间的间距为5像素
#
#         # 主布局使用水平分割器
#         main_splitter = QSplitter(Qt.Horizontal)  # 创建水平分割器，将窗口分为左右两部分
#         main_splitter.addWidget(left_panel)  # 将左侧控制面板加入水平分割器
#         main_splitter.addWidget(right_container)  # 将右侧容器加入水平分割器
#         main_splitter.setSizes([250, 750])  # 设置左右分割初始比例：左 250px，右 750px（大约 1:3）
#
#         # 左侧面板的图像列表框
#         self.left_list_widget = QListWidget()  # 创建图像文件列表控件
#         left_layout.addWidget(self.left_list_widget)  # 将图像列表添加到左侧布局中
#         # 左侧面板的按钮
#         left_btn_layout = QHBoxLayout()  # 创建一个水平布局，用于排列添加和清空按钮
#         self.btn_add = QPushButton("添加图像")  # 创建一个“添加图像”按钮
#         self.btn_add.setFixedHeight(30)  # 设置按钮高度为35像素
#         self.btn_clear = QPushButton("清空列表")  # 创建一个“清空列表”按钮
#         self.btn_clear.setFixedHeight(30)  # 设置按钮高度为35像素
#         left_btn_layout.addWidget(self.btn_add)  # 将“添加图像”按钮添加到按钮水平布局中
#         left_btn_layout.addWidget(self.btn_clear)  # 将“清空列表”按钮添加到按钮水平布局中
#         left_layout.addLayout(left_btn_layout)  # 将按钮布局添加到左侧主布局
#
#         # 右侧显示区域
#         self.right_show_panel = DrawLabel(self)  # 创建自定义的图像显示组件 DrawLabel（支持绘制掩膜），并将主窗口作为参数传入
#         self.right_show_panel.setAlignment(Qt.AlignCenter)  # 设置图像居中显示
#         self.right_show_panel.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)  # 设置自动伸缩策略，填满剩余空间
#         # self.right_show_panel.setStyleSheet("background-color: #f0f0f0;")  # 设置背景色为浅灰色（便于区分图像区域）
#         right_layout.addWidget(self.right_show_panel, 1)  # 将右侧图像显示组件添加到右侧垂直布局中，占用主空间
#         # 右侧面板的按钮
#         right_btn_layout = QHBoxLayout()  # 创建一个水平布局用于容纳按钮
#         right_btn_layout.setContentsMargins(5, 5, 5, 5)  # 设置内边距为 5 像素
#         self.btn_output = QPushButton("输出路径")  # 创建“输出路径”按钮
#         self.btn_output.setFixedHeight(30)  # 设置按钮高度为30像素
#         self.btn_mask = QPushButton("掩膜操作")  # 创建“掩膜操作”按钮（用于绘制和清除掩膜）
#         self.btn_mask.setFixedHeight(30)  # 设置按钮高度为30像素
#         self.btn_size = QPushButton("图像尺寸")  # 创建“图像尺寸”按钮（用于设置像素密度与时间差）
#         self.btn_size.setFixedHeight(30)  # 设置按钮高度为30像素
#         # self.btn_method = QPushButton("理论计算")  # 创建“图像尺寸”按钮（用于设置像素密度与时间差）
#         # self.btn_method.setFixedHeight(30)  # 设置按钮高度为30像素
#         self.btn_process = QPushButton("执行计算")  # 创建“执行计算”按钮（执行分析或演示操作）
#         self.btn_process.setFixedHeight(30)  # 设置按钮高度为30像素
#         btn_style = "QPushButton {padding:5px; font-size:12px; min-width:70px;}"  # 设置统一的按钮样式（填充、字体大小、最小宽度）
#         self.btn_output.setStyleSheet(btn_style)  # 应用样式
#         self.btn_mask.setStyleSheet(btn_style)
#         self.btn_size.setStyleSheet(btn_style)
#         # self.btn_method.setStyleSheet(btn_style)
#         self.btn_process.setStyleSheet(btn_style)
#         right_btn_layout.addWidget(self.btn_output)  # 添加“输出路径”按钮
#         right_btn_layout.addWidget(self.btn_mask)  # 添加“掩膜操作”按钮
#         right_btn_layout.addWidget(self.btn_size)  # 添加“图像尺寸”按钮
#         # right_btn_layout.addWidget(self.btn_method)  # 添加“理论计算”按钮
#         right_btn_layout.addWidget(self.btn_process)  # 添加“执行计算”按钮
#         right_btn_layout.addStretch(1)  # 添加弹性空白项，使按钮靠左排列，右侧留白
#         right_layout.addLayout(right_btn_layout)  # 将控制面板添加到底部的右侧垂直布局中
#
#         # 主窗口布局
#         main_layout = QHBoxLayout(self)  # 设置主窗口为水平布局（实际上只放一个 main_splitter）
#         main_layout.addWidget(main_splitter)  # 添加左右分割器
#
#         # 连接信号
#         self.btn_add.clicked.connect(self.show_selection_dialog)  # “添加图像”按钮连接到图像添加对话框方法
#         self.btn_clear.clicked.connect(self.clear_list)  # “清空列表”按钮连接到清空方法
#         self.left_list_widget.currentRowChanged.connect(self.show_image)  # 图像列表选择项改变时，显示对应图像
#         self.btn_output.clicked.connect(self.select_output_dir)  # 连接按钮点击信号到选择输出目录的方法
#         self.btn_mask.clicked.connect(self.show_mask_dialog)  # 将“掩膜操作”按钮与 show_mask_dialog 方法连接
#         self.btn_size.clicked.connect(self.show_image_params_dialog)  # “图像尺寸”按钮连接到图像参数对话框
#         # self.btn_method.clicked.connect(self.select_theoretical_calculate_method)
#         self.btn_process.clicked.connect(self.execute_calculation)  # “执行计算”按钮连接到计算执行方法
#
#     def show_selection_dialog(self):  # 显示添加图像的方式选择对话框（图像对 or 批量添加）
#         if len(self.image_paths) == 2:      # 判断显示区域是否已经有两个图像
#             QMessageBox.warning(self, "选择错误", "请先清除列表")  # 弹出警告提示
#             return
#         # 第一步：显示选择对话框
#         choice = QMessageBox.question(  # 弹出一个问题对话框，询问用户添加图像的方式
#             self,
#             '添加图像',
#             '请依次添加第一帧、第二帧图片\n一次只能导入一张图片',
#             QMessageBox.Yes | QMessageBox.Cancel  # 三个选项：是、否、取消
#         )
#         if choice == QMessageBox.Yes:  # 用户选择“是” → 添加图像对（两帧）
#             self.add_image_pair()  # 调用添加图像对方法
#         # Cancel则不执行任何操作
#
#     def clear_list(self):  # 清空图像列表的方法
#         self.image_paths.clear()  # 清空图像路径列表
#         self.left_list_widget.clear()  # 清空左侧图像文件名列表
#         self.right_show_panel.clear()  # 清空图像显示区域
#
#     def show_image(self, index):  # 显示当前选中的图像（列表中第 index 项）
#         if 0 <= index < len(self.image_paths):  # 检查索引是否有效
#             try:
#                 pixmap = QPixmap(self.image_paths[index])  # 使用路径加载图像为 QPixmap 对象
#                 if pixmap.isNull():  # 如果图像无效或加载失败
#                     raise ValueError("无效的图像文件")  # 抛出异常
#                 # 自适应显示
#                 scaled_pixmap = pixmap.scaled(  # 将图像缩放至适配窗口大小
#                     self.right_show_panel.size(),  # 缩放目标为右侧面板大小
#                     Qt.KeepAspectRatio,  # 保持原始宽高比
#                     Qt.SmoothTransformation  # 平滑缩放，提高质量
#                 )
#                 self.right_show_panel.setPixmap(scaled_pixmap)  # 设置缩放后的图像到右侧显示区域
#             except Exception as e:  # 捕获异常
#                 QMessageBox.critical(self, "错误", f"无法加载图像：\n{str(e)}")  # 弹出错误提示框
#
#     def select_output_dir(self):  # 选择输出路径的对话框
#         """选择输出路径"""
#         dir_path = QFileDialog.getExistingDirectory(  # 打开文件夹选择对话框
#             self,
#             "选择输出文件夹",
#             QDir.homePath(),  # 默认路径为用户主目录
#             QFileDialog.ShowDirsOnly  # 仅允许选择文件夹
#         )
#         if dir_path:  # 如果用户选择了路径
#             self.output_dir = dir_path  # 保存路径
#             QMessageBox.information(  # 弹出提示框确认路径设置成功
#                 self,
#                 "路径设置成功",
#                 f"输出路径已设置为：\n{dir_path}",
#                 QMessageBox.Ok
#             )
#
#     def show_mask_dialog(self):  # 显示掩膜设置对话框（选择图形 + 清除）
#         dialog = MaskDialog(self)  # 创建掩膜对话框对象，主窗口为父窗口
#         dialog.btn_apply.clicked.connect(  # 连接“执行掩膜”按钮点击事件
#             lambda: self._handle_apply_mask(dialog)  # 使用 lambda 表达式调用处理函数并传入当前对话框
#         )
#         dialog.btn_clear.clicked.connect(self.clear_masks)  # 连接“清除掩膜”按钮点击事件
#         dialog.exec_()  # 显示对话框，阻塞主界面，等待用户操作
#
#     def show_image_params_dialog(self):  # 显示图像参数设置对话框的方法
#         """显示图像参数设置对话框"""  # 方法说明：用于打开像素密度和时间间隔设置窗口
#         dialog = ImageParamsDialog(self)  # 创建图像参数设置对话框对象，父窗口为当前主窗口
#         if dialog.exec_() == QDialog.Accepted:  # 执行对话框并等待用户操作，若点击“确定”
#             px_str, time_str = dialog.get_params()  # 从对话框中获取两个输入值（返回字符串）
#             try:
#                 self.pixels_per_meter = float(px_str)  # 将输入的像素密度转换为浮点数
#                 self.time_interval = float(time_str)  # 将输入的时间间隔转换为浮点数
#                 QMessageBox.information(  # 弹出信息框，显示设置成功的参数
#                     self,
#                     "参数已保存",
#                     f"参数设置成功：\n像素每米 = {self.pixels_per_meter} px/m\n时间间隔 = {self.time_interval} s",
#                     QMessageBox.Ok
#                 )
#             except ValueError:  # 若输入无法转换为数字（非法字符）
#                 QMessageBox.critical(  # 弹出错误提示框
#                     self,
#                     "输入错误",
#                     "请输入有效的数字参数！",
#                     QMessageBox.Ok
#                 )
#
#     def select_theoretical_calculate_method(self):
#         # 第一步：判断前面的步骤是否全部完成
#         if not self.check_preconditions_of_theoretical_calculation():
#             QMessageBox.warning(self, "前置条件未输入", "图像未引入或图像特征未输入")  # 弹出警告提示
#             return
#         # 第二步：弹出理论计算输入框，输入理论计算所需要的信息
#         dialog = QDialog(self)
#         dialog.setWindowTitle("理论计算")
#         # 创建布局
#         theoretical_calculate_layout = QVBoxLayout()
#         # 添加入口流速输入框
#         speed_label = QLabel("入口流速:")
#         theoretical_calculate_layout.addWidget(speed_label)
#         speed_input = QLineEdit()
#         theoretical_calculate_layout.addWidget(speed_input)
#         # 添加计算方法选项
#         calculate_method_layout = QHBoxLayout()
#         mlp_method = QRadioButton("格子玻尔兹曼法")
#         potential_flow_method = QRadioButton("势流理论法")
#         calculate_method_layout.addWidget(mlp_method)
#         calculate_method_layout.addWidget(potential_flow_method)
#         theoretical_calculate_layout.addLayout(calculate_method_layout)
#         # 添加确定和取消按钮
#         button_layout = QHBoxLayout()
#         ok_button = QPushButton("确定")
#         cancel_button = QPushButton("取消")
#         button_layout.addWidget(ok_button)
#         button_layout.addWidget(cancel_button)
#         theoretical_calculate_layout.addLayout(button_layout)
#         dialog.setLayout(theoretical_calculate_layout)
#         # 连接按钮事件
#         def on_ok_clicked():
#             try:
#                 speed = float(speed_input.text())
#             except ValueError:
#                 QMessageBox.warning(dialog, "输入错误", "入口流速必须是一个有效的数字")
#                 return
#             if speed <= 0:
#                 QMessageBox.warning(dialog, "输入错误", "入口流速必须为正数")
#                 return
#             self.theoretical_calculation_init_speed = speed
#             if mlp_method.isChecked():
#                 self.theoretical_calculation_method = "格子玻尔兹曼法"
#             elif potential_flow_method.isChecked():
#                 self.theoretical_calculation_method = "势流理论法"
#             else:
#                 QMessageBox.warning(dialog, "选择错误", "请选择一种计算方法")
#                 return
#             dialog.close()
#         def on_cancel_clicked():
#             dialog.close()
#         ok_button.clicked.connect(on_ok_clicked)
#         cancel_button.clicked.connect(on_cancel_clicked)
#         # 显示对话框
#         dialog.exec_()
#
#     def execute_calculation(self):  # 执行计算的方法，受“执行计算”按钮触发
#         """执行计算按钮功能"""
#         if self.pixels_per_meter is None or self.time_interval is None:  # 如果参数未设置
#             QMessageBox.warning(  # 弹出警告框提醒用户先设置参数
#                 self,
#                 "参数未设置",
#                 "请先设置图像参数！",
#                 QMessageBox.Ok
#             )
#             return  # 中止函数执行
#
#         if len(self.image_paths) % 2 == 0:
#             for i in range(0, len(self.image_paths), 2):
#                 image_path = os.path.dirname(self.image_paths[i])
#                 save_path = self.output_dir
#                 frame_a = os.path.basename(self.image_paths[i])
#                 frame_b = os.path.basename(self.image_paths[i + 1])
#                 scaling_factor = self.pixels_per_meter * self.time_interval
#                 self.display_area = [self.right_show_panel.width(), self.right_show_panel.height()]
#
#                 # 调用 backend 计算
#                 self.result_path, self.result_figure_name = beckend.beckend_calculation(
#                     image_path, save_path, frame_a, frame_b, scaling_factor,
#                     self.mask_shapes, self.display_area, cloud_chart=True
#                 )
#
#                 self.show_result_figure()
#
#                 # 将txt文件中的数据导入excel
#                 self.output_to_excel()
#
#                 # 此处进行理论计算
#                 if self.theoretical_calculation_method is not None:
#                     self.theoretical_calculate()
#         else:
#             QMessageBox.warning(self, "数据量错误", "请导入偶数张图像！")
#
#         # 此处添加实际计算逻辑
#         QMessageBox.information(  # 当前为演示用途，仅弹窗提示“执行成功”
#             self,
#             "计算完成",
#             "执行成功！\n\n（当前为演示功能）",
#             QMessageBox.Ok
#         )
#
#     def add_image_pair(self):  # 添加图像对的方法（用户选择两帧图像用于配对处理），选择一对图像 用于之后piv分析
#         # 获取初始目录（使用最近访问的目录或默认目录）
#         init_dir = QDir.homePath() if not self.image_paths else os.path.dirname(self.image_paths[-1])
#         # 如果尚未导入图像，则使用用户主目录；否则使用上一次导入图像的路径
#
#         # 选择两个文件
#         files, _ = QFileDialog.getOpenFileNames(  # 打开文件选择对话框，允许多选文件
#             self,
#             "添加图像",  # 对话框标题
#             init_dir,  # 初始路径
#             "图像文件 (*.jpg *.jpeg *.png *.tif *.tiff *.bmp)"  # 文件类型过滤器
#         )
#         if len(files) == 1:  # 如果用户刚好选择了1个文件
#             self._add_files(files)  # 调用通用添加方法，将两个文件加入图像列表
#         elif files:  # 用户选了文件但不是1个（1个以上）# QMessageBox.warning(self, "选择错误", "请仅选择一张图片！")  # 弹出警告提示-------------------------这里改了一遍，改成不是一个也能显示
#             self._add_files(files)
#
#     def show_result_figure(self):
#         image_path = os.path.join(self.result_path, self.result_figure_name)
#         pixmap = QPixmap(image_path)  # 将结果加载为 QPixmap 对象
#         if pixmap.isNull():  # 如果图像无效或加载失败
#             print(f"Error: Unable to load image from path: {image_path}")
#             raise ValueError("无效的图像文件")  # 抛出异常
#         # 自适应显示
#         scaled_pixmap = pixmap.scaled(  # 将图像缩放至适配窗口大小
#             self.right_show_panel.size(),  # 缩放目标为右侧面板大小
#             Qt.KeepAspectRatio,  # 保持原始宽高比
#             Qt.SmoothTransformation  # 平滑缩放，提高质量
#         )
#         self.right_show_panel.setPixmap(scaled_pixmap)  # 设置缩放后的图像到右侧显示区域
#
#     def _add_files(self, files):  # 将文件路径添加到列表中显示，同时保存路径数据
#         self.image_paths.extend(files)  # 将新导入的文件路径追加到 image_paths 列表
#         self.left_list_widget.addItems([os.path.basename(f) for f in files])  # 在左侧列表中显示每个图像的文件名（不含路径）
#
#     def resizeEvent(self, event):  # 重写窗口大小变动事件
#         if self.left_list_widget.currentRow() >= 0:  # 如果当前有选中的图像
#             self.show_image(self.left_list_widget.currentRow())  # 刷新图像显示，重新缩放
#         super().resizeEvent(event)  # 保留父类的默认行为
#
#     def _handle_apply_mask(self, dialog):  # 处理用户点击“执行掩膜”后的操作
#         shape_type = dialog.shape_combo.currentText()  # 获取下拉框中当前选中的掩膜形状
#         self.enable_drawing(shape_type)  # 启用绘图模式，并设置形状类型
#         dialog.accept()  # 关闭对话框
#
#     def enable_drawing(self, shape_type):  # 启用绘图模式的方法，接受形状类型（矩形或圆形）
#         self.current_mask_shape = shape_type  # 保存当前掩膜形状类型
#         self.right_show_panel.drawing_enabled = True  # 启用右侧图像区域的绘图模式
#         self.right_show_panel.current_shape["type"] = shape_type  # 设置当前绘制形状的类型
#         self.right_show_panel.setCursor(Qt.CrossCursor)  # 设置鼠标为十字准星光标（提示绘图状态）
#         print(f"已启用绘图模式，当前形状：{shape_type}")  # 控制台打印调试信息
#
#     def clear_masks(self):  # 清除所有已绘制掩膜的方法
#         self.mask_shapes.clear()  # 清空掩膜图形列表
#         self.right_show_panel.update()  # 刷新右侧绘图区域
#
#     def check_preconditions_of_theoretical_calculation(self):
#         if self.image_paths and self.output_dir is not None and self.pixels_per_meter is not None and self.time_interval is not None:
#             return True
#         else:
#             return False
#
#     def output_to_excel(self):
#         # 步骤1：查找包含 "Open_PIV_results" 的文件夹
#         search_path = os.path.join(self.output_dir, 'Open_PIV_results*')
#         result_folders = glob.glob(search_path)
#
#         if not result_folders:
#             print("未找到以 'Open_PIV_results' 开头的文件夹")
#             return
#
#         # 假设我们只处理找到的第一个符合条件的文件夹
#         target_folder = result_folders[0]
#
#         # 步骤2：查找目标文件夹内的 field_A000.txt 文件
#         txt_file_path = os.path.join(target_folder, 'field_A000.txt')
#         if not os.path.exists(txt_file_path):
#             print(f"未找到 {txt_file_path} 文件")
#             return
#
#         # 读取 txt 文件的数据
#         data = []
#         with open(txt_file_path, 'r') as file:
#             next(file)  # 跳过第一行
#             for line in file:
#                 values = line.split()
#                 if len(values) >= 4:  # 确保至少有四个值可以提取
#                     data.append([float(v) for v in values[:4]])  # 只提取前四个数据 x, y, u, v
#
#         # 步骤3：准备写入 Excel 文件
#         excel_file_path = os.path.join(self.output_dir, '分析结果.xlsx')
#         df_new = pd.DataFrame(data, columns=['x', 'y', 'u', 'v'])
#
#         try:
#             # 如果文件已存在，则加载并找到下一个空列
#             df_existing = pd.read_excel(excel_file_path, sheet_name='Sheet1', engine='openpyxl')
#             start_col = len(df_existing.columns) + (1 if len(df_existing.columns) % 5 == 0 else 0) + 1 # 计算起始列位置
#         except FileNotFoundError:
#             # 文件不存在时创建新文件
#             df_existing = pd.DataFrame()
#             start_col = 0  # 从第0列开始
#
#         with pd.ExcelWriter(excel_file_path, mode='w', engine='openpyxl') as writer:
#             # 如果文件已经存在，则先写入现有数据
#             if not df_existing.empty:
#                 df_existing.to_excel(writer, sheet_name='Sheet1', index=False, startrow=0, startcol=0)
#
#             # 写入新的数据
#             df_new.to_excel(writer, sheet_name='Sheet1', index=False, startrow=0, startcol=start_col, header=True)
#
#             # 添加表头
#             workbook = writer.book
#             worksheet = writer.sheets['Sheet1']
#             for col_num, value in enumerate(['x', 'y', 'u', 'v'], start=start_col):
#                 worksheet.cell(row=1, column=col_num + 1, value=value)
#
#     def theoretical_calculate(self):
#         # 第一步，先拿到拍摄区域的宽高，还有障碍物的大小位置
#         area_width, area_height, obstacle, x1, y1, x2, y2 = self.get_obstacle_location()
#
#
#     def get_obstacle_location(self):
#         image_path = os.path.dirname(self.image_paths[0])
#         frame_a = os.path.basename(self.image_paths[0])
#         frame_a = Image.open(os.path.join(image_path, frame_a))
#         figure_width, figure_height = frame_a.size
#         area_width = figure_width/self.pixels_per_meter
#         area_height = figure_height/self.pixels_per_meter
#
#         obstacle = "矩形"
#         for shape in self.mask_shapes:
#             if shape["type"] == "圆形":
#                 obstacle = "圆形"
#                 rect = self.mask_shapes[0]["rect"]
#                 x1 = rect.center().x()  # 圆心x
#                 y1 = rect.center().y()  # 圆心y
#                 radius_width = rect.width() / 2  # 水平半径
#                 radius_height = rect.height() / 2  # 垂直半径
#                 display_width = self.display_area[0]
#                 display_height = self.display_area[1]
#                 if figure_width / figure_height > display_width / display_height:
#                     text_x1 = x1 / display_width * figure_width / self.pixels_per_meter
#                     text_y1 = figure_height / self.pixels_per_meter - (y1 - (
#                                 display_height - figure_height * display_width / figure_width) / 2) / figure_height * figure_width / display_width * figure_height / self.pixels_per_meter
#                     text_radius_width = radius_width / display_width * figure_width / self.pixels_per_meter
#                     text_radius_height = radius_height / display_width * figure_width / self.pixels_per_meter
#                 else:
#                     text_x1 = (x1 - (
#                                 display_width - figure_width * display_height / figure_height) / 2) / figure_width * figure_height / display_height * figure_width / self.pixels_per_meter
#                     text_y1 = figure_height / self.pixels_per_meter - y1 / display_height * figure_height / self.pixels_per_meter  # y轴调换过来了，所以要前面用一个总长来减
#                     text_radius_width = radius_width / display_height * figure_height / self.pixels_per_meter
#                     text_radius_height = radius_height / display_height * figure_height / self.pixels_per_meter
#                 return area_width, area_height, obstacle, text_x1, text_y1, text_radius_width, text_radius_height
#
#         rect = self.mask_shapes[0]["rect"]
#         # 获取左上角和右下角坐标
#         top_left = rect.topLeft()  # QPoint
#         bottom_right = rect.bottomRight()  # QPoint
#         x1, y1 = top_left.x(), top_left.y()
#         x2, y2 = bottom_right.x(), bottom_right.y()
#         display_width = self.display_area[0]
#         display_height = self.display_area[1]
#         if figure_width/figure_height > display_width/display_height:
#             text_x1 = x1/display_width*figure_width/self.pixels_per_meter          # （*figure_width/self.pixels_per_meter）前面的是相对图片的xy长，乘以这个数之后得到text文件中的xy
#             text_x2 = x2/display_width*figure_width/self.pixels_per_meter
#             text_y1 = figure_height/self.pixels_per_meter - (y1 - (display_height - figure_height*display_width/figure_width)/2)/figure_height*figure_width/display_width*figure_height/self.pixels_per_meter
#             text_y2 = figure_height/self.pixels_per_meter - (y2 - (display_height - figure_height*display_width/figure_width)/2)/figure_height*figure_width/display_width*figure_height/self.pixels_per_meter
#         else:
#             text_x1 = (x1 - (display_width - figure_width*display_height/figure_height)/2)/figure_width*figure_height/display_height*figure_width/self.pixels_per_meter
#             text_x2 = (x2 - (display_width - figure_width*display_height/figure_height)/2)/figure_width*figure_height/display_height*figure_width/self.pixels_per_meter
#             text_y1 = figure_height/self.pixels_per_meter - y1/display_height*figure_height/self.pixels_per_meter     # y轴调换过来了，所以要前面用一个总长来减
#             text_y2 = figure_height/self.pixels_per_meter - y2/display_height*figure_height/self.pixels_per_meter
#         return area_width, area_height, obstacle, text_x1, text_y1, text_x2, text_y2
#
#
# if __name__ == '__main__':  # 判断当前模块是否为主程序入口（被直接运行而非作为模块导入）
#     app = QApplication(sys.argv)  # 创建一个应用程序对象 app，传入命令行参数 sys.argv（用于支持控制台参数传递）
#     ex = ImageBrowser()  # 创建 ImageBrowser 类的实例，也就是我们开发的主窗口对象
#     ex.show()  # 显示主窗口，使其可见
#     sys.exit(app.exec_())  # 启动 Qt 事件主循环，直到应用退出。返回退出码，传给系统
