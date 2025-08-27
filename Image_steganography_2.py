import os
import tkinter
import customtkinter as ctk
from CTkMessagebox import CTkMessagebox
from tkinter import filedialog
from PIL import Image, ImageTk
from stegano import lsb

class SteganographyApp(ctk.CTk):
    def __init__(self):
        super().__init__()

        # --- Window Setup ---
        self.title("Steganography Tool")
        self.geometry("700x500")
        self.resizable(False, False)
        ctk.set_appearance_mode("Dark")
        ctk.set_default_color_theme("blue")
        
        self.filename = None
        self.secret_image = None
        # Add instance variables to hold persistent image references
        self.pil_image_ref = None
        self.photo_image = None


        # --- Layout Configuration (using .grid for responsiveness) ---
        self.grid_columnconfigure((0, 1), weight=1)
        self.grid_rowconfigure(1, weight=1)

        # --- Widget Creation ---
        self.create_widgets()

    def create_widgets(self):
        # --- Header ---
        header_label = ctk.CTkLabel(self, text="STEGANOSUITE", font=ctk.CTkFont(size=25, weight="bold"))
        header_label.grid(row=0, column=0, columnspan=2, pady=20)

        # --- Image Frame (Left) ---
        image_frame = ctk.CTkFrame(self, corner_radius=10)
        image_frame.grid(row=1, column=0, padx=(20, 10), pady=(0, 20), sticky="nsew")
        self.image_label = ctk.CTkLabel(image_frame, text="Open an image to view", text_color="gray")
        self.image_label.pack(expand=True, fill="both", padx=10, pady=10)

        # --- Text Frame (Right) ---
        text_frame = ctk.CTkFrame(self, corner_radius=10)
        text_frame.grid(row=1, column=1, padx=(10, 20), pady=(0, 20), sticky="nsew")
        self.text_area = ctk.CTkTextbox(text_frame, font=("Roboto", 16), corner_radius=0, border_width=0)
        self.text_area.pack(expand=True, fill="both")
        
        # --- Image Button Frame (Bottom Left) ---
        img_button_frame = ctk.CTkFrame(self, fg_color="transparent")
        img_button_frame.grid(row=2, column=0, padx=(20, 10), pady=10, sticky="ew")
        img_button_frame.grid_columnconfigure((0, 1), weight=1)

        open_button = ctk.CTkButton(img_button_frame, text="Open Image", height=40, font=("Arial", 14, "bold"), command=self.open_image)
        open_button.grid(row=0, column=0, padx=(0, 5), sticky="ew")
        
        save_button = ctk.CTkButton(img_button_frame, text="Save Image", height=40, font=("Arial", 14, "bold"), command=self.save_image)
        save_button.grid(row=0, column=1, padx=(5, 0), sticky="ew")
        
        # --- Data Button Frame (Bottom Right) ---
        data_button_frame = ctk.CTkFrame(self, fg_color="transparent")
        data_button_frame.grid(row=2, column=1, padx=(10, 20), pady=10, sticky="ew")
        data_button_frame.grid_columnconfigure((0, 1), weight=1)
        
        hide_button = ctk.CTkButton(data_button_frame, text="Hide Data", height=40, font=("Arial", 14, "bold"), command=self.hide_data)
        hide_button.grid(row=0, column=0, padx=(0, 5), sticky="ew")
        
        show_button = ctk.CTkButton(data_button_frame, text="Show Data", height=40, font=("Arial", 14, "bold"), command=self.show_data)
        show_button.grid(row=0, column=1, padx=(5, 0), sticky="ew")

    def open_image(self):
        self.filename = filedialog.askopenfilename(
            initialdir=os.getcwd(),
            title='Select Image File',
            filetypes=(("PNG file", "*.png"), ("JPG File", "*.jpg"))
        )
        if self.filename:
            # Open and resize the Pillow image
            pil_image = Image.open(self.filename)
            pil_image.thumbnail((300, 300))

            # 1. Keep a persistent reference to the Pillow image itself
            self.pil_image_ref = pil_image

            # 2. Create the CTkImage using the persistent Pillow image reference
            self.photo_image = ctk.CTkImage(light_image=self.pil_image_ref, size=self.pil_image_ref.size)

            # 3. Configure the label to use the new image
            self.image_label.configure(image=self.photo_image, text="")

            # 4. CRITICAL: Also attach the CTkImage object directly to the widget.
            # This creates the final, necessary hard reference that prevents garbage collection.
            self.image_label.image = self.photo_image

    def hide_data(self):
        if not self.filename:
            CTkMessagebox(title="Error", message="Please open an image first.", icon="cancel")
            return
            
        message = self.text_area.get("1.0", "end-1c")
        if not message:
            CTkMessagebox(title="Error", message="Please enter a message to hide.", icon="cancel")
            return
            
        self.secret_image = lsb.hide(self.filename, message)
        self.text_area.delete("1.0", "end")
        CTkMessagebox(title="Success", message="Message hidden in the image. You can now save it.", icon="check")


    def show_data(self):
        if not self.filename:
            CTkMessagebox(title="Error", message="Please open an image first.", icon="cancel")
            return
            
        try:
            clear_message = lsb.reveal(self.filename)
            if clear_message is None:
                clear_message = "No hidden message found."
            self.text_area.delete("1.0", "end")
            self.text_area.insert("end", clear_message)
        except IndexError:
            self.text_area.delete("1.0", "end")
            self.text_area.insert("end", "No hidden message found in this image.")

    def save_image(self):
        if not self.secret_image:
            CTkMessagebox(title="Error", message="No hidden message to save. Please hide data first.", icon="cancel")
            return

        save_path = filedialog.asksaveasfilename(
            defaultextension=".png",
            filetypes=[("PNG file", "*.png")],
            initialfile="hidden.png",
            title="Save Image As..."
        )

        if save_path:
            self.secret_image.save(save_path)

            # Clear the UI and reset the state
            self.image_label.configure(image=None, text="Open an image to view")
            self.text_area.delete("1.0", "end")
            
            CTkMessagebox(title="Success", message=f"Image saved successfully at:\n{save_path}", icon="check")
            
            # Reset internal state
            self.filename = None
            self.secret_image = None
            self.pil_image_ref = None
            self.photo_image = None

if __name__ == "__main__":
    app = SteganographyApp()
    app.mainloop()
