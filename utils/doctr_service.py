import threading
from doctr.io import DocumentFile
from doctr.models import ocr_predictor

class DoctrOCRService:
    """
    Singleton OCR service to avoid loading the model multiple times.
    Production safe for Django workers.
    """

    _instance = None
    _lock = threading.Lock()

    def __init__(self):
        self.model = ocr_predictor(pretrained=True)

    @classmethod
    def get_instance(cls):
        if cls._instance is None:
            with cls._lock:
                if cls._instance is None:
                    cls._instance = cls()
        return cls._instance

    def process_document(self, file_path: str):
        """
        Process PDF or image file and return doctr result object.
        """

        if file_path.lower().endswith(".pdf"):
            doc = DocumentFile.from_pdf(file_path)
        else:
            doc = DocumentFile.from_images(file_path)

        result = self.model(doc)
        return result