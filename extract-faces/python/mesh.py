#!/usr/bin/env python
'''The Mesh class is used to represent a polygonal surface mesh.
'''
from collections import defaultdict
from collections import deque 
import logging
from manage import get_logger_name
from math import cos
from math import pi as MATH_PI 
from os import path
import sys 
import vtk
print(" vtk version %s\n" % str(vtk.VTK_MAJOR_VERSION))

from face import Face

class Mesh(object):

    def __init__(self, params):
        self.params = params
        self.file_base_name = None
        self.surface = None
        self.surface_caps = None
        self.graphics = None
        self.boundary_faces = None
        self.boundary_edges = None
        self.boundary_edge_components = None
        self.boundary_face_components = None
        self.logger = logging.getLogger(get_logger_name())

    def extract_faces(self):
        '''Extract the surface faces.
        '''
        self.logger.info("---------- extract faces ---------- ")

        ## Compute edges separating cells by the angle set in 'self.params.angle'.
        #
        self.logger.info("Compute feature edges ...")
        surface = self.surface
        feature_edges = vtk.vtkFeatureEdges()
        feature_edges.SetInputData(surface)
        feature_edges.BoundaryEdgesOff();
        feature_edges.ManifoldEdgesOff();
        feature_edges.NonManifoldEdgesOff();
        feature_edges.FeatureEdgesOn();
        feature_edges.SetFeatureAngle(self.params.angle);
        feature_edges.Update()

        boundary_edges = feature_edges.GetOutput()
        clean_filter = vtk.vtkCleanPolyData()
        boundary_edges_clean = clean_filter.SetInputData(boundary_edges)
        clean_filter.Update();
        cleaned_edges = clean_filter.GetOutput()

        conn_filter = vtk.vtkPolyDataConnectivityFilter()
        conn_filter.SetInputData(cleaned_edges)
        conn_filter.SetExtractionModeToSpecifiedRegions()
        self.boundary_edge_components = list()
        edge_id = 0

        while True:
            conn_filter.AddSpecifiedRegion(edge_id)
            conn_filter.Update()
            component = vtk.vtkPolyData()
            component.DeepCopy(conn_filter.GetOutput())
            if component.GetNumberOfCells() <= 0:
                break
            #print("{0:d}: Number of boundary lines: {1:d}".format(edge_id, component.GetNumberOfCells()))
            self.boundary_edge_components.append(component)
            conn_filter.DeleteSpecifiedRegion(edge_id)
            edge_id += 1

        self.logger.info("Number of edges: {0:d}".format(edge_id))

        ## Identify the cells incident to the feature edges.
        #
        self.logger.info("Identify edge cells ...")

        # Create a set of edge nodes.
        edge_nodes = set()
        for edge in self.boundary_edge_components:
            edge_num_points = edge.GetNumberOfPoints()
            edge_node_ids = edge.GetPointData().GetArray('GlobalNodeID')
            for i in range(edge_num_points):
                nid = edge_node_ids.GetValue(i)
                edge_nodes.add(nid)

        # Create a set of cell IDs incident to the edge nodes.
        surf_points = surface.GetPoints()
        num_cells = surface.GetNumberOfCells()
        surf_node_ids = surface.GetPointData().GetArray('GlobalNodeID')
        edge_cell_ids = set()

        for i in range(num_cells):
            cell = surface.GetCell(i)
            cell_pids = cell.GetPointIds()
            num_ids = cell_pids.GetNumberOfIds()
            node_ids = [ surf_node_ids.GetValue(cell_pids.GetId(j)) for j in range(num_ids) ]
            for pid in node_ids:
                if pid in edge_nodes: 
                    edge_cell_ids.add(i)
                    break

        ## Identify boundary faces using edge cells.
        #
        cell_visited = set()
        cell_normals = surface.GetCellData().GetArray('Normals')
        feature_angle = cos((MATH_PI/180.0) * self.params.angle)
        self.logger.info("feature_angle: {0:g}".format(feature_angle))
        #num_edge_cells = edge_cells.GetNumberOfCells()
        #self.logger.info("Number of edge cells: {0:d}".format(num_edge_cells))
        new_cells = deque()
        faces = defaultdict(list)
        face_id = 0
        self.logger.info("Traverse edge cells ...")

        for cell_id in edge_cell_ids:
            if cell_id in cell_visited:
                continue
            #self.logger.info("----- Edge cell ID: {0:d} -----".format(cell_id))
            self.add_new_cells(surface, cell_normals, edge_cell_ids, cell_visited, cell_id, new_cells, feature_angle, faces[face_id])
            faces[face_id].append(cell_id)
            while len(new_cells) != 0:
                #self.logger.info("  new_cells: {0:s}".format(str(new_cells)))
                new_cell_id = new_cells.pop()
                if new_cell_id not in cell_visited:
                    faces[face_id].append(new_cell_id)
                self.add_new_cells(surface, cell_normals, edge_cell_ids, cell_visited, new_cell_id, new_cells, feature_angle, faces[face_id])

            face_id += 1

        ## Check that we got all of the cells.
        self.logger.info("Number of cells visited: {0:d}".format(len(cell_visited)))
        self.logger.info("Number of faces: {0:d}".format(face_id))
        self.logger.info("Faces: ")
        faces_size = 0
        for face_id in faces:
            cell_list = faces[face_id]
            #self.logger.info("  Face ID: {0:d}  num cells: {1:d}".format(face_id, len(cell_list)))
            faces_size += len(cell_list)
        self.logger.info("Number of faces cells: {0:d}".format(faces_size))

        ## Add the 'ModelFaceID' cell data array identifying each cell with a face ID.
        #
        face_ids_data = vtk.vtkIntArray()
        face_ids_data.SetNumberOfValues(num_cells)
        face_ids_data.SetName("ModelFaceID")
        for face_id in faces:
            cell_list = faces[face_id]
            for cell_id in cell_list:
                face_ids_data.SetValue(cell_id, face_id+1);
        surface.GetCellData().AddArray(face_ids_data)

        # Write the surface with the 'ModelFaceID' cell data array.
        writer = vtk.vtkXMLPolyDataWriter()
        writer.SetFileName(self.file_base_name + "-boundary.vtp");
        writer.SetInputData(surface)
        writer.Write()

        # Write the surface without any data arrays.
        ''' for debugging
        surface.GetCellData().RemoveArray('ModelFaceID')
        surface.GetCellData().RemoveArray('GlobalElementID')
        writer = vtk.vtkXMLPolyDataWriter()
        writer.SetFileName(self.file_base_name + "-no-faceIDs.vtp")
        writer.SetInputData(surface)
        writer.Write()
        '''

    def add_new_cells(self, surface, cell_normals, edge_cell_ids, cell_visited, cell_id, new_cells, feature_angle, faces):
        #self.logger.info("  add new cell: {0:d}".format(cell_id))
        #faces.append(cell_id)
        cell = surface.GetCell(cell_id)
        cell_visited.add(cell_id)
        num_edges = cell.GetNumberOfEdges()
        #self.logger.info("  num edges {0:d}".format(num_edges))
        cell_normal = [ cell_normals.GetComponent(cell_id,j) for j in range(3)]

        for i in range(num_edges):
            edge = cell.GetEdge(i)
            edge_ids = edge.GetPointIds()
            pid1 = edge_ids.GetId(0)
            pid2 = edge_ids.GetId(1)
            #self.logger.info("  edge {0:d} {1:d}".format(pid1, pid2))
            adj_cell_ids = vtk.vtkIdList()
            surface.GetCellEdgeNeighbors(cell_id, pid1, pid2, adj_cell_ids)

            for j in range(adj_cell_ids.GetNumberOfIds()):
                adj_cell_id = adj_cell_ids.GetId(j)
                if adj_cell_id not in cell_visited:
                    add_cell = True
                    if adj_cell_id in edge_cell_ids:
                        dp = sum([ cell_normal[k] * cell_normals.GetComponent(adj_cell_id,k) for k in range(3)] )
                        if dp < feature_angle:
                            #self.logger.info("  adj cell {0:d} is in separate face cell dp {1:g}".format(adj_cell_id, dp))
                            add_cell = False
                    if add_cell: 
                        new_cells.append(adj_cell_id)
                        cell_visited.add(cell_id)

        #self.logger.info("  new cells {0:s}".format(str(new_cells)))
        #for cell_id in new_cells:
        #    self.add_new_cell(surface, cell_visited, cell_id)

    def write_boundary_edges(self):
        '''Write a lines representing boundary edges.

           This is for debugging.
        '''
        append_filter = vtk.vtkAppendPolyData()
        for i,edge in enumerate(self.boundary_edge_components):
            append_filter.AddInputData(edge)
        append_filter.Update()

        writer = vtk.vtkXMLPolyDataWriter()
        writer.SetFileName("boundary_edges.vtp");
        writer.SetInputData(append_filter.GetOutput())
        writer.Write()

    def write_boundary_edge_cells(self, edge_cell_ids):
        '''Write a PolyData surface containing the cells incident to boundary edges.

           This is for debugging.
        '''
        cell_mask = vtk.vtkIntArray()
        cell_mask.SetNumberOfValues(num_cells)
        cell_mask.SetName("CellMask")
        for i in range(num_cells):
            cell_mask.SetValue(i,0);
        surface.GetCellData().AddArray(cell_mask)

        for cell_id in edge_cell_ids:
            cell_mask.SetValue(cell_id,1);

        thresh = vtk.vtkThreshold()
        thresh.SetInputData(surface)
        thresh.ThresholdBetween(1, 1)
        thresh.SetInputArrayToProcess(0, 0, 0, "vtkDataObject::FIELD_ASSOCIATION_CELLS", "CellMask")
        thresh.Update()

        surfacefilter = vtk.vtkDataSetSurfaceFilter()
        surfacefilter.SetInputData(thresh.GetOutput())
        surfacefilter.Update()
        edge_cells = surfacefilter.GetOutput()

        writer = vtk.vtkXMLPolyDataWriter()
        writer.SetFileName("boundary_edge_cells.vtp");
        writer.SetInputData(edge_cells)
        writer.Write()

    def extract_edges(self):
        '''Extract the surface boundary edges.
        '''
        self.logger.info("---------- extract edges ---------- ")
        surface = self.surface
        feature_edges = vtk.vtkFeatureEdges()
        feature_edges.SetInputData(surface)
        feature_edges.BoundaryEdgesOn()
        feature_edges.FeatureEdgesOff()
        feature_edges.ManifoldEdgesOff()
        feature_edges.NonManifoldEdgesOff()
        feature_edges.ColoringOn()
        feature_edges.Update()

        boundary_edges = feature_edges.GetOutput()
        clean_filter = vtk.vtkCleanPolyData() 
        boundary_edges_clean = clean_filter.SetInputData(boundary_edges)
        clean_filter.Update(); 
        cleaned_edges = clean_filter.GetOutput()

        conn_filter = vtk.vtkPolyDataConnectivityFilter()
        conn_filter.SetInputData(cleaned_edges)
        conn_filter.SetExtractionModeToSpecifiedRegions()
        self.boundary_edge_components = list()
        id = 0

        while True:
            conn_filter.AddSpecifiedRegion(id)
            conn_filter.Update()
            component = vtk.vtkPolyData()
            component.DeepCopy(conn_filter.GetOutput())
            if component.GetNumberOfCells() <= 0:
                break
            print("{0:d}: Number of boundary lines: {1:d}".format(id, component.GetNumberOfCells()))
            self.boundary_edge_components.append(component)
            conn_filter.DeleteSpecifiedRegion(id)
            id += 1

        self.boundary_edges = cleaned_edges
        #self.boundary_edges = feature_edges.GetOutput()
        self.boundary_edges.BuildLinks()
        #print(str(self.boundary_edges))

 
    def read_mesh(self):
        '''Read in a surface mesh.
        '''
        self.file_base_name, file_extension = path.splitext(self.params.surface_file_name)
        reader = None
        if file_extension == ".vtp":
            reader = vtk.vtkXMLPolyDataReader()
        elif file_extension == ".stl":
            reader = vtk.vtkSTLReader()
        reader.SetFileName(self.params.surface_file_name)
        reader.Update()
        geometry = reader.GetOutput()

        pd_normals = vtk.vtkPolyDataNormals()
        pd_normals.SetInputData(geometry)
        pd_normals.SplittingOff()
        pd_normals.ComputeCellNormalsOn()
        pd_normals.ComputePointNormalsOn()
        pd_normals.ConsistencyOn()
        pd_normals.AutoOrientNormalsOn()
        pd_normals.Update()
        self.surface = pd_normals.GetOutput()
        self.surface.BuildLinks()

        num_points = self.surface.GetPoints().GetNumberOfPoints()
        self.logger.info("Number of points: %d" % num_points)
        num_polys = self.surface.GetPolys().GetNumberOfCells()
        self.logger.info("Number of triangles: %d" % num_polys)

        # Extract boundary faces.
        self.extract_faces()

        #if self.params.use_feature_angle and self.params.angle != None:
        #    self.extract_faces()
        #else:
        #    self.extract_edges()

