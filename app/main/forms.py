from flask_wtf import FlaskForm
from flask_wtf.file import FileField, FileAllowed
from wtforms import StringField, TextAreaField, SelectField, DateTimeField, IntegerField
from wtforms.validators import DataRequired, Email, Length, Optional, ValidationError, NumberRange
from wtforms.widgets import TextArea

class PickupRequestForm(FlaskForm):
    preferred_slot = DateTimeField('Preferred Date & Time', validators=[DataRequired()])
    designer_id = SelectField('Select Designer (for Redesign)', coerce=int, validators=[Optional()])
    sale_price = StringField('Expected Sale Price (for Resale)', validators=[Optional()])
    items = TextAreaField('Item Descriptions (one per line)', 
                         widget=TextArea(),
                         validators=[Optional()],
                         render_kw={'rows': 4, 'placeholder': 'e.g., Blue cotton shirt\nBlack jeans\nWinter jacket'})
    notes = TextAreaField('Additional Notes', 
                         validators=[Optional(), Length(max=500)],
                         render_kw={'rows': 3})
    photos = FileField('Photos (optional)', 
                      validators=[FileAllowed(['jpg', 'jpeg', 'png'], 'Images only!')])

class ContactForm(FlaskForm):
    name = StringField('Name', validators=[DataRequired(), Length(min=2, max=100)])
    email = StringField('Email', validators=[DataRequired(), Email()])
    subject = StringField('Subject', validators=[DataRequired(), Length(min=5, max=200)])
    message = TextAreaField('Message', validators=[DataRequired(), Length(min=10, max=1000)],
                           render_kw={'rows': 5})

class ProfileForm(FlaskForm):
    name = StringField('Name', validators=[DataRequired(), Length(min=2, max=100)])
    email = StringField('Email', validators=[DataRequired(), Email()])
    phone = StringField('Phone', validators=[Optional(), Length(max=20)])

class AddressForm(FlaskForm):
    line1 = StringField('Address Line 1', validators=[DataRequired(), Length(max=200)])
    line2 = StringField('Address Line 2', validators=[Optional(), Length(max=200)])
    city = StringField('City', validators=[DataRequired(), Length(max=100)])
    state = StringField('State', validators=[DataRequired(), Length(max=100)])
    zip_code = StringField('ZIP Code', validators=[DataRequired(), Length(max=20)])
    is_default = SelectField('Set as Default', choices=[('0', 'No'), ('1', 'Yes')], coerce=int)

class PasswordChangeForm(FlaskForm):
    current_password = StringField('Current Password', validators=[DataRequired()])
    new_password = StringField('New Password', validators=[DataRequired(), Length(min=6)])
    confirm_password = StringField('Confirm Password', validators=[DataRequired()])
    
    def validate_confirm_password(self, field):
        if field.data != self.new_password.data:
            raise ValidationError('Passwords must match.')

class DesignerApplicationForm(FlaskForm):
    portfolio_url = StringField('Portfolio URL', validators=[Optional(), Length(max=500)])
    experience_years = IntegerField('Years of Experience', validators=[DataRequired(), NumberRange(min=0, max=50)])
    specialization = StringField('Specialization', validators=[DataRequired(), Length(min=5, max=200)])
    why_designer = TextAreaField('Why do you want to be a designer?', 
                                validators=[DataRequired(), Length(min=50, max=1000)],
                                render_kw={'rows': 5})