from docling.document_converter import DocumentConverter
from docling.datamodel.base_models import InputFormat
import os
from utils.helper_file import HelperFile
from config.config_file import Config


class DataExtAndRenderingService:
    Config.makeDirectories("rawDataDir")

    @staticmethod
    async def anyThingButJSOrSPA(source: str) -> str:
        converter = DocumentConverter()
        result = converter.convert(source)
        return result.document.export_to_markdown()

    @staticmethod
    async def websiteDataExtrationJs(source: str) -> str:
        rendered_html = await HelperFile.get_dynamic_html(source)
        converter = DocumentConverter()
        result = converter.convert_string(rendered_html, InputFormat.HTML)
        return result.document.export_to_markdown()
