#!/usr/bin/env python

from os import path
import logging
from manage import get_logger_name

try:
    import vtk
    from vtk.util.colors import tomato
except ImportError:
    pass

class MouseSegmentInteractorStyle(vtk.vtkInteractorStyleTrackballCamera):
 
    def __init__(self,parent=None):
        self.AddObserver("LeftButtonPressEvent", self.leftButtonPressEvent)
        self.AddObserver("KeyPressEvent", self.onKeyPressEvent)
        self.LastPickedActor = None
        self.LastPickedProperty = vtk.vtkProperty()
        self.graphics = None
 
    def leftButtonPressEvent(self,obj,event):
        clickPos = self.GetInteractor().GetEventPosition()
        #picker = vtk.vtkPropPicker()
        picker = vtk.vtkCellPicker()
        picker.Pick(clickPos[0], clickPos[1], 0, self.renderer)
        
        # get the new
        self.NewPickedActor = picker.GetActor()
        #print(">>> self.NewPickedActor")
        #print(self.NewPickedActor)
        if self.NewPickedActor == None:
            self.OnLeftButtonDown()
            return

        for seg_name,seg_actor in self.graphics.segment_actors.items():
            if self.NewPickedActor == seg_actor:
              self.graphics.logger.info(" ")
              self.graphics.logger.info("Selected segment %s" % seg_name)
              self.graphics.picked_segment = seg_name

        # If something was selected
        if self.NewPickedActor:
            if self.LastPickedActor:
                self.LastPickedActor.GetProperty().DeepCopy(self.LastPickedProperty)
            self.LastPickedProperty.DeepCopy(self.NewPickedActor.GetProperty())
            self.NewPickedActor.GetProperty().SetColor(1.0, 0.0, 0.0)
            self.NewPickedActor.GetProperty().SetDiffuse(1.0)
            self.NewPickedActor.GetProperty().SetSpecular(0.0)
            self.LastPickedActor = self.NewPickedActor
        
        self.OnLeftButtonDown()
        return

    def onKeyPressEvent(self, renderer, event):
        key = self.GetInteractor().GetKeySym()
        if key == 'p' and self.graphics.picked_segment:
            self.graphics.logger.info("Plot segment %s" % self.graphics.picked_segment)
            self.graphics.solver.plot_segment(self.graphics.picked_segment, "flow")


class Graphics(object):
    """ The Graphics class is used to display the solver mesh in the graphics window.
    """
    def __init__(self, params):
        self.params = params
        self.renderer = None
        self.window = None
        self.interactor = None
        self.segment_actors = {}
        self.solver = None
        self.picked_segment = None
        self.colors = vtk.vtkNamedColors()
        self.logger = logging.getLogger(get_logger_name())
        self.initialize_graphics()

    def create_graphics_geometry(self, poly_data):
        """ Create geometry for display.
        """
        mapper = vtk.vtkPolyDataMapper()
        mapper.SetInputData(poly_data)
        actor = vtk.vtkActor()
        actor.SetMapper(mapper)
        return actor

    def initialize_graphics(self):
        """ Create renderer and graphics window.
        """
        self.renderer = vtk.vtkRenderer()
        self.window = vtk.vtkRenderWindow()
        self.window.AddRenderer(self.renderer)
        self.renderer.SetBackground(1.0, 1.0, 1.0)
        self.window.SetSize(1000, 1000)

        # Create a trackball interacter to transoform the geometry using the mouse.
        self.interactor = vtk.vtkRenderWindowInteractor()
        self.interactor.SetRenderWindow(self.window)

        style = MouseSegmentInteractorStyle() 
        style.renderer = self.renderer 
        style.graphics = self
        self.interactor.SetInteractorStyle(style)
        style.SetCurrentRenderer(self.renderer)

    def add_sphere(self, center, color):
        sphere = vtk.vtkSphereSource()
        sphere.SetCenter(center[0], center[1], center[2])
        sphere.SetRadius(0.1)
        poly_data = sphere.GetOutputPort()
        self.add_graphics_geometry(poly_data, color, True)

    def add_cyl(self, pt1, pt2, name):
        cyl = vtk.vtkCylinderSource()
        cyl.SetRadius(0.05)
        cyl.SetResolution(15)
        x = [0,0,0]
        y = [0,0,0]
        z = [0,0,0]
        vtk.vtkMath.Subtract(pt2, pt1, x)
        length = vtk.vtkMath.Norm(x)
        vtk.vtkMath.Normalize(x)
        #print("length: " + str(length))

        arbitrary = [0,0,0]
        arbitrary[0] = vtk.vtkMath.Random(-10,10)
        arbitrary[1] = vtk.vtkMath.Random(-10,10)
        arbitrary[2] = vtk.vtkMath.Random(-10,10)
        vtk.vtkMath.Cross(x, arbitrary, z)
        vtk.vtkMath.Normalize(z)

        vtk.vtkMath.Cross(z, x, y)
        matrix = vtk.vtkMatrix4x4()
        matrix.Identity()

        for i in range(3):
            matrix.SetElement(i, 0, x[i])
            matrix.SetElement(i, 1, y[i])
            matrix.SetElement(i, 2, z[i])

        #print("x: " + str(x))
        #print("y: " + str(y))
        #print("z: " + str(z))

        transform = vtk.vtkTransform()
        transform.Translate(pt1) 
        transform.Concatenate(matrix); 
        transform.RotateZ(-90.0)      
        transform.Scale(1.0, length, 1.0)
        transform.Translate(0, 0.5, 0)  

        transformPD = vtk.vtkTransformPolyDataFilter()
        transformPD.SetTransform(transform)
        transformPD.SetInputConnection(cyl.GetOutputPort())

        mapper = vtk.vtkPolyDataMapper()
        actor = vtk.vtkActor()

        #mapper.SetInputConnection(transformPD.GetOutputPort())
        mapper.SetInputConnection(cyl.GetOutputPort())
        actor.SetUserMatrix(transform.GetMatrix())

        actor.SetMapper(mapper)
        actor.GetProperty().SetColor(0.0, 1.0, 0.0)
        self.renderer.AddActor(actor)
        self.segment_actors[name] = actor

    def add_graphics_geometry(self, poly_data, color):
        gr_geom = self.create_graphics_geometry(poly_data)
        gr_geom.GetProperty().SetColor(color[0], color[1], color[2])
        gr_geom.GetProperty().SetPointSize(20)
        self.renderer.AddActor(gr_geom)
        self.window.Render()

    def add_graphics_points(self, poly_data, color):
        ball = vtk.vtkSphereSource()
        ball.SetRadius(self.params.node_sphere_radius)
        ball.SetThetaResolution(12)
        ball.SetPhiResolution(12)
        balls = vtk.vtkGlyph3D()
        balls.SetInputData(poly_data)
        balls.SetSourceConnection(ball.GetOutputPort())

        mapBalls = vtk.vtkPolyDataMapper()
        mapBalls.SetInputConnection(balls.GetOutputPort())
        ballActor = vtk.vtkActor()
        ballActor.SetMapper(mapBalls)
        ballActor.GetProperty().SetColor([0.0, 0.0, 1.0])
        ballActor.GetProperty().SetSpecularColor(1, 0, 0)
        ballActor.GetProperty().SetSpecular(0.3)
        ballActor.GetProperty().SetSpecularPower(20)
        ballActor.GetProperty().SetAmbient(0.2)
        ballActor.GetProperty().SetDiffuse(0.8)
        self.renderer.AddActor(ballActor)

        self.window.Render()

    def add_graphics_edges(self, poly_data, names, color):
        pt1 = [0,0,0]
        pt2 = [0,0,0]
        points = poly_data.GetPoints();
        poly_data.GetLines().InitTraversal()
        idList = vtk.vtkIdList()
        n = 0

        while poly_data.GetLines().GetNextCell(idList):
            node1 = idList.GetId(0)
            node2 = idList.GetId(1)
            points.GetPoint(node1,pt1)
            points.GetPoint(node2,pt2)
            self.add_cyl(pt1, pt2, names[n])
            n += 1
        #__while poly_data.GetLines().GetNextCell(idList)

        self.window.Render()

    def show(self):
        self.interactor.Start()

