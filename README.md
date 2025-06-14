# 🛍️ QR Code Generator for Item Pricing
## Meant for small business.
A simple desktop application for generating printable QR codes that encode item details for selling goods. Built with Python and Tkinter, this app allows users to easily manage, view, and print item labels — complete with item name, unique ID, and price.
More features may be available in the future. 

Disclaimer: Despite the name containing POS this is not a Point-of-sale program.
If you want to extend it's functionality, I encourage you to do so and submit pull requests
✨ Features
- Generate unique QR codes for items

Interactive UI:

- Item UID (configurable starting number)

- Item Name

- Item Price

View and manage generated QR codes in the UI

Delete individual QR codes and related data

Print selected QR code labels directly

Automatically saves QR codes and item info in text and image format

🧰 Tech Stack

- Python 3

- Tkinter (GUI)

- Pillow (Image handling)

- qrcode (QR code generation)

🚀 Usage

1. Run the app with:

python app.py
or run the included setupandrun.bat file to automate the process

2. Enter item name and price, then click Generate.

Use the UI to:

- View or print any generated QR code

- Delete individual items

- Search items by UID

📦 Build Instructions

- To create an .exe manually:

- pyinstaller --onefile --windowed --icon=app.ico app.py

- Or use the included build.bat.

📁 Output

- QR codes saved as .png in the qrcodes folder.
- QR codes contain the item UID# in the image (useful for printing)

- Item data saved to items.json.
