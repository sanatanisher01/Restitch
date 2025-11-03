from flask import render_template, request, redirect, url_for, flash, current_app
from flask_login import login_required, current_user
from app.main import bp
from app.models import User, PickupRequest, Order, Product, CityExpansion, Address, DesignerApplication
from app.main.forms import PickupRequestForm, ContactForm, ProfileForm, AddressForm, PasswordChangeForm, DesignerApplicationForm
from app import db
try:
    from app.email import send_contact_email, send_pickup_confirmation_email
except ImportError:
    def send_contact_email(data):
        pass
    def send_pickup_confirmation_email(user, pickup):
        pass
import os
from datetime import datetime

@bp.route('/')
def index():
    # Get statistics for hero section
    total_users = User.query.count()
    total_orders = Order.query.count()
    total_products = Product.query.count()
    featured_products = Product.query.filter_by(is_featured=True).limit(3).all()
    
    stats = {
        'users': total_users,
        'orders': total_orders,
        'products': total_products,
        'kg_saved': total_orders * 2.5,  # Estimate 2.5kg per order
    }
    
    return render_template('main/index.html', stats=stats, featured_products=featured_products)

@bp.route('/about')
def about():
    return render_template('main/about.html')

@bp.route('/how-it-works')
def how_it_works():
    return render_template('main/how_it_works.html')

@bp.route('/services')
def services():
    return render_template('main/services.html')

@bp.route('/contact', methods=['GET', 'POST'])
def contact():
    form = ContactForm()
    if form.validate_on_submit():
        # Send email
        send_contact_email({
            'name': form.name.data,
            'email': form.email.data,
            'subject': form.subject.data,
            'message': form.message.data
        })
        flash('Thank you for your message! We\'ll get back to you soon.', 'success')
        return redirect(url_for('main.contact'))
    return render_template('main/contact.html', form=form)

@bp.route('/schedule-pickup', methods=['GET', 'POST'])
@login_required
def schedule_pickup():
    # Check if user has addresses
    addresses = current_user.addresses.all()
    if not addresses:
        flash('Please add an address first before scheduling a pickup.', 'info')
        return redirect(url_for('main.new_address'))
    
    form = PickupRequestForm()
    
    # Get designers for template
    designers = User.query.filter_by(role='designer').all()
    form.designer_id.choices = [(0, 'Select Designer')] + [(d.id, d.name) for d in designers]
    
    if request.method == 'POST':
        address_id = request.form.get('address', type=int)
        service_type = request.form.get('service_type')
        pickup_date = request.form.get('preferred_slot')
        time_slot = request.form.get('time_slot', '9:00')
        designer_id = request.form.get('designer_id', type=int) if service_type == 'redesign' else None
        sale_price = request.form.get('sale_price') if service_type == 'resale' else None
        
        # Check required fields
        errors = []
        if not address_id:
            errors.append('Please select a pickup address')
        if not service_type:
            errors.append('Please select a service type')
        if not pickup_date:
            errors.append('Please select a pickup date')
        if service_type == 'redesign' and not designer_id:
            errors.append('Please select a designer for redesign service')
        if service_type == 'resale' and not sale_price:
            errors.append('Please enter expected sale price for resale')
        if service_type == 'resale' and not form.photos.data:
            errors.append('Please upload photos for resale items')
            
        if not errors:
            try:
                # Combine date and time
                date_part = datetime.strptime(pickup_date, '%Y-%m-%d').date()
                time_part = datetime.strptime(time_slot, '%H:%M').time()
                preferred_datetime = datetime.combine(date_part, time_part)
                
                pickup = PickupRequest(
                    user_id=current_user.id,
                    address_id=address_id,
                    preferred_slot=preferred_datetime,
                    service_type=service_type,
                    notes=form.notes.data or ''
                )
                
                # Set additional data based on service type
                if service_type == 'redesign':
                    pickup.notes += f'\nSelected Designer ID: {designer_id}'
                elif service_type == 'resale':
                    pickup.notes += f'\nExpected Sale Price: ₹{sale_price}'
                
                if form.items.data:
                    items = [item.strip() for item in form.items.data.split('\n') if item.strip()]
                    pickup.set_items(items)
                
                try:
                    db.session.add(pickup)
                    
                    # Create order directly for redesign with designer assignment
                    if service_type == 'redesign' and designer_id:
                        order = Order(
                            user_id=current_user.id,
                            pickup_id=pickup.id,
                            service_type=service_type,
                            designer_id=designer_id,
                            status='review'  # Designer needs to review first
                        )
                        db.session.add(order)
                    elif service_type == 'resale':
                        # Create order for admin approval
                        order = Order(
                            user_id=current_user.id,
                            pickup_id=pickup.id,
                            service_type=service_type,
                            status='pending_approval'  # Admin needs to approve for store
                        )
                        db.session.add(order)
                    
                    db.session.commit()
                except Exception as e:
                    db.session.rollback()
                    current_app.logger.error(f"Database error in schedule_pickup: {e}")
                    flash('Error scheduling pickup. Please try again.', 'error')
                    return redirect(url_for('main.schedule_pickup'))
                
                if service_type == 'redesign':
                    flash('Redesign request sent to designer for review!', 'success')
                elif service_type == 'resale':
                    flash('Resale request sent to admin for approval!', 'success')
                else:
                    flash('Pickup scheduled successfully!', 'success')
                return redirect(url_for('main.my_orders'))
                
            except ValueError as e:
                flash('Invalid date/time format. Please try again.', 'error')
            except Exception as e:
                current_app.logger.error(f"Unexpected error in schedule_pickup: {e}")
                flash('An unexpected error occurred. Please try again.', 'error')
        else:
            for error in errors:
                flash(error, 'error')
    
    return render_template('main/schedule_pickup.html', form=form, addresses=addresses, designers=designers)

@bp.route('/dashboard')
@login_required
def dashboard():
    # Get user statistics
    user_orders = Order.query.filter_by(user_id=current_user.id).all()
    user_pickups = PickupRequest.query.filter_by(user_id=current_user.id).all()
    
    stats = {
        'total_donations': len(user_pickups),
        'total_redesigns': len(user_orders),
        'kg_saved': len(user_orders) * 2.5,
        'points': current_user.points,
        'trees_saved': int(len(user_orders) * 0.1),  # Estimate
    }
    
    # Recent activity
    recent_orders = Order.query.filter_by(user_id=current_user.id).order_by(Order.created_at.desc()).limit(5).all()
    recent_pickups = PickupRequest.query.filter_by(user_id=current_user.id).order_by(PickupRequest.created_at.desc()).limit(5).all()
    
    return render_template('main/dashboard.html', 
                         stats=stats, 
                         recent_orders=recent_orders, 
                         recent_pickups=recent_pickups)

@bp.route('/my-orders')
@login_required
def my_orders():
    orders = Order.query.filter_by(user_id=current_user.id).order_by(Order.created_at.desc()).all()
    pickups = PickupRequest.query.filter_by(user_id=current_user.id).order_by(PickupRequest.created_at.desc()).all()
    
    return render_template('main/my_orders.html', orders=orders, pickups=pickups)

@bp.route('/redeem')
@login_required
def redeem():
    # Available rewards based on points
    rewards = [
        {'name': '10% Discount', 'points': 100, 'description': 'Get 10% off your next purchase'},
        {'name': 'Free Shipping', 'points': 150, 'description': 'Free shipping on your next order'},
        {'name': '₹500 Credit', 'points': 500, 'description': '₹500 credit for upcycled items'},
        {'name': 'Custom Design', 'points': 1000, 'description': 'Custom redesign service'},
    ]
    
    return render_template('main/redeem.html', rewards=rewards, user_points=current_user.points)

@bp.route('/profile', methods=['GET', 'POST'])
@login_required
def profile():
    form = ProfileForm(obj=current_user)
    
    if form.validate_on_submit():
        current_user.name = form.name.data
        current_user.email = form.email.data
        current_user.phone = form.phone.data
        db.session.commit()
        flash('Profile updated successfully!', 'success')
        return redirect(url_for('main.profile'))
    
    addresses = current_user.addresses.all()
    
    # Check designer application status
    try:
        designer_app = DesignerApplication.query.filter_by(user_id=current_user.id).order_by(DesignerApplication.created_at.desc()).first()
    except Exception as e:
        current_app.logger.error(f"Error fetching designer application: {e}")
        designer_app = None
    
    return render_template('main/profile.html', form=form, addresses=addresses, designer_app=designer_app)

@bp.route('/profile/address/new', methods=['GET', 'POST'])
@login_required
def new_address():
    form = AddressForm()
    
    if form.validate_on_submit():
        # If setting as default, unset other defaults
        if form.is_default.data:
            Address.query.filter_by(user_id=current_user.id, is_default=True).update({'is_default': False})
        
        address = Address(
            user_id=current_user.id,
            line1=form.line1.data,
            line2=form.line2.data,
            city=form.city.data,
            state=form.state.data,
            zip_code=form.zip_code.data,
            is_default=bool(form.is_default.data)
        )
        db.session.add(address)
        db.session.commit()
        flash('Address added successfully!', 'success')
        return redirect(url_for('main.profile'))
    
    return render_template('main/address_form.html', form=form, title='Add Address')

@bp.route('/profile/password', methods=['GET', 'POST'])
@login_required
def change_password():
    form = PasswordChangeForm()
    
    if form.validate_on_submit():
        if current_user.check_password(form.current_password.data):
            current_user.set_password(form.new_password.data)
            db.session.commit()
            flash('Password changed successfully!', 'success')
            return redirect(url_for('main.profile'))
        else:
            flash('Current password is incorrect.', 'error')
    
    return render_template('main/password_form.html', form=form)

@bp.route('/redeem/<int:reward_id>', methods=['POST'])
@login_required
def redeem_reward(reward_id):
    rewards = {
        1: {'name': '10% Discount', 'points': 100},
        2: {'name': 'Free Shipping', 'points': 150},
        3: {'name': '₹500 Credit', 'points': 500},
        4: {'name': 'Custom Design', 'points': 1000}
    }
    
    reward = rewards.get(reward_id)
    if not reward:
        flash('Invalid reward selected.', 'error')
        return redirect(url_for('main.redeem'))
    
    if current_user.points >= reward['points']:
        current_user.points -= reward['points']
        db.session.commit()
        flash(f'Successfully redeemed {reward["name"]}!', 'success')
    else:
        flash('Insufficient points for this reward.', 'error')
    
    return redirect(url_for('main.redeem'))

@bp.route('/apply-designer', methods=['GET', 'POST'])
@login_required
def apply_designer():
    # Check if user is already a designer
    if current_user.role == 'designer':
        flash('You are already a designer!', 'info')
        return redirect(url_for('main.profile'))
    
    # Check if user has pending application
    existing_app = DesignerApplication.query.filter_by(user_id=current_user.id, status='pending').first()
    if existing_app:
        flash('You already have a pending designer application.', 'info')
        return redirect(url_for('main.profile'))
    
    form = DesignerApplicationForm()
    
    if form.validate_on_submit():
        try:
            application = DesignerApplication(
                user_id=current_user.id,
                portfolio_url=form.portfolio_url.data,
                experience_years=form.experience_years.data,
                specialization=form.specialization.data,
                why_designer=form.why_designer.data
            )
            db.session.add(application)
            db.session.commit()
            
            flash('Designer application submitted successfully! We will review it soon.', 'success')
            return redirect(url_for('main.profile'))
        except Exception as e:
            db.session.rollback()
            current_app.logger.error(f"Designer application error: {e}")
            flash('Error submitting application. Please try again.', 'error')
    
    return render_template('main/apply_designer.html', form=form)