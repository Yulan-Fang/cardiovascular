#!/usr/bin/env python

""" 
This script is used to extract data from SimVascular 1D solver results files and write them to CSV format files. 

The script can optionally be used to

  1) Plot selected segment data

  2) Visualize 1D network geometry


Results can be converted and plotted for

  1) A list of segment names

  2) Outlet segments

  3) All segments


Segments can also be interactively selected from 1D network geometry displayed 
in a graphics window. The results of the selected segments can be converted but 
not plotted.

----------------------
Command Line Arguments
----------------------
The script accepts named arguments of the form

    --NAME VALUE

"""

import argparse
import os 
import sys
import logging

from manage import get_logger_name, init_logging
from parameters import Parameters
from solver import Solver

try:
    import vtk
    from graphics import Graphics 
except ImportError:
    pass

logger = logging.getLogger(get_logger_name())

class Args(object):
    """ 
    This class defines the command line arguments for the extract_results.py script.
    """
    PREFIX = "--"
    ALL_SEGMENTS = "all_segments"
    DATA_NAMES = "data_names"
    DISPLAY_GEOMETRY = "display_geometry"
    NODE_SPHERE_RADIUS = "node_sphere_radius"
    OUTPUT_DIRECTORY  = "output_directory"
    OUTPUT_FILE = "output_file_name"
    OUTPUT_FORMAT = "output_format"
    OUTLET_SEGMENTS = "outlet_segments"
    PLOT = "plot"
    RESULTS_DIRECTORY  = "results_directory"
    SEGMENTS = "segments"
    SELECT_SEGMENTS = "select_segments"
    SOLVER_FILE = "solver_file_name"
    TIME_RANGE = "time_range"
    
def cmd(name):
    """ Create an argparse command argument.
    """
    return Args.PREFIX + name.replace("_", "-")

def parse_args():
    """ Parse command-line arguments."""
    parser = argparse.ArgumentParser()

    parser.add_argument(cmd(Args.ALL_SEGMENTS), action='store_true',
      help="If given then read all segment data.")

    parser.add_argument(cmd(Args.DATA_NAMES),
      help="Data name.")

    parser.add_argument(cmd(Args.DISPLAY_GEOMETRY),
      help="Display geometry.")

    parser.add_argument(cmd(Args.NODE_SPHERE_RADIUS), 
      help="Radius of node sphere markers.")

    parser.add_argument(cmd(Args.OUTLET_SEGMENTS), action='store_true',
      help="If given then read all outlet segment data.")

    parser.add_argument(cmd(Args.OUTPUT_DIRECTORY), 
      help="Output directory.")

    parser.add_argument(cmd(Args.OUTPUT_FILE), 
      help="Output file name.")

    parser.add_argument(cmd(Args.OUTPUT_FORMAT), 
      help="Output format.")

    parser.add_argument(cmd(Args.PLOT), 
      help="Plot results.")

    parser.add_argument(cmd(Args.RESULTS_DIRECTORY), required=True,
      help="Results directory.")

    parser.add_argument(cmd(Args.SEGMENTS), 
      help="Segment names to convert.")

    parser.add_argument(cmd(Args.SELECT_SEGMENTS), action='store_true',
      help="Select segments to convert.")

    parser.add_argument(cmd(Args.SOLVER_FILE), required=True,
      help="Solver .in file.")

    parser.add_argument(cmd(Args.TIME_RANGE), 
      help="Time range to save and plot.")

    return parser.parse_args(), parser.print_help

def set_parameters(**kwargs):
    """ Set the values of parameters input from the command line.
    """
    logger.info("Parse arguments ...")

    ## Create a Parameters object to store parameters.
    params = Parameters()

    ## Process arguments.
    #
    if kwargs.get(Args.OUTPUT_DIRECTORY):
        params.output_directory = kwargs.get(Args.OUTPUT_DIRECTORY)
        if not os.path.exists(params.output_directory):
            logger.error("The output directory '%s' was not found." % params.output_directory)
            return None
        logger.info("Output directory: '%s'." % params.output_directory)

    if kwargs.get(Args.RESULTS_DIRECTORY):
        params.results_directory = kwargs.get(Args.RESULTS_DIRECTORY)
        if not os.path.exists(params.results_directory):
            logger.error("The results directory '%s' was not found." % params.results_directory)
            return None
        logger.info("Results directory: '%s'." % params.results_directory)

    params.output_file_name = kwargs.get(Args.OUTPUT_FILE)
    logger.info("Output file name: %s" % params.output_file_name)

    params.output_format = kwargs.get(Args.OUTPUT_FORMAT)
    logger.info("Output format: %s" % params.output_format)

    params.solver_file_name = kwargs.get(Args.SOLVER_FILE)
    logger.info("Solver file name: %s" % params.solver_file_name)

    params.data_names = kwargs.get(Args.DATA_NAMES).split(",")
    logger.info("Data names: %s" % ','.join(params.data_names))

    if kwargs.get(Args.OUTLET_SEGMENTS):
        params.outlet_segments = True 
        logger.info("Outlet segments: %s" % params.outlet_segments)

    if kwargs.get(Args.ALL_SEGMENTS):
        params.all_segments = True 
        logger.info("All segments: %s" % params.all_segments)

    if kwargs.get(Args.SELECT_SEGMENTS):
        params.select_segment_names = True
        logger.info("Select segments: %s" % params.select_segment_names)

    if kwargs.get(Args.DISPLAY_GEOMETRY):
        params.display_geometry = (kwargs.get(Args.DISPLAY_GEOMETRY) in ["on", "true"])
        logger.info("Display geometry: %s" % params.display_geometry)

    if kwargs.get(Args.NODE_SPHERE_RADIUS):
        params.node_sphere_radius = float(kwargs.get(Args.NODE_SPHERE_RADIUS)) 

    if kwargs.get(Args.PLOT):
        params.plot_results = (kwargs.get(Args.PLOT) in ["on", "true"])
        logger.info("Plot results: %s" % params.plot_results)

    if kwargs.get(Args.SEGMENTS):
        params.segment_names = kwargs.get(Args.SEGMENTS).split(",")
        logger.info("Segments: %s" % ','.join(params.segment_names))

    if kwargs.get(Args.TIME_RANGE):
        params.time_range = [float(s) for s in kwargs.get(Args.TIME_RANGE).split(",")]
        logger.info("Time range: %s" % ','.join(map(str,params.time_range)))

    return params 

if __name__ == '__main__':
    init_logging()
    args, print_help = parse_args()
    params = set_parameters(**vars(args))

    if params == None:
        sys.exit()

    ## Create graphics interface.   
    #
    # Creating a Graphics() object fails is vtk
    # is not installed.
    try:
        graphics = Graphics(params)
    except:
        graphics = None
        pass

    ## Read in the solver file.
    solver = Solver(params)
    solver.graphics = graphics 
    solver.read_solver_file()
    if graphics:
        graphics.solver = solver

    ## Read segment data.
    solver.read_segment_data()

    ## Write segment data if segments are not going
    #  to be interactively selected.
    if params.output_file_name and not params.select_segment_names:
        solver.write_segment_data()

    ## Plot results.
    if params.plot_results:
        solver.plot_results()

    ## If displaying geometry then show the network.
    if graphics and params.display_geometry:
        graphics.add_graphics_points(solver.points_polydata, [0.8, 0.8, 0.8])
        graphics.add_graphics_edges(solver.lines_polydata, solver.lines_segment_names, [0.8, 0.8, 0.8])
        graphics.show()


