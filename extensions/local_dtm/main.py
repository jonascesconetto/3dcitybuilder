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


def configure(appResources, appContext):
    pass


def execute(appResources, appContext):
    appContext.update_layer_with_loaded(
        appContext,
        appContext.user_parameters.dtm_input,
        "dtm"
    )
