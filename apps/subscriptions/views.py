from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.utils import timezone
from datetime import timedelta
from .models import SubscriptionPlan, Subscription, Payment
from .services import MpesaService
from django.conf import settings

def subscription_plans_view(request):
    plans = SubscriptionPlan.objects.filter(is_active=True)
    current_subscription = None
    if request.user.is_authenticated:
        try:
            current_subscription = request.user.subscription
        except Subscription.DoesNotExist:
            current_subscription = None
        
    context = {
        "plans": plans,
        "current_subscription": current_subscription
    }
    return render(request, "subscriptions/plan_list.html", context)

@login_required
def subscribe_view(request, plan_id):
    plan = get_object_or_404(SubscriptionPlan, id=plan_id, is_active=True)
    
    if plan.price == 0:
        # Handle free plan activation
        subscription, created = Subscription.objects.update_or_create(
            user=request.user,
            defaults={'plan': plan, 'status': 'active', 'expires_at': timezone.now() + timedelta(days=36500)}
        )
        if not created:
            subscription.plan = plan
            subscription.status = 'active'
            subscription.save()
            
        messages.success(request, f"You are now on the {plan.name} plan!")
        return redirect('accounts:dashboard')
    
    # For paid plans, redirect to a checkout page
    return redirect('subscriptions:checkout', plan_id=plan.id)

@login_required
def checkout_view(request, plan_id):
    plan = get_object_or_404(SubscriptionPlan, id=plan_id, is_active=True)
    
    if request.method == "POST":
        # Initialize payment (M-Pesa STK push)
        phone_number = request.POST.get("phone_number")
        if not phone_number:
            messages.error(request, "Phone number is required for M-Pesa payment.")
            return redirect("subscriptions:checkout", plan_id=plan.id)
            
        # Create pending subscription
        subscription, created = Subscription.objects.update_or_create(
            user=request.user,
            defaults={
                'plan': plan, 
                'status': 'pending', 
                'expires_at': timezone.now() + timedelta(days=30)
            }
        )
        
        # Initialize payment record
        transaction_id = f"MPESA_{timezone.now().timestamp()}"
        payment = Payment.objects.create(
            user=request.user,
            subscription=subscription,
            amount=plan.price,
            payment_method="mpesa",
            phone_number=phone_number,
            transaction_id=transaction_id,
            status="pending"
        )
        
        # Check if we have real M-Pesa credentials
        has_creds = all([
            getattr(settings, 'MPESA_CONSUMER_KEY', None),
            getattr(settings, 'MPESA_CONSUMER_SECRET', None),
            getattr(settings, 'MPESA_SHORTCODE', None),
            getattr(settings, 'MPESA_PASSKEY', None)
        ])
        
        if has_creds:
            mpesa = MpesaService()
            response, error = mpesa.initiate_stk_push(
                phone_number=phone_number,
                amount=plan.price,
                account_reference=f"SUB_{subscription.id}",
                transaction_desc=f"Subscription for {plan.name}"
            )
            
            if error:
                messages.warning(request, f"M-Pesa STK push failed: {error}. Proceeding with mock for demo.")
            else:
                messages.success(request, f"STK Push initiated to {phone_number}. Please enter your M-Pesa PIN.")
        else:
            # Fallback for demo/dev without credentials
            messages.info(request, "DEMO MODE: STK Push simulated. Click 'Confirm' to activate.")
            
        return redirect("subscriptions:payment_confirmation", payment_id=payment.id)

    context = {
        "plan": plan,
    }
    return render(request, "subscriptions/checkout.html", context)

@login_required
def payment_confirmation_view(request, payment_id):
    payment = get_object_or_404(Payment, id=payment_id, user=request.user)
    
    if request.method == "POST":
        # In a real app, this would be an AJAX call checking if the payment status has changed
        # based on a callback from M-Pesa. For now, let's allow manual confirmation or simulate it.
        payment.mark_completed()
        messages.success(request, "Payment confirmed! Your subscription is now active.")
        return redirect("accounts:dashboard")
        
    context = {
        "payment": payment
    }
    return render(request, "subscriptions/payment_confirmation.html", context)
