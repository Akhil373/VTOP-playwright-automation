import re
import os
import base64
import traceback
from PIL import Image
from google import genai
from google.genai.types import GenerateContentResponse
from transformers import VisionEncoderDecoderModel, TrOCRProcessor
import numpy as np

def isolate_red(img):
    img = img.convert("RGB")
    a = np.array(img)
    r, g, b = a[:, :, 0], a[:, :, 1], a[:, :, 2]
    mask = (r > 50) & (g < 150) & (b < 150) 
    bw = np.full(a.shape[:2], 255, dtype=np.uint8)
    bw[mask] = 0
    return Image.fromarray(bw, mode='L')

def solve_captcha_with_gemini(image_path: str) -> str:
    print("Trying to solve captcha...")

    img = Image.open(image_path)
    img = isolate_red(img)
    img.show()

    client: genai.client.Client = genai.Client()
    img: Image.Image = Image.open(image_path)
    prompt = "You are an OCR engine. Extract the uppercase letters (A-Z) and numbers (0-9) from the following CAPTCHA image.Provide ONLY the characters with no explanation."
    result: GenerateContentResponse = client.models.generate_content(
        model="gemini-2.5-flash",
        contents=[
            prompt,
            img,
            "\n\n",
            'Output: ',
        ],
    )
    print(result)
    return result.text if result.text is not None else ""

def debug_solve_local(image_path: str) -> str:
    print("--- Starting Local Solver ---")
    try:
        print(f"1. Attempting to open image at: '{image_path}'")
        image = Image.open(image_path).convert("RGBA")
        print("   - Image opened successfully.")

        print("2. Loading TrOCR processor from Hugging Face...")
        processor = TrOCRProcessor.from_pretrained("anuashok/ocr-captcha-v3", use_fast=True)
        print("   - Processor loaded.")

        print("3. Loading VisionEncoderDecoder model from Hugging Face...")
        model = VisionEncoderDecoderModel.from_pretrained("anuashok/ocr-captcha-v3")
        print("   - Model loaded.")

        print("4. Preparing image for the model...")
        background = Image.new("RGBA", image.size, (255, 255, 255))
        combined = Image.alpha_composite(background, image).convert("RGB")
        pixel_values = processor(combined, return_tensors="pt").pixel_values
        print("   - Image prepared.")

        print("5. Running model inference to generate text...")
        generated_ids = model.generate(pixel_values)
        print("   - Inference complete.")

        print("6. Decoding the result...")
        generated_text = processor.batch_decode(generated_ids, skip_special_tokens=True)[0]
        print("   - Decoding complete.")
        
        return generated_text

    except FileNotFoundError:
        print(f"ERROR: The file was not found at '{image_path}'")
        print("Please make sure the file exists and the path is correct.")
        return ""
    except Exception as e:
        print(f"AN UNEXPECTED ERROR OCCURRED: {e} !!!")
        traceback.print_exc()
        return ""

def solve_with_retry(file_path) -> str: 
    solved_captcha_raw = solve_captcha_with_gemini(file_path)
    input_str: str = solved_captcha_raw.upper()
    if re.fullmatch(r'^[A-Z0-9]{6}$', input_str):
        print(f"Valid CAPTCHA format found: {input_str}")
        return input_str 
    print(f"\nFailed to solve the CAPTCHA with LLM. Trying with OCR...")
    solved_captcha_raw: str = debug_solve_local(file_path)
    return input_str

def get_captcha_and_solve(uri: str | None) -> str | None: 
    if uri is None: 
        return
    header, encoded_data = uri.split(",", 1)
    image_data: bytes = base64.b64decode(encoded_data)
    print("Successfully decoded Base64 image data.")
    file_path = os.path.join("temp", "captcha.jpg")
    with open(file_path, "wb") as f:
        f.write(image_data)
    print(f"CAPTCHA image saved to {file_path}")
    solved_captcha: str = solve_with_retry(file_path)
    return solved_captcha
