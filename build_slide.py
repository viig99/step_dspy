import subprocess
from PIL import Image, ImageDraw, ImageFont
import os


def create_slide(image_path, title, main_text, output_path):
    # Open the image
    img = Image.open(image_path)

    # Create a drawing object
    draw = ImageDraw.Draw(img)

    # Use default font
    title_font = ImageFont.load_default().font_variant(size=36)
    main_font = ImageFont.load_default().font_variant(size=28)

    # Create semi-transparent rectangle
    rectangle_height = int(img.height * 0.25)
    # draw.rectangle(
    #    [(0, 0), (img.width, rectangle_height)], fill=(0, 0, 0, 120)
    # )  # Reduced alpha value for more translucency

    # Add title
    draw.text((img.width / 2, 20), title, font=title_font, fill="black", anchor="mt")

    # Add main text (word wrap)
    lines = []
    words = main_text.split()
    current_line = words[0]
    for word in words[1:]:
        bbox = draw.textbbox((0, 0), current_line + " " + word, font=main_font)
        if bbox[2] - bbox[0] <= img.width - 20:
            current_line += " " + word
        else:
            lines.append(current_line)
            current_line = word
    lines.append(current_line)

    y_text = 70
    for line in lines:
        draw.text(
            (img.width / 2, y_text), line, font=main_font, fill="black", anchor="mt"
        )
        y_text += 30

    # Save the image
    img.save(output_path)


def create_gif(image_paths, titles, main_texts, output_gif_path):
    images = []

    for i, (image_path, title, main_text) in enumerate(
        zip(image_paths, titles, main_texts)
    ):
        output_path = f"temp_slide_{i}.png"
        create_slide(image_path, title, main_text, output_path)
        images.append(Image.open(output_path))

    # Save the gif
    images[0].save(
        output_gif_path, save_all=True, append_images=images[1:], duration=5000, loop=0
    )

    # Clean up temporary files
    for i in range(len(images)):
        os.remove(f"temp_slide_{i}.png")


# Define your image paths, titles, and main texts
image_paths = [
    "Step 0.png",
    "Step 1.png",
    "Step 2.png",
    "Step 3.png",
    "Step 4.png",
    "Step 5.png",
]
titles = ["Step 0", "Step 1", "Step 2", "Step 3", "Step 4", "Step 5"]
main_texts = [
    "Starting state with the goal of 'Measure distance between CVS (closest one) and UPMC Shadyside by walking'",
    "Agent figures to get to the distance between 2 points view",
    "Agent adds in the 'from' section",
    "Agent adds in the 'to' section",
    "Agent selects the Foot (OSRM) option for getting the walking distance",
    "Agent find the distances from the html and logs the result",
]

# Create the gif
create_gif(image_paths, titles, main_texts, "output.gif")

if os.path.exists("output.mp4"):
    os.remove("output.mp4")
# Correct command setup
command = [
    "ffmpeg",
    "-i",
    "output.gif",
    "-movflags",
    "faststart",
    "-pix_fmt",
    "yuv420p",
    "-vf",
    "scale=if(gt(a\\,1)\\,trunc(iw/2)*2\\,trunc(ih/2)*2):if(gt(a\\,1)\\,trunc(ih/2)*2\\,trunc(iw/2)*2)",
    "output.mp4",
]

subprocess.run(command)
