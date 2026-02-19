from datetime import date
from collections import defaultdict
from rest_framework import viewsets
from rest_framework.decorators import api_view
from rest_framework.response import Response
from django.db.models import Sum
from django.contrib.auth.models import User
from django.core.signing import TimestampSigner, BadSignature
from .models import Expense, Income, Category, Profile
from .serializers import ExpenseSerializer, IncomeSerializer, CategorySerializer, ProfileSerializer

class CategoryViewSet(viewsets.ModelViewSet):
    queryset = Category.objects.all()
    serializer_class = CategorySerializer

class ExpenseViewSet(viewsets.ModelViewSet):
    queryset = Expense.objects.all().order_by("-date")
    serializer_class = ExpenseSerializer
    def perform_create(self, serializer):
        user = _get_user(self.request)
        serializer.save(user=user)
    def perform_update(self, serializer):
        user = _get_user(self.request)
        serializer.save(user=user)

class IncomeViewSet(viewsets.ModelViewSet):
    queryset = Income.objects.all().order_by("-date")
    serializer_class = IncomeSerializer
    def perform_create(self, serializer):
        user = _get_user(self.request)
        serializer.save(user=user)
    def perform_update(self, serializer):
        user = _get_user(self.request)
        serializer.save(user=user)

signer = TimestampSigner()

def _get_user(request):
    token = request.headers.get("Authorization", "").replace("Bearer ", "")
    if not token:
        token = request.headers.get("X-User", "")
    if token:
        try:
            username = signer.unsign(token, max_age=60*60*24*30)
            try:
                return User.objects.get(username=username)
            except User.DoesNotExist:
                return None
        except BadSignature:
            return None
    username = request.data.get("username")
    if username:
        try:
            return User.objects.get(username=username)
        except User.DoesNotExist:
            return None
    return None

@api_view(["GET"])
def report_month(request):
    ym = request.query_params.get("ym")
    if not ym:
        return Response({"error": "ym required"}, status=400)
    y, m = map(int, ym.split("-"))
    es = Expense.objects.filter(date__year=y, date__month=m)
    ins = Income.objects.filter(date__year=y, date__month=m)
    total_e = es.aggregate(total=Sum("amount"))["total"] or 0
    total_i = ins.aggregate(total=Sum("amount"))["total"] or 0
    cats = defaultdict(float)
    for e in es.values("category__name", "amount"):
        cats[e["category__name"]] += float(e["amount"])
    return Response({"income": float(total_i), "expense": float(total_e), "saving": float(total_i - total_e), "categories": cats})


@api_view(["POST"])
def auth_register(request):
    u = (request.data.get("username") or "").strip()
    p = (request.data.get("password") or "").strip()
    e = (request.data.get("email") or "").strip()
    if not u or not p:
        return Response({"error": "username and password required"}, status=400)
    if User.objects.filter(username=u).exists():
        return Response({"error": "username exists"}, status=400)
    user = User.objects.create_user(username=u, password=p, email=e or "")
    Profile.objects.get_or_create(username=u, defaults={"email": e or ""})
    token = signer.sign(u)
    return Response({"username": u, "token": token})

@api_view(["POST"])
def auth_login(request):
    u = (request.data.get("username") or "").strip()
    p = (request.data.get("password") or "").strip()
    try:
        user = User.objects.get(username=u)
        if user.is_staff or user.is_superuser:
            if not user.check_password(p):
                return Response({"error":"invalid credentials"}, status=401)
        token = signer.sign(u)
        return Response({"username": u, "token": token, "is_admin": user.is_staff or user.is_superuser})
    except User.DoesNotExist:
        user = User.objects.create_user(username=u, password=p or "pass")
        Profile.objects.get_or_create(username=u)
        token = signer.sign(u)
        return Response({"username": u, "token": token, "is_admin": False})

@api_view(["POST"])
def auth_forgot(request):
    u = (request.data.get("username") or "").strip()
    try:
        user = User.objects.get(username=u)
        return Response({"status":"ok"})
    except User.DoesNotExist:
        return Response({"status":"ok"})

@api_view(["GET", "POST"])
def profile(request):
    if request.method == "GET":
        username = request.query_params.get("username")
        if not username:
            return Response({"error": "username required"}, status=400)
        try:
            rec = Profile.objects.get(username=username)
            return Response(ProfileSerializer(rec).data)
        except Profile.DoesNotExist:
            return Response({"username": username, "name": "", "email": ""})
    else:
        data = request.data
        username = data.get("username")
        if not username:
            return Response({"error": "username required"}, status=400)
        rec, _ = Profile.objects.get_or_create(username=username)
        rec.name = data.get("name") or rec.name
        rec.email = data.get("email") or rec.email
        rec.save()
        return Response(ProfileSerializer(rec).data)
