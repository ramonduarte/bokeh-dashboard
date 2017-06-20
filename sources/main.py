# coding=utf-8
from bokeh.layouts import column
from bokeh.models import Button, ColumnDataSource, HoverTool, FuncTickFormatter
from bokeh.models.glyphs import VBar
from bokeh.models.widgets import Slider, Select
from bokeh.palettes import RdYlBu3
from bokeh.layouts import layout, widgetbox, column, row
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
# excel_file = "D:\Users\Ramon\PycharmProjects\\bokeh-dashboard\data\dados.xlsx"
excel_file = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'data', 'dados.xlsx')
list_of_days = ['{:0>2}'.format(i) for i in range(1, 32)]
list_of_months = {
    '01': 'janeiro', '02': 'fevereiro', '03': 'março', '04': 'abril',
    '05': 'maio', '06': 'junho', '07': 'julho', '08': 'agosto',
    '09': 'setembro', '10': 'outubro', '11': 'novembro', '12': 'dezembro',
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
newspapers = [u'Todos'] + sorted(list(df.source.unique()))

# Interactive controls
candidato_choice = Select(title='Candidato', options=candidatos, value=u'Todos')
newspaper_choice = Select(title='Fonte', options=newspapers, value=u'Todos')
# ... Start date
day_start_choice = Select(title='Dia', options=list_of_days, value='01')
month_start_choice = Select(
    title='Mês',
    options=sorted(list_of_months.keys()),
    value='{:0>2}'.format(dts[0].month)
)
year_start_choice = Select(
    title='Ano',
    options=[str(y) for y in range(start_year, end_year + 1)],
    value=str(start_year)
)
# ... End date
day_end_choice = Select(title='Dia', options=list_of_days, value='31')
month_end_choice = Select(
    title='Mês',
    options=sorted(list_of_months.keys()),
    value='{:0>2}'.format(dts[-1].month)
)
year_end_choice = Select(
    title='Ano',
    options=[str(y) for y in range(start_year, end_year + 1)],
    value=str(end_year)
)


source = ColumnDataSource(data=dict(
    # x=['{:0>2}/{:0>2}/{}'.format(x, 10, 2016) for x in range(1, monthrange(2016, 10)[1] + 1)],
    x=x_range,
    top=[get_news_by_date(df, k) for k in pd.date_range(start_x, end_x)],
    # color=[],
    candidato=[u'Todos'] * ((end_x - start_x).days + 1),
    newspaper=[u'Todos'] * ((end_x - start_x).days + 1),
    # alpha=[],
    # width=[],
))

# Creating and styling a plot comes after all interactive controls have been set
p = figure(
    y_range=(0, 200),
    x_range=x_range,
    toolbar_location=None,
    plot_width=plot_width,
    plot_height=plot_height,
    x_axis_type="datetime",
    title='Notícias por fonte',
)
p.vbar(
    x="x",
    top="top",
    width=0.5,
    source=source,
)
cr = p.circle(
    x='x', y='top', size=20, source=source,
    fill_color="grey",
    hover_fill_color="firebrick",
    fill_alpha=0.005,
    hover_alpha=0.3,
    line_color=None,
    hover_line_color="white"
)
# Hover tooltips can actually be defined before being instantiated
hover = HoverTool(
    tooltips=[
        ('Notícias', '@top'),
        ('Fonte', '@newspaper'),
        ('Candidato', '@candidato'),
        ('Data', '@x'),
        ],
    renderers=[cr],
    mode='hline',
)
p.add_tools(hover)

p.xaxis.formatter = FuncTickFormatter(code="""
var a = new Date('{}');
console.log(a);
a.setUTCDate(a.getUTCDate() + tick);
return a.getUTCDate() + '/' + (a.getUTCMonth() + 1) + '/' + a.getUTCFullYear();
""".format(x_range[0]))
p.xaxis.major_label_orientation = "vertical"
p.xaxis.axis_label = "Data"
p.yaxis.axis_label = "Notícias"
p.title.text_font_size = '20px'


def select_news():
    # .. Candidate
    candidato_value = candidato_choice.value or u'Todos'  # selected by the end user
    both = (candidato_value == u'Todos')
    selected = df[(df.candidato == candidato_value) | both]

    # .. News source
    newspaper_value = newspaper_choice.value or u'Todos'  # selected by the end user
    both = (newspaper_value == u'Todos')
    selected = selected[(df.source == newspaper_value) | both]

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
    newspaper = [newspaper_choice.value or u'Todos']
    newspaper *= days_in_total

    source.data = dict(
        x=[d.isoformat()[:10] for d in pd.date_range(
            date_start_value.isoformat(),
            date_end_value.isoformat(),
        )],
        top=get_news_by_range(dataframe, date_start_value, date_end_value),
        candidato=candidato,
        newspaper=newspaper,
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
    # .. News sources
    newspaper_choice,
]

for c in controls:
    c.on_change('value', lambda attr, old, new: update())

sizing_mode = 'stretch_both'

candidato_inputs = widgetbox(candidato_choice, sizing_mode=sizing_mode)
newspaper_inputs = widgetbox(newspaper_choice, sizing_mode=sizing_mode)
start_date_inputs = [widgetbox(*controls[k:k+1]) for k in [1, 2, 3]]
end_date_inputs = [widgetbox(*controls[k:k+1]) for k in [4, 5, 6]]

# start_date_row = row(start_date_inputs, sizing_mode='fixed')
start_date_row = row(controls[1:4], responsive=True)
# end_date_row = row(end_date_inputs, sizing_mode='scale_width')
end_date_row = row(controls[4:7], responsive=True)

update()
curdoc().add_root(row(p, responsive=True))
curdoc().add_root(row([candidato_inputs, newspaper_inputs], responsive=True))
# curdoc().add_root(row(newspaper_inputs, responsive=True))
curdoc().add_root(start_date_row)
curdoc().add_root(end_date_row)
curdoc().add_periodic_callback(update, 50)

