from app import app
import unittest

class appClientTests(unittest.TestCase):

     ###Test all routes when signed out
     def test_index(self):
         tester = app.test_client(self)
         response = tester.get('/', content_type='html/text')

         #we need to check that the client gets the login page when using "/"
         #expecting an OK
         self.assertEqual(response.status_code, 200)

     def test_login(self):
         tester = app.test_client(self)
         response = tester.get('/login', content_type='html/text')
        
         #we need to check that the client gets the login page when using "/login" with out "/" at end
         #expecting a permanent redirect
         self.assertEqual(response.status_code, 308)

     def test_login_slash(self):
         tester = app.test_client(self)
         response = tester.get('/login/', content_type='html/text')
        
         #we need to check that the client gets the login page when using "/login/"
         #expecting an OK
         self.assertEqual(response.status_code, 200)

     def test_home(self):
         tester = app.test_client(self)
         response = tester.get('/home/', content_type='html/text')
        
         #we need to check that the client is redirected to the login page when not signed in
         #expecting to find requested page (home) but redirect client
         self.assertEqual(response.status_code, 302)

     def test_home_redirect(self):
         tester = app.test_client(self)
         response = tester.get('/home/', follow_redirects=True)
        
         #we need to check that the client is redirected to the login page when not signed in
         #expecting to find "'Please log in to access this page." on the login page
         self.assertTrue(b'Please log in to access this page.' in response.data)
    
     def test_new(self):
         tester = app.test_client(self)
         response = tester.get('/new/', content_type='html/text')
        
         #we need to check that the client is redirected to the login page when not signed in
         #expecting to find requested page (add new) but redirect client
         self.assertEqual(response.status_code, 302)

     def test_new_redirect(self):
         tester = app.test_client(self)
         response = tester.get('/new/', follow_redirects=True)
        
         #we need to check that the client is redirected to the login page when not signed in
         #expecting to find "'Please log in to access this page." on the login page
         self.assertTrue(b'Please log in to access this page.' in response.data)

     def test_update_task(self):
         tester = app.test_client(self)
         response = tester.get('/update/1', content_type='html/text')
        
         #we need to check that the client is redirected to the login page when not signed in
         #expecting to find requested page (update) but redirect client
         self.assertEqual(response.status_code, 302)

     def test_update_redirect(self):
         tester = app.test_client(self)
         response = tester.get('/update/', follow_redirects=True)
        
         #we need to check that the client is redirected to the login page when not signed in
         #expecting to find "'Please log in to access this page." on the login page
         self.assertTrue(b'Page Not Found!' in response.data)

     def test_logout(self):
         tester = app.test_client(self)
         response = tester.get('/logout/', content_type='html/text')
        
         #we need to check that the client is redirected to the login page when not signed in
         #expecting to find redirect for client
         self.assertEqual(response.status_code, 302)

     ###Test pages render when signed out
     def test_login_page_renders(self):
         tester = app.test_client(self)
         response = tester.get('/login/', content_type='html/text')
         #we need to check that the client gets the right page rendered
         #expecting to find word "login" on the login page
         self.assertTrue(b'login' in response.data)

     def test_signup_page_renders(self):
         tester = app.test_client(self)
         response = tester.get('/signup/', content_type='html/text')
         #we need to check that the client gets the right page rendered
         #expecting to find word "signup" on the signup page
         self.assertTrue(b'signup' in response.data)

     ###Test correct login behavior when proper credentials
     def test_sign_up_works(self):
         tester = app.test_client(self)
         response = tester.post('/signup/', 
                        data=dict(username='admin', 
                        email='admin@admin.com', 
                        password='admin'), 
                        follow_redirects=True
                        )
         #we need to check that the client gets redirected to login page
         #expecting OK
         self.assertEqual(response.status_code, 200)

     def test_login_page_correct_behavior_(self):
         tester = app.test_client(self)
         response = tester.post('/login/', 
                                 data=dict( 
                                 email='admin@admin.com', 
                                 password='admin'), 
                                 follow_redirects=True
                                 )
         #we need to check that the client gets logged into home page
         #expecting to find word "admin" on the home page
         self.assertTrue(b'admin' in response.data)

     ###Test correct login behavior when improper credentials
     def test_login_page_correct_behavior_wrong_password(self):
         tester = app.test_client(self)
         response = tester.post('/login/', 
                                 data=dict(username='admin', 
                                 email='admin@admin.com', 
                                 password='notadmin'), 
                                 follow_redirects=True
                                 )
         #we need to check that the client doesnt get logged into home page
         #expecting to find word "login" on the login page
         self.assertTrue(b'login' in response.data) 


#### I tried implementing database tests using information from this site:
# https://pythonhosted.org/Flask-Testing/ and https://flask-testing.readthedocs.io/en/v0.4/
# but kept getting this error: Please make sure to call init_app() first.
# debugging with information from:
# https://stackoverflow.com/questions/30764073/sqlalchemy-extension-isnt-registered-when-running-app-with-gunicorn
# was not helpful.
# I even tried adding db.init_app(app) in app.py as per this resource:
# https://github.com/GoogleCloudPlatform/functions-framework-python/issues/24
# but that didn't work too. I'm leaving the initial code here hoping you can spot the issue.

# from flask import Flask
# from flask_testing import TestCase
# from app import app, db, Users, Tasks
# import unittest

# class MyTest(TestCase):

#     SQLALCHEMY_DATABASE_URI = "sqlite://"
#     TESTING = True

#     def create_app(self):
#         app = Flask(__name__)
#         app.config['TESTING'] = True
#         return app

#     def setUp(self):
#         db.create_all()

#     def tearDown(self):
#         db.session.remove()
#         db.drop_all()
        
#     def test_user(self):
#         user = Users(user='test',password='password',email='test@test.com')
#         db.session.add(user)
#         db.session.commit()
#         assert(user in db.session)

#     def test_task(self):
#         user = Users(user='test',password='password',email='test@test.com')
#         db.session.add(user)
#         db.session.commit()

#         if user in db.session:
#             task = Tasks(types='doing', title='i am a title', description='i am a description', task_owner=user)
#             db.session.add(task)
#             db.session.commit()

#         assert(task in db.session)



if __name__ == '__main__':
    unittest.main()
