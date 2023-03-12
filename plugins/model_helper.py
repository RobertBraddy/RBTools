import sys

from PySide2 import QtCore
from PySide2 import QtGui
from PySide2 import QtWidgets
from shiboken2 import getCppPointer

import maya.OpenMayaUI as omui
import maya.cmds as cmds
import maya.mel as mel


class WorkspaceControl(object):

    def __init__(self, name):
        self.name = name
        self.widget = None

    def create(self, label, widget, ui_script=None):

        cmds.workspaceControl(self.name, label=label)

        if ui_script:
            cmds.workspaceControl(self.name, e=True, uiScript=ui_script)

        self.add_widget_to_layout(widget)
        self.set_visible(True)

    def restore(self, widget):
        self.add_widget_to_layout(widget)

    def add_widget_to_layout(self, widget):
        if widget:
            self.widget = widget
            self.widget.setAttribute(QtCore.Qt.WA_DontCreateNativeAncestors)

            if sys.version_info.major >= 3:
                workspace_control_ptr = int(omui.MQtUtil.findControl(self.name))
                widget_ptr = int(getCppPointer(self.widget)[0])
            else:
                workspace_control_ptr = long(omui.MQtUtil.findControl(self.name))
                widget_ptr = long(getCppPointer(self.widget)[0])

            omui.MQtUtil.addWidgetToMayaLayout(widget_ptr, workspace_control_ptr)

    def exists(self):
        return cmds.workspaceControl(self.name, q=True, exists=True)

    def is_visible(self):
        return cmds.workspaceControl(self.name, q=True, visible=True)

    def set_visible(self, visible):
        if visible:
            cmds.workspaceControl(self.name, e=True, restore=True)
        else:
            cmds.workspaceControl(self.name, e=True, visible=False)

    def set_label(self, label):
        cmds.workspaceControl(self.name, e=True, label=label)

    def is_floating(self):
        return cmds.workspaceControl(self.name, q=True, floating=True)

    def is_collapsed(self):
        return cmds.workspaceControl(self.name, q=True, collapse=True)
        
        
class ScrollableWidget(QtWidgets.QWidget):
    def __init__(self):
        super(ScrollableWidget, self).__init__()

        # Create a scroll area widget
        self.scroll_area = QtWidgets.QScrollArea(self)
        self.scroll_area.setWidgetResizable(True)
        #self.scroll_area.baseSize()
        self.scroll_area.setHorizontalScrollBarPolicy(QtCore.Qt.ScrollBarAlwaysOff)
        #self.scroll_area.setStyleSheet(' border: 2px solid grey;')
        #self.scroll_area.drawFrame(0) 
        self.scroll_area.setContentsMargins(0, 0, 0, 0)
        self.scroll_area.setFrameShape(QtWidgets.QFrame.NoFrame)
        self.scroll_area.setFrameStyle(0)
        self.scroll_area.setLineWidth(0)
        self.scroll_area.setMidLineWidth(0)
        self.scroll_area.setFrameShadow(QtWidgets.QFrame.Plain)
        
        #, frameShadow=Plain, line25=0 and midLine25=0
        #scrollAreaWidgetContents
        
        # Create a widget to hold the contents of the scroll area
        self.contents = QtWidgets.QWidget(self.scroll_area)
        self.scroll_area.setWidget(self.contents)

        # Add widgets to the contents widget
        self.vbox = QtWidgets.QVBoxLayout(self.contents)

        # Add a button to the contents widget


        # Set the layout of the main widget
        main_layout = QtWidgets.QVBoxLayout(self)
        main_layout.addWidget(self.scroll_area)
        
    def add_widget(self, widget):
        self.vbox.addWidget(widget)
                
        widget.setContentsMargins(0, 0, 0, 0)
        #widget.setLayout(sub_layout)
        #scrollarea.setWidget(widget)
        
    def add_layout(self, layout):
        self.vbox.addLayout(layout)
        layout.setContentsMargins(0, 0, 0, 0)
        


class CollapsibleHeader(QtWidgets.QWidget):
    
    COLLAPSED_PIXMAP = QtGui.QPixmap(":teRightArrow.png")
    EXPANDED_PIXMAP = QtGui.QPixmap(":teDownArrow.png")
    
    clicked = QtCore.Signal()
    
    def __init__(self, text, parent=None):
        super(CollapsibleHeader, self).__init__(parent)
        
        self.setAutoFillBackground(True)
        self.set_background_color(None)
        
        self.icon_label = QtWidgets.QLabel()
        self.icon_label.setFixedWidth(self.COLLAPSED_PIXMAP.width())
        
        self.text_label = QtWidgets.QLabel()
        self.text_label.setAttribute(QtCore.Qt.WA_TransparentForMouseEvents)
        
        self.main_layout = QtWidgets.QHBoxLayout(self)
        self.main_layout.setContentsMargins(4, 6, 2, 6)
        self.main_layout.setSpacing(5)
        self.main_layout.addWidget(self.icon_label)
        self.main_layout.addWidget(self.text_label)
        
        self.set_text(text)
        self.set_expanded(False)
        
    def set_text(self, text):
        self.text_label.setText("<b>{0}</b>".format(text))
        
    def set_background_color(self, color):
        if not color:
            color = QtWidgets.QPushButton().palette().color(QtGui.QPalette.Button)
        
        palette = self.palette()
        palette.setColor(QtGui.QPalette.Window, color)
        self.setPalette(palette)
        
    def is_expanded(self):
        return self._expanded
        
    def set_expanded(self, expanded):
        self._expanded = expanded
        
        if(self._expanded):
            self.icon_label.setPixmap(self.EXPANDED_PIXMAP)
        else:
            self.icon_label.setPixmap(self.COLLAPSED_PIXMAP)
            
    def mouseReleaseEvent(self, event):
        self.clicked.emit()  # pylint: disable=E1101
        
    def set_Margins(self,valueA,valueB,valueC,valueD):
        self.main_layout.setContentsMargins(valueA, valueB, valueC, valueD)
            
    
class CollapsibleWidget(QtWidgets.QWidget):
    
    def __init__(self, text, parent=None):
        super(CollapsibleWidget, self).__init__(parent)
        
        self.header_wdg = CollapsibleHeader(text)
        self.header_wdg.clicked.connect(self.on_header_clicked)  # pylint: disable=E1101
        
        self.body_wdg = QtWidgets.QWidget()
        
        self.body_layout = QtWidgets.QVBoxLayout(self.body_wdg)
        self.body_layout.setContentsMargins(0, 0, 0, 0)
        self.body_layout.setSpacing(2)
        
        self.main_layout = QtWidgets.QVBoxLayout(self)
        self.main_layout.setContentsMargins(0, 0, 0, 0)
        self.main_layout.addWidget(self.header_wdg)
        self.main_layout.addWidget(self.body_wdg)
        
        self.set_expanded(False)
        
    def set_Margins(self,valueA,valueB,valueC,valueD):
        self.header_wdg.setContentsMargins(valueA, valueB, valueC, valueD)

        
    def add_widget(self, widget):
        self.body_layout.addWidget(widget)
        
    def add_layout(self, layout):
        self.body_layout.addLayout(layout)
        
    def set_expanded(self, expanded):
        self.header_wdg.set_expanded(expanded)
        self.body_wdg.setVisible(expanded)
        
    def set_header_background_color(self, color):
        self.header_wdg.set_background_color(color)
        
    def on_header_clicked(self):
        self.set_expanded(not self.header_wdg.is_expanded())
        
    def set_Margins(self,valueA,valueB,valueC,valueD):
        self.header_wdg.set_Margins(valueA, valueB, valueC, valueD)
       



class SampleUI(QtWidgets.QWidget):

    WINDOW_TITLE = "Sample UI"
    UI_NAME = "SampleUI"

    ui_instance = None


    @classmethod
    def display(cls):
        if cls.ui_instance:
            cls.ui_instance.show_workspace_control()
        else:
            cls.ui_instance = SampleUI()

    @classmethod
    def get_workspace_control_name(cls):
        return "{0}WorkspaceControl".format(cls.UI_NAME)


    def __init__(self):
        super(SampleUI, self).__init__()

        self.setObjectName(self.__class__.UI_NAME)
        self.setMinimumSize(150, 100)
        self.create_widgets_history()
        self.widgets_sphere()
        self.widgets_cube()
        self.widgets_cylinder()
        self.widgets_plane()
        self.widgets_torus()
        self.widgets_cone()
        self.widgets_disc()
        self.widgets_gear()
        self.widgets_helix()
        self.widgets_pipe()
        self.widgets_platonic()
        self.widgets_primatives()
        self.widgets_prism()
        self.widgets_pyramid()
        self.widgets_soccer()
        self.widgets_superEllipse()
        self.widgets_extra()
        self.widgets_sculpting()
        self.widgets_divide()
        self.widgets_bevel()
        self.widgets_bridge()
        self.create_widgets()
        self.create_layout()
        self.create_connections()
        self.create_workspace_control()
            
    def set_text(self, text):
        self.text_label.setText("<b>{0}</b>".format(text))
    
    def create_widgets_history(self):

        
        self.deleteHistory_button = QtWidgets.QPushButton("History")
        self.deleteHistory_button.setIcon(QtGui.QIcon(":deleteClip.png"))
        self.deleteHistory_button.setIconSize(QtCore.QSize(25, 25))
        
        self.deleteNonDefHistory_button = QtWidgets.QPushButton("ND History")
        self.deleteNonDefHistory_button.setIcon(QtGui.QIcon(":deleteClip.png"))
        self.deleteNonDefHistory_button.setIconSize(QtCore.QSize(25, 25))
        
        self.history_tools = CollapsibleWidget("Delete History")
        self.history_tools.set_expanded(True)
    
    def create_sphere(self):
        mel.eval("CreatePolygonSphere;")
        
    def open_sphereOptions(self):
        mel.eval("CreatePolygonSphereOptions;")
        
    def popup_sphere(self, position):
        sphere_popup = QtWidgets.QMenu()
        sphere_action = QtWidgets.QAction('Settings', self)
        sphere_action.triggered.connect(self.open_sphereOptions)
        sphere_popup.addAction(sphere_action)
        sphere_popup.exec_(self.sphere_button.mapToGlobal(position))
        
    def widgets_sphere(self):
        self.sphere_button = QtWidgets.QPushButton("")
        self.sphere_button.setIcon(QtGui.QIcon(":polySphere.png"))
        self.sphere_button.setIconSize(QtCore.QSize(25, 25))
        self.sphere_button.clicked.connect(self.create_sphere)
        self.sphere_button.setContextMenuPolicy(QtCore.Qt.CustomContextMenu)
        self.sphere_button.customContextMenuRequested.connect(self.popup_sphere)
                                
    def create_cube(self):
        mel.eval("CreatePolygonCube;")
        
    def open_cubeOptions(self):
        mel.eval("CreatePolygonCubeOptions;")
        
    def popup_cube(self, position):
        cube_popup = QtWidgets.QMenu()
        cube_action = QtWidgets.QAction('Settings', self)
        cube_action.triggered.connect(self.open_cubeOptions)
        cube_popup.addAction(cube_action)
        cube_popup.exec_(self.cube_button.mapToGlobal(position))
        
    def widgets_cube(self):
        self.cube_button = QtWidgets.QPushButton("")
        self.cube_button.setIcon(QtGui.QIcon(":polyCube.png"))
        self.cube_button.setIconSize(QtCore.QSize(25, 25))
        self.cube_button.clicked.connect(self.create_cube)
        self.cube_button.setContextMenuPolicy(QtCore.Qt.CustomContextMenu)
        self.cube_button.customContextMenuRequested.connect(self.popup_cube)
        
    def create_cylinder(self):
        mel.eval("CreatePolygonCylinder;")
        
    def create_cylinder(self):
        mel.eval("CreatePolygonCylinder;")
        
    def open_cylinderOptions(self):
        mel.eval("CreatePolygonCylinderOptions;")
        
    def popup_cylinder(self, position):
        cylinder_popup = QtWidgets.QMenu()
        cylinder_action = QtWidgets.QAction('Settings', self)
        cylinder_action.triggered.connect(self.open_cylinderOptions)
        cylinder_popup.addAction(cylinder_action)
        cylinder_popup.exec_(self.cylinder_button.mapToGlobal(position))
        
    def widgets_cylinder(self):
        self.cylinder_button = QtWidgets.QPushButton("")
        self.cylinder_button.setIcon(QtGui.QIcon(":polyCylinder.png"))
        self.cylinder_button.setIconSize(QtCore.QSize(25, 25))
        self.cylinder_button.clicked.connect(self.create_cylinder)
        self.cylinder_button.setContextMenuPolicy(QtCore.Qt.CustomContextMenu)
        self.cylinder_button.customContextMenuRequested.connect(self.popup_cylinder)
        
    def create_plane(self):
        mel.eval("CreatePolygonPlane;")
        
    def open_planeOptions(self):
        mel.eval("CreatePolygonPlaneOptions;")
        
    def popup_plane(self, position):
        plane_popup = QtWidgets.QMenu()
        plane_action = QtWidgets.QAction('Settings', self)
        plane_action.triggered.connect(self.open_planeOptions)
        plane_popup.addAction(plane_action)
        plane_popup.exec_(self.plane_button.mapToGlobal(position))
        
    def widgets_plane(self):
        self.plane_button = QtWidgets.QPushButton("")
        self.plane_button.setIcon(QtGui.QIcon(":polyMesh.png"))
        self.plane_button.setIconSize(QtCore.QSize(25, 25))
        self.plane_button.clicked.connect(self.create_plane)
        self.plane_button.setContextMenuPolicy(QtCore.Qt.CustomContextMenu)
        self.plane_button.customContextMenuRequested.connect(self.popup_plane)

    def create_plane(self):
        mel.eval("CreatePolygonPlane;")
        
    def open_planeOptions(self):
        mel.eval("CreatePolygonPlaneOptions;")
        
    def popup_plane(self, position):
        plane_popup = QtWidgets.QMenu()
        plane_action = QtWidgets.QAction('Settings', self)
        plane_action.triggered.connect(self.open_planeOptions)
        plane_popup.addAction(plane_action)
        plane_popup.exec_(self.plane_button.mapToGlobal(position))
        
    def widgets_plane(self):
        self.plane_button = QtWidgets.QPushButton("")
        self.plane_button.setIcon(QtGui.QIcon(":polyMesh.png"))
        self.plane_button.setIconSize(QtCore.QSize(25, 25))
        self.plane_button.clicked.connect(self.create_plane)
        self.plane_button.setContextMenuPolicy(QtCore.Qt.CustomContextMenu)
        self.plane_button.customContextMenuRequested.connect(self.popup_plane)        

    def create_torus(self):
        mel.eval("CreatePolygonTorus;")
        
    def open_torusOptions(self):
        mel.eval("CreatePolygonTorusOptions;")
        
    def popup_torus(self, position):
        torus_popup = QtWidgets.QMenu()
        torus_action = QtWidgets.QAction('Settings', self)
        torus_action.triggered.connect(self.open_torusOptions)
        torus_popup.addAction(torus_action)
        torus_popup.exec_(self.torus_button.mapToGlobal(position))
        
    def widgets_torus(self):
        self.torus_button = QtWidgets.QPushButton("")
        self.torus_button.setIcon(QtGui.QIcon(":polyTorus.png"))
        self.torus_button.setIconSize(QtCore.QSize(25, 25))
        self.torus_button.clicked.connect(self.create_torus)
        self.torus_button.setContextMenuPolicy(QtCore.Qt.CustomContextMenu)
        self.torus_button.customContextMenuRequested.connect(self.popup_torus) 
        
    def create_cone(self):
        mel.eval("CreatePolygonCone;")
        
    def open_coneOptions(self):
        mel.eval("CreatePolygonConeOptions;")
        
    def popup_cone(self, position):
        cone_popup = QtWidgets.QMenu()
        cone_action = QtWidgets.QAction('Settings', self)
        cone_action.triggered.connect(self.open_coneOptions)
        cone_popup.addAction(cone_action)
        cone_popup.exec_(self.cone_button.mapToGlobal(position))
        
    def widgets_cone(self):
        self.cone_button = QtWidgets.QPushButton("")
        self.cone_button.setIcon(QtGui.QIcon(":polyCone.png"))
        self.cone_button.setIconSize(QtCore.QSize(25, 25))
        self.cone_button.clicked.connect(self.create_cone)
        self.cone_button.setContextMenuPolicy(QtCore.Qt.CustomContextMenu)
        self.cone_button.customContextMenuRequested.connect(self.popup_cone) 
        
    def create_disc(self):
        cmds.polyDisc()
        
    def create_platonicSolid(self):
        cmds.polyPlatonicSolid()
        
    def create_pyramid(self):
        cmds.polyPyramid()
        
    def create_pyramid(self):
        cmds.polyPyramid()
        
    def create_prism(self):
        cmds.polyPrism()
 
    def create_pipe(self):
        cmds.polyPipe()       
        
    def create_helix(self):
        cmds.polyHelix()  
        
    def create_gear(self):
        cmds.polyGear()        
        
    def create_soccerBall(self):
        cmds.polyPrimitive()   
        
    def create_superEllipse(self):
        cmds.polySuperShape()
        

    
    def widgets_disc(self):     
        self.disc_button = QtWidgets.QPushButton("")
        self.disc_button.setIcon(QtGui.QIcon(":polyDisc.png"))
        self.disc_button.setIconSize(QtCore.QSize(25, 25))
   
    def widgets_platonic(self):
        self.platonic_button = QtWidgets.QPushButton("")
        self.platonic_button.setIcon(QtGui.QIcon(":polyPlatonic.png"))
        self.platonic_button.setIconSize(QtCore.QSize(25, 25))
    
    def widgets_pyramid(self):    
        self.pyramid_button = QtWidgets.QPushButton("")
        self.pyramid_button.setIcon(QtGui.QIcon(":polyPyramid.png"))
        self.pyramid_button.setIconSize(QtCore.QSize(25, 25))
    
    def widgets_prism(self):    
        self.prism_button = QtWidgets.QPushButton("")
        self.prism_button.setIcon(QtGui.QIcon(":polyPrism.png"))
        self.prism_button.setIconSize(QtCore.QSize(25, 25))
    
    def widgets_pipe(self):    
        self.pipe_button = QtWidgets.QPushButton("")
        self.pipe_button.setIcon(QtGui.QIcon(":polyPipe.png"))
        self.pipe_button.setIconSize(QtCore.QSize(25, 25))
    
    def widgets_helix(self):    
        self.helix_button = QtWidgets.QPushButton("")
        self.helix_button.setIcon(QtGui.QIcon(":polyHelix.png"))
        self.helix_button.setIconSize(QtCore.QSize(25, 25))
    
    def widgets_gear(self):    
        self.gear_button = QtWidgets.QPushButton("")
        self.gear_button.setIcon(QtGui.QIcon(":polyGear.png"))
        self.gear_button.setIconSize(QtCore.QSize(25, 25))
 
    def widgets_soccer(self):
        self.soccer_button = QtWidgets.QPushButton("")
        self.soccer_button.setIcon(QtGui.QIcon(":polySoccerBall.png"))
        self.soccer_button.setIconSize(QtCore.QSize(25, 25))
 
    def widgets_superEllipse(self):
        self.superEllipse_button = QtWidgets.QPushButton("")
        self.superEllipse_button.setIcon(QtGui.QIcon(":polySuperEllipse.png"))
        self.superEllipse_button.setIconSize(QtCore.QSize(25, 25))
    
    def widgets_primatives(self):    
        self.polygon_primatives = CollapsibleWidget("Polygon Primatives")
        self.polygon_primatives.set_expanded(True)
        self.polygon_primativesSec = CollapsibleWidget("")
        self.polygon_primativesSec.set_expanded(False)
        self.polygon_primativesSec.set_Margins(4,0,0,0)
        self.polygon_primativesSec.set_header_background_color(QtGui.QColor(125,125, 125, 0))
        
    def create_connections_primatives(self):
        self.deleteHistory_button.clicked.connect(self.delete_history)
        self.deleteNonDefHistory_button.clicked.connect(self.delete_nonDifHistory)
        '''
        self.cylinder_button.clicked.connect(self.create_cylinder)
        self.cone_button.clicked.connect(self.create_cone)
        self.torus_button.clicked.connect(self.create_torus)
        self.plane_button.clicked.connect(self.create_plane)
        self.disc_button.clicked.connect(self.create_disc)
        self.platonic_button.clicked.connect(self.create_platonicSolid)
        self.pyramid_button.clicked.connect(self.create_pyramid)
        self.prism_button.clicked.connect(self.create_prism)
        self.pipe_button.clicked.connect(self.create_pipe)
        self.helix_button.clicked.connect(self.create_helix)
        self.gear_button.clicked.connect(self.create_gear)
        self.soccer_button.clicked.connect(self.create_soccerBall)
        self.superEllipse_button.clicked.connect(self.create_superEllipse)
        '''
        
    def perform_divide(self):
        print "running"
        mel.eval("SubdividePolygon;")
        
    def open_divideOptions(self):
        mel.eval("SubdividePolygonOptions;")
        
    def popup_divide(self, position):
        divide_popup = QtWidgets.QMenu()
        divide_action = QtWidgets.QAction('Settings', self)
        divide_action.triggered.connect(self.open_divideOptions)
        divide_popup.addAction(divide_action)
        divide_popup.exec_(self.divide_button.mapToGlobal(position))
 
    def widgets_divide(self):
        self.divide_button = QtWidgets.QPushButton("Divide")
        self.divide_button.setIcon(QtGui.QIcon(":polySubdFacet.png"))
        self.divide_button.setIconSize(QtCore.QSize(25, 25))
        self.divide_button.clicked.connect(self.perform_divide)
        self.divide_button.setContextMenuPolicy(QtCore.Qt.CustomContextMenu)
        self.divide_button.customContextMenuRequested.connect(self.popup_divide) 
        
    def perform_bevel(self):
        mel.eval("BevelPolygon;")
        
    def open_bevelOptions(self):
        mel.eval("BevelPolygonOptions")
        
    def popup_bevel(self, position):
        bevel_popup = QtWidgets.QMenu()
        bevel_action = QtWidgets.QAction('Settings', self)
        bevel_action.triggered.connect(self.open_bevelOptions)
        bevel_popup.addAction(bevel_action)
        bevel_popup.exec_(self.bevel_button.mapToGlobal(position))
 
    def widgets_bevel(self):
        self.bevel_button = QtWidgets.QPushButton("Bevel")
        self.bevel_button.setIcon(QtGui.QIcon(":polyBevel.png"))
        self.bevel_button.setIconSize(QtCore.QSize(25, 25))
        self.bevel_button.clicked.connect(self.perform_bevel)
        self.bevel_button.setContextMenuPolicy(QtCore.Qt.CustomContextMenu)
        self.bevel_button.customContextMenuRequested.connect(self.popup_bevel) 
        
    def perform_bridge(self):
        mel.eval("BevelPolygon;")
        
    def open_bevelOptions(self):
        mel.eval("BevelPolygonOptions")
        
    def popup_bevel(self, position):
        bevel_popup = QtWidgets.QMenu()
        bevel_action = QtWidgets.QAction('Settings', self)
        bevel_action.triggered.connect(self.open_bevelOptions)
        bevel_popup.addAction(bevel_action)
        bevel_popup.exec_(self.bevel_button.mapToGlobal(position))
 
    def widgets_bevel(self):
        self.bevel_button = QtWidgets.QPushButton("Bevel")
        self.bevel_button.setIcon(QtGui.QIcon(":polyBevel.png"))
        self.bevel_button.setIconSize(QtCore.QSize(25, 25))
        self.bevel_button.clicked.connect(self.perform_bevel)
        self.bevel_button.setContextMenuPolicy(QtCore.Qt.CustomContextMenu)
        self.bevel_button.customContextMenuRequested.connect(self.popup_bevel) 
        
    def perform_bridge(self):
        mel.eval("BridgeEdge;")
        
    def open_bridgeOptions(self):
        mel.eval("BridgeEdgeOptions;")
        
    def popup_bridge(self, position):
        bridge_popup = QtWidgets.QMenu()
        bridge_action = QtWidgets.QAction('Settings', self)
        bridge_action.triggered.connect(self.open_bridgeOptions)
        bridge_popup.addAction(bridge_action)
        bridge_popup.exec_(self.bridge_button.mapToGlobal(position))
 
    def widgets_bridge(self):
        self.bridge_button = QtWidgets.QPushButton("bridge")
        self.bridge_button.setIcon(QtGui.QIcon(":polyBridge.png"))
        self.bridge_button.setIconSize(QtCore.QSize(25, 25))
        self.bridge_button.clicked.connect(self.perform_bridge)
        self.bridge_button.setContextMenuPolicy(QtCore.Qt.CustomContextMenu)
        self.bridge_button.customContextMenuRequested.connect(self.popup_bridge) 
        
    def create_widgets(self):
        
        #Mesh Tool Buttons
        self.mesh_menu = CollapsibleWidget("Mesh")
        self.mesh_menu.set_expanded(True)
        
        self.union_button = QtWidgets.QPushButton("Union")
        self.union_button.setIcon(QtGui.QIcon(":polyBooleansUnion.png"))
        self.union_button.setIconSize(QtCore.QSize(25, 25))    
        
        self.difference_button = QtWidgets.QPushButton("Difference")
        self.difference_button.setIcon(QtGui.QIcon(":polyBooleansDifference.png"))
        self.difference_button.setIconSize(QtCore.QSize(25, 25))  
        
        self.intersection_button = QtWidgets.QPushButton("intersection ")
        self.intersection_button.setIcon(QtGui.QIcon(":polyBooleansIntersection.png"))
        self.intersection_button.setIconSize(QtCore.QSize(25, 25))  
        
        self.combine_button = QtWidgets.QPushButton("Combine")
        self.combine_button.setIcon(QtGui.QIcon(":polyUnite.png"))
        self.combine_button.setIconSize(QtCore.QSize(25, 25))
        
        self.seperate_button = QtWidgets.QPushButton("Seperate")
        self.seperate_button.setIcon(QtGui.QIcon(":polySeparate.png"))
        self.seperate_button.setIconSize(QtCore.QSize(25, 25))
        
        self.conform_button = QtWidgets.QPushButton("Conform")
        self.conform_button.setIcon(QtGui.QIcon(":polySeparate.png"))
        self.conform_button.setIconSize(QtCore.QSize(25, 25))
        
        self.fillHole_button = QtWidgets.QPushButton("CFill Hole")
        self.fillHole_button.setIcon(QtGui.QIcon(":polyCloseBorder.png"))
        self.fillHole_button.setIconSize(QtCore.QSize(25, 25))
        
        self.reduce_button = QtWidgets.QPushButton("Reduce")
        self.reduce_button.setIcon(QtGui.QIcon(":polyReduce.png"))
        self.reduce_button.setIconSize(QtCore.QSize(25, 25))
        
        self.remesh_button = QtWidgets.QPushButton("Remesh")
        self.remesh_button.setIcon(QtGui.QIcon(":polyRemesh.png"))
        self.remesh_button.setIconSize(QtCore.QSize(25, 25))
        
        self.retopo_button = QtWidgets.QPushButton("Retopo")
        self.retopo_button.setIcon(QtGui.QIcon(":polyRetopo.png"))
        self.retopo_button.setIconSize(QtCore.QSize(25, 25))
        
        self.retopo_button = QtWidgets.QPushButton("Retopo")
        self.retopo_button.setIcon(QtGui.QIcon(":polyRetopo.png"))
        self.retopo_button.setIconSize(QtCore.QSize(25, 25))
        
        self.smooth_button = QtWidgets.QPushButton("Smooth")
        self.smooth_button.setIcon(QtGui.QIcon(":polySmooth.png"))
        self.smooth_button.setIconSize(QtCore.QSize(25, 25))
        
        self.smooth_button = QtWidgets.QPushButton("Smooth")
        self.smooth_button.setIcon(QtGui.QIcon(":polySmooth.png"))
        self.smooth_button.setIconSize(QtCore.QSize(25, 25))
        
        self.triangulate_button = QtWidgets.QPushButton("Tri")
        self.triangulate_button.setIcon(QtGui.QIcon(":polyTriangulate.png"))
        self.triangulate_button.setIconSize(QtCore.QSize(25, 25))
        
        self.quadrangulate_button = QtWidgets.QPushButton("Quad")
        self.quadrangulate_button.setIcon(QtGui.QIcon(":polyQuad.png"))
        self.quadrangulate_button.setIconSize(QtCore.QSize(25, 25))
        
        self.mirror_button = QtWidgets.QPushButton("Mirror")
        self.mirror_button.setIcon(QtGui.QIcon(":polyMirrorGeometry.png"))
        self.mirror_button.setIconSize(QtCore.QSize(25, 25))
        
    def widgets_sculpting(self):    
        self.sculpting_menu = CollapsibleWidget("Sculpting")
        self.sculpting_menu.set_expanded(True)
        
        self.secSculpting_menu = CollapsibleWidget("")
        self.secSculpting_menu.set_expanded(False)
        self.secSculpting_menu.set_Margins(4,0,0,0)
        self.secSculpting_menu.set_header_background_color(QtGui.QColor(125,125, 125,0))

        self.lift_button = QtWidgets.QPushButton("")
        self.lift_button.setIcon(QtGui.QIcon(":Sculpt.png"))
        self.lift_button.setIconSize(QtCore.QSize(25, 25))
        
        self.sculptSmooth_button = QtWidgets.QPushButton("")
        self.sculptSmooth_button.setIcon(QtGui.QIcon(":Smooth.png"))
        self.sculptSmooth_button.setIconSize(QtCore.QSize(25, 25))
        
           
        self.sculptRelax_button = QtWidgets.QPushButton("")
        self.sculptRelax_button.setIcon(QtGui.QIcon(":Relax.png"))
        self.sculptRelax_button.setIconSize(QtCore.QSize(25, 25))
        
        self.sculptGrab_button = QtWidgets.QPushButton("")
        self.sculptGrab_button.setIcon(QtGui.QIcon(":Grab.png"))
        self.sculptGrab_button.setIconSize(QtCore.QSize(25, 25))
        
        self.sculptPinch_button = QtWidgets.QPushButton("")
        self.sculptPinch_button.setIcon(QtGui.QIcon(":Pinch.png"))
        self.sculptPinch_button.setIconSize(QtCore.QSize(25, 25))
        
        self.sculptFlatten_button = QtWidgets.QPushButton("")
        self.sculptFlatten_button.setIcon(QtGui.QIcon(":Flatten.png"))
        self.sculptFlatten_button.setIconSize(QtCore.QSize(25, 25))
                   
        self.sculptFoamy_button = QtWidgets.QPushButton("")
        self.sculptFoamy_button.setIcon(QtGui.QIcon(":Foamy.png"))
        self.sculptFoamy_button.setIconSize(QtCore.QSize(25, 25))      
        
        self.sculptSpray_button = QtWidgets.QPushButton("")
        self.sculptSpray_button.setIcon(QtGui.QIcon(":Spray.png"))
        self.sculptSpray_button.setIconSize(QtCore.QSize(25, 25))    
        
        self.sculptRepeat_button = QtWidgets.QPushButton("")
        self.sculptRepeat_button.setIcon(QtGui.QIcon(":Spray.png"))
        self.sculptRepeat_button.setIconSize(QtCore.QSize(25, 25))   
        
        self.sculptImprint_button = QtWidgets.QPushButton("")
        self.sculptImprint_button.setIcon(QtGui.QIcon(":Imprint.png"))
        self.sculptImprint_button.setIconSize(QtCore.QSize(25, 25))     
        
        self.sculptWax_button = QtWidgets.QPushButton("")
        self.sculptWax_button.setIcon(QtGui.QIcon(":Wax.png"))
        self.sculptWax_button.setIconSize(QtCore.QSize(25, 25))      
        
        self.sculptScrape_button = QtWidgets.QPushButton("")
        self.sculptScrape_button.setIcon(QtGui.QIcon(":Scrape.png"))
        self.sculptScrape_button.setIconSize(QtCore.QSize(25, 25))  
        
        self.sculptFill_button = QtWidgets.QPushButton("")
        self.sculptFill_button.setIcon(QtGui.QIcon(":Fill.png"))
        self.sculptFill_button.setIconSize(QtCore.QSize(25, 25)) 
        
        self.sculptKnife_button = QtWidgets.QPushButton("")
        self.sculptKnife_button.setIcon(QtGui.QIcon(":Knife.png"))
        self.sculptKnife_button.setIconSize(QtCore.QSize(25, 25)) 
        
        self.sculptSmear_button = QtWidgets.QPushButton("")
        self.sculptSmear_button.setIcon(QtGui.QIcon(":Smear.png"))
        self.sculptSmear_button.setIconSize(QtCore.QSize(25, 25)) 
        
        self.sculptBulge_button = QtWidgets.QPushButton("")
        self.sculptBulge_button.setIcon(QtGui.QIcon(":Bulge.png"))
        self.sculptBulge_button.setIconSize(QtCore.QSize(25, 25)) 
        
        self.sculptAmplify_button = QtWidgets.QPushButton("")
        self.sculptAmplify_button.setIcon(QtGui.QIcon(":Amplify.png"))
        self.sculptAmplify_button.setIconSize(QtCore.QSize(25, 25)) 
        
        self.sculptFreeze_button = QtWidgets.QPushButton("")
        self.sculptFreeze_button.setIcon(QtGui.QIcon(":Freeze.png"))
        self.sculptFreeze_button.setIconSize(QtCore.QSize(25, 25)) 
        
        self.sculptFreezeSelect_button = QtWidgets.QPushButton("")
        self.sculptFreezeSelect_button.setIcon(QtGui.QIcon(":freezeSelected.png"))
        self.sculptFreezeSelect_button.setIconSize(QtCore.QSize(25, 25)) 
        
        self.sculptObjects_button = QtWidgets.QPushButton("")
        self.sculptObjects_button.setIcon(QtGui.QIcon(":Objects.png"))
        self.sculptObjects_button.setIconSize(QtCore.QSize(25, 25)) 
    
    def widgets_extra(self):    
        # Edit Mesh Tools          
        self.editMesh_menu = CollapsibleWidget("Edit Mesh Tools  ")
        self.editMesh_menu.set_expanded(True)  
        self.editMesh_menuSec = CollapsibleWidget("")
        self.editMesh_menuSec.set_expanded(True)  
        self.editMesh_menuSec.set_expanded(False)
        self.editMesh_menuSec.set_Margins(4,0,0,0)
        self.editMesh_menuSec.set_header_background_color(QtGui.QColor(125,125, 125, 0))                
        
        self.bridge_button= QtWidgets.QPushButton("Bridge")
        self.bridge_button.setIcon(QtGui.QIcon(":polyBridge.png"))
        self.bridge_button.setIconSize(QtCore.QSize(25, 25))     
        
        self.circularize_button= QtWidgets.QPushButton("circular")
        self.circularize_button.setIcon(QtGui.QIcon(":polyCircularize.png"))
        self.circularize_button.setIconSize(QtCore.QSize(25, 25))  
        
        self.collapseEdge_button= QtWidgets.QPushButton("collapse")
        self.collapseEdge_button.setIcon(QtGui.QIcon(":polyCollapseEdge.png"))
        self.collapseEdge_button.setIconSize(QtCore.QSize(25, 25))  
        
        self.connect_button= QtWidgets.QPushButton("connect")
        self.connect_button.setIcon(QtGui.QIcon(":polyConnectComponents.png"))
        self.connect_button.setIconSize(QtCore.QSize(25, 25))  
        
        self.detach_button= QtWidgets.QPushButton("detach")
        self.detach_button.setIcon(QtGui.QIcon(":polySplitVertex.png"))
        self.detach_button.setIconSize(QtCore.QSize(25, 25)) 
        
        self.extrude_button= QtWidgets.QPushButton("extrude")
        self.extrude_button.setIcon(QtGui.QIcon(":polyExtrudeFacet.png"))
        self.extrude_button.setIconSize(QtCore.QSize(25, 25)) 
        
        self.merge_button= QtWidgets.QPushButton("merge")
        self.merge_button.setIcon(QtGui.QIcon(":polyMerge.png"))
        self.merge_button.setIconSize(QtCore.QSize(25, 25)) 
        
        self.mergeToCenter_button= QtWidgets.QPushButton("meger center")
        self.mergeToCenter_button.setIcon(QtGui.QIcon(":MergeToCenter"))
        self.mergeToCenter_button.setIconSize(QtCore.QSize(25, 25)) 
        
        self.transform_button= QtWidgets.QPushButton("move vertex")
        self.transform_button.setIcon(QtGui.QIcon(":polyMoveVertex.png"))
        self.transform_button.setIconSize(QtCore.QSize(25, 25)) 
        
        self.flip_button= QtWidgets.QPushButton("flip")
        self.flip_button.setIcon(QtGui.QIcon(":polyFlip.png"))
        self.flip_button.setIconSize(QtCore.QSize(25, 25)) 
        
        self.symmetrize_button= QtWidgets.QPushButton("symmetrize")
        self.symmetrize_button.setIcon(QtGui.QIcon(":symmetrize.png"))
        self.symmetrize_button.setIconSize(QtCore.QSize(25, 25)) 
        
        self.averageVert_button= QtWidgets.QPushButton("average")
        self.averageVert_button.setIcon(QtGui.QIcon(":polyAverageVertex.png"))
        self.averageVert_button.setIconSize(QtCore.QSize(25, 25)) 
        
        self.chamfer_button= QtWidgets.QPushButton("chamfer")
        self.chamfer_button.setIcon(QtGui.QIcon(":polyChamfer.png"))
        self.chamfer_button.setIconSize(QtCore.QSize(25, 25)) 
        
        self.reorderVert_button= QtWidgets.QPushButton("reorder")
        self.reorderVert_button.setIcon(QtGui.QIcon(":reorderIDs.png"))
        self.reorderVert_button.setIconSize(QtCore.QSize(25, 25)) 
        
        self.delEdgeVert_button= QtWidgets.QPushButton("Del Edge/Vert")
        self.delEdgeVert_button.setIcon(QtGui.QIcon(":polyDelEdgeVertex.png"))
        self.delEdgeVert_button.setIconSize(QtCore.QSize(25, 25)) 
        
        self.edgeflow_button= QtWidgets.QPushButton("Edit Flow")
        self.edgeflow_button.setIcon(QtGui.QIcon(":polyEditEdgeFlow.png"))
        self.edgeflow_button.setIconSize(QtCore.QSize(25, 25)) 
        
        self.flipEdge_button= QtWidgets.QPushButton("Flip Edge")
        self.flipEdge_button.setIcon(QtGui.QIcon(":polyFlipEdge.png"))
        self.flipEdge_button.setIconSize(QtCore.QSize(25, 25)) 
        
        self.spinEdgeBack_button= QtWidgets.QPushButton("Spin Edge")
        self.spinEdgeBack_button.setIcon(QtGui.QIcon(":polySpinEdgeBackward.png"))
        self.spinEdgeBack_button.setIconSize(QtCore.QSize(25, 25)) 
        
        self.spinEdgeForw_button= QtWidgets.QPushButton("Spin Edge")
        self.spinEdgeForw_button.setIcon(QtGui.QIcon(":polySpinEdgeForward.png"))
        self.spinEdgeForw_button.setIconSize(QtCore.QSize(25, 25)) 
        
        self.invisibleFace_button= QtWidgets.QPushButton("Invisible Face")
        self.invisibleFace_button.setIcon(QtGui.QIcon(":polyAssignSubdivHole.png"))
        self.invisibleFace_button.setIconSize(QtCore.QSize(25, 25)) 
        
        self.duplicate_button= QtWidgets.QPushButton("Duplicate")
        self.duplicate_button.setIcon(QtGui.QIcon(":polyDuplicateFacet.png"))
        self.duplicate_button.setIconSize(QtCore.QSize(25, 25)) 
        
        self.extract_button= QtWidgets.QPushButton("Extract")
        self.extract_button.setIcon(QtGui.QIcon(":polyChipOff.png"))
        self.extract_button.setIconSize(QtCore.QSize(25, 25)) 
        
        self.poke_button= QtWidgets.QPushButton("Poke")
        self.poke_button.setIcon(QtGui.QIcon(":polyPoke.png"))
        self.poke_button.setIconSize(QtCore.QSize(25, 25)) 
        
        self.wedge_button= QtWidgets.QPushButton("Wedge")
        self.wedge_button.setIcon(QtGui.QIcon(":polyWedgeFace.png"))
        self.wedge_button.setIconSize(QtCore.QSize(25, 25)) 
        
        self.projectCurve_button= QtWidgets.QPushButton("Project Curve")
        self.projectCurve_button.setIcon(QtGui.QIcon(":projectCurve_Poly.png"))
        self.projectCurve_button.setIconSize(QtCore.QSize(25, 25)) 
        
        self.splitMeshCurve_button= QtWidgets.QPushButton("Cuve Spit")
        self.splitMeshCurve_button.setIcon(QtGui.QIcon(":projectCurveSplit_Poly.png"))
        self.splitMeshCurve_button.setIconSize(QtCore.QSize(25, 25)) 

        #Mesh Tools
        self.meshTools_menu = CollapsibleWidget("Mesh Tools")
        self.meshTools_menu.set_expanded(True)

        self.polyAppend_button= QtWidgets.QPushButton("Poly Append")
        self.polyAppend_button.setIcon(QtGui.QIcon(":polyAppendFacet.png"))
        self.polyAppend_button.setIconSize(QtCore.QSize(25, 25)) 
        
        self.connect_button= QtWidgets.QPushButton("connect")
        self.connect_button.setIcon(QtGui.QIcon(":connect_NEX32.png"))
        self.connect_button.setIconSize(QtCore.QSize(25, 25)) 
        
        self.polyCrease_button= QtWidgets.QPushButton("Crease")
        self.polyCrease_button.setIcon(QtGui.QIcon(":polyCrease.png"))
        self.polyCrease_button.setIconSize(QtCore.QSize(25, 25)) 
        
        self.createPoly_button= QtWidgets.QPushButton("Create Poly")
        self.createPoly_button.setIcon(QtGui.QIcon(":polyCreateFacet.png"))
        self.createPoly_button.setIconSize(QtCore.QSize(25, 25)) 
        
        self.insertEdge_button= QtWidgets.QPushButton("Insert Edge")
        self.insertEdge_button.setIcon(QtGui.QIcon(":polySplitEdgeRing.png"))
        self.insertEdge_button.setIconSize(QtCore.QSize(25, 25)) 
            
        self.makeHole_button= QtWidgets.QPushButton("Make Hole")
        self.makeHole_button.setIcon(QtGui.QIcon(":polyMergeFacet.png"))
        self.makeHole_button.setIconSize(QtCore.QSize(25, 25)) 
        
        self.multiCut_button= QtWidgets.QPushButton("Multi-Cut")
        self.multiCut_button.setIcon(QtGui.QIcon(":multiCut_NEX32.png"))
        self.multiCut_button.setIconSize(QtCore.QSize(25, 25)) 
        
        self.offsetEdge_button= QtWidgets.QPushButton("Offset Edge")
        self.offsetEdge_button.setIcon(QtGui.QIcon(":polyDuplicateEdgeLoop.png"))
        self.offsetEdge_button.setIconSize(QtCore.QSize(25, 25)) 
    
        self.paintReduceWeights_button= QtWidgets.QPushButton("Paint Reduce")
        self.paintReduceWeights_button.setIcon(QtGui.QIcon(":polyPaintReduceWeights.png"))
        self.paintReduceWeights_button.setIconSize(QtCore.QSize(25, 25)) 
        
        self.paintTransferWeights_button= QtWidgets.QPushButton("Offset Edge")
        self.paintTransferWeights_button.setIcon(QtGui.QIcon(":polyTransferAttributesWeights.png"))
        self.paintTransferWeights_button.setIconSize(QtCore.QSize(25, 25)) 
        
        self.quadDraw_button= QtWidgets.QPushButton("Quad Draw")
        self.quadDraw_button.setIcon(QtGui.QIcon(":quadDraw_NEX32.png"))
        self.quadDraw_button.setIconSize(QtCore.QSize(25, 25)) 
        
        self.slideEdge_button= QtWidgets.QPushButton("Slide Edge")
        self.slideEdge_button.setIcon(QtGui.QIcon(":slideEdgeTool.png"))
        self.slideEdge_button.setIconSize(QtCore.QSize(25, 25)) 
        
        self.targetWeld_button= QtWidgets.QPushButton("Target Weld")
        self.targetWeld_button.setIcon(QtGui.QIcon(":weld_NEX32.png"))
        self.targetWeld_button.setIconSize(QtCore.QSize(25, 25)) 


    def create_layout(self):
        
        history_layout1 = QtWidgets.QHBoxLayout()
        history_layout1.addWidget(self.deleteHistory_button)
        history_layout1.addWidget(self.deleteNonDefHistory_button)
        history_layout1.setAlignment(QtCore.Qt.AlignTop)
        
        prim_layout1 = QtWidgets.QHBoxLayout()
        prim_layout1.addWidget(self.sphere_button)
        prim_layout1.addWidget(self.cube_button)
        prim_layout1.addWidget(self.plane_button)
        prim_layout1.addWidget(self.cylinder_button)
        prim_layout1.addWidget(self.torus_button)
        prim_layout1.addWidget(self.cone_button)
        
        
        #prim_layout1.addWidget(self.cone_button)
        #prim_layout1.addWidget(self.torus_button)
        
        prim_layout2 = QtWidgets.QHBoxLayout()
        prim_layout2.addWidget(self.disc_button)
        prim_layout2.addWidget(self.platonic_button)
        prim_layout2.addWidget(self.pyramid_button)
        prim_layout2.addWidget(self.prism_button)
        
        prim_layout3 = QtWidgets.QHBoxLayout()
        prim_layout3.addWidget(self.pipe_button)
        prim_layout3.addWidget(self.helix_button)
        prim_layout3.addWidget(self.gear_button)
        prim_layout3.addWidget(self.soccer_button)
        prim_layout3.addWidget(self.superEllipse_button)
        
        sculpt_layout1 = QtWidgets.QHBoxLayout()
        sculpt_layout1.addWidget(self.lift_button)
        sculpt_layout1.addWidget(self.sculptSmooth_button)
        sculpt_layout1.addWidget(self.sculptRelax_button)
        sculpt_layout1.addWidget(self.sculptGrab_button)
        sculpt_layout1.addWidget(self.sculptPinch_button)
        sculpt_layout1.addWidget(self.sculptFlatten_button)
        sculpt_layout1.addWidget(self.sculptObjects_button)
        sculpt_layout1.setAlignment(QtCore.Qt.AlignTop)

        sculpt_layout2 = QtWidgets.QHBoxLayout()

        sculpt_layout2.addWidget(self.sculptFoamy_button)
        sculpt_layout2.addWidget(self.sculptSpray_button)
        sculpt_layout2.addWidget(self.sculptRepeat_button)
        sculpt_layout2.addWidget(self.sculptImprint_button)
        sculpt_layout2.setAlignment(QtCore.Qt.AlignTop)
        
        sculpt_layout3 = QtWidgets.QHBoxLayout()
        sculpt_layout3.addWidget(self.sculptWax_button)
        sculpt_layout3.addWidget(self.sculptScrape_button)
        sculpt_layout3.addWidget(self.sculptFill_button)
        sculpt_layout3.addWidget(self.sculptKnife_button)
        sculpt_layout3.addWidget(self.sculptSmear_button)
        sculpt_layout3.setAlignment(QtCore.Qt.AlignTop)
        
        sculpt_layout4 = QtWidgets.QHBoxLayout()
        sculpt_layout4.addWidget(self.sculptBulge_button)
        sculpt_layout4.addWidget(self.sculptAmplify_button)
        sculpt_layout4.addWidget(self.sculptFreeze_button)
        sculpt_layout4.addWidget(self.sculptFreezeSelect_button)
        sculpt_layout4.setAlignment(QtCore.Qt.AlignTop)

        mesh_layout1 = QtWidgets.QHBoxLayout()
        mesh_layout1.addWidget(self.union_button)
        mesh_layout1.addWidget(self.difference_button)
        mesh_layout1.addWidget(self.intersection_button)
        mesh_layout1.setAlignment(QtCore.Qt.AlignTop)
        
        mesh_layout2 = QtWidgets.QHBoxLayout()
        mesh_layout2.addWidget(self.combine_button)
        mesh_layout2.addWidget(self.seperate_button)
        mesh_layout2.addWidget(self.conform_button)
        mesh_layout2.setAlignment(QtCore.Qt.AlignTop)
        
        mesh_layout3 = QtWidgets.QHBoxLayout()
        #mesh_layout3.addWidget(self.fillHole_button)
        mesh_layout3.addWidget(self.reduce_button)
        mesh_layout3.addWidget(self.remesh_button)
        mesh_layout3.addWidget(self.retopo_button)
        mesh_layout3.setAlignment(QtCore.Qt.AlignTop)
        
        mesh_layout4 = QtWidgets.QHBoxLayout()
        mesh_layout4.setAlignment(QtCore.Qt.AlignTop)
        
        mesh_layout5 = QtWidgets.QHBoxLayout()
        mesh_layout5.addWidget(self.smooth_button)
        mesh_layout5.addWidget(self.triangulate_button)
        mesh_layout5.addWidget(self.quadrangulate_button)
        mesh_layout5.setAlignment(QtCore.Qt.AlignTop)
        
        mesh_layout6 = QtWidgets.QHBoxLayout()
        mesh_layout6.addWidget(self.mirror_button)
        mesh_layout5.setAlignment(QtCore.Qt.AlignTop)
        
        editMesh_layout1 = QtWidgets.QHBoxLayout()
        editMesh_layout1.addWidget(self.divide_button)
        editMesh_layout1.addWidget(self.bevel_button)
        editMesh_layout1.addWidget(self.bridge_button)
        editMesh_layout1.setAlignment(QtCore.Qt.AlignTop)
        
        editMesh_layout2 = QtWidgets.QHBoxLayout()
        editMesh_layout2.addWidget(self.circularize_button)
        editMesh_layout2.addWidget(self.collapseEdge_button)
        editMesh_layout2.setAlignment(QtCore.Qt.AlignTop)
        
        editMesh_layout3 = QtWidgets.QHBoxLayout()
        editMesh_layout3.addWidget(self.connect_button)
        editMesh_layout3.addWidget(self.detach_button)
        editMesh_layout3.addWidget(self.extrude_button)
        editMesh_layout3.setAlignment(QtCore.Qt.AlignTop)
        
        editMesh_layout4 = QtWidgets.QHBoxLayout()
        editMesh_layout4.addWidget(self.merge_button)
        editMesh_layout4.addWidget(self.mergeToCenter_button)
        editMesh_layout4.addWidget(self.transform_button)
        editMesh_layout4.setAlignment(QtCore.Qt.AlignTop)
    
        editMesh_layout5 = QtWidgets.QHBoxLayout()
        editMesh_layout5.addWidget(self.flip_button)
        editMesh_layout5.addWidget(self.symmetrize_button)
        editMesh_layout5.setAlignment(QtCore.Qt.AlignTop)
        
        editMesh_layout6 = QtWidgets.QHBoxLayout()
        editMesh_layout6.addWidget(self.averageVert_button)
        editMesh_layout6.addWidget(self.chamfer_button)
        editMesh_layout6.addWidget(self.reorderVert_button)
        editMesh_layout6.setAlignment(QtCore.Qt.AlignTop)
        
        editMesh_layout7 = QtWidgets.QHBoxLayout()
        editMesh_layout7.addWidget(self.delEdgeVert_button)
        editMesh_layout7.addWidget(self.edgeflow_button)
        editMesh_layout7.addWidget(self.flipEdge_button)
        editMesh_layout7.setAlignment(QtCore.Qt.AlignTop)
        
        editMesh_layout8 = QtWidgets.QHBoxLayout()
        editMesh_layout8.addWidget(self.spinEdgeBack_button)
        editMesh_layout8.addWidget(self.spinEdgeForw_button)
        editMesh_layout8.addWidget(self.invisibleFace_button)
        editMesh_layout8.setAlignment(QtCore.Qt.AlignTop)
        
        editMesh_layout9 = QtWidgets.QHBoxLayout()
        editMesh_layout9.addWidget(self.duplicate_button)
        editMesh_layout9.addWidget(self.extract_button)
        editMesh_layout9.addWidget(self.poke_button)
        editMesh_layout9.addWidget(self.wedge_button)
        editMesh_layout9.setAlignment(QtCore.Qt.AlignTop)
        
        editMesh_layout10 = QtWidgets.QHBoxLayout()
        editMesh_layout10.addWidget(self.projectCurve_button)
        editMesh_layout10.addWidget(self.splitMeshCurve_button)
        editMesh_layout10.setAlignment(QtCore.Qt.AlignTop)
        
        meshTools_layout1 = QtWidgets.QHBoxLayout()
        meshTools_layout1.addWidget(self.polyAppend_button)
        meshTools_layout1.addWidget(self.connect_button)
        meshTools_layout1.addWidget(self.polyCrease_button)
        meshTools_layout1.setAlignment(QtCore.Qt.AlignTop)
        
        meshTools_layout2 = QtWidgets.QHBoxLayout()
        meshTools_layout2.addWidget(self.createPoly_button)
        meshTools_layout2.addWidget(self.insertEdge_button)
        meshTools_layout2.addWidget(self.makeHole_button)
        meshTools_layout2.setAlignment(QtCore.Qt.AlignTop)
        
        meshTools_layout3 = QtWidgets.QHBoxLayout()
        meshTools_layout3.addWidget(self.multiCut_button)
        meshTools_layout3.addWidget(self.offsetEdge_button)
        meshTools_layout3.setAlignment(QtCore.Qt.AlignTop)
        
        meshTools_layout4 = QtWidgets.QHBoxLayout()
        meshTools_layout4.addWidget(self.quadDraw_button)
        meshTools_layout4.setAlignment(QtCore.Qt.AlignTop)
        
        meshTools_layout5 = QtWidgets.QHBoxLayout()
        meshTools_layout5.addWidget(self.slideEdge_button)
        meshTools_layout5.addWidget(self.targetWeld_button)
        meshTools_layout5.setAlignment(QtCore.Qt.AlignTop)
        
        empty_layout = QtWidgets.QHBoxLayout()
        empty_layout.addStretch()
        empty_layout.addStrut(2000)
        
        #self.setCentralWidget(scrollable_widget)
        main_layout = QtWidgets.QVBoxLayout(self)
        main_layout.setSpacing(0)
        main_layout.setContentsMargins(0, 0, 0, 0)
        #main_layout.se

        scrollable_widget = ScrollableWidget()
        main_layout.addWidget(scrollable_widget)

        scrollable_widget.add_widget(self.history_tools)
        self.history_tools.add_layout(history_layout1)     
        self.history_tools.add_layout(history_layout1)
        scrollable_widget.add_widget(self.polygon_primatives)
        self.polygon_primatives.add_layout(prim_layout1)
        self.polygon_primatives.add_widget(self.polygon_primativesSec)
        self.polygon_primativesSec.add_layout(prim_layout2)
        self.polygon_primativesSec.add_layout(prim_layout3)
        
        
        scrollable_widget.add_widget(self.sculpting_menu)
        self.sculpting_menu.add_layout(sculpt_layout1)
        self.sculpting_menu.add_widget(self.secSculpting_menu)
        self.secSculpting_menu.add_layout(sculpt_layout2)
        self.secSculpting_menu.add_layout(sculpt_layout3)
        self.secSculpting_menu.add_layout(sculpt_layout4)
        scrollable_widget.add_widget(self.mesh_menu)
        self.mesh_menu.add_layout(mesh_layout1)
        self.mesh_menu.add_layout(mesh_layout2)
        self.mesh_menu.add_layout(mesh_layout3)
        self.mesh_menu.add_layout(mesh_layout4)
        self.mesh_menu.add_layout(mesh_layout5)
        self.mesh_menu.add_layout(mesh_layout6)
        scrollable_widget.add_widget(self.editMesh_menu)
        self.editMesh_menu.add_layout(editMesh_layout1)
        self.editMesh_menu.add_layout(editMesh_layout3)
        self.editMesh_menu.add_layout(editMesh_layout4)
        self.editMesh_menu.add_layout(editMesh_layout5)
        self.editMesh_menu.add_layout(editMesh_layout6)
        self.editMesh_menu.add_layout(editMesh_layout7)
        self.editMesh_menu.add_widget(self.editMesh_menuSec)
        self.editMesh_menuSec.add_layout(editMesh_layout2)
        self.editMesh_menuSec.add_layout(editMesh_layout8)
        self.editMesh_menuSec.add_layout(editMesh_layout9)
        self.editMesh_menuSec.add_layout(editMesh_layout10)
        scrollable_widget.add_widget(self.meshTools_menu)
        self.meshTools_menu.add_layout(meshTools_layout1)   
        self.meshTools_menu.add_layout(meshTools_layout2)   
        self.meshTools_menu.add_layout(meshTools_layout3)    
        self.meshTools_menu.add_layout(meshTools_layout4)  
        self.meshTools_menu.add_layout(meshTools_layout5)  
        
        scroll_layout = QtWidgets.QVBoxLayout(self)
        scrollable_widget.add_layout(scroll_layout)
        scroll_layout.addStretch()
        
        #scrollable_widget.add_layout(empty_layout)
        
        #main_layout.add_layout(empty_layout )
        main_layout.setAlignment(QtCore.Qt.AlignTop)


    def create_connections(self):
        self.deleteHistory_button.clicked.connect(self.delete_history)
        self.deleteNonDefHistory_button.clicked.connect(self.delete_nonDifHistory)
        
        self.union_button.clicked.connect(self.perform_booleanUnion)
        self.difference_button.clicked.connect(self.perform_booleanDifference)
        self.intersection_button.clicked.connect(self.perform_booleanIntersection)
        self.combine_button.clicked.connect(self.perform_combine)
        self.seperate_button.clicked.connect(self.perform_seperate)
        self.conform_button.clicked.connect(self.perform_conform)
        self.fillHole_button.clicked.connect(self.perform_fillHole)
        self.reduce_button.clicked.connect(self.perform_reduce)
        self.remesh_button.clicked.connect(self.perform_remesh)
        self.retopo_button.clicked.connect(self.perform_retopo)
        self.smooth_button.clicked.connect(self.perform_smooth)
        self.triangulate_button.clicked.connect(self.perform_triangulate)
        self.quadrangulate_button.clicked.connect(self.perform_quadrangulate)
        self.mirror_button.clicked.connect(self.perform_mirror)
        
        self.lift_button.clicked.connect(self.set_meshSculptTool)
        self.sculptSmooth_button.clicked.connect(self.set_meshSmoothTool)
        self.sculptRelax_button.clicked.connect(self.set_meshRelaxTool)
        self.sculptGrab_button.clicked.connect(self.set_meshGrabTool)
        self.sculptPinch_button.clicked.connect(self.set_meshPinchTool)
        self.sculptFlatten_button.clicked.connect(self.set_meshFlattenTool)
        self.sculptObjects_button .clicked.connect(self.set_meshObjectTool)

    def create_workspace_control(self):
        self.workspace_control_instance = WorkspaceControl(self.get_workspace_control_name())
        if self.workspace_control_instance.exists():
            self.workspace_control_instance.restore(self)
        else:
            self.workspace_control_instance.create(self.WINDOW_TITLE, self, ui_script="from workspace_control import SampleUI\nSampleUI.display()")

    def show_workspace_control(self):
        self.workspace_control_instance.set_visible(True)

    def on_clicked(self):
        print("Button Clicked")
        
    def delete_history(self):    
        cmds.delete(constructionHistory = True)    
        
    def delete_history(self):    
        cmds.delete(constructionHistory = True)  
        
    def delete_nonDifHistory(self):   
        cmds.bakePartialHistory()
        
    def perform_booleanUnion(self):
        cmds.PolygonBooleanUnion()
        
    def perform_booleanDifference(self):
        cmds.PolygonBooleanDifference()
        
    def perform_booleanDifference(self):
        cmds.PolygonBooleanDifference()
        
    def perform_booleanIntersection(self):
        cmds.PolygonBooleanIntersection()
        
    def perform_combine(self):
        cmds.polyUnite()
        
    def perform_seperate(self):
        cmds.polySeparate()
        
    def perform_conform(self):
        cmds.ConformPolygon()
        
    def perform_fillHole(self):
        cmds.polyCloseBorder()
        
    def perform_reduce(self):
        cmds.polyReduce(ver=1,trm=0,shp=0, keepBorder=1, keepMapBorder=1,keepColorBorder=1,keepHardEdge=1, keepCreaseEdge=1, keepBorderWeight= 0.5,keepMapBorderWeight=0.5,keepColorBorderWeight=0.5,keepFaceGroupBorderWeight=0.5,keepHardEdgeWeight=0.5,keepCreaseEdgeWeight=0.5,useVirtualSymmetry=0,symmetryTolerance=0.01,sx=0,sy=1,sz=0,sw=0,preserveTopology=1,keepQuadsWeight=1,cachingReduce=1,ch=1,p=50,vct=0,tct=0,replaceOriginal=1)

    def perform_remesh(self):
        cmds.polyRemesh(maxEdgeLength=1,useRelativeValues=1,collapseThreshold=18,smoothStrength=0,tessellateBorders=1,interpolationType=2)
        
    def perform_retopo(self):
        cmds.polyRetopo(constructionHistory=1,replaceOriginal=1, preserveHardEdges=1, topologyRegularity=0.5, faceUniformity=0,anisotropy=1,targetFaceCount=1000,targetFaceCountTolerance=10)
    
    def perform_smooth(self):
        cmds.polySmooth()
        
    def perform_triangulate(self):
        cmds.polyTriangulate()
        
    def perform_quadrangulate(self):
        cmds.polyQuad()
        
    def perform_mirror(self):
        cmds.polyMirrorFace(cutMesh=1,axis=0,axisDirection=0,mergeMode=1,mergeThresholdType=0,mergeThreshold=0.001,mirrorAxis=2,mirrorPosition=0,smoothingAngle=30,flipUVs=0,ch=1)

    def set_meshSculptTool(self):
        cmds.SetMeshSculptTool()
        
    def set_meshSmoothTool(self):
        cmds.SetMeshSmoothTool()
        
    def set_meshRelaxTool(self):
        cmds.SetMeshRelaxTool()
        
    def set_meshGrabTool(self):
        cmds.SetMeshGrabTool()
        
    def set_meshPinchTool(self):
        cmds.SetMeshPinchTool()
        
    def set_meshFlattenTool(self):
        cmds.SetMeshFlattenTool()
        
    def set_meshObjectTool(self):
        cmds.OpenVisorForMeshes()
        
    def showEvent(self, e):
        if self.workspace_control_instance.is_floating():
            self.workspace_control_instance.set_label("Floating Window")
        else:
            self.workspace_control_instance.set_label("Modeling Helper")



if __name__ == "__main__":

    workspace_control_name = SampleUI.get_workspace_control_name()
    if cmds.window(workspace_control_name, exists=True):
        cmds.deleteUI(workspace_control_name)

    try:
        sample_ui.setParent(None)
        sample_ui.deleteLater()
    except:
        pass

    sample_ui = SampleUI()

