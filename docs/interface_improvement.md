#Software Interface Node-RED
This section is a list of the various changes and improvements to the Planktoscope software and the reasons for them.

The Node-Red software interface has undergone many changes. The most notable one, which affects all pages, is the introduction of a beginner/expert mode to make the system easier to use but still perform well for professionals. The Gallery page has been completely revised and a download page has been created. Here we list the changes you will find on each page.

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
  - Button layout
  - Text
- Beginner mode appearance 
- Expert Mode Appearance

### Fluidic Acquisition 

- Beginner mode appearance 
- Expert mode appearance
- Change of the pumped volume selection mode (slide -> arrows).
- Repeated information from hidden sample in expert mode

### Segmentation

- Beginner mode appearance 
- Expert mode appearance
- Removal of the graphic that we think is not necessary.
- Improvement of the folders interface
- Correction of the segmenter code to take into account the different parameters (segmenter/__init__.py fonction treat_message)

### NEW Gallery

- Changed the gallery page to integrate it to the Node-Red
    - File browsing in 4 windows
    - Objects or images buttons to facilitate access.
    - Display images when selected
    - Buttons to browse images
    - Links to the download page

### **NEW** Download Files

- Adding the download file page so you don't have to download everything every time.
    - Selection of files on 3 windows corresponding to the depth of the Path of the files.
    - Button to select all, images or objects.
    - Status of download to know where it is.
    - Link to home

### System Monitoring

- Reorganization of the page for better readability

### Administration

- Beginner mode appearance 
- Expert mode appearance
- Increase the size of the logs to be easier to read.
- In beginner mode, choose the hidden Github repository

### Hardware Settings

- Added manual mode for calibration
- Removed the choice of the lens because it was transferred to the sample page
- Added the different PlanktoScope of the Lac0scope project
