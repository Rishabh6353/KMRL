try:
    import fitz
    print('PyMuPDF is installed - Version:', fitz.__version__)
except ImportError as e:
    print('PyMuPDF is NOT installed:', e)