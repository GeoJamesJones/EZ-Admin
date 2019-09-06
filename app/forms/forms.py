from flask import request
from flask_wtf import FlaskForm
from flask_uploads import UploadSet
from flask_wtf.file import FileField, FileAllowed, FileRequired
from wtforms import StringField, PasswordField, BooleanField, SubmitField, TextAreaField, SelectField, DecimalField, IntegerField
from wtforms.validators import ValidationError, DataRequired, Email, EqualTo, Length
from app.models.models import User

from app import app

# These classes represent simplified forms that were created using the WTForms package.
# This allows for more simple templating of the application and most processes to leverage
# the "simple_form.html" file to render when a GET Request is called.


class LoginForm(FlaskForm):
    username = StringField('Username', validators=[DataRequired()])
    password = PasswordField('Password', validators=[DataRequired()])
    remember_me = BooleanField('Remember Me')
    submit = SubmitField('Sign In')

class RegistrationForm(FlaskForm):
    username = StringField('Username', validators=[DataRequired()])
    email = StringField('Email', validators=[DataRequired(), Email()])
    password = PasswordField('Password', validators=[DataRequired()])
    password2 = PasswordField(
        'Repeat Password', validators=[DataRequired(), EqualTo('password')])
    submit = SubmitField('Register')

    def validate_username(self, username):
        user = User.query.filter_by(username=username.data).first()
        if user is not None:
            raise ValidationError('Please use a different username.')

    def validate_email(self, email):
        user = User.query.filter_by(email=email.data).first()
        if user is not None:
            raise ValidationError('Please use a different email address.')


class UploadForm(FlaskForm):
    upload = FileField('Document', validators=[
        FileRequired()
    ])
    submit = SubmitField('Upload File')


class UploadShapes(FlaskForm):
    upload = FileField('ZIP File: ', validators=[
        FileRequired()
    ])
    myChoices = [('Shapefile', 'Shapefile'), ('Elevation', 'Elevation Data')]
    datatype = SelectField(u'Field name', choices=myChoices)
    submit = SubmitField('Upload File')


class UploadImagery(FlaskForm):
    upload = FileField('ZIP File: ', validators=[
        FileRequired()
    ])
    myChoices = [('cadrg', 'CADRG/ECRG'),
                 ('cib', 'CIB'), ('imagery', 'Imagery')]
    datatype = SelectField(u'Field name', choices=myChoices)
    submit = SubmitField('Upload File')

class GetBrokenLinks(FlaskForm):
    submit = SubmitField('Submit')

class AddPortalUser(FlaskForm):
    firstname = StringField('First Name', validators=[DataRequired()])
    lastname = StringField('Last Name', validators=[DataRequired()])
    username = StringField('Username', validators=[DataRequired()])
    password = PasswordField('Password', validators=[DataRequired()])
    password2 = PasswordField(
        'Repeat Password', validators=[DataRequired(), EqualTo('password')])
    email = StringField('Email', validators=[DataRequired(), Email()])
    roleChoices = [('org_admin', 'Administrator'),
                   ('org_publisher', 'Publisher'),
                   ('org_user', 'User')]
    role = SelectField(u'Role', choices=roleChoices)
    orgChoices = [('SWCS 3rd BN', 'SWCS 3rd BN'), 
                    ('USACAPOC HQ', 'USACAPOC HQ'), 
                    ('350 CACOM', '350 CACOM'), 
                    ('321 BDE ', '321 BDE '), 
                    ('451 BN', '451 BN'), 
                    ('490 BN', '490 BN'), 
                    ('413 BN', '413 BN'), 
                    ('410 BN', '410 BN'), 
                    ('402 BN', '402 BN'), 
                    ('478 BN', '478 BN'), 
                    ('486 BN', '486 BN'), 
                    ('436 BN', '436 BN'), 
                    ('351 CACOM', '351 CACOM'), 
                    ('364 BDE', '364 BDE'), 
                    ('405 BN', '405 BN'), 
                    ('445 BN', '445 BN'), 
                    ('448 BN', '448 BN'), 
                    ('440 BN', '440 BN'), 
                    ('358 BDE', '358 BDE'), 
                    ('416 BN', '416 BN'), 
                    ('425 BN', '425 BN'), 
                    ('492 BN', '492 BN'), 
                    ('426 BN', '426 BN'), 
                    ('352 CACOM', '352 CACOM'), 
                    ('354 BDE', '354 BDE'), 
                    ('401 BN', '401 BN'), 
                    ('414 BN', '414 BN'), 
                    ('422 BN', '422 BN'), 
                    ('437 BN', '437 BN'), 
                    ('360 BDE', '360 BDE'), 
                    ('412 BN ', '412 BN '), 
                    ('431 BN', '431 BN'), 
                    ('450 BN', '450 BN'), 
                    ('489 BN', '489 BN'), 
                    ('353 CACOM', '353 CACOM'), 
                    ('304 BDE', '304 BDE'), 
                    ('403 BN', '403 BN'), 
                    ('404 BN', '404 BN'), 
                    ('411 BN', '411 BN'), 
                    ('443 BN', '443 BN'), 
                    ('308 BDE', '308 BDE'), 
                    ('407 BN ', '407 BN '), 
                    ('415 BN', '415 BN'), 
                    ('418 BN', '418 BN'), 
                    ('432 BN', '432 BN'), 
                    ('361 BDE', '361 BDE'), 
                    ('322 BDE', '322 BDE'), 
                    ('95 BDE', '95 BDE'), 
                    ('91 BN', '91 BN'), 
                    ('92 BN', '92 BN'), 
                    ('96 BN', '96 BN'), 
                    ('97 BN', '97 BN'), 
                    ('98 BN', '98 BN'), 
                    ('83 BN', '83 BN'), 
                    ('83rd: A CO', '83rd: A CO'), 
                    ('83rd: B CO', '83rd: B CO'), 
                    ('83rd: C CO', '83rd: C CO'), 
                    ('83rd: D CO', '83rd: D CO'), 
                    ('83rd: E CO', '83rd: E CO'), 
                    ('83rd: F CO', '83rd: F CO'), 
                    ('G9 AFRICOM', 'G9 AFRICOM'), 
                    ('G9 CENTCOM', 'G9 CENTCOM'), 
                    ('G9 EUCOM', 'G9 EUCOM'), 
                    ('G9 INDOPACOM', 'G9 INDOPACOM'), 
                    ('G9 NORTHCOM', 'G9 NORTHCOM'), 
                    ('G9 SOUTHCOM', 'G9 SOUTHCOM'), 
                    ('18th (A) CORPS G9', '18th (A) CORPS G9'), 
                    ('3rd CORPS G9', '3rd CORPS G9'), 
                    ('1st CORPS G9', '1st CORPS G9'), 
                    ('82nd ABN  DIV G9', '82nd ABN  DIV G9'), 
                    ('101st AASLT DIV G9', '101st AASLT DIV G9'), 
                    ('10th MTN DIV G9', '10th MTN DIV G9'), 
                    ('25th INF DIV G9', '25th INF DIV G9'), 
                    ('4th ID DIV G9', '4th ID DIV G9'), 
                    ('3rd ID DIV G9', '3rd ID DIV G9'), 
                    ('1st ID DIV G9 ', '1st ID DIV G9 '), 
                    ('1st Armored DIV G9', '1st Armored DIV G9'), 
                    ('1st Cavalry DIV G9 ', '1st Cavalry DIV G9 '), 
                    ('TCAPT AFRICOM', 'TCAPT AFRICOM'), 
                    ('TCAPT CENTCOM', 'TCAPT CENTCOM'), 
                    ('TCAPT EUCOM', 'TCAPT EUCOM'), 
                    ('TCAPT INDOPACOM', 'TCAPT INDOPACOM'), 
                    ('TCAPT NORTHCOM', 'TCAPT NORTHCOM'), 
                    ('TCAPT SOUTHCOM', 'TCAPT SOUTHCOM'), 
                    ('Alabama', 'Alabama'), 
                    ('Alaska', 'Alaska'), 
                    ('Arizona', 'Arizona'), 
                    ('Arkansas', 'Arkansas'), 
                    ('California', 'California'), 
                    ('Colorado', 'Colorado'), 
                    ('Connecticut', 'Connecticut'), 
                    ('Delaware', 'Delaware'), 
                    ('District of Columbia', 'District of Columbia'), 
                    ('Florida', 'Florida'), 
                    ('Georgia', 'Georgia'), 
                    ('Guam', 'Guam'), 
                    ('Hawaii', 'Hawaii'), 
                    ('Idaho', 'Idaho'), 
                    ('Illinois', 'Illinois'), 
                    ('Indiana', 'Indiana'), 
                    ('Iowa', 'Iowa'), 
                    ('Kansas', 'Kansas'), 
                    ('Kentucky', 'Kentucky'), 
                    ('Louisiana', 'Louisiana'), 
                    ('Maine', 'Maine'), 
                    ('Maryland', 'Maryland'), 
                    ('Massachusetts', 'Massachusetts'), 
                    ('Michigan', 'Michigan'), 
                    ('Minnesota', 'Minnesota'), 
                    ('Mississippi', 'Mississippi'), 
                    ('Missouri', 'Missouri'), 
                    ('Montana', 'Montana'), 
                    ('Nebraska', 'Nebraska'), 
                    ('Nevada', 'Nevada'), 
                    ('New Hampshire', 'New Hampshire'), 
                    ('New Jersey', 'New Jersey'), 
                    ('New Mexico ', 'New Mexico '), 
                    ('New York', 'New York'), 
                    ('North Carolina', 'North Carolina'), 
                    ('North Dakota', 'North Dakota'), 
                    ('Ohio ', 'Ohio '), 
                    ('Oklahoma', 'Oklahoma'), 
                    ('Oregon', 'Oregon'), 
                    ('Pennsylvania', 'Pennsylvania'), 
                    ('Puerto Rico', 'Puerto Rico'), 
                    ('Rhode Island', 'Rhode Island'), 
                    ('South Carolina', 'South Carolina'), 
                    ('South Dakota', 'South Dakota'), 
                    ('Tennessee', 'Tennessee'), 
                    ('Texas', 'Texas'), 
                    ('Utah', 'Utah'), 
                    ('Vermont', 'Vermont'), 
                    ('Virgin Islands', 'Virgin Islands'), 
                    ('Virginia', 'Virginia'), 
                    ('Washington', 'Washington'), 
                    ('West Virginia', 'West Virginia'), 
                    ('Wisconsin', 'Wisconsin'), 
                    ('Wyoming', 'Wyoming'), 
                    ('Farm Bureau', 'Farm Bureau'), 
                    ('Hudson Valley Agribusiness Development Corp', 'Hudson Valley Agribusiness Development Corp'), 
                    ('Ukraine', 'Ukraine')]
    organization = SelectField(u'Organization', choices=orgChoices)
    licenseChoices = [('Yes', 'Yes'), ('No', 'No')]
    submit = SubmitField('Submit')

class UploadCMB(FlaskForm):
    upload = FileField('CMB ZIP File', validators=[
        FileRequired()
    ])
    submit = SubmitField('Upload File')

class QueryWeb(FlaskForm):
    query = StringField('Query Keywords', validators=[DataRequired()])
    choices = [
        ('Warehouse/Storage Facility', 'Warehouses'),
        ('Commercial Food Distribution Center',
         'Commercial Food Distribution Center'),
        ('Farm/Ranch', 'Farms or Ranches'),
        ('Food Distribution Center', 'Food Distribution Center'),
        ('Food Production Center', 'Food Production Center'),
        ('Food Retail', 'Food Retail'),
        ('Food Retail', 'Grain Storage'),
        ('Generation Station', 'Generation Station'),
        ('Natural Gas Facility', 'Natural Gas Facility'),
        ('Petroleum Facility', 'Petroleum Facility'),
        ('Propane Facility', 'Propane Facility'),
        ('Government Site Infrastructure', 'Government Site Infrastructure'),
        ('Medical Treatment Facility (Hospital)', 'Hospitals'),
        ('Civilian Television', 'Television Stations')
    ]
    category = SelectField(u'Category', choices=choices)
    submit = SubmitField('Submit')

class QueryNews(FlaskForm):
    query = StringField('Query Keywords', validators=[DataRequired()])
    submit = SubmitField('Submit')

class DetectFaces(FlaskForm):
    upload = FileField('Image File:', validators=[
        FileRequired()
    ])
    lat = DecimalField("Latitude", places=12)
    lon = DecimalField("Longitude", places=12)
    submit = SubmitField('Submit')


class SimulateNetOwl(FlaskForm):
    myChoices = [(app.config['INVESTIGATION_REPORTS'], 'Investigation Reports'),
                 (app.config['EARLY_BIRD'], 'News Articles')]
    datatype = SelectField(u'Data Type', choices=myChoices)
    submit = SubmitField('Start')

class SearchForm(FlaskForm):
    q = StringField('Search', validators=[DataRequired()])

    def __init__(self, *args, **kwargs):
        if 'formdata' not in kwargs:
            kwargs['formdata'] = request.args
        if 'csrf_enabled' not in kwargs:
            kwargs['csrf_enabled'] = False
        super(SearchForm, self).__init__(*args, **kwargs)

class ChangeUserPortal(FlaskForm):
    portal_name = StringField('Portal Name', validators=[DataRequired()])
    portal_url = StringField('Portal URL', validators=[DataRequired()])
    username = StringField('Username', validators=[DataRequired()])
    password = PasswordField('Password', validators=[DataRequired()])
    password2 = PasswordField(
        'Repeat Password', validators=[DataRequired(), EqualTo('password')])
    login_to_portal = BooleanField(
        'Login to Portal for ArcGIS / ArcGIS Online?')
    submit = SubmitField('Submit')
