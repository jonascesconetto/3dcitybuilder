# -*- coding: utf-8 -*-
"""
/***************************************************************************
 citygen
                                 A QGIS plugin
 A plugin to generate 3D models of urban areas
 Generated by Plugin Builder: http://g-sherman.github.io/Qgis-Plugin-Builder/
                              -------------------
        begin                : 2020-04-30
        git sha              : $Format:%H$
        copyright            : (C) 2020 by Arthur Ruf Hosang da Costa
        email                : arthur.rhc@gmail.com
 ***************************************************************************/

/***************************************************************************
 *                                                                         *
 *   This program is free software; you can redistribute it and/or modify  *
 *   it under the terms of the GNU General Public License as published by  *
 *   the Free Software Foundation; either version 2 of the License, or     *
 *   (at your option) any later version.                                   *
 *                                                                         *
 ***************************************************************************/
"""
from qgis.PyQt.QtCore import QSettings, QTranslator, QCoreApplication
from qgis.PyQt.QtGui import QIcon
from qgis.PyQt.QtWidgets import QAction, QFileDialog, QErrorMessage, QFileDialog
from qgis.core import QgsProject, Qgis, QgsMessageLog, QgsCoordinateReferenceSystem
from qgis.gui import QgsMessageBar

from .generate_model.main import start
from .generate_model.appCtx import appContext
from .generate_model.bibliotecas import DotDict, execute, plugin_management, internet, path_manager, path_manager, \
    progress_bar, plugin_management, logger
from .generate_model.gis.gis import create_viewport_polygon

# Initialize Qt resources from file resources.py
from .resources import *
# Import the code for the dialog
from .citygen_dialog import citygenDialog
import os.path


class citygen:
    """QGIS Plugin Implementation."""

    def __init__(self, iface):
        """Constructor.

        :param iface: An interface instance that will be passed to this class
            which provides the hook by which you can manipulate the QGIS
            application at run time.
        :type iface: QgsInterface
        """
        # Save reference to the QGIS interface
        self.iface = iface
        # initialize plugin directory
        self.plugin_dir = os.path.dirname(__file__)
        # initialize locale
        locale = QSettings().value('locale/userLocale')[0:2]
        locale_path = os.path.join(
            self.plugin_dir,
            'i18n',
            'citygen_{}.qm'.format(locale))

        if os.path.exists(locale_path):
            self.translator = QTranslator()
            self.translator.load(locale_path)
            QCoreApplication.installTranslator(self.translator)

        # Declare instance attributes
        self.actions = []
        self.menu = self.tr(u'&citygen')

        # Check if plugin was started the first time in current QGIS session
        # Must be set in initGui() to survive plugin reloads
        self.first_start = None

    # noinspection PyMethodMayBeStatic
    def tr(self, message):
        """Get the translation for a string using Qt translation API.

        We implement this ourselves since we do not inherit QObject.

        :param message: String for translation.
        :type message: str, QString

        :returns: Translated version of message.
        :rtype: QString
        """
        # noinspection PyTypeChecker,PyArgumentList,PyCallByClass
        return QCoreApplication.translate('citygen', message)

    def add_action(
            self,
            icon_path,
            text,
            callback,
            enabled_flag=True,
            add_to_menu=True,
            add_to_toolbar=True,
            status_tip=None,
            whats_this=None,
            parent=None):
        """Add a toolbar icon to the toolbar.

        :param icon_path: Path to the icon for this action. Can be a resource
            path (e.g. ':/plugins/foo/bar.png') or a normal file system path.
        :type icon_path: str

        :param text: Text that should be shown in menu items for this action.
        :type text: str

        :param callback: Function to be called when the action is triggered.
        :type callback: function

        :param enabled_flag: A flag indicating if the action should be enabled
            by default. Defaults to True.
        :type enabled_flag: bool

        :param add_to_menu: Flag indicating whether the action should also
            be added to the menu. Defaults to True.
        :type add_to_menu: bool

        :param add_to_toolbar: Flag indicating whether the action should also
            be added to the toolbar. Defaults to True.
        :type add_to_toolbar: bool

        :param status_tip: Optional text to show in a popup when mouse pointer
            hovers over the action.
        :type status_tip: str

        :param parent: Parent widget for the new action. Defaults None.
        :type parent: QWidget

        :param whats_this: Optional text to show in the status bar when the
            mouse pointer hovers over the action.

        :returns: The action that was created. Note that the action is also
            added to self.actions list.
        :rtype: QAction
        """

        icon = QIcon(icon_path)
        action = QAction(icon, text, parent)
        action.triggered.connect(callback)
        action.setEnabled(enabled_flag)

        if status_tip is not None:
            action.setStatusTip(status_tip)

        if whats_this is not None:
            action.setWhatsThis(whats_this)

        if add_to_toolbar:
            # Adds plugin icon to Plugins toolbar
            self.iface.addToolBarIcon(action)

        if add_to_menu:
            self.iface.addPluginToMenu(
                self.menu,
                action)

        self.actions.append(action)

        return action

    def initGui(self):
        """Create the menu entries and toolbar icons inside the QGIS GUI."""

        icon_path = ':/plugins/citygen/icon.png'
        self.add_action(
            icon_path,
            text=self.tr(u'3D City Generator'),
            callback=self.run,
            parent=self.iface.mainWindow())

        # will be set False in run()
        self.first_start = True

    def unload(self):
        """Removes the plugin menu item and icon from QGIS GUI."""
        for action in self.actions:
            self.iface.removePluginMenu(
                self.tr(u'&citygen'),
                action)
            self.iface.removeToolBarIcon(action)

    def run(self):
        """Run method that performs all the real work"""

        # Create the dialog with elements (after translation) and keep reference
        # Only create GUI ONCE in callback, so that it will only load when the plugin is started
        if self.first_start == True:
            self.first_start = False
            self.dlg = citygenDialog()

        # Loading Vars
        appContext.qgis.iface = self.iface
        appContext.qgis.segf = self
        appContext.qgis.dlg = self.dlg

        layer_list = QgsProject.instance().layerTreeRoot().children()
        getter_list = plugin_management.get_list()

        self.dlg.cbxBuildingHeightMethod.clear()
        self.dlg.cbxBuildingHeightMethod.addItems([method["title"] for method in appContext.BUILDING_HEIGHT_METHODS])
        self.dlg.cbxBuildingHeightMethod.currentIndexChanged.connect(self.cbxBuildingHeightMethod_on_change)
        self.dlg.cbxBuildingHeightMethod.setCurrentIndex(1)
        self.cbxBuildingHeightMethod_on_change(1)

        # CmbClip
        self.dlg.cmbClip.currentIndexChanged.connect(self.cmbClip_on_change)
        self.dlg.cmbClip.clear()
        self.dlg.cmbClip.addItems(["Don't clip", "Use map viewport"] + [layer.name() for layer in layer_list])

        ### BEGIN Ortho ###
        appContext.plugins.getter_ortho_list = list(filter(lambda x: "ortho" in x["layer"], list(getter_list)))
        self.dlg.cbxOrthoSource.currentIndexChanged.connect(self.cbxOrthoSource_on_change)
        self.dlg.cbxOrthoLayer.currentIndexChanged.connect(self.cbxOrthoLayer_on_change)
        self.dlg.cbxOrthoSource.clear()
        self.dlg.cbxOrthoSource.addItems([plugin["name"] for plugin in appContext.plugins.getter_ortho_list])

        self.dlg.cbxOrthoLayer.clear()
        self.dlg.cbxOrthoLayer.addItems([layer.name() for layer in layer_list])

        self.cbxOrthoSource_on_change(0)
        ### END Ortho ###

        ### BEGIN DTM ###
        appContext.plugins.getter_dtm_list = list(filter(lambda x: "dtm" in x["layer"], list(getter_list)))
        self.dlg.cbxDTMSource.currentIndexChanged.connect(self.cbxDTMSource_on_change)
        self.dlg.cbxDTMLayer.currentIndexChanged.connect(self.cbxDTMLayer_on_change)
        self.dlg.cbxDTMSource.clear()
        self.dlg.cbxDTMSource.addItems([plugin["name"] for plugin in appContext.plugins.getter_dtm_list])

        self.dlg.cbxDTMLayer.clear()
        self.dlg.cbxDTMLayer.addItems([layer.name() for layer in layer_list])

        self.cbxDTMSource_on_change(0)
        ### END DTM ###

        ### BEGIN DSM ###
        appContext.plugins.getter_dsm_list = list(filter(lambda x: "dsm" in x["layer"], list(getter_list)))
        self.dlg.cbxDSMSource.currentIndexChanged.connect(self.cbxDSMSource_on_change)
        self.dlg.cbxDSMLayer.currentIndexChanged.connect(self.cbxDSMLayer_on_change)
        self.dlg.cbxDSMSource.clear()
        self.dlg.cbxDSMSource.addItems([plugin["name"] for plugin in appContext.plugins.getter_dsm_list])

        self.dlg.cbxDSMLayer.clear()
        self.dlg.cbxDSMLayer.addItems([layer.name() for layer in layer_list])

        self.cbxDSMSource_on_change(0)
        ### END DSM ###

        ### BEGIN Footprint ###
        appContext.plugins.getter_footprint_list = list(filter(lambda x: "footprint" in x["layer"], list(getter_list)))
        self.dlg.cbxFootprintSource.currentIndexChanged.connect(self.cbxFootprintSource_on_change)
        self.dlg.cbxFootprintLayer.currentIndexChanged.connect(self.cbxFootprintLayer_on_change)
        self.dlg.cbxFootprintSource.clear()
        self.dlg.cbxFootprintSource.addItems([plugin["name"] for plugin in appContext.plugins.getter_footprint_list])

        self.dlg.cbxFootprintLayer.clear()
        self.dlg.cbxFootprintLayer.addItems([layer.name() for layer in layer_list])

        self.cbxFootprintSource_on_change(0)
        ### END Footprint ###

        self.dlg.btnRun.clicked.connect(self.on_run)
        self.dlg.btnCancel.clicked.connect(self.on_cancel)
        self.dlg.btnTest.clicked.connect(self.on_test)
        self.dlg.btnClear.clicked.connect(self.on_clear)
        self.dlg.btnFixCRS.clicked.connect(self.on_fixCRS)
        self.dlg.btnOrthoSateTo.clicked.connect(self.btnOrthoSateTo_on_click)
        self.dlg.btnDTMSateTo.clicked.connect(self.btnDTMSateTo_on_click)
        self.dlg.btnDSMSateTo.clicked.connect(self.btnDSMSateTo_on_click)
        self.dlg.btnFootprintSateTo.clicked.connect(self.btnFootprintSateTo_on_click)

        # show the dialog
        self.dlg.show()
        # Run the dialog event loop
        result = self.dlg.exec_()
        # See if OK was pressed
        if result:
            pass

    def on_run(self):
        logger.general_log("clicked on_run")
        self.dlg.tabMain.setCurrentIndex(2)


        appContext.user_parameters.ortho_output = self.dlg.edtOrthoSateTo.text()
        appContext.user_parameters.dtm_output = self.dlg.edtDTMSateTo.text()
        appContext.user_parameters.dsm_output = self.dlg.edtDSMSateTo.text()
        appContext.user_parameters.footprint_output = self.dlg.edtFootprintSateTo.text()

        start()
        self.dlg.btnCancel.setText("Close")
        self.dlg.btnRun.setText("Run again")
        self.iface.messageBar().pushMessage("Success", "Concluded without errors!", level=Qgis.Success, duration=3)

    def on_cancel(self):
        self.dlg.close()

    def on_test(self):
        logger.general_log("clicked on_test")

    def on_clear(self):
        logger.general_log("clicked on_clear")
        self.dlg.txtLog.setText("")

    def on_fixCRS(self):
        my_crs = QgsCoordinateReferenceSystem("EPSG:3395")
        QgsProject.instance().setCrs(my_crs)

    def select_output_file(self, extension="Images (*.tif)"):
        filename, _filter = QFileDialog.getSaveFileName(
            self.dlg, "Select output file ", "", extension)
        return filename

    def cbxBuildingHeightMethod_on_change(self, selected_index):
        for index, method in enumerate(appContext.BUILDING_HEIGHT_METHODS):
            if index == selected_index:
                appContext.user_parameters.building_height_method = method

    ## cmbClip ##
    def cmbClip_on_change(self, selected_index):
        if selected_index == 0:
            appContext.user_parameters.clip_layer = None
        elif selected_index == 1:
            appContext.user_parameters.clip_layer = "viewport"
        else:
            appContext.user_parameters.clip_layer = QgsProject.instance().layerTreeRoot().children()[
                selected_index - 2].layer()

    ## BEGIN Ortho ##
    def get_first_layer_by_name(self, layer_name, default=0):
        for index, i in enumerate(QgsProject.instance().layerTreeRoot().children()):
            if layer_name in i.layer().name().lower():
                return index
        return default

    def cbxOrthoSource_on_change(self, selected_index):
        appContext.user_parameters.ortho_getter = appContext.plugins.getter_ortho_list[selected_index]

        self.dlg.frmOrthoLayer.setVisible(appContext.user_parameters.ortho_getter.format == "layer")
        self.dlg.frmOrthoSateTo.setVisible(appContext.user_parameters.ortho_getter.format == "file")

        self.dlg.cbxOrthoLayer.setCurrentIndex(self.get_first_layer_by_name("ortho", 0))

    def cbxOrthoLayer_on_change(self, selected_index):
        appContext.user_parameters.ortho_input = QgsProject.instance().layerTreeRoot().children()[
            selected_index].layer()

    def btnOrthoSateTo_on_click(self):
        filename = self.select_output_file()
        self.dlg.edtOrthoSateTo.setText(filename)

    ## END Ortho ##

    ## BEGIN DTM ##
    def cbxDTMSource_on_change(self, selected_index):
        appContext.user_parameters.dtm_getter = appContext.plugins.getter_dtm_list[selected_index]
        self.dlg.frmDTMLayer.setVisible(appContext.user_parameters.dtm_getter.format == "layer")
        self.dlg.frmDTMSateTo.setVisible(appContext.user_parameters.dtm_getter.format == "file")

        self.dlg.cbxDTMLayer.setCurrentIndex(self.get_first_layer_by_name("dtm", 0))

    def cbxDTMLayer_on_change(self, selected_index):
        appContext.user_parameters.dtm_input = QgsProject.instance().layerTreeRoot().children()[
            selected_index].layer()

    def btnDTMSateTo_on_click(self):
        filename = self.select_output_file()
        self.dlg.edtDTMSateTo.setText(filename)

    ## END DTM ##

    ## BEGIN DSM ##
    def cbxDSMSource_on_change(self, selected_index):
        appContext.user_parameters.dsm_getter = appContext.plugins.getter_dsm_list[selected_index]
        self.dlg.frmDSMLayer.setVisible(appContext.user_parameters.dsm_getter.format == "layer")
        self.dlg.frmDSMSateTo.setVisible(appContext.user_parameters.dsm_getter.format == "file")

        self.dlg.cbxDSMLayer.setCurrentIndex(self.get_first_layer_by_name("dsm", 0))

    def cbxDSMLayer_on_change(self, selected_index):
        appContext.user_parameters.dsm_input = QgsProject.instance().layerTreeRoot().children()[
            selected_index].layer()

    def btnDSMSateTo_on_click(self):
        filename = self.select_output_file()
        self.dlg.edtDSMSateTo.setText(filename)

    ## END DSM ##

    ## BEGIN Footprint ##
    def cbxFootprintSource_on_change(self, selected_index):
        appContext.user_parameters.footprint_getter = appContext.plugins.getter_footprint_list[selected_index]

        self.dlg.frmFootprintLayer.setVisible(appContext.user_parameters.footprint_getter.format == "layer")
        self.dlg.frmFootprintSateTo.setVisible(appContext.user_parameters.footprint_getter.format in ["file", "algorithm"])

        self.dlg.cbxFootprintLayer.setCurrentIndex(self.get_first_layer_by_name("footprint", 0))

    def cbxFootprintLayer_on_change(self, selected_index):
        appContext.user_parameters.footprint_input = QgsProject.instance().layerTreeRoot().children()[
            selected_index].layer()

    def btnFootprintSateTo_on_click(self):
        filename = self.select_output_file("ShapeFil (*.shp)")
        self.dlg.edtFootprintSateTo.setText(filename)

    def cbxFootprintAlgorithm_on_change(self, selected_index):
        appContext.user_parameters.footprint_input = QgsProject.instance().layerTreeRoot().children()[
            selected_index].layer()

    ## END Footprint ##
