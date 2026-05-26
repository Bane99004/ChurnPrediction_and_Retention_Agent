import pandas as pd, openpyxl
import numpy as np
from sklearn.preprocessing import LabelEncoder, OneHotEncoder
from sklearn.compose import ColumnTransformer
from sklearn.preprocessing import StandardScaler
from sklearn.metrics import accuracy_score, precision_score, recall_score, roc_auc_score, classification_report
import matplotlib.pyplot as plt
from sklearn.model_selection import train_test_split
import joblib
cols_with_text = []

def seperate_features_output(df):
  data = df
  x = data.iloc[:, :-1]
  y = data.iloc[:, -1]
  return x, y
  
def encode_output(x_train, y_train, x_test, y_test, x_val, y_val):
  
  # le = LabelEncoder()
  # y_train = le.fit_transform(y_train)
  # y_test = le.transform(y_test)
  # y_val = le.trasform(y_val)
  
  x_sc = x_train.select_dtypes(include=["int64", "float64"]).columns
  x_cat = x_train.select_dtypes(include=['object', 'string', 'category']).columns
  
  x_train = x_train.copy()
  x_test = x_test.copy()
  x_val = x_val.copy()
  
  x_train[x_cat] = x_train[x_cat].astype(str)
  x_test[x_cat] = x_test[x_cat].astype(str)
  x_val[x_cat] = x_val[x_cat].astype(str)
  ct = ColumnTransformer(transformers = [('encoder', OneHotEncoder(handle_unknown='ignore', sparse_output=False, drop="first"), x_cat), ('scaling', StandardScaler(), x_sc)], remainder='passthrough')
  x_train = ct.fit_transform(x_train)
  x_test = ct.transform(x_test)
  x_val = ct.transform(x_val)
  feature_names = ct.get_feature_names_out()
  joblib.dump(ct, "transformer.pkl")
  return x_train, y_train, x_test, y_test, x_val, y_val, feature_names

def plot_features(df, features, target):
  for feature in features:
    plt.figure()
    plt.hist(df[df[target] == 0][feature], alpha = 0.5, label='No Churn')
    plt.hist(df[df[target]==1][feature], alpha = 0.5,  label="Churn")
    plt.title(f"Distribution of {feature}")
    plt.xlabel(feature)
    plt.ylabel("Frequency")
    plt.legend()
    plt.show()

def split_train_test(x, y):
  x_train, x_temp, y_train, y_temp = train_test_split(x, y , test_size=0.3, random_state=42, stratify=y)
  x_val, x_test, y_val, y_test = train_test_split(x_temp, y_temp, test_size=0.5, stratify=y_temp)
  return x_train, x_test, y_train, y_test, x_val, y_val

def drop_cols(df, col_name):
  df = df.drop(columns = col_name)
  return df

def seperate_x_y(df, output):
  y = df[output]
  x = df.drop(columns=[output])
  return x, y

def feature_importance(x_train, y_train, output_col, feature_names):
  df_x = pd.DataFrame(x_train,columns=feature_names)
  df_y = pd.DataFrame(y_train,columns=[output_col])
  train = pd.concat([df_x, df_y], axis=1)
  mean = train.groupby('Churn Value').mean(numeric_only=True)
  mean.to_csv("mean.csv")
  diff = abs((mean.loc[0] - mean.loc[1]))
  
  top10 = diff.sort_values(ascending = False).head(8)
  print(top10)
  # plot_features(train, top10.index, output_col)
  return 0
  
  
df = pd.read_excel("datasets/Telco_customer_churn.xlsx", engine='openpyxl')


col_names = ["Churn Label","Country", "Churn Reason", "Zip Code", "Count", "Latitude", "Longitude", "CustomerID", "State", "City", "Lat Long", "Contract", "Churn Score", "CLTV"]
output_col = "Churn Value"

df["Total Charges"] = pd.to_numeric(df["Total Charges"], errors='coerce')

df["Tenure Group"] = pd.cut(
  df["Tenure Months"],
  bins=[0,12,24,36,48,60,72],
  labels=["0-1yr", "1-2yr", "2-3yr", "3-4yr", "4-5yr", "5-6yr"]
)

services = [
    "Phone Service", "Internet Service", "Online Security",
    "Tech Support", "Streaming TV", "Streaming Movies", "Online Backup", "Device Protection", 
]

df["Total Services"] = (df[services] == "Yes").sum(axis=1).astype(str)


# df["Charge per Month"] = df["Total Charges"] / df["Tenure Months"].replace(0, np.nan)

# mean = df.groupby('Churn Value').mean(numeric_only=True)
# mean.to_csv("mean.csv")
# diff = abs((mean.loc[0] - mean.loc[1]))
# top10 = diff.sort_values(ascending = False).head(12)
# print(top10)
# print(df[output_col].value_counts())

df = drop_cols(df, col_names)
x, y= seperate_x_y(df, output_col)
x_train, x_test, y_train, y_test, x_val, y_val = split_train_test(x, y)

print("y_train output: ",y_train.value_counts())
print("y_test output: ", y_test.value_counts())

x_train, y_train, x_test, y_test, x_val, y_val, feature_names = encode_output(x_train, y_train, x_test, y_test, x_val, y_val)

# df = pd.DataFrame(x_train, columns=feature_names)
# print("---------------------------------",df)
# df_y = pd.DataFrame(y_train, columns=['Churn']) 
# print("Is null: ", x.isnull().sum())
# print("Features: ", df_train.info())

# feature_importance(x_train, y_train, output_col, feature_names)



# from sklearn.ensemble import RandomForestClassifier
# model = RandomForestClassifier(n_estimators=400,
#     class_weight='balanced',
#     random_state=42)
# model.fit(x_train, y_train)
# y_pred = model.predict(x_test)

# print("Accuracy score: ",accuracy_score(y_test, y_pred))
# print("Precision score: ",precision_score(y_test, y_pred))
# print("Recall score: ",recall_score(y_test, y_pred))

from xgboost import XGBClassifier
model = XGBClassifier(n_estimators= 2000, max_depth = 4, learning_rate=0.4, scale_pos_weight=2.78, eval_metric="logloss", random_state=42, early_stopping_rounds=20)
model.fit(x_train, y_train, eval_set=[(x_val, y_val)], verbose=True)

probs = model.predict_proba(x_test)[:,1]
threshold = 0.5
y_pred = (probs > threshold).astype(int)
print(threshold, "recall_score: ",recall_score(y_test, y_pred), "precision_score:", precision_score(y_test, y_pred))
print(f"ROC-AUC: {roc_auc_score(y_test, probs):.4f}")

print(classification_report(y_test, y_pred))
model.save_model('churn_model_v2.json')
import shap
explainer = shap.Explainer(model)
x_test_df = pd.DataFrame(x_test, columns=feature_names)
shap_values = explainer(x_test_df[:100])
shap.plots.beeswarm(shap_values, show=False)


# import matplotlib.pyplot as plt

# plt.savefig("beesswarm.png", bbox_inches='tight', dpi=300)
# plt.close()
# shap.plots.waterfall(shap_values[0], show=False)
# plt.savefig("waterfall.png", bbox_inches='tight', dpi=300)
# plt.close()

# importance = model.feature_importances_
# feat_imp = pd.Series(importance, index=feature_names).sort_values(ascending=False)

# print(feat_imp.head(10))
# import matplotlib.pyplot as plt

# no_churned=df_train['Churn'].value_counts(normalize=True).mul(100).round(1)
# print(no_churned)
