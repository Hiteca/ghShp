# Shapefile Import and Export for Grasshopper

![ghShp](https://github.com/Hiteca/ghShp/blob/master/shapefile128.png?raw=true)

## Description

Grasshopper plugin to import and export ESRI Shapefile. Plugin written in pyhton and using pyshp module. So GhPython and pyshp are needed to be installed.

## Dependencies

- GhPython http://www.food4rhino.com/app/ghpython
- pyshp https://github.com/GeospatialPython/pyshp

## Changelog

- 2017-10-12 Decimal number support, more examples
- 2017-08-27 Initial version


## Installation

### Install GhPython
Download last version from food4rhino http://www.food4rhino.com/app/ghpython. 
Tested with 0.6.0.3.

To install:

1. In Grasshopper, choose File > Special Folders > Components folder. Save the gha file there.

2. Right-click the file > Properties > make sure there is no "blocked" text

3. Restart Rhino and Grasshopper

### Install pyshp

Plugin developed for using in native python environment while Grasshopper is using IronPython. So installation of the module requires a bit of creativity.

1. Download pyshp zip achive https://github.com/GeospatialPython/pyshp/archive/1.2.12.zip

2. Extract it to C:\Users\\%USERNAME%\AppData\Roaming\McNeel\Rhinoceros\5.0\scripts\. Final path to shapefile.py should be ...Rhinoceros\5.0\scripts\shapefile.py

Then copy user object files, add to layout and check that it works.

### Install UserObjects

1. Download zip archive https://github.com/Hiteca/ghShp/archive/master.zip

2. In Grasshopper, choose File > Special Folders > User Objects folder. Save two .userobject files from zip into this folder.

3. New buttons will appears at "Extra" tab

## Contributing

Have any questions or ideas - please write to alex@hiteca.ru

Feel free to add bug issues and submit pull requests.

## Thank you

Before this code was published here it have already been implemented in some of the projects by many people. Thank you for participation and feedback.

A "core" of the code is pyshp module. We thank the people who develop it 
