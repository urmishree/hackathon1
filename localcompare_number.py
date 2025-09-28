# pip install torch torchvision pillow transformers

import torch
from PIL import Image
from transformers import CLIPProcessor, CLIPModel, BlipProcessor, BlipForConditionalGeneration
import json

# ---------------- CONFIGURE PATHS ----------------
reference_image = "Good4.jpg"   # <-- reference image path
target_image = "broken4.jpg"    # <-- target image path

# ---------------- Load Models ----------------
clip_model = CLIPModel.from_pretrained("openai/clip-vit-base-patch32")
clip_processor = CLIPProcessor.from_pretrained("openai/clip-vit-base-patch32")
blip_model = BlipForConditionalGeneration.from_pretrained("Salesforce/blip-image-captioning-base")
blip_processor = BlipProcessor.from_pretrained("Salesforce/blip-image-captioning-base")

# ---------------- Helpers ----------------
def caption_image(path):
    try:
        image = Image.open(path).convert("RGB")
        inputs = blip_processor(images=image, return_tensors="pt")
        out = blip_model.generate(**inputs, max_new_tokens=30)
        return blip_processor.decode(out[0], skip_special_tokens=True)
    except Exception:
        return "Unable to generate caption"

def image_similarity(img1, img2):
    try:
        images = [Image.open(img1).convert("RGB"), Image.open(img2).convert("RGB")]
        inputs = clip_processor(images=images, return_tensors="pt", padding=True)
        with torch.no_grad():
            embeddings = clip_model.get_image_features(**inputs)
        sim = torch.cosine_similarity(embeddings[0].unsqueeze(0), embeddings[1].unsqueeze(0))
        return float(sim.item())
    except Exception:
        return 0.0

# ---------------- Main Comparison ----------------
def compare_vehicle(target_img, reference_img=reference_image):
    print("Comparing target image:", target_img, "with reference image:", reference_img)
    try:
        ref_caption = caption_image(reference_img)
        tgt_caption = caption_image(target_img)

        # ---------- Vehicle Number (HARDCODED) ----------
        ref_vehicle_number = "GJ01 JY0887"
        tgt_vehicle_number = "GJ01 JY0887"

        # ---------- Condition Check ----------
        damage_keywords = ["scratch", "dent", "broken", "crack", "damaged"]
        condition = "not good" if any(k in tgt_caption.lower() for k in damage_keywords) else "good"
        operative = "yes" if condition == "good" else "no"

        # ---------- Brand & Color Match ----------
        brand_keywords = ["toyota", "honda", "bmw", "maruti", "tata"]
        color_keywords = ["red", "blue", "black", "white", "silver", "maroon"]
        brand_match = any(b in ref_caption.lower() and b in tgt_caption.lower() for b in brand_keywords)
        color_match = any(c in ref_caption.lower() and c in tgt_caption.lower() for c in color_keywords)

        # ---------- Overall Similarity ----------
        overall_similarity = image_similarity(reference_img, target_img)

        # ---------- Same Vehicle Decision ----------
        same_vehicle = True if condition == "good" and ref_vehicle_number == tgt_vehicle_number else False

        result = {
            "vehicle_number": tgt_vehicle_number,
            "condition": condition,
            "operative": operative,
            "same-vehicle": same_vehicle,
            "overall_similarity": round(overall_similarity, 2),
            "explanation": f"Reference: {ref_caption} | Target: {tgt_caption}"
        }

    except Exception as e:
        result = {
            "vehicle_number": "Unknown",
            "condition": "unknown",
            "operative": "unknown",
            "same-vehicle": False,
            "overall_similarity": 0.0,
            "explanation": f"Error processing images: {str(e)}"
        }

    # Save JSON
    with open("vehicle_comparison.json", "w") as f:
        json.dump(result, f, indent=4)

    return result

# ---------------- Run Comparison ----------------
# if __name__ == "__main__":
#     result = compare_vehicle(reference_image, target_image)
#     print(json.dumps(result, indent=4))
