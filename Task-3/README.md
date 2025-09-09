Hello shabab, here's the task for this week:

Diabetes Classification Pipeline
Objective
Build a supervised learning pipeline to classify patients as diabetic or non-diabetic using the Diabetes dataset on Hugging Face.

Instructions
Preprocessing

- Load the dataset and inspect it.
- Handle missing values or incorrect data types if present.
- Encode the target variable appropriately.
- Normalization
- Apply feature scaling to all numeric features.
- Ensure the scaler is fit only on the training data.
- Data Splitting & Cross-Validation
- Use an appropriate train/validation/test split.
- Incorporate k-fold cross-validation for model evaluation.

Hyperparameter Tuning

- For each model, tune at least one or two key hyperparameters using grid search or random search.

Model Training
Train the following classifiers:

- SVM (test multiple kernels: linear, polynomial, RBF, sigmoid)
- Decision Tree
- Random Forest
- XGBoost
- k-NN
- Logistic Regression

Evaluation & Comparison:

- Evaluate using accuracy, precision, recall, F1-score, and confusion matrices.
- Compare models in a summary table and briefly discuss results.

Deliverable:

- A single Jupyter Notebook containing:
- Code for the full pipeline
- Results & comparisons
- Short written conclusions

Dataset: https://huggingface.co/datasets/weeebdev/diabetes

Happy learning!

You can also find last session's code here: https://github.com/M-Abdelmegeed/Konecta-DS-W03
And for those of you who are interested to know a bit more about forecasting, here you go: https://www.coursera.org/learn/time-series-mastery-forecasting-with-ets-arima-python
