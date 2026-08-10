# How to visualize...

## Calorie economy
Here is the issue: Internet chefs notoriously love reporting how cheap a recipe is ***per serving***, but just as important is the minimal price of all ingredients. For example, you only use a cup of rice in a recipe, but you still have to buy a whole container of it. 

**How can we...**
1. **portray the calories per dollar spent**
2. **while also acknowledging the total upfront cost?**

### Scatter plot
* X: Price (USD)
* Y: Total calories in a container
* Line with slope equal to the mean (median?) calories per dollar
* Point color: Whether the item is above or below mean (median?) calories per dollar
    * Probably just a binary color scheme is enough. Start to think about percentiles and you are too far in the weeds for any normal human being to bother reading.
* Critique
    * (1) This chart answers the question of which product is more calorie-economical than another.
    * (2) This chart also uses the actual price of a whole package as the x-axis.