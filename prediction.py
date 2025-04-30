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
    numeric_data = data_input[:9]
    categoric_data = data_input[9:]

    # PCA
    pca1_result = list(pca1.transform([numeric_data[:6]])[0])  # pca1_1, pca1_2
    pca2_result = list(pca2.transform([numeric_data[6:8]])[0]) # pca2

    # PowerTransformer: pca1_1, pca1_2 disimpan terpisah
    transformed_age = transform_age.transform([[numeric_data[8]]])[0][0]
    transformed_pca1_1 = transform_pca1_1.transform([[pca1_result[0]]])[0][0]
    transformed_pca1_2 = transform_pca1_2.transform([[pca1_result[1]]])[0][0]
    transformed_pca2 = transform_pca2.transform([[pca2_result[0]]])[0][0]

    transformed_vals = [
        transformed_age,
        transformed_pca1_1,
        transformed_pca1_2,
        transformed_pca2
    ]

    # Kategorikal → One-hot Encoding
    df.loc[len(df)] = categoric_data
    new_df = pd.get_dummies(df, dtype="int")

    # Pastikan kolom selalu sama urutan dan jumlahnya
    for col in ["Debtor_Tidak", "Debtor_Ya", 
                "Tuition_fees_up_to_date_Tidak", "Tuition_fees_up_to_date_Ya", 
                "Gender_Laki-laki", "Gender_Perempuan", 
                "Scholarship_holder_Tidak", "Scholarship_holder_Ya"]:
        if col not in new_df.columns:
            new_df[col] = 0

    encoded_data_list = list(new_df.iloc[-1][[
        "Debtor_Tidak", "Debtor_Ya",
        "Tuition_fees_up_to_date_Tidak", "Tuition_fees_up_to_date_Ya",
        "Gender_Laki-laki", "Gender_Perempuan",
        "Scholarship_holder_Tidak", "Scholarship_holder_Ya"
    ]])

    # Gabung semua fitur (numerik + kategorikal)
    all_features = transformed_vals + encoded_data_list

    # Kolom total 4 (numerik) + 8 (kategorikal) = 12
    # Jika sebelumnya Anda pernah menyimpan 17 fitur, mungkin ada tambahan numerik lainnya?
    # Misalnya: ditambah `Admission_grade`, `enrolled_total`, dll?
    # Kalau tidak, pastikan yang sekarang **match** persis saat Anda fit model sebelumnya

    # Dummy kolom tambahan jika dibutuhkan 17 fitur
    while len(all_features) < 17:
        all_features.append(0)  # isi dummy 0 agar pas 17 fitur

    columns = [  # Anda harus pastikan urutan ini sesuai saat model dilatih
        'Transformed_Age_at_enrollment',
        'Transformed_pca1_1',
        'Transformed_pca1_2',
        'Transformed_pca2',
        'Debtor_Tidak', 'Debtor_Ya',
        'Tuition_fees_up_to_date_Tidak', 'Tuition_fees_up_to_date_Ya',
        'Gender_Laki-laki', 'Gender_Perempuan',
        'Scholarship_holder_Tidak', 'Scholarship_holder_Ya',
    ] + [f'dummy_{i}' for i in range(17 - len(transformed_vals + encoded_data_list))]

    preprocessed_data = pd.DataFrame([all_features], columns=columns)
    return preprocessed_data

def prediction(preprocessed_data, model=tree_model):
    array = np.array(preprocessed_data)
    result = model.predict(array)[0]
    return result
