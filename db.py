<<<<<<< HEAD
import sqlite3
from flask import g
import datetime, calendar
import string
import random

import os
#DATABASE = 'dograntcounty.sqlite'
DATABASE = '/home/dograntcounty/mysite/dograntcounty.sqlite'

import dograntcounty


# Connect to the database.
def connect_db():
    db_path = os.path.join(dograntcounty.app.root_path, DATABASE)
    # if not os.path.isfile(db_path):
        # raise RuntimeError("Can't find database file '{}'".format(db_path))
    connection = sqlite3.connect(db_path)
    connection.row_factory = sqlite3.Row
    return connection


# Open a database connection and hang on to it in the global object.
def open_db_connection():
    g.db = connect_db()


# If the database is open, close it.
def close_db_connection():
    db = getattr(g, 'db', None)
    if db is not None:
        db.close()


# Convert the 'row' retrieved with 'cursor' to a dictionary
# whose keys are column names and whose values are column values.
def row_to_dictionary(cursor, row):
    dictionary = {}
    for idx, col in enumerate(cursor.description):
        dictionary[col[0]] = row[idx]
    return dictionary


######################################

months = {
    'jan': 1,
    'feb': 2,
    'mar': 3,
    'apr': 4,
    'may': 5,
    'jun': 6,
    'jul': 7,
    'aug': 8,
    'sep': 9,
    'oct': 10,
    'nov': 11,
    'dec': 12
}


def all_events():
    return g.db.execute('SELECT * FROM event').fetchall()


def event(id):
    return g.db.execute('SELECT * FROM event WHERE id = ?', (id,)).fetchone()


def event_password(password):
    return g.db.execute('SELECT * FROM event WHERE password = ?', (password,)).fetchone()


def events(year, month):
    from_month = months[month]
    to_year = int(year)
    to_month = int(from_month) + 1
    if to_month > 12:
        to_month = 1
        to_year = int(year) + 1
    from_date = datetime.datetime.strptime(str(year) + '/' + str(from_month) + '/1', '%Y/%m/%d').strftime('%Y-%m-%d')
    to_date = datetime.datetime.strptime(str(to_year) + '/' + str(to_month) + '/1', '%Y/%m/%d').strftime('%Y-%m-%d')

    return g.db.execute('SELECT * FROM event WHERE start_date BETWEEN ? AND ? AND verified = 1 ORDER BY start_date, start_time, end_date, end_time, title', (from_date,to_date,)).fetchall()


def events2(year, month):
    from_month = months[month]
    day = calendar.monthrange(int(year), int(from_month))[1]
    end_date_month = datetime.datetime.strptime(str(year) + '/' + str(from_month) + '/' + str(day), '%Y/%m/%d').strftime('%Y-%m-%d')
    start_date_month = datetime.datetime.strptime(str(year) + '/' + str(from_month) + '/1', '%Y/%m/%d').strftime('%Y-%m-%d')

    return g.db.execute('''SELECT * FROM event WHERE ((? BETWEEN start_date AND end_date)
                                                      OR (? BETWEEN start_date AND end_date)
                                                      OR (start_date BETWEEN ? AND ?))
                                                AND verified = 1
                           ORDER BY start_date, start_time, end_date, end_time, title''', (start_date_month,end_date_month,start_date_month,end_date_month)).fetchall()


def filter_events(events, category):
    new_events = []
    for e in events:
        if g.db.execute('SELECT * FROM event_category WHERE event_id = ? AND category_id = ?', (e['id'],category)).fetchone() is not None:
            new_events.append(e)
    return new_events


def daterange(start_date, end_date, now, repeat):
    #print(start_date, end_date, repeat)
    this_date = start_date
    dates = []
    if start_date.month == now.month:
        dates = [start_date.strftime('%Y-%m-%d')]
    #if start_date < start_month:
        #this_date = start_month
        #dates = [start_month.strftime('%Y-%m-%d')]
    until_date = end_date
    #if end_date > end_month:
        #until_date = end_month

    if repeat == 'weekday':
        # calculate th of the weekday
        temp = this_date
        weekday = this_date.strftime('%A')
        num_weeks = 0
        while temp.day > 1:
            if temp.strftime('%A') == weekday:
                num_weeks += 1
            temp = temp - datetime.timedelta(days=1)
        #print(num_weeks,weekday)
        while this_date < until_date:
            month = this_date.month + 1
            year = this_date.year
            if month > 12:
                month = 1
                year += 1
            this_date = datetime.date(year,month,1)
            #print(' ', this_date)
            # go to the first th weekday
            while this_date.strftime('%A') != weekday:
                this_date = this_date + datetime.timedelta(days=1)
            #print('  ', this_date)
            # go to the th of the weekday
            num = 1
            while num < num_weeks:
                this_date = this_date + datetime.timedelta(days=7)
                num += 1
            #print('   ', this_date)
            if this_date <= until_date and this_date.month == now.month and this_date.year == now.year:
                print(this_date.strftime('%Y-%m-%d'))
                dates.append(this_date.strftime('%Y-%m-%d'))
    else:
        while this_date < until_date:
            if repeat == 'month':
                month = this_date.month + 1
                year = this_date.year
                if month > 12:
                    month = 1
                    year += 1
                day = min(this_date.day, calendar.monthrange(year, month)[1])
                this_date = datetime.date(year, month, day)
                if this_date <= until_date and this_date.month == now.month and this_date.year == now.year:
                    dates.append(this_date.strftime('%Y-%m-%d'))
            else:
                this_date = this_date + datetime.timedelta(days=repeat)
                if this_date <= until_date and this_date.month == now.month and this_date.year == now.year:
                    dates.append(this_date.strftime('%Y-%m-%d'))
    #print(dates)
    return dates


def ar_events(events, year, month):
    event_dates = []

    end_m = months[month]
    end_d = calendar.monthrange(int(year), int(end_m))[1]
    end_month = datetime.date(int(year), int(end_m), int(end_d))

    for e in events:
        repeat = 1
        if e['repeated'] == 'weekly':
            repeat = 7
        elif e['repeated'] == 'monthly':
            repeat = 'month'
        elif e['repeated'] == 'weekday':
            repeat = 'weekday'
        for single_date in daterange(datetime.date(int(e['start_date'][:4]), int(e['start_date'][5:7]), int(e['start_date'][8:])),
                                     datetime.date(int(e['end_date'][:4]),int(e['end_date'][5:7]),int(e['end_date'][8:])),
                                     datetime.date(int(year),int(end_m),1),
                                     repeat):
            if single_date not in event_dates:
                #print(single_date)
                event_dates.append(single_date)

    event_dates = sorted(event_dates, key=lambda x: datetime.datetime.strptime(x, '%Y-%m-%d'))

    new_events = {}

    for n in range(len(events)):

        new_event = {}
        new_event['id'] = random_string(12)
        new_event['title'] = events[n]['title']
        new_event['organization'] = events[n]['organization']
        new_event['location'] = events[n]['location']
        new_event['description'] = events[n]['description']

        new_event['cost'] = events[n]['cost']

        new_event['contact_name'] = events[n]['contact_name']
        new_event['contact_email'] = events[n]['contact_email']
        new_event['contact_phone'] = events[n]['contact_phone']
        new_event['url'] = events[n]['url']
        new_event['password'] = events[n]['password']
        new_event['photo'] = events[n]['photo']

        start_hour = int(datetime.datetime.strptime(events[n]['start_time'], '%H:%M').strftime("%H"))
        start_minute = datetime.datetime.strptime(events[n]['start_time'], '%H:%M').strftime("%M")
        start_ampm = "AM"
        end_hour = int(datetime.datetime.strptime(events[n]['end_time'], '%H:%M').strftime("%H"))
        end_minute = datetime.datetime.strptime(events[n]['end_time'], '%H:%M').strftime("%M")
        end_ampm = "AM"

        if start_hour == 12:
            start_ampm = "PM"
        elif start_hour > 12:
            start_hour -= 12
            start_ampm = "PM"
        if end_hour == 12:
            end_ampm = "PM"
        elif end_hour > 12:
            end_hour -= 12
            end_ampm = "PM"

        new_event['start_time'] = str(start_hour) + ":" + start_minute + " " + start_ampm
        new_event['end_time'] = str(end_hour) + ":" + end_minute + " " + end_ampm

        start_month = datetime.datetime.strptime(events[n]['start_date'], '%Y-%m-%d').strftime("%B")
        start_day = int(datetime.datetime.strptime(events[n]['start_date'], '%Y-%m-%d').strftime("%d"))
        start_year = datetime.datetime.strptime(events[n]['start_date'], '%Y-%m-%d').strftime("%y")
        end_month = datetime.datetime.strptime(events[n]['end_date'], '%Y-%m-%d').strftime("%B")
        end_day = int(datetime.datetime.strptime(events[n]['end_date'], '%Y-%m-%d').strftime("%d"))
        end_year = datetime.datetime.strptime(events[n]['end_date'], '%Y-%m-%d').strftime("%y")

        new_event['start_date'] = start_month + " " + str(start_day)
        new_event['end_date'] = end_month + " " + str(end_day)

        repeat = 1
        if events[n]['repeated'] == 'weekly':
            repeat = 7
        elif events[n]['repeated'] == 'monthly':
            repeat = 'month'
        elif events[n]['repeated'] == 'weekday':
            repeat = 'weekday'
        for single_date in daterange(
                datetime.date(int(events[n]['start_date'][:4]), int(events[n]['start_date'][5:7]), int(events[n]['start_date'][8:])),
                datetime.date(int(events[n]['end_date'][:4]), int(events[n]['end_date'][5:7]), int(events[n]['end_date'][8:])),
                datetime.date(int(year), int(end_m), 1),
                repeat):
            num = event_dates.index(single_date)

            if num not in new_events.keys():
                new_events[num] = []

            new_events[num].append(new_event)
    return new_events, event_dates


def arrange_events(events):
    event_dates = []
    for e in events:
        if str(e['start_date']) not in event_dates:
            event_dates.append(str(e['start_date']))

    new_events = {}

    for n in range(len(events)):
        num = event_dates.index(str(events[n]['start_date']))

        if num not in new_events.keys():
            new_events[num] = []

        new_event = {}
        new_event['id'] = events[n]['id']
        new_event['title'] = events[n]['title']
        new_event['organization'] = events[n]['organization']
        new_event['location'] = events[n]['location']
        new_event['description'] = events[n]['description']
        new_event['repeated'] = events[n]['repeated']

        new_event['cost'] = events[n]['cost']

        new_event['contact_name'] = events[n]['contact_name']
        new_event['contact_email'] = events[n]['contact_email']
        new_event['contact_phone'] = events[n]['contact_phone']
        new_event['url'] = events[n]['url']
        new_event['password'] = events[n]['password']
        new_event['photo'] = events[n]['photo']

        start_hour = int(datetime.datetime.strptime(events[n]['start_time'], '%H:%M').strftime("%H"))
        start_minute = datetime.datetime.strptime(events[n]['start_time'], '%H:%M').strftime("%M")
        start_ampm = "AM"
        end_hour = int(datetime.datetime.strptime(events[n]['end_time'], '%H:%M').strftime("%H"))
        end_minute = datetime.datetime.strptime(events[n]['end_time'], '%H:%M').strftime("%M")
        end_ampm = "AM"

        if start_hour == 12:
            start_ampm = "PM"
        elif start_hour > 12:
            start_hour -= 12
            start_ampm = "PM"
        if end_hour == 12:
            end_ampm = "PM"
        elif end_hour > 12:
            end_hour -= 12
            end_ampm = "PM"

        new_event['start_time'] = str(start_hour) + ":" + start_minute + " " + start_ampm
        new_event['end_time'] = str(end_hour) + ":" + end_minute + " " + end_ampm

        start_month = datetime.datetime.strptime(events[n]['start_date'], '%Y-%m-%d').strftime("%B")
        start_day = int(datetime.datetime.strptime(events[n]['start_date'], '%Y-%m-%d').strftime("%d"))
        start_year = datetime.datetime.strptime(events[n]['start_date'], '%Y-%m-%d').strftime("%y")
        end_month = datetime.datetime.strptime(events[n]['end_date'], '%Y-%m-%d').strftime("%B")
        end_day = int(datetime.datetime.strptime(events[n]['end_date'], '%Y-%m-%d').strftime("%d"))
        end_year = datetime.datetime.strptime(events[n]['end_date'], '%Y-%m-%d').strftime("%y")

        new_event['start_date'] = start_month + " " + str(start_day)
        new_event['end_date'] = end_month + " " + str(end_day)

        new_events[num].append(new_event)
    return new_events, event_dates


def search_events(keyword):
    keyword = '%'+str(keyword)+'%'
    return g.db.execute('SELECT * FROM event WHERE title COLLATE UTF8_GENERAL_CI LIKE ? OR organization COLLATE UTF8_GENERAL_CI LIKE ? AND verified = 1 ORDER BY start_date, start_time, end_date, end_time, title', (keyword,keyword,)).fetchall()


def add_event(title, organization, description, start_date, start_time, end_date, end_time, repeated, location, categories, cost, contact_name, contact_email, contact_phone, url):

    event_id = random_string(12)
    password = random_string(8)

    add = '''
                 INSERT INTO event (id, title, organization, description, start_date, start_time, end_date, end_time, repeated, location, cost, contact_name, contact_email, contact_phone, url, password)
                 VALUES (:id, :title, :organization, :description, :start_date, :start_time, :end_date, :end_time, :repeated, :location, :cost, :contact_name, :contact_email, :contact_phone, :url, :password)
                 '''
    add_cursor = g.db.execute(add, {'id': event_id, 'title': title, 'organization': organization, 'description': description, 'start_date': start_date,
                                    'start_time': start_time, 'end_date': end_date, 'end_time': end_time, 'repeated': repeated, 'location': location, 'cost': cost,
                                    'contact_name': contact_name, 'contact_email': contact_email, 'contact_phone': contact_phone,
                                    'url': url, 'password': password})
    g.db.commit()
    if add_cursor.rowcount == 1:
        for category in categories:
            connect = '''
                            INSERT INTO event_category (event_id, category_id)
                            VALUES (:event_id, :category_id)
                            '''
            connect_cursor = g.db.execute(connect, {'event_id': event_id, 'category_id': category })
            g.db.commit()
            if connect_cursor.rowcount != 1:
                return 0
        return event_id, password
    return 0


def upload_photo(event,photo):
    update = 'UPDATE event SET photo = :photo WHERE id = :event_id'
    update_cursor = g.db.execute(update, {'photo': photo, 'event_id': event})
    g.db.commit()
    if update_cursor.rowcount == 1:
        return 1
    return 0


def event_categories(id):
    result = []
    categories = g.db.execute('SELECT * FROM event_category WHERE event_id = ?',(id,)).fetchall()
    for c in categories:
        result.append(c['category_id'])
    return result


def category(id):
    return g.db.execute('SELECT * FROM category WHERE id = ?',(id,)).fetchone()


def categories():
    return g.db.execute('SELECT * FROM category ORDER BY title').fetchall()


def admin_arrange_categories(categories):
    new_categories = []
    for c in categories:
        new_category = {}
        new_category['id'] = c['id']
        new_category['title'] = c['title']
        new_category['date'] = datetime.datetime.strptime(c['created_at'], '%Y-%m-%d %H:%M:%S').strftime('%B') +\
                               " " + str(int(datetime.datetime.strptime(c['created_at'], '%Y-%m-%d %H:%M:%S').strftime('%d'))) + \
                               ", " + datetime.datetime.strptime(c['created_at'], '%Y-%m-%d %H:%M:%S').strftime('%Y')
        new_category['events'] = len(category_events(c['id']))
        new_categories.append(new_category)
    return new_categories


def category_events(id):
    return g.db.execute('SELECT * FROM event_category WHERE category_id = ?',(id,)).fetchall()


def random_string(n):
    return ''.join(random.choice(string.ascii_lowercase + string.digits) for _ in range(n))


def random_integer(n):
    return ''.join(random.choice(string.digits) for _ in range(n))


def question(id):
    return g.db.execute('SELECT * FROM faq WHERE id = ?',(id,)).fetchone()


def questions():
    return g.db.execute('SELECT * FROM faq').fetchall()


def arrange_questions(questions):
    new_questions = []
    for q in questions:
        new_question = {}
        new_question['id'] = q['id']
        new_question['question'] = q['question']
        new_question['answer'] = q['answer']
        new_question['date'] = datetime.datetime.strptime(q['created_at'], '%Y-%m-%d %H:%M:%S').strftime('%B') +\
                               " " + str(int(datetime.datetime.strptime(q['created_at'], '%Y-%m-%d %H:%M:%S').strftime('%d'))) + \
                               ", " + datetime.datetime.strptime(q['created_at'], '%Y-%m-%d %H:%M:%S').strftime('%Y')
        new_questions.append(new_question)
    return new_questions


def setting():
    return g.db.execute('SELECT * FROM setting WHERE id = ?',('dograntcounty',)).fetchone()


def admin_events(year):
    to_year = int(year)+1
    from_date = datetime.datetime.strptime(str(year) + '/1/1', '%Y/%m/%d').strftime(
        '%Y-%m-%d')
    to_date = datetime.datetime.strptime(str(to_year) + '/1/1', '%Y/%m/%d').strftime('%Y-%m-%d')

    return g.db.execute('SELECT * FROM event WHERE start_date BETWEEN ? AND ? AND verified = 1 ORDER BY start_date, start_time, end_date, end_time, title',(from_date, to_date,)).fetchall()


def admin_filter_events(events, category):
    new_events = []
    for e in events:
        if g.db.execute('SELECT * FROM event_category WHERE event_id = ? AND category_id = ?', (e['id'],category)).fetchone() is not None:
            new_events.append(e)
    return new_events


def admin_search_events(keyword):
    keyword = '%' + str(keyword) + '%'
    return g.db.execute('SELECT * FROM event WHERE title COLLATE UTF8_GENERAL_CI LIKE ? OR organization COLLATE UTF8_GENERAL_CI LIKE ? AND verified = 1 ORDER BY start_date, start_time, end_date, end_time, title',(keyword,keyword,)).fetchall()


def admin_arrange_events(events):
    event_dates = {}

    for e in events:
        if int(datetime.datetime.strptime(e['start_date'], '%Y-%m-%d').strftime("%m")) not in event_dates.keys():
            event_dates[int(datetime.datetime.strptime(e['start_date'], '%Y-%m-%d').strftime("%m"))] = []

    for e in events:
        if str(e['start_date']) not in event_dates[int(datetime.datetime.strptime(e['start_date'], '%Y-%m-%d').strftime("%m"))]:
            event_dates[int(datetime.datetime.strptime(e['start_date'], '%Y-%m-%d').strftime("%m"))].append(str(e['start_date']))

    new_events = {}

    for n in range(len(events)):
        month = int(datetime.datetime.strptime(events[n]['start_date'], '%Y-%m-%d').strftime("%m"))
        num = event_dates[month].index(str(events[n]['start_date']))

        if month not in new_events.keys():
            new_events[month] = {}

        if num not in new_events[month].keys():
            new_events[month][num] = []

        new_event = {}
        new_event['id'] = events[n]['id']
        new_event['title'] = events[n]['title']
        new_event['organization'] = events[n]['organization']
        new_event['location'] = events[n]['location']
        new_event['description'] = events[n]['description']
        new_event['repeated'] = events[n]['repeated']

        new_event['cost'] = events[n]['cost']

        new_event['contact_name'] = events[n]['contact_name']
        new_event['contact_email'] = events[n]['contact_email']
        new_event['contact_phone'] = events[n]['contact_phone']
        new_event['url'] = events[n]['url']
        new_event['password'] = events[n]['password']
        new_event['photo'] = events[n]['photo']

        start_hour = int(datetime.datetime.strptime(events[n]['start_time'], '%H:%M').strftime("%H"))
        start_minute = datetime.datetime.strptime(events[n]['start_time'], '%H:%M').strftime("%M")
        start_ampm = "AM"
        end_hour = int(datetime.datetime.strptime(events[n]['end_time'], '%H:%M').strftime("%H"))
        end_minute = datetime.datetime.strptime(events[n]['end_time'], '%H:%M').strftime("%M")
        end_ampm = "AM"

        if start_hour == 12:
            start_ampm = "PM"
        elif start_hour > 12:
            start_hour -= 12
            start_ampm = "PM"
        if end_hour == 12:
            end_ampm = "PM"
        elif end_hour > 12:
            end_hour -= 12
            end_ampm = "PM"

        new_event['start_time'] = str(start_hour) + ":" + start_minute + " " + start_ampm
        new_event['end_time'] = str(end_hour) + ":" + end_minute + " " + end_ampm

        start_month = datetime.datetime.strptime(events[n]['start_date'], '%Y-%m-%d').strftime("%B")
        start_day = int(datetime.datetime.strptime(events[n]['start_date'], '%Y-%m-%d').strftime("%d"))
        start_year = datetime.datetime.strptime(events[n]['start_date'], '%Y-%m-%d').strftime("%Y")
        end_month = datetime.datetime.strptime(events[n]['end_date'], '%Y-%m-%d').strftime("%B")
        end_day = int(datetime.datetime.strptime(events[n]['end_date'], '%Y-%m-%d').strftime("%d"))
        end_year = datetime.datetime.strptime(events[n]['end_date'], '%Y-%m-%d').strftime("%Y")

        new_event['start_date'] = start_month + " " + str(start_day) + ", " + str(start_year)
        new_event['end_date'] = end_month + " " + str(end_day) + ", " + str(end_year)

        new_events[month][num].append(new_event)
    return new_events, event_dates


def admin_edited_events():
    return g.db.execute('SELECT * FROM edit_event ORDER BY created_at').fetchall()


def admin_pendings():
    return g.db.execute('SELECT * FROM event WHERE verified = 0 ORDER BY created_at').fetchall()


def admin_arrange_pendings(pendings):

    new_pendings = []

    for p in pendings:

        new_pending = {}
        new_pending['id'] = p['id']
        new_pending['title'] = p['title']
        new_pending['organization'] = p['organization']
        new_pending['location'] = p['location']
        new_pending['description'] = p['description']
        new_pending['repeated'] = p['repeated']

        new_pending['cost'] = p['cost']

        new_pending['contact_name'] = p['contact_name']
        new_pending['contact_email'] = p['contact_email']
        new_pending['contact_phone'] = p['contact_phone']
        new_pending['url'] = p['url']
        new_pending['password'] = p['password']
        new_pending['photo'] = p['photo']

        start_hour = int(datetime.datetime.strptime(p['start_time'], '%H:%M').strftime("%H"))
        start_minute = datetime.datetime.strptime(p['start_time'], '%H:%M').strftime("%M")
        start_ampm = "AM"
        end_hour = int(datetime.datetime.strptime(p['end_time'], '%H:%M').strftime("%H"))
        end_minute = datetime.datetime.strptime(p['end_time'], '%H:%M').strftime("%M")
        end_ampm = "AM"

        if start_hour == 12:
            start_ampm = "PM"
        elif start_hour > 12:
            start_hour -= 12
            start_ampm = "PM"
        if end_hour == 12:
            end_ampm = "PM"
        elif end_hour > 12:
            end_hour -= 12
            end_ampm = "PM"

        new_pending['start_time'] = str(start_hour) + ":" + start_minute + " " + start_ampm
        new_pending['end_time'] = str(end_hour) + ":" + end_minute + " " + end_ampm

        start_month = datetime.datetime.strptime(p['start_date'], '%Y-%m-%d').strftime("%B")
        start_day = int(datetime.datetime.strptime(p['start_date'], '%Y-%m-%d').strftime("%d"))
        start_year = datetime.datetime.strptime(p['start_date'], '%Y-%m-%d').strftime("%y")
        end_month = datetime.datetime.strptime(p['end_date'], '%Y-%m-%d').strftime("%B")
        end_day = int(datetime.datetime.strptime(p['end_date'], '%Y-%m-%d').strftime("%d"))
        end_year = datetime.datetime.strptime(p['end_date'], '%Y-%m-%d').strftime("%y")

        new_pending['start_date'] = start_month + " " + str(start_day) + ", " + str(start_year)
        new_pending['end_date'] = end_month + " " + str(end_day)+ ", " + str(end_year)

        new_pendings.append(new_pending)
    return new_pendings


def admin_arrange_edited_events(events):

    new_events = []

    for p in events:

        new_pending = {}
        new_pending['id'] = p['id']
        new_pending['title'] = p['title']
        new_pending['organization'] = p['organization']
        new_pending['location'] = p['location']
        new_pending['description'] = p['description']
        new_pending['repeated'] = p['repeated']

        new_pending['cost'] = p['cost']

        new_pending['contact_name'] = p['contact_name']
        new_pending['contact_email'] = p['contact_email']
        new_pending['contact_phone'] = p['contact_phone']
        new_pending['url'] = p['url']
        new_pending['photo'] = p['photo']

        start_hour = int(datetime.datetime.strptime(p['start_time'], '%H:%M').strftime("%H"))
        start_minute = datetime.datetime.strptime(p['start_time'], '%H:%M').strftime("%M")
        start_ampm = "AM"
        end_hour = int(datetime.datetime.strptime(p['end_time'], '%H:%M').strftime("%H"))
        end_minute = datetime.datetime.strptime(p['end_time'], '%H:%M').strftime("%M")
        end_ampm = "AM"

        if start_hour == 12:
            start_ampm = "PM"
        elif start_hour > 12:
            start_hour -= 12
            start_ampm = "PM"
        if end_hour == 12:
            end_ampm = "PM"
        elif end_hour > 12:
            end_hour -= 12
            end_ampm = "PM"

        new_pending['start_time'] = str(start_hour) + ":" + start_minute + " " + start_ampm
        new_pending['end_time'] = str(end_hour) + ":" + end_minute + " " + end_ampm

        start_month = datetime.datetime.strptime(p['start_date'], '%Y-%m-%d').strftime("%B")
        start_day = int(datetime.datetime.strptime(p['start_date'], '%Y-%m-%d').strftime("%d"))
        start_year = datetime.datetime.strptime(p['start_date'], '%Y-%m-%d').strftime("%y")
        end_month = datetime.datetime.strptime(p['end_date'], '%Y-%m-%d').strftime("%B")
        end_day = int(datetime.datetime.strptime(p['end_date'], '%Y-%m-%d').strftime("%d"))
        end_year = datetime.datetime.strptime(p['end_date'], '%Y-%m-%d').strftime("%y")

        new_pending['start_date'] = start_month + " " + str(start_day)
        new_pending['end_date'] = end_month + " " + str(end_day)

        new_events.append(new_pending)
    return new_events


def admin_accept_event(id):
    update = 'UPDATE event SET verified = :verified WHERE id = :event_id'
    update_cursor = g.db.execute(update, {'verified': 1, 'event_id': id})
    g.db.commit()
    if update_cursor.rowcount == 1:
        return 1
    return 0


def admin_delete_event(id):
    category = 'DELETE FROM event_category WHERE event_id = :event_id'
    category_cursor = g.db.execute(category, {'event_id': id})
    g.db.commit()
    edit = 'DELETE FROM edit_event WHERE event_id = :event_id'
    edit_cursor = g.db.execute(edit, {'event_id': id})
    g.db.commit()
    event = 'DELETE FROM event WHERE id = :event_id'
    event_cursor = g.db.execute(event, {'event_id': id})
    g.db.commit()
    if event_cursor.rowcount == 1:
        return 1
    return 0


def admin_edit(id):
    return g.db.execute('SELECT * FROM edit_event WHERE id = ?', (id,)).fetchone()


def admin_accept_edit(id):
    edit = g.db.execute('SELECT * FROM edit_event WHERE id = ?', (id,)).fetchone()
    update = '''
                     UPDATE event SET title = :title, organization = :organization, description = :description,
                      start_date = :start_date, start_time = :start_time, end_date = :end_date, end_time = :end_time, location = :location,
                      cost = :cost, contact_name = :contact_name, contact_email = :contact_email, contact_phone = :contact_phone,
                      url = :url, photo = :photo WHERE id = :event_id
                     '''
    update_cursor = g.db.execute(update, {'event_id': edit['event_id'], 'title': edit['title'], 'organization': edit['organization'],
                                      'description': edit['description'], 'start_date': edit['start_date'],
                                      'start_time': edit['start_time'], 'end_date': edit['end_date'], 'end_time': edit['end_time'],
                                      'location': edit['location'], 'cost': edit['cost'],
                                      'contact_name': edit['contact_name'], 'contact_email': edit['contact_email'],
                                      'contact_phone': edit['contact_phone'],
                                      'url': edit['url'], 'photo': edit['photo']})
    g.db.commit()
    if update_cursor.rowcount == 1:
        event = 'DELETE FROM edit_event WHERE id = :event_id'
        edit_cursor = g.db.execute(event, {'event_id': id})
        g.db.commit()
        if edit_cursor.rowcount == 1:
            return 1
        return 0
    return 0


def admin_delete_edit(id):
    edit = 'DELETE FROM edit_event WHERE id = :event_id'
    edit_cursor = g.db.execute(edit, {'event_id': id})
    g.db.commit()
    if edit_cursor.rowcount == 1:
        return 1
    return 0


def admin_edit_event(id,title, organization, description, start_date, start_time, end_date, end_time, repeated, location, categories, cost, contact_name, contact_email, contact_phone, url):

    edit = '''
                 UPDATE event SET title = :title, organization = :organization, description = :description,
                  start_date = :start_date, start_time = :start_time, end_date = :end_date, end_time = :end_time, repeated = :repeated, location = :location,
                  cost = :cost, contact_name = :contact_name, contact_email = :contact_email, contact_phone = :contact_phone,
                  url = :url WHERE id = :event_id
                 '''
    edit_cursor = g.db.execute(edit, {'event_id': id, 'title': title, 'organization': organization, 'description': description, 'start_date': start_date,
                                    'start_time': start_time, 'end_date': end_date, 'end_time': end_time, 'repeated': repeated, 'location': location, 'cost': cost,
                                    'contact_name': contact_name, 'contact_email': contact_email, 'contact_phone': contact_phone,
                                    'url': url})
    g.db.commit()
    if edit_cursor.rowcount == 1:
        category = 'DELETE FROM event_category WHERE event_id = :event_id'
        category_cursor = g.db.execute(category, {'event_id': id})
        g.db.commit()
        for category in categories:
            connect = '''
                            INSERT INTO event_category (event_id, category_id)
                            VALUES (:event_id, :category_id)
                            '''
            connect_cursor = g.db.execute(connect, {'event_id': id, 'category_id': category})
            g.db.commit()
            if connect_cursor.rowcount != 1:
                return 0
        return 1
    return 0


def edit_event(event_id, title, organization, description, start_date, start_time, end_date, end_time, repeated, location, categories, cost, contact_name, contact_email, contact_phone, url, photo):

    id = random_string(12)

    edit = '''
                     INSERT INTO edit_event (id, event_id, title, organization, description, start_date, start_time, end_date, end_time, repeated, location, cost, contact_name, contact_email, contact_phone, url, photo)
                           VALUES (:id, :event_id, :title, :organization, :description, :start_date, :start_time, :end_date, :end_time, :repeated, :location, :cost, :contact_name, :contact_email, :contact_phone, :url, :photo)
                     '''
    edit_cursor = g.db.execute(edit, {'id': id, 'event_id': event_id, 'title': title, 'organization': organization,
                                      'description': description, 'start_date': start_date,
                                      'start_time': start_time, 'end_date': end_date, 'end_time': end_time,
                                      'repeated': repeated,
                                      'location': location, 'cost': cost,
                                      'contact_name': contact_name, 'contact_email': contact_email,
                                      'contact_phone': contact_phone,
                                      'url': url, 'photo': photo})
    g.db.commit()
    if edit_cursor.rowcount == 1:
        category = 'DELETE FROM event_category WHERE event_id = :event_id'
        category_cursor = g.db.execute(category, {'event_id': event_id})
        g.db.commit()
        for category in categories:
            connect = '''
                            INSERT INTO event_category (event_id, category_id)
                            VALUES (:event_id, :category_id)
                            '''
            connect_cursor = g.db.execute(connect, {'event_id': event_id, 'category_id': category})
            g.db.commit()
            if connect_cursor.rowcount != 1:
                return 0
        return 1
    return 0


def admin_add_category(title):

    category_id = random_string(12)

    add = '''
                 INSERT INTO category (id, title)
                 VALUES (:id, :title)
                 '''
    add_cursor = g.db.execute(add, {'id': category_id, 'title': title })
    g.db.commit()
    if add_cursor.rowcount == 1:
        return 1
    return 0


def admin_edit_category(id, title):

    today = datetime.datetime.today().strftime('%Y-%m-%d %H:%M:%S')

    edit = '''
                 UPDATE category SET title = :title, created_at = :today WHERE id = :category_id
                 '''
    edit_cursor = g.db.execute(edit, {'category_id': id, 'title': title, 'today': today})
    g.db.commit()
    if edit_cursor.rowcount == 1:
        return 1
    return 0


def admin_delete_category(id):
    category = 'DELETE FROM event_category WHERE category_id = :category_id'
    category_cursor = g.db.execute(category, {'category_id': id})
    g.db.commit()
    delete = 'DELETE FROM category WHERE id = :category_id'
    delete_cursor = g.db.execute(delete, {'category_id': id})
    g.db.commit()
    if delete_cursor.rowcount == 1:
        return 1
    return 0


def admin_edit_question(id, question, answer):

    today = datetime.datetime.today().strftime('%Y-%m-%d %H:%M:%S')

    edit = '''
                 UPDATE faq SET question = :question, answer = :answer, created_at = :today WHERE id = :question_id
                 '''
    edit_cursor = g.db.execute(edit, {'question_id': id, 'question': question, 'answer': answer, 'today': today})
    g.db.commit()
    if edit_cursor.rowcount == 1:
        return 1
    return 0


def admin_delete_question(id):
    question = 'DELETE FROM faq WHERE id = :question_id'
    question_cursor = g.db.execute(question, {'question_id': id})
    g.db.commit()
    if question_cursor.rowcount == 1:
        return 1
    return 0


def admin_add_question(question, answer):

    question_id = random_string(12)

    add = '''
                 INSERT INTO faq (id, question, answer)
                 VALUES (:id, :question, :answer)
                 '''
    add_cursor = g.db.execute(add, {'id': question_id, 'question': question, 'answer': answer})
    g.db.commit()
    if add_cursor.rowcount == 1:
        return 1
    return 0


def admin_update_about(title, content):
    today = datetime.datetime.today().strftime('%Y-%m-%d %H:%M:%S')
    edit = '''
                 UPDATE setting SET about_title = :title, about_content = :content, created_at = :today WHERE id = :id
                 '''
    edit_cursor = g.db.execute(edit, {'id': 'dograntcounty', 'title': title, 'content': content, 'today': today})
    g.db.commit()
    if edit_cursor.rowcount == 1:
        return 1
    return 0


def admin_update_faq(title, content):
    today = datetime.datetime.today().strftime('%Y-%m-%d %H:%M:%S')
    edit = '''
                 UPDATE setting SET faq_title = :title, faq_content = :content, created_at = :today WHERE id = :id
                 '''
    edit_cursor = g.db.execute(edit, {'id': 'dograntcounty', 'title': title, 'content': content, 'today': today})
    g.db.commit()
    if edit_cursor.rowcount == 1:
        return 1
    return 0


def admin_update_contact(title, content, email, phone):
    today = datetime.datetime.today().strftime('%Y-%m-%d %H:%M:%S')
    edit = '''
                 UPDATE setting SET contact_title = :title, contact_content = :content, contact_email = :email, contact_phone = :phone, created_at = :today WHERE id = :id
                 '''
    edit_cursor = g.db.execute(edit, {'id': 'dograntcounty', 'title': title, 'content': content, 'email': email, 'phone': phone, 'today': today})
    g.db.commit()
    if edit_cursor.rowcount == 1:
        return 1
    return 0


def admin_add_event(title, organization, description, start_date, start_time, end_date, end_time, repeated, location, categories, cost, contact_name, contact_email, contact_phone, url):

    event_id = random_string(12)
    password = random_string(8)

    add = '''
                 INSERT INTO event (id, title, organization, description, start_date, start_time, end_date, end_time, repeated, location, cost, contact_name, contact_email, contact_phone, url, password, verified)
                 VALUES (:id, :title, :organization, :description, :start_date, :start_time, :end_date, :end_time, :repeated, :location, :cost, :contact_name, :contact_email, :contact_phone, :url, :password, :verified)
                 '''
    add_cursor = g.db.execute(add, {'id': event_id, 'title': title, 'organization': organization, 'description': description, 'start_date': start_date,
                                    'start_time': start_time, 'end_date': end_date, 'end_time': end_time, 'repeated': repeated, 'location': location, 'cost': cost,
                                    'contact_name': contact_name, 'contact_email': contact_email, 'contact_phone': contact_phone,
                                    'url': url, 'password': password, 'verified': 1})
    g.db.commit()
    if add_cursor.rowcount == 1:
        for category in categories:
            connect = '''
                            INSERT INTO event_category (event_id, category_id)
                            VALUES (:event_id, :category_id)
                            '''
            connect_cursor = g.db.execute(connect, {'event_id': event_id, 'category_id': category })
            g.db.commit()
            if connect_cursor.rowcount != 1:
                return 0
        return event_id, password
    return 0


def event_id(password):
    e = g.db.execute('SELECT * FROM event WHERE password = ?', (password,)).fetchone()
=======
import sqlite3
from flask import g
import datetime, calendar
import string
import random

import os
#DATABASE = 'dograntcounty.sqlite'
DATABASE = '/var/www/dograntcounty/dograntcounty.sqlite'

import dograntcounty


# Connect to the database.
def connect_db():
    db_path = os.path.join(dograntcounty.app.root_path, DATABASE)
    # if not os.path.isfile(db_path):
        # raise RuntimeError("Can't find database file '{}'".format(db_path))
    connection = sqlite3.connect(db_path)
    connection.row_factory = sqlite3.Row
    return connection


# Open a database connection and hang on to it in the global object.
def open_db_connection():
    g.db = connect_db()


# If the database is open, close it.
def close_db_connection():
    db = getattr(g, 'db', None)
    if db is not None:
        db.close()


# Convert the 'row' retrieved with 'cursor' to a dictionary
# whose keys are column names and whose values are column values.
def row_to_dictionary(cursor, row):
    dictionary = {}
    for idx, col in enumerate(cursor.description):
        dictionary[col[0]] = row[idx]
    return dictionary


######################################

months = {
    'jan': 1,
    'feb': 2,
    'mar': 3,
    'apr': 4,
    'may': 5,
    'jun': 6,
    'jul': 7,
    'aug': 8,
    'sep': 9,
    'oct': 10,
    'nov': 11,
    'dec': 12
}


def all_events():
    return g.db.execute('SELECT * FROM event').fetchall()


def event(id):
    return g.db.execute('SELECT * FROM event WHERE id = ?', (id,)).fetchone()


def event_password(password):
    return g.db.execute('SELECT * FROM event WHERE password = ?', (password,)).fetchone()


def events(year, month):
    from_month = months[month]
    to_year = int(year)
    to_month = int(from_month) + 1
    if to_month > 12:
        to_month = 1
        to_year = int(year) + 1
    from_date = datetime.datetime.strptime(str(year) + '/' + str(from_month) + '/1', '%Y/%m/%d').strftime('%Y-%m-%d')
    to_date = datetime.datetime.strptime(str(to_year) + '/' + str(to_month) + '/1', '%Y/%m/%d').strftime('%Y-%m-%d')

    return g.db.execute('SELECT * FROM event WHERE start_date BETWEEN ? AND ? AND verified = 1 ORDER BY start_date, start_time, end_date, end_time, title', (from_date,to_date,)).fetchall()


def events2(year, month):
    from_month = months[month]
    day = calendar.monthrange(int(year), int(from_month))[1]
    end_date_month = datetime.datetime.strptime(str(year) + '/' + str(from_month) + '/' + str(day), '%Y/%m/%d').strftime('%Y-%m-%d')
    start_date_month = datetime.datetime.strptime(str(year) + '/' + str(from_month) + '/1', '%Y/%m/%d').strftime('%Y-%m-%d')

    return g.db.execute('''SELECT * FROM event WHERE ((? BETWEEN start_date AND end_date) 
                                                      OR (? BETWEEN start_date AND end_date) 
                                                      OR (start_date BETWEEN ? AND ?)) 
                                                AND verified = 1 
                           ORDER BY start_date, start_time, end_date, end_time, title''', (start_date_month,end_date_month,start_date_month,end_date_month)).fetchall()


def filter_events(events, category):
    new_events = []
    for e in events:
        if g.db.execute('SELECT * FROM event_category WHERE event_id = ? AND category_id = ?', (e['id'],category)).fetchone() is not None:
            new_events.append(e)
    return new_events


def daterange(start_date, end_date, now, repeat):
    #print(start_date, end_date, repeat)
    this_date = start_date
    dates = []
    if start_date.month == now.month:
        dates = [start_date.strftime('%Y-%m-%d')]
    #if start_date < start_month:
        #this_date = start_month
        #dates = [start_month.strftime('%Y-%m-%d')]
    until_date = end_date
    #if end_date > end_month:
        #until_date = end_month

    if repeat == 'weekday':
        # calculate th of the weekday
        temp = this_date
        weekday = this_date.strftime('%A')
        num_weeks = 0
        while temp.day > 1:
            if temp.strftime('%A') == weekday:
                num_weeks += 1
            temp = temp - datetime.timedelta(days=1)
        #print(num_weeks,weekday)
        while this_date < until_date:
            month = this_date.month + 1
            year = this_date.year
            if month > 12:
                month = 1
                year += 1
            this_date = datetime.date(year,month,1)
            #print(' ', this_date)
            # go to the first th weekday
            while this_date.strftime('%A') != weekday:
                this_date = this_date + datetime.timedelta(days=1)
            #print('  ', this_date)
            # go to the th of the weekday
            num = 1
            while num < num_weeks:
                this_date = this_date + datetime.timedelta(days=7)
                num += 1
            #print('   ', this_date)
            if this_date <= until_date and this_date.month == now.month and this_date.year == now.year:
                print(this_date.strftime('%Y-%m-%d'))
                dates.append(this_date.strftime('%Y-%m-%d'))
    else:
        while this_date < until_date:
            if repeat == 'month':
                month = this_date.month + 1
                year = this_date.year
                if month > 12:
                    month = 1
                    year += 1
                day = min(this_date.day, calendar.monthrange(year, month)[1])
                this_date = datetime.date(year, month, day)
                if this_date <= until_date and this_date.month == now.month and this_date.year == now.year:
                    dates.append(this_date.strftime('%Y-%m-%d'))
            else:
                this_date = this_date + datetime.timedelta(days=repeat)
                if this_date <= until_date and this_date.month == now.month and this_date.year == now.year:
                    dates.append(this_date.strftime('%Y-%m-%d'))
    #print(dates)
    return dates


def ar_events(events, year, month):
    event_dates = []

    end_m = months[month]
    end_d = calendar.monthrange(int(year), int(end_m))[1]
    end_month = datetime.date(int(year), int(end_m), int(end_d))

    for e in events:
        repeat = 1
        if e['repeated'] == 'weekly':
            repeat = 7
        elif e['repeated'] == 'monthly':
            repeat = 'month'
        elif e['repeated'] == 'weekday':
            repeat = 'weekday'
        for single_date in daterange(datetime.date(int(e['start_date'][:4]), int(e['start_date'][5:7]), int(e['start_date'][8:])),
                                     datetime.date(int(e['end_date'][:4]),int(e['end_date'][5:7]),int(e['end_date'][8:])),
                                     datetime.date(int(year),int(end_m),1),
                                     repeat):
            if single_date not in event_dates:
                #print(single_date)
                event_dates.append(single_date)

    event_dates = sorted(event_dates, key=lambda x: datetime.datetime.strptime(x, '%Y-%m-%d'))

    new_events = {}

    for n in range(len(events)):

        new_event = {}
        new_event['id'] = random_string(12)
        new_event['title'] = events[n]['title']
        new_event['organization'] = events[n]['organization']
        new_event['location'] = events[n]['location']
        new_event['description'] = events[n]['description']

        new_event['cost'] = events[n]['cost']

        new_event['contact_name'] = events[n]['contact_name']
        new_event['contact_email'] = events[n]['contact_email']
        new_event['contact_phone'] = events[n]['contact_phone']
        new_event['url'] = events[n]['url']
        new_event['password'] = events[n]['password']
        new_event['photo'] = events[n]['photo']

        start_hour = int(datetime.datetime.strptime(events[n]['start_time'], '%H:%M').strftime("%H"))
        start_minute = datetime.datetime.strptime(events[n]['start_time'], '%H:%M').strftime("%M")
        start_ampm = "AM"
        end_hour = int(datetime.datetime.strptime(events[n]['end_time'], '%H:%M').strftime("%H"))
        end_minute = datetime.datetime.strptime(events[n]['end_time'], '%H:%M').strftime("%M")
        end_ampm = "AM"

        if start_hour == 12:
            start_ampm = "PM"
        elif start_hour > 12:
            start_hour -= 12
            start_ampm = "PM"
        if end_hour == 12:
            end_ampm = "PM"
        elif end_hour > 12:
            end_hour -= 12
            end_ampm = "PM"

        new_event['start_time'] = str(start_hour) + ":" + start_minute + " " + start_ampm
        new_event['end_time'] = str(end_hour) + ":" + end_minute + " " + end_ampm

        start_month = datetime.datetime.strptime(events[n]['start_date'], '%Y-%m-%d').strftime("%B")
        start_day = int(datetime.datetime.strptime(events[n]['start_date'], '%Y-%m-%d').strftime("%d"))
        start_year = datetime.datetime.strptime(events[n]['start_date'], '%Y-%m-%d').strftime("%y")
        end_month = datetime.datetime.strptime(events[n]['end_date'], '%Y-%m-%d').strftime("%B")
        end_day = int(datetime.datetime.strptime(events[n]['end_date'], '%Y-%m-%d').strftime("%d"))
        end_year = datetime.datetime.strptime(events[n]['end_date'], '%Y-%m-%d').strftime("%y")

        new_event['start_date'] = start_month + " " + str(start_day)
        new_event['end_date'] = end_month + " " + str(end_day)

        repeat = 1
        if events[n]['repeated'] == 'weekly':
            repeat = 7
        elif events[n]['repeated'] == 'monthly':
            repeat = 'month'
        elif events[n]['repeated'] == 'weekday':
            repeat = 'weekday'
        for single_date in daterange(
                datetime.date(int(events[n]['start_date'][:4]), int(events[n]['start_date'][5:7]), int(events[n]['start_date'][8:])),
                datetime.date(int(events[n]['end_date'][:4]), int(events[n]['end_date'][5:7]), int(events[n]['end_date'][8:])),
                datetime.date(int(year), int(end_m), 1),
                repeat):
            num = event_dates.index(single_date)

            if num not in new_events.keys():
                new_events[num] = []

            new_events[num].append(new_event)
    return new_events, event_dates


def arrange_events(events):
    event_dates = []
    for e in events:
        if str(e['start_date']) not in event_dates:
            event_dates.append(str(e['start_date']))

    new_events = {}

    for n in range(len(events)):
        num = event_dates.index(str(events[n]['start_date']))

        if num not in new_events.keys():
            new_events[num] = []

        new_event = {}
        new_event['id'] = events[n]['id']
        new_event['title'] = events[n]['title']
        new_event['organization'] = events[n]['organization']
        new_event['location'] = events[n]['location']
        new_event['description'] = events[n]['description']
        new_event['repeated'] = events[n]['repeated']

        new_event['cost'] = events[n]['cost']

        new_event['contact_name'] = events[n]['contact_name']
        new_event['contact_email'] = events[n]['contact_email']
        new_event['contact_phone'] = events[n]['contact_phone']
        new_event['url'] = events[n]['url']
        new_event['password'] = events[n]['password']
        new_event['photo'] = events[n]['photo']

        start_hour = int(datetime.datetime.strptime(events[n]['start_time'], '%H:%M').strftime("%H"))
        start_minute = datetime.datetime.strptime(events[n]['start_time'], '%H:%M').strftime("%M")
        start_ampm = "AM"
        end_hour = int(datetime.datetime.strptime(events[n]['end_time'], '%H:%M').strftime("%H"))
        end_minute = datetime.datetime.strptime(events[n]['end_time'], '%H:%M').strftime("%M")
        end_ampm = "AM"

        if start_hour == 12:
            start_ampm = "PM"
        elif start_hour > 12:
            start_hour -= 12
            start_ampm = "PM"
        if end_hour == 12:
            end_ampm = "PM"
        elif end_hour > 12:
            end_hour -= 12
            end_ampm = "PM"

        new_event['start_time'] = str(start_hour) + ":" + start_minute + " " + start_ampm
        new_event['end_time'] = str(end_hour) + ":" + end_minute + " " + end_ampm

        start_month = datetime.datetime.strptime(events[n]['start_date'], '%Y-%m-%d').strftime("%B")
        start_day = int(datetime.datetime.strptime(events[n]['start_date'], '%Y-%m-%d').strftime("%d"))
        start_year = datetime.datetime.strptime(events[n]['start_date'], '%Y-%m-%d').strftime("%y")
        end_month = datetime.datetime.strptime(events[n]['end_date'], '%Y-%m-%d').strftime("%B")
        end_day = int(datetime.datetime.strptime(events[n]['end_date'], '%Y-%m-%d').strftime("%d"))
        end_year = datetime.datetime.strptime(events[n]['end_date'], '%Y-%m-%d').strftime("%y")

        new_event['start_date'] = start_month + " " + str(start_day)
        new_event['end_date'] = end_month + " " + str(end_day)

        new_events[num].append(new_event)
    return new_events, event_dates


def search_events(keyword):
    keyword = '%'+str(keyword)+'%'
    return g.db.execute('SELECT * FROM event WHERE title COLLATE UTF8_GENERAL_CI LIKE ? OR organization COLLATE UTF8_GENERAL_CI LIKE ? AND verified = 1 ORDER BY start_date, start_time, end_date, end_time, title', (keyword,keyword,)).fetchall()


def add_event(title, organization, description, start_date, start_time, end_date, end_time, repeated, location, categories, cost, contact_name, contact_email, contact_phone, url):

    event_id = random_string(12)
    password = random_string(8)

    add = '''
                 INSERT INTO event (id, title, organization, description, start_date, start_time, end_date, end_time, repeated, location, cost, contact_name, contact_email, contact_phone, url, password)
                 VALUES (:id, :title, :organization, :description, :start_date, :start_time, :end_date, :end_time, :repeated, :location, :cost, :contact_name, :contact_email, :contact_phone, :url, :password)
                 '''
    add_cursor = g.db.execute(add, {'id': event_id, 'title': title, 'organization': organization, 'description': description, 'start_date': start_date,
                                    'start_time': start_time, 'end_date': end_date, 'end_time': end_time, 'repeated': repeated, 'location': location, 'cost': cost,
                                    'contact_name': contact_name, 'contact_email': contact_email, 'contact_phone': contact_phone,
                                    'url': url, 'password': password})
    g.db.commit()
    if add_cursor.rowcount == 1:
        for category in categories:
            connect = '''
                            INSERT INTO event_category (event_id, category_id)
                            VALUES (:event_id, :category_id)
                            '''
            connect_cursor = g.db.execute(connect, {'event_id': event_id, 'category_id': category })
            g.db.commit()
            if connect_cursor.rowcount != 1:
                return 0
        return event_id, password
    return 0


def upload_photo(event,photo):
    update = 'UPDATE event SET photo = :photo WHERE id = :event_id'
    update_cursor = g.db.execute(update, {'photo': photo, 'event_id': event})
    g.db.commit()
    if update_cursor.rowcount == 1:
        return 1
    return 0


def event_categories(id):
    result = []
    categories = g.db.execute('SELECT * FROM event_category WHERE event_id = ?',(id,)).fetchall()
    for c in categories:
        result.append(c['category_id'])
    return result


def category(id):
    return g.db.execute('SELECT * FROM category WHERE id = ?',(id,)).fetchone()


def categories():
    return g.db.execute('SELECT * FROM category ORDER BY title').fetchall()


def admin_arrange_categories(categories):
    new_categories = []
    for c in categories:
        new_category = {}
        new_category['id'] = c['id']
        new_category['title'] = c['title']
        new_category['date'] = datetime.datetime.strptime(c['created_at'], '%Y-%m-%d %H:%M:%S').strftime('%B') +\
                               " " + str(int(datetime.datetime.strptime(c['created_at'], '%Y-%m-%d %H:%M:%S').strftime('%d'))) + \
                               ", " + datetime.datetime.strptime(c['created_at'], '%Y-%m-%d %H:%M:%S').strftime('%Y')
        new_category['events'] = len(category_events(c['id']))
        new_categories.append(new_category)
    return new_categories


def category_events(id):
    return g.db.execute('SELECT * FROM event_category WHERE category_id = ?',(id,)).fetchall()


def random_string(n):
    return ''.join(random.choice(string.ascii_lowercase + string.digits) for _ in range(n))


def random_integer(n):
    return ''.join(random.choice(string.digits) for _ in range(n))


def question(id):
    return g.db.execute('SELECT * FROM faq WHERE id = ?',(id,)).fetchone()


def questions():
    return g.db.execute('SELECT * FROM faq').fetchall()


def arrange_questions(questions):
    new_questions = []
    for q in questions:
        new_question = {}
        new_question['id'] = q['id']
        new_question['question'] = q['question']
        new_question['answer'] = q['answer']
        new_question['date'] = datetime.datetime.strptime(q['created_at'], '%Y-%m-%d %H:%M:%S').strftime('%B') +\
                               " " + str(int(datetime.datetime.strptime(q['created_at'], '%Y-%m-%d %H:%M:%S').strftime('%d'))) + \
                               ", " + datetime.datetime.strptime(q['created_at'], '%Y-%m-%d %H:%M:%S').strftime('%Y')
        new_questions.append(new_question)
    return new_questions


def setting():
    return g.db.execute('SELECT * FROM setting WHERE id = ?',('dograntcounty',)).fetchone()


def admin_events(year):
    to_year = int(year)+1
    from_date = datetime.datetime.strptime(str(year) + '/1/1', '%Y/%m/%d').strftime(
        '%Y-%m-%d')
    to_date = datetime.datetime.strptime(str(to_year) + '/1/1', '%Y/%m/%d').strftime('%Y-%m-%d')

    return g.db.execute('SELECT * FROM event WHERE start_date BETWEEN ? AND ? AND verified = 1 ORDER BY start_date, start_time, end_date, end_time, title',(from_date, to_date,)).fetchall()


def admin_filter_events(events, category):
    new_events = []
    for e in events:
        if g.db.execute('SELECT * FROM event_category WHERE event_id = ? AND category_id = ?', (e['id'],category)).fetchone() is not None:
            new_events.append(e)
    return new_events


def admin_search_events(keyword):
    keyword = '%' + str(keyword) + '%'
    return g.db.execute('SELECT * FROM event WHERE title COLLATE UTF8_GENERAL_CI LIKE ? OR organization COLLATE UTF8_GENERAL_CI LIKE ? AND verified = 1 ORDER BY start_date, start_time, end_date, end_time, title',(keyword,keyword,)).fetchall()


def admin_arrange_events(events):
    event_dates = {}

    for e in events:
        if int(datetime.datetime.strptime(e['start_date'], '%Y-%m-%d').strftime("%m")) not in event_dates.keys():
            event_dates[int(datetime.datetime.strptime(e['start_date'], '%Y-%m-%d').strftime("%m"))] = []

    for e in events:
        if str(e['start_date']) not in event_dates[int(datetime.datetime.strptime(e['start_date'], '%Y-%m-%d').strftime("%m"))]:
            event_dates[int(datetime.datetime.strptime(e['start_date'], '%Y-%m-%d').strftime("%m"))].append(str(e['start_date']))

    new_events = {}

    for n in range(len(events)):
        month = int(datetime.datetime.strptime(events[n]['start_date'], '%Y-%m-%d').strftime("%m"))
        num = event_dates[month].index(str(events[n]['start_date']))

        if month not in new_events.keys():
            new_events[month] = {}

        if num not in new_events[month].keys():
            new_events[month][num] = []

        new_event = {}
        new_event['id'] = events[n]['id']
        new_event['title'] = events[n]['title']
        new_event['organization'] = events[n]['organization']
        new_event['location'] = events[n]['location']
        new_event['description'] = events[n]['description']
        new_event['repeated'] = events[n]['repeated']

        new_event['cost'] = events[n]['cost']

        new_event['contact_name'] = events[n]['contact_name']
        new_event['contact_email'] = events[n]['contact_email']
        new_event['contact_phone'] = events[n]['contact_phone']
        new_event['url'] = events[n]['url']
        new_event['password'] = events[n]['password']
        new_event['photo'] = events[n]['photo']

        start_hour = int(datetime.datetime.strptime(events[n]['start_time'], '%H:%M').strftime("%H"))
        start_minute = datetime.datetime.strptime(events[n]['start_time'], '%H:%M').strftime("%M")
        start_ampm = "AM"
        end_hour = int(datetime.datetime.strptime(events[n]['end_time'], '%H:%M').strftime("%H"))
        end_minute = datetime.datetime.strptime(events[n]['end_time'], '%H:%M').strftime("%M")
        end_ampm = "AM"

        if start_hour == 12:
            start_ampm = "PM"
        elif start_hour > 12:
            start_hour -= 12
            start_ampm = "PM"
        if end_hour == 12:
            end_ampm = "PM"
        elif end_hour > 12:
            end_hour -= 12
            end_ampm = "PM"

        new_event['start_time'] = str(start_hour) + ":" + start_minute + " " + start_ampm
        new_event['end_time'] = str(end_hour) + ":" + end_minute + " " + end_ampm

        start_month = datetime.datetime.strptime(events[n]['start_date'], '%Y-%m-%d').strftime("%B")
        start_day = int(datetime.datetime.strptime(events[n]['start_date'], '%Y-%m-%d').strftime("%d"))
        start_year = datetime.datetime.strptime(events[n]['start_date'], '%Y-%m-%d').strftime("%Y")
        end_month = datetime.datetime.strptime(events[n]['end_date'], '%Y-%m-%d').strftime("%B")
        end_day = int(datetime.datetime.strptime(events[n]['end_date'], '%Y-%m-%d').strftime("%d"))
        end_year = datetime.datetime.strptime(events[n]['end_date'], '%Y-%m-%d').strftime("%Y")

        new_event['start_date'] = start_month + " " + str(start_day) + ", " + str(start_year)
        new_event['end_date'] = end_month + " " + str(end_day) + ", " + str(end_year)

        new_events[month][num].append(new_event)
    return new_events, event_dates


def admin_edited_events():
    return g.db.execute('SELECT * FROM edit_event ORDER BY created_at').fetchall()


def admin_pendings():
    return g.db.execute('SELECT * FROM event WHERE verified = 0 ORDER BY created_at').fetchall()


def admin_arrange_pendings(pendings):

    new_pendings = []

    for p in pendings:

        new_pending = {}
        new_pending['id'] = p['id']
        new_pending['title'] = p['title']
        new_pending['organization'] = p['organization']
        new_pending['location'] = p['location']
        new_pending['description'] = p['description']
        new_pending['repeated'] = p['repeated']

        new_pending['cost'] = p['cost']

        new_pending['contact_name'] = p['contact_name']
        new_pending['contact_email'] = p['contact_email']
        new_pending['contact_phone'] = p['contact_phone']
        new_pending['url'] = p['url']
        new_pending['password'] = p['password']
        new_pending['photo'] = p['photo']

        start_hour = int(datetime.datetime.strptime(p['start_time'], '%H:%M').strftime("%H"))
        start_minute = datetime.datetime.strptime(p['start_time'], '%H:%M').strftime("%M")
        start_ampm = "AM"
        end_hour = int(datetime.datetime.strptime(p['end_time'], '%H:%M').strftime("%H"))
        end_minute = datetime.datetime.strptime(p['end_time'], '%H:%M').strftime("%M")
        end_ampm = "AM"

        if start_hour == 12:
            start_ampm = "PM"
        elif start_hour > 12:
            start_hour -= 12
            start_ampm = "PM"
        if end_hour == 12:
            end_ampm = "PM"
        elif end_hour > 12:
            end_hour -= 12
            end_ampm = "PM"

        new_pending['start_time'] = str(start_hour) + ":" + start_minute + " " + start_ampm
        new_pending['end_time'] = str(end_hour) + ":" + end_minute + " " + end_ampm

        start_month = datetime.datetime.strptime(p['start_date'], '%Y-%m-%d').strftime("%B")
        start_day = int(datetime.datetime.strptime(p['start_date'], '%Y-%m-%d').strftime("%d"))
        start_year = datetime.datetime.strptime(p['start_date'], '%Y-%m-%d').strftime("%y")
        end_month = datetime.datetime.strptime(p['end_date'], '%Y-%m-%d').strftime("%B")
        end_day = int(datetime.datetime.strptime(p['end_date'], '%Y-%m-%d').strftime("%d"))
        end_year = datetime.datetime.strptime(p['end_date'], '%Y-%m-%d').strftime("%y")

        new_pending['start_date'] = start_month + " " + str(start_day) + ", " + str(start_year)
        new_pending['end_date'] = end_month + " " + str(end_day)+ ", " + str(end_year)

        new_pendings.append(new_pending)
    return new_pendings


def admin_arrange_edited_events(events):

    new_events = []

    for p in events:

        new_pending = {}
        new_pending['id'] = p['id']
        new_pending['title'] = p['title']
        new_pending['organization'] = p['organization']
        new_pending['location'] = p['location']
        new_pending['description'] = p['description']
        new_pending['repeated'] = p['repeated']

        new_pending['cost'] = p['cost']

        new_pending['contact_name'] = p['contact_name']
        new_pending['contact_email'] = p['contact_email']
        new_pending['contact_phone'] = p['contact_phone']
        new_pending['url'] = p['url']
        new_pending['photo'] = p['photo']

        start_hour = int(datetime.datetime.strptime(p['start_time'], '%H:%M').strftime("%H"))
        start_minute = datetime.datetime.strptime(p['start_time'], '%H:%M').strftime("%M")
        start_ampm = "AM"
        end_hour = int(datetime.datetime.strptime(p['end_time'], '%H:%M').strftime("%H"))
        end_minute = datetime.datetime.strptime(p['end_time'], '%H:%M').strftime("%M")
        end_ampm = "AM"

        if start_hour == 12:
            start_ampm = "PM"
        elif start_hour > 12:
            start_hour -= 12
            start_ampm = "PM"
        if end_hour == 12:
            end_ampm = "PM"
        elif end_hour > 12:
            end_hour -= 12
            end_ampm = "PM"

        new_pending['start_time'] = str(start_hour) + ":" + start_minute + " " + start_ampm
        new_pending['end_time'] = str(end_hour) + ":" + end_minute + " " + end_ampm

        start_month = datetime.datetime.strptime(p['start_date'], '%Y-%m-%d').strftime("%B")
        start_day = int(datetime.datetime.strptime(p['start_date'], '%Y-%m-%d').strftime("%d"))
        start_year = datetime.datetime.strptime(p['start_date'], '%Y-%m-%d').strftime("%y")
        end_month = datetime.datetime.strptime(p['end_date'], '%Y-%m-%d').strftime("%B")
        end_day = int(datetime.datetime.strptime(p['end_date'], '%Y-%m-%d').strftime("%d"))
        end_year = datetime.datetime.strptime(p['end_date'], '%Y-%m-%d').strftime("%y")

        new_pending['start_date'] = start_month + " " + str(start_day)
        new_pending['end_date'] = end_month + " " + str(end_day)

        new_events.append(new_pending)
    return new_events


def admin_accept_event(id):
    update = 'UPDATE event SET verified = :verified WHERE id = :event_id'
    update_cursor = g.db.execute(update, {'verified': 1, 'event_id': id})
    g.db.commit()
    if update_cursor.rowcount == 1:
        return 1
    return 0


def admin_delete_event(id):
    category = 'DELETE FROM event_category WHERE event_id = :event_id'
    category_cursor = g.db.execute(category, {'event_id': id})
    g.db.commit()
    edit = 'DELETE FROM edit_event WHERE event_id = :event_id'
    edit_cursor = g.db.execute(edit, {'event_id': id})
    g.db.commit()
    event = 'DELETE FROM event WHERE id = :event_id'
    event_cursor = g.db.execute(event, {'event_id': id})
    g.db.commit()
    if event_cursor.rowcount == 1:
        return 1
    return 0


def admin_edit(id):
    return g.db.execute('SELECT * FROM edit_event WHERE id = ?', (id,)).fetchone()


def admin_accept_edit(id):
    edit = g.db.execute('SELECT * FROM edit_event WHERE id = ?', (id,)).fetchone()
    update = '''
                     UPDATE event SET title = :title, organization = :organization, description = :description,
                      start_date = :start_date, start_time = :start_time, end_date = :end_date, end_time = :end_time, location = :location,
                      cost = :cost, contact_name = :contact_name, contact_email = :contact_email, contact_phone = :contact_phone,
                      url = :url, photo = :photo WHERE id = :event_id
                     '''
    update_cursor = g.db.execute(update, {'event_id': edit['event_id'], 'title': edit['title'], 'organization': edit['organization'],
                                      'description': edit['description'], 'start_date': edit['start_date'],
                                      'start_time': edit['start_time'], 'end_date': edit['end_date'], 'end_time': edit['end_time'],
                                      'location': edit['location'], 'cost': edit['cost'],
                                      'contact_name': edit['contact_name'], 'contact_email': edit['contact_email'],
                                      'contact_phone': edit['contact_phone'],
                                      'url': edit['url'], 'photo': edit['photo']})
    g.db.commit()
    if update_cursor.rowcount == 1:
        event = 'DELETE FROM edit_event WHERE id = :event_id'
        edit_cursor = g.db.execute(event, {'event_id': id})
        g.db.commit()
        if edit_cursor.rowcount == 1:
            return 1
        return 0
    return 0


def admin_delete_edit(id):
    edit = 'DELETE FROM edit_event WHERE id = :event_id'
    edit_cursor = g.db.execute(edit, {'event_id': id})
    g.db.commit()
    if edit_cursor.rowcount == 1:
        return 1
    return 0


def admin_edit_event(id,title, organization, description, start_date, start_time, end_date, end_time, repeated, location, categories, cost, contact_name, contact_email, contact_phone, url):

    edit = '''
                 UPDATE event SET title = :title, organization = :organization, description = :description,
                  start_date = :start_date, start_time = :start_time, end_date = :end_date, end_time = :end_time, repeated = :repeated, location = :location,
                  cost = :cost, contact_name = :contact_name, contact_email = :contact_email, contact_phone = :contact_phone,
                  url = :url WHERE id = :event_id
                 '''
    edit_cursor = g.db.execute(edit, {'event_id': id, 'title': title, 'organization': organization, 'description': description, 'start_date': start_date,
                                    'start_time': start_time, 'end_date': end_date, 'end_time': end_time, 'repeated': repeated, 'location': location, 'cost': cost,
                                    'contact_name': contact_name, 'contact_email': contact_email, 'contact_phone': contact_phone,
                                    'url': url})
    g.db.commit()
    if edit_cursor.rowcount == 1:
        category = 'DELETE FROM event_category WHERE event_id = :event_id'
        category_cursor = g.db.execute(category, {'event_id': id})
        g.db.commit()
        for category in categories:
            connect = '''
                            INSERT INTO event_category (event_id, category_id)
                            VALUES (:event_id, :category_id)
                            '''
            connect_cursor = g.db.execute(connect, {'event_id': id, 'category_id': category})
            g.db.commit()
            if connect_cursor.rowcount != 1:
                return 0
        return 1
    return 0


def edit_event(event_id, title, organization, description, start_date, start_time, end_date, end_time, repeated, location, categories, cost, contact_name, contact_email, contact_phone, url, photo):

    id = random_string(12)

    edit = '''
                     INSERT INTO edit_event (id, event_id, title, organization, description, start_date, start_time, end_date, end_time, repeated, location, cost, contact_name, contact_email, contact_phone, url, photo)
                           VALUES (:id, :event_id, :title, :organization, :description, :start_date, :start_time, :end_date, :end_time, :repeated, :location, :cost, :contact_name, :contact_email, :contact_phone, :url, :photo)
                     '''
    edit_cursor = g.db.execute(edit, {'id': id, 'event_id': event_id, 'title': title, 'organization': organization,
                                      'description': description, 'start_date': start_date,
                                      'start_time': start_time, 'end_date': end_date, 'end_time': end_time,
                                      'repeated': repeated,
                                      'location': location, 'cost': cost,
                                      'contact_name': contact_name, 'contact_email': contact_email,
                                      'contact_phone': contact_phone,
                                      'url': url, 'photo': photo})
    g.db.commit()
    if edit_cursor.rowcount == 1:
        category = 'DELETE FROM event_category WHERE event_id = :event_id'
        category_cursor = g.db.execute(category, {'event_id': event_id})
        g.db.commit()
        for category in categories:
            connect = '''
                            INSERT INTO event_category (event_id, category_id)
                            VALUES (:event_id, :category_id)
                            '''
            connect_cursor = g.db.execute(connect, {'event_id': event_id, 'category_id': category})
            g.db.commit()
            if connect_cursor.rowcount != 1:
                return 0
        return 1
    return 0


def admin_add_category(title):

    category_id = random_string(12)

    add = '''
                 INSERT INTO category (id, title)
                 VALUES (:id, :title)
                 '''
    add_cursor = g.db.execute(add, {'id': category_id, 'title': title })
    g.db.commit()
    if add_cursor.rowcount == 1:
        return 1
    return 0


def admin_edit_category(id, title):

    today = datetime.datetime.today().strftime('%Y-%m-%d %H:%M:%S')

    edit = '''
                 UPDATE category SET title = :title, created_at = :today WHERE id = :category_id
                 '''
    edit_cursor = g.db.execute(edit, {'category_id': id, 'title': title, 'today': today})
    g.db.commit()
    if edit_cursor.rowcount == 1:
        return 1
    return 0


def admin_delete_category(id):
    category = 'DELETE FROM event_category WHERE category_id = :category_id'
    category_cursor = g.db.execute(category, {'category_id': id})
    g.db.commit()
    delete = 'DELETE FROM category WHERE id = :category_id'
    delete_cursor = g.db.execute(delete, {'category_id': id})
    g.db.commit()
    if delete_cursor.rowcount == 1:
        return 1
    return 0


def admin_edit_question(id, question, answer):

    today = datetime.datetime.today().strftime('%Y-%m-%d %H:%M:%S')

    edit = '''
                 UPDATE faq SET question = :question, answer = :answer, created_at = :today WHERE id = :question_id
                 '''
    edit_cursor = g.db.execute(edit, {'question_id': id, 'question': question, 'answer': answer, 'today': today})
    g.db.commit()
    if edit_cursor.rowcount == 1:
        return 1
    return 0


def admin_delete_question(id):
    question = 'DELETE FROM faq WHERE id = :question_id'
    question_cursor = g.db.execute(question, {'question_id': id})
    g.db.commit()
    if question_cursor.rowcount == 1:
        return 1
    return 0


def admin_add_question(question, answer):

    question_id = random_string(12)

    add = '''
                 INSERT INTO faq (id, question, answer)
                 VALUES (:id, :question, :answer)
                 '''
    add_cursor = g.db.execute(add, {'id': question_id, 'question': question, 'answer': answer})
    g.db.commit()
    if add_cursor.rowcount == 1:
        return 1
    return 0


def admin_update_about(title, content):
    today = datetime.datetime.today().strftime('%Y-%m-%d %H:%M:%S')
    edit = '''
                 UPDATE setting SET about_title = :title, about_content = :content, created_at = :today WHERE id = :id
                 '''
    edit_cursor = g.db.execute(edit, {'id': 'dograntcounty', 'title': title, 'content': content, 'today': today})
    g.db.commit()
    if edit_cursor.rowcount == 1:
        return 1
    return 0


def admin_update_faq(title, content):
    today = datetime.datetime.today().strftime('%Y-%m-%d %H:%M:%S')
    edit = '''
                 UPDATE setting SET faq_title = :title, faq_content = :content, created_at = :today WHERE id = :id
                 '''
    edit_cursor = g.db.execute(edit, {'id': 'dograntcounty', 'title': title, 'content': content, 'today': today})
    g.db.commit()
    if edit_cursor.rowcount == 1:
        return 1
    return 0


def admin_update_contact(title, content, email, phone):
    today = datetime.datetime.today().strftime('%Y-%m-%d %H:%M:%S')
    edit = '''
                 UPDATE setting SET contact_title = :title, contact_content = :content, contact_email = :email, contact_phone = :phone, created_at = :today WHERE id = :id
                 '''
    edit_cursor = g.db.execute(edit, {'id': 'dograntcounty', 'title': title, 'content': content, 'email': email, 'phone': phone, 'today': today})
    g.db.commit()
    if edit_cursor.rowcount == 1:
        return 1
    return 0


def admin_add_event(title, organization, description, start_date, start_time, end_date, end_time, repeated, location, categories, cost, contact_name, contact_email, contact_phone, url):

    event_id = random_string(12)
    password = random_string(8)

    add = '''
                 INSERT INTO event (id, title, organization, description, start_date, start_time, end_date, end_time, repeated, location, cost, contact_name, contact_email, contact_phone, url, password, verified)
                 VALUES (:id, :title, :organization, :description, :start_date, :start_time, :end_date, :end_time, :repeated, :location, :cost, :contact_name, :contact_email, :contact_phone, :url, :password, :verified)
                 '''
    add_cursor = g.db.execute(add, {'id': event_id, 'title': title, 'organization': organization, 'description': description, 'start_date': start_date,
                                    'start_time': start_time, 'end_date': end_date, 'end_time': end_time, 'repeated': repeated, 'location': location, 'cost': cost,
                                    'contact_name': contact_name, 'contact_email': contact_email, 'contact_phone': contact_phone,
                                    'url': url, 'password': password, 'verified': 1})
    g.db.commit()
    if add_cursor.rowcount == 1:
        for category in categories:
            connect = '''
                            INSERT INTO event_category (event_id, category_id)
                            VALUES (:event_id, :category_id)
                            '''
            connect_cursor = g.db.execute(connect, {'event_id': event_id, 'category_id': category })
            g.db.commit()
            if connect_cursor.rowcount != 1:
                return 0
        return event_id, password
    return 0


def event_id(password):
    e = g.db.execute('SELECT * FROM event WHERE password = ?', (password,)).fetchone()
>>>>>>> e4b61b7595c8a18fb64b8632a62f9a096ff8459c
    return e['id']