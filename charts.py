import logging
from io import BytesIO

import requests
import seaborn as sns
import matplotlib.pyplot as plt
import pandas as pd
import numpy as np


from datetime import datetime


'''
@Title charts service
@Project ：Crime data analysis
@File    ：charts.py
@Author  ：XChen202
@Date    ：7/15/2022 9:50M
@evn python3.7
'''


# search data for website(return json)
def getWebData(param):
    crime_type = tuple(param.getlist("crime_type"));

    date_between = param.get("date_between").split(" - ");
    start_date = datetime.strptime(date_between[0], '%m-%d-%Y').__format__("%Y-%m-%dT%H:%M:%S")
    end_date = datetime.strptime(date_between[1], '%m-%d-%Y').__format__("%Y-%m-%dT%H:%M:%S")
    start_latitude = param.get("start_latitude")
    start_longitude = param.get("start_longitude")
    end_latitude = param.get("end_latitude")
    end_longitude = param.get("end_longitude")

    baseurl = "https://data.cityofchicago.org/resource/w98m-zvie.json"

    #datebetw = "?$where=date between '2019-01-01T12:00:00' and '2019-07-16T14:00:00'"
    datebetw = "?$where=date between '"+start_date+"' and '"+end_date+"'"

    # syntax for below filter is  'within_box(location_col, NW_lat, NW_long, SE_lat, SE_long)'
    boxurl = 'within_box(location, %s, %s, %s, %s)' % (start_latitude, start_longitude, end_latitude, end_longitude)

    # Create the overall URL to interogate API with our data and location filters
    ourl = baseurl + datebetw + ' AND ' + boxurl + " AND primary_type in" + str(crime_type)
    logging.info(ourl)
    text = requests.get(ourl).json()

    # create pandas dataframe dictionary container object
    df = pd.DataFrame(
        text, columns=['date', 'block', 'primary_type', 'description'])

    df.rename(columns = {'primary_type': 'Primary Type'}, inplace=True)
    return df;
#end getWebData


#bar chart
def get_bar_chart_iamge(crimes):

    types = crimes[['Primary Type']]
    crime_count = pd.DataFrame(types.groupby('Primary Type').size().sort_values(ascending=False).rename('counts').reset_index())
    logging.info("coutns:"+ str(len(crime_count)));

    # Plot the total crashes
    sns.set_color_codes("pastel")
    print(crime_count.iloc[:10, :])
    sns.barplot(x="counts", y="Primary Type", data=crime_count.iloc[:10, :],
                color="b", linewidth=4.5)
    plt.subplots_adjust(left=0.4)  # 调整图片边缘距离


    label = "counts " + str(crime_count.iloc[:10, :]["counts"].sum())
    plt.title('Bar chart ')
    plt.xlabel('Number')
    plt.ylabel('Primary Type')
    plt.legend([label])
    # Add a legend and informative axis label
    #plt.show()

    img = BytesIO()
    plt.savefig(img)
    img.seek(0)
    plt.close('all')
    return img
#end get_bar_chart_iamge


#line chart
def get_line_chart_iamge(crimes):
    types = crimes[['Primary Type']].groupby('Primary Type')
    crime_count = pd.DataFrame(types.size().sort_values(ascending=False).rename('counts').reset_index())
    logging.info("coutns:"+ str(len(crime_count)));

    label = 'Primary Type Counts: ' + str(crime_count.iloc[:10, :]["counts"].sum())
    plt.plot(crime_count["counts"], color='r')
    #['THEFT', 'BATTERY', 'DECEPTIVE PRACTICE', 'BURGLARY', 'CRIMINAL DAMAGE', 'OTHER OFFENSE', 'ASSAULT', 'CRIMINAL TRESPASS', 'MOTOR VEHICLE THEFT', 'ROBBERY', 'CRIMINAL SEXUAL ASSAULT', 'NARCOTICS', 'PUBLIC PEACE VIOLATION', 'SEX OFFENSE']
    xticks_text = crime_count["Primary Type"].values.tolist()
    xticks_unit = range(len(xticks_text))
    plt.xticks(xticks_unit, xticks_text, rotation=45)

    #plt.subplots_adjust(left=0.05, right=0.95, top=0.95, bottom=0.3)  # 调整图片边缘距离
    plt.subplots_adjust(bottom=0.4)  # 调整图片边缘距离


    # image
    plt.title('Line chart ')
    plt.xlabel('Number')
    plt.ylabel('Primary Type')
    plt.legend([label])
    #plt.show()

    img = BytesIO()
    plt.savefig(img)
    img.seek(0)
    plt.close('all')
    return img
#end get_line_chart_iamge


#pie chart
def get_pie_chart_iamge(crimes):
    s = crimes[['Primary Type']]
    crime_count = pd.DataFrame(
    s.groupby('Primary Type').size().sort_values(ascending=False).rename('counts').reset_index());
    logging.info("coutns:" + str(len(crime_count)));

    labels = crime_count['Primary Type']
    data = crime_count['counts']


    explode = np.zeros(len(crime_count));
    maxIndex = crime_count['counts'].idxmax(axis=0)
    explode[maxIndex] = 0.2;
    # y = np.array([35, 25, 25, 15])


    plt.pie(data,
        labels=labels,  # 设置饼图标签
        explode=explode,  # 第二部分突出显示，值越大，距离中心越远
        autopct='%.2f%%',  # 格式化输出百分比
        #shadow=True
    );
    label = "counts " + str(crime_count.iloc[:10, :]["counts"].sum())
    plt.legend([label])
    #plt.show()

    img = BytesIO()
    plt.savefig(img)
    img.seek(0)
    plt.close('all')
    return img
#end get_pie_chart_iamge


