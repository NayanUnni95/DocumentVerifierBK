from .doctr_service import DoctrOCRService


def doctr_to_text(result):
    """
    Converts doctr result to structured dictionary.
    """
    return result.export()


def doctr_to_plain_text(result):
    """
    Converts doctr result to plain text.
    """
    text = ""
    for page in result.pages:
        for block in page.blocks:
            for line in block.lines:
                for word in line.words:
                    text += word.value + " "
                text += "\n"
            text += "\n"
    return text.strip()


def extract_document_text(file_path: str, structured: bool = False):
    """
    Main utility function for OCR extraction.

    Args:
        file_path: path to document
        structured: return layout json instead of plain text

    Returns:
        extracted data
    """

    ocr_service = DoctrOCRService.get_instance()

    result = ocr_service.process_document(file_path)

    if structured:
        return doctr_to_text(result)

    return doctr_to_plain_text(result)