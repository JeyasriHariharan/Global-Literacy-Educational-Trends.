import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt
import sqlite3

st.title("📊 Literacy & Education Analysis")

# Load raw data
adult_lit = pd.read_csv("literacy.csv")
youth_lit = pd.read_csv("literacy-rate-of-young-men-and-women.csv")
illiteracy = pd.read_csv("literate-and-illiterate-world-population.csv")
gdp = pd.read_csv("gdp-per-capita-worldbank.csv")
schooling = pd.read_csv("literacy-rates-vs-average-years-of-schooling.csv")

# Merge
df_literacy = pd.merge(adult_lit, youth_lit, on=["entity", "year"])
df_illiteracy = illiteracy.copy()
df_gdp = pd.merge(gdp, schooling, on=["entity", "year"])

# Rename
df_literacy = df_literacy.rename(columns={
    'adult_literacy_rate__population_15plus_years__both_sexes__pct__lr_ag15t99': 'adult_literacy',
    'youth_literacy_rate__population_15_24_years__male__pct__lr_ag15t24_m': 'youth_male',
    'youth_literacy_rate__population_15_24_years__female__pct__lr_ag15t24_f': 'youth_female'
})

df_gdp = df_gdp.rename(columns={
    'ny_gdp_pcap_pp_kd': 'gdp_per_capita',
    'mf_youth_and_adults__15_64_years__average_years_of_education': 'avg_schooling_years'
})

# Features
df_illiteracy['illiteracy_percent'] = 100 - df_illiteracy['literacy_rate']
df_gdp['gdp_per_schooling'] = df_gdp['gdp_per_capita'] / df_gdp['avg_schooling_years']

# Rename columns (important)
df_literacy = df_literacy.rename(columns={
    df_literacy.columns[3]: 'adult_literacy'
})

df_gdp = df_gdp.rename(columns={
    df_gdp.columns[3]: 'gdp_per_capita'
})

# Simple chart
st.subheader("📊 Literacy Distribution")
df_literacy['adult_literacy'].hist()
st.pyplot(plt)

# Scatter plot
st.subheader("📊 GDP vs Literacy")
# Merge data for correct plotting
merged = pd.merge(df_literacy, df_gdp, on=["entity", "year"])

st.subheader("📊 GDP vs Literacy")

plt.figure()
plt.scatter(merged['gdp_per_capita'], merged['adult_literacy'])
plt.xlabel("GDP per Capita")
plt.ylabel("Adult Literacy")
st.pyplot(plt)
st.pyplot(plt)

# SQL part
conn = sqlite3.connect(':memory:')
df_literacy.to_sql('literacy', conn, index=False)

st.subheader("📋 SQL Query")

# Create SQL tables
conn = sqlite3.connect(':memory:')

df_literacy.to_sql('literacy_rates', conn, index=False, if_exists='replace')
df_illiteracy.to_sql('illiteracy_population', conn, index=False, if_exists='replace')
df_gdp.to_sql('gdp_schooling', conn, index=False, if_exists='replace')
st.subheader("📋 SQL Queries Dashboard")

query_options = {

"Top 5 Countries with Highest Adult Literacy (2020)":
"SELECT entity, adult_literacy FROM literacy_rates WHERE year=2020 ORDER BY adult_literacy DESC LIMIT 5",

"Countries with Female Youth Literacy < 80%":
"SELECT entity, youth_female FROM literacy_rates WHERE youth_female < 80",

"Average Adult Literacy per Continent":
"SELECT owid_region, AVG(adult_literacy) FROM literacy_rates GROUP BY owid_region",

"Countries with Illiteracy > 20% in 2000":
"SELECT entity, illiteracy_percent FROM illiteracy_population WHERE year=2000 AND illiteracy_percent>20",

"Illiteracy Trend for India":
"SELECT year, illiteracy_percent FROM illiteracy_population WHERE entity='India'",

"Top 10 Countries with Highest Illiteracy":
"SELECT entity, illiteracy_percent FROM illiteracy_population ORDER BY illiteracy_percent DESC LIMIT 10",

"Countries with High Schooling but Low GDP":
"SELECT entity FROM gdp_schooling WHERE avg_schooling_years>7 AND gdp_per_capita<5000",

"GDP per Schooling Ranking (2020)":
"SELECT entity, gdp_per_schooling FROM gdp_schooling WHERE year=2020 ORDER BY gdp_per_schooling DESC",

"Global Average Schooling per Year":
"SELECT year, AVG(avg_schooling_years) FROM gdp_schooling GROUP BY year",

"Top GDP but Low Schooling Countries (2020)":
"SELECT entity FROM gdp_schooling WHERE year=2020 AND avg_schooling_years<6 ORDER BY gdp_per_capita DESC LIMIT 10",

"High Illiteracy despite High Schooling":
"SELECT g.entity FROM gdp_schooling g JOIN illiteracy_population i ON g.entity=i.entity AND g.year=i.year WHERE avg_schooling_years>10 AND illiteracy_percent>20",

"India Literacy vs GDP Trend":
"SELECT l.year,l.adult_literacy,g.gdp_per_capita FROM literacy_rates l JOIN gdp_schooling g ON l.entity=g.entity AND l.year=g.year WHERE l.entity='India'",

"Gender Gap in High GDP Countries (2020)":
"SELECT l.entity,(youth_male-youth_female) FROM literacy_rates l JOIN gdp_schooling g ON l.entity=g.entity AND l.year=g.year WHERE g.gdp_per_capita>30000 AND l.year=2020"

}
selected_query = st.selectbox("Select Query", list(query_options.keys()))
result = pd.read_sql_query(query_options[selected_query], conn)

st.dataframe(result)

# Country filter
st.subheader("🌍 Country Analysis")

country = st.selectbox("Select Country", df_literacy['entity'].unique())

filtered = df_literacy[df_literacy['entity'] == country]

st.line_chart(filtered.set_index('year')['adult_literacy'])