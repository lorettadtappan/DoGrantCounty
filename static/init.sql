
/*
INSERT INTO event (id, title, organization, description, location, start_date, start_time, end_date, end_time, cost, contact_name, contact_email, contact_phone, url, password, verified)
    VALUES ('i3iglpksli24', 'Airband','Taylor University', 'Dude, I have a description', '236 W Reade Ave, Upland', '2018-02-01', '9:00', '2018-02-01', '17:00', 1500, 'Taylor Univ', 'taylor@taylor.edu', '765-567-7657', 'www.taylor.edu', '0000', 1);
INSERT INTO event (id, title, organization, description, location, start_date, start_time, end_date, end_time, cost, contact_name, contact_email, contact_phone, url, password, verified, has_photo)
    VALUES ('i3iglaksli24', 'Free Coffee Day','Starbucks', 'Today is our Free Coffee Day! Bring your friends, and enjoy your Monday.', '524 N Coffee Ave, Upland', '2018-02-05', '7:00', '2018-02-05', '19:00', 0, 'Starbucks Manager', 'help@starbucks.com', '765-567-7657', 'www.starbucks.com', '0000', 1, 1);
INSERT INTO event (id, title, organization, description, location, start_date, start_time, end_date, end_time, cost, contact_name, contact_email, contact_phone, url, password, verified)
    VALUES ('i3iglaasli24', 'Baloon Party','Good Kids', 'Dude, I have a description', '25 S Baloon Ave, Marion', '2018-02-01', '13:00', '2018-02-01', '14:00', 0, 'Taylor Univ', 'taylor@taylor.edu', '765-567-7657', 'www.taylor.edu', '0000', 1);
INSERT INTO event (id, title, organization, description, location, start_date, start_time, end_date, end_time, cost, contact_name, contact_email, contact_phone, url, password, verified)
    VALUES ('i3ibbpksli24', 'Free Movie: The Avengers III','Marvel', 'Dude, I have a description', '5212 Marvel St, Gas City', '2018-02-07', '14:00', '2018-02-07', '17:00', 0, 'Taylor Univ', 'taylor@taylor.edu', '765-567-7657', 'www.taylor.edu', '0000', 1);
INSERT INTO event (id, title, organization, description, location, start_date, start_time, end_date, end_time, cost, contact_name, contact_email, contact_phone, url, password, verified)
    VALUES ('i3iglccsli24', 'Free Donuts','Taylor University', 'Dude, I have a description', '236 W Reade Ave, Upland', '2018-02-22', '11:00', '2018-02-23', '13:00', 0, 'Taylor Univ', 'taylor@taylor.edu', '765-567-7657', 'www.taylor.edu', '0000', 1);
INSERT INTO event (id, title, organization, description, location, start_date, start_time, end_date, end_time, cost, contact_name, contact_email, contact_phone, url, password, verified)
    VALUES ('iddglpksli24', 'How to Make Cookies?','Cookie Factory', 'Learn how to make cookies with us! It is so much fun.', '142 Cookie St, Marion', '2018-02-22', '9:00', '2018-02-22', '12:00', 1000, 'Taylor Univ', 'taylor@taylor.edu', '765-567-7657', 'www.taylor.edu', '0000', 1);
INSERT INTO event (id, title, organization, description, location, start_date, start_time, end_date, end_time, cost, contact_name, contact_email, contact_phone, url, password, verified)
    VALUES ('i3iglpksaa24', 'Free Movie: Iron Man II','Marvel', 'Dude, I have a description', '5212 Marvel St, Gas City', '2018-02-10', '14:00', '2018-02-10', '17:00', 0, 'Taylor Univ', 'taylor@taylor.edu', '765-567-7657', 'www.taylor.edu', '0000', 1);
INSERT INTO event (id, title, organization, location, start_date, start_time, end_date, end_time, cost, contact_name, contact_email, contact_phone, url, password, verified)
    VALUES ('i3iglpksli25', 'Good Event','Taylor University', '236 W Reade Ave, Upland', '2018-02-07', '13:00', '2018-02-07', '15:00', 0, 'Admin', 'admin@taylor.edu', '765-567-7657', 'www.taylor.edu', '0000', 1);
INSERT INTO event (id, title, organization, description, location, start_date, start_time, end_date, end_time, cost, contact_name, contact_email, contact_phone, url, password, verified)
    VALUES ('i3iglpksli26', 'Dance Party','The Boys', 'This is a description.', '523 Dancing St, Upland', '2018-03-03', '9:00', '2018-03-07', '17:00', 600, 'Admin', 'admin@event.com', '765-567-7657', 'www.theboys.com', '0000', 1);
INSERT INTO event (id, title, organization, location, start_date, start_time, end_date, end_time, cost, contact_name, contact_email, contact_phone, url, password, verified)
    VALUES ('i3iglpksli27', 'Fruit Party','Taylor University','524 Fruit Ave, Upland','2018-03-02', '9:00', '2018-03-10', '17:00', 500, 'Fruit Lover', 'fruit@fruit.edu', '765-567-7657', 'www.fruits.com', '0000', 1);
INSERT INTO event (id, title, organization, location, start_date, start_time, end_date, end_time, cost, contact_name, contact_email, contact_phone, url, password)
    VALUES ('i3iglpksli28', 'Play with Dogs!','Dog Care','11 Doglover St, Gas City','2018-02-22', '11:00', '2018-02-25', '14:00', 1000, 'Dog Manager', 'manage@dogs.com', '765-567-7657', 'www.dogs.com', '0000');

*/

INSERT INTO category (id, title)
    VALUES ('i3iglpksai28', 'Family');
INSERT INTO category (id, title)
    VALUES ('i3iglbksai28', 'Kids');
INSERT INTO category (id, title)
    VALUES ('i3iglpasai28', 'Elders');

/*

INSERT INTO event_category (event_id, category_id)
    VALUES ('i3iglpksli24', 'i3iglpksai28');
INSERT INTO event_category (event_id, category_id)
    VALUES ('i3iglpksli24', 'i3iglpasai28');
INSERT INTO event_category (event_id, category_id)
    VALUES ('i3iglpksli27', 'i3iglpksai28');
INSERT INTO event_category (event_id, category_id)
    VALUES ('i3iglpksli28', 'i3iglbksai28');

*/


INSERT INTO faq (id, question, answer)
    VALUES ('aasieodlck12', 'How can I add new events?', 'In order to add a new event, simply click ont the "Add Event" button on the top right corner above events. Once you fill out all the event information, the administrators will verify your event and will soon be displayed on the website.');
INSERT INTO faq (id, question, answer)
    VALUES ('aasie3dlck12', 'How can I contact the event host?', 'In the event details, you can find the phone number of the event host. You can also go to the related website to get even more detailed information.');
INSERT INTO faq (id, question, answer)
    VALUES ('aasieod6ck12', 'Who is organizing all these events?', 'I am.');
INSERT INTO faq (id, question, answer)
    VALUES ('aasieodack12', 'Why are you handsome?', 'God made me handsome.');



INSERT INTO setting (id, about_title, about_content, faq_title, faq_content, contact_title, contact_email, contact_phone, contact_content)
    VALUES ('dograntcounty', 'FIND AND SUBMIT
EVENTS THAT ARE HAPPENING WITH GRANT COUNTY, INDIANA-BASED ORGANIZATIONS',
            'Do! Grant County is a website developed to bring active relations between residents. By providing platform for users to freely find and submit events, we are aiming to increase the opportunity of interaction of fantastic and great events. Grant County currently has over average of 100 events that are happening every months, and we want this events to be known and be available to all residents and visitors.',
            'QUESTIONS YOU MIGHT ASK',
            'example content',
            'FOR MORE INFORMATION',
            'contact@dograntcounty.com',
            '123-123-1234',
            'example content');
