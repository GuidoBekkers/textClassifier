# Methods of AI Research Team Project @ Utrecht University
### Team 07 - Alexander Kern (5711088), Guido Bekkers (6232590), Martijn Dekker (6013368) and Thomas Voets (5535891).

This an the implementation of a dialog system, which is part of the group project of the Methods in Artificial Intelligence Research (MAIR) course at Utrecht University.


#### Dialog system
The dailog system is implemented in the dialog_system.py file. One can run this file using the following command in the command line: `python dialog_system.py`. 

#### Dialog classifier evaluation
The dialog classifier is implemented in the dialogActClassifcation.py file. One can run this file using the following command in the command line: `python dialogActClassification.py CLASSIFIER`. Where `CLASSIFIER` is either one of `majority`, `rule`, `tree`, `svm` or `mlp`. Note: This just loads the trained classifiers from their .joblibs files. One can analyse the training of the classifiers in `evaluation.py`.

The evaluation of these different baseline and machine learning classifier are done using a jupyter notebook called `Evaluation.ipynb`. The evaluation will is described in the final technical report. One can also view this evaluation in python script called `evaluation.py`.
