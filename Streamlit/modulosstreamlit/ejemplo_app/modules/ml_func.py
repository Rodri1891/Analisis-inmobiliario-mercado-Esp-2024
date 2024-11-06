import streamlit as st
import pandas as pd
import os
import pickle
import base64
import sklearn

PAGE_CONFIG = {"page_title"             : "CO2 Emissions Model - Streamlit",
                "page_icon"             : ":robot_face:",
                "layout"                : "wide",
                "initial_sidebar_state" : "expanded"}

@st.cache_data
def read_data():

    lista_df = list()

    if not os.getcwd().endswith("sources"):
        os.chdir("sources")

    csv_files = [file for file in os.listdir() if file.endswith(".csv") and file.startswith("MY")]
    
    for file in csv_files:

        df_ = pd.read_csv(filepath_or_buffer = file, encoding = "latin1", header = 1)

        df_ = df_.iloc[:, :13]

        df_.dropna(inplace = True)

        df_.columns = ["Model Year", "Make", "Model", "Vehicle Class", "Engine Size", "Cylinders",
                       "Transmission", "Fuel Type", "Fuel Consumption City", "Fuel Consumption Hwy",
                       "Fuel Consumption Comb", "Fuel Consumption Comb (mpg)", "CO2 Emissions"]

        # Int Columns
        int_columns = ["Model Year", "CO2 Emissions"]

        # Float Columns
        float_columns = ["Engine Size", "Cylinders", "Fuel Consumption City", "Fuel Consumption Hwy",
                       "Fuel Consumption Comb", "Fuel Consumption Comb (mpg)"]
        
        # String Columns
        string_columns = ["Make", "Model", "Vehicle Class", "Transmission", "Fuel Type"]

        df_[int_columns] = df_[int_columns].astype(int)
        df_[float_columns] = df_[float_columns].astype(float)
        df_[string_columns] = df_[string_columns].astype(str)

        lista_df.append(df_)

    df = pd.concat(lista_df, ignore_index = True)
    df.drop_duplicates(inplace = True)

    fuel_type_dict = {"X" : "Reg. Gasoline", 
                      "Z" : "Prm. Gasoline",
                      "D" : "Diesel",
                      "E" : "Ethanol (E85)",
                      "N" : "Natural Gas"}

    df["Fuel Type"] = df["Fuel Type"].replace(fuel_type_dict)

    os.chdir("..")

    return df

def load_model(fuel_type):

    if not os.getcwd().endswith("sources"):
        os.chdir("sources")

    with open(file = f"{fuel_type}_X_scaler.pkl", mode = "rb") as file:
        X_scaler = pickle.load(file)

    with open(file = f"{fuel_type}_y_scaler.pkl", mode = "rb") as file:
        y_scaler = pickle.load(file)

    with open(file = f"{fuel_type}_model.pkl", mode = "rb") as file:
        model = pickle.load(file)

    os.chdir("..")
    
    return X_scaler, y_scaler, model

def download_file(df, fuel_type = "all"):

    csv = df.to_csv(index = False)
    b64 = base64.b64encode(csv.encode()).decode()
    href = f"<a href='data:file/csv;base64,{b64}' download='{fuel_type}_data.csv'>Download CSV File</a>"

    return href

