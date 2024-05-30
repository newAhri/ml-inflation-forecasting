#!/usr/bin/env python
# coding: utf-8

# In[1]:


# bibliotēka datu apstrādei
import pandas as pd

# bibliotēka SARIMAX izmantošanai
from statsmodels.tsa.statespace.sarimax import SARIMAX

# bibliotēka AR(1) izmantošanai
from statsmodels.tsa.ar_model import AutoReg

# bibliotēka darbā ar kļūdu rādītāju 
from sklearn.metrics import mean_squared_error

# bibliotēka grafiku veidošanai
import matplotlib.pyplot as plt

# bibliotēka autokorelācijas funkciju attēlošanai
from statsmodels.graphics.tsaplots import plot_acf

# bibliotēka statistiskai modelēšanai un analīzei
import statsmodels.api as sm

# bibliotēka Ljung-Box testa veikšanai autokorelācijas diagnosticēšanai
from statsmodels.stats.diagnostic import acorr_ljungbox

# bibliotēka matemātiskajām operācijām
import numpy as np


# In[ ]:


f_cost_of_living = "interpol_cost_of_living.csv"
f_fuel_prices = "output_fuel_prices.csv"
f_electricity_prices = "output_electricity_prices.csv"
f_cpi = "interpol_cpi.csv"


# In[2]:


# korelācijas slieksnis
threshold = 0.5

# apmācības un validācijas kopu sadalīšanas proporcija
split_ratio = 0.8

# hiperparametri
p = 1
d = 1
q = 1
P = 1
D = 1
Q = 1
s = 7


# In[3]:


# datu pirmsapstrāde - tukšo vērtību noraidīšana
def load_and_preprocess(file_path):
    df = pd.read_csv(file_path, parse_dates=['date'], index_col='date')
    df = df.dropna()
    return df

cost_of_living = load_and_preprocess(f_cost_of_living)
fuel_prices = load_and_preprocess(f_fuel_prices)
electricity_prices = load_and_preprocess(f_electricity_prices)
cpi = load_and_preprocess(f_cpi)


# In[4]:


# datu diapazonu pārbaudīšana
print("cost of living date range:", cost_of_living.index.min(), "to", cost_of_living.index.max())
print("fuel data date range:", fuel_prices.index.min(), "to", fuel_prices.index.max())
print("local electricity price date range:", electricity_prices.index.min(), "to", electricity_prices.index.max())
print("CPI date range:", cpi.index.min(), "to", cpi.index.max())


# In[5]:


# datu sakārtošana pēc diapazoniem
start_date = max(cpi.index.min(), cost_of_living.index.min(), electricity_prices.index.min(), fuel_prices.index.min())
end_date = min(cpi.index.max(), cost_of_living.index.max(), electricity_prices.index.max(), fuel_prices.index.max())


# In[6]:


# datu sadalīšana vienādos datumu ietvaros
cost_of_living = cost_of_living[start_date:end_date]
fuel_prices = fuel_prices[start_date:end_date]
electricity_prices = electricity_prices[start_date:end_date]
cpi = cpi[start_date:end_date]


# In[7]:


# datu dimensiju pārbaudīšana - 1.dimensijām jābūt vienādām 
print("cost of living shape", cost_of_living.shape)
print("fuel prices shape", fuel_prices.shape)
print("electricity price shape", local_electricity_price.shape)
print("CPI shape", cpi.shape)


# In[8]:


# endogēnu un eksogēnu datu savienošana pēc datumiem
data = cpi.join([cost_of_living, electricity_price, fuel_prices], how='inner')

# korelācijas aprēķināšana
correlations = data.corr()
points_correlations = correlations['points']


# In[10]:


# prediktoru izvēlēšana
selected_predictors = points_correlations[points_correlations.abs() > threshold].index
if 'points' in selected_predictors:
    selected_predictors = selected_predictors.drop('points')

print("selected predictors:\n", selected_predictors)

# datu filtrēšana pēc korelācijas
data_selected = data[['points'] + list(selected_predictors)]
data_selected = data_selected.dropna()


# In[11]:


# datu sadalīšana apmācības un validācijas kopās
split_index = int(len(data_selected) * split_ratio)
train_data = data_selected.iloc[:split_index]
val_data = data_selected.iloc[split_index:]

# endogēnu un eksogēnu datu sadalīšana kopās
train_end = train_data['points']
train_ex = train_data.drop(columns=['points'])
val_end = val_data['points']
val_ex = val_data.drop(columns=['points'])


# In[12]:


# SARIMAX modelēšana
model = SARIMAX(train_end, ex=train_ex, order=(p, d, q), seasonal_order=(P, D, Q, s))
result = model.fit()

# grafiskā diagnostika analīzei
result.plot_diagnostics(figsize=(10,7))
plt.show()


# In[42]:


# atlikumu analīze
residuals = result.resid
acorr_ljungbox(residuals, np.arange(1, 11, 1))


# In[15]:


# prognozēšana un validācija
val_predictions = result.predict(start=val_ex.index[0], end=val_ex.index[-1], ex=val_ex)


# In[45]:


# RMSFE kļūdas aprēķināšana RMSFE
rmsfe = np.sqrt(mean_squared_error(val_end, val_predictions))
print(f'RMSFE: {rmsfe}')

# RMSPE kļūdas aprēķināšana 
rmspe = np.sqrt(np.mean(np.square((val_endog - val_predictions) / val_endog)))
print(f'RMSPE: {rmspe}')


# In[64]:


# modelēšana ar AR(1) etalonmodeli
split_index = int(len(data_selected) * split_ratio)

train_data = data_selected.iloc[:split_index]
val_data = data_selected.iloc[split_index:]

train_end = train_data['points']
val_end = val_data['points']

ar_model = AutoReg(train_end, lags=1).fit()

print(ar_model.summary())

val_predictions = ar_model.predict(start=len(train_end), end=len(train_end) + len(val_end) - 1, dynamic=False)


# In[ ]:


rmsfe = np.sqrt(mean_squared_error(val_end, val_predictions))
print(f'RMSFE: {rmsfe}')

rmspe = np.sqrt(np.mean(np.square((val_end - val_predictions) / val_end)))
print(f'RMSPE: {rmspe}')

