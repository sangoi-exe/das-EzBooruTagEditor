# das-EzBooruTagEditor

<p align="center">
  <img src="https://github.com/DevArqSangoi/das-EzBooruTagEditor/blob/main/preview.png" alt="Screenshot">
</p>


## Introduction
This application is designed to accelerate and simplify the management of Booru-style tags, primarily for fine-tuning Stable Diffusion models where tags play a crucial role, often more significant than the actual image dataset.

## Installation

You can set up das-EzBooruTagEditor on your system in two ways:

### Option 1: Using the Executable
- **Download the Executable**: Go to the [Releases](https://github.com/DevArqSangoi/das-EzBooruTagEditor/releases) page and download the latest `.exe` file.
- **Run**: Double-click the downloaded file to run the application. No installation or Python environment required.

### Option 2: Cloning the Repository
- **Clone the Repository**: Run `git clone https://github.com/DevArqSangoi/das-EzBooruTagEditor.git` to clone the repository to your local machine.
- **Navigate to the Directory**: Change to the directory where the repository was cloned. E.g., `cd das-EzBooruTagEditor`.
- **Install Dependencies**: Install the Pillow library by running `pip install Pillow` in your command line. This is necessary for image processing.
- **Run the Script**: Execute the script with `python EzBooruTagEditor.py`.
## Operation Guide

### Starting Up
- **Select Folder**: From the home screen, choose the folder containing images and their respective text files (.txt).
![Choose Dir](https://github.com/DevArqSangoi/das-EzBooruTagEditor/blob/main/choose_dir.gif)

### Managing Tags
- **Viewing and Selecting Tags**:
  - The left-hand list populates with text files having corresponding images.
  - Selecting a list item displays the image and tags.
- **Editing Tags**:
  - **Delete**: Click a tag once to select, and again to delete.
  ![Delete](https://github.com/DevArqSangoi/das-EzBooruTagEditor/blob/main/delete.gif)
  - **Undo Deletion**: Click 'Undo' or use 'Ctrl+Z'.  
  ![Undo](https://github.com/DevArqSangoi/das-EzBooruTagEditor/blob/main/undo.gif)
  - **Add Tag**: Enter the tag in the text box and press "Add Tag" or "Enter". Unique tags are added to a unique list; similar tags are grouped.
  ![Add](https://github.com/DevArqSangoi/das-EzBooruTagEditor/blob/main/add_tag.gif)
  

### Navigation
- Navigate through images using (in the order of navigation shown in the gif) mouse scroll with the cursor on the image frame, by clicking in the list, with the keyboard arrows (up and down), or by using the buttons on the interface.
![Navigation](https://github.com/DevArqSangoi/das-EzBooruTagEditor/blob/main/navigate.gif)

### Saving and Grouping
- **Save Changes**: Press 'Save' or use 'Ctrl+S'.
- **Tag Grouping**: The app groups tags with common words (e.g., "blue hair" and "white hair") to ease removing redundant or incorrect automatic tags.
  - Note: Tags may be grouped multiple times for analysis ease.

### Important Notes
- **🛑 Backup First**: **Always back up your tag files before using this app.** This step is crucial to protect your data against any unintended changes.
- **Non-Real-Time Editing**: Changes are not real-time; navigate away to discard large mistakes.
- **Save Before Switching**: Unsaved changes are lost when switching images. Future updates may include memory-based temporary saving.

## Future Plans
I plan to introduce memory-based modifications in the app to prevent the loss of unsaved changes when switching between images.
  
<br />
  
## License
This work is licensed under a [Creative Commons Attribution-NonCommercial-ShareAlike 4.0 International License][cc-by-nc-sa].

[![CC BY-NC-SA 4.0][cc-by-nc-sa-shield]][cc-by-nc-sa]

[![CC BY-NC-SA 4.0][cc-by-nc-sa-image]][cc-by-nc-sa]

[cc-by-nc-sa]: http://creativecommons.org/licenses/by-nc-sa/4.0/
[cc-by-nc-sa-image]: https://licensebuttons.net/l/by-nc-sa/4.0/88x31.png
[cc-by-nc-sa-shield]: https://img.shields.io/badge/License-CC%20BY--NC--SA%204.0-lightgrey.svg
