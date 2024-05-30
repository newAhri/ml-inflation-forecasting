#!/usr/bin/env python
# coding: utf-8

# In[63]:


# bibliotēka datu apstrādei
import pandas as pd


# In[ ]:


data_file1 = 'output_cpi.csv'
data_file2 = 'output_cost_of_living.csv'

output_file1 = 'interpol_cost_of_living.csv'
output_file2 = 'interpol_cpi.csv'


# In[ ]:


def interpolate_data(input_file, output_file):
    # lejuplādēsāna
    df = pd.read_csv(input_file)

    # datumu pārveidošana t periodos
    df['Date'] = pd.date_range(start='2024-01-02', periods=len(df), freq='MS')
    df.set_index('Date', inplace=True)
    df.drop(columns=['t'], inplace=True)

    # ikdienas diapazona izveide
    daily_index = pd.date_range(start=df.index.min(), end=df.index.max(), freq='D')
    df_daily = df.reindex(daily_index)

    # datu splaina interpolācija, 3.kārta
    for column in df.columns:
        df_daily[column] = df_daily[column].interpolate(method='spline', order=3)

    # datu saglabāšana
    df_daily.to_csv(output_file)


# In[ ]:


def main():
    interpolate_data(data_file1, output_file1)
    interpolate_data(data_file2, output_file2)


# In[ ]:


if __name__ == "__main__":
    main()

