import os, processing
from qgis.core import QgsProcessingUtils, QgsRasterLayer, QgsProject


def configure(appResources, appContext):
    pass


def execute(appResources, appContext):
    print(os.path)

    appResources.bibliotecas.logger.update_progress(step_current=1, step_maximum=5)
    raw_folder = f"{appContext.execution.raw_temp_folder}/dtm"
    appResources.bibliotecas.file_management.create_dirs(raw_folder)

    appResources.bibliotecas.logger.update_progress(step_description="Downloading DTM...")
    
    region_list = [
        # "22_4",
        # "32_2",
        # "32_4",
        # "42_2",
        # "42_4",
        # "23_3",
        # "33_1",
        # "33_3",
        # "43_1",
        # "43_3",
        # "53_1",
        # "53_3",
        # "23_4",
        # "33_2",
        # "33_4",
        # "43_2",
        # "43_4",
        # "53_2",
        # "53_4",
        # "24_1",
        # "24_3",
        # "34_1",
        # "34_3",
        # "44_1",
        # "44_3",
        # "54_1",
        # "54_3",
        # "24_2",
        # "24_4",
        # "34_2",
        # "34_4",
        # "44_2",
        # "44_4",
        # "54_2",
        # "54_4",
        # "15_3",
        # "25_1",
        # "25_3",
        # "35_1",
        # "35_3",
        # "45_1",
        # "45_3",
        # "55_1",
        # "55_3",
        # "15_1",
        # "15_4",
        # "25_2",
        # "25_4",
        # "35_2",
        # "35_4",
        # "45_2",
        # "45_4",
        # "55_2",
        # "55_4",
        # "16_1",
        # "16_3",
        # "26_1",
        # "26_3",
        # "36_1",
        # "36_3",
        # "46_1",
        # "46_3",
        # "56_1",
        # "56_3",
        # "16_2",
        # "16_4",
        # "26_2",
        # "26_4",
        # "36_2",
        # "36_4",
        # "46_2",
        # "46_4",
        # "56_2",
        # "56_4",
        # "17_3",
        # "27_1",
        # "27_3",
        # "37_1",
        # "37_3",
        # "47_1",
        # "47_3",
        # "57_1",
        # "17_4",
        # "27_2",
        # "27_4",
        # "37_2",
        # "37_4",
        # "47_2",
        # "47_4",
        # "57_2",
        # "28_3",
        # "38_1",
        # "38_3",
        # "48_1",
        # "48_3",
        # "58_1",
        # "48_4",
        # "58_2"

        ### TEST ###
        "25_4",
        "26_3",
        "35_4",
        "36_1",
        "36_4",
        "36_2",
        "35_2",
        "36_3",
        "26_4",
    ]

    url_list = []
    zip_file_list = []
    destination_list = []
    tiff_list = []
    tiff_epsg_list = []
    for region in region_list:
        url_list.append(f"https://www.wien.gv.at/ma41datenviewer/downloads/ma41/geodaten/dgm_tif/{region}_dgm_tif.zip")
        zip_file_list.append(f"{raw_folder}/dtm_{region}.zip")
        destination_list.append(f"{appContext.execution.raw_temp_folder}/dtm/")
        tiff_list.append(f"/Users/arthurrufhosangdacosta/qgis_data/temp/dtm/{region}_dgm.tif")
        tiff_epsg_list.append(f"/Users/arthurrufhosangdacosta/qgis_data/temp/dtm/{region}_dgm_epsg.tif")

    # appResources.bibliotecas.internet.download_file_list(url_list, zip_file_list)

    # NORMALIZING
    # appResources.bibliotecas.logger.update_progress(step_description="Uncompromising...")
    # appResources.bibliotecas.file_management.unzip_file_list(zip_file_list, destination_list)

    for index, layer_path in enumerate(tiff_list):
        output = tiff_epsg_list[index]

        processing.run(
            "gdal:warpreproject",
            {
                'INPUT': layer_path,
                'SOURCE_CRS': appResources.qgis.core.QgsCoordinateReferenceSystem('EPSG:31256'),
                'TARGET_CRS': appResources.qgis.core.QgsCoordinateReferenceSystem('EPSG:4326'),
                'RESAMPLING': 0,
                'NODATA': None,
                'TARGET_RESOLUTION': None,
                'OPTIONS': '',
                'DATA_TYPE': 0,
                'TARGET_EXTENT': None,
                'TARGET_EXTENT_CRS': None,
                'MULTITHREADING': False,
                'EXTRA': '',
                'OUTPUT': output
            }
        )

    result = f"{appContext.execution.raw_temp_folder}/dtm/dtm.tif"
    result = f"/Users/arthurrufhosangdacosta/qgis_data/temp/dtm/dtm.tif"
    processing.run(
        "gdal:merge",
        {
            'INPUT': tiff_epsg_list,
            'PCT': False,
            'SEPARATE': False,
            'NODATA_INPUT': None,
            'NODATA_OUTPUT': None,
            'OPTIONS': '',
            'DATA_TYPE': 5,
            'OUTPUT': result
        }
    )

    appContext.update_layer(
        appContext,
        result,
        "dtm",
        "gdal",
        "raster",
        4326
    )
    # QgsProject.instance().addMapLayer(appContext.layers.dtm.layer)

    appResources.bibliotecas.logger.update_progress(step_current=1, step_maximum=1)
    appResources.bibliotecas.logger.plugin_log("Done!")
