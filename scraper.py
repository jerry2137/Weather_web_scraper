from pandas import DataFrame, ExcelWriter, to_numeric, to_datetime, read_excel, Timedelta, Timestamp, date_range, concat
import requests
import sys
import os
from tkinter import Tk, ttk, Label, Button, IntVar, Checkbutton
import base64


path = os.path.dirname(os.path.realpath(sys.argv[0])) + '/weather.xlsx'

def save(df, sheet):
    if not os.path.isfile(path):
        DataFrame().to_excel(path, sheet_name=sheet)

    with ExcelWriter(path, engine="openpyxl", mode="a") as writer:
        workBook = writer.book
        try:
            workBook.remove(workBook[sheet])
        except:
            print("creating sheet: " + sheet)
        finally:
            df.to_excel(writer, sheet_name=sheet)

def scrap(ym):
    page = requests.get('https://www.hko.gov.hk/cis/dailyExtract/dailyExtract_' + ym + '.xml')
    table = page.json()['stn']['data'][0]['dayData']
    df = DataFrame(table)
    df = df.loc[df[0].str.isdigit(), [0, 3, 5, 6]]

    df.columns = [
        'Day',
        'Air Temperature Mean (deg. C)',
        'Mean Dew Point (deg. C)',
        'Mean Relative Humidity (%)',
    ]
    df.set_index('Day', inplace=True)
    df = df.apply(to_numeric, errors='coerce')

    df['Cooling Degree Day (deg. C)'] = df['Air Temperature Mean (deg. C)'].map(lambda x : max(0, x - 18.5))
    return df

def total(df, sequence=[i for i in range(7)]):
    return [
        df.iloc[:,sequence[0]].sum(),
        df.iloc[:,sequence[1]].mean(),
        df.iloc[:,sequence[2]].max(),
        df.iloc[:,sequence[3]].min(),
        df.iloc[:,sequence[4]].mean(),
        df.iloc[:,sequence[5]].max(),
        df.iloc[:,sequence[6]].min(),
    ]

def try_sheet(sheet_name):
    try:
        df = read_excel(path, sheet_name=sheet_name, index_col=0)
    except:
        df = DataFrame(columns=['total CDD', 'avg. temp.', 'max temp.', 'min temp.', 'avg. RH', 'max RH', 'min RH'])
        print(sheet_name + ' sheet does not exist')
    return df

def summary(start, end, day, month, year):
    summary_df = try_sheet('summary')

    months_df = DataFrame(columns=['total CDD', 'avg. temp.', 'max temp.', 'min temp.', 'avg. RH', 'max RH', 'min RH'])
    end_month = end
    while end_month >= start:
        end_month = end_month.replace(day=1)
        this_month = end_month.strftime('%Y%m')

        day_df = scrap(this_month)
        months_df.loc[end_month] = total(day_df, [3,0,0,0,2,2,2])

        day_df.loc['Total'], day_df.loc['Mean'] = day_df.sum(), day_df.mean()
        if day:
            save(day_df, this_month)

        end_month = end_month - Timedelta(days=1)

    for year in range(start.year, end.year+1):
        month_df = months_df.loc[months_df.index.year == year]
        month_df.index = month_df.index.month
        month_df = concat([month_df, try_sheet(str(year))])
        month_df = month_df[~month_df.index.duplicated(keep='first')]
        month_df.sort_index(inplace=True)
        summary_df.loc[year] = total(month_df)
        if month:
            save(month_df, str(year))

    if year:
        summary_df.loc['all'] = total(summary_df)
        summary_df = summary_df.reindex(sorted(summary_df.columns), axis=1)
        save(summary_df, 'summary')

# def ask_month():
#     print('Please input starting month')
#     while True:
#         try:
#             start = to_datetime(input())
#             if start > Timestamp.now():
#                 print('Starting date in the future')
#                 continue
#             break
#         except:
#             print('Invalid date format')
#     print('Please input ending month')
#     while True:
#         try:
#             end = to_datetime(input())
#             if end > Timestamp.now():
#                 print('Ending date in the future')
#                 continue
#             if end < start:
#                 print('Ending date before starting date')
#                 continue
#             break
#         except:
#             print('Invalid date format')
#     summary(start, end)

def icon(window):
    #The Base64 icon version as a string
    icon = \
        '''
        AAABAAEAQEAAAAEAIAAoQgAAFgAAACgAAABAAAAAgAAAAAEAIAAAAAAAAAAAAAAAAAAAAAAAAAAA
        AAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAA
        AAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAA0W4AUNFuAOjRbgDo0W4AUAAAAAAA
        AAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAANFuAFDRbgDo0W4A6NFu
        AFAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAA
        AAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAA
        AAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAA
        AAAAAAAAANFuAOjSbwD/0m8A/9FuAOgAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAA
        AAAAAAAAAAAAAAAAAADRbgDo0m8A/9JvAP/RbgDoAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAA
        AAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAA
        AAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAA
        AAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAADSbwD/0m8A/9JvAP/SbwD/AAAAAAAA
        AAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAA0m8A/9JvAP/SbwD/0m8A
        /wAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAA
        AAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAA
        AAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAA
        AAAAAAAA0m8A/9JvAP/SbwD/0m8A/wAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAA
        AAAAAAAAAAAAAAAAANJvAP/SbwD/0m8A/9JvAP8AAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAA
        AAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAA
        AAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAA
        AADRbgBQ0W4A6NFuAOjRbgBQAAAAAAAAAAAAAAAAAAAAANJvAP/SbwD/0m8A/9JvAP8AAAAAAAAA
        AAAAAAAAAAAA0W4AUNFuAOjRbgDo0W4AUAAAAAAAAAAAAAAAAAAAAADSbwD/0m8A/9JvAP/SbwD/
        AAAAAAAAAAAAAAAAAAAAANFuAFDRbgDo0W4A6NFuAFAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAA
        AAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAA
        AAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAA0W4A6NJvAP/SbwD/0W4A6AAAAAAAAAAAAAAA
        AAAAAADSbwD/0m8A/9JvAP/SbwD/AAAAAAAAAAAAAAAAAAAAANFuAOjSbwD/0m8A/9FuAOgAAAAA
        AAAAAAAAAAAAAAAA0m8A/9JvAP/SbwD/0m8A/wAAAAAAAAAAAAAAAAAAAADRbgDo0m8A/9JvAP/R
        bgDoAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAA
        AAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAA
        ANJvAP/SbwD/0m8A/9JvAP8AAAAAAAAAAAAAAAAAAAAA0W4A6NJvAP/SbwD/0W4A6AAAAAAAAAAA
        AAAAAAAAAADSbwD/0m8A/9JvAP/SbwD/AAAAAAAAAAAAAAAAAAAAANFuAOjSbwD/0m8A/9FuAOgA
        AAAAAAAAAAAAAAAAAAAA0m8A/9JvAP/SbwD/0m8A/wAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAA
        AAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAA
        AAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAADSbwD/0m8A/9JvAP/SbwD/AAAAAAAAAAAAAAAA
        AAAAANFuAFDRbgDo0W4A6NFuAFAAAAAAAAAAAAAAAAAAAAAA0m8A/9JvAP/SbwD/0m8A/wAAAAAA
        AAAAAAAAAAAAAADRbgBQ0W4A6NFuAOjRbgBQAAAAAAAAAAAAAAAAAAAAANJvAP/SbwD/0m8A/9Jv
        AP8AAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAA
        AAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAA
        0m8A/9JvAP/SbwD/0m8A/wAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAA
        AAAAAAAAANJvAP/SbwD/0m8A/9JvAP8AAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAA
        AAAAAAAAAAAAAAAAAADSbwD/0m8A/9JvAP/SbwD/AAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAA
        AAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAA
        AAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAANJvAP/SbwD/0m8A/9JvAP8AAAAAAAAAAAAAAAAA
        AAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAADSbwD/0m8A/9JvAP/SbwD/AAAAAAAA
        AAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAA0m8A/9JvAP/SbwD/0m8A
        /wAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAA
        AAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAADR
        bgDo0m8A/9JvAP/RbgDoAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAA
        AAAAAAAA0W4A6NJvAP/SbwD/0W4A6AAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAA
        AAAAAAAAAAAAAAAAANFuAOjSbwD/0m8A/9FuAOgAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAA
        AAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAA
        AAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAA0W4AUNFuAOjRbgDo0W4AUAAAAAAAAAAAAAAAAAAA
        AAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAANFuAFDRbgDo0W4A6NFuAFAAAAAAAAAA
        AAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAADRbgBQ0W4A6NFuAOjRbgBQ
        AAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAA
        AAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAA
        AAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAA
        AAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAA
        AAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAA
        AAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAA
        AAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAA
        AAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAA
        AAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAA
        AAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAA
        AAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAADFxcUixcXFeMXFxbrFxcXkxcXF+sbGxv/Gxsb/xsbG
        /8bGxv/Gxsb/xsbG/8bGxv/Gxsb/xsbG/8bGxv/Gxsb/xsbG/8bGxv/Gxsb/xsbG/8bGxv/Gxsb/
        xsbG/8bGxv/Gxsb/xsbG/8bGxv/Gxsb/xsbG/8bGxv/Gxsb/xsbG/8bGxv/Gxsb/xsbG/8bGxv/G
        xsb/xsbG/8bGxv/Gxsb/xsbG/8bGxv/Gxsb/xsbG/8bGxv/FxcX6xcXF5MXFxbrFxcV4xcXFIAAA
        AAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAMXFxSDFxcWoxcXF
        /MbGxv/Gxsb/xsbG/8bGxv/Gxsb/xsbG/8bGxv/Gxsb/xsbG/8bGxv/Gxsb/xsbG/8bGxv/Gxsb/
        xsbG/8bGxv/Gxsb/xsbG/8bGxv/Gxsb/xsbG/8bGxv/Gxsb/xsbG/8bGxv/Gxsb/xsbG/8bGxv/G
        xsb/xsbG/8bGxv/Gxsb/xsbG/8bGxv/Gxsb/xsbG/8bGxv/Gxsb/xsbG/8bGxv/Gxsb/xsbG/8bG
        xv/Gxsb/xsbG/8bGxv/Gxsb/xsbG/8bGxvzFxcWmxcXFIAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAA
        AAAAAAAAAAAAAAAAAMXFxVzFxcXyxsbG/8bGxv/Gxsb/xsbG/8bGxv/Gxsb/xsbG/8bGxv/Gxsb/
        xsbG/8bGxv/Gxsb/xsbG/8bGxv/Gxsb/xsbG/8bGxv/Gxsb/xsbG/8bGxv/Gxsb/xsbG/8bGxv/G
        xsb/xsbG/8bGxv/Gxsb/xsbG/8bGxv/Gxsb/xsbG/8bGxv/Gxsb/xsbG/8bGxv/Gxsb/xsbG/8bG
        xv/Gxsb/xsbG/8bGxv/Gxsb/xsbG/8bGxv/Gxsb/xsbG/8bGxv/Gxsb/xsbG/8bGxv/Gxsb/xsbG
        /8bGxvLFxcVaAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAMXFxXTGxsb/xsbG/8bGxv/Gxsb/
        xsbG/8bGxv/Gxsb/xsbG/8bGxv/Gxsb/xsbG/8bGxv/Gxsb/xsbG/8bGxv/Gxsb/xsbG/8bGxv/G
        xsb/xsbG/8bGxv/Gxsb/xsbG/8bGxv/Gxsb/xsbG/8bGxv/Gxsb/xsbG/8bGxv/Gxsb/xsbG/8bG
        xv/Gxsb/xsbG/8bGxv/Gxsb/xsbG/8bGxv/Gxsb/xsbG/8bGxv/Gxsb/xsbG/8bGxv/Gxsb/xsbG
        /8bGxv/Gxsb/xsbG/8bGxv/Gxsb/xsbG/8bGxv/Gxsb/xcXF/8XFxXQAAAAAAAAAAAAAAAAAAAAA
        AAAAAMXFxVzGxsb/xsbG/8bGxv/Gxsb/xsbG/8bGxv/Gxsb/xsbG/8bGxv/Gxsb/xsbG/8bGxv/G
        xsb/xsbG/8bGxv/Gxsb/xsbG/8bGxv/Gxsb/xsbG/8bGxv/Gxsb/xsbG/8bGxv/Gxsb/xsbG/8bG
        xv/Gxsb/xsbG/8bGxv/Gxsb/xsbG/8bGxv/Gxsb/xsbG/8bGxv/Gxsb/xsbG/8bGxv/Gxsb/xsbG
        /8bGxv/Gxsb/xsbG/8bGxv/Gxsb/xsbG/8bGxv/Gxsb/xsbG/8bGxv/Gxsb/xsbG/8bGxv/Gxsb/
        xsbG/8bGxv/FxcX/xcXFWgAAAAAAAAAAAAAAAMXFxSDFxcXyxsbG/8bGxv/Gxsb/xsbG/8bGxv/G
        xsb/xsbG/8bGxv/Gxsb/xsbG/8bGxv/Gxsb/xsbG/8bGxv/Gxsb/xsbG/8bGxv/Gxsb/xsbG/8bG
        xv/Gxsb/xsbG/8bGxv/Gxsb/xsbG/8bGxv/Gxsb/xsbG/8bGxv/Gxsb/xsbG/8bGxv/Gxsb/xsbG
        /8bGxv/Gxsb/xsbG/8bGxv/Gxsb/xsbG/8bGxv/Gxsb/xsbG/8bGxv/Gxsb/xsbG/8bGxv/Gxsb/
        xsbG/8bGxv/Gxsb/xsbG/8bGxv/Gxsb/xsbG/8bGxv/Gxsb/xsbG/8bGxvLFxcUgAAAAAAAAAADF
        xcWoxsbG/8bGxv/Gxsb/xsbG/8bGxv/Gxsb/xsbG/8bGxv/Gxsb/xsbG/8bGxv/Gxsb/xsbG/8bG
        xv/Gxsb/xsbG/8bGxv/Gxsb/xsbG/8bGxv/Gxsb/xsbG/8bGxv/Gxsb/xsbG/8bGxv/Gxsb/xsbG
        /8bGxv/Gxsb/xsbG/8bGxv/Gxsb/xsbG/8bGxv/Gxsb/xsbG/8bGxv/Gxsb/xsbG/8bGxv/Gxsb/
        xsbG/8bGxv/Gxsb/xsbG/8bGxv/Gxsb/xsbG/8bGxv/Gxsb/xsbG/8bGxv/Gxsb/xsbG/8bGxv/G
        xsb/xsbG/8bGxv/Gxsb/xcXFpgAAAADFxcUixcXF/MbGxv/Gxsb/xsbG/8bGxv/Gxsb/xsbG/8bG
        xv/Gxsb/xsbG/8bGxv/Gxsb/xsbG/8bGxv/Gxsb/xsbG/8bGxv/Gxsb/xsbG/8bGxv/Gxsb/xsbG
        /8bGxv/Gxsb/xsbG/8bGxv/Gxsb/xsbG/8bGxv/Gxsb/xsbG/8bGxv/Gxsb/xsbG/8bGxv/Gxsb/
        xsbG/8bGxv/Gxsb/xsbG/8bGxv/Gxsb/xsbG/8bGxv/Gxsb/xsbG/8bGxv/Gxsb/xsbG/8bGxv/G
        xsb/xsbG/8bGxv/Gxsb/xsbG/8bGxv/Gxsb/xsbG/8bGxv/Gxsb/xsbG/8bGxvzFxcUgxcXFesbG
        xv/Gxsb/xsbG/8bGxv/Gxsb/xsbG/8bGxv/Gxsb/xsbG/8bGxv/Gxsb/xsbG/8bGxv/Gxsb/xsbG
        /8bGxv/Gxsb/xsbG/8bGxv/Gxsb/xsbG/8bGxv/Gxsb/xsbG/8bGxv/Gxsb/xsbG/8bGxv/Gxsb/
        xsbG/8bGxv/Gxsb/xsbG/8bGxv/Gxsb/xsbG/8bGxv/Gxsb/xsbG/8bGxv/Gxsb/xsbG/8bGxv/G
        xsb/xsbG/8bGxv/Gxsb/xsbG/8bGxv/Gxsb/xsbG/8bGxv/Gxsb/xsbG/8bGxv/Gxsb/xsbG/8bG
        xv/Gxsb/xsbG/8bGxv/Gxsb/xcXFeMXFxbrGxsb/xsbG/8bGxv/Gxsb/xsbG/8bGxv/Gxsb/xsbG
        /8bGxv/Gxsb/xsbG/8bGxv/Gxsb/xsbG/8bGxv/Gxsb/xsbG/8bGxv/Gxsb/xsbG/8bGxv/Gxsb/
        xsbG/8bGxv/Gxsb/xsbG/8bGxv/Gxsb/xsbG/8bGxv/Gxsb/xsbG/8bGxv/Gxsb/xsbG/8bGxv/G
        xsb/xsbG/8bGxv/Gxsb/xsbG/8bGxv/Gxsb/xsbG/8bGxv/Gxsb/xsbG/8bGxv/Gxsb/xsbG/8bG
        xv/Gxsb/xsbG/8bGxv/Gxsb/xsbG/8bGxv/Gxsb/xsbG/8bGxv/Gxsb/xsbG/8XFxbrFxcXmxsbG
        /8bGxv/Gxsb/xsbG/8bGxv/Gxsb/xsbG/8bGxv/Gxsb/xsbG/8bGxv/Gxsb/xsbG/8bGxv/Gxsb/
        xsbG/8bGxv/Gxsb/xsbG/8bGxv/Gxsb/xsbG/8bGxv/Gxsb/xsbG/8bGxv/Gxsb/xsbG/8bGxv/G
        xsb/xsbG/8bGxv/Gxsb/xsbG/8bGxv/Gxsb/xsbG/8bGxv/Gxsb/xsbG/8bGxv/Gxsb/xsbG/8bG
        xv/Gxsb/xsbG/8bGxv/Gxsb/xsbG/8bGxv/Gxsb/xsbG/8bGxv/Gxsb/xsbG/8bGxv/Gxsb/xsbG
        /8bGxv/Gxsb/xsbG/8bGxv/FxcXkxcXF+sbGxv/Gxsb/xsbG/8bGxv/Gxsb/xsbG/8bGxv/Gxsb/
        xsbG/8bGxv/Gxsb/xsbG/8bGxv/Gxsb/xsbG/8bGxv/Gxsb/xsbG/8bGxv/Gxsb/xsbG/8bGxv/G
        xsb/xsbG/8bGxv/Gxsb/xsbG/8bGxv/Gxsb/xsbG/8bGxv/Gxsb/xsbG/8bGxv/Gxsb/xsbG/8bG
        xv/Gxsb/xsbG/8bGxv/Gxsb/xsbG/8bGxv/Gxsb/xsbG/8bGxv/Gxsb/xsbG/8bGxv/Gxsb/xsbG
        /8bGxv/Gxsb/xsbG/8bGxv/Gxsb/xsbG/8bGxv/Gxsb/xsbG/8bGxv/Gxsb/xcXF+sXFxfrGxsb/
        xsbG/8bGxv/Gxsb/xsbG/8bGxv/Gxsb/xsbG/8bGxv/Gxsb/xsbG/8bGxv/Gxsb/xsbG/8bGxv/G
        xsb/xsbG/8bGxv/Gxsb/xsbG/8bGxv/Gxsb/xsbG/8bGxv/Gxsb/xsbG/8bGxv/Gxsb/xsbG/8bG
        xv/Gxsb/xsbG/8bGxv/Gxsb/xsbG/8bGxv/Gxsb/xsbG/8bGxv/Gxsb/xsbG/8bGxv/Gxsb/xsbG
        /8bGxv/Gxsb/xsbG/8bGxv/Gxsb/xsbG/8bGxv/Gxsb/xsbG/8bGxv/Gxsb/xsbG/8bGxv/Gxsb/
        xsbG/8bGxv/Gxsb/xsbG/8XFxfrFxcXkxsbG/8bGxv/Gxsb/xsbG/8bGxv/Gxsb/xsbG/8bGxv/G
        xsb/xsbG/8bGxv/Gxsb/xsbG/8bGxv/Gxsb/xsbG/8bGxv/Gxsb/xsbG/8bGxv/Gxsb/xsbG/8bG
        xv/Gxsb/xsbG/8bGxv/Gxsb/xsbG/8bGxv/Gxsb/xsbG/8bGxv/Gxsb/xsbG/8bGxv/Gxsb/xsbG
        /8bGxv/Gxsb/xsbG/8bGxv/Gxsb/xsbG/8bGxv/Gxsb/xsbG/8bGxv/Gxsb/xsbG/8bGxv/Gxsb/
        xsbG/8bGxv/Gxsb/xsbG/8bGxv/Gxsb/xsbG/8bGxv/Gxsb/xsbG/8bGxv/FxcXkxcXFusbGxv/G
        xsb/xsbG/8bGxv/Gxsb/xsbG/8bGxv/Gxsb/xsbG/8bGxv/Gxsb/xsbG/8bGxv/Gxsb/xsbG/8bG
        xv/Gxsb/xsbG/8bGxv/Gxsb/xsbG/8bGxv/Gxsb/xsbG/8bGxv/Gxsb/xsbG/8bGxv/Gxsb/xsbG
        /8bGxv/Gxsb/xsbG/8bGxv/Gxsb/xsbG/8bGxv/Gxsb/xsbG/8bGxv/Gxsb/xsbG/8bGxv/Gxsb/
        xsbG/8bGxv/Gxsb/xsbG/8bGxv/Gxsb/xsbG/8bGxv/Gxsb/xsbG/8bGxv/Gxsb/xsbG/8bGxv/G
        xsb/xsbG/8bGxv/Gxsb/xcXFusXFxXjGxsb/xsbG/8bGxv/Gxsb/xsbG/8bGxv/Gxsb/xsbG/8bG
        xv/Gxsb/xsbG/8bGxv/Gxsb/xsbG/8bGxv/Gxsb/xsbG/8bGxv/Gxsb/xsbG/8bGxv/Gxsb/xsbG
        /8bGxv/Gxsb/xsbG/8bGxv/Gxsb/xsbG/8bGxv/Gxsb/xsbG/8bGxv/Gxsb/xsbG/8bGxv/Gxsb/
        xsbG/8bGxv/Gxsb/xsbG/8bGxv/Gxsb/xsbG/8bGxv/Gxsb/xsbG/8bGxv/Gxsb/xsbG/8bGxv/G
        xsb/xsbG/8bGxv/Gxsb/xsbG/8bGxv/Gxsb/xsbG/8bGxv/Gxsb/xsbG/8XFxXjFxcUgxcXF/MbG
        xv/Gxsb/xsbG/8bGxv/Gxsb/xsbG/8bGxv/Gxsb/xsbG/8bGxv/Gxsb/xsbG/8bGxv/Gxsb/xsbG
        /8bGxv/Gxsb/xsbG/8bGxv/Gxsb/xsbG/8bGxv/Gxsb/xsbG/8bGxv/Gxsb/xsbG/8bGxv/Gxsb/
        xsbG/8bGxv/Gxsb/xsbG/8bGxv/Gxsb/xsbG/8bGxv/Gxsb/xsbG/8bGxv/Gxsb/xsbG/8bGxv/G
        xsb/xsbG/8bGxv/Gxsb/xsbG/8bGxv/Gxsb/xsbG/8bGxv/Gxsb/xsbG/8bGxv/Gxsb/xsbG/8bG
        xv/Gxsb/xsbG/8XFxfzFxcUgAAAAAMXFxabGxsb/xsbG/8bGxv/Gxsb/xsbG/8bGxv/Gxsb/xsbG
        /8bGxv/Gxsb/xsbG/8bGxv/Gxsb/xsbG/8bGxv/Gxsb/xsbG/8bGxv/Gxsb/xsbG/8bGxv/Gxsb/
        xsbG/8bGxv/Gxsb/xsbG/8bGxv/Gxsb/xsbG/8bGxv/Gxsb/xsbG/8bGxv/Gxsb/xsbG/8bGxv/G
        xsb/xsbG/8bGxv/Gxsb/xsbG/8bGxv/Gxsb/xsbG/8bGxv/Gxsb/xsbG/8bGxv/Gxsb/xsbG/8bG
        xv/Gxsb/xsbG/8bGxv/Gxsb/xsbG/8bGxv/Gxsb/xsbG/8bGxv/FxcWoAAAAAAAAAADFxcUgxcXF
        8sbGxv/Gxsb/xsbG/8bGxv/Gxsb/xsbG/8bGxv/Gxsb/xsbG/8bGxv/Gxsb/xsbG/8bGxv/Gxsb/
        xsbG/8bGxv/Gxsb/xsbG/8bGxv/Gxsb/xsbG/8bGxv/Gxsb/xsbG/8bGxv/Gxsb/xsbG/8bGxv/G
        xsb/xsbG/8bGxv/Gxsb/xsbG/8bGxv/Gxsb/xsbG/8bGxv/Gxsb/xsbG/8bGxv/Gxsb/xsbG/8bG
        xv/Gxsb/xsbG/8bGxv/Gxsb/xsbG/8bGxv/Gxsb/xsbG/8bGxv/Gxsb/xsbG/8bGxv/Gxsb/xsbG
        /8bGxv/FxcXyxcXFIAAAAAAAAAAAAAAAAMXFxVrGxsb/xsbG/8bGxv/Gxsb/xsbG/8bGxv/Gxsb/
        xsbG/8bGxv/Gxsb/xsbG/8bGxv/Gxsb/xsbG/8bGxv/Gxsb/xsbG/8bGxv/Gxsb/xsbG/8bGxv/G
        xsb/xsbG/8bGxv/Gxsb/xsbG/8bGxv/Gxsb/xsbG/8bGxv/Gxsb/xsbG/8bGxv/Gxsb/xsbG/8bG
        xv/Gxsb/xsbG/8bGxv/Gxsb/xsbG/8bGxv/Gxsb/xsbG/8bGxv/Gxsb/xsbG/8bGxv/Gxsb/xsbG
        /8bGxv/Gxsb/xsbG/8bGxv/Gxsb/xsbG/8bGxv/Gxsb/xcXFXAAAAAAAAAAAAAAAAAAAAAAAAAAA
        xcXFdMbGxv/Gxsb/xsbG/8bGxv/Gxsb/xsbG/8bGxv/Gxsb/xsbG/8bGxv/Gxsb/xsbG/8bGxv/G
        xsb/xsbG/8bGxv/Gxsb/xsbG/8bGxv/Gxsb/xsbG/8bGxv/Gxsb/xsbG/8bGxv/Gxsb/xsbG/8bG
        xv/Gxsb/xsbG/8bGxv/Gxsb/xsbG/8bGxv/Gxsb/xsbG/8bGxv/Gxsb/xsbG/8bGxv/Gxsb/xsbG
        /8bGxv/Gxsb/xsbG/8bGxv/Gxsb/xsbG/8bGxv/Gxsb/xsbG/8bGxv/Gxsb/xsbG/8bGxv/Gxsb/
        xcXFdAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAADFxcVaxcXF8sbGxv/Gxsb/xsbG/8bGxv/G
        xsb/xsbG/8bGxv/Gxsb/xsbG/8bGxv/Gxsb/xsbG/8bGxv/Gxsb/xsbG/8bGxv/Gxsb/xsbG/8bG
        xv/Gxsb/xsbG/8bGxv/Gxsb/xsbG/8bGxv/Gxsb/xsbG/8bGxv/Gxsb/xsbG/8bGxv/Gxsb/xsbG
        /8bGxv/Gxsb/xsbG/8bGxv/Gxsb/xsbG/8bGxv/Gxsb/xsbG/8bGxv/Gxsb/xsbG/8bGxv/Gxsb/
        xsbG/8bGxv/Gxsb/xsbG/8bGxv/FxcXyxsbGXAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAA
        AAAAAAAAAMXFxSDFxcX8xsbG/8bGxv/Gxsb/xsbG/8bGxv/Gxsb/xsbG/8bGxv/Gxsb/xsbG/8bG
        xv/Gxsb/xsbG/8bGxv/Gxsb/xsbG/8bGxv/Gxsb/xsbG/8bGxv/Gxsb/xsbG/8bGxv/Gxsb/xsbG
        /8bGxv/Gxsb/xsbG/8bGxv/Gxsb/xsbG/8bGxv/Gxsb/xsbG/8bGxv/Gxsb/xsbG/8bGxv/Gxsb/
        xsbG/8bGxv/Gxsb/xsbG/8bGxv/Gxsb/xsbG/8bGxv/Gxsb/xsbG/8XFxfzFxcWoxcXFIAAAAAAA
        AAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAxcXF7sbGxv/Gxsb/xsbG/8bG
        xv/Gxsb/xsbG/8bGxv/Gxsb/xsbG/8bGxv/Gxsb/xsbG/8bGxv/Gxsb/xsbG/8bGxv/Gxsb/xsbG
        /8bGxv/Gxsb/xsbG/8bGxv/Gxsb/xsbG/8bGxv/Gxsb/xsbG/8bGxv/Gxsb/xsbG/8bGxv/Gxsb/
        xsbG/8bGxv/Gxsb/xsbG/8bGxv/Gxsb/xsbG/8bGxv/Gxsb/xsbG/8bGxv/Gxsb/xsbG/8bGxv/G
        xsb/xsbG/8XFxYLFxcUiAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAA
        AAAAAAAAAAAAAMXFxdLGxsb/xsbG/8bGxv/Gxsb/xsbG/8bGxv/Gxsb/xsbG/8bGxv/Gxsb/xsbG
        /8bGxv/Gxsb/xsbG/8bGxv/Gxsb/xsbG/8bGxv/Gxsb/xsbG/8bGxv/Gxsb/xsbG/8bGxv/Gxsb/
        xsbG/8bGxv/Gxsb/xsbG/8bGxv/Gxsb/xsbG/8bGxv/Gxsb/xsbG/8bGxv/Gxsb/xsbG/8bGxv/G
        xsb/xsbG/8bGxv/Gxsb/xsbG/8bGxv/Gxsb/xsbG/8XFxcYAAAAAAAAAAAAAAAAAAAAAAAAAAAAA
        AAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAADFxcWmxsbG/8bGxv/Gxsb/xsbG
        /8bGxv/Gxsb/xsbG/8bGxv/Gxsb/xsbG/8bGxv/Gxsb/xsbG/8bGxv/Gxsb/xsbG/8bGxv/Gxsb/
        xsbG/8bGxv/Gxsb/xsbG/8bGxv/Gxsb/xsbG/8bGxv/Gxsb/xsbG/8bGxv/Gxsb/xsbG/8bGxv/G
        xsb/xsbG/8bGxv/Gxsb/xsbG/8bGxv/Gxsb/xsbG/8bGxv/Gxsb/xsbG/8bGxv/Gxsb/xsbG/8XF
        xf/FxcVAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAA
        AAAAAAAAAAAAxcXFbsbGxv/Gxsb/xsbG/8bGxv/Gxsb/xsbG/8bGxv/Gxsb/xsbG/8bGxv/Gxsb/
        xsbG/8bGxv/Gxsb/xsbG/8bGxv/Gxsb/xsbG/8bGxv/Gxsb/xsbG/8bGxv/Gxsb/xsbG/8bGxv/G
        xsb/xsbG/8bGxv/Gxsb/xsbG/8bGxv/Gxsb/xsbG/8bGxv/Gxsb/xsbG/8bGxv/Gxsb/xsbG/8bG
        xv/Gxsb/xsbG/8bGxv/Gxsb/xsbG/8bGxv/FxcWcAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAA
        AAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAMXFxSTGxsb/xsbG/8bGxv/Gxsb/
        xsbG/8bGxv/Gxsb/xsbG/8bGxv/Gxsb/xsbG/8bGxv/Gxsb/xsbG/8bGxv/Gxsb/xsbG/8bGxv/G
        xsb/xsbG/8bGxv/Gxsb/xsbG/8bGxv/Gxsb/xsbG/8bGxv/Gxsb/xsbG/8bGxv/Gxsb/xsbG/8bG
        xv/Gxsb/xsbG/8bGxv/Gxsb/xsbG/8bGxv/Gxsb/xsbG/8bGxv/Gxsb/xsbG/8bGxv/FxcXIxcXF
        CgAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAA
        AAAAAAAAAAAAAAAAxcXFyMbGxv/Gxsb/xsbG/8bGxv/Gxsb/xsbG/8bGxv/Gxsb/xsbG/8bGxv/G
        xsb/xsbG/8bGxv/Gxsb/xsbG/8bGxv/Gxsb/xsbG/8bGxv/Gxsb/xsbG/8bGxv/Gxsb/xsbG/8bG
        xv/Gxsb/xsbG/8bGxv/Gxsb/xsbG/8bGxv/Gxsb/xsbG/8bGxv/Gxsb/xsbG/8bGxv/Gxsb/xsbG
        /8bGxv/Gxsb/xsbG/8bGxv/FxcXIxcXFEgAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAA
        AAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAMXFxVzGxsb/xsbG/8bGxv/G
        xsb/xsbG/8bGxv/Gxsb/xsbG/8bGxv/Gxsb/xsbG/8bGxv/Gxsb/xsbG/8bGxv/Gxsb/xsbG/8bG
        xv/Gxsb/xsbG/8bGxv/Gxsb/xsbG/8bGxv/Gxsb/xsbG/8bGxv/Gxsb/xsbG/8bGxv/Gxsb/xsbG
        /8bGxv/Gxsb/xsbG/8bGxv/Gxsb/xsbG/8bGxv/Gxsb/xsbG/8bGxv/FxcWcxsbGCgAAAAAAAAAA
        AAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAA
        AAAAAAAAAAAAAADGxsYExcXF2MbGxv/Gxsb/xsbG/8bGxv/Gxsb/xsbG/8bGxv/Gxsb/xsbG/8bG
        xv/Gxsb/xsbG/8bGxv/Gxsb/xsbG/8bGxv/Gxsb/xsbG/8bGxv/Gxsb/xsbG/8bGxv/Gxsb/xsbG
        /8bGxv/Gxsb/xsbG/8bGxv/Gxsb/xsbG/8bGxv/Gxsb/xsbG/8bGxv/Gxsb/xsbG/8bGxv/Gxsb/
        xsbG/8XFxcbFxcVCAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAA
        AAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAMXFxUjGxsb/xsbG/8bG
        xv/Gxsb/xsbG/8bGxv/Gxsb/xsbG/8bGxv/Gxsb/xsbG/8bGxv/Gxsb/xsbG/8bGxv/Gxsb/xsbG
        /8bGxv/Gxsb/xsbG/8bGxv/Gxsb/xsbG/8bGxv/Gxsb/xsbG/8bGxv/Gxsb/xsbG/8XFxf/FxcWc
        xcXFwMXFxejFxcX8xcXF+sXFxejFxcXAxcXFhMXFxTIAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAA
        AAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAA
        AAAAAAAAAAAAAAAAAAAAAAAAxcXFnMbGxv/Gxsb/xsbG/8bGxv/Gxsb/xsbG/8bGxv/Gxsb/xsbG
        /8bGxv/Gxsb/xsbG/8bGxv/Gxsb/xsbG/8bGxv/Gxsb/xsbG/8bGxv/Gxsb/xsbG/8bGxv/Gxsb/
        xsbG/8bGxv/Gxsb/xsbG/8bGxv/FxcWcAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAA
        AAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAA
        AAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAMXFxQrFxcXMxsbG
        /8bGxv/Gxsb/xsbG/8bGxv/Gxsb/xsbG/8bGxv/Gxsb/xsbG/8bGxv/Gxsb/xsbG/8bGxv/Gxsb/
        xsbG/8bGxv/Gxsb/xsbG/8bGxv/Gxsb/xsbG/8bGxv/Gxsb/xsbG/8bGxv/FxcXMxsbGCgAAAAAA
        AAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAA
        AAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAA
        AAAAAAAAAAAAAAAAAAAAAAAAAAAAxcXFGMXFxdjGxsb/xsbG/8bGxv/Gxsb/xsbG/8bGxv/Gxsb/
        xsbG/8bGxv/Gxsb/xsbG/8bGxv/Gxsb/xsbG/8bGxv/Gxsb/xsbG/8bGxv/Gxsb/xsbG/8bGxv/G
        xsb/xsbG/8bGxv/FxcXYxcXFGAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAA
        AAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAA
        AAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAADFxcUY
        xcXFzMbGxv/Gxsb/xsbG/8bGxv/Gxsb/xsbG/8bGxv/Gxsb/xsbG/8bGxv/Gxsb/xsbG/8bGxv/G
        xsb/xsbG/8bGxv/Gxsb/xsbG/8bGxv/Gxsb/xsbG/8bGxv/FxcXMxcXFGAAAAAAAAAAAAAAAAAAA
        AAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAA
        AAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAA
        AAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAMXFxQrFxcWcxcXF/8bGxv/Gxsb/xsbG/8bGxv/G
        xsb/xsbG/8bGxv/Gxsb/xsbG/8bGxv/Gxsb/xsbG/8bGxv/Gxsb/xsbG/8bGxv/Gxsb/xsbG/8bG
        xv/FxcWcxMTECgAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAA
        AAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAA
        AAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAA
        AAAAAAAAAMXFxUrFxcXYxsbG/8bGxv/Gxsb/xsbG/8bGxv/Gxsb/xsbG/8bGxv/Gxsb/xsbG/8bG
        xv/Gxsb/xsbG/8bGxv/Gxsb/xsbG/8XFxdjFxcVKAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAA
        AAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAA
        AAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAA
        AAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAxcXFBMXFxVzFxcXIxcXF/8bG
        xv/Gxsb/xsbG/8bGxv/Gxsb/xsbG/8bGxv/Gxsb/xsbG/8bGxv/FxcX/xcXFyMXFxVzFxcUEAAAA
        AAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAA
        AAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAA
        AAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAA
        AAAAAAAAAAAAAAAAAAAAAAAAAAAAAMXFxSTFxcVsxcXFpsXFxdDFxcXuxcXF/MXFxfzFxcXuxcXF
        0sXFxabFxcVuxcXFJAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAA
        AAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAA
        AAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAA
        AAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAA
        AAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAA
        AAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAA
        AAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAA
        AAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAA
        AAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAA
        AAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAA
        AAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAA
        AAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAA
        AAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAA
        AAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAA
        AAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAA
        AAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAA
        AAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAA
        AAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAA
        AAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAA
        AAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAA
        AAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAA
        AAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAA
        AAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAA
        AAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAA
        AAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAA
        AAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAA
        AAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAA
        AAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAA
        AAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAA
        AAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAA
        AAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAA
        AAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAA
        AAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAA
        AAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAA
        AAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAA
        AAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAA
        AAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAA
        AAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAA
        AAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAA
        AAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAA
        AAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAA
        AAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAA
        AAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAA
        AAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAA
        AAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAA
        AAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAA
        AAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAA
        AAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAA///+f/5///////w//D///////D/8P//////8
        P/w//////nw+fD5////8PDw8PD////w8PDw8P////D58Pnw////8P/w//D////w//D/8P////D/8
        P/w////+f/5//n////////////////////////+AAAAAAAH//AAAAAAAAD/4AAAAAAAAH/AAAAAA
        AAAP4AAAAAAAAAfAAAAAAAAAA4AAAAAAAAABgAAAAAAAAAGAAAAAAAAAAQAAAAAAAAAAAAAAAAAA
        AAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAIAAAAAAAAABgAAAAAAAAAGAAAAAAAAA
        AcAAAAAAAAAD4AAAAAAAAAfwAAAAAAAAD/gAAAAAAAAf/AAAAAAAAD/8AAAAAAAA//wAAAAAAAH/
        /AAAAAAAA//+AAAAAAAD//4AAAAAAAf//gAAAAAAD///AAAAAAAf//8AAAAAAH///4AAAAAB////
        gAAAAf/////AAAAD/////+AAAAf/////8AAAD//////4AAAf//////4AAH///////4AB////////
        8A//////////////////////////////////////////////////////////////////////////
        //////////////////////////////////////8=
        '''
    icondata= base64.b64decode(icon)
    # The temp file is icon.ico
    iconfile= "icon.ico"
    # Extract the icon
    with open(iconfile,"wb") as f:
        f.write(icondata)
    window.iconbitmap(iconfile)
    # Delete the tempfile
    os.remove(iconfile)

def time_optionList(window, kind):
    combobox = ttk.Combobox(window, state='readonly')

    if kind == 'year':
        t = 'year'
        combobox['values'] = date_range('1884', Timestamp.now(), freq='YS').strftime("%Y").tolist()[::-1]
    elif kind == 'month':
        t = 'month'
        combobox['values'] = date_range('2000-01', '2000-12', freq='MS').strftime("%b").tolist()
    
    Label(window, text=t).pack()
    combobox.pack()
    return combobox

def update(box, year, kind, start_year='', start_month=''):
    box.set('')
    
    start = to_datetime(year+'-01')
    end = to_datetime(year+'-12')
    frequency = 'MS'
    format = '%b'

    if kind == 'end_year':
        end = Timestamp.now()
        frequency = 'YS'
        format = '%Y'
        
    elif kind == 'end_month':
        if year == start_year:
            start = to_datetime(year+'-'+start_month)

    if year == str(Timestamp.now().year):
        end = Timestamp.now()
        
    box.config(values=date_range(start, end, freq=frequency).strftime(format).tolist())

def window():
    window = Tk()
    icon(window)
    window.title('Monthly Weather Scraper')
    window.geometry('600x550')

    Label(window, text='Monthly Weather Scraper', font=("Arial", 25)).pack()
    Label(window, text='This application will scrape the monthly weather data from HKO and save it into an Excel file.').pack()
    Label(window, text='The Excel file will be generated into the directory of this file.').pack()
    Label(window, text='Please do not modify the file manually.').pack()
    Label(window, text='If there is anything goes wrong, please delete the excel file and run this program again.').pack()

    Label(window, text='please choose a starting month', font=("Arial", 15)).pack()
    start_year_box = time_optionList(window, kind='year')
    start_month_box = time_optionList(window, kind='month')

    Label(window, text='please choose an ending month', font=("Arial", 15)).pack()
    end_year_box = time_optionList(window, kind='year')
    end_month_box = time_optionList(window, kind='month')

    start_year_box.bind('<<ComboboxSelected>>', lambda _:(
        update(start_month_box, start_year_box.get(), 'start_month'),
        update(end_year_box, start_year_box.get(), 'end_year')
    ))
    end_year_box.bind('<<ComboboxSelected>>', lambda _:(
        update(end_month_box, end_year_box.get(), 'end_month', start_year_box.get(), start_month_box.get())
    ))

    year_state = IntVar(value=1)
    month_state = IntVar(value=1)
    day_state = IntVar(value=1)
    Checkbutton(window, text='yearly summary', variable=year_state).pack()
    Checkbutton(window, text='monthly data per year', variable=month_state).pack()
    Checkbutton(window, text='daily data per month', variable=day_state).pack()

    Button(window, text='create', command=lambda :(
        start := start_year_box.get()+' '+start_month_box.get(),
        end := end_year_box.get()+' '+end_month_box.get(),
        result.config(text='Please select a time length')
        if not (day_state.get() | month_state.get() | year_state.get())
        else (
            result.config(text='Please select an interval')
            if not all([start_year_box.get(), start_month_box.get(), end_year_box.get(), end_month_box.get()])
            else(
                summary(to_datetime(start), to_datetime(end), day_state.get(), month_state.get(), year_state.get()),
                result.config(text=start+'~'+end+' '+'file saved!')
            )
        )
    )).pack()

    result = Label(window, text='')
    result.pack()

    Button(window, text='delete excel file', command=lambda :(os.remove(path) if os.path.isfile(path) else 0)).pack()
    

    Button(window, text='exit', command=window.destroy).pack(side="bottom")

    window.mainloop()

if __name__ == '__main__':
    # ask_month()
    window()