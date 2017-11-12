from wand.image import Image
from PIL import Image as PI
import pyocr
import pyocr.builders
import io
import glob, os

def get_ocr(file):
	print(file.name)
	tool = pyocr.get_available_tools()[0]
	lang = tool.get_available_languages()[0]

	req_image = []
	final_text = []
	# image_pdf = Image(filename="./"+file, resolution=300)
	# imagem_jpeg = image_pdf.convert('jpeg')

	image_pdf = Image(filename=file)
	imagem_jpeg = image_pdf.convert('jpeg')

	for img in imagem_jpeg.sequence:
		img_page = Image(image=img)
		req_image.append(img_page.make_blob('jpeg'))

	for img in req_image:
		txt = tool.image_to_string(
			PI.open(io.BytesIO(img)),
			lang=lang,
			builder=pyocr.builders.TextBuilder()
			)
		final_text.append(txt)
	return final_text