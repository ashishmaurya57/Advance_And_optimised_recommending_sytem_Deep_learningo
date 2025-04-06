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

# from .models import ProductInteraction, product

# def handle_like_dislike(user, product_id, action):
#     product_instance = product.objects.get(id=product_id)
#     interaction, created = ProductInteraction.objects.get_or_create(user=user, product=product_instance)

#     if action == "like":
#         if not interaction.liked:
#             interaction.liked = True
#             interaction.disliked = False
#             product_instance.likes += 1
#             if not created and interaction.disliked:
#                 product_instance.dislikes -= 1
#     elif action == "dislike":
#         if not interaction.disliked:
#             interaction.disliked = True
#             interaction.liked = False
#             product_instance.dislikes += 1
#             if not created and interaction.liked:
#                 product_instance.likes -= 1

#     interaction.save()
#     product_instance.save()    

