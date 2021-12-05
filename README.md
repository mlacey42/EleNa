# EleNa

EleNa is an elevation-based navigation system that determines, given a start and end location, a route that maximizes or minimizes elevation gain while limiting the toal distance between the two locations to x% of the shortest path.

## Backend

The backend makes use of a conda environment, so miniconda or anaconda must be installed. To download the dependencies for the conda environment, use the following command:  
`conda env update --file environment.yml --prune`

Once installed, activate the environment using one of the following commands (depending on your os):  
`conda activate ox`  
`activate ox`

To run the backend server use:  
 `python app.py`