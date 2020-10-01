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
        copyright            : (C) 2020 by Arthur Ruf Hosang da Costa (https://github.com/arthurRuf)
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


import time, shutil, os, sys, requests
from qgis.core import QgsRasterLayer


def configure(appResources, appContext):
    pass


def execute(appResources, appContext):
    # WMS Server: https://maps.wien.gv.at/wmts/1.0.0/WMTSCapabilities-arcmap.xml

    appContext.update_layer(
        appContext,
        'crs=EPSG:3857&dpiMode=7&format=image/jpeg&layers=lb&styles=farbe&tileMatrixSet=google3857&url=http://sigsc.sc.gov.br/sigserver/gwc/service/wmts',
        "ortho",
        "wms"
    )

    appResources.bibliotecas.logger.update_progress(step_current=1, step_maximum=1)
    appResources.bibliotecas.logger.plugin_log("Done!")
