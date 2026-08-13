import streamlit as st
import polars as pl
import pandas as pd
import altair as alt
from textwrap import wrap


st.set_page_config(layout='wide')
# st.json(st.config.get_option("theme.font"))

tjhp_clean = pl.read_csv('data/tjhp_clean.csv')
tjhp_clean_instock = tjhp_clean.filter(pl.col('stock_status') == 'IN_STOCK')

total_points = tjhp_clean_instock.shape[0]

"""
# TJ's Products: Nutritional and Dollar Values

Here are several charts that give a high-level overview of what was in stock when I pulled Hyde Park Trader Joe's grocery item data (early summer 2025).
  Out of **3860** products found after mild pruning, there were **369** labeled `IN_STOCK`. Mouse over a data point for more details.
"""

options = ['Calories', 'Protein']
nutrient_selection = st.pills(
    'Pick a nutrient:',
    options, 
    default='Calories',
    selection_mode='single'
)

nutrient_configs = {
    'Calories': dict(
        density_field='calories_per_dollar', density_title='Calories per USD',
        container_field='calories_per_container', container_title='Calories per package',
        density_label='total calories per dollar', value_label='calories',
        slider_key='calories_slider'
    ),
    'Protein': dict(
        density_field='grams_protein_per_dollar', density_title='Grams of protein per USD',
        container_field='protein_per_container', container_title='Grams of protein per package',
        density_label='grams of protein per dollar', value_label='protein',
        slider_key='protein_slider'
    ),
}
cfg = nutrient_configs[nutrient_selection]

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

    title.markdown(f"### TJ\'s {num_points} in-stock items with the most total {cfg['value_label']} per dollar")

    nutrient_density_bar = alt.Chart(
            tjhp_clean_instock.sort(by=cfg['density_field'], descending=True).head(num_points)
        ).mark_bar().encode(
            y=alt.Y('name', title="Product", type='nominal', sort=None, 
                    axis=alt.Axis(labelAngle=0, labelLimit=200)
                ),
            x=alt.X(cfg['density_field'], title=cfg['density_title']),
            color=alt.Color('price_usd', title="Price (USD)").scale(
                    scheme='greens'
                ).legend(
                    orient='right',
                    direction='vertical'
                ),
            tooltip=[
                'sku', 'name', 'price_usd', 'calories_per_serving', 
                'protein_per_serving', 'servings_per_container'
            ]
        )
    
    st.altair_chart(
        nutrient_density_bar,
        use_container_width=True,
        key=f"bar_{nutrient_selection}"
    )


cols = st.columns([3,1])
with cols[0].container(border=True, width="stretch", height="stretch"):
    f"### Total {cfg['value_label']} per dollar of \"in-stock\" TJ's food products "
    slope = (tjhp_clean_instock[cfg['container_field']] / tjhp_clean_instock['price_usd']).mean()

    tj_nutrient_scatter = alt.Chart(tjhp_clean_instock).transform_calculate(
        above_average = f"(datum.{cfg['container_field']} / datum.price_usd) > " + str(slope) + " ? 'Above average' : 'Below average'"
    ).mark_point(
        filled=True, stroke='black', strokeWidth=0, size=50
    ).encode(
        x=alt.X('price_usd', title='Price per package (USD)', axis=alt.Axis(format='.2f')),
        y=alt.Y(cfg['container_field'], title=cfg['container_title']),
        opacity=alt.value(0.5),
        color=alt.Color('above_average:N',
            scale=alt.Scale(
                domain=['Above average', 'Below average'],
                range=['forestgreen', 'sienna']
            ),
            legend=alt.Legend(title=['Product\'s nutrient', 'value for your dollar'], symbolStrokeWidth=0)
        ),
        tooltip=[
            'sku', 'name', 'price_usd', 'calories_per_container', 
            'calories_per_dollar', 'protein_per_container', 'servings_per_container'
        ]
    )
    
    xy_ranges = pd.DataFrame(
        {
            'price_usd': range(0, 2+int(tjhp_clean_instock['price_usd'].max())),
            'legend': f'Average {cfg['value_label']}/$'
        }
    )
    xy_ranges[cfg['container_field']] = slope * xy_ranges['price_usd']
    formula_line = alt.Chart(xy_ranges).mark_line(
        strokeWidth=3,
        strokeDash=[5, 5],
        color='black'
    ).encode(
        x=alt.X('price_usd'),
        y=alt.Y(cfg['container_field']),
        strokeWidth=alt.StrokeWidth(
            'legend:N', 
            legend=alt.Legend(title=['','']) # Blank title => X axis title gets cut off!
        ),
    )

    # By using pill selector for nutrients, vega tries patching
    # the same chart. Instead, fully remount the chart
    st.altair_chart(
        formula_line + tj_nutrient_scatter,
        use_container_width=True,
        key=f"scatter_{nutrient_selection}"
    )

""
""

"""
## Data Quality & Analysis Takeaways
There are plenty of erroneous data entries! An example of a common data issue is when a box 
containing many servings is listed with the price of a single serving, like a box of granola bars. Red
Argentinian shrimp are seemingly one of the worst-value purchases (located in bottom-right of the scatter chart)
by the calories/dollar metric, 
but I didn't believe at first that a $12 bag of shrimp contains only 240 calories. 
I checked with Trader Joe's website, and apparently that was not just a data issue.

Overall, some big winners that maximize the caloric bang for your buck include:
*  Cooking oils (+ mayo)
*  Flour
*  Rice
*  Nut butters
*  Pasta
*  Milk

I would like to eventually:
* grab each nutritional fact for each product (not just calories and protein)
* find a better way to filter out erroneous product data (e.g. nutrition data errors, products listed as available when really discontinued)
* categorize products by food group, frozen vs. fresh, ingredient vs. meal, and maybe some other things
* dump it all into a vector database so I can actually search for particular items (SKUs and arbitrary product titles are a pain)
* fit a curve to the apparent upper bound on the scatter plots
"""

