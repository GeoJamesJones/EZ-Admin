from flask import request
from flask_wtf import FlaskForm
from flask_uploads import UploadSet
from flask_wtf.file import FileField, FileAllowed, FileRequired
from wtforms import StringField, PasswordField, BooleanField, SubmitField, TextAreaField, SelectField, DecimalField, IntegerField
from wtforms.validators import ValidationError, DataRequired, Email, EqualTo, Length
from app.models.models import User

from app import app

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
    myChoices = [('cadrg', 'CADRG/ECRG'), ('cib', 'CIB'), ('imagery', 'Imagery')]
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
    orgChoices = [('AFRICOM', 'AFRICOM'),('CENTCOM', 'CENTCOM'),('EUCOM', 'EUCOM'),('PACOM', 'PACOM')]
    organization = SelectField(u'Organization', choices=orgChoices)
    licenseChoices = [('Yes', 'Yes'),('No', 'No')]
    licensepro = SelectField(u'License ArcGIS Pro?', choices=licenseChoices)
    submit = SubmitField('Submit')

class UploadCMB(FlaskForm):
    upload = FileField('CMB ZIP File', validators=[
        FileRequired()
    ])
    submit = SubmitField('Upload File')