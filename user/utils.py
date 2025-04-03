import pikepdf
from django.core.files.base import ContentFile
from io import BytesIO

def compress_pdf(file):
    """
    Compress a PDF file using pikepdf.
    :param file: Uploaded PDF file
    :return: Compressed PDF file
    """
    try:
        # Read the uploaded PDF file
        input_pdf = BytesIO(file.read())
        output_pdf = BytesIO()

        # Compress the PDF using pikepdf
        with pikepdf.open(input_pdf) as pdf:
            pdf.save(output_pdf, optimize_image=True)

        # Return the compressed PDF as a Django ContentFile
        return ContentFile(output_pdf.getvalue(), name=file.name)
    except Exception as e:
        print(f"Error compressing PDF: {e}")
        return file  # Return the original file if compression fails