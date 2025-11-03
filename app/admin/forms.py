from flask_wtf import FlaskForm
from wtforms import StringField, TextAreaField, SelectField, IntegerField, DecimalField, BooleanField
from wtforms.validators import DataRequired, Length, NumberRange, Optional

class OrderUpdateForm(FlaskForm):
    status = SelectField('Status', 
                        choices=[
                            ('received', 'Received'),
                            ('sorting', 'Sorting'),
                            ('designing', 'Designing'),
                            ('ready', 'Ready'),
                            ('shipped', 'Shipped'),
                            ('delivered', 'Delivered')
                        ],
                        validators=[DataRequired()])
    designer_id = SelectField('Designer', coerce=int, validators=[Optional()])
    fabric_type = StringField('Fabric Type', validators=[Optional(), Length(max=100)])
    notes = TextAreaField('Notes', validators=[Optional()], render_kw={'rows': 4})
    estimated_days = IntegerField('Estimated Days', validators=[Optional(), NumberRange(min=1, max=365)])
    points_awarded = IntegerField('Points Awarded', validators=[Optional(), NumberRange(min=0, max=10000)])

class ProductForm(FlaskForm):
    title = StringField('Title', validators=[DataRequired(), Length(min=2, max=200)])
    description = TextAreaField('Description', validators=[Optional()], render_kw={'rows': 5})
    price = DecimalField('Price (₹)', validators=[DataRequired(), NumberRange(min=0)])
    stock = IntegerField('Stock', validators=[DataRequired(), NumberRange(min=0)])
    designer_id = SelectField('Designer', coerce=int, validators=[Optional()])
    tags = StringField('Tags (comma-separated)', validators=[Optional(), Length(max=500)])
    is_featured = BooleanField('Featured Product')