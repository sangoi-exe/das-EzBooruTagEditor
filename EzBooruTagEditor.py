import tkinter as tk
import tkinter.font as tkFont
import os
import json
import re
from tkinter import filedialog
from PIL import Image, ImageTk
from tkinter import ttk


class TextImageEditor:
    def __init__(self, root):
        self.root = root
        self.root.title("Ez Booru Tag Editor")
        self.current_directory = None
        self.text_files = []
        self.current_file = None
        self.current_image = None
        self.tags = []
        self.removed_tags = []
        self.marked_tags = {}
        self.currently_marked_tag = None
        self.unique_tags = []
        self.common_words_tags = {}

        self.main_frame = tk.Frame(self.root, borderwidth=5)
        self.main_frame.pack(side=tk.TOP, fill=tk.BOTH, expand=True)
        self.main_frame.pack_propagate(False)

        self.navigator = tk.Frame(self.root, borderwidth=5)
        self.navigator.pack(side=tk.TOP, fill=tk.BOTH)
        self.navigator.config(height=30)

        self.bottom_frame = tk.Frame(self.root, borderwidth=5)
        self.bottom_frame.pack(side=tk.TOP, fill=tk.X)

        self.left_frame = tk.Frame(self.main_frame, borderwidth=4, relief="sunken")
        self.left_frame.pack(side=tk.LEFT, fill=tk.BOTH, expand=False)
        self.left_frame.config(width=200)

        scrollbar = tk.Scrollbar(self.left_frame, orient="vertical")

        self.listbox = tk.Listbox(self.left_frame, selectmode=tk.SINGLE, yscrollcommand=scrollbar.set)
        self.listbox.pack(side=tk.LEFT, fill=tk.Y, expand=True)
        self.listbox.bind("<<ListboxSelect>>", self.show_file_content)

        scrollbar.config(command=self.listbox.yview, width=15)
        scrollbar.pack(side="right", fill="y")

        def on_mousewheel(event):
            self.listbox.yview_scroll(int(-1 * (event.delta / 120)), "units")

        self.listbox.bind("<MouseWheel>", on_mousewheel)

        self.middle_frame = tk.Frame(self.main_frame, borderwidth=4, relief="sunken")
        self.middle_frame.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        self.middle_frame.pack_propagate(False)

        self.image_label = tk.Label(self.middle_frame)
        self.image_label.pack(fill=tk.BOTH, expand=True)
        self.image_label.bind("<MouseWheel>", self.on_mouse_wheel)

        self.right_frame = tk.Frame(self.main_frame, borderwidth=4, relief="sunken")
        self.right_frame.pack(side=tk.LEFT, fill=tk.BOTH, expand=False)
        self.right_frame.config(width=400)
        self.right_frame.pack_propagate(False)

        self.tag_frame = tk.Frame(self.right_frame)
        self.tag_frame.pack(side=tk.TOP, fill=tk.BOTH, expand=True)

        self.unique_frame = tk.Frame(self.tag_frame, borderwidth=4, relief="groove")
        self.unique_frame.pack(side=tk.TOP, fill=tk.X, expand=True)

        self.common_frame = tk.Frame(self.tag_frame, borderwidth=4, relief="groove")
        self.common_frame.pack(side=tk.TOP, fill=tk.X, expand=True)

        self.button_frame = tk.Frame(self.bottom_frame, borderwidth=4, relief="sunken")
        self.button_frame.pack(side=tk.BOTTOM, fill=tk.X, expand=True)

        self.nav_frame = tk.Frame(self.navigator, borderwidth=4, relief="sunken")
        self.nav_frame.pack(side=tk.BOTTOM, fill=tk.X, expand=True)

        self.next_button = tk.Button(self.nav_frame, text="Next Image 〉〉〉", command=lambda: self.change_image(1))
        self.next_button.pack(side=tk.RIGHT, fill=tk.X, expand=True)

        self.prev_button = tk.Button(self.nav_frame, text="〈〈〈 Previous Image", command=lambda: self.change_image(-1))
        self.prev_button.pack(side=tk.LEFT, fill=tk.X, expand=True)

        self.dir_button = tk.Button(
            self.button_frame,
            text="Choose Directory",
            command=self.choose_directory,
        )
        self.dir_button.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)

        self.save_button = tk.Button(self.button_frame, text="Save", command=self.save_file)
        self.save_button.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)

        self.center_bottom_frame = tk.Frame(self.bottom_frame)
        self.center_bottom_frame.pack(side=tk.LEFT, fill=tk.X, expand=True)

        self.right_bottom_frame = tk.Frame(self.bottom_frame)
        self.right_bottom_frame.pack(side=tk.LEFT, fill=tk.X, expand=False)

        self.undo_button = tk.Button(self.button_frame, text="Undo", command=self.undo)
        self.undo_button.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)

        self.tag_entry = tk.Entry(self.button_frame)
        self.tag_entry.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)

        self.add_tag_button = tk.Button(
            self.button_frame,
            text="Add Tag",
            command=lambda: self.add_tag(self.tag_entry.get()),
        )
        self.add_tag_button.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)

        self.tag_entry.bind("<Return>", lambda event: self.add_tag(event=event))
        self.right_frame.bind("<Configure>", lambda event: self.resize_image())

    def choose_directory(self):
        new_directory = filedialog.askdirectory()

        if new_directory:
            self.current_directory = new_directory
            self.current_image = None
            self.image_label.config(image=self.current_image)
            self.clear_tag_frame()
            self.update_file_list()

    def update_file_list(self):
        if not self.current_directory:
            return

        all_files = os.listdir(self.current_directory)

        self.file_map = {}
        for file in all_files:
            name, ext = os.path.splitext(file)
            if ext.lower() in [".txt"]:
                for img_ext in [".png", ".jpg", ".jpeg", ".gif", ".webp"]:
                    img_path = os.path.join(self.current_directory, name + img_ext)
                    if os.path.exists(img_path):
                        self.file_map[file] = img_path
                        break

        sorted_files = sorted(self.file_map.keys(), key=self.natural_sort_key)

        self.listbox.delete(0, tk.END)
        for txt_file in sorted_files:
            self.listbox.insert(tk.END, txt_file)

    def change_image(self, direction):
        file_map_keys = list(self.file_map.keys())
        if not file_map_keys:
            return

        selected_index = self.listbox.curselection()
        if not selected_index:
            return

        new_index = selected_index[0] + direction
        if 0 <= new_index < len(file_map_keys):
            self.listbox.selection_clear(selected_index[0])
            self.listbox.selection_set(new_index)
            self.listbox.event_generate("<<ListboxSelect>>")

    def on_key_press(self, event):
        if event.keysym in ["Up", "Down"]:
            direction = -1 if event.keysym == "Up" else 1
            self.change_image(direction)
        elif event.keysym == "z" and event.state & 0x0004:
            self.undo()
        elif event.keysym == "s" and event.state & 0x0004:
            self.save_file()

    def on_mouse_wheel(self, event):
        direction = -1 if event.delta > 0 else 1
        self.change_image(direction)

    def nav_buttons(self, button_direction):
        direction = -1 if button_direction == "<" else 1
        self.change_image(direction)

    def show_file_content(self, event):
        self.currently_marked_tag = []
        selected_index = self.listbox.curselection()
        if not selected_index:
            return

        self.current_file = list(self.file_map.keys())[selected_index[0]]
        tag_file_path = os.path.join(self.current_directory, self.current_file)

        self.unique_tags, self.common_words_tags = self.read_tags_from_file(tag_file_path)
        self.removed_tags = []

        self.tags = self.unique_tags.copy()
        for tags in self.common_words_tags.values():
            self.tags.extend(tags)

        self.create_tag_widget()
        self.resize_image()

    def resize_image(self):
        if self.current_file is None or self.current_file not in self.file_map:
            return

        image_path = self.file_map[self.current_file]

        image = Image.open(image_path)
        aspect_ratio = image.width / image.height

        frame_width = self.middle_frame.winfo_width()
        frame_height = self.middle_frame.winfo_height()

        new_width = frame_width
        new_height = int(new_width / aspect_ratio)

        if new_height > frame_height:
            new_height = frame_height
            new_width = int(new_height * aspect_ratio)

        image = image.resize((new_width, new_height))
        self.current_image = ImageTk.PhotoImage(image)

        self.image_label.config(image=self.current_image)

    def read_tags_from_file(self, file_path):
        try:
            json_path = "wordsToGroup.json"
            try:
                with open(json_path, "r") as json_file:
                    common_words = json.load(json_file).get("words", [])
            except FileNotFoundError:
                # Cria um arquivo JSON padrão com palavras pré-definidas.
                common_words = ["hair", "lips"]
                with open(json_path, "w") as json_file:
                    json.dump({"words": common_words}, json_file)

            common_word_to_tags = {word: [] for word in common_words}

            with open(file_path, "r") as file:
                content = file.read()
                tags = content.split(",")
                tags = [tag.strip() for tag in tags if tag.strip()]

            for tag in tags:
                for word in common_word_to_tags:
                    if word in tag.split():
                        common_word_to_tags[word].append(tag)
                        break

            self.unique_tags = [tag for tag in tags if all(word not in tag for word in common_words)]
            self.common_words_tags = common_word_to_tags

            return self.unique_tags, self.common_words_tags
        except FileNotFoundError as e:
            print(f"File not found: {e.filename}")
            return [], {}

    def create_tag_widget(self):
        customFont = tkFont.Font(family="Helvetica", size=10)
        self.clear_tag_frame()
        max_width = 400

        unique_frame = tk.Frame(self.unique_frame)
        unique_frame.pack(side=tk.TOP, fill=tk.BOTH, expand=True)

        common_frame = tk.Frame(self.common_frame)
        common_frame.pack(side=tk.BOTTOM, fill=tk.BOTH, expand=True)

        current_width = 0
        for tag in self.unique_tags:
            temp_widget = tk.Label(unique_frame, text=tag, borderwidth=4, relief="raised", font=customFont)
            tag_width = temp_widget.winfo_reqwidth()
            temp_widget.destroy()

            if current_width + tag_width > max_width:
                unique_frame = tk.Frame(self.unique_frame)
                unique_frame.pack(side=tk.TOP, fill=tk.BOTH, expand=True)
                current_width = 0

            tag_label = tk.Label(unique_frame, text=tag, borderwidth=2, relief="raised", font=customFont)
            tag_label.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)

            tag_label.original_bg = tag_label.cget("background")
            tag_label.bind("<Enter>", lambda event, tl=tag_label: self.on_hover(tl))
            tag_label.bind("<Leave>", lambda event, tl=tag_label: self.on_leave(tl))
            tag_label.bind("<Button-1>", lambda event, t=tag, tl=tag_label: self.on_click(t, tl))

            current_width += tag_width

        if self.common_words_tags:
            for common_word, common_tags in self.common_words_tags.items():
                common_frame = tk.Frame(self.common_frame)
                common_frame.pack(side=tk.BOTTOM, fill=tk.BOTH, expand=True)
                current_width = 0

                for tag in common_tags:
                    temp_widget = tk.Label(common_frame, text=tag, borderwidth=4, relief="raised", font=customFont)
                    tag_width = temp_widget.winfo_reqwidth()
                    temp_widget.destroy()

                    if current_width + tag_width > max_width:
                        common_frame = tk.Frame(self.common_frame)
                        common_frame.pack(side=tk.BOTTOM, fill=tk.BOTH, expand=True)
                        current_width = 0

                    tag_label = tk.Label(common_frame, text=tag, borderwidth=2, relief="raised", font=customFont)
                    tag_label.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)

                    tag_label.original_bg = tag_label.cget("background")
                    tag_label.bind("<Enter>", lambda event, tl=tag_label: self.on_hover(tl))
                    tag_label.bind("<Leave>", lambda event, tl=tag_label: self.on_leave(tl))
                    tag_label.bind("<Button-1>", lambda event, t=tag, tl=tag_label: self.on_click(t, tl))

                    current_width += tag_width

    def rearrange_tags(self):
        self.create_tag_widget()

    def add_tag(self, tag_text=None, event=None):
        new_tag = tag_text if tag_text is not None else self.tag_entry.get()
        if not new_tag:
            return

        common_word_found = False
        for common_word in self.common_words_tags:
            if common_word in new_tag.split():
                self.common_words_tags[common_word].append(new_tag)
                common_word_found = True
                break

        if not common_word_found:
            self.unique_tags.append(new_tag)

        self.rearrange_tags()
        self.tag_entry.delete(0, tk.END)

    def remove_tag(self, tag, tag_label):
        if tag in self.unique_tags:
            self.unique_tags.remove(tag)
        else:
            for common_word, common_tags in self.common_words_tags.items():
                if tag in common_tags:
                    common_tags.remove(tag)
                    break

            empty_keys = [k for k, v in self.common_words_tags.items() if not v]
            for key in empty_keys:
                del self.common_words_tags[key]

            for common_word, common_tags in list(self.common_words_tags.items()):
                if len(common_tags) == 1:
                    unique_tag = common_tags.pop()
                    self.unique_tags.append(unique_tag)
                    del self.common_words_tags[common_word]

        self.removed_tags.append(tag)
        tag_label.destroy()
        self.rearrange_tags()

        if tag_label == self.currently_marked_tag:
            self.currently_marked_tag = None
        if tag_label in self.marked_tags:
            del self.marked_tags[tag_label]

    def undo(self):
        if self.removed_tags:
            last_removed_tag = self.removed_tags.pop()
            self.add_tag(last_removed_tag)

    def save_file(self):
        if not self.current_file:
            return

        all_tags = self.unique_tags.copy()
        for tags in self.common_words_tags.values():
            all_tags.extend(tags)

        new_content = ", ".join(all_tags)
        with open(os.path.join(self.current_directory, self.current_file), "w") as f:
            f.write(new_content)

    def on_hover(self, tag_label):
        tag_label.hover_bg = tag_label.cget("background")
        tag_label.config(bg="#ffcac9")

    def on_click(self, tag, tag_label):
        if tag_label == self.currently_marked_tag:
            self.remove_tag(tag, tag_label)
            self.currently_marked_tag = None
        else:
            if self.currently_marked_tag:
                self.currently_marked_tag.config(relief="raised", bg=self.currently_marked_tag.original_bg)
                del self.marked_tags[self.currently_marked_tag]

            self.marked_tags[tag_label] = tag
            tag_label.config(relief="sunken", bg="#ffcac9")
            self.currently_marked_tag = tag_label

    def on_leave(self, tag_label):
        if tag_label not in self.marked_tags:
            tag_label.config(bg=tag_label.original_bg)

    def clear_tag_frame(self):
        for frame in [self.unique_frame, self.common_frame]:
            for widget in frame.winfo_children():
                widget.destroy()

    def natural_sort_key(self, s):
        return [int(text) if text.isdigit() else text.lower() for text in re.split("([0-9]+)", s)]


if __name__ == "__main__":
    root = tk.Tk()
    app = TextImageEditor(root)
    root.geometry("800x600")
    style = ttk.Style()
    style.theme_use("classic")
    style.configure("TScrollbar", arrowsize=15)
    style.configure("TButton", font=("MS Sans Serif", 8))
    style.configure("TLabel", font=("MS Sans Serif", 8), background="lightgrey")
    style.map("TButton", background=[("active", "!disabled", "darkgrey"), ("pressed", "black")])

    screen_width = root.winfo_screenwidth()
    screen_height = root.winfo_screenheight()

    center_x = int(screen_width / 2 - 800 / 2)
    center_y = int(screen_height / 2 - 600 / 2)

    root.geometry(f"800x600+{center_x}+{center_y}")

    root.bind("<Up>", app.on_key_press)
    root.bind("<Down>", app.on_key_press)
    root.bind("<Control-z>", app.on_key_press)
    root.bind("<Control-s>", app.on_key_press)

    root.mainloop()
