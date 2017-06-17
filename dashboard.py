from bokeh.layouts import column
from bokeh.models import Button, ColumnDataSource, HoverTool, FuncTickFormatter, PrintfTickFormatter, DatetimeTickFormatter
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
excel_file = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), 'bokeh-dashboard\\dados.xlsx')


# noinspection PyShadowingNames
def get_news_by_date(df, user_date):
    """

    :param user_date:
    :param df:
    :return:
    """
    dataframe = df[df.date_published > pd.to_datetime(user_date)]
    dataframe = dataframe[dataframe.date_published < (pd.to_datetime(user_date) + timedelta(days=1))]
    return len(dataframe)


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
# for d in datas:
#     # year = d[:4], month = d[5:7], day = d[8:10]. Good luck!
#     new_datas.setdefault(d[:4], {}).setdefault(d[5:7], []).append(d[8:10])

candidatos = [u'Todos'] + sorted(list(df.candidato.unique()))
dts = sorted(list(df.date_published))
start_year, end_year = dts[0].year, dts[-1].year
start_x, end_x = date(dts[0].year, dts[0].month, dts[0].day), date(dts[-1].year, dts[-1].month, dts[-1].day)
# x_range = (start_x.isoformat(), end_x.isoformat())
x_range = [d.isoformat()[:10] for d in pd.date_range(start_x, end_x, freq='D')]
x = [d.isoformat()[:10] for d in pd.date_range(start_x, end_x, freq='D')]

# Interactive controls
candidato_choice = Select(title='Candidato', options=candidatos)
# day_choice = Slider(title='Dia', start=1, end=31, value=10, step=1)
month_choice = Slider(title='Mes', start=1, end=12, value=10, step=1)
year_choice = Slider(title='Ano', start=start_year, end=end_year, value=start_year, step=1)

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
    # top=get_news_by_month(df, '2016', '10'),
    # color=[],
    candidato=[u'Todos'] * ((end_x - start_x).days + 1),
    # noticias=[],
    # alpha=[],
    # width=[],
    # date=[''.format()],
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
    # x=range(1, monthrange(2016, 10)[1] + 1),
    x="x",
    # top=get_news_by_month(df, '2016', '10'),
    top="top",
    width=0.5,
    source=source,
)

#
# def date_axis_formatter():
#     return "{}".format((start_x + timedelta(days=tick)).strftime('%d/%m/%Y'))


# p.xaxis.formatter = FuncTickFormatter.from_py_func(date_axis_formatter)
p.xaxis.formatter = FuncTickFormatter(code="""
var a = new Date('{}');
console.log(a);
a.setUTCDate(a.getUTCDate() + tick);
return a.getUTCDate() + '/' + (a.getUTCMonth() + 1) + '/' + a.getUTCFullYear();
""".format(x_range[0]))
# p.xaxis.formatter = DatetimeTickFormatter('%d/%m/%Y')
p.xaxis.major_label_orientation = "vertical"


#
def select_news():
    candidato_value = candidato_choice.value or u'Todos'  # selected by the end user
    month_value = month_choice.value  # selected by the end user
    year_value = year_choice.value  # selected by the end user
    # day_value = day_choice.value  # selected by the end user
    date_value = date(year_value, month_value, 1)
    both = (candidato_value == u'Todos')

    selected = df[(df.candidato == candidato_value) | both]
    selected = selected[selected.date_published > date_value]
    selected = selected[
        selected.date_published < (date_value + timedelta(days=monthrange(year_value, month_value)[1]))
        ]
    # selected = selected[
    #     (selected.date_published > '{}-{:0>2}-01'.format(year_value, month_value)) &
    #     (selected.date_published < '{}-{:0>2}-32'.format(year_value, month_value))
    # ]
    return selected


def update():
    dataframe = select_news()
    days_in_month = monthrange(year_choice.value, month_choice.value)[1]
    # candidato = list(dataframe.candidato.unique())
    candidato = [candidato_choice.value or u'Todos']
    # if len(candidato) != 1:
    #     candidato = [u'Todos']
    candidato *= days_in_month

    source.data = dict(
        x=[d.isoformat() for d in pd.date_range(
            date(year_choice.value, month_choice.value, 1).isoformat(),
            date(year_choice.value, month_choice.value, days_in_month).isoformat(),
        )],
        # x=['{:0>2}/{:0>2}/{}'.format(day, month_choice.value, year_choice.value)
        #    for day in range(1, monthrange(year_choice.value, month_choice.value)[1] + 1)],
        # x=range(1, days_in_month + 1),
        top=get_news_by_month(dataframe, year_choice.value, month_choice.value),
        # top=get_news_by_month(dataframe, '2016', '10'),
        candidato=candidato,
    )


controls = [
    candidato_choice,
    month_choice,
    year_choice,
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
update()
curdoc().add_root(lay_out)
curdoc().add_periodic_callback(update, 50)

# session.loop_until_closed()  # run forever
