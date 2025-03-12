import json
from forex_python.converter import CurrencyRates
from datetime import datetime
import pandas as pd
from plotly.subplots import make_subplots
from IPython.display import HTML

BILLION = 1e9
FILE_PATH = '/Users/atash/Desktop/ukrain_aid_data.xlsx'
FOREX_DATA_PATH = '/Users/atash/Desktop/daily_forex_rates.csv'
SHEET_NAME = 'Bilateral Assistance, MAIN DATA'
SELECTED_COLUMNS = [
    'announcement_date', 
    'donor', 
    'reporting_currency', 
    'tot_activity_value', 
    'aid_type_general', 
    'aid_type_specific'
]

AID_TYPES = ['Military', 'Financial', 'Humanitarian']

def read_excel_sheet(file_path, sheet_name=None):

    try:
        df = pd.read_excel(file_path, sheet_name=sheet_name)
        
        return df
    
    except FileNotFoundError:
        print(f"Error: File not found at {file_path}")
        return None
    except Exception as e:
        print(f"An error occurred: {e}")
        return None


def align_aid_data(countries, mil_aid_countries, mil_aid_list):
    return [mil_aid_list[mil_aid_countries.index(country)] if country in mil_aid_countries else 0 for country in countries]

# First, clean the announcement_date column
def clean_date(date_str):
    if pd.isna(date_str):
        return None
    # If the date contains "until", extract just the date part
    if 'until' in str(date_str).lower():
        # Extract the date part after "until"
        date_part = date_str.lower().split('until')[-1].strip()
        return date_part
    return date_str

def preprocess_aid_data(df, selected_columns):
    # Select only needed columns
    processed_df = df[selected_columns].copy()
    
    # Standardize donor names
    processed_df['donor'] = processed_df['donor'].apply(
        lambda x: 'European Union' if x == 'EU (Commission and Council)' else x
    )

    processed_df = processed_df.rename(columns={'donor': 'country'})
    
    # Clean numeric values
    processed_df['tot_activity_value'] = (
        pd.to_numeric(processed_df['tot_activity_value'], errors='coerce')
        .fillna(0)
        .astype(int)
    )
    
    # Process dates
    processed_df['announcement_date'] = (
        processed_df['announcement_date']
        .apply(clean_date)
        .pipe(pd.to_datetime, errors='coerce')
        .dt.date
        .pipe(pd.to_datetime)
    )
    
    return processed_df

def merge_currency_data(df):
    currency_df = pd.read_csv(FOREX_DATA_PATH)
    currency_df['date'] = pd.to_datetime(currency_df['date'])

    df = pd.merge(df, currency_df, 
                        left_on=['announcement_date', 'reporting_currency'],
                        right_on=['date', 'currency'], 
                        how='inner') 

    df['tot_activity_value_eur'] = df['tot_activity_value']/df['exchange_rate']
    df['tot_activity_value_eur'] = df['tot_activity_value_eur'].round(2)

    return df

def shorten_billions(column):
    return (column / BILLION).round(1)
    
def get_top_countries(df, top_n):
    # Get top countries by total aid amount
    top_countries = (
        df.groupby('country')['tot_activity_value_eur']
        .sum()
        .nlargest(top_n)
        .reset_index()
    )
    
    # Convert to billions and round
    top_countries['tot_activity_value_eur_billions'] = shorten_billions(top_countries['tot_activity_value_eur'])
    
    return top_countries['country'].tolist()

def get_top_countries_data(df, top_n=8):
    data = {"countries": get_top_countries(df, top_n)}
    df = (df.groupby(['aid_type_general', 'country'])['tot_activity_value_eur'].sum()
          .reset_index()
          .query(f"country in {data['countries']}"))
    
    for aid_type in AID_TYPES:
        aid_type_key = aid_type.lower()

        type_df = df[df['aid_type_general'] == aid_type]

        if aid_type == 'Military':
            data[f"{aid_type_key}_aid_list"] = align_aid_data(data['countries'], 
                type_df["country"].tolist(), 
                (type_df["tot_activity_value_eur"] / BILLION).round(1).tolist())
        else:
            sorted_values = (type_df.set_index('country').reindex(data['countries']).fillna(0).reset_index())
            data[f"{aid_type_key}_aid_list"] = (sorted_values["tot_activity_value_eur"] / BILLION).round(1).tolist()

    return data

def calculate_general_stats(data, df):
    
    total_aid = (df["tot_activity_value_eur"] / BILLION).sum().round(1)
    data["total_aid"] = f"€{total_aid}B"
    aid_by_type = (df.groupby('aid_type_general')["tot_activity_value_eur"].sum().div(BILLION).round(1))

    for aid_type in AID_TYPES:
        aid_type_key = aid_type.lower() + '_aid'
        data[aid_type_key] = aid_by_type.get(aid_type, 0)
        percent_key = f"{aid_type_key.split('_')[0]}_percent"
        data[percent_key] = f"{round((data[aid_type_key] / total_aid) * 100)}%"
        data[aid_type_key] = f"€{data[aid_type_key]}B"
    
    return data


def get_quarterly_data(data):
    original_df['announcement_date'] = pd.to_datetime(original_df['announcement_date'])
    quarterly_totals = original_df.groupby(original_df['announcement_date'].dt.to_period('Q'))['tot_activity_value_eur'].sum().apply(lambda x: round(x/1000000000, 1)).tolist()
    
    data["aid_by_quarter"] = quarterly_totals
    
    return data

def collect_aid_data():
    df = read_excel_sheet(FILE_PATH, SHEET_NAME)
    df = preprocess_aid_data(df, SELECTED_COLUMNS)
    original_df = df = merge_currency_data(df)

    data = get_top_countries_data(df)
    data = calculate_general_stats(data, original_df)

    # original_df['announcement_date'] = pd.to_datetime(original_df['announcement_date'])
    # quarterly_totals = original_df.groupby(original_df['announcement_date'].dt.to_period('Q'))['tot_activity_value_eur'].sum().apply(lambda x: round(x/1000000000, 1)).tolist()
    
    # data["aid_by_quarter"] = quarterly_totals
  
    mil_breakdown_df = original_df[original_df['aid_type_general'] == 'Military']
    mil_breakdown_df = mil_breakdown_df.groupby('aid_type_specific')['tot_activity_value_eur'].sum().reset_index()
    mil_breakdown_df = mil_breakdown_df.nlargest(5, 'tot_activity_value_eur')
    sum = mil_breakdown_df['tot_activity_value_eur'].sum()
    mil_breakdown_df['total_activity_percent'] = ((mil_breakdown_df['tot_activity_value_eur']/sum) * 100).round()

    hum_breakdown_df = original_df[original_df['aid_type_general'] == 'Humanitarian']
    hum_breakdown_df = hum_breakdown_df.groupby('aid_type_specific')['tot_activity_value_eur'].sum().reset_index()
    hum_breakdown_df = hum_breakdown_df.nlargest(5, 'tot_activity_value_eur')
    sum = hum_breakdown_df['tot_activity_value_eur'].sum()
    hum_breakdown_df['total_activity_percent'] = ((hum_breakdown_df['tot_activity_value_eur']/sum) * 100).round()

    data["mil_breakdown_list"] = mil_breakdown_df['total_activity_percent'].to_list()
    data["mil_breakdown_names"] = mil_breakdown_df['aid_type_specific'].to_list()
    data["hum_breakdown_list"] =  hum_breakdown_df['total_activity_percent'].to_list()
    data["hum_breakdown_names"] =  hum_breakdown_df['aid_type_specific'].to_list()

    top_aid = original_df.nlargest(8, 'tot_activity_value_eur')[['announcement_date', 'country', 'aid_type_general', 'tot_activity_value_eur']]
    top_aid = top_aid.reset_index(drop=True)
    nested_dict = df_to_nested_dict(top_aid)
    
    data["top_aid"] = nested_dict
    
    # print(top_aid)

    with open('data.json', 'w') as json_file:
      json.dump(data, json_file)

def df_to_nested_dict(df):
    result = {}
    for i, row in df.iterrows():
        key = f"entry_{i}"  # You can customize the key naming scheme
        result[key] = {
            'announcement_date': row['announcement_date'].strftime('%b %Y'),
            'country': row['country'],
            'aid_type_general': row['aid_type_general'],
            'tot_activity_value_eur': f"€{round(row['tot_activity_value_eur']/1000000000, 1)}B"
        }
    return result
    
collect_aid_data()