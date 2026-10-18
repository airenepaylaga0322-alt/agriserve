from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, BooleanField, SubmitField
from wtforms.validators import DataRequired, Email, Length, EqualTo
from wtforms import DateField, TextAreaField

class RegisterForm(FlaskForm):
    full_name = StringField("Full Name", validators=[DataRequired(), Length(min=2, max=150)])
    email = StringField("Email", validators=[DataRequired(), Email(), Length(max=255)])
    password = PasswordField("Password", validators=[DataRequired(), Length(min=8, max=128)])
    confirm = PasswordField(
        "Confirm Password",
        validators=[DataRequired(), EqualTo("password", message="Passwords must match.")],
    )
    submit = SubmitField("Create Account")


class LoginForm(FlaskForm):
    class Meta:
        csrf = False  # Temporarily disabled CSRF just for login to fix the refresh bug

    email = StringField("Email", validators=[DataRequired(), Email()])
    password = PasswordField("Password", validators=[DataRequired()])
    remember = BooleanField("Remember me")
    submit = SubmitField("Log In")

# Add to the bottom of app/forms.py
from wtforms import DecimalField, IntegerField, SelectField

class ProfileForm(FlaskForm):
    class Meta:
        csrf = False # Disabled temporarily

    contact_number = StringField("Contact Number")
    barangay = StringField("Barangay", validators=[DataRequired()])
    municipality = StringField("Municipality", validators=[DataRequired()])
    province = StringField("Province", validators=[DataRequired()])
    household_size = IntegerField("Household Size", default=1)
    dependents = IntegerField("Number of Dependents", default=0)
    primary_income_source = StringField("Primary Income Source")
    estimated_monthly_income = DecimalField("Estimated Monthly Income (PHP)")
    submit = SubmitField("Save Profile")

class FarmForm(FlaskForm):
    class Meta:
        csrf = False

    location = StringField("Farm Location/Description")
    barangay = StringField("Barangay", validators=[DataRequired()])
    municipality = StringField("Municipality", validators=[DataRequired()])
    province = StringField("Province", validators=[DataRequired()])
    area = DecimalField("Area (Hectares)", validators=[DataRequired()])
    land_tenure = SelectField("Land Tenure", choices=[("owned", "Owned"), ("tenant", "Tenant"), ("leased", "Leased"), ("shared", "Shared"), ("other", "Other")])
    submit = SubmitField("Add Farm")

class CropForm(FlaskForm):
    class Meta:
        csrf = False

    crop_type = StringField("Crop Type (e.g. Rice, Corn)", validators=[DataRequired()])
    planting_date = DateField("Planting Date", validators=[DataRequired()])
    estimated_production = DecimalField("Estimated Production (kg)", validators=[DataRequired()])
    submit = SubmitField("Save Crop")

class LossForm(FlaskForm):
    class Meta:
        csrf = False

    crop_id = SelectField("Affected Crop", coerce=int, validators=[DataRequired()])
    loss_type = SelectField("Type of Loss", choices=[
        ("Typhoon", "Typhoon/Flood"), 
        ("Drought", "Drought"), 
        ("Pest", "Pest Infestation"), 
        ("Disease", "Crop Disease"), 
        ("Other", "Other")
    ])
    loss_percentage = DecimalField("Percentage of Production Lost (%)", validators=[DataRequired()])
    estimated_value = DecimalField("Estimated Value Lost (PHP)")
    loss_date = DateField("Date of Loss", validators=[DataRequired()])
    description = TextAreaField("Description/Details")
    submit = SubmitField("Record Loss")

class ProgramForm(FlaskForm):
    class Meta:
        csrf = False

    code = StringField("Program Code (e.g. RCEF-2026)", validators=[DataRequired()])
    name = StringField("Program Name", validators=[DataRequired()])
    category = SelectField("Category", choices=[
        ("Seeds", "Seeds"), ("Fertilizer", "Fertilizer"), ("Cash Aid", "Cash Assistance"),
        ("Credit", "Credit / Loan"), ("Insurance", "Insurance"), ("Other", "Other")
    ])
    description = TextAreaField("Description / Eligibility Rules")
    available_allocation = DecimalField("Total Allocation (PHP)")
    max_benefit_per_farmer = DecimalField("Max Benefit Per Farmer (PHP)")
    submit = SubmitField("Create Program")

class ApplyForm(FlaskForm):
    class Meta:
        csrf = False

    farm_id = SelectField("Select Farm to use for this Application", coerce=int, validators=[DataRequired()])
    notes = TextAreaField("Additional Notes / Justification")
    submit = SubmitField("Submit Application")