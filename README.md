# EleNa

EleNa is an elevation-based navigation system that determines, given a start and end location, a route that maximizes or minimizes elevation gain while limiting the toal distance between the two locations to x% of the shortest path.

![EleNa Demo](https://user-images.githubusercontent.com/41837625/145832370-d8d49935-b391-45fd-b63e-ae037f0f20ec.gif)

## Backend

The backend makes use of a conda environment, so miniconda or anaconda must be installed. To download the dependencies for the conda environment, use the following command:  
`conda env update --file environment.yml --prune`

Once installed, activate the environment using one of the following commands (depending on your os):  
`conda activate ox`  
`activate ox`

To run the Flask server use:  
 `python app.py`


## Frontend

To install the frontend dependencies use:  
 `npm install`

Once installed, run the React client using:  
 `npm start`

 Open [http://localhost:3000](http://localhost:3000) to view the application in the browser.