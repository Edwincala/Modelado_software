from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
from sklearn.linear_model import LinearRegression
from sklearn.preprocessing import LabelEncoder
import streamlit as st
import os

service = Service(executable_path="C:\\Users\\edwin\\Downloads\\chromedriver-win64\\chromedriver-win64\\chromedriver.exe")

def actualizar_info():
    df = pd.DataFrame()

    driver = webdriver.Chrome(service=service)


    driver.get('https://www.properati.com.co/s/bogota-d-c-colombia/casa/venta')
    
    wait = WebDriverWait(driver, 10)
    elemento = wait.until(EC.presence_of_element_located((By.XPATH, '/html/body/main/div[2]/div/div[2]/section')))
    texto_elemento = elemento.text
    driver.close()

    lista_elementos = texto_elemento.split("\n/")[1:]
    # print(len(lista_elementos))
    # print(lista_elementos)

    lista_propiedades = list()
    for elem in lista_elementos:
        elemento = elem.strip().split("\n")
        lista_propiedades.append(elemento)

    data_dict = dict()
    data = pd.DataFrame()

    for elem in lista_propiedades:
        data_dict['id'] = int(elem[0])
        data_dict['title'] = elem[1]
        data_dict['price'] = float(elem[2].strip().split(" ")[1].replace(".", ""))
        data_dict['location'] = elem[3].strip().split(",")[0]
        data_dict['bedrooms'] = int(elem[4].strip().split(" ")[0])
        data_dict['bathrooms'] = float(elem[5].strip().split(" ")[0].replace(",", "."))
        if elem[6].endswith('m²'):
            data_dict['area'] = int(elem[6].strip().split(" ")[0].replace(".", ""))
            data_dict['agency'] = elem[7]
            data_dict['date'] = elem[8]
        else: 
            data_dict['area'] = 0 
            data_dict['agency'] = elem[6]
            data_dict['date'] = elem[7]
        data = data._append(data_dict, ignore_index=True)
        
        data.to_csv('info.csv', index=False)
        
if not os.path.exists('info.csv') or st.button("Actualizar información"):
    actualizar_info()


data=pd.read_csv('info.csv')
location_encoder = LabelEncoder()
data["location_code"] = location_encoder.fit_transform(data['location'])

model = LinearRegression()
model.fit(data[["area", "bedrooms", "bathrooms", "location_code"]], data["price"])
y_pred = model.predict(data[["area", "bedrooms", "bathrooms", "location_code"]])

st.title("Calcula el precio de tu casa en Bogotá")


habitaciones = st.slider("Número de habitaciones", 1, 15)
banos = st.slider("Número de baños", 1, 8)
area = st.slider("Área en metros cuadrados", 20, 5000)
locacion = st.selectbox("Ubicación", range(len(location_encoder.classes_)), format_func=lambda x: location_encoder.classes_[x])

prediction = model.predict([[area, habitaciones, banos, locacion]])

st.write("El precio estimado es: $" + str(round(float(np.abs(prediction[0])),2)))

st.title("Proyecciones")

st.text("¿Cómo varía el precio con respecto al área?")

st.scatter_chart(data=data, x='area', y='price')

st.text("¿Cómo varía el precio con respecto al número de habitaciones?")

st.scatter_chart(data=data, x='bedrooms', y='price')

st.text("¿Cómo varía el precio con respecto al número de baños?")

st.scatter_chart(data=data, x='bathrooms', y='price')

st.text("¿Cómo varía el precio con respecto a la ubicación?")

st.scatter_chart(data=data, x='location', y='price')

