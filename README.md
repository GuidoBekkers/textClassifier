# Methods of AI Research Team Project @ Utrecht University
### Team 07 - Alexander Kern (5711088), Guido Bekkers (6232590), Martijn Dekker (6013368) and Thomas Voets (5535891).

This an the implementation of a dialog system, which is part of the group project of the Methods in Artificial Intelligence Research (MAIR) course at Utrecht University.

#### Running
The dialog classifier is implemented in the mair_main.py file. One can run this file using the following command in the command line: `python mair_main.py CLASSIFIER`. Where `CLASSIFIER` is either one of `majority`, `rule`, `tree`, `svm` or `mlp`.

The script `load_and_preprocess.py` implements a function which loads in the .dat file into a pandas dataframe and preprocesses the data. The function returns a pandas dataframe which can be used by the models and baselines systems.

The other python scripts are standalone versions of the dialog classifier, each one for a model.