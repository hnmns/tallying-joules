# https://github.com/data-sloth/uv-streamlit-setup
# https://stackoverflow.com/questions/18713086/virtualenv-wont-activate-on-windows
# In short, must activate virtual env IN CMD, then run 
import streamlit as st
import polars as pl
import altair as alt
# from textwrap import wrap


st.set_page_config(layout='wide')

tjhp_clean = pl.read_csv("data/tjhp_clean.csv")
tjhp_clean_instock = tjhp_clean.filter(pl.col('stock_status') == 'IN_STOCK')

# st.write(tjhp_clean)
chart1_width = 2000
# tjhp_clean_instock = tjhp_clean_instock.with_columns(
#     pl.col('name').map_elements(lambda x: wrap(x, width=12))
# )
calorie_density_bar = alt.Chart(tjhp_clean_instock.sort(by='calories_per_dollar', descending=True).head(20)).mark_bar().encode(
    # x='name',
    x=alt.X('name', title="Product", type='nominal', sort=None, axis=alt.Axis(labelAngle=-85)),
    y=alt.Y('calories_per_dollar', title="Calories per USD"),
    color=alt.Color('price_usd', title="Price (USD)").scale(
            scheme='greens'
        ).legend(
            orient='top-right',
            direction='vertical'
        ),
    tooltip=['sku', 'name', 'price_usd', 'calories_per_serving', 'servings_per_container']
).properties(
    title=alt.Title(
        text='Hyde Park TJ\'s 20 in-stock items with the most total calories per dollar',
        subtitle=''
    ),
    width=chart1_width,
    height=400
)


height_top=300
height_bottom=100
width_left=600
width_right=100
chart2_width = width_left + width_right

tj_calorie_scatter = alt.Chart(tjhp_clean_instock).mark_point(
    filled=True, stroke='black', strokeWidth=0.5, size=50
    ).encode(
        x=alt.X('price_usd', title='Price (USD)', axis=alt.Axis(format='.2f')),
        y=alt.Y('calories_per_container', title="Calories per Container"),
        opacity=alt.value(0.7),
        color=alt.Color(
            'protein_per_container', title="Protein per Container"
            ).scale(
                scheme="plasma"
            ).legend(
                orient='top-right',
                # legendX=450,
                # legendY=25,
                direction='vertical'),
        tooltip=['sku', 'name', 'price_usd', 'calories_per_container', 'calories_per_dollar', 'protein_per_container', 'servings_per_container']
    ).properties(
        title='Dollar value of total calories in in-stock TJ\'s food items',
        width=width_left,
        height=height_top,
)


chart = alt.vconcat(calorie_density_bar, tj_calorie_scatter).configure(
        font='TW Cen MT'
).configure_axis(
    labelLimit=300, # Measured in pixels, not characters
    labelFontSize=15,
    titleFontSize=20
).configure_title(
    fontSize=24,
    anchor='start',
    color='black',
    align='left'
).resolve_scale(color='independent')

"""
# TJ's Products: Nutritional and Dollar Values

Here are a couple charts that give a high-level overview of what was in stock when I pulled all these grocery item data (early summer 2025).
  Out of **3860** products found after mild pruning, there were **369** labeled `IN_STOCK`.
"""

""
""

chart

"""
## Thoughts
Overall, the big winners of maximizing calories for your dollar include:
1. Cooking oils (+ mayo)
2. Flour
3. Rice
4. Peanut butter
5. Pasta
6. Milk

I would like to eventually:
* grab each nutritional fact for each product (not just calories and protein)
* find a better way to filter out erroneous product data (e.g. nutrition data errors, products listed as available when really discontinued)
* categorize products by food group, frozen vs. fresh, ingredient vs. meal, and maybe some other things
* dump it all into a vector database so I can actually search for particular items (SKUs and arbitrary product titles are a pain)
* fit a curve to the apparent upper bound on the scatter plot
"""

