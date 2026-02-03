from openpiv import windef
import glob
import os.path
from skimage.io import imread


settings = windef.Settings()

def settings_windowsizes_option(settings):
    figure = imread(
        sorted(glob.glob(os.path.join(os.path.abspath(settings.filepath_images), settings.frame_pattern_a)))[0])
    longer_edge = max(figure.shape[0], figure.shape[1])
    # left_windowsize = longer_edge // 50
    left_windowsize = longer_edge // 50
    option = (left_windowsize * 4, left_windowsize * 2)
    if settings.num_iterations == 3:
        option = (left_windowsize * 4, left_windowsize * 2, left_windowsize)
    elif settings.num_iterations == 4:
        option = (left_windowsize * 4, left_windowsize * 2, left_windowsize, left_windowsize/2)
    return option


def settings_overlap_option(settings):
    figure = imread(
        sorted(glob.glob(os.path.join(os.path.abspath(settings.filepath_images), settings.frame_pattern_a)))[0])
    longer_edge = max(figure.shape[0], figure.shape[1])
    # left_windowsize = longer_edge // 50
    left_windowsize = longer_edge // 50
    option = (left_windowsize * 2, left_windowsize)
    if settings.num_iterations == 3:
        option = (left_windowsize * 2, left_windowsize, left_windowsize/2)
    elif settings.num_iterations == 4:
        option = (left_windowsize * 2, left_windowsize, left_windowsize/2, left_windowsize/4)
    return option


def settings_minmax_uv_disp_option(settings):
    minmax = (settings.windowsizes[settings.num_iterations - 1] - settings.overlap[settings.num_iterations - 1]) * 0.75
    option = (-minmax, minmax)
    return option




