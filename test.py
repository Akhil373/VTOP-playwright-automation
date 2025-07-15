# import tkinter as tk
# from tkinter import messagebox
# from PIL import Image, ImageTk
# import os
# import csv

# IMAGE_FOLDER = "temp/dataset/600"
# OUTPUT_CSV = "temp/labels600.csv"

# class LabelingApp:
#     def __init__(self, root):
#         self.root = root
#         self.root.title("Captcha Labeling Tool")

#         self.image_files = self.get_unlabeled_images()
#         if not self.image_files:
#             messagebox.showinfo("Done!", "No more images to label.")
#             self.root.destroy()
#             return

#         self.current_image_index = 0

#         self.image_label = tk.Label(root)
#         self.image_label.pack(pady=10)

#         self.progress_label = tk.Label(root, text="", font=("Helvetica", 12))
#         self.progress_label.pack(pady=5)

#         self.entry = tk.Entry(root, font=("Helvetica", 16), width=20)
#         self.entry.pack(pady=10)
#         self.entry.focus_set()

#         self.info_label = tk.Label(root, text="Note: Input will be converted to uppercase.", font=("Helvetica", 10), fg="gray")
#         self.info_label.pack(pady=5)

#         self.root.bind('<Return>', self.save_and_next)

#         self.load_image()

#     def get_unlabeled_images(self):
#         """Finds images in IMAGE_FOLDER that are not yet in the CSV."""
#         all_images = {f for f in os.listdir(IMAGE_FOLDER) if f.lower().endswith(('.png', '.jpg', '.jpeg'))}

#         labeled_images = set()
#         if os.path.exists(OUTPUT_CSV):
#             with open(OUTPUT_CSV, 'r', newline='') as f:
#                 reader = csv.reader(f)

#                 try:
#                     next(reader)
#                 except StopIteration:
#                     pass
#                 for row in reader:
#                     if row:
#                         labeled_images.add(row[0])

#         unlabeled = sorted(list(all_images - labeled_images))
#         print(f"Found {len(all_images)} total images.")
#         print(f"Found {len(labeled_images)} already labeled images.")
#         print(f"Found {len(unlabeled)} images to label.")
#         return unlabeled

#     def load_image(self):
#         """Loads and displays the current image."""
#         image_path = os.path.join(IMAGE_FOLDER, self.image_files[self.current_image_index])

#         img = Image.open(image_path)
#         img.thumbnail((600, 200))
#         self.tk_img = ImageTk.PhotoImage(img)
#         self.image_label.config(image=self.tk_img)

#         progress_text = f"Image {self.current_image_index + 1} of {len(self.image_files)}"
#         self.progress_label.config(text=progress_text)

#         self.entry.delete(0, tk.END)

#     def save_and_next(self, event=None):
#         """Saves the current label to the CSV and loads the next image."""
#         label_text = self.entry.get().strip().upper()
#         if not label_text:
#             messagebox.showwarning("Warning", "Label cannot be empty.")
#             return

#         image_filename = self.image_files[self.current_image_index]

#         write_header = not os.path.exists(OUTPUT_CSV)

#         with open(OUTPUT_CSV, 'a', newline='') as f:
#             writer = csv.writer(f)
#             if write_header:
#                 writer.writerow(['file_name', 'text'])
#             writer.writerow([image_filename, label_text])

#         self.current_image_index += 1
#         if self.current_image_index < len(self.image_files):
#             self.load_image()
#         else:
#             messagebox.showinfo("Done!", "All images have been labeled.")
#             self.root.destroy()

# if __name__ == "__main__":
#     os.makedirs(os.path.dirname(OUTPUT_CSV), exist_ok=True)

#     root = tk.Tk()
#     app = LabelingApp(root)
#     root.mainloop()
from plyer import notification
notification.notify()
