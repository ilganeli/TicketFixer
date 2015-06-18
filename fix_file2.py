import pandas as pd
import sys

def pivotSeats(info_to_pivot):
    common_keys = ['Name','Address','Package Name','Venue 1','Event Name 1','Date 1','Number of Seats','Subscription Total']
    grouped = info_to_pivot.groupby(common_keys)
    ordered_keys = common_keys[0:len(common_keys)-2]
    list_of_dicts = list()
    max_seats = 0

    ## First, group all seats per venue
    for item in grouped:
        vals = item[0]
        df = item[1]
        local_dict = dict()

        for key,val in zip(common_keys, vals):
            local_dict[key] = val

        if max_seats < len(df):
            max_seats = len(df)

        for row in enumerate(df.iterrows()):
            count = str(row[0]+1)
            local_dict['Seat ' + count] = str(row[1][1]['Section 1']) + \
                                          "," + str(row[1][1]['Row 1']) + \
                                          "," + str(row[1][1]['Seat 1']) + \
                                          "," + str(row[1][1]['Seat Price 1'])
        list_of_dicts.append(local_dict)
        #break

    for i in range(0, max_seats):
        ordered_keys.append('Seat ' + str(i+1))

    ordered_keys.append('Number of Seats')
    ordered_keys.append('Subscription Total')
    new_df = pd.DataFrame(list_of_dicts)
    new_df = new_df[ordered_keys]
    return new_df, max_seats

def pivot_venues(pivot_by_venue, seat_count):
    common_keys = ['Name','Address','Package Name','Number of Seats','Subscription Total']
    grouped = pivot_by_venue.groupby(common_keys)
    ordered_keys = common_keys[0:len(common_keys)-2]
    list_of_dicts = list()
    max_venues = 0

    ## Then, do all seats and venues
    for item in grouped:
        vals = item[0]
        df = item[1]
        local_dict = dict()

        for key,val in zip(common_keys, vals):
            local_dict[key] = val

        if max_venues < len(df):
            max_venues = len(df)

        for row in enumerate(df.iterrows()):
            count = str(row[0]+1)

            # Add all the seats back in per venue
            print row
            for i in range(0, seat_count):
                local_dict['Seat V' + count + "_" + str(i+1)] = row[1][1]['Seat ' + str(i+1)]

            local_dict['Venue V' + count] = row[1][1]['Venue 1']
            local_dict['Event Name V' + count] = row[1][1]['Event Name 1']
            local_dict['Date V' + count] = row[1][1]['Date 1']

        list_of_dicts.append(local_dict)

    # Define schema
    for i in range(0, max_venues):
        ordered_keys.append('Venue V' + str(i+1))
        ordered_keys.append('Event Name V' + str(i+1))
        ordered_keys.append('Date V' + str(i+1))

        for j in range(0, seat_count):
            ordered_keys.append('Seat V' + str(i+1) + "_" + str(j+1))

    ordered_keys.append('Number of Seats')
    ordered_keys.append('Subscription Total')
    new_df = pd.DataFrame(list_of_dicts)
    new_df = new_df[ordered_keys]
    return new_df

def parse_non_sf(file_name):
    ordering = [u'Name', u'Address', u'Package Name', u'Venue 1', u'Event Name 1', u'Date 1', u'Section 1', u'Row 1', u'Seat 1', u'Seat Price 1', u'Number of Seats', u'Subscription Total']
    f = pd.ExcelFile(file_name).parse('Sheet1')
    f = pd.DataFrame(f)
    #f = f.fillna(method="ffill")
    tickets = f[['Name', 'Section 1', 'Row 1', 'Seat 1', 'Seat Price 1']]
    tickets = tickets.fillna(method='ffill')
    tickets_unique = tickets.drop_duplicates()

    venues = f[['Name', 'Package Name', 'Venue 1', 'Event Name 1', 'Date 1']]
    venues = venues.fillna(method='ffill')

    person = f[['Name', 'Address', 'Number of Seats', 'Subscription Total']]
    person = person.fillna(method='ffill')
    merged = pd.merge(venues, tickets, left_on='Name',right_on='Name', how='outer').drop_duplicates()
    with_info = pd.merge(person, merged, left_on='Name', right_on='Name', how='outer').drop_duplicates()
    with_info = with_info[ordering]
    with_info = pd.DataFrame(with_info)
    return with_info

def parse_sf(file_name):
    f = pd.ExcelFile(file_name).parse('Sheet1')
    f = pd.DataFrame(f)
    f = f.fillna(method="ffill")
    return f

def pivot_and_output(with_info, out_name):
    with_seats,max_seats = pivotSeats(with_info)
    # Next, group all seats per Venue
    with_venues = pivot_venues(with_seats, max_seats)
    # selected = new_df[new_df['Name'] =='Lela DiGeronimo']
    # print selected

    #print new_df.keys()
    #print new_df
    new_df = pd.DataFrame(with_venues)
    new_df.to_csv(out_name)

desired_width = 640
pd.set_option('display.width', desired_width)

with_info_non_sf = parse_non_sf("non_sf_tickets.xlsx")
pivot_and_output(with_info_non_sf, "fixed_ticketing_non_sf.csv")

with_info_sf = parse_sf("sf_tickets.xlsx")
pivot_and_output(with_info_sf, "fixed_ticketing_sf.csv")