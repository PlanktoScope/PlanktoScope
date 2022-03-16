# Software Interface Node-RED
This section is a list of the various changes and improvements to the Planktoscope software and the reasons for them.

The Node-Red software interface has undergone many changes, we started from version 2.3 with the integrated segmenter. The most notable one, which affects all pages, is the introduction of a beginner/expert mode to make the system easier to use but still perform well for professionals. The Gallery page has been completely revised and a download page has been created. Here we list the changes you will find on each page.

## Quick sumery
- Simplification and embellishment of several tabs
- Implementation of a button to switch from a beginner mode to an expert mode. This beginner mode simplifies the interface by hiding and pre-filling several fields to make the device more accessible (specific to the lacoscope project). Expert mode is the basic mode with all the functionalities.
- Implementation of a new gallery with simplified access, backspace and a next and previous button to browse the images.
- Implementation of a download tab to download and delete specific folders with a progress bar that indicates the amount of data downloaded.

### Home

- Expert / beginner button controlling the mode on all pages.
- Double check for mode selection for security.
- Added icons and links for each page (depending on the selected mode)

### Sample

- Beginner mode appearance 
- Expert mode appearance
- Added location, date and time prefill options.
- GPS modification

### Optic Configuration

- Beginner mode appearance 
- Expert mode appearance
- Complete change of the interface
  - Button layout (left and right horizontal button)
  - Text
- Beginner mode appearance 
- Expert Mode Appearance

### Fluidic Acquisition 

- Beginner mode appearance 
- Expert mode appearance
- Change of the pumped volume selection mode (slide -> arrows).
- Repeated information from hidden sample in expert mode
- Link to segmentation page

### Segmentation

- Beginner mode appearance 
- Expert mode appearance
- Removal of the graphic that we think is not necessary.
- Correction of the segmenter code to take into account the different parameters (segmenter/__init__.py fonction treat_message)
- Link to gallery or download page

### NEW Gallery

- Changed the gallery page to integrate it to the Node-Red
    - File browsing in 4 windows
    - Objects or images buttons to facilitate access.
    - Display images when selected
    - Buttons to browse images (previous/continue)
    - Links to the download page

### **NEW** Download Files

- Adding the download file page so you don't have to download everything every time.
    - Selection of files on 3 windows corresponding to the depth of the Path of the files.
    - Button to select all, images or objects.
    - Status of download to know where it is.
    - Possibility to download or delete the folder selected
    - Link to home

### System Monitoring

- Reorganization of the page for better readability

### Administration

- Beginner mode appearance 
- Expert mode appearance
- Increase the size of the logs to be easier to read.
- In beginner mode, Github repository is hidden.

### Hardware Settings

- Added custom mode for calibration
- Removed the choice of the lens because it was transferred to the optic configuration page
- Added the different PlanktoScope of the Lacoscope project
