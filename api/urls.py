from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import (
    ExpenseViewSet,
    IncomeViewSet,
    CategoryViewSet,
    report_month,
    profile,
    auth_register,
    auth_login,
    auth_forgot
)

# Create DRF router
router = DefaultRouter()
router.register("expenses", ExpenseViewSet, basename="expenses")
router.register("incomes", IncomeViewSet, basename="incomes")
router.register("categories", CategoryViewSet, basename="categories")

# URL patterns
urlpatterns = [
    path("", include(router.urls)),        # ViewSets routes
    path("report/", report_month),         # Monthly report
    path("profile/", profile),             # User profile
    path("auth/register/", auth_register), # Register
    path("auth/login/", auth_login),       # Login
    path("auth/forgot/", auth_forgot),     # Forgot password
]
