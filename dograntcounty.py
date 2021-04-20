# coding=utf-8
from flask import Flask, render_template, flash, redirect, url_for, request, session, jsonify
from wtforms import StringField, SubmitField, SelectField, SelectMultipleField, PasswordField, BooleanField, HiddenField, TextAreaField
from wtforms.fields.html5 import DateField, EmailField, TelField, DecimalField, URLField, IntegerField
from wtforms_components import TimeField, DateRange
from wtforms.validators import Email, Length, NumberRange, DataRequired, InputRequired, EqualTo, AnyOf, Regexp, Optional, Required, URL
from flask_wtf import FlaskForm, validators
from flask_wtf.file import FileField, FileRequired, FileAllowed
from flask_uploads import UploadSet, configure_uploads, IMAGES, patch_request_class
from flask_login import LoginManager, login_user, logout_user, login_required, current_user
from flask_hashing import Hashing
from flask_mail import Mail, Message
import string, random, datetime, re, os

import db

import smtplib
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from email.header import Header
from email.utils import formataddr



app = Flask(__name__)
hashing = Hashing(app)

UPLOAD_FOLDER = db_path = os.path.join(app.root_path, os.path.abspath('/home/dograntcounty/mysite/static/event-pics'))
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER

app.config.update(
    DEBUG=True,
    #MAIL_SERVER='smtp.mail.com',
    #MAIL_PORT=465,
    #MAIL_USE_SSL=True,
    #MAIL_USERNAME='dograntcounty@email.com',
    MAIL_SERVER='smtp.office365.com',
    MAIL_PORT=587,
    MAIL_USE_TSL=True,
    MAIL_USERNAME='contact@dograntcounty.com',
    MAIL_PASSWORD='GC-Community-Events1!'
)

mail = Mail(app)


def send_email(recipients, title, text_body, html_body):
    msg = Message(title, sender='contact@dograntcounty.com', recipients=recipients)
    msg.body = text_body
    msg.html = html_body
    mail.send(msg)


app.config['SECRET_KEY'] = 'Do Grant County Key'
app.config['WTF_CSRF_ENABLED'] = False


@app.before_request
def before():
    db.open_db_connection()
    session.permanent = False


@app.teardown_request
def after(exception):
    db.close_db_connection()


# LOGIN
login_mgr = LoginManager(app)


@login_mgr.user_loader
def load_user(id):
    return User(id)


class User(object):
    def __init__(self, id):
        self.id = id
        self.name = 'Do! Grant County'
        self.is_authenticated = True
        self.is_active = True
        self.is_anonymous = False
        if id == "GC-Community-Events1!":
            self.is_admin = True
        else:
            self.is_admin = False

    def get_id(self):
        return self.id

    def __repr__(self):
        return "<User '{}' {} {} {}>".format(self.id, self.is_authenticated, self.is_active, self.is_anonymous)


def authenticate_id(id):
    if id == 'GC-Community-Events1!':
        return id
    else:
        for p in db.all_events():
            if p['password'] == id:
                return id
    return None


@app.route('/admin/logout')
@login_required
def logout():

    if not current_user.is_authenticated:
        return redirect(url_for('admin'))

    logout_user()
    return redirect(url_for('admin'))


@app.route('/logout')
@login_required
def user_logout():

    if not current_user.is_authenticated:
        return redirect(url_for('login'))

    logout_user()
    return redirect(url_for('login'))


months_char = {
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
months_num = {
    1: 'jan',
    2: 'feb',
    3: 'mar',
    4: 'apr',
    5: 'may',
    6: 'jun',
    7: 'jul',
    8: 'aug',
    9: 'sep',
    10: 'oct',
    11: 'nov',
    12: 'dec'
}
months_whole = {
    'jan': 'January',
    'feb': 'February',
    'mar': 'March',
    'apr': 'April',
    'may': 'May',
    'jun': 'June',
    'jul': 'July',
    'aug': 'August',
    'sep': 'September',
    'oct': 'October',
    'nov': 'November',
    'dec': 'December'
}

global new_event
new_event = ''


global admin_year
admin_year = ''


@app.route('/')
def index():
    return redirect(url_for('events'))


@app.route('/about', methods=["GET", "POST"])
def about():
    setting = db.setting()
    return render_template('about.html', setting=setting)


@app.route('/events', methods=["GET", "POST"])
def events():
    year = datetime.datetime.today().year
    month = months_num[datetime.datetime.today().month]
    return redirect(url_for('event', year=year, month=month))


@app.route('/events/', methods=["GET", "POST"])
def events2():
    year = datetime.datetime.today().year
    month = months_num[datetime.datetime.today().month]
    return redirect(url_for('event', year=year, month=month))


@app.route('/events/<year>/<month>/', methods=["GET", "POST"])
def event(year, month):

    if not session.get('filter-event'):
        session['filter-event'] = '0'

    today = datetime.datetime.today() - datetime.timedelta(days=1)
    today = today.strftime('%Y-%m-%d')

    today = datetime.datetime.strptime(today, '%Y-%m-%d').strftime("%A") \
    + ", " + datetime.datetime.strptime(today, '%Y-%m-%d').strftime("%b") + " " + \
    str(int(datetime.datetime.strptime(today, '%Y-%m-%d').strftime("%d")))

    previous_year = int(year)
    previous_month = months_char[month] - 1
    if previous_month == 0:
        previous_month = 12
        previous_year = int(year) - 1
    previous_month = months_num[previous_month]

    next_year = int(year)
    next_month = months_char[month] + 1
    if next_month > 12:
        next_month = 1
        next_year = int(year) + 1
    next_month = months_num[next_month]

    controls = {
        'previous': [previous_month, previous_year],
        'next': [next_month, next_year]
    }

    events = db.events2(year, month)
    if session.get('filter-event') != '0':
        events = db.filter_events(events, session.get('filter-event'))

    event_dates = db.ar_events(events, year, month)[1]
    nums = []
    for n in range(len(event_dates)):
        nums.append(n)
        event_dates[n] = datetime.datetime.strptime(event_dates[n], '%Y-%m-%d').strftime("%A")\
                         + ", " + datetime.datetime.strptime(event_dates[n], '%Y-%m-%d').strftime("%b") + " " +\
                         str(int(datetime.datetime.strptime(event_dates[n], '%Y-%m-%d').strftime("%d"))) + ", " +\
                         datetime.datetime.strptime(event_dates[n], '%Y-%m-%d').strftime("%Y")

    events = db.ar_events(events, year, month)[0]

    search = SearchEventForm()

    if search.validate_on_submit() and search.search_submit.data:
        return redirect(url_for('search_event', keyword=search.keyword.data))

    category = CategoryEventForm(category=session.get('filter-event'))
    category2 = CategoryEventForm2(category2=session.get('filter-event'))
    category.category.choices = [('0', 'All Categories')]
    category2.category2.choices = [('0', 'All Categories')]

    for c in db.categories():
        category.category.choices.append((c['id'], c['title']))
        category2.category2.choices.append((c['id'], c['title']))

    if category.validate_on_submit() and category.category_submit.data:
        #filter_event = category.category.data
        session['filter-event'] = category.category.data
        return redirect(url_for('event', year=year, month=month))

    if category2.validate_on_submit() and category2.category_submit2.data:
        session['filter-event'] = category2.category2.data
        return redirect(url_for('event', year=year, month=month))

    return render_template('event.html', year=year, month=months_whole[month], today=today, nums=nums, event_dates=event_dates, events=events, controls=controls, search=search, category=category, category2=category2)


@app.route('/update/events/<year>/<month>/', methods=["GET", "POST"])
def update_event(year, month):

    global filter_event

    print(filter_event)

    today = datetime.datetime.today() - datetime.timedelta(days=1)
    today = today.strftime('%Y-%m-%d')

    today = datetime.datetime.strptime(today, '%Y-%m-%d').strftime("%A") \
    + ", " + datetime.datetime.strptime(today, '%Y-%m-%d').strftime("%b") + " " + \
    str(int(datetime.datetime.strptime(today, '%Y-%m-%d').strftime("%d")))

    previous_year = int(year)
    previous_month = months_char[month] - 1
    if previous_month == 0:
        previous_month = 12
        previous_year = int(year) - 1
    previous_month = months_num[previous_month]

    next_year = int(year)
    next_month = months_char[month] + 1
    if next_month > 12:
        next_month = 1
        next_year = int(year) + 1
    next_month = months_num[next_month]

    controls = {
        'previous': [previous_month, previous_year],
        'next': [next_month, next_year]
    }

    events = db.events(year, month)
    if filter_event != '0':
        events = db.filter_events(events, filter_event)

    print(events)

    event_dates = db.ar_events(events)[1]
    nums = []
    for n in range(len(event_dates)):
        nums.append(n)
        event_dates[n] = datetime.datetime.strptime(event_dates[n], '%Y-%m-%d').strftime("%A")\
                         + ", " + datetime.datetime.strptime(event_dates[n], '%Y-%m-%d').strftime("%b") + " " +\
                         str(int(datetime.datetime.strptime(event_dates[n], '%Y-%m-%d').strftime("%d")))

    events = db.ar_events(events)[0]

    search = SearchEventForm()

    if search.validate_on_submit() and search.search_submit.data:
        return redirect(url_for('search_event', keyword=search.keyword.data))

    category = CategoryEventForm(category=filter_event)
    category.category.choices = [('0', 'All Categories')]
    for c in db.categories():
        category.category.choices.append((c['id'], c['title']))

    if category.validate_on_submit() and category.category_submit.data:
        filter_event = category.category.data
        return redirect(url_for('event', year=year, month=month))

    return render_template('event.html', year=year, month=months_whole[month], today=today, nums=nums, event_dates=event_dates, events=events, controls=controls, search=search, category=category)


@app.route('/events/search/<keyword>', methods=["GET", "POST"])
def search_event(keyword):

    events = db.search_events(keyword)

    event_dates = db.arrange_events(events)[1]
    nums = []
    for n in range(len(event_dates)):
        nums.append(n)
        event_dates[n] = datetime.datetime.strptime(event_dates[n], '%Y-%m-%d').strftime("%A") \
                         + ", " + datetime.datetime.strptime(event_dates[n], '%Y-%m-%d').strftime("%b") + " " + \
                         str(int(datetime.datetime.strptime(event_dates[n], '%Y-%m-%d').strftime("%d")))

    events = db.arrange_events(events)[0]

    search = SearchEventForm(keyword=keyword)

    if search.validate_on_submit() and search.search_submit.data:
        return redirect(url_for('search_event', keyword=search.keyword.data))

    return render_template('search.html', events=events, search=search, nums=nums, event_dates=event_dates)


@app.route('/events/search/', methods=["GET", "POST"])
def search_event2():
    return redirect(url_for('events'))


@app.route('/events/new', methods=["GET", "POST"])
def new():

    global new_event

    today = datetime.datetime.today().strftime('%Y-%m-%d %H:%M:%S')
    start_time = '9:00'
    end_time = '10:00'

    form = NewEventForm(start_date=datetime.datetime.strptime(today, '%Y-%m-%d %H:%M:%S'),
                        end_date=datetime.datetime.strptime(today, '%Y-%m-%d %H:%M:%S'),
                        start_time=datetime.datetime.strptime(start_time, '%H:%M'),
                        end_time=datetime.datetime.strptime(end_time, '%H:%M'))
    form.category.choices = [(i['id'], i['title']) for i in db.categories()]

    if form.validate_on_submit():

        start_time = str(form.start_time.data)[:5]
        end_time = str(form.end_time.data)[:5]

        if re.match(r"(^[a-zA-Z0-9_.+-]+@[a-zA-Z0-9-]+\.[a-zA-Z0-9-.]+$)", form.contact_email.data):

            id, password = db.add_event(form.title.data,
                                     form.organization.data,
                                     form.description.data,
                                     form.start_date.data,
                                     start_time,
                                     form.end_date.data,
                                     end_time,
                                     form.repeated.data,
                                     form.location.data,
                                     form.category.data,
                                     form.cost.data,
                                     form.contact_name.data,
                                     form.contact_email.data,
                                     form.contact_phone.data,
                                     form.url.data)

            if 'photo' in request.files:
                file = request.files['photo']
                print(file.filename)
                name = ''
                if file.filename != '':
                    #fix_orientation(file, save_over=False)
                    ext = file.filename.split('.')
                    name = db.random_string(12) + '.' + ext[-1]
                    f = os.path.join(app.config['UPLOAD_FOLDER'], name)
                    file.save(f)

                upload = db.upload_photo(id, name)

                if upload != 1:
                    print('UPLOAD PHOTO FAILED')

            if password != 0:

                """

                title = "Thanks for creating an event!"

                html = '''
                                    <!DOCTYPE html>
                                    <html lang="en-us">
                                    <head>
                                    <meta charset="utf-8">
                                    <meta http-equiv="X-UA-Compatible" content="IE=edge">
                                    <meta name="viewport" content="width=device-width, initial-scale=1, maximum-scale=1, user-scalable=0">
                                    <link href="https://fonts.googleapis.com/css?family=Encode+Sans+Semi+Expanded:300,400,500,600,700" rel="stylesheet">
                                    <title></title>
                                    <style>
                                        body { width: 100%; height: 100%; background: none; padding: 1rem; margin: 0;
                                            font-size: 0.95rem; font-family: 'Encode Sans Semi Expanded', sans-serif; font-weight: 300;
                                            color: #474747; text-align: center; line-height: 1.5; }
                                        p { margin: 0; padding: 0; margin-bottom: 0.5rem; text-align: left; }
                                        button {
                                            font-size: 0.95rem; font-family: 'Encode Sans Semi Expanded', sans-serif; font-weight: 500;
                                            width: auto; cursor: pointer; background: #fff;
                                            border: 0.06rem solid #5f3bba; border-radius: 0.25rem; color: #5f3bba;
                                            padding: 0.6rem 1rem; margin: 1rem auto; }
                                        button:hover { background: #5f3bba; color: #fff; }
                                        #frame { width: 100%; max-width: 450px; margin: 3rem auto; }
                                        #logo { width: 11rem; height: auto; margin: 0 auto; }
                                        #dear { margin-top: 2.5rem; margin-bottom: 2.5rem; }
                                        #end-message { margin-top: 2.5rem;}
                                        #info { padding: 1.5rem; text-align: center; }
                                        #note { margin-top: 2rem; color: #cecece; font-size: 0.8rem; }
                                    </style>
                                    </head><body><div id="frame">
                                        <p id="dear">Dear ''' + form.contact_name.data + ''',</p>
                                        <p>Thank you for adding an event to DoGrantCounty!<br>Our administrative team will review your event details before publishing to ensure it follows our event guidelines. We will do our best to post your event within 2-3 business days. Don’t forget to share www.DoGrantCounty.com and your event on social media.<br>
                                        Thanks again, for using DoGrantCounty to promote the good things happening in Grant County, Indiana!</p>
                                        <p id="end-message">The Do Grant County Team</p>
                                    </div></body></html>
                                    '''

                msg = MIMEMultipart('alternative')
                msg['From'] = formataddr((str(Header('DoGrantCounty.com', 'utf-8')), 'contact@dograntcounty.com'))
                msg['To'] = form.contact_email.data
                msg['Subject'] = title
                mt_html = MIMEText(html, 'html')
                msg.attach(mt_html)

                s = smtplib.SMTP("smtp.office365.com", 587)
                s.ehlo()
                s.starttls()
                s.login("contact@dograntcounty.com", "GC-Community-Events1!")
                s.sendmail("contact@dograntcounty.com", [form.contact_email.data], msg.as_string())


                """

                """

                # Mail to Admin

                title2 = "New Event: "+form.title.data

                html2 = '<!DOCTYPE html><html lang="en-us"><head><meta charset="utf-8"><meta http-equiv="X-UA-Compatible" content="IE=edge"><meta name="viewport" content="width=device-width, initial-scale=1, maximum-scale=1, user-scalable=0"><link href="https://fonts.googleapis.com/css?family=Encode+Sans+Semi+Expanded:300,400,500,600,700" rel="stylesheet"><title></title><style>' \
                        + 'body { width: 100%; height: 100%; background: none; padding: 1rem; margin: 0; font-size: 0.95rem; font-family: "Encode Sans Semi Expanded", sans-serif; font-weight: 300; color: #474747; text-align: center; line-height: 1.5; } p { margin: 0; padding: 0; margin-bottom: 0.5rem; text-align: left; } button { font-size: 0.95rem; font-family: "Encode Sans Semi Expanded", sans-serif; font-weight: 500; width: auto; cursor: pointer; background: #fff; border: 0.06rem solid #5f3bba; border-radius: 0.25rem; color: #5f3bba; padding: 0.6rem 1rem; margin: 1rem auto; } button:hover { background: #5f3bba; color: #fff; } @media all and (min-width: 700px) {#frame {margin: 1rem;}}' \
                        + '#frame { width: 100%; max-width: 450px; margin: 3rem auto; } #logo { width: 11rem; height: auto; margin: 0 auto; } #dear { margin-top: 2.5rem; margin-bottom: 2.5rem; } #end-message { margin-top: 2.5rem;} #info { padding: 1.5rem; text-align: center; } #note { margin-top: 2rem; color: #cecece; font-size: 0.8rem; }' \
                        + '</style> </head><body><div id="frame">' \
                        + '<p id="dear">Dear DoGrantCounty.com,</p><p>New event has been added. Please go and verify the new event.</p>' \
                        + '<div id="info"><p>Event Host: <b>'+ str(form.organization.data) + '</b></p><p>Event Title: <b>' + str(form.title.data) + '</b></p></div>' \
                        + '<p id="end-message">The Do Grant County Team</p><p id="note">Note: New event will not be displayed on the website until you verify the event.</p></div></body></html>'



                msg2 = MIMEMultipart('alternative')
                msg2['From'] = formataddr((str(Header('DoGrantCounty.com', 'utf-8')), 'contact@dograntcounty.com'))
                msg2['To'] = 'contact@dograntcounty.com'
                msg2['Subject'] = title2
                mt_html2 = MIMEText(html2, 'html')
                msg2.attach(mt_html2)

                """

                s2 = smtplib.SMTP("smtp.office365.com", 587)
                s2.ehlo()
                s2.starttls()
                s2.login("contact@dograntcounty.com", "GC-Community-Events1!")

                #s2.sendmail("contact@dograntcounty.com", ["contact@dograntcounty.com"], msg2.as_string())

                # Mail to User

                title1 = "Thanks for creating an event!"

                html1 = '<!DOCTYPE html><html lang="en-us"><head><meta charset="utf-8"><meta http-equiv="X-UA-Compatible" content="IE=edge"><meta name="viewport" content="width=device-width, initial-scale=1, maximum-scale=1, user-scalable=0"><link href="https://fonts.googleapis.com/css?family=Encode+Sans+Semi+Expanded:300,400,500,600,700" rel="stylesheet"><title></title><style>' \
                        + 'body { width: 100%; height: 100%; background: none; padding: 1rem; margin: 0; font-size: 0.95rem; font-family: "Encode Sans Semi Expanded", sans-serif; font-weight: 300; color: #474747; text-align: center; line-height: 1.5; } p { margin: 0; padding: 0; margin-bottom: 0.5rem; text-align: left; }' \
                        + 'a { font-size: inherit; font-weight: inherit; color: #5f3bba; text-decoration: none; } a:hover { color: #5f3bba; } button { font-size: 0.95rem; font-family: "Encode Sans Semi Expanded", sans-serif; font-weight: 500; width: auto; cursor: pointer; background: #fff; border: 0.06rem solid #5f3bba; border-radius: 0.25rem; color: #5f3bba; padding: 0.6rem 1rem; margin: 1rem auto; } button:hover { background: #5f3bba; color: #fff; } #frame { width: 100%; max-width: 450px; margin: 3rem auto; } #logo { width: 11rem; height: auto; margin: 0 auto; } #dear { margin-top: 2.5rem; margin-bottom: 2.5rem; } #end-message { margin-top: 2.5rem;} #info { padding: 1.5rem; text-align: center; } #note { margin-top: 2rem; color: #cecece; font-size: 0.8rem; } @media all and (min-width: 700px) {#frame {margin: 1rem;}}' \
                        + '</style></head><body><div id="frame">' \
                        + '<p id="dear">Dear '+ str(form.contact_name.data)+',</p><p>Thank you for adding an event to DoGrantCounty!<br>Our administrative team will review your event details before publishing to ensure it follows our event guidelines. We will do our best to post your event within 2-3 business days. Do not forget to share <a href="https://www.dograntcounty.com">www.DoGrantCounty.com</a> and your event on social media.<br>Thanks again, for using DoGrantCounty to promote the good things happening in Grant County, Indiana!</p>' \
                        + '<p id="end-message">The Do Grant County Team</p><p id="note"></p></div></body></html>'

                msg1 = MIMEMultipart('alternative')
                msg1['From'] = formataddr((str(Header('DoGrantCounty.com', 'utf-8')), 'contact@dograntcounty.com'))
                msg1['To'] = form.contact_email.data
                msg1['Subject'] = title1
                mt_html1 = MIMEText(html1, 'html')
                msg1.attach(mt_html1)

                s2.sendmail("contact@dograntcounty.com", [str(form.contact_email.data)], msg1.as_string())
                s2.quit()

                flash('New event has been added.')
                flash('Please wait for verification.')

            return redirect(url_for('events'))

        else:
            flash('Email is invalid.')

    return render_template('new.html', form=form, categories=db.categories())


@app.route('/update/events/new', methods=["GET", "POST"])
def update_new():

    global new_event

    today = datetime.datetime.today().strftime('%Y-%m-%d %H:%M:%S')
    start_time = '9:00'
    end_time = '10:00'

    form = NewEventForm(start_date=datetime.datetime.strptime(today, '%Y-%m-%d %H:%M:%S'),
                        end_date=datetime.datetime.strptime(today, '%Y-%m-%d %H:%M:%S'),
                        start_time=datetime.datetime.strptime(start_time, '%H:%M'),
                        end_time=datetime.datetime.strptime(end_time, '%H:%M'))
    form.category.choices = [(i['id'], i['title']) for i in db.categories()]

    if form.validate_on_submit():

        start_time = str(form.start_time.data)[:5]
        end_time = str(form.end_time.data)[:5]

        if re.match(r"(^[a-zA-Z0-9_.+-]+@[a-zA-Z0-9-]+\.[a-zA-Z0-9-.]+$)", form.contact_email.data):

            id, password = db.add_event(form.title.data,
                                     form.organization.data,
                                     form.description.data,
                                     form.start_date.data,
                                     start_time,
                                     form.end_date.data,
                                     end_time,
                                     form.repeated.data,
                                     form.location.data,
                                     form.category.data,
                                     form.cost.data,
                                     form.contact_name.data,
                                     form.contact_email.data,
                                     form.contact_phone.data,
                                     form.url.data)

            if 'photo' in request.files:
                file = request.files['photo']
                print(file.filename)
                name = ''
                if file.filename != '':
                    #fix_orientation(file, save_over=False)
                    ext = file.filename.split('.')
                    name = db.random_string(12) + '.' + ext[-1]
                    f = os.path.join(app.config['UPLOAD_FOLDER'], name)
                    file.save(f)

                upload = db.upload_photo(id, name)

                if upload != 1:
                    print('UPLOAD PHOTO FAILED')

            if password != 0:

                flash('New event has been added.')
            else:
                flash('Error: Cannot add new event.')

            return redirect(url_for('events'))

        else:
            flash('Email is invalid.')

    return render_template('new-event.html', form=form, categories=db.categories())


@app.route('/guidelines', methods=["GET", "POST"])
def guidelines():
    return render_template('guidelines.html')


@app.route('/events/new/photo', methods=["GET", "POST"])
def new_photo():

    global new_event

    if new_event == 0:
        return redirect(url_for('events'))

    form = PhotoForm()

    if form.validate_on_submit():
        if 'photo' not in request.files:
            flash('Photo not chosen.')
        else:
            file = request.files['photo']
            print(file.filename)
            ext = file.filename.split('.')
            name = db.random_string(12) + '.' + ext[-1]
            print(name)
            f = os.path.join(app.config['UPLOAD_FOLDER'], name)
            file.save(f)

            upload = db.upload_photo(new_event, name)

            if upload == 1:
                return redirect(url_for('events'))
            else:
                flash('Photo Upload failed.')

    return render_template('new-photo.html', form=form)


@app.route('/events/new/photo/upload', methods=["POST"])
def upload_photo():

    global new_event

    file = request.files['photo']
    ext = file.filename.split('.')
    name = db.random_string(12)+'.'+ext[-1]
    f = os.path.join(app.config['UPLOAD_FOLDER'], name)
    file.save(f)

    upload = db.upload_photo(new_event, name)

    if upload != 1:
        print("Upload Fail")

    return redirect(url_for('events'))


@app.route('/faq', methods=["GET", "POST"])
def faq():
    setting = db.setting()
    questions = db.questions()
    questions = db.arrange_questions(questions)
    return render_template('faq.html', questions=questions, setting=setting)


@app.route('/contact', methods=["GET", "POST"])
def contact():
    setting = db.setting()
    return render_template('contact.html', setting=setting)


class NewEventForm(FlaskForm):
    title = StringField('Title', [InputRequired(message="Title is required."), Length(max=50, message="Title is too long (max 50 char).")])
    organization = StringField('Host (Organization)', [InputRequired(message="Host is required."), Length(max=50, message="Host is too long (max 50 char).")])
    description = TextAreaField('Description', [InputRequired(message="Description is required."), Length(max=1000, message="Description is too long (max 1,000 char).")])
    start_date = DateField('Start Date', [InputRequired(message="Start Date is required."), DateRange(min=datetime.date(2000,1,1),message="Date should be later than Jan 1, 2000.")], format='%Y-%m-%d')
    end_date = DateField('End Date', [InputRequired(message="End Date is required."), DateRange(min=datetime.date(2000,1,1),message="Date should be later than Jan 1, 2000.")], format='%Y-%m-%d')
    start_time = TimeField('Start Time', [InputRequired(message="Start Time is required.")])
    end_time = TimeField('End Time', [InputRequired(message="End Time is required.")])
    category = SelectMultipleField('Category')
    cost = StringField('Cost', [Length(max=50, message="Cost is too long (max 50 char).")])
    contact_name = StringField('Contact Name', [InputRequired(message="Contact Name is required.")])
    contact_email = EmailField('Contact Email', [InputRequired(message="Contact Email is required.")])
    contact_phone = TelField('Contact Phone')
    location = StringField('Location', [InputRequired(message="Location is required.")])
    url = StringField('Web URL', [Length(max=100, message="Web URL is too long (max 100 char).")])
    photo = FileField('Photo', [FileAllowed(['jpg', 'png', 'jpeg', 'gif'], 'You can upload images only.')])
    repeated = SelectField('Repeated', choices=[('daily', 'Daily'), ('weekly', 'Weekly'), ('monthly', 'Monthly'), ('weekday','Every th day')])
    submit = SubmitField('Add Event')


class EditEventForm(FlaskForm):
    title = StringField('Title', [InputRequired(message="Title is required."),
                                  Length(max=50, message="Title is too long (max 50 char).")])
    organization = StringField('Host (Organization)', [InputRequired(message="Host is required."),
                                                       Length(max=50, message="Host is too long (max 50 char).")])
    description = TextAreaField('Description', [InputRequired(message="Description is required."),
                                                Length(max=1000, message="Description is too long (max 1,000 char).")])
    start_date = DateField('Start Date', [InputRequired(message="Start Date is required."), DateRange(min=datetime.date(2000,1,1),message="Date should be later than Jan 1, 2000.")], format='%Y-%m-%d')
    end_date = DateField('End Date', [InputRequired(message="End Date is required."), DateRange(min=datetime.date(2000,1,1),message="Date should be later than Jan 1, 2000.")], format='%Y-%m-%d')
    start_time = TimeField('Start Time', [InputRequired(message="Start Time is required.")])
    end_time = TimeField('End Time', [InputRequired(message="End Time is required.")])
    category = SelectMultipleField('Category')
    cost = StringField('Cost', [Length(max=50, message="Cost is too long (max 50 char).")])
    contact_name = StringField('Contact Name', [InputRequired(message="Contact Name is required.")])
    contact_email = EmailField('Contact Email', [InputRequired(message="Contact Email is required.")])
    contact_phone = TelField('Contact Phone')
    location = StringField('Location', [InputRequired(message="Location is required.")])
    url = StringField('Web URL', [Length(max=100, message="Web URL is too long (max 100 char).")])
    photo = FileField('Photo', [FileAllowed(['jpg', 'png', 'jpeg', 'gif'], 'You can upload images only.')])
    repeated = SelectField('Repeated', choices=[('daily', 'Daily'), ('weekly', 'Weekly'), ('monthly', 'Monthly'), ('weekday','Every th day')])
    old_photo = HiddenField('Old Photo')
    replicate = HiddenField('Replicate')
    submit = SubmitField('Edit Event')


class PhotoForm(FlaskForm):
    photo = FileField('Photo', [FileAllowed(['jpg', 'png', 'jpeg', 'gif'], 'You can upload images only.')])
    submit = SubmitField('Upload Photo')


class NewCategoryForm(FlaskForm):
    title = StringField('Title', [InputRequired(message="Title is required.")])
    submit = SubmitField('Add Category')


class NewQuestionForm(FlaskForm):
    question = StringField('Question', [InputRequired(message="Question is required.")])
    answer = TextAreaField('Answer', [InputRequired(message="Answer is required.")])
    submit = SubmitField('Add Question')


class LoginForm(FlaskForm):
    username = StringField('Username', [InputRequired(message="Username is required.")])
    password = PasswordField('Password', [InputRequired(message="Password is required.")])
    submit = SubmitField('Sign In')


class UserLoginForm(FlaskForm):
    password = StringField('Event Password', [InputRequired(message="Password is required.")])
    submit = SubmitField('Sign In')


class SearchEventForm(FlaskForm):
    keyword = StringField('Keyword')
    search_submit = SubmitField('Search Event')


class CategoryEventForm(FlaskForm):
    category = SelectField('Category', choices=[('0','All Categories')])
    category_submit = SubmitField('Category Event')

class CategoryEventForm2(FlaskForm):
    category2 = SelectField('Category', choices=[('0', 'All Categories')])
    category_submit2 = SubmitField('Category Event')


class AboutForm(FlaskForm):
    about_title = StringField('Title', [InputRequired(message="Title is required.")])
    about_content = TextAreaField('Content', [InputRequired(message="Content is required.")])
    about_submit = SubmitField('Update')


class FaqForm(FlaskForm):
    faq_title = StringField('Title', [InputRequired(message="Title is required.")])
    faq_content = TextAreaField('Content')
    faq_submit = SubmitField('Update')


class ContactForm(FlaskForm):
    contact_title = StringField('Title', [InputRequired(message="Title is required.")])
    contact_email = StringField('Email', [InputRequired(message="Email is required."), Email(message="Email is invalid.")])
    contact_phone = StringField('Phone', [InputRequired(message="Phone is required.")])
    contact_content = TextAreaField('Content')
    contact_submit = SubmitField('Update')







#######    ADMIN


@app.route('/admin/', methods=["GET", "POST"])
def admin():

    print(current_user)

    if current_user.is_authenticated and current_user.is_admin:
        return redirect(url_for('admin_events'))

    form = LoginForm()

    if form.validate_on_submit():

        if form.username.data == 'admin' and form.password.data == 'GC-Community-Events1!':
            user = User(form.password.data)
            login_user(user)
            return redirect(url_for('admin_events'))

    return render_template('admin-login.html', form=form)


@app.route('/admin/events', methods=["GET", "POST"])
def admin_events():

    if not current_user.is_authenticated or not current_user.is_admin:
        return redirect(url_for('admin'))

    year = datetime.datetime.today().year
    return redirect(url_for('admin_event', year=year))


@app.route('/admin/events/', methods=["GET", "POST"])
def admin_events2():

    if not current_user.is_authenticated or not current_user.is_admin:
        return redirect(url_for('admin'))

    year = datetime.datetime.today().year
    return redirect(url_for('admin_event', year=year))



@app.route('/admin/events/<year>', methods=["GET", "POST"])
def admin_event(year):

    if not current_user.is_authenticated or not current_user.is_admin:
        return redirect(url_for('admin'))

    if not session.get('admin-filter-event'):
        session['admin-filter-event'] = '0'

    global admin_year

    admin_year = year

    previous_year = int(year)-1
    next_year = int(year)+1

    controls = {
        'previous': previous_year,
        'next': next_year
    }

    events = db.admin_events(year)

    if session.get('admin-filter-event') != '0':
        events = db.admin_filter_events(events, session.get('admin-filter-event'))

    event_dates = db.admin_arrange_events(events)[1]

    nums = []
    for n in event_dates.keys():
        nums.append(n)
        event_dates[n] = datetime.datetime.strptime(str(n), '%m').strftime("%B")

    events = db.admin_arrange_events(events)[0]

    pendings = db.admin_pendings()
    pendings = db.admin_arrange_pendings(pendings)

    edits = db.admin_edited_events()
    edits = db.admin_arrange_edited_events(edits)

    search = SearchEventForm()

    if search.validate_on_submit() and search.search_submit.data:
        print('search')
        return redirect(url_for('admin_search_event', keyword=search.keyword.data))

    category = CategoryEventForm(category=session.get('admin-filter-event'))
    category.category.choices = [('0', 'All Categories')]
    for c in db.categories():
        category.category.choices.append((c['id'], c['title']))

    if category.validate_on_submit() and category.category_submit.data:
        session['admin-filter-event'] = category.category.data
        return redirect(url_for('admin_event', year=year))

    return render_template('admin-event.html', year=year, controls=controls, events=events, pendings=pendings, edits=edits, nums=nums, event_dates=event_dates, search=search, category=category)


@app.route('/admin/events/search/<keyword>', methods=["GET", "POST"])
def admin_search_event(keyword):

    if not current_user.is_authenticated or not current_user.is_admin:
        return redirect(url_for('admin'))

    global admin_year

    events = db.admin_search_events(keyword)

    event_dates = db.admin_arrange_events(events)[1]

    nums = []
    keys = []
    for n in event_dates.keys():
        nums.append(n)
        event_dates[n] = datetime.datetime.strptime(str(n), '%m').strftime("%B")

    events = db.admin_arrange_events(events)[0]

    search = SearchEventForm(keyword=keyword)

    if search.validate_on_submit() and search.search_submit.data:
        print('search')
        return redirect(url_for('admin_search_event', keyword=search.keyword.data))


    return render_template('admin-search.html', events=events, nums=nums, event_dates=event_dates, search=search, year=admin_year)


@app.route('/admin/events/search/', methods=["GET", "POST"])
def admin_search_event2():

    if not current_user.is_authenticated or not current_user.is_admin:
        return redirect(url_for('admin'))

    return redirect(url_for('admin_events'))


@app.route('/admin/events/accept/<id>', methods=["GET", "POST"])
def admin_accept_event(id):

    if not current_user.is_authenticated or not current_user.is_admin:
        return redirect(url_for('admin'))

    result = db.admin_accept_event(id)

    if result == 1:

        event = db.event(id)

        email = event['contact_email']

        title = "Your event has been verified!"

        html = '''
                    <!DOCTYPE html>
                    <html lang="en-us">
                    <head>
                    <meta charset="utf-8">
                    <meta http-equiv="X-UA-Compatible" content="IE=edge">
                    <meta name="viewport" content="width=device-width, initial-scale=1, maximum-scale=1, user-scalable=0">
                    <link href="https://fonts.googleapis.com/css?family=Encode+Sans+Semi+Expanded:300,400,500,600,700" rel="stylesheet">
                    <title></title>
                    <style>
                    body { width: 100%; height: 100%; background: none; padding: 1rem; margin: 0;
                           font-size: 0.95rem; font-family: 'Encode Sans Semi Expanded', sans-serif; font-weight: 300;
                           color: #474747; text-align: center; line-height: 1.5; }
                    p { margin: 0; padding: 0; margin-bottom: 0.5rem; text-align: left; }
                    button {
                        font-size: 0.95rem; font-family: 'Encode Sans Semi Expanded', sans-serif; font-weight: 500;
                        width: auto; cursor: pointer; background: #fff;
                        border: 0.06rem solid #5f3bba; border-radius: 0.25rem; color: #5f3bba;
                        padding: 0.6rem 1rem; margin: 1rem auto; }
                    button:hover { background: #5f3bba; color: #fff; }
                    #frame { width: 100%; max-width: 450px; margin: 3rem auto; }
                    @media all and (max-width: 700px) and (min-width: 50px) {
                        #frame {
                            margin: 1rem;
                        }
                    }
                    #logo { width: 11rem; height: auto; margin: 0 auto; }
                    #dear { margin-top: 2.5rem; margin-bottom: 2.5rem; }
                    #end-message { margin-top: 2.5rem;}
                    #info { padding: 1.5rem; text-align: center; }
                    #note { margin-top: 2rem; color: #cecece; font-size: 0.8rem; }
                    </style>
                    </head><body><div id="frame">

                        <p id="dear">Dear ''' + event['contact_name'] + ''',</p>
                        <p>Your event is now on our website!<br>You can edit your event information anytime through the link below.<br>Please use the attached password to login.</p>
                    <div id="info">
                        <p>Event Password: <b>''' + event['password'] + '''</b></p>
                        <p><a href="https://dograntcounty.com/events/login"><button>Edit Event</button></a></p>
                    </div>
                    <p>Thanks again, for using our website.</p>
                        <p id="end-message">The Do Grant County Team</p>
                        <p id="note">Note: You will need to wait for our verification whenever you make changes to your event.</p>
                    </div></body></html>
                    '''

        msg = MIMEMultipart('alternative')
        msg['From'] = formataddr((str(Header('DoGrantCounty.com', 'utf-8')), 'contact@dograntcounty.com'))
        msg['To'] = email
        msg['Subject'] = title
        mt_html = MIMEText(html, 'html')
        msg.attach(mt_html)

        s = smtplib.SMTP("smtp.office365.com", 587)
        s.ehlo()
        s.starttls()
        s.login("contact@dograntcounty.com", "GC-Community-Events1!")
        s.sendmail("contact@dograntcounty.com", [email], msg.as_string())

        return redirect(url_for('admin_event', year=admin_year))

    return redirect(url_for('admin_error', code="accept"))


@app.route('/admin/events/delete/<id>', methods=["GET", "POST"])
def admin_delete_event(id):

    if not current_user.is_authenticated or not current_user.is_admin:
        return redirect(url_for('admin'))

    result = db.admin_delete_event(id)
    print(result)

    if result == 1:
        return redirect(url_for('admin_event', year=admin_year))

    return redirect(url_for('admin_error', code="delete"))


@app.route('/admin/events/accept/edit/<id>', methods=["GET", "POST"])
def admin_accept_edit(id):

    if not current_user.is_authenticated or not current_user.is_admin:
        return redirect(url_for('admin'))

    result = db.admin_accept_edit(id)

    if result == 1:
        return redirect(url_for('admin_event', year=admin_year))

    return redirect(url_for('admin_error', code="accept"))


@app.route('/admin/events/delete/edit/<id>', methods=["GET", "POST"])
def admin_delete_edit(id):

    if not current_user.is_authenticated or not current_user.is_admin:
        return redirect(url_for('admin'))

    result = db.admin_delete_edit(id)
    print(result)

    if result == 1:
        return redirect(url_for('admin_event', year=admin_year))

    return redirect(url_for('admin_error', code="delete"))


@app.route('/admin/events/edit/<id>', methods=["GET", "POST"])
def admin_edit_event(id):

    if not current_user.is_authenticated or not current_user.is_admin:
        return redirect(url_for('admin'))

    event = db.event(id)

    repeated = event['repeated']
    end_date = event['end_date']


    form = EditEventForm(title=event['title'],
                         organization=event['organization'],
                         description=event['description'],
                         start_date=datetime.datetime.strptime(event['start_date'], '%Y-%m-%d'),
                         end_date=datetime.datetime.strptime(event['end_date'], '%Y-%m-%d'),
                         start_time=datetime.datetime.strptime(event['start_time'], '%H:%M'),
                         end_time=datetime.datetime.strptime(event['end_time'], '%H:%M'),
                         repeated=event['repeated'],
                         cost=event['cost'],
                         contact_name=event['contact_name'],
                         contact_email=event['contact_email'],
                         contact_phone=event['contact_phone'],
                         location=event['location'],
                         url=event['url'],
                         photo=event['photo'],
                         old_photo=event['photo'])

    form.category.choices = [(i['id'], i['title']) for i in db.categories()]

    all_categories = db.categories()

    categories = []

    for c in db.event_categories(id):
        categories.append(str(c))

    if form.validate_on_submit():

        if form.replicate.data == '1':

            start_time = str(form.start_time.data)[:5]
            end_time = str(form.end_time.data)[:5]

            if re.match(r"(^[a-zA-Z0-9_.+-]+@[a-zA-Z0-9-]+\.[a-zA-Z0-9-.]+$)", form.contact_email.data):

                id, password = db.admin_add_event(form.title.data,
                                                  form.organization.data,
                                                  form.description.data,
                                                  form.start_date.data,
                                                  start_time,
                                                  form.end_date.data,
                                                  end_time,
                                                  form.repeated.data,
                                                  form.location.data,
                                                  form.category.data,
                                                  form.cost.data,
                                                  form.contact_name.data,
                                                  form.contact_email.data,
                                                  form.contact_phone.data,
                                                  form.url.data)

                if 'photo' in request.files:
                    file = request.files['photo']
                    print(file.filename)
                    name = ''
                    if file.filename != '':
                        # fix_orientation(file, save_over=False)
                        ext = file.filename.split('.')
                        name = db.random_string(12) + '.' + ext[-1]
                        f = os.path.join(app.config['UPLOAD_FOLDER'], name)
                        file.save(f)
                    if event['photo'] != '':
                        name = event['photo']
                    if form.old_photo.data == '-1':
                        name = ''

                    upload = db.upload_photo(id, name)

                    if upload != 1:
                        print('UPLOAD PHOTO FAILED')

                if password != 0:
                    flash('Event has been replicated.')
                else:
                    flash('Event Replicate failed.')

                return redirect(url_for('admin_events'))

            else:
                flash('Email is invalid.')

        else:

            start_time = str(form.start_time.data)[:5]
            end_time = str(form.end_time.data)[:5]

            result = db.admin_edit_event(id,
                                         form.title.data,
                                         form.organization.data,
                                         form.description.data,
                                         form.start_date.data,
                                         start_time,
                                         form.end_date.data,
                                         end_time,
                                         form.repeated.data,
                                         form.location.data,
                                         form.category.data,
                                         form.cost.data,
                                         form.contact_name.data,
                                         form.contact_email.data,
                                         form.contact_phone.data,
                                         form.url.data)

            if 'photo' in request.files:
                file = request.files['photo']
                print(file.filename)
                name = ''
                if file.filename != '':
                    #fix_orientation(file, save_over=False)
                    ext = file.filename.split('.')
                    name = db.random_string(12) + '.' + ext[-1]
                    f = os.path.join(app.config['UPLOAD_FOLDER'], name)
                    file.save(f)
                if event['photo'] != '':
                    name = event['photo']
                if form.old_photo.data == '-1':
                    name = ''

                upload = db.upload_photo(id, name)

                if upload != 1:
                    print('UPLOAD PHOTO FAILED')

            if result != 0:
                flash('Event has been edited.')
                return redirect(url_for('admin_events'))
            else:
                flash('Event Edit failed.')

    return render_template('admin-edit-event.html', form=form, id=id, categories=categories, all_categories=all_categories, year=admin_year, repeated=repeated, end_date=end_date)


@app.route('/admin/events/new', methods=["GET", "POST"])
def admin_new():

    today = datetime.datetime.today().strftime('%Y-%m-%d %H:%M:%S')
    start_time = '9:00'
    end_time = '10:00'

    form = NewEventForm(start_date=datetime.datetime.strptime(today, '%Y-%m-%d %H:%M:%S'),
                        end_date=datetime.datetime.strptime(today, '%Y-%m-%d %H:%M:%S'),
                        start_time=datetime.datetime.strptime(start_time, '%H:%M'),
                        end_time=datetime.datetime.strptime(end_time, '%H:%M'))
    form.category.choices = [(i['id'], i['title']) for i in db.categories()]

    if form.validate_on_submit():

        start_time = str(form.start_time.data)[:5]
        end_time = str(form.end_time.data)[:5]


        if re.match(r"(^[a-zA-Z0-9_.+-]+@[a-zA-Z0-9-]+\.[a-zA-Z0-9-.]+$)", form.contact_email.data):

            id, password = db.admin_add_event(form.title.data,
                                     form.organization.data,
                                     form.description.data,
                                     form.start_date.data,
                                     start_time,
                                     form.end_date.data,
                                     end_time,
                                     form.repeated.data,
                                     form.location.data,
                                     form.category.data,
                                     form.cost.data,
                                     form.contact_name.data,
                                     form.contact_email.data,
                                     form.contact_phone.data,
                                     form.url.data)

            if 'photo' in request.files:
                file = request.files['photo']
                print(file.filename)
                name = ''
                if file.filename != '':
                    #fix_orientation(file, save_over=False)
                    ext = file.filename.split('.')
                    name = db.random_string(12) + '.' + ext[-1]
                    f = os.path.join(app.config['UPLOAD_FOLDER'], name)
                    file.save(f)

                upload = db.upload_photo(id, name)

                if upload != 1:
                    print('UPLOAD PHOTO FAILED')

            if password != 0:
                flash('New event has been added.')
            else:
                flash('Event Create failed.')

            return redirect(url_for('admin_events'))

        else:
            flash('Email is invalid.')

    return render_template('admin-new.html', form=form, categories=db.categories())


@app.route('/admin/questions', methods=["GET", "POST"])
def admin_questions():

    if not current_user.is_authenticated or not current_user.is_admin:
        return redirect(url_for('admin'))

    questions = db.questions()
    questions = db.arrange_questions(questions)

    form = NewQuestionForm()

    if form.validate_on_submit():
        print(form.question.data)
        print(form.answer.data)

        result = db.admin_add_question(form.question.data, form.answer.data)

        if result == 1:
            flash('Question has been added.')
            return redirect(url_for('admin_questions'))
        else:
            flash('Question Create failed.')

    return render_template('admin-question.html', questions=questions, form=form)


@app.route('/admin/settings', methods=["GET", "POST"])
def admin_settings():

    if not current_user.is_authenticated or not current_user.is_admin:
        return redirect(url_for('admin'))

    setting = db.setting()

    about = AboutForm(about_title=setting['about_title'],about_content=setting['about_content'])

    faq = FaqForm(faq_title=setting['faq_title'],faq_content=setting['faq_content'])

    contact = ContactForm(contact_title=setting['contact_title'],contact_email=setting['contact_email'],contact_phone=setting['contact_phone'],contact_content=setting['contact_content'])

    if about.is_submitted() and about.about_submit.data:
        print('about')
        valid = True

        if about.about_title.data == "":
            flash('Title is required.')
            valid = False
        if about.about_content.data == "":
            flash('Content is required.')
            valid = False

        if valid:
            result = db.admin_update_about(about.about_title.data,
                                           about.about_content.data)

            if result == 1:
                flash('Updated About information.')
            else:
                flash('Update About failed.')

        return redirect(url_for('admin_settings'))

    if faq.is_submitted() and faq.faq_submit.data:
        print('faq')
        valid = True

        if faq.faq_title.data == "":
            flash('Title is required.')
            valid = False

        if valid:
            result = db.admin_update_faq(faq.faq_title.data,
                                         faq.faq_content.data)

            if result == 1:
                flash('Updated FAQ information.')
            else:
                flash('Update FAQ failed.')

        return redirect(url_for('admin_settings'))

    if contact.validate_on_submit() and contact.contact_submit.data:
        print('contact')
        valid = True

        if contact.contact_title.data == "":
            flash('Title is required.')
            valid = False
        if contact.contact_email.data == "":
            flash('Email is required.')
            valid = False
        if contact.contact_phone.data == "":
            flash('Phone is required.')
            valid = False

        if valid:

            result = db.admin_update_contact(contact.contact_title.data,
                                             contact.contact_content.data,
                                             contact.contact_email.data,
                                             contact.contact_phone.data)

            if result == 1:
                flash('Updated Contact information.')
            else:
                flash('Update Contact failed.')

        return redirect(url_for('admin_settings'))

    return render_template('admin-setting.html', about=about, contact=contact, faq=faq)


@app.route('/admin/error/<code>', methods=["GET", "POST"])
def admin_error(code):

    if not current_user.is_authenticated or not current_user.is_admin:
        return redirect(url_for('admin'))

    message = ""
    if code == "accept":
        message = "[Event Accept] failed."
    elif code == "delete":
        message = "[Event Delete] failed."
    elif code == "edit":
        message = "[Event Edit] failed."
    elif code == "add-category":
        message = "[Category Add] failed."
    elif code == "edit-category":
        message = "[Category Edit] failed."
    elif code == "delete-category":
        message = "[Category Delete] failed."
    elif code == "add-category":
        message = "[Question Add] failed."
    elif code == "edit-question":
        message = "[Question Edit] failed."
    elif code == "delete-question":
        message = "[Question Delete] failed."
    return render_template('admin-error.html', message=message)


@app.route('/admin/categories', methods=["GET", "POST"])
def admin_categories():

    if not current_user.is_authenticated or not current_user.is_admin:
        return redirect(url_for('admin'))

    categories = db.categories()
    categories = db.admin_arrange_categories(categories)

    form = NewCategoryForm()

    if form.validate_on_submit():
        print(form.title.data)

        result = db.admin_add_category(form.title.data)

        if result == 1:
            flash('Category has been added.')
            return redirect(url_for('admin_categories'))
        else:
            flash('Category Create failed.')

    return render_template('admin-category.html', categories=categories, form=form)


@app.route('/admin/categories/delete/<id>', methods=["GET", "POST"])
def admin_delete_category(id):

    if not current_user.is_authenticated or not current_user.is_admin:
        return redirect(url_for('admin'))

    result = db.admin_delete_category(id)

    if result == 1:
        flash('Category has been deleted.')
        return redirect(url_for('admin_categories'))
    else:
        flash('Category Delete failed.')

    return redirect(url_for('admin_error', code="delete-category"))


@app.route('/admin/categories/edit/<id>', methods=["GET", "POST"])
def admin_edit_category(id):

    if not current_user.is_authenticated or not current_user.is_admin:
        return redirect(url_for('admin'))

    category = db.category(id)

    form = NewCategoryForm(title=category['title'])

    if form.validate_on_submit():
        print(form.title.data)

        result = db.admin_edit_category(id, form.title.data)

        if result == 1:
            flash('Category has been edited.')
            return redirect(url_for('admin_categories'))
        else:
            flash('Category Edit failed.')

    return render_template('admin-edit-category.html', form=form, id=id)


@app.route('/admin/questions/delete/<id>', methods=["GET", "POST"])
def admin_delete_question(id):

    if not current_user.is_authenticated or not current_user.is_admin:
        return redirect(url_for('admin'))

    result = db.admin_delete_question(id)

    if result == 1:
        flash('Question has been deleted.')
        return redirect(url_for('admin_questions'))
    else:
        flash('Question Delete failed.')

    return redirect(url_for('admin_error', code="delete-question"))


@app.route('/admin/questions/edit/<id>', methods=["GET", "POST"])
def admin_edit_question(id):

    if not current_user.is_authenticated or not current_user.is_admin:
        return redirect(url_for('admin'))

    question = db.question(id)

    form = NewQuestionForm(question=question['question'],
                           answer=question['answer'])

    if form.validate_on_submit():
        print(form.question.data)
        print(form.answer.data)

        result = db.admin_edit_question(id, form.question.data, form.answer.data)

        if result == 1:
            flash('Question has been edited.')
            return redirect(url_for('admin_questions'))
        else:
            flash('Question Edit failed.')

    return render_template('admin-edit-question.html', form=form, id=id)


@app.route('/events/edit', methods=["GET", "POST"])
def edit_event():

    if not current_user.is_authenticated:
        return redirect(url_for('login'))

    if current_user.is_admin:
        return redirect(url_for('login'))

    event = db.event_password(current_user.id)

    print(event['id'])

    repeated = event['repeated']
    end_date = event['end_date']

    form = EditEventForm(title=event['title'],
                         organization=event['organization'],
                         description=event['description'],
                         start_date=datetime.datetime.strptime(event['start_date'], '%Y-%m-%d'),
                         end_date=datetime.datetime.strptime(event['end_date'], '%Y-%m-%d'),
                         start_time=datetime.datetime.strptime(event['start_time'], '%H:%M'),
                         end_time=datetime.datetime.strptime(event['end_time'], '%H:%M'),
                         repeated=event['repeated'],
                         cost=event['cost'],
                         contact_name=event['contact_name'],
                         contact_email=event['contact_email'],
                         contact_phone=event['contact_phone'],
                         location=event['location'],
                         url=event['url'],
                         photo=event['photo'],
                         old_photo=event['photo'])

    form.category.choices = [(i['id'], i['title']) for i in db.categories()]

    all_categories = db.categories()

    categories = []

    for c in db.event_categories(event['id']):
        categories.append(str(c))

    if form.validate_on_submit():

        if form.replicate.data == '1':

            start_time = str(form.start_time.data)[:5]
            end_time = str(form.end_time.data)[:5]

            if re.match(r"(^[a-zA-Z0-9_.+-]+@[a-zA-Z0-9-]+\.[a-zA-Z0-9-.]+$)", form.contact_email.data):

                id, password = db.add_event(form.title.data,
                                                  form.organization.data,
                                                  form.description.data,
                                                  form.start_date.data,
                                                  start_time,
                                                  form.end_date.data,
                                                  end_time,
                                                  form.repeated.data,
                                                  form.location.data,
                                                  form.category.data,
                                                  form.cost.data,
                                                  form.contact_name.data,
                                                  form.contact_email.data,
                                                  form.contact_phone.data,
                                                  form.url.data)

                if 'photo' in request.files:
                    file = request.files['photo']
                    print(file.filename)
                    name = ''
                    if file.filename != '':
                        # fix_orientation(file, save_over=False)
                        ext = file.filename.split('.')
                        name = db.random_string(12) + '.' + ext[-1]
                        f = os.path.join(app.config['UPLOAD_FOLDER'], name)
                        file.save(f)
                    if event['photo'] != '':
                        name = event['photo']
                    if form.old_photo.data == '-1':
                        name = ''

                    upload = db.upload_photo(id, name)

                    if upload != 1:
                        print('UPLOAD PHOTO FAILED')

                if password != 0:

                    s2 = smtplib.SMTP("smtp.office365.com", 587)
                    s2.ehlo()
                    s2.starttls()
                    s2.login("contact@dograntcounty.com", "GC-Community-Events1!")

                    # s2.sendmail("contact@dograntcounty.com", ["contact@dograntcounty.com"], msg2.as_string())

                    # Mail to User

                    title1 = "Thanks for creating an event!"

                    html1 = '<!DOCTYPE html><html lang="en-us"><head><meta charset="utf-8"><meta http-equiv="X-UA-Compatible" content="IE=edge"><meta name="viewport" content="width=device-width, initial-scale=1, maximum-scale=1, user-scalable=0"><link href="https://fonts.googleapis.com/css?family=Encode+Sans+Semi+Expanded:300,400,500,600,700" rel="stylesheet"><title></title><style>' \
                            + 'body { width: 100%; height: 100%; background: none; padding: 1rem; margin: 0; font-size: 0.95rem; font-family: "Encode Sans Semi Expanded", sans-serif; font-weight: 300; color: #474747; text-align: center; line-height: 1.5; } p { margin: 0; padding: 0; margin-bottom: 0.5rem; text-align: left; }' \
                            + 'a { font-size: inherit; font-weight: inherit; color: #5f3bba; text-decoration: none; } a:hover { color: #5f3bba; } button { font-size: 0.95rem; font-family: "Encode Sans Semi Expanded", sans-serif; font-weight: 500; width: auto; cursor: pointer; background: #fff; border: 0.06rem solid #5f3bba; border-radius: 0.25rem; color: #5f3bba; padding: 0.6rem 1rem; margin: 1rem auto; } button:hover { background: #5f3bba; color: #fff; } #frame { width: 100%; max-width: 450px; margin: 3rem auto; } #logo { width: 11rem; height: auto; margin: 0 auto; } #dear { margin-top: 2.5rem; margin-bottom: 2.5rem; } #end-message { margin-top: 2.5rem;} #info { padding: 1.5rem; text-align: center; } #note { margin-top: 2rem; color: #cecece; font-size: 0.8rem; } @media all and (min-width: 700px) {#frame {margin: 1rem;}}' \
                            + '</style></head><body><div id="frame">' \
                            + '<p id="dear">Dear ' + str(
                        form.contact_name.data) + ',</p><p>Thank you for adding an event to DoGrantCounty!<br>Our administrative team will review your event details before publishing to ensure it follows our event guidelines. We will do our best to post your event within 2-3 business days. Do not forget to share <a href="https://www.dograntcounty.com">www.DoGrantCounty.com</a> and your event on social media.<br>Thanks again, for using DoGrantCounty to promote the good things happening in Grant County, Indiana!</p>' \
                            + '<p id="end-message">The Do Grant County Team</p><p id="note"></p></div></body></html>'

                    msg1 = MIMEMultipart('alternative')
                    msg1['From'] = formataddr((str(Header('DoGrantCounty.com', 'utf-8')), 'contact@dograntcounty.com'))
                    msg1['To'] = form.contact_email.data
                    msg1['Subject'] = title1
                    mt_html1 = MIMEText(html1, 'html')
                    msg1.attach(mt_html1)

                    s2.sendmail("contact@dograntcounty.com", [str(form.contact_email.data)], msg1.as_string())
                    s2.quit()

                    return redirect(url_for('edit_result', code="replicate"))
                else:
                    return redirect(url_for('edit_result', code="failure"))

            else:
                flash('Email is invalid.')

        else:

            start_time = str(form.start_time.data)[:5]
            end_time = str(form.end_time.data)[:5]

            photo = ''

            if 'photo' in request.files:
                file = request.files['photo']
                print(file.filename)
                if file.filename != '':
                    #fix_orientation(file, save_over=False)
                    ext = file.filename.split('.')
                    photo = db.random_string(12) + '.' + ext[-1]
                    f = os.path.join(app.config['UPLOAD_FOLDER'], photo)
                    file.save(f)
                if event['photo'] != '':
                    photo = event['photo']
                if form.old_photo.data == '-1':
                    photo = ''

            result = db.edit_event(event['id'],
                                         form.title.data,
                                         form.organization.data,
                                         form.description.data,
                                         form.start_date.data,
                                         start_time,
                                         form.end_date.data,
                                         end_time,
                                         form.repeated.data,
                                         form.location.data,
                                         form.category.data,
                                         form.cost.data,
                                         form.contact_name.data,
                                         form.contact_email.data,
                                         form.contact_phone.data,
                                         form.url.data,
                                         photo)

            if result == 1:
                return redirect(url_for('edit_result', code="success"))
            else:
                return redirect(url_for('edit_result', code="failure"))

    return render_template('edit-event.html', form=form, id=event['id'], categories=categories, all_categories=all_categories, repeated=repeated, end_date=end_date)


@app.route('/events/login', methods=["GET", "POST"])
def login():

    form = UserLoginForm()

    if form.validate_on_submit():
        print(form.password.data)

        for e in db.all_events():
            if form.password.data == e['password']:
                user = User(form.password.data)
                login_user(user)
                return redirect(url_for('edit_event'))
        flash('This password is not available.')

    return render_template('login.html', form=form)


@app.route('/events/edit/<code>', methods=["GET", "POST"])
def edit_result(code):

    if not current_user.is_authenticated:
        return redirect(url_for('login'))

    message = ""
    if code == "success":
        message = "Event has been edited.\r\nEvent information will be changed when the administrator verifies it."
    elif code == "failure":
        message = "Error occurred."
    elif code == "delete":
        message = "Event has been deleted.\r\nThank you for using our website."
    elif code == "replicate":
        message = "Event has been replicated.\r\nThank you for using our website."

    return render_template('error.html', message=message)


@app.route('/events/delete/<id>', methods=["GET", "POST"])
def delete_event(id):

    if not current_user.is_authenticated or id != db.event_id(current_user.id):
        return redirect(url_for('login'))

    result = db.admin_delete_event(id)

    if result == 1:
        return redirect(url_for('edit_result', code="delete"))

    return redirect(url_for('edit_result', code="failure"))



if __name__ == '__main__':
    app.run()
