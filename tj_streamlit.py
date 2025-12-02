import streamlit as st
import polars as pl
import altair as alt
from textwrap import wrap


st.set_page_config(layout='wide')
# st.json(st.config.get_option("theme.font"))

tjhp_clean = pl.read_csv('data/tjhp_clean.csv')
tjhp_clean_instock = tjhp_clean.filter(pl.col('stock_status') == 'IN_STOCK')
tjhp_clean_instock_sorted = tjhp_clean_instock.sort(by='calories_per_dollar', descending=True)
tjhp_clean_instock_sorted = tjhp_clean_instock_sorted.with_columns(
    pl.col('name').map_elements(
        lambda x: '\n'.join(wrap(x, 2))
    ).alias('name_wrap')
)

total_points = tjhp_clean_instock.shape[0]

"""
# TJ's Products: Nutritional and Dollar Values

Here are a couple charts that give a high-level overview of what was in stock when I pulled all these grocery item data (early summer 2025).
  Out of **3860** products found after mild pruning, there were **369** labeled `IN_STOCK`.
"""

cols = st.columns(1)

with cols[0].container(border=True, height='stretch'):
    num_points_default = 10

    title = st.empty()

    subcols = st.columns([1,1,1])
    with subcols[1].container(border=False, height='stretch'):
        num_points = st.slider(
            'Select number of products to display',
            min_value=3,
            max_value=20,
            value=num_points_default,
            step=1
        )

    title.markdown(f"### Hyde Park TJ\'s {num_points} in-stock items with the most total calories per dollar")

    calorie_density_bar = alt.Chart(tjhp_clean_instock_sorted.head(num_points)).mark_bar().encode(
        y=alt.Y('name', title="Product", type='nominal', sort=None, 
                axis=alt.Axis(labelAngle=0, labelLimit=200)
            ),
        x=alt.X('calories_per_dollar', title="Calories per USD"),
        color=alt.Color('price_usd', title="Price (USD)").scale(
                scheme='greens'
            ).legend(
                orient='right',
                direction='vertical'
            ),
        tooltip=['sku', 'name', 'price_usd', 'calories_per_serving', 'servings_per_container']
    )
    calorie_density_bar

cols = st.columns(1)

with cols[0].container(border=True, height="stretch"):
    "### Dollar value of total calories in in-stock TJ\'s food items"

    tj_calorie_scatter = alt.Chart(tjhp_clean_instock).mark_point(
        filled=True, stroke='black', strokeWidth=0.25, size=50
        ).encode(
            x=alt.X('price_usd', title='Price (USD)', axis=alt.Axis(format='.2f')),
            y=alt.Y('calories_per_container', title="Calories per Container"),
            opacity=alt.value(0.5),
            color=alt.Color(
                'protein_per_container', title="Protein per Container"
                ).scale(
                    scheme="oranges"
                ).legend(
                    orient='right',
                    direction='vertical'),
            tooltip=['sku', 'name', 'price_usd', 'calories_per_container', 'calories_per_dollar', 'protein_per_container', 'servings_per_container']
        )
    tj_calorie_scatter


cols = st.columns(1)


""
""

"""
## Thoughts
There are plenty of erroneous data entries! A common issue seems to be that single-serving prices were attributed to the nutritional value of a full box of some things.

Overall, the big winners of maximizing calories for your dollar include:
1. Cooking oils (+ mayo)
2. Flour
3. Rice
4. Nut butters
5. Pasta
6. Milk

I would like to eventually:
* grab each nutritional fact for each product (not just calories and protein)
* find a better way to filter out erroneous product data (e.g. nutrition data errors, products listed as available when really discontinued)
* categorize products by food group, frozen vs. fresh, ingredient vs. meal, and maybe some other things
* dump it all into a vector database so I can actually search for particular items (SKUs and arbitrary product titles are a pain)
* fit a curve to the apparent upper bound on the scatter plot
"""

