import tkinter as tk
import tkinter.font as tkFont
import os
import json
import re
import requests
import webbrowser
from tkinter import simpledialog, filedialog, ttk, messagebox, Toplevel, Label
from PIL import Image, ImageTk
from urllib.parse import quote_plus


class TextImageEditor:
	def __init__(self, root):
		self.root = root
		self.root.title(f"Ez Booru Tag Editor")
		self.currently_marked_tag = None
		self.current_image_path = None
		self.current_directory = None
		self.current_image = None
		self.current_file = None
		self.apiKey = None
		self.login = None
		self.removed_tags = []
		self.unique_tags = []
		self.text_files = []
		self.tags = []
		self.common_words_tags = {}
		self.marked_tags = {}
		self.file_map = {}

		self.main_frame = tk.Frame(self.root, borderwidth=5)
		self.main_frame.pack(side=tk.TOP, fill=tk.BOTH, expand=True)
		self.main_frame.pack_propagate(False)

		self.navigator = tk.Frame(self.root, borderwidth=5)
		self.navigator.pack(side=tk.TOP, fill=tk.BOTH)
		self.navigator.config(height=30)

		self.bottom_frame = tk.Frame(self.root, borderwidth=5)
		self.bottom_frame.pack(side=tk.TOP, fill=tk.X)

		self.left_frame = tk.Frame(self.main_frame, borderwidth=4, relief=tk.SUNKEN)
		self.left_frame.pack(side=tk.LEFT, fill=tk.BOTH, expand=False)
		self.left_frame.config(width=200)

		scrollbar = tk.Scrollbar(self.left_frame, orient="vertical")

		self.listbox = tk.Listbox(self.left_frame, selectmode=tk.SINGLE, yscrollcommand=scrollbar.set, exportselection=False)
		self.listbox.pack(side=tk.LEFT, fill=tk.Y, expand=True)
		self.listbox.bind("<<ListboxSelect>>", self.show_file_content)

		scrollbar.config(command=self.listbox.yview, width=15)
		scrollbar.pack(side=tk.RIGHT, fill=tk.Y)

		def on_mousewheel(event):
			self.listbox.yview_scroll(int(-1 * (event.delta / 120)), "units")

		self.listbox.bind("<MouseWheel>", on_mousewheel)

		self.middle_frame = tk.Frame(self.main_frame, borderwidth=4, relief="sunken")
		self.middle_frame.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
		self.middle_frame.pack_propagate(False)

		self.image_box = tk.Label(self.middle_frame)
		self.image_box.pack(side=tk.TOP, fill=tk.BOTH, expand=True)
		self.image_box.bind("<MouseWheel>", self.on_mouse_wheel)

		self.right_frame = tk.Frame(self.main_frame, borderwidth=4, relief="sunken")
		self.right_frame.pack(side=tk.LEFT, fill=tk.BOTH, expand=False)
		self.right_frame.config(width=400)
		self.right_frame.pack_propagate(False)
		
		self.image_name = tk.Label(self.right_frame, borderwidth=4, relief=tk.SUNKEN)
		self.image_name.pack(side=tk.BOTTOM, fill=tk.X, expand=False)        
		self.image_name.config(text=None)

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

		self.api_key_button = tk.Button(
			self.button_frame,
			text="Add API Key",
			command=self.add_apiData,
		)
		self.api_key_button.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)

		self.save_button = tk.Button(self.button_frame, text="Save", command=self.save_file)
		self.save_button.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)

		self.undo_button = tk.Button(self.button_frame, text="Undo", command=self.undo)
		self.undo_button.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)

		self.tag_entry = tk.Entry(self.button_frame, exportselection=False)
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
			self.image_box.config(image=self.current_image)
			self.root.title(f"Ez Booru Tag Editor - {new_directory}")
			self.clear_tag_frame()
			self.update_file_list()

	def update_file_list(self):
		if not self.current_directory:
			return

		all_files = os.listdir(self.current_directory)

		unsorted_file_map = {}
		for file in all_files:
			name, ext = os.path.splitext(file)
			if ext.lower() in [".txt"]:
				for img_ext in [".png", ".jpg", ".jpeg", ".gif", ".webp"]:
					img_path = os.path.join(self.current_directory, name + img_ext)
					if os.path.exists(img_path):
						unsorted_file_map[file] = img_path
						break

		sorted_files = sorted(unsorted_file_map.keys(), key=self.natural_sort_key)

		self.file_map = {file: unsorted_file_map[file] for file in sorted_files}

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
			if self.file_map:
				direction = -1 if event.keysym == "Up" else 1
				self.change_image(direction)
		elif event.keysym == "z" and event.state & 0x0004:
			self.undo()
		elif event.keysym == "s" and event.state & 0x0004:
			self.save_file()

	def on_mouse_wheel(self, event):
		if self.file_map:
			direction = -1 if event.delta > 0 else 1
			self.change_image(direction)

	def nav_buttons(self, button_direction):
		if self.file_map:
			direction = -1 if button_direction == "<" else 1
			self.change_image(direction)

	def show_file_content(self, event):
		self.currently_marked_tag = []
		selected_index = self.listbox.curselection()
		if not selected_index:
			return

		self.current_file = list(self.file_map.keys())[selected_index[0]]
		print(f"Selected file: {self.current_file}, Image path: {self.file_map[self.current_file]}")

		tag_file_path = os.path.join(self.current_directory, self.current_file)

		self.unique_tags, self.common_words_tags = self.read_tags_from_file(tag_file_path)
		self.removed_tags = []

		self.tags = self.unique_tags.copy()
		for tags in self.common_words_tags.values():
			self.tags.extend(tags)

		self.current_image_path = self.file_map[self.current_file]
		self.image_name.config(text=os.path.basename(self.current_image_path))

		self.create_tag_widget()
		self.resize_image()

	def resize_image(self):
		if not self.current_image_path:
			return

		image = Image.open(self.current_image_path)
		aspect_ratio = image.width / image.height

		self.middle_frame.update_idletasks()
		frame_width = self.middle_frame.winfo_width()
		frame_height = self.middle_frame.winfo_height()

		new_width = frame_width
		new_height = int(new_width / aspect_ratio)

		if new_height > frame_height:
			new_height = frame_height
			new_width = int(new_height * aspect_ratio)

		image = image.resize((new_width, new_height))
		self.current_image = ImageTk.PhotoImage(image)

		self.image_box.config(image=self.current_image)

	def read_tags_from_file(self, file_path):
		try:
			json_path = "config.json"
			try:
				with open(json_path, "r") as json_file:
					common_words = json.load(json_file).get("words", [])
			except FileNotFoundError:
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

			# Verificar e mover tags com menos de duas ocorrências para unique_tags
			for word, tag_list in list(common_word_to_tags.items()):
				if len(tag_list) < 2:
					self.unique_tags.extend(tag_list)
					del common_word_to_tags[word]

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
			tag_label.bind("<Button-3>", lambda event, t=tag: self.on_right_click(event, t))

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
					tag_label.bind("<Button-3>", lambda event, t=tag: self.on_right_click(event, t))

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
		
		# Cria uma nova janela Toplevel que serve como notificação
		self.popup = tk.Toplevel(self.root)
		self.popup.overrideredirect(True)  # Isso remove a barra de título

		# Cria um label dentro da janela popup para exibir a mensagem
		label = tk.Label(self.popup, text="Saved!", borderwidth=2, relief=tk.RIDGE)
		label.pack(ipadx=10, ipady=5)  # Adiciona um pouco de padding interno

		# Atualiza o layout dos widgets e obtém as coordenadas globais do botão Save
		self.root.update_idletasks()
		global_x = self.save_button.winfo_rootx()
		global_y = self.save_button.winfo_rooty()

		x_offset = global_x + self.save_button.winfo_width() + 5
		y_offset = global_y + 2

		self.popup.geometry(f"+{x_offset}+{y_offset}")

		self.popup.after(1000, self.popup.destroy)


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

	def on_right_click(self, event, tag):
		with open("config.json", "r") as file:
			data = json.load(file)
			self.apiKey = data.get("api_key", "")
			self.login = data.get("login", "")

		if not self.apiKey:
			api_key_info = (
				"API key is missing.\n\nRegister for a Danbooru account and generate an API key.\n"				
				"After registering, you can generate it at bottom of your profile page.\n"
				"Then, use the 'Add API Key' button in this application to set your API key and login."				
			)
			links = [("Danbooru", "https://danbooru.donmai.us/users/new"),
					("Generate API key", "https://danbooru.donmai.us/profile")]
			self.show_custom_popup(api_key_info, links)
			return

		url = f"https://danbooru.donmai.us/wiki_pages/{tag}.json?api_key={self.apiKey}&login={self.login}"
		response = requests.get(url)

		if response.status_code == 200:
			data = response.json()
			body_content = data.get("body", "No body content found")

			cutoff_strings = ["\nUse this tag if:\r\n\r\n*", "\nh4"]
			for cutoff in cutoff_strings:
				index = body_content.find(cutoff)
				if index != -1:
					body_content = body_content[:index]
					break

		else:
			body_content = f"Error: {response.status_code}"
		
		simpledialog.messagebox.showinfo(f"{tag.title()} [Wiki Page Content]", body_content)

	def show_custom_popup(self, message, links):
		popup = Toplevel(self.root, borderwidth=2, relief=tk.RIDGE)
		popup.overrideredirect(True)

		label = tk.Label(popup, text=message)
		label.pack(ipadx=10, ipady=5)

		self.root.update_idletasks()
		global_x = self.root.winfo_rootx()
		global_y = self.root.winfo_rooty()

		x_offset = global_x + (self.root.winfo_width() // 2) - (popup.winfo_reqwidth() // 2)
		y_offset = global_y + (self.root.winfo_height() // 2) - (popup.winfo_reqheight())

		popup.geometry(f"+{x_offset}+{y_offset}")

		for text, url in links:
			link_label = Label(popup, text=text, fg="blue", cursor="hand2")
			link_label.pack(side=tk.TOP)
			link_label.bind("<Button-1>", lambda e, link=url: webbrowser.open_new(link))

		close_button = tk.Button(popup, text="Ok", command=popup.destroy)
		close_button.pack(side=tk.BOTTOM, pady=(10, 10))

		popup.bind("<Return>", lambda e: popup.destroy())
		popup.bind("<Escape>", lambda e: popup.destroy())

		popup.focus_set()
		

	def add_apiData(self):
		api_key = simpledialog.askstring("Input", "Enter your API key:", parent=self.main_frame)
		login = simpledialog.askstring("Input", "Enter your login:", parent=self.main_frame)

		if api_key is not None and login is not None:
			self.update_json_file(api_key, login)

	def update_json_file(self, api_key, login):
		file_path = "config.json"
		try:
			with open(file_path, "r+") as file:
				data = json.load(file)
				# Salva a API key e o login no JSON
				data["api_key"] = api_key
				data["login"] = login
				file.seek(0)
				json.dump(data, file, indent=4)
				file.truncate()
		except FileNotFoundError:
			print(f"Error: The file {file_path} was not found.")
		except json.JSONDecodeError:
			print("Error: The file is not a valid JSON document.")


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
