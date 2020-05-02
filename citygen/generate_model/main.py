import sys, os, random, string
from qgis.core import QgsProcessingUtils, QgsRasterLayer, QgsProject
from .bibliotecas import logger, file_menagement
from .appCtx import appContext

from .crawler import crawler_management
from .gis import gis


# def cleanup_temp():
#     os.rmdir("temp")
#
#     os.mkdir("temp")
#
#     os.mkdir("temp/raw")
#     os.mkdir("temp/raw/ortho")
#     os.mkdir("temp/raw/dtm")
#     os.mkdir("temp/raw/dsm")
#
#     os.mkdir("temp/normalized")
#     os.mkdir("temp/normalized/ortho")
#     os.mkdir("temp/normalized/dtm")
#     os.mkdir("temp/normalized/dsm")

def appContext_setup():
    logger.update_progress(step_current=0, step_description="Loading...", step_maximum=100,
                           overall_current=1, overall_description="Initialization", overall_maximum=100)

    appContext.execution.id = ''.join(random.choices(string.ascii_letters + string.digits, k=16))
    temp_folder = QgsProcessingUtils.tempFolder()
    appContext.execution.temp_folder = f"{temp_folder}/{appContext.execution.id}"
    appContext.execution.raw_temp_folder = f"{appContext.execution.temp_folder}/raw"
    appContext.execution.normalized_temp_folder = f"{appContext.execution.temp_folder}/normalized"

    file_menagement.create_dirs(appContext.execution.temp_folder)
    file_menagement.create_dirs(appContext.execution.raw_temp_folder)
    file_menagement.create_dirs(appContext.execution.normalized_temp_folder)

    logger.plugin_log(f"Plugin Temp folder: {appContext.execution.temp_folder}")

    logger.update_progress(step_current=100, overall_current=2)


def start():
    appContext_setup()

    logger.plugin_log("Getting files...")
    crawler_management.execute_crawlers()

    gis.generate_3d_model()
    logger.plugin_log("Process complete without errors!")

    logger.update_progress(step_current=100, step_description="Done!", step_maximum=100,
                           overall_current=100, overall_description="", overall_maximum=100)
