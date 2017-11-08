from flask import Flask, render_template, url_for, session, flash, redirect, request
from flask_sqlalchemy import SQLAlchemy 
from form import JobForm, AdminRegistrationForm, AdminLoginForm, EditStatus, ContactForm
from flask_mail import Mail, Message
from werkzeug.security import generate_password_hash, check_password_hash
from itsdangerous import URLSafeTimedSerializer,SignatureExpired
from flask_login import LoginManager , UserMixin, login_user, login_required, logout_user, current_user
from flask_uploads import UploadSet, IMAGES, configure_uploads


app = Flask(__name__)
app.config["SECRET_KEY"] = "Cariuangitugampang"
app.config["SQLALCHEMY_DATABASE_URI"] = "mysql://root:root@localhost/kerjasales"
app.debug = True
db = SQLAlchemy(app)

#fungsi mail
app.config.from_pyfile("config.cfg") 
mail = Mail(app)
s = URLSafeTimedSerializer("secret")

#flask login
login_manager = LoginManager()
login_manager.init_app(app)
login_manager.login_view = "UserLogin"

#fungsi Upload
#mengatur image
images = UploadSet("images",IMAGES)
app.config["UPLOADED_IMAGES_DEST"] = "static/img/profile/"
app.config["UPLOADED_IMAGES_URL"] = "http://127.0.0.1:5000/static/img/profile/"
configure_uploads(app,images)





class Job(db.Model):
	id = db.Column(db.Integer, primary_key=True)
	title = db.Column(db.String(220))
	description = db.Column(db.UnicodeText())
	email = db.Column(db.String(100))
	phone = db.Column(db.String(100))
	address = db.Column(db.String(100))
	salary = db.Column(db.String(100))
	company = db.Column(db.String(100))
	position = db.Column(db.String(100))
	image_name = db.Column(db.String(100))
	status = db.Column(db.String(100))



class Admin(db.Model):
	id = db.Column(db.Integer, primary_key=True)
	username = db.Column(db.String(220))
	email = db.Column(db.String(100))
	password = db.Column(db.String(200))

	def is_active(self):
		return True

	def get_id(self):
		return self.id

	def is_authenticated(self):
		return self.authenticated

	def is_anonymous(self):
		return False


class Contact(db.Model):
	id = db.Column(db.Integer, primary_key=True)
	name = db.Column(db.String(100))
	email = db.Column(db.String(100))
	phone = db.Column(db.String(100))
	subject = db.Column(db.String(100))
	message = db.Column(db.UnicodeText())



#login manager
@login_manager.user_loader
def user_loader(user_id):
	return Admin.query.get(int(user_id))







@app.route("/")
def index():
	jobs = Job.query.filter_by(status="publish").all()
	return render_template("index.html",jobs=jobs)



@app.route("/<string:id>",methods=["GET","POST"])
def IndexJobs(id):
	job = Job.query.filter_by(id=id).first()
	return render_template("index_job.html",job=job)







@app.route("/pasang-iklan",methods=["GET","POST"])
def PostJob():
	form = JobForm()
	if form.validate_on_submit():
		email = form.email.data
		msg = Message("Invoice Iklan", sender="makinrame@gmail.com", recipients=[email])
		link = url_for("JobInvoice",_external=True)
		link2 = url_for("ContactMe",_external=True)
		msg.body = "Iklan anda akan segera tayang. Silakan lakukan pembayaran dengan mengikuti invoice di link berikut {} dan anda dapat konfirmasikan pembayaran anda di link berikut {}".format(link,link2)
		mail.send(msg)

		filename = images.save(form.images.data)
		job = Job(title=form.title.data,description=form.description.data,position=form.position.data,email=form.email.data,phone=form.phone.data,address=form.address.data,salary=form.salary.data,company=form.company.data,image_name=filename,status="pending")
		db.session.add(job)
		db.session.commit()
		flash("Iklan telah kami terima,invoice telah kami kirim ke email anda,silakan lunasi pembayaran agar iklan segera tayang","success")
		return redirect(url_for("JobInvoice"))
	return render_template("post_job.html",form=form)



@app.route("/invoice",methods=["GET","POST"])
def JobInvoice():
	return render_template("invoice.html")


@app.route("/kontak",methods=["GET","POST"])
def ContactMe():
	form = ContactForm()
	if form.validate_on_submit():
		pesan = Contact(name=form.name.data,email=form.email.data,phone=form.phone.data,subject=form.subject.data,message=form.message.data)
		db.session.add(pesan)
		db.session.commit()
		flash("Pesan anda terkirim","success")
		return redirect(url_for("index"))
	return render_template("contact.html",form=form)







#########################################################################################
################################# ADMIN ROUTE ###########################################
#########################################################################################
#########################################################################################


@app.route("/register",methods=["GET","POST"])
def AdminRegister():
	form = AdminRegistrationForm()
	if form.validate_on_submit():
		hass_pass = generate_password_hash(form.password.data,method="sha256")
		admin = Admin(username=form.username.data,email=form.email.data,password=hass_pass)
		db.session.add(admin)
		db.session.commit()

		flash("admin berhasil di tambah","success")
		return redirect(url_for("AdminLogin"))
	return render_template("admin/register.html",form=form)


@app.route("/natagon",methods=["GET","POST"])
def AdminLogin():
	form = AdminLoginForm()
	if form.validate_on_submit():
		admin = Admin.query.filter_by(username=form.username.data).first()
		if admin:
			if check_password_hash(admin.password,form.password.data):
				login_user(admin)
				flash("login sukses","success")
				return redirect(url_for("AdminDashboard"))
		
		flash("semua salah","danger")
		return render_template("admin/login.html",form=form)
	return render_template("admin/login.html",form=form)







#########################################################################################
################################# Admin Publish Job #####################################
#########################################################################################
#########################################################################################


@app.route("/dashboard")
@login_required
def AdminDashboard():
	return render_template("admin/admin.html")




@app.route("/dashboard/submited",methods=["GET","POST"])
@login_required
def AllJobs():
	submits = Job.query.all()
	return render_template("admin/all_jobs.html",submits=submits)




@app.route("/dashboard/jobs/<string:id>",methods=["GET","POST"])
@login_required
def Jobs(id):
	form = EditStatus()
	job = Job.query.filter_by(id=id).first()
	return render_template("admin/jobs.html",job=job,form=form)


@app.route("/dashboard/delete/<string:id>",methods=["GET","POST"])
@login_required
def DeleteJob(id):
	job = Job.query.filter_by(id=id).first()
	db.session.delete(job)
	db.session.commit()

	flash("Iklan di hapus","success")
	return redirect(url_for("AdminDashboard"))




@app.route("/dashboard/edit-status/<string:id>",methods=["GET","POST"])
@login_required
def EditJob(id):
	form = EditStatus()
	job = Job.query.filter_by(id=id).first()
	form.status.data = job.status
	if form.validate_on_submit():
		jobs = Job.query.filter_by(id=id).first()
		jobs.status = request.form["status"]
		db.session.commit()

		flash("Data berhasil di update","success")
		return redirect(url_for("AdminDashboard"))
	return render_template("admin/editstatus.html",form=form)


@app.route("/dashboard/message",methods=["GET","POST"])
@login_required
def MessageList():
	messages = Contact.query.all()
	return render_template("admin/messages.html",messages=messages)


@app.route("/dashboard/message/<string:id>",methods=["GET","POST"])
@login_required
def MessagePost(id):
	message = Contact.query.filter_by(id=id).first()
	return render_template("admin/messages_post.html",message=message)


@app.route("/dashboard/delete-message/<string:id>",methods=["GET","POST"])
@login_required
def DeleteMessage(id):
	message = Contact.query.filter_by(id=id).first()
	db.session.delete(message)
	db.session.commit()

	flash("Pesan di hapus","success")
	return redirect(url_for("AdminDashboard"))

















































if __name__ == "__main__":
	app.run(host='0.0.0.0')
