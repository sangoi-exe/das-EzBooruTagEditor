# das-EzBooruTagEditor

<p align="center">
  <img src="https://github.com/DevArqSangoi/das-EzBooruTagEditor/blob/main/preview.png" alt="Screenshot">
</p>


## Introduction
This application is designed to accelerate and simplify the management of Booru-style tags, primarily for fine-tuning Stable Diffusion models where tags play a crucial role, often more significant than the actual image dataset.

## Current Status
The app is in its final stages of adjustment and testing before the code becomes publicly available. It's a large and somewhat complex single-file codebase, chosen for its simplicity due to the low data flow involved.

## Operation Guide

### Starting Up
- **Select Folder**: From the home screen, choose the folder containing images and their respective text files (.txt).

### Managing Tags
- **Viewing and Selecting Tags**:
  - The left-hand list populates with text files having corresponding images.
  - Selecting a list item displays the image and tags.
- **Editing Tags**:
  - **Delete**: Click a tag once to select, and again to delete.
  - **Undo Deletion**: Click 'Undo' or use 'Ctrl+Z'.
  - **Add Tag**: Enter the tag in the text box and press "Add Tag" or "Enter". Unique tags are added to a unique list; similar tags are grouped.

### Navigation
- Navigate images using the list, keyboard arrows, or mouse scroll within the image frame.

### Saving and Grouping
- **Save Changes**: Press 'Save' or use 'Ctrl+S'.
- **Tag Grouping**: The app groups tags with common words (e.g., "blue hair" and "white hair") to ease removing redundant or incorrect automatic tags.
  - Note: Tags may be grouped multiple times for analysis ease.

### Important Notes
- **Non-Real-Time Editing**: Changes are not real-time; navigate away to discard large mistakes.
- **Save Before Switching**: Unsaved changes are lost when switching images. Future updates may include memory-based temporary saving.

## Future Plans
The app aims to introduce memory-based modifications to prevent loss of unsaved changes when switching between images.

This work is licensed under a
[Creative Commons Attribution-NonCommercial-ShareAlike 4.0 International License][cc-by-nc-sa].

[![CC BY-NC-SA 4.0][cc-by-nc-sa-shield]][cc-by-nc-sa]

[![CC BY-NC-SA 4.0][cc-by-nc-sa-image]][cc-by-nc-sa]

[cc-by-nc-sa]: http://creativecommons.org/licenses/by-nc-sa/4.0/
[cc-by-nc-sa-image]: https://licensebuttons.net/l/by-nc-sa/4.0/88x31.png
[cc-by-nc-sa-shield]: https://img.shields.io/badge/License-CC%20BY--NC--SA%204.0-lightgrey.svg
