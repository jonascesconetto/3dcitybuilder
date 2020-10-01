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


import os, processing
from qgis.core import QgsProcessingUtils, QgsRasterLayer, QgsProject


def configure(appResources, appContext):
    pass


def execute(appResources, appContext):
    print(os.path)

    appResources.bibliotecas.logger.update_progress(step_current=1, step_maximum=5)
    raw_folder = f"{appContext.execution.raw_temp_folder}/footprint"
    appResources.bibliotecas.file_management.create_dirs(raw_folder)

    appResources.bibliotecas.logger.update_progress(step_description="Downloading Footprint...")

    zip_file_path = f"{raw_folder}/footprint.zip"

    # zip_file_path = f"/private/var/folders/6k/gwc2zlsd7tl7ph27q44pcm0w0000gn/T/processing_c9b8c5d3c16e439fb67a0bbb40d8904e/citygen/W6FSUo5EqeZuqURU/raw/footprint/footprint.zip"

    uncompressed_file_path = f"{raw_folder}"
    appResources.bibliotecas.internet.download_file("http://download.geofabrik.de/europe/austria-latest-free.shp.zip",
                                                    zip_file_path)

    # NORMALIZING
    appResources.bibliotecas.logger.update_progress(step_description="Uncompressing...")
    appResources.bibliotecas.file_management.unzip_file(zip_file_path, uncompressed_file_path)

    result = f"{uncompressed_file_path}/gis_osm_buildings_a_free_1.shp"

    appContext.update_layer(
        appContext,
        path=result,
        name="footprint",
        data_provider="ogr",
        type="vector",
        crs=4626
    )

    appResources.bibliotecas.logger.update_progress(step_current=1, step_maximum=1)
    appResources.bibliotecas.logger.plugin_log("Done!")
