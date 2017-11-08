from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField ,TextAreaField
from wtforms.validators import InputRequired, EqualTo, Email, Length
from flask_wtf.file import FileField, FileAllowed, FileRequired
from flask_uploads import UploadSet, IMAGES, configure_uploads


images = UploadSet("images",IMAGES)


class JobForm(FlaskForm):
	title = StringField("Judul",validators=[Length(min=5,max=100),InputRequired()])
	description = TextAreaField("Deskripsi",validators=[InputRequired()])
	position = StringField("Posisi",validators=[InputRequired(),Length(max=100)])
	email = StringField("Email",validators=[Email(),Length(max=100),InputRequired()])
	phone = StringField("Phone",validators=[InputRequired(),Length(max=100)])
	address = StringField("Alamat",validators=[InputRequired(),Length(max=100)])
	salary = StringField("Gaji",validators=[Length(max=100)])
	company = StringField("Nama Perusahaan",validators=[Length(max=100)])
	images = FileField("Upload Logo",validators=[InputRequired(),FileAllowed(images,"Images only")])


class AdminRegistrationForm(FlaskForm):
	username = StringField("Username",validators=[InputRequired(),Length(max=100)])
	email = StringField("Email",validators=[InputRequired(),Email(message="Invalid Email"),Length(max=100)])
	password = PasswordField("Password",validators=[InputRequired(),EqualTo("confirm",message="Password not match")])
	confirm = PasswordField("Confirm Password")


class AdminLoginForm(FlaskForm):
	username = StringField("Username",validators=[InputRequired(),Length(max=100)])
	password = PasswordField("Password",validators=[InputRequired()])
	

class EditStatus(FlaskForm):
	status = StringField("Status",validators=[Length(max=100)])


class ContactForm(FlaskForm):
	name = StringField("Nama",validators=[Length(max=100),InputRequired()])
	email = StringField("Email",validators=[Email(),Length(max=100),InputRequired()])
	phone = StringField("Phone",validators=[InputRequired(),Length(max=100)])
	subject = StringField("Subject",validators=[Length(max=100)])
	message = TextAreaField("Pesan",validators=[InputRequired()])



