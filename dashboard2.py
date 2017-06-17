from bokeh.layouts import column
from bokeh.models import Button, ColumnDataSource, HoverTool, FuncTickFormatter
from bokeh.models.glyphs import VBar
from bokeh.models.widgets import Slider, Select
from bokeh.palettes import RdYlBu3
from bokeh.layouts import layout, widgetbox
from bokeh.plotting import figure, curdoc, show, output_file
from bokeh.embed import file_html, components
from bokeh.resources import CDN
from bokeh.client import push_session
import pandas as pd
import os
from calendar import monthrange
from datetime import date, timedelta, datetime

# Predefinitions
plot_width, plot_height = 300, 300
# excel_file = "D:\Users\Ramon\PycharmProjects\\bokeh-dashboard\dados.xlsx"
excel_file = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'dados.xlsx')
list_of_days = [str(i) for i in range(1, 32)]
list_of_months = {
    '1': 'janeiro', '2': 'fevereiro', '3': 'marco', '4': 'abril',
    '5': 'maio', '6': 'junho', '7': 'julho', '8': 'agosto',
    '9': 'setembro', '10': 'outubro', '11': 'novembro', '12': 'dezembro',
}


# noinspection PyShadowingNames
def get_news_by_date(df, user_date):
    """

    :param user_date:
    :param df:
    :return:
    """
    dataframe = df[df.date_published > pd.to_datetime(user_date)]
    dataframe = dataframe[
        dataframe.date_published < (pd.to_datetime(user_date) + timedelta(days=1))
        ]
    return len(dataframe)


# noinspection PyShadowingNames
def get_news_by_range(df, start_date, end_date):
    """

    :param end_date:
    :param start_date:
    :param df:
    :return:
    """
    return [get_news_by_date(df, day) for day in pd.date_range(start_date, end_date)]


# noinspection PyShadowingNames
def get_news_by_month(df, year, month):
    """

    :param year:
    :param month:
    :param df:
    :return:
    """
    return [get_news_by_date(df, date(year, month, day))
            for day in range(1, monthrange(int(year), int(month))[1] + 1)]


# noinspection PyShadowingNames
def get_news_by_year(df, year):
    """

    :param year:
    :param df:
    :return:
    """
    return [get_news_by_month(df, year, month) for month in range(1, 13)]


df = pd.read_excel(
    io=str(excel_file),
    sheetname='Sheet1',
    index_col=None,
)
df.date_published = pd.to_datetime(df.date_published)

candidatos = [u'Todos'] + sorted(list(df.candidato.unique()))
dts = sorted(list(df.date_published))
start_year, end_year = dts[0].year, dts[-1].year
start_x = date(dts[0].year, dts[0].month, dts[0].day)
end_x = date(dts[-1].year, dts[-1].month, dts[-1].day)
x_range = [d.isoformat()[:10] for d in pd.date_range(start_x, end_x, freq='D')]
x = [d.isoformat()[:10] for d in pd.date_range(start_x, end_x, freq='D')]

# Interactive controls
candidato_choice = Select(title='Candidato', options=candidatos, value=u'Todos')
# ... Start date
day_start_choice = Select(title='Dia', options=list_of_days, value='1')
month_start_choice = Select(
    title='Mes',
    options=list_of_months.keys(),
    value=str(dts[0].month)
)
year_start_choice = Select(
    title='Ano',
    options=[str(y) for y in range(start_year, end_year + 1)],
    value=str(start_year)
)
# ... End date
day_end_choice = Select(title='Dia', options=list_of_days, value='31')
month_end_choice = Select(
    title='Mes',
    options=list_of_months.keys(),
    value=str(dts[0].month)
)
year_end_choice = Select(
    title='Ano',
    options=[str(y) for y in range(start_year, end_year + 1)],
    value=str(end_year)
)

# Hover tooltips can actually be defined before being instantiated
hover = HoverTool(tooltips=[
    ('Noticias', '@top'),
    ('Candidato', '@candidato'),
    ('Data', '@x')
])

source = ColumnDataSource(data=dict(
    # x=['{:0>2}/{:0>2}/{}'.format(x, 10, 2016) for x in range(1, monthrange(2016, 10)[1] + 1)],
    x=x_range,
    top=[get_news_by_date(df, k) for k in pd.date_range(start_x, end_x)],
    # color=[],
    candidato=[u'Todos'] * ((end_x - start_x).days + 1),
    # noticias=[],
    # alpha=[],
    # width=[],
))

# Creating and styling a plot comes after all interactive controls have been set
p = figure(
    y_range=(0, 250),
    x_range=x_range,
    toolbar_location=None,
    tools=[hover],
    plot_width=plot_width,
    plot_height=plot_height,
    x_axis_type="datetime",
)
p.vbar(
    x="x",
    top="top",
    width=0.5,
    source=source,
)

p.xaxis.formatter = FuncTickFormatter(code="""
var a = new Date('{}');
console.log(a);
a.setUTCDate(a.getUTCDate() + tick);
return a.getUTCDate() + '/' + (a.getUTCMonth() + 1) + '/' + a.getUTCFullYear();
""".format(x_range[0]))
p.xaxis.major_label_orientation = "vertical"


#
def select_news():
    # .. Candidate
    candidato_value = candidato_choice.value or u'Todos'  # selected by the end user
    both = (candidato_value == u'Todos')
    selected = df[(df.candidato == candidato_value) | both]

    # .. Start date
    day_start_value = int(day_start_choice.value)  # selected by the end user
    month_start_value = int(month_start_choice.value)  # selected by the end user
    year_start_value = int(year_start_choice.value)  # selected by the end user
    date_start_value = date(year_start_value, month_start_value, day_start_value)
    selected = selected[selected.date_published > date_start_value]

    # .. End date
    day_end_value = int(day_end_choice.value)  # selected by the end user
    month_end_value = int(month_end_choice.value)  # selected by the end user
    year_end_value = int(year_end_choice.value)  # selected by the end user
    date_end_value = date(year_end_value, month_end_value, day_end_value)
    selected = selected[selected.date_published < date_end_value]
    return selected


def update():
    dataframe = select_news()
    date_start_value = date(
        int(year_start_choice.value),
        int(month_start_choice.value),
        int(day_start_choice.value)
    )
    date_end_value = date(
        int(year_end_choice.value),
        int(month_end_choice.value),
        int(day_end_choice.value)
    )
    days_in_total = (date_end_value - date_start_value).days + 1
    candidato = [candidato_choice.value or u'Todos']
    candidato *= days_in_total

    source.data = dict(
        x=[d.isoformat()[:10] for d in pd.date_range(
            date_start_value.isoformat(),
            date_end_value.isoformat(),
        )],
        top=get_news_by_range(dataframe, date_start_value, date_end_value),
        candidato=candidato,
    )


controls = [
    candidato_choice,
    # .. Start date
    day_start_choice,
    month_start_choice,
    year_start_choice,
    # .. End date
    day_end_choice,
    month_end_choice,
    year_end_choice,
]

for c in controls:
    c.on_change('value', lambda attr, old, new: update())

sizing_mode = 'fixed'

inputs = widgetbox(*controls, sizing_mode=sizing_mode)
lay_out = layout([
    [inputs, p]
], sizing_mode=sizing_mode)

# open a session to keep our local document in sync with server
# session = push_session(curdoc())
# update()
# curdoc().add_root(p)
curdoc().add_root(lay_out)
# curdoc().add_periodic_callback(update, 50)

# session.loop_until_closed()  # run forever
