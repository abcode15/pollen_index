#######################
# Import libraries
import streamlit as st
import pandas as pd
import geopandas as gpd
import matplotlib.pyplot as plt
import matplotlib.colors as colors
import matplotlib as mpl
from matplotlib.pyplot import MultipleLocator
from matplotlib.dates import DateFormatter
import matplotlib.dates as mdates
import altair as alt
import plotly.express as px
from datetime import datetime, date, time, timedelta
from st_click_detector import click_detector
import numpy as np

#######################
# Page configuration
st.set_page_config(
    page_title="Pollen Allergy Index of city china",
    page_icon="",
    layout="wide",
    initial_sidebar_state="expanded")

alt.themes.enable("dark")

# China font simhei added to show chinese characters
mpl.font_manager.fontManager.addfont('font/SimHei.ttf') #临时注册新的全局字体
plt.rcParams['font.sans-serif']=['SimHei'] #用来正常显示中文标签
plt.rcParams['axes.unicode_minus']=False#用来正常显示负号

#######################
# Load data
pollen_data = pd.read_csv('data/pollen_optimize.csv')
pollen_data = pollen_data.loc[:, ['Date', 'num', 'City']]
pollen_data['Date'] = pd.to_datetime(pollen_data['Date'], 'coerce')
china_map = gpd.read_file('data/chn_admbnda_adm2_ocha_2020.shp')
china_map.loc[china_map.ADM2_ZH == "西安市", 'ADM2_EN'] = 'Xian'

pollen_city = pd.DataFrame((ct for ct in list(pollen_data.City.unique())), columns=('City',))

#######################
# Sidebar
with st.sidebar:
    st.title('中国部分城市花粉指数')
    
    # color_theme_list = ['blues', 'cividis', 'greens', 'inferno', 'magma', 'plasma', 'reds', 'rainbow', 'turbo', 'viridis']
    # selected_color_theme = st.selectbox('Select a color theme', color_theme_list)
    

    # Select a day box
    day_list = [dt.date() for dt in list(pollen_data.Date.unique())]
    day_list.sort(reverse=True)
    max_day = day_list[0]
    min_day = day_list[-1]
    st.markdown("---")
    st.markdown("### Select a day:")
    selected_day = st.selectbox(' days list', day_list)
    tm = time(0,0,0)
    selected_datetime = datetime.combine(selected_day, tm)
    selected_lower_datetime = selected_datetime - timedelta(days=9)
    pollen_day = pollen_data[pollen_data.Date == selected_datetime]
    pollen_day = pollen_city.merge(pollen_day, on='City', how='left')
    pollen_heatmap = pollen_data[pollen_data.Date.between(selected_lower_datetime, selected_datetime)]
    pollen_heatmap['Date'] = pollen_heatmap.Date.dt.strftime('%y-%m-%d')
    
    pollen_day_sorted = pollen_day.sort_values(by="num", ascending=False)[ : 10]
    
    # Dynamic Color Pickers
    st.markdown("---")
    st.markdown("#### Select the color code for your legend:",
                unsafe_allow_html = True)

    # color = st.color_picker("Pick A Color", "#00f900")
    
    content = """
        <div style='display: flex; flex-direction: column; align-items: center;'>
            <div style='display: flex; justify-content: center;'>
                <a href='#' id='reds' style='background-color: red; width: 40px; height: 40px; margin: 10px; display: flex; justify-content: center; align-items: center;'></a>
                <a href='#' id='greens' style='background-color: green; width: 40px; height: 40px; margin: 10px; display: flex; justify-content: center; align-items: center;'></a>
                <a href='#' id='blues' style='background-color: blue; width: 40px; height: 40px; margin: 10px; display: flex; justify-content: center; align-items: center;'></a>
                <a href='#' id='yellowgreen' style='background-color: yellow; width: 40px; height: 40px; margin: 10px; display: flex; justify-content: center; align-items: center;'></a>
            </div>
        </div>
        """

    color_clicked = click_detector(content)
    
    if color_clicked == "":
        color_clicked = "blues"

    # color_clicked = "blues"
    
#######################
# Plots
######################
# Global Value
columnA = 'Beijing Municipality'
columnB = 'Chengde'
labelA = '北京'
labelB = '承德'
# Chart
def make_chart(input_df):
    data_set = input_df.loc[pollen_data.City.isin([columnA, columnB])]
    pollen_line = data_set.pivot(index='Date', columns='City', values='num')
    pollen_line = pollen_line.sort_index()
    min_date = pollen_line.index.min()
    max_date = pollen_line.index.max()
    ############################
    # Init
    fig, ax = plt.subplots(figsize=(12,8))
    # ax.xaxis.set_major_locator(mdates.DayLocator(interval=7))
    # ax.xaxis.set_minor_locator(mdates.DayLocator())
    # ax.xaxis.set_major_formatter(DateFormatter("%m-%d"))
    
    locator = mdates.AutoDateLocator(minticks=11, maxticks=21)
    formatter = mdates.ConciseDateFormatter(locator)
    formatter.formats = ['%y',  # ticks are mostly years
                         '%y-%m',       # ticks are mostly months
                         '%d',       # ticks are mostly days
                         '%H:%M',    # hrs
                         '%H:%M',    # min
                         '%S.%f', ]  # secs
    # these are mostly just the level above...
    formatter.zero_formats = [''] + formatter.formats[:-1]
    # ...except for ticks that are mostly hours, then it is nice to have
    # month-day:
    formatter.zero_formats[3] = '%m-%d'

    formatter.offset_formats = ['',
                                '%Y',
                                '%Y-%m-%d',
                                '%Y-%m-%d',
                                '%Y-%m-%d',
                                '%Y-%m-%d %H:%M', ]
    ax.xaxis.set_major_locator(locator)
    ax.xaxis.set_major_formatter(formatter)
      
    ax.grid(True)
    ax.grid(which='major', color='#DDDDDD', linewidth=0.9)
    ax.grid(which='minor', color='#CCCCCC', linestyle=':', linewidth=0.8)
    ax.minorticks_on()

    # Set title
    ax.set_title('花粉指数: 北京 ：承德')
    # Set the limits for the Y axis
    ax.set_ylim([-100, 2100])
    # ax.set_xlim([0, 100])
    ax.set_xlim(np.array([min_date, max_date]).astype('datetime64[D]'))
  
    chartA, = ax.plot(np.array(list(pollen_line.index)).astype('datetime64[D]'), list(pollen_line[columnA]), marker='o', color= '#00A88F', linestyle='dotted', label=labelA)
    chartB, = ax.plot(np.array(list(pollen_line.index)).astype('datetime64[D]'), list(pollen_line[columnB]), marker='+', color= '#884b8f', linestyle='dotted', label=labelB)    
    legend = ax.legend(loc='upper left', shadow=False, fontsize='medium')
    legend.get_frame().set_facecolor('None')
    return fig

# Pollen Map
def make_pollen_map(input_df, input_gdf, input_date):
    # Drawing map with matplotlib
    fig, ax = plt.subplots(1, 
                           figsize = (6, 4))
    # Clear the axes each iteration
    ax.clear()
    fig.set_facecolor('none')
    
    # Filter data based on current date
    current_data = input_df
    
    # Merge the data with the world dataframe
    map_for_date = input_gdf.merge(current_data, how='left', left_on='ADM2_EN', right_on='City')
    
    map_match_data = input_gdf.merge(current_data, how='inner', left_on='ADM2_EN', right_on='City')
    
    # Parameters for missing values
    missing_kwds = {
        "color"    : "white",
        "edgecolor": "lightgrey",
        "hatch"    : "///", 
        "label"    : "缺失值"
    }
    
    classification_kwds = {
        'bins': [50, 100, 300, 500, 800, 9999]
        }

    legend_kwds = {
        'loc': 'lower right', 
        'prop': {'size': 7 },
        'title': '花粉过敏指数', 
        "edgecolor": "grey",
        'fontsize': '5',
        'title_fontsize': '8',
        'shadow': True
        }
    
    # Create a custom colormap
    # colors_list = color_breaks
    # cmap_name   = "default_cmap"
    # cmap        = (colors
    #                .LinearSegmentedColormap
    #                .from_list(cmap_name, colors_list))

    map_for_date.plot(column='num', cmap='coolwarm', linewidth=0.1, ax=ax, edgecolor='grey',
                      legend=False, vmin=0, vmax=3000, missing_kwds={'color': 'lightgrey', 'hatch': '///'})
    # map_for_date.plot(ax=ax, 
    #                   column='num',     
    #                   edgecolor    = "grey",                         
    #                 #   cmap         = cmap,
    #                   cmap         = 'Reds',
    #                   linewidth    = 0.5,
    #                   legend       = True,
    #                   missing_kwds = missing_kwds,
    #                   scheme       = 'UserDefined',
    #                   classification_kwds = classification_kwds,
    #                   legend_kwds  = legend_kwds
    #                  )
    
    for idx, _ in enumerate(map_match_data.geometry.representative_point()):
        region = map_match_data.loc[idx, 'ADM2_ZH'][:5]
        ax.text(_.x, _.y, region, ha="center", va="center", size=3)
    
    #Title, lines and annotations
    # ax.set_title('Tracking Pollen Index', fontsize=25, pad=30, weight='bold')
    # ax.axhline(y=0.5, color='black', linestyle='--', alpha=0.2) # Horizontal line 
    
    # date_pd = pd.to_datetime(str(input_date))
    # # date_formatted = date_pd.strftime('%B %d %Y')
    # date_formatted = date_pd.strftime('%Y %m %d')
    
    # # ax.annotate("Pollen Allergy Index On " + date_formatted,xy=(0.5,0), xytext=(0,0), 
    #                 #    xycoords='axes fraction', textcoords='offset points', ha='center', fontsize=14, 
    #                 #    color='grey', weight='bold')
    # ax.annotate("花粉过敏指数： " + date_formatted,xy=(0.5,0), xytext=(0,0), 
    #                    xycoords='axes fraction', textcoords='offset points', ha='center', fontsize=14, 
    #                    color='grey', weight='bold')
   
    # ax.annotate('Equatorial Line',xy=(0.9,0.43), xytext=(0,0), 
    #                    xycoords='axes fraction', textcoords='offset points', ha='center', fontsize=7, 
    #                    color='black', weight='bold')
    
    # Turn off the axes
    # ax.xaxis.set_visible(False)
    # ax.yaxis.set_visible(False)
    ax.axis('off')
    return fig
    
def make_bar(names, values, label, x, y):
    # Figure Size
    fig, ax = plt.subplots(figsize =(x, y))
    
    # Horizontal Bar Plot
    color = 'lightblue'
    ax.barh(names, values, color=color)
    
    # Remove axes splines
    for s in ['top', 'bottom', 'left', 'right']:
        ax.spines[s].set_visible(False)
    
    # Remove x, y Ticks
    ax.xaxis.set_ticks_position('none')
    ax.yaxis.set_ticks_position('none')
    
    # Add padding between axes and labels
    ax.xaxis.set_tick_params(pad = 5)
    ax.yaxis.set_tick_params(pad = 10)
    
    # Add x, y gridlines
    ax.grid(visible = True, color ='grey',
            linestyle ='-.', linewidth = 0.5,
            alpha = 0.2)
    
    ax.invert_yaxis()
    
    # Add annotation to bars
    for i in ax.patches:
        plt.text(i.get_width()+0.2, i.get_y()+0.5, 
                str(round((i.get_width()), 2)),
                fontsize = 10, fontweight ='bold',
                color ='lightblue')
    
    # Add Plot Title
    # ax.set_title(label, loc ='left', )
    
    # Add Text watermark
    fig.text(0.9, 0.15, 'robertyu', fontsize = 12,
            color ='grey', ha ='right', va ='bottom',
            alpha = 0.7)
    
    return fig

        
#######################
# Dashboard Main Panel
st.markdown('#### 城市花粉指数')

col = st.columns((6, 6), gap='small')

with col[0]:
    
    pollenplt = make_pollen_map(pollen_day, china_map, selected_day)
    st.pyplot(pollenplt, use_container_width=True)    

with col[1]:    
    fig = make_chart(pollen_data)
    st.pyplot(fig, use_container_width=True)

col = st.columns((2, 2, 1), gap='medium')    
with col[0]:
    st.markdown('#### 花粉指数列表')
    pollen_day['Date'] = pollen_day['Date'].astype(str)
    st.dataframe(pollen_day, column_config={
                    "City": st.column_config.TextColumn(
                        "城市",
                        width="medium",
                        # max_chars=20,
                    ),
                    "num": st.column_config.NumberColumn(
                        "花粉指数",
                        help="Number of Pollen",
                        format="%d",
                    ),
                    "Date": st.column_config.DatetimeColumn(
                        "日期",
                        format="YYYY-MM-DD",
                    ),
                },
                hide_index=True
    )
    
    # table_day = pollen_day.drop('Date', axis=1)
    # table_day['num']  = table_day['num'].fillna(0)
    # table_day['num']  = table_day['num'].astype(int)
    # st.table(table_day)


with col[1]:
    st.markdown('#### 花粉最多十城市')

    cities = pollen_day_sorted['City']
    values = pollen_day_sorted['num']
    label  = '花粉最多十城市'
    fig = make_bar(cities, values, label, 5, 5)
    st.pyplot(fig)

with col[2]:        
    with st.expander('花粉指数', expanded=True):
        st.write('''
            - 极高（>=801）： 极易过敏，敏感人群需加强防护和用药，室内需开启净化装置
            - 很高（501~800）：敏感人群尽量减少外出，按时用药，室内需开启净化装置
            - 较高（301~500）：敏感人群尽量减少外出，并按需用药
            - 偏高（100~300）：敏感人群减少外出，外出需防护
            - 较低（51~100）：敏感人群外出需防护
            - 很低（<=50）：不易过敏
            ''')
