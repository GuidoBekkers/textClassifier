# Methods of AI Research Team Project @ Utrecht University
### Team 07 - Alexander Kern (5711088), Guido Bekkers (6232590), Martijn Dekker (6013368) and Thomas Voets (5535891).

This an the implementation of a dialog system, which is part of the group project of the Methods in Artificial Intelligence Research (MAIR) course at Utrecht University.

#### Requirements
The necessary requirements for MacOS and Windows can be installed at once using one of the following commands: 'pip install -r mac_requirements.txt' or 'pip install -r windows_requirements.txt'. 

#### Dialog system
The dailog system is implemented in the dialog_system.py file. One can run this file using the following command in the command line: `python dialog_system.py`. 

The keyword and pattern matching functions that are implemented can be found in the main `dialog_system.py` script. 

The csv lookup function is implemented in `lookup.py` file. The implemented function loads in the .csv file and returns a list of restaurants that match the inputted preferences. 

#### Dialog Classifier
The dialog classifier is implemented in the mair_main.py file. One can run this file using the following command in the command line: `python mair_main.py CLASSIFIER`. Where `CLASSIFIER` is either one of `majority`, `rule`, `tree`, `svm` or `mlp`.

The script `load_and_preprocess.py` implements a function which loads in the .dat file into a pandas dataframe and preprocesses the data. The function returns a pandas dataframe which can be used by the models and baselines systems.

The other python scripts are standalone versions of the dialog classifier, each one for a model.

The evaluation of these different baseline and machine learning classifier are done using a jupyter notebook called Evaluation.ipynb. The evaluation will later on be described in the final technical report. 
