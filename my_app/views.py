import json
from django.shortcuts import redirect, render, get_object_or_404
from django.contrib.auth import get_user_model, login, authenticate, logout
from django.urls import reverse_lazy, reverse
from django.http import JsonResponse, HttpResponse
from django.views.generic import TemplateView, FormView, View
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.cache import never_cache
from django.utils.decorators import method_decorator
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.apps import apps
from django.db import IntegrityError
from rest_framework import generics, permissions, viewsets, serializers, status
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework.permissions import IsAuthenticated, AllowAny
from rest_framework_simplejwt.serializers import TokenObtainPairSerializer
from rest_framework_simplejwt.views import TokenObtainPairView
from rest_framework.exceptions import ValidationError
from rest_framework_simplejwt.tokens import RefreshToken
from rest_framework.decorators import api_view, permission_classes
from rest_framework.authtoken.models import Token
from .forms import ManuscriptSubmissionForm, SignUpForm, SignInForm
from django.conf import settings
import jwt
from datetime import datetime, timedelta, timezone
from .serializers import (
    UserSerializer,
    ProfileSerializer,
    ManuscriptSerializer,
    KeywordSerializer,
    FeedbackQuestionSerializer,
    FeedbackResponseSerializer,
    AuthorSettingsSerializer,
    ResourceSerializer,
    ResourceInteractionSerializer,
    NotificationSerializer,
    BetaReaderApplicationSerializer,
    ManuscriptFeedbackPreferenceSerializer,
)
from .models import (
    Manuscript,
    Feedback,
    Profile,
    Keyword,
    FeedbackQuestion,
    FeedbackResponse,
    ManuscriptFeedbackPreference,
    AuthorSettings,
    Resource,
    ResourceInteraction,
    Notification,
    BetaReaderApplication,
    BetaReader,
)


# Models
Profile = apps.get_model("my_app", "Profile")
Manuscript = apps.get_model("my_app", "Manuscript")
User = get_user_model()


# Serializers
class BetaReaderSerializer(serializers.ModelSerializer):
    class Meta:
        model = BetaReader
        fields = ["id", "user", "experience", "genres", "created_at", "updated_at"]


# Views
def some_view(request):
    if request.user.profile.user_type == "author":
        url = reverse("author-dashboard.html")
    else:
        url = reverse("reader-dashboard.html")
    serializer = UserSerializer(data=request.data)
    if serializer.is_valid():
        serializer.save()


def base_url(request):
    return {"BASE_URL": settings.BASE_URL}


class CustomSignUpView(generics.CreateAPIView):
    queryset = User.objects.all()
    serializer_class = UserSerializer

    def create(self, request, *args, **kwargs):
        try:
            return super().create(request, *args, **kwargs)
        except ValidationError as e:
            return Response({"errors": e.detail}, status=400)


class MyTokenObtainPairSerializer(TokenObtainPairSerializer):
    @classmethod
    def get_token(cls, user):
        token = super().get_token(user)
        token["name"] = user.username
        token["role"] = user.profile.role
        return token


class MyTokenObtainPairView(TokenObtainPairView):
    serializer_class = MyTokenObtainPairSerializer

    def post(self, request, *args, **kwargs):
        response = super().post(request, *args, **kwargs)
        user_type = request.data.get("user_type")
        if user_type:
            response.data["user_type"] = user_type
        return response


class ReaderDashboardView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        manuscripts = Manuscript.objects.all()
        manuscripts_data = ManuscriptSerializer(manuscripts, many=True).data
        notifications = Notification.objects.filter(user=request.user, is_read=False)
        notifications_data = NotificationSerializer(notifications, many=True).data
        data = {
            "manuscripts": manuscripts_data,
            "notifications": notifications_data,
        }
        return Response(data)


class AuthorDashboardView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        manuscripts = Manuscript.objects.filter(author=request.user)
        manuscripts_data = ManuscriptSerializer(manuscripts, many=True).data
        notifications = Notification.objects.filter(user=request.user, is_read=False)
        notifications_data = NotificationSerializer(notifications, many=True).data
        data = {
            "manuscripts": manuscripts_data,
            "notifications": notifications_data,
        }
        return Response(data)


class ReaderDashboardTemplateView(TemplateView):
    template_name = "reader-dashboard.html"


class AuthorDashboardTemplateView(TemplateView):
    template_name = "author-dashboard.html"


class UserProfileView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        user = request.user
        serializer = UserSerializer(user)
        return Response(serializer.data)

    def put(self, request):
        user = request.user
        serializer = UserSerializer(user, data=request.data, partial=True)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data)
        return Response(serializer.errors, status=400)


class UserListCreateView(generics.ListCreateAPIView):
    queryset = User.objects.all()
    serializer_class = UserSerializer
    permission_classes = [permissions.IsAuthenticatedOrReadOnly]


class UserDetailView(generics.RetrieveUpdateDestroyAPIView):
    queryset = User.objects.all()
    serializer_class = UserSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        return User.objects.filter(id=self.request.user.id)


class ManuscriptListCreateView(generics.ListCreateAPIView):
    queryset = Manuscript.objects.all()
    serializer_class = ManuscriptSerializer
    permission_classes = [permissions.IsAuthenticated]

    def perform_create(self, serializer):
        serializer.save(author=self.request.user)


class ManuscriptDetailView(generics.RetrieveUpdateDestroyAPIView):
    queryset = Manuscript.objects.all()
    serializer_class = ManuscriptSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        return Manuscript.objects.filter(author=self.request.user)


class ProfileDetailView(generics.RetrieveUpdateDestroyAPIView):
    queryset = Profile.objects.all()
    serializer_class = ProfileSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        return Profile.objects.filter(user=self.request.user)


class ProfileListCreateView(generics.ListCreateAPIView):
    queryset = Profile.objects.all()
    serializer_class = ProfileSerializer
    permission_classes = [permissions.IsAuthenticated]

    def perform_create(self, serializer):
        serializer.save(user=self.request.user)


class AuthorSettingsListCreateView(generics.ListCreateAPIView):
    queryset = AuthorSettings.objects.all()
    serializer_class = AuthorSettingsSerializer
    permission_classes = [permissions.IsAuthenticated]

    def perform_create(self, serializer):
        serializer.save(author=self.request.user)


class AuthorSettingsDetailView(generics.RetrieveUpdateDestroyAPIView):
    queryset = AuthorSettings.objects.all()
    serializer_class = AuthorSettingsSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        return AuthorSettings.objects.filter(author=self.request.user)


class BetaReaderListCreateView(generics.ListCreateAPIView):
    queryset = BetaReader.objects.all()
    serializer_class = BetaReaderSerializer
    permission_classes = [permissions.IsAuthenticated]

    def perform_create(self, serializer):
        serializer.save(user=self.request.user)


class ResourceInteractionListCreateView(generics.ListCreateAPIView):
    queryset = ResourceInteraction.objects.all()
    serializer_class = ResourceInteractionSerializer
    permission_classes = [permissions.IsAuthenticated]

    def perform_create(self, serializer):
        serializer.save(user=self.request.user)


class ResourceListCreateView(generics.ListCreateAPIView):
    queryset = Resource.objects.all()
    serializer_class = ResourceSerializer
    permission_classes = [permissions.IsAuthenticated]

    def perform_create(self, serializer):
        serializer.save(creator=self.request.user)


class ResourceInteractionDetailView(generics.RetrieveUpdateDestroyAPIView):
    queryset = ResourceInteraction.objects.all()
    serializer_class = ResourceInteractionSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        return ResourceInteraction.objects.filter(user=self.request.user)


class ResourceDetailView(generics.RetrieveUpdateDestroyAPIView):
    queryset = Resource.objects.all()
    serializer_class = ResourceSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        return Resource.objects.filter(creator=self.request.user)


class NotificationListCreateView(generics.ListCreateAPIView):
    queryset = Notification.objects.all()
    serializer_class = NotificationSerializer
    permission_classes = [permissions.IsAuthenticated]

    def perform_create(self, serializer):
        serializer.save(user=self.request.user)


class NotificationDetailView(generics.RetrieveUpdateDestroyAPIView):
    queryset = Notification.objects.all()
    serializer_class = NotificationSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        return Notification.objects.filter(user=self.request.user)


class KeywordListCreateView(generics.ListCreateAPIView):
    queryset = Keyword.objects.all()
    serializer_class = KeywordSerializer
    permission_classes = [permissions.IsAuthenticated]

    def perform_create(self, serializer):
        serializer.save()


class KeywordDetailView(generics.RetrieveUpdateDestroyAPIView):
    queryset = Keyword.objects.all()
    serializer_class = KeywordSerializer
    permission_classes = [permissions.IsAuthenticated]


class BetaReaderApplicationDetailView(generics.RetrieveUpdateDestroyAPIView):
    queryset = BetaReaderApplication.objects.all()
    serializer_class = BetaReaderApplicationSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        return BetaReaderApplication.objects.filter(user=self.request.user)


class FeedbackQuestionListCreateView(generics.ListCreateAPIView):
    queryset = FeedbackQuestion.objects.all()
    serializer_class = FeedbackQuestionSerializer
    permission_classes = [permissions.IsAuthenticated]

    def perform_create(self, serializer):
        serializer.save()


class FeedbackResponseDetailView(generics.RetrieveUpdateDestroyAPIView):
    queryset = FeedbackResponse.objects.all()
    serializer_class = FeedbackResponseSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        return FeedbackResponse.objects.filter(reader=self.request.user)


class FeedbackQuestionDetailView(generics.RetrieveUpdateDestroyAPIView):
    queryset = FeedbackQuestion.objects.all()
    serializer_class = FeedbackQuestionSerializer
    permission_classes = [permissions.IsAuthenticated]


class ManuscriptFeedbackPreferenceListCreateView(generics.ListCreateAPIView):
    queryset = ManuscriptFeedbackPreference.objects.all()
    serializer_class = ManuscriptFeedbackPreferenceSerializer
    permission_classes = [permissions.IsAuthenticated]

    def perform_create(self, serializer):
        serializer.save()


class ManuscriptFeedbackPreferenceDetailView(generics.RetrieveUpdateDestroyAPIView):
    queryset = ManuscriptFeedbackPreference.objects.all()
    serializer_class = ManuscriptFeedbackPreferenceSerializer
    permission_classes = [permissions.IsAuthenticated]


class FeedbackResponseListCreateView(generics.ListCreateAPIView):
    queryset = FeedbackResponse.objects.all()
    serializer_class = FeedbackResponseSerializer
    permission_classes = [permissions.IsAuthenticated]

    def perform_create(self, serializer):
        serializer.save(reader=self.request.user)


class InvalidKeyError(Exception):
    pass


class ManuscriptViewSet(viewsets.ModelViewSet):
    queryset = Manuscript.objects.all()
    serializer_class = ManuscriptSerializer


class UserViewSet(viewsets.ModelViewSet):
    queryset = User.objects.all()
    serializer_class = UserSerializer


class ProfileViewSet(viewsets.ModelViewSet):
    queryset = Profile.objects.all()
    serializer_class = ProfileSerializer


# main View
def home(request):
    return render(request, "main.html")


class SignUpView(APIView):
    permission_classes = [AllowAny]
    template_name = "signup.html"
    form_class = SignUpForm
    success_url = reverse_lazy("main")

    def get(self, request, *args, **kwargs):
        form = self.form_class()
        return render(request, self.template_name, {"form": form})

    def post(self, request):
        serializer = UserSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(
                {"success": True, "message": "User created successfully!"},
                status=status.HTTP_201_CREATED,
            )
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class SignInView(APIView):
    permission_classes = [AllowAny]
    template_name = "signin.html"
    form_class = SignInForm
    success_url = reverse_lazy("main")

    def get(self, request, *args, **kwargs):
        form = self.form_class()
        return render(request, self.template_name, {"form": form})

    def post(self, request, *args, **kwargs):
        form = self.form_class(request.POST)
        if form.is_valid():
            username = form.cleaned_data["username"]
            password = form.cleaned_data["password"]
            user = authenticate(request, username=username, password=password)
            if user is not None:
                login(request, user)
                return redirect(self.success_url)
            else:
                form.add_error(None, "Invalid username or password")
        return render(request, self.template_name, {"form": form})


class AuthorDashboardView(TemplateView):
    template_name = "author-dashboard.html"


class ReaderDashboardView(TemplateView):
    template_name = "reader-dashboard.html"


def signup_page(request):
    if request.method == "GET":
        return render(request, "signup.html")


def register_user(username, email, password):
    user = User.objects.create_user(username=username, email=email, password=password)
    return user


@csrf_exempt
def signup(request):
    if request.method == "GET":
        # Render the signup HTML form
        return render(request, "signup.html")

    if request.method == "POST":
        try:
            data = json.loads(request.body)
            # Log the incoming data for debugging
            logger.debug("Received signup data: %s", data)

            username = data.get("username")
            email = data.get("email")
            password = data.get("password")
            first_name = data.get("first_name")
            last_name = data.get("last_name")
            user_type = data.get("user_type")

            # Ensure all required fields are provided
            if not all([username, email, password, first_name, last_name, user_type]):
                logger.error("Missing required fields.")
                return JsonResponse({"message": "Missing required fields."}, status=400)

            # Create the user and log it
            user = User.objects.create_user(
                username=username, email=email, password=password
            )
            user.first_name = first_name
            user.last_name = last_name
            user.save()
            logger.debug("User created successfully: %s", user)

            return JsonResponse({"message": "User created successfully!"}, status=201)

        except Exception as e:
            logger.error("Error during user creation: %s", str(e))
            return JsonResponse({"message": f"Error: {str(e)}"}, status=400)

    return JsonResponse({"message": "Invalid request method."}, status=405)


@csrf_exempt
def signin(request):
    if request.method == "GET":
        # Render the signin HTML form
        return render(request, "signin.html")

    if request.method == "POST":
        try:
            body = json.loads(request.body)
        except json.JSONDecodeError as e:
            logger.error("JSON decode error: %s", e)
            return JsonResponse({"error": "Invalid JSON"}, status=400)

        username = body.get("username")
        password = body.get("password")
        user_type = body.get("user_type")

        # Authenticate user
        user = authenticate(username=username, password=password)

        if user is not None:
            login(request, user)
            profile = Profile.objects.get(user=user)
            if profile.user_type == "beta_reader":
                redirect_url = "/reader-dashboard/"
            elif profile.user_type == "admin":
                redirect_url = "/admin-dashboard/"
            else:
                redirect_url = "/author-dashboard/"
            logger.debug("User authenticated successfully: %s", username)

            # Check if the user has a profile
            if not hasattr(user, "profile"):
                logger.error("Profile missing for user: %s", username)
                return JsonResponse({"error": "Profile not found"}, status=404)

            # Verify the user type
            if user.profile.user_type != user_type:
                logger.warning(
                    "User type mismatch. Expected: %s, Actual: %s",
                    user_type,
                    user.profile.user_type,
                )

            return JsonResponse(
                {"message": "Login successful", "redirect": redirect_url}
            )
        else:
            return JsonResponse({"message": "Invalid credentials"}, status=401)
    else:
        return JsonResponse({"message": "Invalid request method"}, status=400)


@login_required
def logout_view(request):
    logout(request)
    return redirect("signin")


def signin_view(request):
    if request.method == "POST":
        username = request.POST.get("username")
        password = request.POST.get("password")
        user = authenticate(username=username, password=password)
        if user:
            if hasattr(user, "profile"):
                return JsonResponse({"message": "Login successful"}, status=200)
            else:
                return JsonResponse({"error": "Profile not found"}, status=404)
        return JsonResponse({"error": "Invalid credentials"}, status=401)


# def login(request):
#     return render(request, "signin.html")


def logout(request):
    return render(request, "logout.html")


# Reader Dashboard Views
def reader_dashboard(request):
    return render(request, "reader-dashboard.html")


def available_manuscripts(request):
    # Your view logic here
    return render(request, "available_manuscripts.html")


def reader_feedback(request):
    # Your view logic here
    return render(request, "reader_feedback.html")


def beta_reader_training(request):
    # Your view logic here
    return render(request, "beta_reader_training.html")


def beta_reader_performance_metrics(request):
    # Your view logic here
    return render(request, "beta_reader_performance_metrics.html")


def reader_profile(request):
    # Your view logic here
    return render(request, "reader_profile.html")


def reader_resource_library(request):
    # Your view logic here
    return render(request, "reader_resource_library.html")


def reader_payment_page(request):
    # Your view logic here
    return render(request, "reader_payment_page.html")


def reader_settings(request):
    # Your view logic here
    return render(request, "reader_settings.html")


# Author Dashboard Views
def author_dashboard(request):
    return render(request, "author-dashboard.html")


def author_dashboard(request):
    return render(request, "my-manuscripts.html")


def manuscript_submission(request):
    return render(request, "manuscript-submission.html")


def manuscript_success(request):
    return render(request, "manuscript-success.html")


def my_books(request):
    return render(request, "my-books.html")


def find_beta_readers(request):
    experience_query = request.GET.get("experience", "")
    genres_query = request.GET.getlist("genres")
    beta_readers = BetaReader.objects.all()

    if experience_query:
        beta_readers = beta_readers.filter(experience__icontains=experience_query)
    if genres_query:
        beta_readers = beta_readers.filter(genres__id__in=genres_query).distinct()

    return render(request, "find-beta-readers.html", {"beta_readers": beta_readers})


def beta_reader_list(request):
    beta_readers = BetaReader.objects.all()
    return render(request, "beta-reader-list.html", {"beta_readers": beta_readers})


def manuscript_submission(request):
    if request.method == "POST":
        form = ManuscriptSubmissionForm(request.POST, request.FILES)
        if form.is_valid():
            manuscript = form.save(commit=False)
            manuscript.author = request.user
            manuscript.save()
            form.save_m2m()

            return redirect("manuscript-success")


@login_required
def create_manuscript(request):
    if request.method == "POST":
        form = ManuscriptSubmissionForm(request.POST, request.FILES)
        if form.is_valid():
            manuscript = form.save(commit=False)
            manuscript.author = request.user
            manuscript.save()
            form.save_m2m()
            return redirect("manuscript-success")
    else:
        form = ManuscriptSubmissionForm()
    return render(request, "manuscript-submission2.html", {"form": form})


def feedback_form(request, manuscript_id):
    manuscript = get_object_or_404(Manuscript, id=manuscript_id)
    if request.method == "POST":
        feedback_data = request.POST
        Feedback.objects.create(
            manuscript=manuscript,
            user=request.user,
            plot=feedback_data.get("plot"),
            characters=feedback_data.get("characters"),
            pacing=feedback_data.get("pacing"),
            worldbuilding=feedback_data.get("worldbuilding"),
            comments=feedback_data.get("comments"),
        )
        return redirect("feedback-success")
    return render(request, "reader-feedback.html", {"manuscript": manuscript})


def feedback_summary(request):
    feedback = Feedback.objects.all()
    return render(request, "feedback-summary.html", {"feedback": feedback})


def author_resource_library(request):
    return render(request, "author_resource_library.html")


def author_community_groups(request):
    return render(request, "author_community_groups.html")


def author_profile(request):
    return render(request, "Author_Dashboard/author-profile.html")


def author_payment_page(request):
    return render(request, "author_payment_page.html")


def author_settings(request):
    return render(request, "author_settings.html")


@api_view(["GET"])
@permission_classes([IsAuthenticated])
def reader_dashboard(request):
    return HttpResponse("Reader Dashboard Content", content_type="text/html")


@api_view(["GET"])
@permission_classes([IsAuthenticated])
def author_dashboard(request):
    return HttpResponse("Author Dashboard Content", content_type="text/html")


@api_view(["GET"])
@permission_classes([IsAuthenticated])
def find_beta_readers(request):
    experience_query = request.GET.get("experience", "")
    genres_query = request.GET.getlist("genres")
    beta_readers = BetaReader.objects.all()

    if experience_query:
        beta_readers = beta_readers.filter(experience__icontains=experience_query)
    if genres_query:
        beta_readers = beta_readers.filter(genres__id__in=genres_query).distinct()

    serializer = BetaReaderSerializer(beta_readers, many=True)
    return JsonResponse(serializer.data, safe=False)


@api_view(["GET"])
@permission_classes([IsAuthenticated])
def beta_reader_list(request):
    beta_readers = BetaReader.objects.all()
    serializer = BetaReaderSerializer(beta_readers, many=True)
    return Response(serializer.data)


# Error 404 View
def error_404_view(request, exception):
    return render(request, "404.html", status=404)


@csrf_exempt
def save_token(request):
    if request.method == "POST":
        data = json.loads(request.body)
        token = data.get("token")
        user_id = data.get("user_id")
        if not token or not user_id:
            return JsonResponse({"error": "Token and user_id are required"}, status=400)
        try:
            user = User.objects.get(id=user_id)
            Token.objects.create(token=token, user=user)
            return JsonResponse({"message": "Token saved successfully"}, status=200)
        except User.DoesNotExist:
            return JsonResponse({"error": "User not found"}, status=404)
    return JsonResponse({"error": "Invalid request method"}, status=405)


import logging

logger = logging.getLogger(__name__)


@csrf_exempt
def authenticate_user(request):
    logger.info(f"Request to authenticate: {request.method} {request.body}")
    if request.method == "POST":
        try:
            data = json.loads(request.body)
            username = data.get("username")
            password = data.get("password")
            user_type = data.get("user_type")

            print(f"Received data: {data}")  # Log received data

            user = authenticate(username=username, password=password)
            if user is not None:
                return JsonResponse({"success": True, "user_type": user_type})
            else:
                return JsonResponse(
                    {"success": False, "message": "Invalid credentials"}, status=400
                )
        except json.JSONDecodeError as e:
            print(f"JSON decode error: {e}")  # Log JSON decode error
            return JsonResponse(
                {"success": False, "message": "Invalid JSON"}, status=400
            )
        except Exception as e:
            logger.error(f"Error in authenticate_user: {e}")
            return JsonResponse(
                {"success": False, "message": "Internal server error"}, status=500
            )
    return JsonResponse({"success": False}, status=400)


class UserCreate(generics.CreateAPIView):
    queryset = User.objects.all()
    serializer_class = UserSerializer


class SignInView(View):
    def get(self, request):
        return render(request, "signin.html")

    def post(self, request):
        username = request.POST["username"]
        password = request.POST["password"]

        user = authenticate(request, username=username, password=password)
        if user is not None:
            if user.is_active:
                login(request, user)
                if user.profile.user_type == "author":
                    return redirect("my_app:author_dashboard")
                else:
                    return redirect("my_app:reader_dashboard")
            else:
                messages.error(
                    request, "Your account is inactive. Please contact support."
                )
        else:
            messages.error(request, "Invalid username or password.")
        return render(request, "signin.html")


class SignUpView(View):
    def get(self, request):
        form = SignUpForm()
        return render(request, "signup.html", {"form": form})

    def post(self, request):
        form = SignUpForm(request.POST)
        if form.is_valid():
            user = form.save()
            if user.is_author:
                return redirect("author_dashboard")
            else:
                return redirect("reader_dashboard")
        return render(request, "signup.html", {"form": form})


@method_decorator(login_required, name="dispatch")
class LogoutView(View):
    def get(self, request):
        logout(request)
        return redirect("signin")
