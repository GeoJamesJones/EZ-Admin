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
    orgChoices = [('AFRICOM', 'AFRICOM'), ('CENTCOM', 'CENTCOM'),
                  ('EUCOM', 'EUCOM'), ('PACOM', 'PACOM')]
    organization = SelectField(u'Organization', choices=orgChoices)
    licenseChoices = [('Yes', 'Yes'), ('No', 'No')]
    licensepro = SelectField(u'License ArcGIS Pro?', choices=licenseChoices)
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
