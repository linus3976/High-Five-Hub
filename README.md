# HighFive

## Simplified autonumous delivery vehicule
ST5 project at CentraleSupélec

## Usage
To just follow the 8, use commit tagged v1
To use the latest revision of the Grid-navigator, use the handle_ObstacleException branch
Running main.py will prompt for start and endpoints as well as the initial direction.
If the battery is at another voltage and prevents the turns from being taken correctly, run calibration.py, this will calibrate the taken time and enable the main.py to correctly turn.

The coordinate system is considered such that (0,0) is the lower left corner, (4, 4) the top right for a grid of size 5, (4, 0) the top left and so on.
X is therfore the vertical position (from a topdown view), Y the horizontal.

## Authors and acknowledgment
We are group No. 5, thanks to CentraleSupélec and Renault for enabling this project.

## Project status
The project is over, there is of course stuff left to do...
