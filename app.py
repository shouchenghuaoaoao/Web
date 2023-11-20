import streamlit as st
import plotly.express as px
from pysurvival.utils import load_model
import pandas as pd
import numpy as np

st.set_page_config(layout="wide")

if 'model_deep' not in st.session_state:
    st.session_state["DeepSurv"] = load_model('DeepSurv.zip')
    st.session_state["NMTLR"] = load_model('NMTLR.zip')


if 'patients' not in st.session_state:
    st.session_state['patients'] = []
if 'display' not in st.session_state:
    st.session_state['display'] = 1


def get_select1():
    dic = {
        "Age": ["≤ 66", "> 66, ≤ 77", "> 77"],
        "Race": ["American Indian/Alaska Native", "Asian or Pacific Islander",
                 "Black", "White"],
        "Marital_status": ["Married", "Other"],
        "Histological_type": ["8170", "8171", "8172", "8173", "8174", "8175"],
        "Grade": ["Moderately differentiated; Grade II", "Poorly differentiated; Grade III",
                  "Undifferentiated; anaplastic; Grade IV", "Well differentiated; Grade I"],
        "T": ["T1", "T2", "T3a", "T3b", "T4"],
    }
    return dic


def get_select2():
    dic = {
        "N": ["N0", "N1"],
        "M": ["M0", "M1"],
        "AFP": ["Negative/normal; within normal limits", "Positive/elevated"],
        "Tumor_size": ["> 62 mm", "≤ 62 mm"],
        "Surgery": ["Lobectomy", "Local tumor destruction", "No", "Wedge or segmental resection"],
        "Chemotherapy": ["No/Unknown", "Yes"]
    }
    return dic


def plot_below_header():
    col1, col2 = st.columns([1, 9])
    col3, col4, col5, col6, col7 = st.columns([2, 2, 2, 2, 2])
    with col1:
        st.write('')
        st.write('')
        st.write('')
        st.write('')
        st.write('')
        st.write('')
        st.write('')
        st.write('')
        # st.session_state[''] = ['Single', 'Multiple'].index(
        #     st.radio("", ('Single', 'Multiple'), st.session_state['']))
        st.session_state['display'] = ['Single', 'Multiple'].index(
            st.radio("Display", ('Single', 'Multiple'), st.session_state['display']))
        # st.radio("Model", ('DeepSurv', 'NMTLR','RSF','CoxPH'), 0,key='model',on_change=predict())
    with col2:
        plot_survival()
    with col4:
        st.metric(
            label='1-Year survival probability',
            value="{:.2f}%".format(st.session_state['patients'][-1]['1-year'] * 100)
        )
    with col5:
        st.metric(
            label='3-Year survival probability',
            value="{:.2f}%".format(st.session_state['patients'][-1]['3-year'] * 100)
        )
    with col6:
        st.metric(
            label='5-Year survival probability',
            value="{:.2f}%".format(st.session_state['patients'][-1]['5-year'] * 100)
        )
    st.write('')
    st.write('')
    st.write('')
    plot_patients()
    st.write('')
    st.write('')
    st.write('')
    st.write('')
    st.write('')


def plot_survival():
    pd_data = pd.concat(
        [
            pd.DataFrame(
                {
                    'Survival': item['survival'],
                    'Time': item['times'],
                    'Patients': [item['No'] for i in item['times']]
                }
            ) for item in st.session_state['patients']
        ]
    )
    if st.session_state['display']:
        fig = px.line(pd_data, x="Time", y="Survival", color='Patients', range_y=[0, 1])
    else:
        fig = px.line(pd_data.loc[pd_data['Patients'] == pd_data['Patients'].to_list()[-1], :], x="Time", y="Survival",
                      range_y=[0, 1])
    fig.update_layout(title={
        'text': 'Estimated Survival Probability',
        'y': 1,
        'x': 0.5,
        'xanchor': 'center',
        'yanchor': 'top',
        'font': dict(
            size=25
        )
    },
        plot_bgcolor="LightGrey",
        xaxis_title="Time, month",
        yaxis_title="Survival probability",
    )
    st.plotly_chart(fig, use_container_width=True)


def plot_patients():
    patients = pd.concat(
        [
            pd.DataFrame(
                dict(
                    {
                        'Patients': [item['No']],
                        'Model': [item["use_model"]],
                        '1-Year': ["{:.2f}%".format(item['1-year'] * 100)],
                        '3-Year': ["{:.2f}%".format(item['3-year'] * 100)],
                        '5-Year': ["{:.2f}%".format(item['5-year'] * 100)]
                    },
                    **item['arg']
                )
            ) for item in st.session_state['patients']
        ]
    ).reset_index(drop=True)
    st.dataframe(patients)


with st.sidebar:
    col1, col2 = st.columns([5, 5])
    with col1:
        for _ in get_select1():
            st.selectbox(_, get_select1()[_], index=None, key=_)
    with col2:
        for _ in get_select2():
            st.selectbox(_, get_select2()[_], index=None, key=_)

st.header('DeepSurv for predicting cancer-specific survival of Osteosarcoma',
          anchor='Cancer-specific survival of osteosarcoma')
if st.session_state['patients']:
    plot_below_header()


def predict():
    model = st.session_state[st.session_state["model"]]
    input_keys = ['AFP', 'Age', 'Chemotherapy', 'Grade', 'Histological_type', 'M',
                  'Marital_status', 'N', 'Race', 'Surgery', 'T', 'Tumor_size']
    all_dic = dict(get_select1(), **get_select2())
    test_df = [all_dic[_].index(st.session_state[_]) for _ in input_keys]
    survival = model.predict_survival(test_df)[0]
    data = {
        'survival': survival,
        'times': [i for i in range(1, len(survival) + 1)],
        'No': len(st.session_state['patients']) + 1,
        'arg': {key: st.session_state[key] for key in input_keys},
        'use_model': st.session_state["model"],
        '1-year': model.predict_survival(test_df, t=12)[0],
        '3-year': model.predict_survival(test_df, t=36)[0],
        '5-year': model.predict_survival(test_df, t=60)[0],
    }
    st.session_state['patients'].append(
        data
    )
    print('update patients ... ##########')


with st.sidebar:
    st.selectbox("Please select model 👇", ["DeepSurv", "NMTLR"], key='model')
    prediction = st.button(
        'Predict',
        type='primary',
        on_click=predict,
        use_container_width=True
    )
