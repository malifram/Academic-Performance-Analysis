import pandas as pd
import numpy as np
from joblib import load

cat_features_dict = {
    'Debtor': ['Tidak', 'Ya'],
    'Tuition_fees_up_to_date': ['Ya', 'Tidak'],
    'Gender': ['Perempuan', 'Laki-laki'],
    'Scholarship_holder': ['Ya', 'Tidak']
}

helper_df = pd.DataFrame(cat_features_dict)

# Load PCA
pca1 = load("data/enroll_approve_grade_1st_2nd")  # gabungan 6 fitur
pca2 = load("data/eval_1st_2nd")                  # evaluations

# Load Transformers
transform_age = load("data/Transformed_Age_at_enrollment")
transform_pca1_1 = load("data/Transformed_pca1_1")
transform_pca1_2 = load("data/Transformed_pca1_2")
transform_pca2 = load("data/Transformed_pca2")

# Model
tree_model = load("data/tree_model.joblib")

transformers = [
    transform_age,
    transform_pca1_1,
    transform_pca1_2,
    transform_pca2
]

def data_preprocessing(data_input, df=helper_df):
    numeric_data = data_input[:9]      # 9 nilai numerik
    categoric_data = data_input[9:]    # 4 nilai kategorik

    # PCA
    pca1_result = list(pca1.transform([numeric_data[:6]])[0])  # 6 kolom: enrolled + approved + grade
    pca2_result = list(pca2.transform([numeric_data[6:8]])[0]) # 2 kolom evaluations

    # Power Transform
    val_to_transformed_list = [numeric_data[8], *pca1_result, *pca2_result]  # age + pca1_1 + pca1_2 + pca2
    transformed_vals = []
    for transformer, val in zip(transformers, val_to_transformed_list):
        transformed_val = transformer.transform([[val]])[0][0]
        transformed_vals.append(transformed_val)

    # One-hot encoding
    df.loc[len(df)] = categoric_data
    new_df = pd.get_dummies(df, dtype="int")
    encoded_data_list = list(new_df.iloc[-1])

    # Final dataframe
    preprocessed_data = pd.DataFrame([[*transformed_vals, *encoded_data_list]],
        columns=['Transformed_Age_at_enrollment',
                 'Transformed_pca1_1',
                 'Transformed_pca1_2',
                 'Transformed_pca2',
                 'Debtor_Tidak',
                 'Debtor_Ya',
                 'Tuition_fees_up_to_date_Tidak',
                 'Tuition_fees_up_to_date_Ya',
                 'Gender_Laki-laki',
                 'Gender_Perempuan',
                 'Scholarship_holder_Tidak',
                 'Scholarship_holder_Ya'])

    return preprocessed_data


def prediction(preprocessed_data, model=tree_model):
    array = np.array(preprocessed_data)
    result = model.predict(array)[0]
    return result