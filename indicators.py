import sankey
import pandas as pd

filename = 'Indicator2'
sheet = 'Sankey'
title = ''


circular_sankey = pd.read_excel(f'{filename}.xlsx', sheet_name=sheet)
sankey.draw_circular_sankey(circular_sankey, title_text=title)
