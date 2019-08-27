import numpy as np
import os
import cv2
import matplotlib.pyplot as plt
from draw import draw
from scipy import stats
from TrackingObjects import Line
from math import atan, pi
from DataReader import read_data


class Tracker:
    """Creates a tracker object that takes a dataset and can perform various
    calculations on it.
    data: lst[lst[float]]
    output: lst[tuple(float, float)]
    contains marked parts and their corresponding points at each frame.
    """

    def __init__(self, data):
        self.data = data
        self.left = []
        self.right = []

    def frame_by(self, path, run):
        """Goes through each frame worth of data. Analyses and graphs opening
        angle of vocal cords. Prints summary statistics."""
        ac1 = self.data[0]
        # frames dropped
        i = 0
        for item in self.data[1]:
            if item is not None:
                i += 1
        print(i)
        LC = [ac1, self.data[1], self.data[2], self.data[3], self.data[4],
              self.data[5], self.data[6]]
        RC = [ac1, self.data[7], self.data[8], self.data[9], self.data[10],
              self.data[11], self.data[12]]
        graph = []
        for i in range(len(self.data[1])):
            LC_now = []
            RC_now = []
            cords_there = False
            comm = False
            for j in range(len(LC)):
                if LC[j][i] is not None:
                    LC_now.append(LC[j][i])
                    if j == 0:
                        comm = True
                    cords_there = True
                else:
                    LC_now.append(None)
            for j in range(len(RC)):
                if RC[j][i] is not None:
                    RC_now.append(RC[j][i])
                    cords_there = True
                else:
                    RC_now.append(None)
            num_pts = 0  # number of legitimate points on a cord
            for item in LC_now:
                if item is not None:
                    num_pts += 1
            if num_pts < 3 and LC_now[0] is None:
                cords_there = False
            num_pts = 0
            for item in RC_now:
                if item is not None:
                    num_pts += 1
            if num_pts < 3 and RC_now[0] is None:
                cords_there = False
            if cords_there:
                angle = self.alt_angle(LC_now, RC_now, comm)
                graph.append(angle)
            else:
                self.left.append(None)
                self.right.append(None)
                graph.append(None)
        dgraph = []  # keep none to show blank space in graph.
        sgraph = []  # remove none to perform statistical analysis.
        for item in graph:
            if item is not None:
                dgraph.append(item * 180 / pi)
                sgraph.append(item * 180 / pi)
            else:
                dgraph.append(None)
        arr = np.array(sgraph)
        display_graph = []
        count = 0
        for i in range(len(dgraph)):
            if dgraph[i] is None:
                display_graph.append(None)
            elif count >= len(arr):
                display_graph.append(None)
            elif arr[count] > np.percentile(arr, 97):
                display_graph.append(0)
                count += 1
            else:
                display_graph.append(arr[count])
                count += 1
        vid = cv2.VideoCapture(path)
        frames = vid.get(cv2.CAP_PROP_FPS)
        vels = [0] # change in angle in degrees / sec
        dif = 1
        for i in range(1, len(dgraph)):
            if dgraph[i] is not None and dgraph[i - dif] is not None:
                vels.append((dgraph[i] - dgraph[i-dif]) * frames / dif)
                dif = 1
            elif dgraph[i - dif] is None:
                i += 1
                vels.append(None)
            else:
                vels.append(None)
                i += 1
                dif += 1
        accs = [0]
        dif = 1
        for i in range(1, len(vels)):
            if vels[i] is not None and vels[i - dif] is not None:
                accs.append((vels[i] - vels[i-dif]) * frames / dif)
                dif = 1
            elif vels[i - dif] is None:
                i += 1
            else:
                i += 1
                dif += 1
        plt.figure()
        plt.title('Glottic Angle')
        plt.plot(display_graph)
        plt.xlabel('Frames')
        plt.ylabel('Angle Between Cords')
        print(len(dgraph))
        vidtype = path[path.rfind('.'):]
        video_path = draw(path, (self.left, self.right), dgraph, videotype=vidtype)
        print('Video made')
        ret_list = []
        new_vel = []
        for vel in vels:
            if vel is not None:
                new_vel.append(vel)
        vel_arr = np.array(new_vel)
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
        name = path[path.rfind('\\') + 1: path.rfind('Deep')]
        outfile = os.path.join(os.getcwd(), name + 'plot%d.png' % run)
        plt.savefig(outfile)
        return ret_list

    def angle_of_opening(self, left_cord, right_cord, comm):
        """Calculates angle of opening between left and right cord."""
        left_line = calc_reg_line(left_cord, comm)
        right_line = calc_reg_line(right_cord, comm)
        self.left.append(left_line)
        self.right.append(right_line)
        if left_line is None or right_line is None:
            return None
        left_line.set_ends(left_cord)
        right_line.set_ends(right_cord)
        if right_line.slope < 0 < left_line.slope:
            return 0
        """cross = intersect(left_line, right_line)
        if cross is not None:
            crossy = cross[1]
        else:
            return 0
        if crossy > left_cord[0][1] + 20 or crossy > right_cord[0][1] + 20:
            return 0"""
        tan = abs((left_line.slope - right_line.slope) / (1 + left_line.slope *
                                                          right_line.slope))
        return atan(tan)


    def alt_angle(self, left_cord, right_cord, comm):
        """Alternative angle of opening calculation."""
        left_line = calc_muscular_line(left_cord, comm)
        right_line = calc_muscular_line(right_cord, comm)
        self.left.append(left_line)
        self.right.append(right_line)
        if left_line is None or right_line is None:
            return None
        left_line.set_ends(left_cord)
        right_line.set_ends(right_cord)
        if right_line.slope < 0 < left_line.slope:
            return 0
        tan = abs((left_line.slope - right_line.slope) / (1 + left_line.slope *
                                                          right_line.slope))
        return atan(tan)


def calc_reg_line(pt_lst, comm):
    """Given a list corresponding to points plotted on a vocal cord. Calculates
    a regression line from those points which is used to represent the cord."""
    pfx = []
    pfy = []
    for item in pt_lst:
        if item is not None:
            pfx.append(item[0])
            pfy.append(item[1])
    pf = stats.linregress(pfx, pfy)
    if comm and len(pfx) > 3:
        pfc = stats.linregress(pfx[1:], pfy[1:])
        if pfc[2] > pf[2]:
            pf = pfc
    pfc = outlier_del(pfx, pfy, comm, pf)
    if pfc[2] > pf[2]:
        pf = pfc
    if pf[2] ** 2 < .8:
        return None
    slope = pf[0]
    yint = pf[1]
    return Line(slope, yint)


def calc_muscular_line(pt_list, comm):
    """Calculates angle of opening by drawing straight line from anterior
     commisure if availible and most distal point on cord."""
    if pt_list[0] is not None:
        far_ind = 0
        for i in range(len(pt_list)):
            if pt_list[i] is not None:
                far_ind = i
        return Line(pt_list[0], pt_list[far_ind])
    else:
        return calc_reg_line(pt_list, comm)


def outlier_del(pfx, pfy, comm, pf):
    """Deletes outliers from sufficiently large cord lists."""
    if comm:
        pfx = pfx[1:]
        pfy = pfy[1:]
    if len(pfx) > 3:
        for i in range(len(pfx) - 1):
            newx = []
            newy = []
            for j in range(len(pfx)):
                newx.append(pfx[j])
                newy.append(pfy[j])
            newx.pop(i)
            newy.pop(i)
            newline = stats.linregress(newx, newy)
            if len(newx) > 3:
                newline = outlier_del(newx, newy, False, newline)
            if newline[2] > pf[2]:
                pf = newline
    return pf


if __name__ == '__main__':
    # data = read_data('nop10DeepCut_resnet50_vocalJun10shuffle1_1030000.h5')
    data = read_data('nop10DeepCut_resnet50_vocal_foldAug7shuffle1_1030000.h5')
    t = Tracker(data)
    # t.frame_by('nop10DeepCut_resnet50_vocalJun10shuffle1_1030000_labeled.mp4')
    t.frame_by('nop10.mp4', 0)
