#!/usr/bin/env python

from os import path
import logging
from manage import get_logger_name
from node import Node
from segment import Segment 
from parameters import Parameters
from collections import namedtuple

try:
    import vtk
except ImportError:
    print("vtk not found.")

try:
    from matplotlib import pyplot as plt
except ImportError:
    print("matplotlib is not installed")

class Solver(object):

    class SegmentFields(object):
        """ This class defines the location of segment fields in the solver file SEGMENT statement.
        """
        NAME = 1 
        ID = 2 
        LENGTH = 3
        NUM_ELEMS = 4
        INLET_NODE = 5
        OUTLET_NODE = 6
        INLET_AREA = 7
        OUTLET_AREA = 8
        INFLOW_VALUE = 9
        MATERIAL = 10
        LOSS_TYPE = 11
        BRANCH_ANGLE = 12
        UPSTREAM_SEGMENT_ID = 13
        BRANCH_SEGMENT_ID = 14
        BC_TYPE = 15
        DATA_TABLE_NAME = 16

    class BcTypes(object):
        """ This class defines boundary condition types.
        """
        NONE = "NOBOUND"
        PRESSURE = "PRESSURE"
        AREA = "AREA"
        FLOW = "FLOW"
        RESISTANCE = "RESISTANCE"
        RESISTANCE_TIME = "RESISTANCE_TIME"
        PRESSURE_WAVE = "PRESSURE_WAVE"
        WAVE = "WAVE"
        RCR = "RCR"
        CORONARY = "CORONARY"
        IMPEDANCE = "IMPEDANCE"
        PULMONARY ="PULMONARY"

    def __init__(self, params):
        self.params = params
        self.nodes = None
        self.segments = None
        self.graphics = None
        self.logger = logging.getLogger(get_logger_name())

        try:
            self.points = vtk.vtkPoints()
            self.vertices = vtk.vtkCellArray()
        except:
            self.points = None 
            self.vertices = None 
            self.params.display_geometry = False

        self.points_polydata = None
        self.lines_polydata = None

    def read_solver_file(self):
        """ Read in a solver.in file.
        """
        self.logger.info("---------- Read solver file ----------")
        #self.logger.info("Number of points: %d" % num_points)
        self.nodes = []
        self.segments = {}
        file_name = self.params.results_directory + "/" + self.params.solver_file_name

        with open(file_name) as fp:
            line = fp.readline()
            cnt = 1
            while line:
                #print("Line {}: {}".format(cnt, line.strip()))
                line = fp.readline()
                tokens = line.split()
                if len(tokens) == 0: 
                    continue
                if tokens[0] == 'NODE':
                    self.add_node(tokens)
                elif tokens[0] == 'SEGMENT':
                    self.add_segment(tokens)
                elif tokens[0] == 'SOLVEROPTIONS':
                    self.add_solver_options(tokens)
                elif tokens[0] == 'MODEL':
                    self.params.model_name = tokens[1]
            #__while line
        #__with open(self.params.solver_file_name) as fp:

        self.logger.info("Model name: %s" % self.params.model_name)
        self.logger.info("Number of nodes: %d" % len(self.nodes))
        self.logger.info("Number of segments: %d" % len(self.segments))
        self.logger.info("Number of time steps: %d" % self.params.num_steps) 
        self.logger.info("Time step: %g" % self.params.time_step) 

        if self.params.time_range == None:
            self.params.time_range = [0.0, self.params.times[-1]]

        # Create a points polydata object
        if self.params.display_geometry:
            self.points_polydata = vtk.vtkPolyData()
            self.points_polydata.SetPoints(self.points)
            self.points_polydata.SetVerts(self.vertices)

            # Create a lines polydata object
            self.lines_polydata = vtk.vtkPolyData()
            self.lines_polydata.SetPoints(self.points)
            lines = vtk.vtkCellArray()
            for key,segment in self.segments.items():
                line = vtk.vtkLine()
                line.GetPointIds().SetId(0, segment.node1)
                line.GetPointIds().SetId(1, segment.node2)
                lines.InsertNextCell(line)
            self.lines_polydata.SetLines(lines)

    def add_solver_options(self, tokens):
        """ Add solver options.
        """
        time_step = float(tokens[1])
        self.params.time_step = time_step
        save_freq = int(tokens[2])
        num_steps = int(tokens[3])
        self.params.num_steps = num_steps 
        self.params.times = [i*time_step for i in range(0,num_steps+1,save_freq)]

    def add_node(self, tokens):
        """ Add a node..
        """
        id = tokens[1]
        x = float(tokens[2])
        y = float(tokens[3])
        z = float(tokens[4])
        self.nodes.append(Node(id,x,y,z))

        if self.params.display_geometry:
            id = self.points.InsertNextPoint([x, y, z])
            self.vertices.InsertNextCell(1)
            self.vertices.InsertCellPoint(id)

    def add_segment(self, tokens):
        """ Add a segment.
        """
        fields = self.SegmentFields
     
        name = tokens[fields.NAME]
        id = tokens[fields.ID]
        node1 = int(tokens[fields.INLET_NODE])
        node2 = int(tokens[fields.OUTLET_NODE])
        bc_type = tokens[fields.BC_TYPE]
        self.segments[name] = Segment(id, name, node1, node2, bc_type)
        self.logger.info("Add segment name: %s" % name) 

    def read_segment_data_files(self, data_name):
        """ Read in all outlet segment data files.
        """
        self.logger.info("---------- Read all outlet segment data files ----------")
        self.params.segments = []
        for name,segment in self.segments.items():
            if segment.bc_type != self.BcTypes.NONE:
                self.read_segment_data_file(segment.name, data_name)
                self.params.segments.append(name)
        #__for name,segment in self.segments.items()
        self.logger.info("Number of outlet segments: %d" % len(self.params.segments))
        self.logger.info("Outlet segment names: %s" % ','.join(self.params.segments))

    def read_segment_data_file(self, segment_name, data_name):
        """ Read in a segment data file.
        """
        self.logger.info("---------- Read segment data file ----------")
        self.logger.info("Segment name: %s" % segment_name) 

        if not segment_name in self.segments:
            msg = "No segment named: %s" % segment_name
            self.logger.error(msg)
            raise Exception(msg)

        segment = self.segments[segment_name]
        segment.data = {}
        sep = Parameters.FILE_NAME_SEP
        ext = Parameters.DATA_FILE_EXTENSION 

        for data_name in self.params.data_names:
            self.logger.info("Data name: %s" % data_name) 
            file_name = self.params.results_directory + "/" + self.params.model_name + segment_name + sep + data_name + ext
            num_rows = 0
            data = []

            with open(file_name) as fp:
                line = fp.readline()
                cnt = 1
                while line:
                    #print("Line {}: {}".format(cnt, line.strip()))
                    line = fp.readline()
                    tokens = line.split()
                    num_rows += 1
                    if len(tokens) == 0:
                        continue
                    values = [float(v) for v in tokens]
                    num_cols = len(values)
                data.append(values)
                #__while line
            #__with open(file_name) as fp
            segment.data[data_name] = data
        #__for data_name in self.params.data_names:

        self.logger.info("Number of rows read: %d" % num_rows) 
        self.logger.info("Number of columns read: %d" % num_cols) 

    def write_segment_data(self):
        self.logger.info("---------- Write segment data ----------")
        file_format = self.params.output_format
        ext = "." + file_format 
        sep = "_"

        for data_name in self.params.data_names:
            self.logger.info("Data name: %s" % data_name) 
            file_name = self.params.output_directory + "/" + self.params.output_file_name + sep + data_name + ext
            times = self.params.times

            with open(file_name, "w") as fp:
                for i,name in enumerate(self.params.segments):
                    self.logger.info("Segment name: %s" % name) 
                    fp.write(name)
                    if i != len(self.params.segments)-1:
                        fp.write(",")
                fp.write("\n")

                for i,time in enumerate(times):
                    fp.write(str(time) + ",")
                    for j,name in enumerate(self.params.segments):
                        segment = self.segments[name]
                        data_list = segment.data[data_name]
                        data = data_list[-1]
                        fp.write(str(data[i]))
                        if j != len(self.params.segments)-1:
                            fp.write(",")
                    #__for j,name in enumerate(self.params.segments)
                    fp.write("\n")
                #__for i,time in enumerate(times):

        #__for data_name in self.params.data_names

    def plot_results(self):
        """ Plot results.
        """
        self.logger.info("---------- Plot results ----------")
        title = self.params.solver_file_name
        min_time = self.params.time_range[0]
        max_time = self.params.time_range[1]
        self.logger.info("Min time: %f" % min_time)
        self.logger.info("Max time: %f" % max_time)

        for data_name in self.params.data_names:
            self.logger.info("Data name: %s" % data_name)
            times = self.params.times
            plot_values = [] 
            plot_names = [] 
            fig, ax = plt.subplots()
            ylabel = data_name

            for j,name in enumerate(self.params.segments):
                values = []
                plot_times = [] 
                for i,time in enumerate(times):
                    if (time > min_time) and (time <= max_time):
                        segment = self.segments[name]
                        data_list = segment.data[data_name]
                        data = data_list[-1]
                        values.append(data[i])
                        plot_times.append(time)
                #__for i,time in enumerate(times)
                plot_values.append(values)
                plot_names.append(name) 
                ax.plot(plot_times, plot_values[j], label=plot_names[j])
            #__for j,name in enumerate(self.params.segments)

            ax.set(xlabel='time (s)', ylabel=ylabel, title=title)
            ax.grid()
            chartBox = ax.get_position()
            ax.set_position([chartBox.x0, chartBox.y0, chartBox.width*0.6, chartBox.height])
            ax.legend(loc='upper center', bbox_to_anchor=(1.45, 0.8), shadow=True, ncol=1)
            #plt.legend(bbox_to_anchor=(1.5, 1.0), loc='upper right', ncol=1)
            #ax.legend()
        #__for data_name in self.params.data_names

        # Set the figure window position.
        plt.get_current_fig_manager().window.wm_geometry("+200+100")

        # Add key events.
        cid = plt.gcf().canvas.mpl_connect('key_press_event', self.press_key)

        ## If displaying geometry then don't block.
        if self.params.display_geometry:
            plt.ion()
            plt.show()
            plt.pause(0.001)
        else:
            plt.show()

    def press_key(self, event):
        """ Add key events.

        Keys:
           q: key to quit.
        """
        if event.key == 'q':
            plt.close(event.canvas.figure)


