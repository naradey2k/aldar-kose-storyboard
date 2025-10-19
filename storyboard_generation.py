import json
import os
from PIL import Image
from IPython.display import Image as IPImage, display
from tqdm import tqdm
from google import genai
from PIL import Image
from io import BytesIO
import os

os.environ["GEMINI_API_KEY"] = ""
client = genai.Client()

ref_image = Image.open('/Users/danialsultanov/Coding Projects/higgsfield/ref_images/1.png')

def generate_images_from_json(json_path="index.json"):

    with open(json_path, "r", encoding="utf-8") as f:
        scenes = json.load(f)
    print(f"🎞 {len(scenes)} frames loaded.\n")

    for scene in tqdm(scenes, desc="🎨 Generating frames"):
        sid = scene.get("scene_id", 0)
        caption = scene.get("caption", "")
        prompt = scene.get("prompt", "")
        neg = scene.get("neg", "low quality, inconsistent, cartoon, blur")  

        if sid == 1:
            text_input = """Use the provided image of a Aldar Kose as reference image how my character must and only look like. Generate """ + prompt
            response = client.models.generate_content(
                model="gemini-2.5-flash-image",
                contents=[text_input, ref_image],
            )
        else:
            ctx = Image.open(f"results/frame_{sid -1:02}.png")
            text_input = f"""Use the provided image as a context of what happened in previous scene. Generate """ + prompt
            response = client.models.generate_content(
                model="gemini-2.5-flash-image",
                contents=[text_input, ctx],
            )


        image_parts = [
            part.inline_data.data
            for part in response.candidates[0].content.parts
            if part.inline_data
        ]

        path = f"results/frame_{sid:02}.png"
        
        if image_parts:
            image = Image.open(BytesIO(image_parts[0]))
            image.save(path)
            image.show()

        print(f"✅ Saved: {path} — {caption}")
        

    print("\n🎉 All frames generated successfully! Saved in /outputs/")

    for i in range(1, len(scenes) + 1):
        display(IPImage(filename=f"results/frame_{i:02}.png"))

if __name__ == "__main__":
    generate_images_from_json("index.json")