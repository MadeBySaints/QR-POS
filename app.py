import tkinter as tk
from tkinter import messagebox, ttk
from PIL import Image, ImageTk
import qrcode
import json
import os
import subprocess
import sys

# --- CONFIG ---
CONFIG = {
    "next_uid": 1001001,
    "data_file": "items.json",
    "qr_output_dir": "qrcodes"
}

# --- SETUP ---
os.makedirs(CONFIG["qr_output_dir"], exist_ok=True)
if os.path.exists(CONFIG["data_file"]):
    with open(CONFIG["data_file"], "r") as f:
        items = json.load(f)
        if items:
            CONFIG["next_uid"] = max(int(i["uid"]) for i in items) + 1
else:
    items = []

# --- FUNCTIONS ---
def save_items():
    with open(CONFIG["data_file"], "w") as f:
        json.dump(items, f, indent=4)

def generate_qr():
    name = entry_name.get().strip()
    price = entry_price.get().strip()

    if not name or not price:
        messagebox.showwarning("Missing data", "Item name and price are required.")
        return

    try:
        price = float(price)
    except ValueError:
        messagebox.showerror("Invalid price", "Price must be a number.")
        return

    uid = str(CONFIG["next_uid"])
    CONFIG["next_uid"] += 1

    item_data = {
        "uid": uid,
        "name": name,
        "price": price
    }

    items.append(item_data)
    save_items()

    # Generate QR code
    qr = qrcode.QRCode(
        version=1,
        error_correction=qrcode.constants.ERROR_CORRECT_L,
        box_size=10,
        border=4,
    )
    qr.add_data(json.dumps(item_data))
    qr.make(fit=True)
    
    # Create the QR code image
    qr_img = qr.make_image(fill_color="black", back_color="white")
    qr_img = qr_img.convert("RGB")  # Ensure it's in RGB mode
    
    # Create a new image with space for text below QR code
    qr_width, qr_height = qr_img.size
    text_height = 30  # Space for text
    combined_img = Image.new("RGB", (qr_width, qr_height + text_height), "white")
    combined_img.paste(qr_img, (0, 0))
    
    # Add text (UID) below the QR code
    from PIL import ImageDraw, ImageFont
    draw = ImageDraw.Draw(combined_img)
    
    try:
        # Try to use a nice font if available
        font = ImageFont.truetype("arial.ttf", 16)
    except:
        # Fallback to default font
        font = ImageFont.load_default()
    
    text = f"UID: {uid}"
    text_width = draw.textlength(text, font=font)
    draw.text(((qr_width - text_width) // 2, qr_height + 5), text, font=font, fill="black")
    
    # Save the combined image
    qr_path = os.path.join(CONFIG["qr_output_dir"], f"{uid}.png")
    combined_img.save(qr_path)

    update_item_list()
    show_item(item_data)

    entry_name.delete(0, tk.END)
    entry_price.delete(0, tk.END)

def update_item_list(filtered_items=None):
    item_list.delete(*item_list.get_children())
    display_items = filtered_items if filtered_items is not None else items
    for item in reversed(display_items):
        item_list.insert("", "end", values=(item["uid"], item["name"], f"${item['price']:.2f}"))

def show_item(item_data):
    qr_path = os.path.join(CONFIG["qr_output_dir"], f"{item_data['uid']}.png")
    if os.path.exists(qr_path):
        img = Image.open(qr_path).resize((200, 200))
        img_tk = ImageTk.PhotoImage(img)
        qr_label.config(image=img_tk)
        qr_label.image = img_tk
    else:
        qr_label.config(image=blank_qr_image)
        qr_label.image = blank_qr_image

    text = f"UID: {item_data['uid']}\nName: {item_data['name']}\nPrice: ${item_data['price']:.2f}"
    item_info_box.config(state="normal")
    item_info_box.delete(1.0, tk.END)
    item_info_box.insert(tk.END, text)
    item_info_box.config(state="disabled")

def on_item_select(event):
    selected = item_list.focus()
    if not selected:
        return
    values = item_list.item(selected, 'values')
    uid = values[0]
    item = next((i for i in items if i["uid"] == uid), None)
    if item:
        show_item(item)

def delete_selected():
    selected_items = item_list.selection()  # Get all selected items
    if not selected_items:
        messagebox.showinfo("No selection", "Please select item(s) to delete.")
        return

    # Get all UIDs from selected items
    uids_to_delete = []
    for item in selected_items:
        values = item_list.item(item, 'values')
        uids_to_delete.append(values[0])

    if not messagebox.askyesno(
        "Confirm Delete", 
        f"Are you sure you want to delete {len(uids_to_delete)} item(s)?\n" +
        f"UIDs: {', '.join(uids_to_delete)}"
    ):
        return

    global items
    deleted_count = 0
    
    for uid in uids_to_delete:
        # Remove from items list
        items = [i for i in items if i["uid"] != uid]
        
        # Delete QR code file
        qr_path = os.path.join(CONFIG["qr_output_dir"], f"{uid}.png")
        try:
            if os.path.exists(qr_path):
                os.remove(qr_path)
                deleted_count += 1
        except Exception as e:
            messagebox.showerror("Delete Error", f"Could not delete QR code for UID {uid}:\n{e}")

    save_items()
    update_item_list()
    
    # Clear the display after deletion
    qr_label.config(image=blank_qr_image)
    qr_label.image = blank_qr_image
    item_info_box.config(state="normal")
    item_info_box.delete(1.0, tk.END)
    item_info_box.config(state="disabled")
    
    messagebox.showinfo(
        "Deletion Complete", 
        f"Successfully deleted {deleted_count} item(s)."
    )

def create_blank_image(size=(200, 200), color="white"):
    img = Image.new("RGB", size, color)
    return ImageTk.PhotoImage(img)

def print_selected():
    selected = item_list.focus()
    if not selected:
        messagebox.showinfo("No selection", "Please select an item to print.")
        return

    values = item_list.item(selected, 'values')
    uid = values[0]
    qr_path = os.path.abspath(os.path.join(CONFIG["qr_output_dir"], f"{uid}.png"))

    if not os.path.exists(qr_path):
        messagebox.showerror("Error", "QR code image not found.")
        return

    try:
        if sys.platform.startswith("win"):
            os.startfile(qr_path, "print")
        elif sys.platform == "darwin":
            subprocess.run(["open", "-a", "Preview", qr_path])
        else:
            subprocess.run(["xdg-open", qr_path])
    except Exception as e:
        messagebox.showerror("Print Error", f"Could not print QR code:\n{e}")

def search_items():
    query = search_entry.get().strip().lower()
    if not query:
        update_item_list()
        return
    filtered = [i for i in items if query in i["name"].lower() or query in i["uid"]]
    update_item_list(filtered)

# --- UI SETUP ---
root = tk.Tk()
root.title("Item QR Code Generator")

# --- ENTRY FORM ---
form_frame = tk.Frame(root)
form_frame.pack(padx=10, pady=10)

tk.Label(form_frame, text="Item Name:").grid(row=0, column=0, padx=5, pady=5, sticky="e")
entry_name = tk.Entry(form_frame, width=30)
entry_name.grid(row=0, column=1, padx=5, pady=5)

tk.Label(form_frame, text="Item Price:").grid(row=1, column=0, padx=5, pady=5, sticky="e")
entry_price = tk.Entry(form_frame, width=30)
entry_price.grid(row=1, column=1, padx=5, pady=5)

generate_btn = tk.Button(form_frame, text="Generate QR", command=generate_qr)
generate_btn.grid(row=2, column=0, columnspan=2, pady=10)

# --- QR DISPLAY + ITEM INFO ---
display_frame = tk.Frame(root)
display_frame.pack(pady=10)

qr_label = tk.Label(display_frame)
qr_label.pack()

blank_qr_image = create_blank_image()
qr_label.config(image=blank_qr_image)
qr_label.image = blank_qr_image

item_info_box = tk.Text(display_frame, font=("Arial", 12), height=3, wrap="word", width=50)
item_info_box.pack(pady=5)
item_info_box.config(state="disabled")

# --- SEARCH BAR ---
search_frame = tk.Frame(root)
search_frame.pack(padx=10, pady=5)

search_entry = tk.Entry(search_frame, width=40)
search_entry.pack(side="left", padx=(0, 5))
search_btn = tk.Button(search_frame, text="Search", command=search_items)
search_btn.pack(side="left")
clear_btn = tk.Button(search_frame, text="Clear", command=lambda: update_item_list())
clear_btn.pack(side="left", padx=(5, 0))

# --- ITEM LIST TABLE ---
table_frame = tk.Frame(root)
table_frame.pack(padx=10, pady=10, fill="both", expand=True)

columns = ("uid", "name", "price")
item_list = ttk.Treeview(table_frame, columns=columns, show="headings", height=10)
for col in columns:
    item_list.heading(col, text=col.capitalize())
    anchor = "e" if col == "price" else "w"
    item_list.column(col, anchor=anchor, width=120)
item_list.pack(side="left", fill="both", expand=True)

scrollbar = ttk.Scrollbar(table_frame, orient="vertical", command=item_list.yview)
item_list.configure(yscroll=scrollbar.set)
scrollbar.pack(side="right", fill="y")

item_list.bind("<<TreeviewSelect>>", on_item_select)

# --- DELETE + PRINT BUTTONS ---
btn_frame = tk.Frame(root)
btn_frame.pack(pady=5)

delete_btn = tk.Button(btn_frame, text="Delete Selected", command=delete_selected, bg="#e66", fg="white")
delete_btn.pack(side="left", padx=5)

print_btn = tk.Button(btn_frame, text="Print QR Code", command=print_selected, bg="#4a9", fg="white")
print_btn.pack(side="left", padx=5)

# --- INIT ---
update_item_list()
if items:
    show_item(items[-1])

root.mainloop()
