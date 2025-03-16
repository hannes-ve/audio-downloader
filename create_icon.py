from PIL import Image, ImageDraw
import os

# Check if Pillow is installed
try:
    from PIL import Image
except ImportError:
    print("Pillow is not installed. Installing...")
    os.system("pip install pillow")
    from PIL import Image

# Create a simple icon
def create_icon():
    # Create a 256x256 image with a transparent background
    img = Image.new('RGBA', (256, 256), color=(0, 0, 0, 0))
    draw = ImageDraw.Draw(img)
    
    # Draw a blue circle
    draw.ellipse((20, 20, 236, 236), fill=(65, 105, 225, 255))
    
    # Draw a white sound wave symbol
    for i in range(3):
        # Draw arcs with increasing radius
        radius = 40 + i * 30
        x1, y1 = 128 - radius, 128 - radius
        x2, y2 = 128 + radius, 128 + radius
        draw.arc((x1, y1, x2, y2), start=300, end=60, fill=(255, 255, 255, 255), width=10)
    
    # Draw a white triangle (play button)
    draw.polygon([(90, 90), (90, 166), (166, 128)], fill=(255, 255, 255, 255))
    
    # Save as .ico file
    img.save('icon.ico', format='ICO')
    print("Icon created successfully: icon.ico")

if __name__ == "__main__":
    create_icon() 