
# About


# Todo
## Next steps
* x Slider for image
* x Export Image File (check overwrite?)
* x Export/reload marks with image
* x Chek into github
* x make starter + parse command line


* more tests before refactorig
  * Gui tests
  * E2E test (open, play, mark, save, load?)
    * with Mock or real HD?
* E2E tests, GUI tests, Functional tests
* Refactor
  * Extract modules: datamodel, io, gui, datatypes?

* Add chapters (save + reload)
* Save description text

* starter: without param take arguent as file
* Expand to audio only files?


* Scale preview correctly
* Fix strange offset of marks when setting time

* Slider for audio (Workarund -> OS Gui)

## Basic Fuctionality
* Open file
  * as command parameter
  * from file menu
    * Select all video filetypes
* Export Image File
  * filename same as image
  * select filetype (+ compression? jpeg, 40% default)
  * select x size
  * select max geometry (for scaling)


## Advanced
### Technical
* reference file per hash 
* Extract Modules
  * Player
  * Data model
  * Gui part from main app
  
* Functional Tests
  * Player


### Gui Stuff
* Sub dialogs
  * Store preferences for each file (in Yaml files)
  * Store application wide preferences
* Keyboard shortcuts
* Forward/back buttons (+-1s +-5s,...)
* Beautify slider
  * Ticks ?

Make the gui nice....maybe....some time....:)

### Data model + Yaml file description
* Add chapters (+ chapter description?)
* Extract marks filename, filepath, etc into datamodel
* Yaml export of data model
* yaml import of model with file

* save model whithout image export?
* export images with/without question (save/save as functionality???)
* autosave?

### Extract
* Select region for frames (per chapter?)

#### Filelist/Playlist 
- Open direcory (commandline + from dialog)
- Open File = Add file? Or start new list?
- Remove selecte from List?plugins
- Mark files without yaml file?
- Mark finished/in progressf Files?

