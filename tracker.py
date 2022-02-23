from csv import writer as csvwriter
import numpy as np
from cv2 import CAP_PROP_FPS, VideoCapture
import os
import matplotlib.pyplot as plt
from draw import draw
from scipy import stats
from dlc_generic_analysis.geometries import Line
from math import atan, pi, degrees
import pandas
from typing import List
from tqdm import tqdm


def set_ends(line, cord):
    c = cord[np.logical_not(np.isnan(cord).any(axis=1))]
    y = c[len(c) - 1, 1]
    if line.slope != 0:
        line.end2 = (int((y - line.intercept) / line.slope), int(y))
    else:
        line.end2 = (1, int(y))
    y = c[0][1]
    if line.slope != 0:
        line.end1 = (int((y - line.intercept) / line.slope), int(y))
    else:
        line.end1 = (1, int(y))


def point_array(data_frame: pandas.DataFrame, points: List[str]):
    nd_arrays = list()
    for point in points:
        nd_arrays.append(data_frame[point][["x", "y"]])
    return np.stack(nd_arrays, axis=0)[:, :]


COMMISURE_NAME = "AC"
RIGHT_PT_NAMES = [COMMISURE_NAME, "LC1", "LC2", "LC3", "LC4", "LC5", "LVP"]
LEFT_PT_NAMES = [COMMISURE_NAME, "RC1", "RC2", "RC3", "RC4", "RC5", "RVP"]


class Tracker:
    """
    Creates a tracker object that takes a dataset and can perform various
    calculations on it.
    data: lst[lst[float]]
    output: lst[tuple(float, float)]
    contains marked parts and their corresponding points at each frame.
    """

    def __init__(self, df):
        self.left_points = point_array(df, LEFT_PT_NAMES)
        self.right_points = point_array(df, RIGHT_PT_NAMES)

    def frame_by(self, path, _, outfile, name):
        """Goes through each frame worth of data. Analyses and graphs opening
        angle of vocal cords. Prints summary statistics."""
        print("Analyzing Video Data")
        of = outfile
        # frames dropped
        LC = self.left_points
        RC = self.right_points
        graph = np.zeros(shape=(LC.shape[1], 3))
        left = []
        right = []
        for i in tqdm(range(LC.shape[1])):
            comm = np.logical_not(np.isnan(RC[:, i]).any())
            LC_now = LC[np.logical_not(np.isnan(LC[:, i]).any(axis=1)), i]
            RC_now = RC[np.logical_not(np.isnan(RC[:, i]).any(axis=1)), i]
            cords_there = False
            # Checking Point Validity
            if LC_now.shape[0] >= 3:
                cords_there = True
            if RC_now.shape[0] >= 3:
                cords_there = True
            # Performing angle calculations
            if cords_there:
                angle, lang, left_line, right_line = alt_angle(LC_now, RC_now, comm)
                left.append(left_line)
                right.append(right_line)
                if lang is not None:
                    rang = -(angle * 180 / pi - lang)
                else:
                    rang = None
                graph[i] = np.array([angle, lang, rang])
            else:
                left.append(None)
                right.append(None)
                graph[i] = ([np.nan, np.nan, np.nan])
        dgraph = []  # keep none to show blank space in graph.
        sgraph = []  # remove none to perform statistical analysis.
        for item in graph:
            if item is None:
                dgraph.append(None)
            elif item[0] is not None:
                dgraph.append([item[0] * 180 / pi, item[1], item[2]])
                sgraph.append(item[0] * 180 / pi)
            else:
                dgraph.append(None)
        arr = np.array(sgraph)
        display_graph = []
        count = 0
        for i in range(len(dgraph)):
            if dgraph[i] is None:
                display_graph.append(None)
            elif dgraph[i][0] is None:
                display_graph.append(None)
            elif count >= len(arr):
                display_graph.append(None)
            elif arr[count] > np.percentile(arr, 97):
                display_graph.append(0)
                count += 1
            else:
                display_graph.append(arr[count])
                count += 1

        # Computing velocities and accelerations
        vid = VideoCapture(path)
        frames = vid.get(CAP_PROP_FPS)
        vels = np.zeros(shape=len(dgraph))  # change in angle in degrees / sec
        dif = 1
        for i in range(1, len(dgraph)):
            if dgraph[i] is None or dgraph[i - dif] is None:
                vels[i] = np.nan
            elif dgraph[i][0] is not None and dgraph[i - dif][0] is not None:
                vels[i] = (dgraph[i][0] - dgraph[i - dif][0]) * frames / dif
                dif = 1
            elif dgraph[i - dif][0] is None:
                i += 1
                vels[i] = np.nan
            else:
                vels[i] = np.nan
                i += 1
                dif += 1
        accs = [0]
        dif = 1
        for i in range(1, len(vels)):
            if vels[i] is not None and vels[i - dif] is not None:
                accs.append((vels[i] - vels[i - dif]) * frames / dif)
                dif = 1
            elif vels[i - dif] is None:
                i += 1
            else:
                i += 1
                dif += 1
        plt.figure()
        plt.title("Glottic Angle")
        plt.plot(display_graph)
        plt.xlabel("Frames")
        plt.ylabel("Angle Between Cords")
        print(len(dgraph))
        vidtype = path[path.rfind("."):]
        video_path = draw(
            path, left, right, dgraph, outfile, videotype=vidtype
        )
        print("Video made")
        ret_list = []
        new_vels = vels[np.logical_not(np.isnan(vels))]
        vel_arr = np.array(new_vels)
        acc_arr = np.array(accs)
        """list indecies doc: 
        0: video_path
        1: min angle
        2: 3rd percentile angle
        3: 97th percentile angle
        4: max angle
        5: 97th percentile pos velocity
        6: 97th percentile neg velocity
        7: 97th percentile pos acceleration
        8: 97th percentile neg acceleration"""
        ret_list.append(video_path)
        ret_list.append(np.min(arr))
        ret_list.append(np.percentile(arr, 3))
        ret_list.append(np.percentile(arr, 97))
        ret_list.append(np.max(arr))
        ret_list.append(np.percentile(vel_arr, 97))
        ret_list.append(np.percentile(vel_arr, 3))
        ret_list.append(np.percentile(acc_arr, 97))
        ret_list.append(np.percentile(acc_arr, 3))
        pn = name + "graph.png"
        dn = name + "data.csv"
        out = os.path.join(of, pn)
        plt.savefig(out)
        csvout = os.path.join(of, dn)
        with open(csvout, "w") as file:
            writer = csvwriter(file, delimiter=",")
            # Right line and left line flipped in videos
            writer.writerow(
                [
                    "Frame Number",
                    "Anterior Glottic Angle",
                    "Angle of Left Cord",
                    "Angle of Right Cord",
                ]
            )
            for i in range(len(dgraph)):
                if dgraph[i] is not None:
                    writer.writerow([i + 1, dgraph[i][0], dgraph[i][1], dgraph[i][2]])
                else:
                    writer.writerow([i + 1, dgraph[i]])
        return ret_list


def alt_angle(left_cord, right_cord, comm):
    """Alternative angle of opening calculation."""
    # AGA @ anterior commisure
    left_line = calc_reg_line(left_cord, comm)
    right_line = calc_reg_line(right_cord, comm)
    if left_line is None or right_line is None:
        return np.nan, np.nan, None, None
    set_ends(left_line, left_cord)
    set_ends(right_line, right_cord)
    if right_line.slope < 0 < left_line.slope:
        return np.nan, np.nan, None, None
    tan = abs(
        (left_line.slope - right_line.slope)
        / (1 + left_line.slope * right_line.slope)
    )
    # Angles of cords from vertical midline
    ladj = left_line.end2[0] - left_line.end1[0]
    lop = abs(left_line.end2[1] - left_line.end1[1])
    if ladj == 0:
        ladj = 0.00001
    lang = degrees(atan(lop / ladj))
    if left_line.slope < 0:
        lret = 90 - lang
    else:
        lret = -lang - 90
    return atan(tan), lret, left_line, right_line


def calc_reg_line(points, comm):
    """Given a list corresponding to points plotted on a vocal cord. Calculates
    a regression line from those points which is used to represent the cord."""
    pfx = points[:, 0]
    pfy = points[:, 1]
    pf = stats.linregress(pfx, pfy)
    if comm and len(pfx) > 3:
        pfc = stats.linregress(pfx[1:], pfy[1:])
        if abs(pfc[2]) > abs(pf[2]):
            pf = pfc
    # print(f" r^2 = {pf.rvalue ** 2}")
    if pf.rvalue ** 2 < .9:
        pfc = outlier_del(pfx, pfy, comm, pf)
        if abs(pfc.rvalue) > abs(pf.rvalue):
            pf = pfc
    if pf.rvalue ** 2 < 0.8:
        return None
    return Line(slope=pf.slope, intercept=pf.intercept)


def outlier_del(pfx, pfy, comm, pf):
    """Deletes outliers from sufficiently large cord lists."""
    if comm:
        pfx = pfx[1:]
        pfy = pfy[1:]
    if len(pfx) > 3:
        for i in range(len(pfx) - 1):
            newx = pfx[:-1]
            newy = pfy[:-1]
            newline = stats.linregress(newx, newy)
            if len(newx) > 3:
                newline = outlier_del(newx, newy, False, newline)
            if newline[2] > pf[2]:
                pf = newline
    return pf
