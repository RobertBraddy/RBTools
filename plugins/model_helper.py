import sys
from maya import OpenMayaUI
from PySide2 import QtCore
from PySide2 import QtGui
from PySide2 import QtWidgets
from shiboken2 import getCppPointer
from shiboken2 import wrapInstance
import maya.api.OpenMaya as om
import maya.OpenMayaUI as omui
import maya.cmds as cmds
import maya.mel as mel

def maya_useNewAPI():
    """
    The presence of this function tells Maya that the plugin produces, and
    expects to be passed, objects created using the Maya Python API 2.0.
    """
    pass
    
def initializePlugin(plugin):
    """
    Entry point for a plugin. It is called once -- immediately after the plugin is loaded.
    This function registers all of the commands, nodes, contexts, etc... associated with the plugin.

    It is required by all plugins.

    :param plugin: MObject used to register the plugin using an MFnPlugin function set
    """
    vendor = "Robert Braddy"
    version = "1.0.0"

    om.MFnPlugin(plugin, vendor, version)
    global sample_ui
    sample_ui = SampleUI()
    
def uninitializePlugin(plugin):
    """
    Exit point for a plugin. It is called once -- when the plugin is unloaded.
    This function de-registers everything that was registered in the initializePlugin function.

    It is required by all plugins.

    :param plugin: MObject used to de-register the plugin using an MFnPlugin function set
    """
    try:
        workspace_control_name = SampleUI.get_workspace_control_name()

        sample_ui.undock()
        if cmds.window(workspace_control_name, exists=True):
            cmds.deleteUI(workspace_control_name)  
        try:
            sample_ui.setParent(None)
            sample_ui.deleteLater()
        except:
            pass  
    except:
        pass

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
    
    def set_floating(self):
        print "undocking"
        cmds.workspaceControl(self.name, floating=True, edit=True)       

        
        
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
        self.vbox.setSpacing(3)
        # Add a button to the contents widget


        # Set the layout of the main widget
        main_layout = QtWidgets.QVBoxLayout(self)
        main_layout.addWidget(self.scroll_area)
        #main_layout.setSpacing(0)
        
    def add_widget(self, widget):
        self.vbox.addWidget(widget)
                
        widget.setContentsMargins(0, 0, 0, 0)

        #widget.setLayout(sub_layout)
        #scrollarea.setWidget(widget)
        
    def add_layout(self, layout):
        self.vbox.addLayout(layout)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(2)


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
        self.main_layout.setContentsMargins(4, 3, 2, 3)
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
    
    @classmethod    
    def undock(self):
        self.workspace_control_instance = WorkspaceControl(self.get_workspace_control_name())
        print "this"
        self.workspace_control_instance.set_floating()
            
    def create_workspace_control(self):
        self.workspace_control_instance = WorkspaceControl(self.get_workspace_control_name())
        if self.workspace_control_instance.exists():
            self.workspace_control_instance.restore(self)
        else:
            self.workspace_control_instance.create(self.WINDOW_TITLE, self, ui_script="from workspace_control import SampleUI\nSampleUI.display()")

    def show_workspace_control(self):
        self.workspace_control_instance.set_visible(True)
                        
    def __init__(self):
        super(SampleUI, self).__init__()

        self.setObjectName(self.__class__.UI_NAME)
        self.setMinimumSize(150, 100)
        self.widgets_history()
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
        self.widgets_prism()
        self.widgets_pyramid()
        self.widgets_soccer()
        self.widgets_superEllipse()
        self.widgets_sphericalHarm()
        self.widgets_ultraShape()
        self.widgets_collapsables()
        self.widgets_sculpting()
        self.widgets_divide()
        self.widgets_bevel()
        self.widgets_bridge()
        self.widgets_detach()  
        self.widgets_flip()  
        self.widgets_merge()
        self.widgets_mergeToCenter()
        self.widgets_extrude()
        self.widgets_edgeFlow()
        self.widgets_symmetrize()
        self.widgets_averageVert()
        self.widgets_chamfer()
        self.widgets_reorder()
        self.widgets_delEdge()
        self.widgets_flipEdge()
        self.widgets_transform()
        self.widgets_circularize()
        self.widgets_collapseEdge()
        self.widgets_curveSplit()
        self.widgets_duplicateFacet()
        self.widgets_extract()
        self.widgets_invisibleFace()   
        self.widgets_poke()
        self.widgets_projectCurve()
        self.widgets_wedge()
        self.widgets_spinEdgeForward()
        self.widgets_spinEdgeBackward()
        self.widgets_appendFacet()
        self.widgets_connect()
        self.widgets_crease()
        self.widgets_createPoly()
        self.widgets_insertEdge()
        self.widgets_makeHole()
        self.widgets_multiCut()
        self.widgets_offsetEdge()
        self.widgets_paintReduceWeights()
        self.widgets_paintTransferWeights()
        self.widgets_quadDraw()
        self.widgets_slideEdge()
        self.widgets_targetWeld()
        self.widgets_mirror()
        self.widgets_quadrangulate()
        self.widgets_triangulate()
        self.widgets_smooth()
        self.widgets_retopo()
        self.widgets_remesh()
        self.widgets_reduce()
        self.widgets_fillHole()
        self.widgets_conform()
        self.widgets_separate()
        self.widgets_combine()
        self.widgets_intersection()
        self.widgets_difference()
        self.widgets_union()
        self.widgets_centerPivot()
        self.widgets_bakePivot()
        self.widgets_zeroPivot()
        self.widgets_freezeTransform()
        self.widgets_resetTransform()
        self.widgets_duplicate()
        self.widgets_instance()
        self.widgets_replace()
        self.widgets_average()
        self.widgets_unlockNormals()
        self.widgets_reverse()
        self.widgets_lockNormals()
        self.widgets_setToFace()
        self.widgets_average()
        self.widgets_toggleReflectionSetModeOff()
        self.widgets_toggleReflectionSetModeOn()
        self.widgets_toggleCamBasedSelOff()
        self.widgets_toggleCamBasedSelOn()
        self.widgets_marquee()
        self.widgets_drag()
        self.widgets_preserveUVs()
        self.widgets_preserveChildren()
        self.widgets_tweakMode()
        self.widgets_edgeConstraint()
        self.create_layout()
        self.create_connections()
        self.create_workspace_control()
            
    def set_text(self, text):
        self.text_label.setText("<b>{0}</b>".format(text))
    
    def widgets_history(self):

        self.deleteHistory_button = QtWidgets.QPushButton("History")
        self.deleteHistory_button.setIcon(QtGui.QIcon(":deleteClip.png"))
        self.deleteHistory_button.setIconSize(QtCore.QSize(25, 15))
        self.deleteHistory_button.clicked.connect(self.delete_history)
        
        self.deleteNonDefHistory_button = QtWidgets.QPushButton("ND History")
        self.deleteNonDefHistory_button.setIcon(QtGui.QIcon(":deleteClip.png"))
        self.deleteNonDefHistory_button.setIconSize(QtCore.QSize(25, 15))
        self.deleteNonDefHistory_button.clicked.connect(self.delete_nonDifHistory)
        
    def perform_centerPivot(self):
        mel.eval("CenterPivot;")
        
    def widgets_centerPivot(self):
        self.centerPivot_button = QtWidgets.QPushButton("Center Piv")
        self.centerPivot_button.setIcon(QtGui.QIcon(":menuIconModify.png"))
        self.centerPivot_button.setIconSize(QtCore.QSize(25, 20))
        self.centerPivot_button.clicked.connect(self.perform_centerPivot)

        
    def perform_bakePivot(self):
        mel.eval("BakeCustomPivot;")
        
    def open_bakePivotOptions(self):
        mel.eval("BakeCustomPivotOptions;")
        
    def popup_bakePivot(self, position):
        bakePivot_popup = QtWidgets.QMenu()
        bakePivot_action = QtWidgets.QAction('Settings', self)
        bakePivot_action.triggered.connect(self.open_bakePivotOptions)
        bakePivot_popup.addAction(bakePivot_action)
        bakePivot_popup.exec_(self.bakePivot_button.mapToGlobal(position))

    def widgets_bakePivot(self):
        self.bakePivot_button = QtWidgets.QPushButton("Bake Piv")
        self.bakePivot_button.setIcon(QtGui.QIcon(":menuIconModify.png"))
        self.bakePivot_button.setIconSize(QtCore.QSize(25, 20))
        self.bakePivot_button.clicked.connect(self.perform_bakePivot)
        self.bakePivot_button.setContextMenuPolicy(QtCore.Qt.CustomContextMenu)
        self.bakePivot_button.customContextMenuRequested.connect(self.popup_bakePivot) 
        
    def perform_zeroPivot(self):
        node_list = cmds.ls( sl=True )
        if not node_list:
            cmds.error( 'Select one or more nodes to zero its transforms.' )

        for node in node_list:
            parent = None
            try:
                parent = cmds.listRelatives( node, p=True )[0]
            except:
                pass
                
            if parent:
                node = cmds.parent( node, w=True )[0]
                
            cmds.xform(node,piv=[0, 0, 0],ws=True,)
            cmds.makeIdentity(node,apply=True,t=True,r=True,s=True)

        cmds.select( node_list, r=True )

    def widgets_zeroPivot(self):
        self.zeroPivot_button = QtWidgets.QPushButton("Zero Piv")
        self.zeroPivot_button.setIcon(QtGui.QIcon(":menuIconModify.png"))
        self.zeroPivot_button.setIconSize(QtCore.QSize(25, 20))
        self.zeroPivot_button.clicked.connect(self.perform_zeroPivot)
        
    def perform_freezeTransform(self):
        mel.eval("FreezeTransformations;")
        
    def open_freezeTransformOptions(self):
        mel.eval("FreezeTransformationsOptions;")
        
    def popup_freezeTransform(self, position):
        freezeTransform_popup = QtWidgets.QMenu()
        freezeTransform_action = QtWidgets.QAction('Settings', self)
        freezeTransform_action.triggered.connect(self.open_freezeTransformOptions)
        freezeTransform_popup.addAction(freezeTransform_action)
        freezeTransform_popup.exec_(self.freezeTransform_button.mapToGlobal(position))

    def widgets_freezeTransform(self):
        
        self.freezeTransform_button = QtWidgets.QPushButton("Freeze Transform")
        self.freezeTransform_button.setIcon(QtGui.QIcon(":menuIconModify.png"))
        self.freezeTransform_button.setIconSize(QtCore.QSize(25, 20))
        self.freezeTransform_button.clicked.connect(self.perform_freezeTransform)
        self.freezeTransform_button.setContextMenuPolicy(QtCore.Qt.CustomContextMenu)
        self.freezeTransform_button.customContextMenuRequested.connect(self.popup_freezeTransform) 
        
    def perform_resetTransform(self):
        mel.eval("ResetTransformations;")
        
    def open_resetTransformOptions(self):
        mel.eval("ResetTransformationsOptions;")
        
    def popup_resetTransform(self, position):
        resetTransform_popup = QtWidgets.QMenu()
        resetTransform_action = QtWidgets.QAction('Settings', self)
        resetTransform_action.triggered.connect(self.open_resetTransformOptions)
        resetTransform_popup.addAction(resetTransform_action)
        resetTransform_popup.exec_(self.resetTransform_button.mapToGlobal(position))

    def widgets_resetTransform(self):
        self.resetTransform_button = QtWidgets.QPushButton("Reset Transform")
        self.resetTransform_button.setIcon(QtGui.QIcon(":menuIconModify.png"))
        self.resetTransform_button.setIconSize(QtCore.QSize(25, 20))
        self.resetTransform_button.clicked.connect(self.perform_resetTransform)
        self.resetTransform_button.setContextMenuPolicy(QtCore.Qt.CustomContextMenu)
        self.resetTransform_button.customContextMenuRequested.connect(self.popup_resetTransform) 

    def perform_duplicate(self):
        mel.eval("duplicatePreset(1,1,1,0,0,0,0,0,0,0,0,0,0,0,1,1,1);")
        
    def widgets_duplicate(self):
        self.duplicate_button = QtWidgets.QPushButton("Duplicate")
        #self.resetTransform_button.setIcon(QtGui.QIcon(":menuIconModify.png"))
        self.duplicate_button.setIconSize(QtCore.QSize(25, 20))
        self.duplicate_button.clicked.connect(self.perform_duplicate)
        
    def perform_instance(self):
        mel.eval("duplicatePreset(1,0,1,0,0,0,0,0,0,0,0,0,0,0,1,1,1);")
        
    def widgets_instance(self):
        self.instance_button = QtWidgets.QPushButton("Instance")
        #self.resetTransform_button.setIcon(QtGui.QIcon(":menuIconModify.png"))
        self.instance_button.setIconSize(QtCore.QSize(25, 20))
        self.instance_button.clicked.connect(self.perform_instance)
        
    def perform_replace(self):
        mel.eval("ReplaceObjects;")
        
    def open_replaceOptions(self):
        self.replace_button.setHidden(True)
        mel.eval("ReplaceObjectsOptions;")
        self.replace_button.setHidden(False)
        
    def popup_replace(self, position):
        replace_popup = QtWidgets.QMenu()
        replace_action = QtWidgets.QAction('Settings', self)
        replace_action.triggered.connect(self.open_replaceOptions)
        replace_popup.addAction(replace_action)
        replace_popup.exec_(self.replace_button.mapToGlobal(position))
        
    def widgets_replace(self):
        self.replace_button = QtWidgets.QPushButton("Replace")
        self.replace_button.setIconSize(QtCore.QSize(25, 25))
        self.replace_button.clicked.connect(self.perform_replace)
        self.replace_button.setContextMenuPolicy(QtCore.Qt.CustomContextMenu)
        self.replace_button.customContextMenuRequested.connect(self.popup_replace)

    def create_sphere(self):
        mel.eval("CreatePolygonSphere;")
        
    def open_sphereOptions(self):
        self.sphere_button.setHidden(True)
        mel.eval("CreatePolygonSphereOptions;")
        self.sphere_button.setHidden(False)
        
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
        #self.sphere_button.doubleClicked.connect(self.open_sphereOptions)
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
        
    def widgets_sphericalHarm(self):
        self.sphericalHarm_button = QtWidgets.QPushButton("")
        self.sphericalHarm_button.setIcon(QtGui.QIcon(":polySphericalHarmonics.png"))
        self.sphericalHarm_button.setIconSize(QtCore.QSize(25, 25))
        
    def widgets_ultraShape(self):
        self.ultraShape_button = QtWidgets.QPushButton("")
        self.ultraShape_button.setIcon(QtGui.QIcon(":polyUltraShape.png"))
        self.ultraShape_button.setIconSize(QtCore.QSize(25, 25))

    def create_connections_primatives(self):
        self.deleteHistory_button.clicked.connect(self.delete_history)
        self.deleteNonDefHistory_button.clicked.connect(self.delete_nonDifHistory)



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
        self.divide_button.setIconSize(QtCore.QSize(25, 20))
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
        self.bevel_button.setIconSize(QtCore.QSize(25, 20))
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
        self.bevel_button.setIconSize(QtCore.QSize(25, 20))
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
        self.bridge_button.setIconSize(QtCore.QSize(25, 20))
        self.bridge_button.clicked.connect(self.perform_bridge)
        self.bridge_button.setContextMenuPolicy(QtCore.Qt.CustomContextMenu)
        self.bridge_button.customContextMenuRequested.connect(self.popup_bridge) 
        
    def perform_detach(self):
        mel.eval("DetachComponent;")

    def widgets_detach(self):
        self.detach_button = QtWidgets.QPushButton("Detach")
        self.detach_button.setIcon(QtGui.QIcon(":polySplitVertex.png"))
        self.detach_button.setIconSize(QtCore.QSize(25, 20))
        self.detach_button.clicked.connect(self.perform_detach)
        
    def perform_extrude(self):
        mel.eval("PolyExtrude;")
        
    def open_extrudeOptions(self):
        mel.eval("PolyExtrudeOptions;")
        
    def popup_extrude(self, position):
        extrude_popup = QtWidgets.QMenu()
        extrude_action = QtWidgets.QAction('Settings', self)
        extrude_action.triggered.connect(self.open_extrudeOptions)
        extrude_popup.addAction(extrude_action)
        extrude_popup.exec_(self.extrude_button.mapToGlobal(position))

    def widgets_extrude(self):
        self.extrude_button = QtWidgets.QPushButton("extrude")
        self.extrude_button.setIcon(QtGui.QIcon(":polyExtrudeFacet.png"))
        self.extrude_button.setIconSize(QtCore.QSize(25, 20))
        self.extrude_button.clicked.connect(self.perform_extrude)
        self.extrude_button.setContextMenuPolicy(QtCore.Qt.CustomContextMenu)
        self.extrude_button.customContextMenuRequested.connect(self.popup_extrude) 
        
    def perform_merge(self):
        mel.eval("PolyMerge")
        
    def open_mergeOptions(self):
        mel.eval("PolyMergeOptions;")
        
    def popup_merge(self, position):
        merge_popup = QtWidgets.QMenu()
        merge_action = QtWidgets.QAction('Settings', self)
        merge_action.triggered.connect(self.open_mergeOptions)
        merge_popup.addAction(merge_action)
        merge_popup.exec_(self.merge_button.mapToGlobal(position))

    def widgets_merge(self):
        self.merge_button = QtWidgets.QPushButton("Merge")
        self.merge_button.setIcon(QtGui.QIcon(":polyMerge.png"))
        self.merge_button.setIconSize(QtCore.QSize(25, 20))
        self.merge_button.clicked.connect(self.perform_merge)
        self.merge_button.setContextMenuPolicy(QtCore.Qt.CustomContextMenu)
        self.merge_button.customContextMenuRequested.connect(self.popup_merge) 
        
    def perform_mergeToCenter(self):
        mel.eval("MergeToCenter")

    def widgets_mergeToCenter(self):
        self.mergeToCenter_button = QtWidgets.QPushButton("Merge2Center")
        self.mergeToCenter_button.setIcon(QtGui.QIcon(":polyMergeToCenter.png"))
        self.mergeToCenter_button.setIconSize(QtCore.QSize(25, 20))
        self.mergeToCenter_button.clicked.connect(self.perform_mergeToCenter)

    def perform_transform(self):
        mel.eval("MovePolygonComponent;")
        
    def open_transformOptions(self):
        mel.eval("MovePolygonComponentOptions;")
        
    def popup_transform(self, position):
        transform_popup = QtWidgets.QMenu()
        transform_action = QtWidgets.QAction('Settings', self)
        transform_action.triggered.connect(self.open_transformOptions)
        transform_popup.addAction(transform_action)
        transform_popup.exec_(self.transform_button.mapToGlobal(position))

    def widgets_transform(self):
        self.transform_button = QtWidgets.QPushButton("transform")
        self.transform_button.setIcon(QtGui.QIcon(":polyMoveVertex.png"))
        self.transform_button.setIconSize(QtCore.QSize(25, 20))
        self.transform_button.clicked.connect(self.perform_transform)
        self.transform_button.setContextMenuPolicy(QtCore.Qt.CustomContextMenu)
        self.transform_button.customContextMenuRequested.connect(self.popup_transform) 
        
    def perform_flip(self):
        mel.eval("FlipMesh;")

    def widgets_flip(self):
        self.flip_button = QtWidgets.QPushButton("flip")
        self.flip_button.setIcon(QtGui.QIcon(":polyFlip.png"))
        self.flip_button.setIconSize(QtCore.QSize(25, 20))
        self.flip_button.clicked.connect(self.perform_flip)
        
    def perform_symmetrize(self):
        mel.eval("Symmetrize")

    def widgets_symmetrize(self):
        self.symmetrize_button = QtWidgets.QPushButton("symmetrize")
        self.symmetrize_button.setIcon(QtGui.QIcon(":symmetrize.png"))
        self.symmetrize_button.setIconSize(QtCore.QSize(25, 20))
        self.symmetrize_button.clicked.connect(self.perform_symmetrize)
        
    def perform_averageVert(self):
        mel.eval("AverageVertex;")
        
    def open_averageVertOptions(self):
        mel.eval("AverageVertexOptions;")
        
    def popup_averageVert(self, position):
        averageVert_popup = QtWidgets.QMenu()
        averageVert_action = QtWidgets.QAction('Settings', self)
        averageVert_action.triggered.connect(self.open_averageVertOptions)
        averageVert_popup.addAction(averageVert_action)
        averageVert_popup.exec_(self.averageVert_button.mapToGlobal(position))

    def widgets_averageVert(self):
        self.averageVert_button = QtWidgets.QPushButton("Average")
        self.averageVert_button.setIcon(QtGui.QIcon(":polyAverageVertex.png"))
        self.averageVert_button.setIconSize(QtCore.QSize(25, 20))
        self.averageVert_button.clicked.connect(self.perform_averageVert)
        self.averageVert_button.setContextMenuPolicy(QtCore.Qt.CustomContextMenu)
        self.averageVert_button.customContextMenuRequested.connect(self.popup_averageVert) 
        
    def perform_chamfer(self):
        mel.eval("ChamferVertex;")
        
    def open_chamferOptions(self):
        mel.eval("ChamferVertexOptions;")
        
    def popup_chamfer(self, position):
        chamfer_popup = QtWidgets.QMenu()
        chamfer_action = QtWidgets.QAction('Settings', self)
        chamfer_action.triggered.connect(self.open_chamferOptions)
        chamfer_popup.addAction(chamfer_action)
        chamfer_popup.exec_(self.chamfer_button.mapToGlobal(position))

    def widgets_chamfer(self):
        self.chamfer_button = QtWidgets.QPushButton("Chamfer")
        self.chamfer_button.setIcon(QtGui.QIcon(":polyChamfer.png"))
        self.chamfer_button.setIconSize(QtCore.QSize(25, 20))
        self.chamfer_button.clicked.connect(self.perform_chamfer)
        self.chamfer_button.setContextMenuPolicy(QtCore.Qt.CustomContextMenu)
        self.chamfer_button.customContextMenuRequested.connect(self.popup_chamfer) 
        
    def perform_reorder(self):
        mel.eval("ReorderVertex;")

    def widgets_reorder(self):
        self.reorder_button = QtWidgets.QPushButton("Reorder")
        self.reorder_button.setIcon(QtGui.QIcon(":reorderIDs.png"))
        self.reorder_button.setIconSize(QtCore.QSize(25, 20))
        self.reorder_button.clicked.connect(self.perform_reorder)
        
    def perform_delEdge(self):
        mel.eval("DeletePolyElements;")

    def widgets_delEdge(self):
        self.delEdge_button = QtWidgets.QPushButton("Delete Edge")
        self.delEdge_button.setIcon(QtGui.QIcon(":polyDelEdgeVertex.png"))
        self.delEdge_button.setIconSize(QtCore.QSize(25, 20))
        self.delEdge_button.clicked.connect(self.perform_delEdge)
        
    def perform_edgeFlow(self):
        mel.eval("PolyEditEdgeFlow;")
        
    def open_edgeFlowOptions(self):
        mel.eval("PolyEditEdgeFlowOptions;")
        
    def popup_edgeFlow(self, position):
        edgeFlow_popup = QtWidgets.QMenu()
        edgeFlow_action = QtWidgets.QAction('Settings', self)
        edgeFlow_action.triggered.connect(self.open_edgeFlowOptions)
        edgeFlow_popup.addAction(edgeFlow_action)
        edgeFlow_popup.exec_(self.edgeFlow_button.mapToGlobal(position))

    def widgets_edgeFlow(self):
        self.edgeFlow_button = QtWidgets.QPushButton("Edge Flow")
        self.edgeFlow_button.setIcon(QtGui.QIcon(":polyEditEdgeFlow.png"))
        self.edgeFlow_button.setIconSize(QtCore.QSize(25, 20))
        self.edgeFlow_button.clicked.connect(self.perform_edgeFlow)
        self.edgeFlow_button.setContextMenuPolicy(QtCore.Qt.CustomContextMenu)
        self.edgeFlow_button.customContextMenuRequested.connect(self.popup_edgeFlow) 
        
    def perform_flipEdge(self):
        mel.eval("FlipTriangleEdge;")
        
    def widgets_flipEdge(self):
        self.flipEdge_button = QtWidgets.QPushButton("Flip Edge")
        self.flipEdge_button.setIcon(QtGui.QIcon(":polyFlipEdge.png"))
        self.flipEdge_button.setIconSize(QtCore.QSize(25, 20))
        self.flipEdge_button.clicked.connect(self.perform_flipEdge)
        
    def perform_circularize(self):
        mel.eval("PolyCircularize;")
        
    def open_circularizeOptions(self):
        mel.eval("PolyCircularizeOptions;")
        
    def popup_circularize(self, position):
        circularize_popup = QtWidgets.QMenu()
        circularize_action = QtWidgets.QAction('Settings', self)
        circularize_action.triggered.connect(self.open_circularizeOptions)
        circularize_popup.addAction(circularize_action)
        circularize_popup.exec_(self.circularize_button.mapToGlobal(position))

    def widgets_circularize(self):
        self.circularize_button = QtWidgets.QPushButton("Circularize")
        self.circularize_button.setIcon(QtGui.QIcon(":polyCircularize.png"))
        self.circularize_button.setIconSize(QtCore.QSize(25, 20))
        self.circularize_button.clicked.connect(self.perform_circularize)
        self.circularize_button.setContextMenuPolicy(QtCore.Qt.CustomContextMenu)
        self.circularize_button.customContextMenuRequested.connect(self.popup_circularize) 
        
    def perform_collapseEdge(self):
        mel.eval("performPolyCollapse 0;")

    def widgets_collapseEdge(self):
        self.collapseEdge_button = QtWidgets.QPushButton("Collapse")
        self.collapseEdge_button.setIcon(QtGui.QIcon(":polyCollapseEdge.png"))
        self.collapseEdge_button.setIconSize(QtCore.QSize(25, 20))
        self.collapseEdge_button.clicked.connect(self.perform_collapseEdge)

    def perform_spinEdgeBackward(self):
        mel.eval("PolySpinEdgeBackward;")

    def widgets_spinEdgeBackward(self):
        self.spinEdgeBackward_button = QtWidgets.QPushButton("Collapse")
        self.spinEdgeBackward_button.setIcon(QtGui.QIcon(":polySpinEdgeBackward.png"))
        self.spinEdgeBackward_button.setIconSize(QtCore.QSize(25, 20))
        self.spinEdgeBackward_button.clicked.connect(self.perform_spinEdgeBackward)
        
    def perform_spinEdgeForward(self):
        mel.eval("PolySpinEdgeForward;")

    def widgets_spinEdgeForward(self):
        self.spinEdgeForward_button = QtWidgets.QPushButton("Collapse")
        self.spinEdgeForward_button.setIcon(QtGui.QIcon(":polySpinEdgeForward.png"))
        self.spinEdgeForward_button.setIconSize(QtCore.QSize(25, 20))
        self.spinEdgeForward_button.clicked.connect(self.perform_spinEdgeForward)
        
    def perform_invisibleFace(self):
        mel.eval("PolyAssignSubdivHole;")
        
    def open_invisibleFaceOptions(self):
        mel.eval("PolyAssignSubdivHoleOptions;")
        
    def popup_invisibleFace(self, position):
        invisibleFace_popup = QtWidgets.QMenu()
        invisibleFace_action = QtWidgets.QAction('Settings', self)
        invisibleFace_action.triggered.connect(self.open_invisibleFaceOptions)
        invisibleFace_popup.addAction(invisibleFace_action)
        invisibleFace_popup.exec_(self.invisibleFace_button.mapToGlobal(position))

    def widgets_invisibleFace(self):
        self.invisibleFace_button = QtWidgets.QPushButton("Invisible Face")
        self.invisibleFace_button.setIcon(QtGui.QIcon(":polyAssignSubdivHole.png"))
        self.invisibleFace_button.setIconSize(QtCore.QSize(25, 20))
        self.invisibleFace_button.clicked.connect(self.perform_invisibleFace)
        self.invisibleFace_button.setContextMenuPolicy(QtCore.Qt.CustomContextMenu)
        self.invisibleFace_button.customContextMenuRequested.connect(self.popup_invisibleFace) 

    def perform_duplicateFacet(self):
        mel.eval("performPolyChipOff 0 1;")
        
    def open_duplicateFacetOptions(self):
        mel.eval("DuplicateFaceOptions;")
        
    def popup_duplicateFacet(self, position):
        duplicateFacet_popup = QtWidgets.QMenu()
        duplicateFacet_action = QtWidgets.QAction('Settings', self)
        duplicateFacet_action.triggered.connect(self.open_duplicateFacetOptions)
        duplicateFacet_popup.addAction(duplicateFacet_action)
        duplicateFacet_popup.exec_(self.duplicateFacet_button.mapToGlobal(position))

    def widgets_duplicateFacet(self):
        self.duplicateFacet_button = QtWidgets.QPushButton("Duplicate")
        self.duplicateFacet_button.setIcon(QtGui.QIcon(":polyDuplicateFacet.png"))
        self.duplicateFacet_button.setIconSize(QtCore.QSize(25, 20))
        self.duplicateFacet_button.clicked.connect(self.perform_duplicateFacet)
        self.duplicateFacet_button.setContextMenuPolicy(QtCore.Qt.CustomContextMenu)
        self.duplicateFacet_button.customContextMenuRequested.connect(self.popup_duplicateFacet) 
        
    def perform_extract(self):
        mel.eval("performPolyChipOff 0 0")
        
    def open_extractOptions(self):
        mel.eval("ExtractFaceOptions;")
        
    def popup_extract(self, position):
        extract_popup = QtWidgets.QMenu()
        extract_action = QtWidgets.QAction('Settings', self)
        extract_action.triggered.connect(self.open_extractOptions)
        extract_popup.addAction(extract_action)
        extract_popup.exec_(self.extract_button.mapToGlobal(position))

    def widgets_extract(self):
        self.extract_button = QtWidgets.QPushButton("extract")
        self.extract_button.setIcon(QtGui.QIcon(":polyChipOff.png"))
        self.extract_button.setIconSize(QtCore.QSize(25, 20))
        self.extract_button.clicked.connect(self.perform_extract)
        self.extract_button.setContextMenuPolicy(QtCore.Qt.CustomContextMenu)
        self.extract_button.customContextMenuRequested.connect(self.popup_extract) 
        
    def perform_poke(self):
        mel.eval("PokePolygon")
        
    def open_pokeOptions(self):
        mel.eval("PokePolygonOptions;")
        
    def popup_poke(self, position):
        poke_popup = QtWidgets.QMenu()
        poke_action = QtWidgets.QAction('Settings', self)
        poke_action.triggered.connect(self.open_pokeOptions)
        poke_popup.addAction(poke_action)
        poke_popup.exec_(self.poke_button.mapToGlobal(position))

    def widgets_poke(self):
        self.poke_button = QtWidgets.QPushButton("poke")
        self.poke_button.setIcon(QtGui.QIcon(":polyPoke.png"))
        self.poke_button.setIconSize(QtCore.QSize(25, 20))
        self.poke_button.clicked.connect(self.perform_poke)
        self.poke_button.setContextMenuPolicy(QtCore.Qt.CustomContextMenu)
        self.poke_button.customContextMenuRequested.connect(self.popup_poke) 
        
    def perform_wedge(self):
        mel.eval("WedgePolygon;")
        
    def open_wedgeOptions(self):
        mel.eval("WedgePolygonOptions;")
        
    def popup_wedge(self, position):
        wedge_popup = QtWidgets.QMenu()
        wedge_action = QtWidgets.QAction('Settings', self)
        wedge_action.triggered.connect(self.open_wedgeOptions)
        wedge_popup.addAction(wedge_action)
        wedge_popup.exec_(self.wedge_button.mapToGlobal(position))

    def widgets_wedge(self):
        self.wedge_button = QtWidgets.QPushButton("Wedge")
        self.wedge_button.setIcon(QtGui.QIcon(":polyWedgeFace.png"))
        self.wedge_button.setIconSize(QtCore.QSize(25, 20))
        self.wedge_button.clicked.connect(self.perform_wedge)
        self.wedge_button.setContextMenuPolicy(QtCore.Qt.CustomContextMenu)
        self.wedge_button.customContextMenuRequested.connect(self.popup_wedge) 
        
    def perform_projectCurve(self):
        mel.eval("ProjectCurveOnMesh;")
        
    def open_projectCurveOptions(self):
        mel.eval("ProjectCurveOnMeshOptions;")
        
    def popup_projectCurve(self, position):
        projectCurve_popup = QtWidgets.QMenu()
        projectCurve_action = QtWidgets.QAction('Settings', self)
        projectCurve_action.triggered.connect(self.open_projectCurveOptions)
        projectCurve_popup.addAction(projectCurve_action)
        projectCurve_popup.exec_(self.projectCurve_button.mapToGlobal(position))

    def widgets_projectCurve(self):
        self.projectCurve_button = QtWidgets.QPushButton("Project Curve")
        self.projectCurve_button.setIcon(QtGui.QIcon(":projectCurve_Poly.png"))
        self.projectCurve_button.setIconSize(QtCore.QSize(25, 20))
        self.projectCurve_button.clicked.connect(self.perform_projectCurve)
        self.projectCurve_button.setContextMenuPolicy(QtCore.Qt.CustomContextMenu)
        self.projectCurve_button.customContextMenuRequested.connect(self.popup_projectCurve) 
        
    def perform_curveSplit(self):
        mel.eval("SplitMeshWithProjectedCurve")
        
    def open_curveSplitOptions(self):
        mel.eval("SplitMeshWithProjectedCurveOptions;")
        
    def popup_curveSplit(self, position):
        curveSplit_popup = QtWidgets.QMenu()
        curveSplit_action = QtWidgets.QAction('Settings', self)
        curveSplit_action.triggered.connect(self.open_curveSplitOptions)
        curveSplit_popup.addAction(curveSplit_action)
        curveSplit_popup.exec_(self.curveSplit_button.mapToGlobal(position))

    def widgets_curveSplit(self):
        self.curveSplit_button = QtWidgets.QPushButton("curveSplit")
        self.curveSplit_button.setIcon(QtGui.QIcon(":projectCurveSplit_Poly.png"))
        self.curveSplit_button.setIconSize(QtCore.QSize(25, 20))
        self.curveSplit_button.clicked.connect(self.perform_curveSplit)
        self.curveSplit_button.setContextMenuPolicy(QtCore.Qt.CustomContextMenu)
        self.curveSplit_button.customContextMenuRequested.connect(self.popup_curveSplit) 
        
    def perform_appendFacet(self):
        mel.eval("setToolTo polyAppendFacetContext ; polyAppendFacetCtx -e -pc `optionVar -q polyKeepFacetsPlanar` polyAppendFacetContext;")
        
    def open_appendFacetOptions(self):
        mel.eval("setToolTo polyAppendFacetContext ; polyAppendFacetCtx -e -pc `optionVar -q polyKeepFacetsPlanar` polyAppendFacetContext; toolPropertyWindow;")
        
    def popup_appendFacet(self, position):
        appendFacet_popup = QtWidgets.QMenu()
        appendFacet_action = QtWidgets.QAction('Settings', self)
        appendFacet_action.triggered.connect(self.open_appendFacetOptions)
        appendFacet_popup.addAction(appendFacet_action)
        appendFacet_popup.exec_(self.appendFacet_button.mapToGlobal(position))

    def widgets_appendFacet(self):
        self.appendFacet_button = QtWidgets.QPushButton("Append")
        self.appendFacet_button.setIcon(QtGui.QIcon(":polyAppendFacet.png"))
        self.appendFacet_button.setIconSize(QtCore.QSize(25, 20))
        self.appendFacet_button.clicked.connect(self.perform_appendFacet)
        self.appendFacet_button.setContextMenuPolicy(QtCore.Qt.CustomContextMenu)
        self.appendFacet_button.customContextMenuRequested.connect(self.popup_appendFacet) 
        
    def perform_connect(self):
        mel.eval("EnterConnectTool;")
        
    def open_connectOptions(self):
        mel.eval("dR_connectTool; toolPropertyWindow;")
        
    def popup_connect(self, position):
        connect_popup = QtWidgets.QMenu()
        connect_action = QtWidgets.QAction('Settings', self)
        connect_action.triggered.connect(self.open_connectOptions)
        connect_popup.addAction(connect_action)
        connect_popup.exec_(self.connect_button.mapToGlobal(position))

    def widgets_connect(self):
        self.connect_button = QtWidgets.QPushButton("connect")
        self.connect_button.setIcon(QtGui.QIcon(":connect_NEX32.png"))
        self.connect_button.setIconSize(QtCore.QSize(25, 20))
        self.connect_button.clicked.connect(self.perform_connect)
        self.connect_button.setContextMenuPolicy(QtCore.Qt.CustomContextMenu)
        self.connect_button.customContextMenuRequested.connect(self.popup_connect) 
        
    def perform_crease(self):
        mel.eval("PolyCreaseTool;")
        
    def open_creaseOptions(self):
        mel.eval("PolyCreaseToolOptions;")
        
    def popup_crease(self, position):
        crease_popup = QtWidgets.QMenu()
        crease_action = QtWidgets.QAction('Settings', self)
        crease_action.triggered.connect(self.open_creaseOptions)
        crease_popup.addAction(crease_action)
        crease_popup.exec_(self.crease_button.mapToGlobal(position))

    def widgets_crease(self):
        self.crease_button = QtWidgets.QPushButton("crease")
        self.crease_button.setIcon(QtGui.QIcon(":polyCrease.png"))
        self.crease_button.setIconSize(QtCore.QSize(25, 20))
        self.crease_button.clicked.connect(self.perform_crease)
        self.crease_button.setContextMenuPolicy(QtCore.Qt.CustomContextMenu)
        self.crease_button.customContextMenuRequested.connect(self.popup_crease) 
        
    def perform_createPoly(self):
        mel.eval("setToolTo polyCreateFacetContext ; polyCreateFacetCtx -e -pc `optionVar -q polyKeepFacetsPlanar` polyCreateFacetContext;")
        
    def open_createPolyOptions(self):
        mel.eval("setToolTo polyCreateFacetContext ; polyCreateFacetCtx -e -pc `optionVar -q polyKeepFacetsPlanar` polyCreateFacetContext; toolPropertyWindow;")
        
    def popup_createPoly(self, position):
        createPoly_popup = QtWidgets.QMenu()
        createPoly_action = QtWidgets.QAction('Settings', self)
        createPoly_action.triggered.connect(self.open_createPolyOptions)
        createPoly_popup.addAction(createPoly_action)
        createPoly_popup.exec_(self.createPoly_button.mapToGlobal(position))

    def widgets_createPoly(self):
        self.createPoly_button = QtWidgets.QPushButton("createPoly")
        self.createPoly_button.setIcon(QtGui.QIcon(":polyCreateFacet.png"))
        self.createPoly_button.setIconSize(QtCore.QSize(25, 20))
        self.createPoly_button.clicked.connect(self.perform_createPoly)
        self.createPoly_button.setContextMenuPolicy(QtCore.Qt.CustomContextMenu)
        self.createPoly_button.customContextMenuRequested.connect(self.popup_createPoly) 
        
    def perform_insertEdge(self):
        mel.eval("SplitEdgeRingTool;")
        
    def open_insertEdgeOptions(self):
        mel.eval("InsertEdgeLoopToolOptions;")
        
    def popup_insertEdge(self, position):
        insertEdge_popup = QtWidgets.QMenu()
        insertEdge_action = QtWidgets.QAction('Settings', self)
        insertEdge_action.triggered.connect(self.open_insertEdgeOptions)
        insertEdge_popup.addAction(insertEdge_action)
        insertEdge_popup.exec_(self.insertEdge_button.mapToGlobal(position))

    def widgets_insertEdge(self):
        self.insertEdge_button = QtWidgets.QPushButton("insertEdge")
        self.insertEdge_button.setIcon(QtGui.QIcon(":polySplitEdgeRing.png"))
        self.insertEdge_button.setIconSize(QtCore.QSize(25, 20))
        self.insertEdge_button.clicked.connect(self.perform_insertEdge)
        self.insertEdge_button.setContextMenuPolicy(QtCore.Qt.CustomContextMenu)
        self.insertEdge_button.customContextMenuRequested.connect(self.popup_insertEdge) 
        
    def perform_makeHole(self):
        mel.eval("MakeHoleTool;")
        
    def open_makeHoleOptions(self):
        mel.eval("MakeHoleToolOptions")
        
    def popup_makeHole(self, position):
        makeHole_popup = QtWidgets.QMenu()
        makeHole_action = QtWidgets.QAction('Settings', self)
        makeHole_action.triggered.connect(self.open_makeHoleOptions)
        makeHole_popup.addAction(makeHole_action)
        makeHole_popup.exec_(self.makeHole_button.mapToGlobal(position))

    def widgets_makeHole(self):
        self.makeHole_button = QtWidgets.QPushButton("Make Hole")
        self.makeHole_button.setIcon(QtGui.QIcon(":polyMergeFacet.png"))
        self.makeHole_button.setIconSize(QtCore.QSize(25, 20))
        self.makeHole_button.clicked.connect(self.perform_makeHole)
        self.makeHole_button.setContextMenuPolicy(QtCore.Qt.CustomContextMenu)
        self.makeHole_button.customContextMenuRequested.connect(self.popup_makeHole) 
        
    def perform_multiCut(self):
        mel.eval("MultiCutTool;")
        
    def open_multiCutOptions(self):
        mel.eval("dR_multiCutTool; toolPropertyWindow;")
        
    def popup_multiCut(self, position):
        multiCut_popup = QtWidgets.QMenu()
        multiCut_action = QtWidgets.QAction('Settings', self)
        multiCut_action.triggered.connect(self.open_multiCutOptions)
        multiCut_popup.addAction(multiCut_action)
        multiCut_popup.exec_(self.multiCut_button.mapToGlobal(position))

    def widgets_multiCut(self):
        self.multiCut_button = QtWidgets.QPushButton("multiCut")
        self.multiCut_button.setIcon(QtGui.QIcon(":multiCut_NEX32.png"))
        self.multiCut_button.setIconSize(QtCore.QSize(25, 20))
        self.multiCut_button.clicked.connect(self.perform_multiCut)
        self.multiCut_button.setContextMenuPolicy(QtCore.Qt.CustomContextMenu)
        self.multiCut_button.customContextMenuRequested.connect(self.popup_multiCut) 
        
    def perform_offsetEdge(self):
        mel.eval("performPolyDuplicateEdge 0;")
        
    def open_offsetEdgeOptions(self):
        mel.eval("DuplicateEdgesOptions;")
        
    def popup_offsetEdge(self, position):
        offsetEdge_popup = QtWidgets.QMenu()
        offsetEdge_action = QtWidgets.QAction('Settings', self)
        offsetEdge_action.triggered.connect(self.open_offsetEdgeOptions)
        offsetEdge_popup.addAction(offsetEdge_action)
        offsetEdge_popup.exec_(self.offsetEdge_button.mapToGlobal(position))

    def widgets_offsetEdge(self):
        self.offsetEdge_button = QtWidgets.QPushButton("offsetEdge")
        self.offsetEdge_button.setIcon(QtGui.QIcon(":polyDuplicateEdgeLoop.png"))
        self.offsetEdge_button.setIconSize(QtCore.QSize(25, 20))
        self.offsetEdge_button.clicked.connect(self.perform_offsetEdge)
        self.offsetEdge_button.setContextMenuPolicy(QtCore.Qt.CustomContextMenu)
        self.offsetEdge_button.customContextMenuRequested.connect(self.popup_offsetEdge) 
        
    def perform_paintReduceWeights(self):
        mel.eval("PaintReduceWeightsTool;")
        
    def open_paintReduceWeightsOptions(self):
        mel.eval("PaintReduceWeightsToolOptions;")
        
    def popup_paintReduceWeights(self, position):
        paintReduceWeights_popup = QtWidgets.QMenu()
        paintReduceWeights_action = QtWidgets.QAction('Settings', self)
        paintReduceWeights_action.triggered.connect(self.open_paintReduceWeightsOptions)
        paintReduceWeights_popup.addAction(paintReduceWeights_action)
        paintReduceWeights_popup.exec_(self.paintReduceWeights_button.mapToGlobal(position))

    def widgets_paintReduceWeights(self):
        self.paintReduceWeights_button = QtWidgets.QPushButton("paintReduceWeights")
        self.paintReduceWeights_button.setIcon(QtGui.QIcon(":polyPaintReduceWeights.png"))
        self.paintReduceWeights_button.setIconSize(QtCore.QSize(25, 20))
        self.paintReduceWeights_button.clicked.connect(self.perform_paintReduceWeights)
        self.paintReduceWeights_button.setContextMenuPolicy(QtCore.Qt.CustomContextMenu)
        self.paintReduceWeights_button.customContextMenuRequested.connect(self.popup_paintReduceWeights) 
        
    def perform_paintTransferWeights(self):
        mel.eval("PaintTransferAttributes;")
        
    def open_paintTransferWeightsOptions(self):
        mel.eval("PaintTransferAttributesOptions;")
        
    def popup_paintTransferWeights(self, position):
        paintTransferWeights_popup = QtWidgets.QMenu()
        paintTransferWeights_action = QtWidgets.QAction('Settings', self)
        paintTransferWeights_action.triggered.connect(self.open_paintTransferWeightsOptions)
        paintTransferWeights_popup.addAction(paintTransferWeights_action)
        paintTransferWeights_popup.exec_(self.paintTransferWeights_button.mapToGlobal(position))

    def widgets_paintTransferWeights(self):
        self.paintTransferWeights_button = QtWidgets.QPushButton("Transfer Weights")
        self.paintTransferWeights_button.setIcon(QtGui.QIcon(":polyTransferAttributesWeights.png"))
        self.paintTransferWeights_button.setIconSize(QtCore.QSize(25, 20))
        self.paintTransferWeights_button.clicked.connect(self.perform_paintTransferWeights)
        self.paintTransferWeights_button.setContextMenuPolicy(QtCore.Qt.CustomContextMenu)
        self.paintTransferWeights_button.customContextMenuRequested.connect(self.popup_paintTransferWeights) 
        
    def perform_quadDraw(self):
        mel.eval("QuadDrawTool;")
        
    def open_quadDrawOptions(self):
        mel.eval("dR_quadDrawTool; toolPropertyWindow;")
        
    def popup_quadDraw(self, position):
        quadDraw_popup = QtWidgets.QMenu()
        quadDraw_action = QtWidgets.QAction('Settings', self)
        quadDraw_action.triggered.connect(self.open_quadDrawOptions)
        quadDraw_popup.addAction(quadDraw_action)
        quadDraw_popup.exec_(self.quadDraw_button.mapToGlobal(position))

    def widgets_quadDraw(self):
        self.quadDraw_button = QtWidgets.QPushButton("Quad Draw")
        self.quadDraw_button.setIcon(QtGui.QIcon(":quadDraw_NEX32.png"))
        self.quadDraw_button.setIconSize(QtCore.QSize(25, 20))
        self.quadDraw_button.clicked.connect(self.perform_quadDraw)
        self.quadDraw_button.setContextMenuPolicy(QtCore.Qt.CustomContextMenu)
        self.quadDraw_button.customContextMenuRequested.connect(self.popup_quadDraw) 
        
    def perform_slideEdge(self):
        mel.eval("SlideEdgeTool;")
        
    def open_slideEdgeOptions(self):
        mel.eval("SlideEdgeToolOptions;")
        
    def popup_slideEdge(self, position):
        slideEdge_popup = QtWidgets.QMenu()
        slideEdge_action = QtWidgets.QAction('Settings', self)
        slideEdge_action.triggered.connect(self.open_slideEdgeOptions)
        slideEdge_popup.addAction(slideEdge_action)
        slideEdge_popup.exec_(self.slideEdge_button.mapToGlobal(position))

    def widgets_slideEdge(self):
        self.slideEdge_button = QtWidgets.QPushButton("Slide Edge")
        self.slideEdge_button.setIcon(QtGui.QIcon(":slideEdgeTool.png"))
        self.slideEdge_button.setIconSize(QtCore.QSize(25, 20))
        self.slideEdge_button.clicked.connect(self.perform_slideEdge)
        self.slideEdge_button.setContextMenuPolicy(QtCore.Qt.CustomContextMenu)
        self.slideEdge_button.customContextMenuRequested.connect(self.popup_slideEdge) 
        
    def perform_targetWeld(self):
        mel.eval("MergeVertexTool;")
        
    def open_targetWeldOptions(self):
        mel.eval("MergeVertexToolOptions;")
        
    def popup_targetWeld(self, position):
        targetWeld_popup = QtWidgets.QMenu()
        targetWeld_action = QtWidgets.QAction('Settings', self)
        targetWeld_action.triggered.connect(self.open_targetWeldOptions)
        targetWeld_popup.addAction(targetWeld_action)
        targetWeld_popup.exec_(self.targetWeld_button.mapToGlobal(position))

    def widgets_targetWeld(self):
        self.targetWeld_button = QtWidgets.QPushButton("targetWeld")
        self.targetWeld_button.setIcon(QtGui.QIcon(":weld_NEX32.png"))
        self.targetWeld_button.setIconSize(QtCore.QSize(25, 20))
        self.targetWeld_button.clicked.connect(self.perform_targetWeld)
        self.targetWeld_button.setContextMenuPolicy(QtCore.Qt.CustomContextMenu)
        self.targetWeld_button.customContextMenuRequested.connect(self.popup_targetWeld) 
        
    def perform_union(self):
        mel.eval("PolygonBooleanUnion;")
        
    def open_unionOptions(self):
        mel.eval("PolygonBooleanUnionOptions;")
        
    def popup_union(self, position):
        union_popup = QtWidgets.QMenu()
        union_action = QtWidgets.QAction('Settings', self)
        union_action.triggered.connect(self.open_unionOptions)
        union_popup.addAction(union_action)
        union_popup.exec_(self.union_button.mapToGlobal(position))

    def widgets_union(self):
        self.union_button = QtWidgets.QPushButton("Union")
        self.union_button.setIcon(QtGui.QIcon(":polyBooleansUnion.png"))
        self.union_button.setIconSize(QtCore.QSize(25, 20))
        self.union_button.clicked.connect(self.perform_union)
        self.union_button.setContextMenuPolicy(QtCore.Qt.CustomContextMenu)
        self.union_button.customContextMenuRequested.connect(self.popup_union) 
        
    def perform_difference(self):
        mel.eval("PolygonBooleanDifference;")
        
    def open_differenceOptions(self):
        mel.eval("PolygonBooleanDifferenceOptions;")
        
    def popup_difference(self, position):
        difference_popup = QtWidgets.QMenu()
        difference_action = QtWidgets.QAction('Settings', self)
        difference_action.triggered.connect(self.open_differenceOptions)
        difference_popup.addAction(difference_action)
        difference_popup.exec_(self.difference_button.mapToGlobal(position))

    def widgets_difference(self):
        self.difference_button = QtWidgets.QPushButton("difference")
        self.difference_button.setIcon(QtGui.QIcon(":polyBooleansDifference.png"))
        self.difference_button.setIconSize(QtCore.QSize(25, 20))
        self.difference_button.clicked.connect(self.perform_difference)
        self.difference_button.setContextMenuPolicy(QtCore.Qt.CustomContextMenu)
        self.difference_button.customContextMenuRequested.connect(self.popup_difference)
        
    def perform_difference(self):
        mel.eval("PolygonBooleanIntersection;")
        
    def open_differenceOptions(self):
        mel.eval("PolygonBooleanIntersectionOptions;")
        
    def popup_difference(self, position):
        difference_popup = QtWidgets.QMenu()
        difference_action = QtWidgets.QAction('Settings', self)
        difference_action.triggered.connect(self.open_differenceOptions)
        difference_popup.addAction(difference_action)
        difference_popup.exec_(self.difference_button.mapToGlobal(position))

    def widgets_difference(self):
        self.difference_button = QtWidgets.QPushButton("difference")
        self.difference_button.setIcon(QtGui.QIcon(":polyBooleansIntersection.png"))
        self.difference_button.setIconSize(QtCore.QSize(25, 20))
        self.difference_button.clicked.connect(self.perform_difference)
        self.difference_button.setContextMenuPolicy(QtCore.Qt.CustomContextMenu)
        self.difference_button.customContextMenuRequested.connect(self.popup_difference) 
        
    def perform_intersection(self):
        mel.eval("PolygonBooleanIntersection;")
        
    def open_intersectionOptions(self):
        mel.eval("PolygonBooleanIntersectionOptions;")
        
    def popup_intersection(self, position):
        intersection_popup = QtWidgets.QMenu()
        intersection_action = QtWidgets.QAction('Settings', self)
        intersection_action.triggered.connect(self.open_intersectionOptions)
        intersection_popup.addAction(intersection_action)
        intersection_popup.exec_(self.intersection_button.mapToGlobal(position))

    def widgets_intersection(self):
        self.intersection_button = QtWidgets.QPushButton("intersection")
        self.intersection_button.setIcon(QtGui.QIcon(":polyBooleansIntersection.png"))
        self.intersection_button.setIconSize(QtCore.QSize(25, 20))
        self.intersection_button.clicked.connect(self.perform_intersection)
        self.intersection_button.setContextMenuPolicy(QtCore.Qt.CustomContextMenu)
        self.intersection_button.customContextMenuRequested.connect(self.popup_intersection) 
        
    def perform_combine(self):
        mel.eval("polyPerformAction polyUnite o 0;")
        
    def open_combineOptions(self):
        mel.eval("PolyUniteOptions;")
        
    def popup_combine(self, position):
        combine_popup = QtWidgets.QMenu()
        combine_action = QtWidgets.QAction('Settings', self)
        combine_action.triggered.connect(self.open_combineOptions)
        combine_popup.addAction(combine_action)
        combine_popup.exec_(self.combine_button.mapToGlobal(position))

    def widgets_combine(self):
        self.combine_button = QtWidgets.QPushButton("combine")
        self.combine_button.setIcon(QtGui.QIcon(":polycombineFacet.png"))
        self.combine_button.setIconSize(QtCore.QSize(25, 20))
        self.combine_button.clicked.connect(self.perform_combine)
        self.combine_button.setContextMenuPolicy(QtCore.Qt.CustomContextMenu)
        self.combine_button.customContextMenuRequested.connect(self.popup_combine) 
        
    def perform_separate(self):
        mel.eval("SeparatePolygon;")
        
    def open_separateOptions(self):
        mel.eval("SeparatePolygonOptions;")
        
    def popup_separate(self, position):
        separate_popup = QtWidgets.QMenu()
        separate_action = QtWidgets.QAction('Settings', self)
        separate_action.triggered.connect(self.open_separateOptions)
        separate_popup.addAction(separate_action)
        separate_popup.exec_(self.separate_button.mapToGlobal(position))

    def widgets_separate(self):
        self.separate_button = QtWidgets.QPushButton("separate")
        self.separate_button.setIcon(QtGui.QIcon(":polySeparate.png"))
        self.separate_button.setIconSize(QtCore.QSize(25, 20))
        self.separate_button.clicked.connect(self.perform_separate)
        self.separate_button.setContextMenuPolicy(QtCore.Qt.CustomContextMenu)
        self.separate_button.customContextMenuRequested.connect(self.popup_separate) 
        
    def perform_fillHole(self):
        mel.eval("FillHole")
        
    def open_fillHoleOptions(self):
        mel.eval("FillHoleOptions;")
        
    def popup_fillHole(self, position):
        fillHole_popup = QtWidgets.QMenu()
        fillHole_action = QtWidgets.QAction('Settings', self)
        fillHole_action.triggered.connect(self.open_fillHoleOptions)
        fillHole_popup.addAction(fillHole_action)
        fillHole_popup.exec_(self.fillHole_button.mapToGlobal(position))

    def widgets_fillHole(self):
        self.fillHole_button = QtWidgets.QPushButton("Fill Hole")
        self.fillHole_button.setIcon(QtGui.QIcon(":polyCloseBorder.png"))
        self.fillHole_button.setIconSize(QtCore.QSize(25, 20))
        self.fillHole_button.clicked.connect(self.perform_fillHole)
        self.fillHole_button.setContextMenuPolicy(QtCore.Qt.CustomContextMenu)
        self.fillHole_button.customContextMenuRequested.connect(self.popup_fillHole) 
        
    def perform_reduce(self):
        mel.eval('doPerformPolyReduceArgList 3 {"1","0","0","1","1","1","1","1","1","0.5","0.5","0.5","0.5","0.5","0.5","0","0.01","0","1","0","0.0","1","1","","1","1","50","0","0","1","0","0","0","0"};')
        
    def open_reduceOptions(self):
        mel.eval("performPolyReduce 1;")
        
    def popup_reduce(self, position):
        reduce_popup = QtWidgets.QMenu()
        reduce_action = QtWidgets.QAction('Settings', self)
        reduce_action.triggered.connect(self.open_reduceOptions)
        reduce_popup.addAction(reduce_action)
        reduce_popup.exec_(self.reduce_button.mapToGlobal(position))

    def widgets_reduce(self):
        self.reduce_button = QtWidgets.QPushButton("reduce")
        self.reduce_button.setIcon(QtGui.QIcon(":polyReduce.png"))
        self.reduce_button.setIconSize(QtCore.QSize(25, 20))
        self.reduce_button.clicked.connect(self.perform_reduce)
        self.reduce_button.setContextMenuPolicy(QtCore.Qt.CustomContextMenu)
        self.reduce_button.customContextMenuRequested.connect(self.popup_reduce) 
        
    def perform_remesh(self):
        mel.eval("polyRemesh -maxEdgeLength 2 -useRelativeValues 0 -collapseThreshold 44.4015 -smoothStrength 0 -tessellateBorders 1 -interpolationType 2;")
        mel.eval('polyAverageNormal -prenormalize 1 -allowZeroNormal 0 -postnormalize 0 -distance 0.1 -replaceNormalXYZ 1 0 0') 
        
    def open_remeshOptions(self):
        mel.eval("performPolyRemesh 1;")
        
    def popup_remesh(self, position):
        remesh_popup = QtWidgets.QMenu()
        remesh_action = QtWidgets.QAction('Settings', self)
        remesh_action.triggered.connect(self.open_remeshOptions)
        remesh_popup.addAction(remesh_action)
        remesh_popup.exec_(self.remesh_button.mapToGlobal(position))

    def widgets_remesh(self):
        self.remesh_button = QtWidgets.QPushButton("remesh")
        self.remesh_button.setIcon(QtGui.QIcon(":polyRemesh.png"))
        self.remesh_button.setIconSize(QtCore.QSize(25, 20))
        self.remesh_button.clicked.connect(self.perform_remesh)
        self.remesh_button.setContextMenuPolicy(QtCore.Qt.CustomContextMenu)
        self.remesh_button.customContextMenuRequested.connect(self.popup_remesh) 
        
    def perform_retopo(self):
        mel.eval("polyRetopo -constructionHistory 1 -replaceOriginal 1 -preserveHardEdges 0 -topologyRegularity 0.5 -faceUniformity 0 -anisotropy 0.75 -targetFaceCount 1000 -targetFaceCountTolerance 10;")
        
    def open_retopoOptions(self):
        mel.eval("performPolyRetopo 1:")
        
    def popup_retopo(self, position):
        retopo_popup = QtWidgets.QMenu()
        retopo_action = QtWidgets.QAction('Settings', self)
        retopo_action.triggered.connect(self.open_retopoOptions)
        retopo_popup.addAction(retopo_action)
        retopo_popup.exec_(self.retopo_button.mapToGlobal(position))

    def widgets_retopo(self):
        self.retopo_button = QtWidgets.QPushButton("retopo")
        self.retopo_button.setIcon(QtGui.QIcon(":polyRetopo.png"))
        self.retopo_button.setIconSize(QtCore.QSize(25, 20))
        self.retopo_button.clicked.connect(self.perform_retopo)
        self.retopo_button.setContextMenuPolicy(QtCore.Qt.CustomContextMenu)
        self.retopo_button.customContextMenuRequested.connect(self.popup_retopo) 
        
    def perform_smooth(self):
        mel.eval('polyPerformAction "polySmooth  -mth 0 -sdt 2 -ovb 1 -ofb 3 -ofc 0 -ost 0 -ocr 0 -dv 1 -peh 0 -bnr 1 -c 1 -kb 1 -ksb 1 -khe 0 -kt 1 -kmb 1 -suv 1 -sl 1 -dpe 1 -ps 0.1 -ro 1" f 0;')
        
    def open_smoothOptions(self):
        mel.eval("performPolySmooth 1;")
        
    def popup_smooth(self, position):
        smooth_popup = QtWidgets.QMenu()
        smooth_action = QtWidgets.QAction('Settings', self)
        smooth_action.triggered.connect(self.open_smoothOptions)
        smooth_popup.addAction(smooth_action)
        smooth_popup.exec_(self.smooth_button.mapToGlobal(position))

    def widgets_smooth(self):
        self.smooth_button = QtWidgets.QPushButton("smooth")
        self.smooth_button.setIcon(QtGui.QIcon(":polySmooth.png"))
        self.smooth_button.setIconSize(QtCore.QSize(25, 20))
        self.smooth_button.clicked.connect(self.perform_smooth)
        self.smooth_button.setContextMenuPolicy(QtCore.Qt.CustomContextMenu)
        self.smooth_button.customContextMenuRequested.connect(self.popup_smooth) 
        
    def perform_triangulate(self):
        mel.eval("polyPerformAction polytri f 0;")

    def widgets_triangulate(self):
        self.triangulate_button = QtWidgets.QPushButton("triangulate")
        self.triangulate_button.setIcon(QtGui.QIcon(":polytri.png"))
        self.triangulate_button.setIconSize(QtCore.QSize(25, 20))
        self.triangulate_button.clicked.connect(self.perform_triangulate)
        
    def perform_quadrangulate(self):
        mel.eval('polyPerformAction "polyQuad  -a 30 -kgb 1 -ktb 1 -khe 1 -ws 1" f 0;')
        
    def open_quadrangulateOptions(self):
        mel.eval("performPolyQuadrangulate 1;")
        
    def popup_quadrangulate(self, position):
        quadrangulate_popup = QtWidgets.QMenu()
        quadrangulate_action = QtWidgets.QAction('Settings', self)
        quadrangulate_action.triggered.connect(self.open_quadrangulateOptions)
        quadrangulate_popup.addAction(quadrangulate_action)
        quadrangulate_popup.exec_(self.quadrangulate_button.mapToGlobal(position))

    def widgets_quadrangulate(self):
        self.quadrangulate_button = QtWidgets.QPushButton("quad")
        self.quadrangulate_button.setIcon(QtGui.QIcon(":polyQuad.png"))
        self.quadrangulate_button.setIconSize(QtCore.QSize(25, 20))
        self.quadrangulate_button.clicked.connect(self.perform_quadrangulate)
        self.quadrangulate_button.setContextMenuPolicy(QtCore.Qt.CustomContextMenu)
        self.quadrangulate_button.customContextMenuRequested.connect(self.popup_quadrangulate) 
            
    def perform_mirror(self):
        mel.eval('polyPerformAction "polyMirrorFace  -cutMesh 1 -axis 0 -axisDirection 0 -mergeMode 1 -mergeThresholdType 0 -mergeThreshold 0.001 -mirrorAxis 2 -mirrorPosition 0 -smoothingAngle 30 -flipUVs 0" "f" 0;')
        
    def open_mirrorOptions(self):
        mel.eval("performPolyMirror 1;")
        
    def popup_mirror(self, position):
        mirror_popup = QtWidgets.QMenu()
        mirror_action = QtWidgets.QAction('Settings', self)
        mirror_action.triggered.connect(self.open_mirrorOptions)
        mirror_popup.addAction(mirror_action)
        mirror_popup.exec_(self.mirror_button.mapToGlobal(position))

    def widgets_mirror(self):
        self.mirror_button = QtWidgets.QPushButton("mirror")
        self.mirror_button.setIcon(QtGui.QIcon(":polyMirrorGeometry.png"))
        self.mirror_button.setIconSize(QtCore.QSize(25, 20))
        self.mirror_button.clicked.connect(self.perform_mirror)
        self.mirror_button.setContextMenuPolicy(QtCore.Qt.CustomContextMenu)
        self.mirror_button.customContextMenuRequested.connect(self.popup_mirror) 
        
    def perform_average(self):
        mel.eval("AveragePolygonNormals;")
        
    def open_averageOptions(self):
        mel.eval("AveragePolygonNormalsOptions;")
        
    def popup_average(self, position):
        average_popup = QtWidgets.QMenu()
        average_action = QtWidgets.QAction('Settings', self)
        average_action.triggered.connect(self.open_averageOptions)
        average_popup.addAction(average_action)
        average_popup.exec_(self.average_button.mapToGlobal(position))

    def widgets_average(self):
        self.average_button = QtWidgets.QPushButton("Average")
        self.average_button.setIcon(QtGui.QIcon(":polyNormalAverage.png"))
        self.average_button.setIconSize(QtCore.QSize(25, 20))
        self.average_button.clicked.connect(self.perform_average)
        self.average_button.setContextMenuPolicy(QtCore.Qt.CustomContextMenu)
        self.average_button.customContextMenuRequested.connect(self.popup_average) 
        
    def perform_setToFace(self):
        mel.eval("polySetToFaceNormal ;")
        
    def open_setToFaceOptions(self):
        mel.eval("polySetToFaceNormal Options;")
        
    def popup_setToFace(self, position):
        setToFace_popup = QtWidgets.QMenu()
        setToFace_action = QtWidgets.QAction('Settings', self)
        setToFace_action.triggered.connect(self.open_setToFaceOptions)
        setToFace_popup.addAction(setToFace_action)
        setToFace_popup.exec_(self.setToFace_button.mapToGlobal(position))

    def widgets_setToFace(self):
        self.setToFace_button = QtWidgets.QPushButton("setToFace")
        self.setToFace_button.setIcon(QtGui.QIcon(":polyNormalSetToFace.png"))
        self.setToFace_button.setIconSize(QtCore.QSize(25, 20))
        self.setToFace_button.clicked.connect(self.perform_setToFace)
        self.setToFace_button.setContextMenuPolicy(QtCore.Qt.CustomContextMenu)
        self.setToFace_button.customContextMenuRequested.connect(self.popup_setToFace) 
        
    def perform_reverse(self):
        mel.eval("ReversePolygonNormals;")
        
    def open_reverseOptions(self):
        mel.eval("ReversePolygonNormalsOptions;")
        
    def popup_reverse(self, position):
        reverse_popup = QtWidgets.QMenu()
        reverse_action = QtWidgets.QAction('Settings', self)
        reverse_action.triggered.connect(self.open_reverseOptions)
        reverse_popup.addAction(reverse_action)
        reverse_popup.exec_(self.reverse_button.mapToGlobal(position))

    def widgets_reverse(self):
        self.reverse_button = QtWidgets.QPushButton("Reverse")
        self.reverse_button.setIcon(QtGui.QIcon(":polyNormal.png"))
        self.reverse_button.setIconSize(QtCore.QSize(25, 20))
        self.reverse_button.clicked.connect(self.perform_reverse)
        self.reverse_button.setContextMenuPolicy(QtCore.Qt.CustomContextMenu)
        self.reverse_button.customContextMenuRequested.connect(self.popup_reverse) 
        
    def perform_conform(self):
        mel.eval("ConformPolygonNormals;")
        
    def widgets_conform(self):
        self.conform_button = QtWidgets.QPushButton("Conform")
        self.conform_button.setIcon(QtGui.QIcon(":polyNormalsConform.png"))
        self.conform_button.setIconSize(QtCore.QSize(25, 20))
        self.conform_button.clicked.connect(self.perform_conform)

        
    def perform_lockNormals(self):
        mel.eval("LockNormals;")
        
    def widgets_lockNormals(self):
        self.lockNormals_button = QtWidgets.QPushButton("Lock Normals")
        self.lockNormals_button.setIcon(QtGui.QIcon(":polyNormalLock.png"))
        self.lockNormals_button.setIconSize(QtCore.QSize(25, 20))
        self.lockNormals_button.clicked.connect(self.perform_lockNormals)
        
    def perform_unlockNormals(self):
        mel.eval("UnlockNormals;")
        
    def widgets_unlockNormals(self):
        self.unlockNormals_button = QtWidgets.QPushButton("Unlock Normals")
        self.unlockNormals_button.setIcon(QtGui.QIcon(":polyNormalUnlock.png"))
        self.unlockNormals_button.setIconSize(QtCore.QSize(25, 20))
        self.unlockNormals_button.clicked.connect(self.perform_unlockNormals)
        
    def perform_unlockNormals(self):
        mel.eval("UnlockNormals;")
        
    def widgets_unlockNormals(self):
        self.unlockNormals_button = QtWidgets.QPushButton("Unlock Normals")
        self.unlockNormals_button.setIcon(QtGui.QIcon(":polyNormalUnlock.png"))
        self.unlockNormals_button.setIconSize(QtCore.QSize(25, 20))
        self.unlockNormals_button.clicked.connect(self.perform_unlockNormals)
    

    
    def perform_toggleReflectionSetMode(self):
        print "this"
        currentMode = cmds.symmetricModelling(query=True,symmetry=False)
        print currentMode
        newMode = "none" 
        if currentMode == 0:
            self.toggleReflectionSetModeOn_button.setHidden(False)
            self.toggleReflectionSetModeOff_button.setHidden(True)
            cmds.symmetricModelling(symmetry=True)
            cmds.symmetricModelling(about='world')
            cmds.symmetricModelling(axis='x')
        else:
            self.toggleReflectionSetModeOn_button.setHidden(True)
            self.toggleReflectionSetModeOff_button.setHidden(False)
            cmds.symmetricModelling(symmetry=False)
            
    def widgets_toggleReflectionSetModeOff(self):
        self.toggleReflectionSetModeOff_button = QtWidgets.QPushButton("Symmetry")
        self.toggleReflectionSetModeOff_button.setIconSize(QtCore.QSize(40, 30))
        self.toggleReflectionSetModeOff_button.clicked.connect(self.perform_toggleReflectionSetMode)
        
    def widgets_toggleReflectionSetModeOn(self):
        self.toggleReflectionSetModeOn_button = QtWidgets.QPushButton("Symmetry")
        self.toggleReflectionSetModeOn_button.setHidden(True)
        self.toggleReflectionSetModeOn_button.setStyleSheet("background-color: darkblue;")
        self.toggleReflectionSetModeOn_button.setIconSize(QtCore.QSize(40, 30))
        self.toggleReflectionSetModeOn_button.clicked.connect(self.perform_toggleReflectionSetMode)
        
    def set_camBasedSel(self):

        currentMode=cmds.selectPref(query=True,useDepth=True)

        if currentMode == False:
            self.toggleCamBasedSelOff_button.setHidden(True)
            self.toggleCamBasedSelOn_button.setHidden(False)
            cmds.selectPref(useDepth=True)
        else:
            self.toggleCamBasedSelOff_button.setHidden(False)
            self.toggleCamBasedSelOn_button.setHidden(True)
            cmds.selectPref(useDepth=False)
            
    def widgets_toggleCamBasedSelOff(self):
        self.toggleCamBasedSelOff_button = QtWidgets.QPushButton("Cam Base Selection Off")
        self.toggleCamBasedSelOff_button.setIconSize(QtCore.QSize(40, 30))
        self.toggleCamBasedSelOff_button.clicked.connect(self.set_camBasedSel)
        
    def widgets_toggleCamBasedSelOn(self):
        self.toggleCamBasedSelOn_button = QtWidgets.QPushButton("Cam Base Selection On")
        self.toggleCamBasedSelOn_button.setStyleSheet("background-color: darkblue;")
        self.toggleCamBasedSelOn_button.setHidden(True)
        self.toggleCamBasedSelOn_button.setIconSize(QtCore.QSize(40, 30))
        self.toggleCamBasedSelOn_button.clicked.connect(self.set_camBasedSel)
        
                
    def set_marquee(self):
        cmds.selectPref(paintSelect=False)

    def widgets_marquee(self):
        self.marquee_button = QtWidgets.QPushButton("Marquee")
        self.marquee_button.setIconSize(QtCore.QSize(40, 30))
        self.marquee_button.clicked.connect(self.set_marquee)
        
    def set_drag(self):
        cmds.selectPref(paintSelect=True)

    def widgets_drag(self):
        self.drag_button = QtWidgets.QPushButton("Drag")
        self.drag_button.setIconSize(QtCore.QSize(40, 30))
        self.drag_button.clicked.connect(self.set_drag)
        
    def set_preserveUVs(self):
        mel.eval("setTRSPreserveUVs(!`optionVar -q trsManipsPreserveUvs`)")

    def widgets_preserveUVs(self):
        self.preserveUVs_button = QtWidgets.QPushButton("Preserve UVs")
        self.preserveUVs_button.setIconSize(QtCore.QSize(40, 30))
        self.preserveUVs_button.clicked.connect(self.set_preserveUVs)
        
    def set_preserveChildren(self):
        mel.eval("setTRSPreserveChildPosition(!`optionVar -q TRSPreserveChildPosition`)")

    def widgets_preserveChildren(self):
        self.preserveChildren_button = QtWidgets.QPushButton("Preserve Children")
        self.preserveChildren_button.setIconSize(QtCore.QSize(40, 30))
        self.preserveChildren_button.clicked.connect(self.set_preserveChildren)
        
    def set_tweakMode(self):
        mel.eval("setTRSPreserveChildPosition(!`optionVar -q TRSPreserveChildPosition`)")

    def widgets_tweakMode(self):
        self.tweakMode_button = QtWidgets.QPushButton("Tweak")
        self.tweakMode_button.setIconSize(QtCore.QSize(40, 30))
        self.tweakMode_button.clicked.connect(self.set_tweakMode)
        
        
    def set_edgeConstraint(self):    
        if not constraint_state:
            constraint_state = 0
        global constraint_state
        if constraint_state == 0:
            cmds.dR_slideEdge()
            constraint_state = 1
        else:
            cmds.dR_slideOff()
            constraint_state = 0
            
    def widgets_edgeConstraint(self):
        self.edgeConstraint_button = QtWidgets.QPushButton("Edge Constraint")
        self.edgeConstraint_button.setIconSize(QtCore.QSize(40, 30))
        self.edgeConstraint_button.clicked.connect(self.set_edgeConstraint)
            

    def widgets_sculpting(self):    
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

    def widgets_collapsables(self): 
        
        self.view_tools = CollapsibleWidget("Views")
        self.view_tools.set_expanded(True)
        self.history_tools = CollapsibleWidget("Delete History")
        self.history_tools.set_expanded(True)
        self.modify_tools = CollapsibleWidget("Modify")
        self.modify_tools.set_expanded(False)
        self.duplicate_tools = CollapsibleWidget("Duplicate")
        self.duplicate_tools.set_expanded(False)
        
        self.polygon_primatives = CollapsibleWidget("Polygon Primatives")
        self.polygon_primatives.set_expanded(True)
        self.polygon_primativesSec = CollapsibleWidget("")
        self.polygon_primativesSec.set_expanded(False)
        self.polygon_primativesSec.set_Margins(4,0,0,0)
        self.polygon_primativesSec.set_header_background_color(QtGui.QColor(125,125, 125, 0))
 
        self.sculpting_menu = CollapsibleWidget("Sculpting")
        self.sculpting_menu.set_expanded(True)
        
        self.secSculpting_menu = CollapsibleWidget("")
        self.secSculpting_menu.set_expanded(False)
        self.secSculpting_menu.set_Margins(4,0,0,0)
        self.secSculpting_menu.set_header_background_color(QtGui.QColor(125,125, 125,0)) 
        
        self.boolean_menu = CollapsibleWidget("Boolean")
        self.boolean_menu.set_expanded(False)  
        
        self.display_menu = CollapsibleWidget("Display")
        self.display_menu.set_expanded(False)          
        
        self.combine_menu = CollapsibleWidget("Combine")
        self.combine_menu.set_expanded(True)
        
        self.remesh_menu = CollapsibleWidget("Remesh")
        self.remesh_menu .set_expanded(True)
        
        self.edgeTools_menu = CollapsibleWidget("Edge Tools")
        self.edgeTools_menu .set_expanded(True)
        
        self.symmetry_menu = CollapsibleWidget("Symmetry")
        self.edgeTools_menu .set_expanded(True)
        
        # Edit Mesh Tools          
        self.editMesh_menu = CollapsibleWidget("Edit Mesh Tools  ")
        self.editMesh_menu.set_expanded(True)  
        self.editMesh_menuSec = CollapsibleWidget("")
        self.editMesh_menuSec.set_expanded(True)  
        self.editMesh_menuSec.set_expanded(False)
        self.editMesh_menuSec.set_Margins(4,0,0,0)
        self.editMesh_menuSec.set_header_background_color(QtGui.QColor(125,125, 125, 0))                

        #Mesh Tools
        self.meshTools_menu = CollapsibleWidget("Mesh Tools")
        self.meshTools_menu.set_expanded(True)

    def create_layout(self):
        
        history_layout1 = QtWidgets.QHBoxLayout()
        history_layout1.addWidget(self.deleteHistory_button)
        history_layout1.addWidget(self.deleteNonDefHistory_button)
        
        modify_layout0 = QtWidgets.QHBoxLayout()
        modify_layout0.addWidget(self.centerPivot_button)
        modify_layout0.addWidget(self.zeroPivot_button)

        
        modify_layout1 = QtWidgets.QHBoxLayout()
        modify_layout1.addWidget(self.bakePivot_button)
        modify_layout1.addWidget(self.freezeTransform_button)
        modify_layout1.addWidget(self.resetTransform_button)

        duplicate_layout1 = QtWidgets.QHBoxLayout()
        duplicate_layout1.addWidget(self.duplicate_button)
        duplicate_layout1.addWidget(self.instance_button)
        duplicate_layout1.addWidget(self.replace_button)
        
        selection_layout1 = QtWidgets.QHBoxLayout()
        selection_layout1.addWidget(self.toggleReflectionSetModeOff_button)
        selection_layout1.addWidget(self.toggleReflectionSetModeOn_button)
        selection_layout1.addWidget(self.toggleCamBasedSelOff_button)
        selection_layout1.addWidget(self.toggleCamBasedSelOn_button)
        
        selection_layout2 = QtWidgets.QHBoxLayout()
        selection_layout2.addWidget(self.marquee_button)
        selection_layout2.addWidget(self.drag_button)
        selection_layout2.addWidget(self.tweakMode_button)
        
        selection_layout3 = QtWidgets.QHBoxLayout()
        selection_layout3.addWidget(self.preserveUVs_button)
        selection_layout3.addWidget(self.preserveChildren_button)
        
        selection_layout4 = QtWidgets.QHBoxLayout()
        selection_layout4.addWidget(self.edgeConstraint_button)



        prim_layout1 = QtWidgets.QHBoxLayout()
        prim_layout1.addWidget(self.sphere_button)
        prim_layout1.addWidget(self.cube_button)
        prim_layout1.addWidget(self.plane_button)
        prim_layout1.addWidget(self.cylinder_button)
        prim_layout1.addWidget(self.torus_button)
        prim_layout1.addWidget(self.cone_button)
        
        prim_layout2 = QtWidgets.QHBoxLayout()
        prim_layout2.addWidget(self.disc_button)
        prim_layout2.addWidget(self.platonic_button)
        prim_layout2.addWidget(self.pyramid_button)
        prim_layout2.addWidget(self.prism_button)
        prim_layout2.addWidget(self.pipe_button)
        prim_layout2.addWidget(self.helix_button)
        
        prim_layout3 = QtWidgets.QHBoxLayout()
        #prim_layout3.addWidget(self.pipe_button)
        #prim_layout3.addWidget(self.helix_button)
        prim_layout3.addWidget(self.gear_button)
        prim_layout3.addWidget(self.soccer_button)
        prim_layout3.addWidget(self.superEllipse_button)
        prim_layout3.addWidget(self.sphericalHarm_button)
        prim_layout3.addWidget(self.ultraShape_button)
        prim_layout3.addWidget(self.sculptObjects_button)
        
        sculpt_layout1 = QtWidgets.QHBoxLayout()
        sculpt_layout1.addWidget(self.lift_button)
        sculpt_layout1.addWidget(self.sculptSmooth_button)
        sculpt_layout1.addWidget(self.sculptRelax_button)
        sculpt_layout1.addWidget(self.sculptGrab_button)
        sculpt_layout1.addWidget(self.sculptPinch_button)
        sculpt_layout1.addWidget(self.sculptFlatten_button)
        #sculpt_layout1.addWidget(self.sculptObjects_button)
        sculpt_layout1.setAlignment(QtCore.Qt.AlignTop)

        sculpt_layout2 = QtWidgets.QHBoxLayout()

        sculpt_layout2.addWidget(self.sculptFoamy_button)
        sculpt_layout2.addWidget(self.sculptSpray_button)
        sculpt_layout2.addWidget(self.sculptRepeat_button)
        sculpt_layout2.addWidget(self.sculptImprint_button)
        sculpt_layout2.addWidget(self.sculptWax_button)
        sculpt_layout2.addWidget(self.sculptScrape_button)
        sculpt_layout2.addWidget(self.sculptFill_button)
        
        sculpt_layout2.setAlignment(QtCore.Qt.AlignTop)
        
        sculpt_layout3 = QtWidgets.QHBoxLayout()
        sculpt_layout3.addWidget(self.sculptKnife_button)
        sculpt_layout3.addWidget(self.sculptSmear_button)
        sculpt_layout3.addWidget(self.sculptBulge_button)
        sculpt_layout3.addWidget(self.sculptAmplify_button)
        sculpt_layout3.addWidget(self.sculptFreeze_button)
        sculpt_layout3.addWidget(self.sculptFreezeSelect_button)
        sculpt_layout3.setAlignment(QtCore.Qt.AlignTop)
        
        boolean_layout1 = QtWidgets.QHBoxLayout()
        boolean_layout1.addWidget(self.union_button)
        boolean_layout1.addWidget(self.difference_button)
        boolean_layout1.addWidget(self.intersection_button)
        boolean_layout1.setAlignment(QtCore.Qt.AlignTop)

        
        mesh_layout2 = QtWidgets.QHBoxLayout()
        mesh_layout2.addWidget(self.combine_button)
        mesh_layout2.addWidget(self.separate_button)
        mesh_layout2.setAlignment(QtCore.Qt.AlignTop)
        
        mesh_layout3 = QtWidgets.QHBoxLayout()
        mesh_layout3.addWidget(self.reduce_button)
        mesh_layout3.addWidget(self.remesh_button)
        mesh_layout3.addWidget(self.retopo_button)
        mesh_layout3.setAlignment(QtCore.Qt.AlignTop)
        
        mesh_layout4 = QtWidgets.QHBoxLayout()
        mesh_layout4.setAlignment(QtCore.Qt.AlignTop)
        
        mesh_layout5 = QtWidgets.QHBoxLayout()
        mesh_layout5.addWidget(self.averageVert_button)
        mesh_layout5.addWidget(self.divide_button)
        mesh_layout5.addWidget(self.smooth_button)
        mesh_layout5.setAlignment(QtCore.Qt.AlignTop)
        
        mesh_layout6 = QtWidgets.QHBoxLayout()
        mesh_layout6.addWidget(self.conform_button)
        mesh_layout6.addWidget(self.triangulate_button)
        mesh_layout6.addWidget(self.quadrangulate_button)
        #mesh_layout6.addWidget(self.mirror_button)

        
        editMesh_layout1 = QtWidgets.QHBoxLayout()
        #editMesh_layout1.addWidget(self.divide_button)
        #editMesh_layout1.addWidget(self.bevel_button)
        
        editMesh_layout1.addWidget(self.connect_button)
        editMesh_layout1.addWidget(self.bridge_button)
        editMesh_layout1.setAlignment(QtCore.Qt.AlignTop)
        
        
        editMesh_layout2 = QtWidgets.QHBoxLayout()
        editMesh_layout2.addWidget(self.appendFacet_button)
        editMesh_layout2.addWidget(self.transform_button)
        editMesh_layout2.addWidget(self.circularize_button)
        editMesh_layout2.addWidget(self.collapseEdge_button)
        editMesh_layout2.setAlignment(QtCore.Qt.AlignTop)
        
        editMesh_layout3 = QtWidgets.QHBoxLayout()
        #editMesh_layout3.addWidget(self.connect_button)
        editMesh_layout3.addWidget(self.bevel_button)
        editMesh_layout3.addWidget(self.extrude_button)
        editMesh_layout3.setAlignment(QtCore.Qt.AlignTop)

        editMesh_layout4 = QtWidgets.QHBoxLayout()
        editMesh_layout4.addWidget(self.merge_button)
        #editMesh_layout4.addWidget(self.mergeToCenter_button)
        editMesh_layout4.addWidget(self.targetWeld_button)
        #editMesh_layout4.addWidget(self.transform_button)
        editMesh_layout4.setAlignment(QtCore.Qt.AlignTop)
        
    
        editMesh_layout5 = QtWidgets.QHBoxLayout()
        #editMesh_layout5.addWidget(self.flip_button)
        editMesh_layout5.addWidget(self.symmetrize_button)
        editMesh_layout5.addWidget(self.mirror_button)
        editMesh_layout5.setAlignment(QtCore.Qt.AlignTop)
        
        editMesh_layout6 = QtWidgets.QHBoxLayout()
        editMesh_layout6.addWidget(self.detach_button)
        editMesh_layout6.addWidget(self.extract_button)
        editMesh_layout6.addWidget(self.duplicateFacet_button)
        #editMesh_layout6.addWidget(self.reorder_button)
        editMesh_layout6.setAlignment(QtCore.Qt.AlignTop)
        
        editMesh_layout7 = QtWidgets.QHBoxLayout()
        editMesh_layout7.addWidget(self.crease_button)
        #editMesh_layout7.addWidget(self.delEdge_button)
        editMesh_layout7.addWidget(self.edgeFlow_button)
        editMesh_layout7.setAlignment(QtCore.Qt.AlignTop)
        
        editMesh_layout8 = QtWidgets.QHBoxLayout()
        editMesh_layout8.addWidget(self.spinEdgeBackward_button)
        editMesh_layout8.addWidget(self.spinEdgeForward_button)
        editMesh_layout8.addWidget(self.invisibleFace_button)
        editMesh_layout8.addWidget(self.createPoly_button)
        editMesh_layout8.setAlignment(QtCore.Qt.AlignTop)
        
        editMesh_layout9 = QtWidgets.QHBoxLayout()
        editMesh_layout9.addWidget(self.chamfer_button)
        editMesh_layout9.addWidget(self.poke_button)
        editMesh_layout9.addWidget(self.wedge_button)
        editMesh_layout9.setAlignment(QtCore.Qt.AlignTop)
        
        editMesh_layout10 = QtWidgets.QHBoxLayout()
        editMesh_layout10.addWidget(self.reorder_button)
        editMesh_layout10.addWidget(self.flipEdge_button)
        editMesh_layout10.addWidget(self.projectCurve_button)
        editMesh_layout10.addWidget(self.curveSplit_button)
        editMesh_layout10.setAlignment(QtCore.Qt.AlignTop)
        
        meshTools_layout1 = QtWidgets.QHBoxLayout()
        #meshTools_layout1.addWidget(self.appendFacet_button)
        
        
        meshTools_layout1.addWidget(self.slideEdge_button)
        meshTools_layout1.addWidget(self.insertEdge_button)
        #meshTools_layout1.addWidget(self.crease_button)
        meshTools_layout1.setAlignment(QtCore.Qt.AlignTop)
        
        meshTools_layout2 = QtWidgets.QHBoxLayout()
        #meshTools_layout2.addWidget(self.createPoly_button)
        #meshTools_layout2.addWidget(self.insertEdge_button)
        #meshTools_layout2.addWidget(self.insertEdge_button)
        meshTools_layout2.addWidget(self.offsetEdge_button)
        meshTools_layout2.addWidget(self.fillHole_button)
        meshTools_layout2.addWidget(self.makeHole_button)
        meshTools_layout2.setAlignment(QtCore.Qt.AlignTop)
        
        meshTools_layout3 = QtWidgets.QHBoxLayout()
        #meshTools_layout3.addWidget(self.multiCut_button)

        meshTools_layout3.setAlignment(QtCore.Qt.AlignTop)
        
        meshTools_layout4 = QtWidgets.QHBoxLayout()
        meshTools_layout4.addWidget(self.multiCut_button)
        meshTools_layout4.addWidget(self.quadDraw_button)
        meshTools_layout4.setAlignment(QtCore.Qt.AlignTop)
        
        meshTools_layout5 = QtWidgets.QHBoxLayout()
        meshTools_layout5.addWidget(self.slideEdge_button)
        #meshTools_layout5.addWidget(self.targetWeld_button)
        meshTools_layout5.setAlignment(QtCore.Qt.AlignTop)
        
        #self.setCentralWidget(scrollable_widget)
        main_layout = QtWidgets.QVBoxLayout(self)
        main_layout.setSpacing(0)
        main_layout.setContentsMargins(0, 0, 0, 0)
        #main_layout.se
        
        display_layout1= QtWidgets.QHBoxLayout()
        display_layout1.addWidget(self.average_button)
        display_layout1.addWidget(self.reverse_button)
        display_layout1.addWidget(self.setToFace_button)
        
        
        display_layout2= QtWidgets.QHBoxLayout()
        display_layout2.addWidget(self.conform_button)
        display_layout2.addWidget(self.lockNormals_button)
        display_layout2.addWidget(self.unlockNormals_button)
        
        
        line1 = QtWidgets.QFrame()
        line1.setFrameShape(QtWidgets.QFrame.HLine)
        line1.setFrameShadow(QtWidgets.QFrame.Sunken)
        line_layout1= QtWidgets.QHBoxLayout()
        line_layout1.addWidget(line1)  
        line2 = QtWidgets.QFrame()
        line2.setFrameShape(QtWidgets.QFrame.HLine)
        line2.setFrameShadow(QtWidgets.QFrame.Sunken)
        line_layout2 = QtWidgets.QHBoxLayout()
        line_layout2.addWidget(line2)
        line3 = QtWidgets.QFrame()
        line3.setFrameShape(QtWidgets.QFrame.HLine)
        line3.setFrameShadow(QtWidgets.QFrame.Sunken)
        line3_layout = QtWidgets.QHBoxLayout()
        line3_layout.addWidget(line3)
        line4 = QtWidgets.QFrame()
        line4.setFrameShape(QtWidgets.QFrame.HLine)
        line4.setFrameShadow(QtWidgets.QFrame.Sunken)
        line4_layout = QtWidgets.QHBoxLayout()
        line4_layout.addWidget(line4)
        line5 = QtWidgets.QFrame()
        line5.setFrameShape(QtWidgets.QFrame.HLine)
        line5.setFrameShadow(QtWidgets.QFrame.Sunken)
        line5_layout = QtWidgets.QHBoxLayout()
        line5_layout.addWidget(line5)
        line6 = QtWidgets.QFrame()
        line6.setFrameShape(QtWidgets.QFrame.HLine)
        line6.setFrameShadow(QtWidgets.QFrame.Sunken)
        line6_layout = QtWidgets.QHBoxLayout()
        line6_layout.addWidget(line6)
        line7 = QtWidgets.QFrame()
        line7.setFrameShape(QtWidgets.QFrame.HLine)
        line7.setFrameShadow(QtWidgets.QFrame.Sunken)
        line7_layout = QtWidgets.QHBoxLayout()
        line7_layout.addWidget(line7)
        line8 = QtWidgets.QFrame()
        line8.setFrameShape(QtWidgets.QFrame.HLine)
        line8.setFrameShadow(QtWidgets.QFrame.Sunken)
        line8_layout = QtWidgets.QHBoxLayout()
        line8_layout.addWidget(line8)
        line9 = QtWidgets.QFrame()
        line9.setFrameShape(QtWidgets.QFrame.HLine)
        line9.setFrameShadow(QtWidgets.QFrame.Sunken)
        line9_layout = QtWidgets.QHBoxLayout()
        line9_layout.addWidget(line9)
        line10 = QtWidgets.QFrame()
        line10.setFrameShape(QtWidgets.QFrame.HLine)
        line10.setFrameShadow(QtWidgets.QFrame.Sunken)
        line10_layout = QtWidgets.QHBoxLayout()
        line10_layout.addWidget(line10)
        line11 = QtWidgets.QFrame()
        line11.setFrameShape(QtWidgets.QFrame.HLine)
        line11.setFrameShadow(QtWidgets.QFrame.Sunken)
        line11_layout = QtWidgets.QHBoxLayout()
        line11_layout.addWidget(line11)



        scrollable_widget = ScrollableWidget()
        main_layout.addWidget(scrollable_widget)
        scrollable_widget.add_layout(history_layout1) 
        scrollable_widget.add_layout(line_layout1 )
        scrollable_widget.add_layout(modify_layout0)
        scrollable_widget.add_layout(modify_layout1)
        scrollable_widget.add_layout(line_layout2 )  

        #scrollable_widget.add_widget(self.history_tools)
        #self.history_tools.add_layout(history_layout1)     
        #scrollable_widget.add_widget(self.modify_tools)
        #self.modify_tools.add_layout(modify_layout0)
        #self.modify_tools.add_layout(modify_layout1)
        #scrollable_widget.add_widget(self.duplicate_tools)
        scrollable_widget.add_layout(selection_layout2 )
        scrollable_widget.add_layout(selection_layout1 )
        scrollable_widget.add_layout(selection_layout3 )
        scrollable_widget.add_layout(selection_layout4 )
        scrollable_widget.add_layout(duplicate_layout1)

        scrollable_widget.add_layout(line3_layout )  
        #scrollable_widget.add_widget(self.polygon_primatives)
        scrollable_widget.add_layout(prim_layout1)
        scrollable_widget.add_layout(prim_layout2)
        scrollable_widget.add_layout(prim_layout3)
        scrollable_widget.add_layout(line4_layout )  
    
        
        #scrollable_widget.add_widget(self.sculpting_menu)
        scrollable_widget.add_layout(sculpt_layout1)
        scrollable_widget.add_layout(sculpt_layout2)
        scrollable_widget.add_layout(sculpt_layout3)
        scrollable_widget.add_layout(line5_layout ) 
        #self.sculpting_menu.add_widget(self.secSculpting_menu)
        
        #scrollable_widget.add_widget(self.remesh_menu)
        scrollable_widget.add_layout(mesh_layout3)
        scrollable_widget.add_layout(mesh_layout4)
        scrollable_widget.add_layout(mesh_layout5)
        scrollable_widget.add_layout(line6_layout ) 
        #scrollable_widget.add_widget(self.combine_menu)
        
        scrollable_widget.add_layout(mesh_layout2)
        scrollable_widget.add_layout(editMesh_layout6)
        scrollable_widget.add_layout(line7_layout ) 
        

        #self.remesh_menu.add_layout(mesh_layout6)
        #scrollable_widget.add_widget(self.editMesh_menu)
        
        scrollable_widget.add_layout(meshTools_layout4)
        scrollable_widget.add_layout(editMesh_layout1)
        scrollable_widget.add_layout(line8_layout ) 
        scrollable_widget.add_layout(editMesh_layout3)
        scrollable_widget.add_layout(editMesh_layout4)
        scrollable_widget.add_layout(line9_layout ) 
        scrollable_widget.add_layout(editMesh_layout5)
        scrollable_widget.add_layout(editMesh_layout7)
        #scrollable_widget.add_layout(meshTools_layout1) 
        scrollable_widget.add_layout(line10_layout ) 
        #self.editMesh_menu.add_widget(self.editMesh_menuSec)

        #scrollable_widget.add_widget(self.meshTools_menu)
  
        #self.meshTools_menu.add_layout(meshTools_layout4)  
        #self.meshTools_menu.add_layout(meshTools_layout5)  
        #scrollable_widget.add_widget(self.edgeTools_menu)
        #scrollable_widget.add_widget(self.symmetry_menu)
        #scrollable_widget.add_widget(self.boolean_menu)
        scrollable_widget.add_layout(boolean_layout1)
        scrollable_widget.add_layout(line11_layout ) 
        #scrollable_widget.add_widget(self.display_menu)
        scrollable_widget.add_layout(display_layout1)
        scrollable_widget.add_layout(display_layout2)
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
        self.separate_button.clicked.connect(self.perform_separate)
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
        
    def perform_separate(self):
        cmds.polySeparate()
        

        
    def perform_fillHole(self):
        cmds.polyCloseBorder()
        
    def perform_reduce(self):
        cmds.polyReduce(ver=1,trm=0,shp=0, keepBorder=1, keepMapBorder=1,keepColorBorder=1,keepHardEdge=1, keepCreaseEdge=1, keepBorderWeight= 0.5,keepMapBorderWeight=0.5,keepColorBorderWeight=0.5,keepFaceGroupBorderWeight=0.5,keepHardEdgeWeight=0.5,keepCreaseEdgeWeight=0.5,useVirtualSymmetry=0,symmetryTolerance=0.01,sx=0,sy=1,sz=0,sw=0,preserveTopology=1,keepQuadsWeight=1,cachingReduce=1,ch=1,p=50,vct=0,tct=0,replaceOriginal=1)
 
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
        cmds.OpenContentBrowser()
        
    def showEvent(self, e):
        if self.workspace_control_instance.is_floating():
            self.workspace_control_instance.set_label("Floating Window")
        else:
            self.workspace_control_instance.set_label("Modeling Helper")
            
class UIEventFilter(QtCore.QObject):

    def eventFilter(self, watched, event):

        camBased= cmds.selectPref(q=True, useDepth=True)

        if camBased==True:

            sample_ui.toggleCamBasedSelOff_button.setHidden(True)
            sample_ui.toggleCamBasedSelOn_button.setHidden(False)
        else:
            sample_ui.toggleCamBasedSelOff_button.setHidden(False)
            sample_ui.toggleCamBasedSelOn_button.setHidden(True)




if __name__ == "__main__":

    workspace_control_name = SampleUI.get_workspace_control_name()
    win_ptr = OpenMayaUI.MQtUtil.mainWindow()
    win = wrapInstance(long(win_ptr), QtWidgets.QMainWindow)

    if cmds.window(workspace_control_name, exists=True):
        cmds.deleteUI(workspace_control_name)  
    try:
        sample_ui.setParent(None)
        sample_ui.deleteLater()
    except:
        pass  

 
    sample_ui = SampleUI()
    filter2 = UIEventFilter()
    win.installEventFilter(filter2)
