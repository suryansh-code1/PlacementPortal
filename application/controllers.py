from flask import Blueprint, render_template, redirect, url_for, flash, request
from flask_login import login_user, logout_user, login_required, current_user
from functools import wraps
from datetime import datetime
from . import db
from .models import User, CompanyProfile, StudentProfile, PlacementDrive, Application




auth_bp = Blueprint('auth', __name__)
admin_bp = Blueprint('admin', __name__, url_prefix='/admin')
company_bp = Blueprint('company', __name__, url_prefix='/company')
student_bp = Blueprint('student', __name__, url_prefix='/student')




def admin_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if not current_user.is_authenticated or current_user.role != 'admin':
            flash('Access denied. Admin privileges required.', 'danger')
            return redirect(url_for('auth.login'))
        return f(*args, **kwargs)
    return decorated_function




def company_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if not current_user.is_authenticated or current_user.role != 'company':
            flash('Access denied. Company account required.', 'danger')
            return redirect(url_for('auth.login'))
        if current_user.company_profile.approval_status != 'approved':
            flash('Your company account is pending approval.', 'warning')
            return redirect(url_for('auth.login'))
        return f(*args, **kwargs)
    return decorated_function




def student_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if not current_user.is_authenticated or current_user.role != 'student':
            flash('Access denied. Student account required.', 'danger')
            return redirect(url_for('auth.login'))
        return f(*args, **kwargs)
    return decorated_function




@auth_bp.route('/')
def index():
    if current_user.is_authenticated:
        if current_user.role == 'admin':
            return redirect(url_for('admin.dashboard'))
        elif current_user.role == 'company':
            return redirect(url_for('company.dashboard'))
        else:
            return redirect(url_for('student.dashboard'))
    return redirect(url_for('auth.login'))




@auth_bp.route('/login', methods=['GET', 'POST'])
def login():
    if current_user.is_authenticated:
        return redirect(url_for('auth.index'))
    
    if request.method == 'POST':
        email = request.form.get('email')
        password = request.form.get('password')
        
        user = User.query.filter_by(email=email).first()
        
        if user and user.check_password(password):
            if not user.is_active:
                flash('Your account has been deactivated.', 'danger')
                return redirect(url_for('auth.login'))
            
            if user.role == 'company' and user.company_profile.approval_status != 'approved':
                flash('Your company registration is pending approval.', 'warning')
                return redirect(url_for('auth.login'))
            
            login_user(user)
            flash('Login successful!', 'success')
            
            if user.role == 'admin':
                return redirect(url_for('admin.dashboard'))
            elif user.role == 'company':
                return redirect(url_for('company.dashboard'))
            else:
                return redirect(url_for('student.dashboard'))
        else:
            flash('Invalid email or password.', 'danger')
    
    return render_template('login.html')




@auth_bp.route('/logout')
@login_required
def logout():
    logout_user()
    flash('You have been logged out.', 'info')
    return redirect(url_for('auth.login'))




@auth_bp.route('/register')
def register():
    return render_template('register.html')




@auth_bp.route('/register/company', methods=['GET', 'POST'])
def register_company():
    if request.method == 'POST':
        email = request.form.get('email')
        password = request.form.get('password')
        name = request.form.get('name')
        hr_contact = request.form.get('hr_contact')
        website = request.form.get('website')
        
        if User.query.filter_by(email=email).first():
            flash('Email already registered.', 'danger')
            return redirect(url_for('auth.register_company'))
        
        user = User(email=email, role='company')
        user.set_password(password)
        db.session.add(user)
        db.session.flush()
        
        company = CompanyProfile(
            user_id=user.id,
            name=name,
            hr_contact=hr_contact,
            website=website,
            approval_status='pending'
        )
        db.session.add(company)
        db.session.commit()
        
        flash('Registration successful! Please wait for admin approval.', 'success')
        return redirect(url_for('auth.login'))
    
    return render_template('register_company.html')




@auth_bp.route('/register/student', methods=['GET', 'POST'])
def register_student():
    if request.method == 'POST':
        email = request.form.get('email')
        password = request.form.get('password')
        name = request.form.get('name')
        student_id = request.form.get('student_id')
        contact = request.form.get('contact')
        resume_bio = request.form.get('resume_bio')
        
        if User.query.filter_by(email=email).first():
            flash('Email already registered.', 'danger')
            return redirect(url_for('auth.register_student'))
        
        if StudentProfile.query.filter_by(student_id=student_id).first():
            flash('Student ID already registered.', 'danger')
            return redirect(url_for('auth.register_student'))
        
        user = User(email=email, role='student')
        user.set_password(password)
        db.session.add(user)
        db.session.flush()
        
        student = StudentProfile(
            user_id=user.id,
            name=name,
            student_id=student_id,
            contact=contact,
            resume_bio=resume_bio
        )
        db.session.add(student)
        db.session.commit()
        
        flash('Registration successful! You can now login.', 'success')
        return redirect(url_for('auth.login'))
    
    return render_template('register_student.html')




@admin_bp.route('/dashboard')
@admin_required
def dashboard():
    total_students = StudentProfile.query.count()
    total_companies = CompanyProfile.query.count()
    total_applications = Application.query.count()
    total_drives = PlacementDrive.query.count()
    pending_companies = CompanyProfile.query.filter_by(approval_status='pending').count()
    pending_drives = PlacementDrive.query.filter_by(status='pending').count()
    
    return render_template('admin/dashboard.html',
                         total_students=total_students,
                         total_companies=total_companies,
                         total_applications=total_applications,
                         total_drives=total_drives,
                         pending_companies=pending_companies,
                         pending_drives=pending_drives)




@admin_bp.route('/companies')
@admin_required
def companies():
    search = request.args.get('search', '')
    if search:
        companies = CompanyProfile.query.filter(CompanyProfile.name.contains(search)).all()
    else:
        companies = CompanyProfile.query.all()
    return render_template('admin/companies.html', companies=companies, search=search)




@admin_bp.route('/students')
@admin_required
def students():
    search = request.args.get('search', '')
    if search:
        students = StudentProfile.query.filter(
            (StudentProfile.name.contains(search)) | 
            (StudentProfile.student_id.contains(search))
        ).all()
    else:
        students = StudentProfile.query.all()
    return render_template('admin/students.html', students=students, search=search)




@admin_bp.route('/drives')
@admin_required
def drives():
    drives = PlacementDrive.query.all()
    return render_template('admin/drives.html', drives=drives)




@admin_bp.route('/approvals')
@admin_required
def approvals():
    pending_companies = CompanyProfile.query.filter_by(approval_status='pending').all()
    pending_drives = PlacementDrive.query.filter_by(status='pending').all()
    return render_template('admin/approvals.html', 
                         pending_companies=pending_companies,
                         pending_drives=pending_drives)




@admin_bp.route('/approve/company/<int:id>')
@admin_required
def approve_company(id):
    company = CompanyProfile.query.get_or_404(id)
    company.approval_status = 'approved'
    db.session.commit()
    flash(f'Company "{company.name}" has been approved.', 'success')
    return redirect(url_for('admin.approvals'))




@admin_bp.route('/reject/company/<int:id>')
@admin_required
def reject_company(id):
    company = CompanyProfile.query.get_or_404(id)
    company.approval_status = 'rejected'
    db.session.commit()
    flash(f'Company "{company.name}" has been rejected.', 'warning')
    return redirect(url_for('admin.approvals'))




@admin_bp.route('/approve/drive/<int:id>')
@admin_required
def approve_drive(id):
    drive = PlacementDrive.query.get_or_404(id)
    drive.status = 'approved'
    db.session.commit()
    flash(f'Drive "{drive.title}" has been approved.', 'success')
    return redirect(url_for('admin.approvals'))




@admin_bp.route('/reject/drive/<int:id>')
@admin_required
def reject_drive(id):
    drive = PlacementDrive.query.get_or_404(id)
    drive.status = 'rejected'
    db.session.commit()
    flash(f'Drive "{drive.title}" has been rejected.', 'warning')
    return redirect(url_for('admin.approvals'))




@admin_bp.route('/delete/company/<int:id>')
@admin_required
def delete_company(id):
    company = CompanyProfile.query.get_or_404(id)
    user = company.user
    db.session.delete(user)
    db.session.commit()
    flash('Company has been deleted.', 'success')
    return redirect(url_for('admin.companies'))




@admin_bp.route('/delete/student/<int:id>')
@admin_required
def delete_student(id):
    student = StudentProfile.query.get_or_404(id)
    user = student.user
    db.session.delete(user)
    db.session.commit()
    flash('Student has been deleted.', 'success')
    return redirect(url_for('admin.students'))




@admin_bp.route('/blacklist/company/<int:id>')
@admin_required
def blacklist_company(id):
    company = CompanyProfile.query.get_or_404(id)
    company.user.is_active = False
    db.session.commit()
    flash(f'Company "{company.name}" has been blacklisted.', 'warning')
    return redirect(url_for('admin.companies'))




@admin_bp.route('/blacklist/student/<int:id>')
@admin_required
def blacklist_student(id):
    student = StudentProfile.query.get_or_404(id)
    student.user.is_active = False
    db.session.commit()
    flash(f'Student "{student.name}" has been blacklisted.', 'warning')
    return redirect(url_for('admin.students'))




@admin_bp.route('/activate/company/<int:id>')
@admin_required
def activate_company(id):
    company = CompanyProfile.query.get_or_404(id)
    company.user.is_active = True
    db.session.commit()
    flash(f'Company "{company.name}" has been activated.', 'success')
    return redirect(url_for('admin.companies'))




@admin_bp.route('/activate/student/<int:id>')
@admin_required
def activate_student(id):
    student = StudentProfile.query.get_or_404(id)
    student.user.is_active = True
    db.session.commit()
    flash(f'Student "{student.name}" has been activated.', 'success')
    return redirect(url_for('admin.students'))




@company_bp.route('/dashboard')
@company_required
def dashboard():
    company = current_user.company_profile
    drives = company.placement_drives
    return render_template('company/dashboard.html', company=company, drives=drives)




@company_bp.route('/drive/create', methods=['GET', 'POST'])
@company_required
def create_drive():
    if request.method == 'POST':
        title = request.form.get('title')
        description = request.form.get('description')
        eligibility = request.form.get('eligibility')
        deadline_str = request.form.get('deadline')
        
        deadline = datetime.strptime(deadline_str, '%Y-%m-%dT%H:%M')
        
        if deadline < datetime.now():
            flash('Deadline must be in the future.', 'danger')
            return redirect(url_for('company.create_drive'))
        
        drive = PlacementDrive(
            company_id=current_user.company_profile.id,
            title=title,
            description=description,
            eligibility=eligibility,
            deadline=deadline,
            status='pending'
        )
        db.session.add(drive)
        db.session.commit()
        
        flash('Placement drive created successfully! Pending admin approval.', 'success')
        return redirect(url_for('company.dashboard'))
    
    return render_template('company/create_drive.html')




@company_bp.route('/drive/edit/<int:id>', methods=['GET', 'POST'])
@company_required
def edit_drive(id):
    drive = PlacementDrive.query.get_or_404(id)
    
    if drive.company_id != current_user.company_profile.id:
        flash('Access denied.', 'danger')
        return redirect(url_for('company.dashboard'))
    
    if request.method == 'POST':
        drive.title = request.form.get('title')
        drive.description = request.form.get('description')
        drive.eligibility = request.form.get('eligibility')
        deadline_str = request.form.get('deadline')
        drive.deadline = datetime.strptime(deadline_str, '%Y-%m-%dT%H:%M')
        
        db.session.commit()
        flash('Drive updated successfully!', 'success')
        return redirect(url_for('company.dashboard'))
    
    return render_template('company/edit_drive.html', drive=drive)




@company_bp.route('/drive/close/<int:id>')
@company_required
def close_drive(id):
    drive = PlacementDrive.query.get_or_404(id)
    
    if drive.company_id != current_user.company_profile.id:
        flash('Access denied.', 'danger')
        return redirect(url_for('company.dashboard'))
    
    drive.status = 'closed'
    db.session.commit()
    flash('Drive has been closed.', 'success')
    return redirect(url_for('company.dashboard'))




@company_bp.route('/drive/delete/<int:id>')
@company_required
def delete_drive(id):
    drive = PlacementDrive.query.get_or_404(id)
    
    if drive.company_id != current_user.company_profile.id:
        flash('Access denied.', 'danger')
        return redirect(url_for('company.dashboard'))
    
    db.session.delete(drive)
    db.session.commit()
    flash('Drive has been deleted.', 'success')
    return redirect(url_for('company.dashboard'))




@company_bp.route('/applicants/<int:drive_id>')
@company_required
def applicants(drive_id):
    drive = PlacementDrive.query.get_or_404(drive_id)
    
    if drive.company_id != current_user.company_profile.id:
        flash('Access denied.', 'danger')
        return redirect(url_for('company.dashboard'))
    
    applications = Application.query.filter_by(drive_id=drive_id).all()
    return render_template('company/applicants.html', drive=drive, applications=applications)




@company_bp.route('/application/<int:id>/update', methods=['POST'])
@company_required
def update_application(id):
    application = Application.query.get_or_404(id)
    
    if application.drive.company_id != current_user.company_profile.id:
        flash('Access denied.', 'danger')
        return redirect(url_for('company.dashboard'))
    
    new_status = request.form.get('status')
    if new_status in ['applied', 'shortlisted', 'selected', 'rejected']:
        application.status = new_status
        db.session.commit()
        flash('Application status updated.', 'success')
    
    return redirect(url_for('company.applicants', drive_id=application.drive_id))




@student_bp.route('/dashboard')
@student_required
def dashboard():
    student = current_user.student_profile
    applications = Application.query.filter_by(student_id=student.id).all()
    return render_template('student/dashboard.html', student=student, applications=applications)




@student_bp.route('/profile', methods=['GET', 'POST'])
@student_required
def profile():
    student = current_user.student_profile
    
    if request.method == 'POST':
        student.name = request.form.get('name')
        student.contact = request.form.get('contact')
        student.resume_bio = request.form.get('resume_bio')
        db.session.commit()
        flash('Profile updated successfully!', 'success')
        return redirect(url_for('student.profile'))
    
    return render_template('student/profile.html', student=student)




@student_bp.route('/drives')
@student_required
def drives():
    student = current_user.student_profile
    approved_drives = PlacementDrive.query.filter_by(status='approved').filter(
        PlacementDrive.deadline > datetime.now()
    ).all()
    
    applied_drive_ids = [app.drive_id for app in student.applications]
    
    return render_template('student/drives.html', 
                         drives=approved_drives, 
                         applied_drive_ids=applied_drive_ids)




@student_bp.route('/apply/<int:drive_id>')
@student_required
def apply(drive_id):
    drive = PlacementDrive.query.get_or_404(drive_id)
    student = current_user.student_profile
    
    if drive.status != 'approved':
        flash('This drive is not accepting applications.', 'danger')
        return redirect(url_for('student.drives'))
    
    if drive.deadline < datetime.now():
        flash('Application deadline has passed.', 'danger')
        return redirect(url_for('student.drives'))
    
    existing = Application.query.filter_by(student_id=student.id, drive_id=drive_id).first()
    if existing:
        flash('You have already applied for this drive.', 'warning')
        return redirect(url_for('student.drives'))
    
    application = Application(
        student_id=student.id,
        drive_id=drive_id,
        status='applied'
    )
    db.session.add(application)
    db.session.commit()
    
    flash('Application submitted successfully!', 'success')
    return redirect(url_for('student.history'))




@student_bp.route('/history')
@student_required
def history():
    student = current_user.student_profile
    applications = Application.query.filter_by(student_id=student.id).order_by(Application.applied_date.desc()).all()
    return render_template('student/history.html', applications=applications)
