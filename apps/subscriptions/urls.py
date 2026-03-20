
from django.urls import path
from . import views
from . import models


app_name="subscriptions"

urlpatterns = [
    path("plans/", views.subscription_plans_view, name="plans"),
    path("subscribe/<int:plan_id>/", views.subscribe_view, name="subscribe"),
    path("checkout/<int:plan_id>/", views.checkout_view, name="checkout"),
    path("confirm-payment/<int:payment_id>/", views.payment_confirmation_view, name="payment_confirmation"),
]
