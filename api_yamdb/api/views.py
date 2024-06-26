from django.contrib.auth import get_user_model
from django.core.exceptions import SuspiciousOperation
from django.db.models import Avg
from django.shortcuts import get_object_or_404
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework import filters, mixins, status, viewsets
from rest_framework.decorators import action
from rest_framework.generics import CreateAPIView
from rest_framework.pagination import PageNumberPagination
from rest_framework.permissions import (
    AllowAny,
    IsAuthenticated,
    IsAuthenticatedOrReadOnly,
)
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework_simplejwt.tokens import AccessToken

from api.filters import TitleFilter
from api.permissions import (
    IsAdmin,
    IsAdminOrReadOnly,
    IsAuthorModerAdminOrReadOnly,
)
from api.serializers import (
    CategoriesSerializer,
    CommentSerializer,
    GenresSerializer,
    GetTitleSerializer,
    ReviewSerializer,
    SignUpSerializer,
    TitleSerializer,
    TokenObtainWithConfirmationSerializer,
    UserSerializer,
)
from api.utils import send_confirmation_email
from reviews.models import Category, Genre, Review, Title


User = get_user_model()


class GetPostDeleteViewSet(
    mixins.CreateModelMixin,
    mixins.DestroyModelMixin,
    mixins.ListModelMixin,
    viewsets.GenericViewSet,
):
    pass


class CategoriesViewSet(GetPostDeleteViewSet):
    """Обрабатывает информацию о категориях."""

    queryset = Category.objects.all()
    serializer_class = CategoriesSerializer
    filter_backends = (filters.SearchFilter,)
    search_fields = ("name",)
    lookup_field = "slug"
    permission_classes = (IsAdminOrReadOnly,)


class GenresViewSet(GetPostDeleteViewSet):
    """Обрабатывает информацию о жанрах."""

    queryset = Genre.objects.all()
    serializer_class = GenresSerializer
    filter_backends = (filters.SearchFilter,)
    search_fields = ("name",)
    lookup_field = "slug"
    permission_classes = (IsAdminOrReadOnly,)


class TitleViewSet(viewsets.ModelViewSet):
    """Обрабатывает информацию о произведениях."""

    filter_backends = (filters.SearchFilter, DjangoFilterBackend)
    search_fields = ("name",)
    permission_classes = (IsAdminOrReadOnly,)
    filterset_class = TitleFilter
    http_method_names = [
        m for m in viewsets.ModelViewSet.http_method_names if m not in ["put"]
    ]

    def get_queryset(self):
        """Добавить поле "rating" в queryset."""
        return Title.objects.annotate(rating=Avg("reviews__score")).order_by(
            "-year"
        )

    def get_serializer_class(self):
        """Заменить сериализатор."""
        if self.action in ("list", "retrieve"):
            return GetTitleSerializer
        return TitleSerializer


class UsersViewSet(viewsets.ModelViewSet):
    """Создаёт новых пользователей."""

    serializer_class = UserSerializer
    permission_classes = (IsAdmin,)
    pagination_class = PageNumberPagination
    lookup_field = "username"
    filter_backends = [filters.SearchFilter]
    search_fields = ["username"]

    def get_queryset(self):
        """Получить queryset."""
        return User.objects.all()

    def update(self, request, *args, **kwargs):
        """Обновить профиль пользователя."""
        if request.method == "PUT":
            return Response(status=status.HTTP_405_METHOD_NOT_ALLOWED)
        return super().update(request, *args, **kwargs)

    @action(
        methods=["GET", "PATCH"],
        detail=False,
        url_path="me",
        permission_classes=(IsAuthenticated,),
    )
    def get_update_me(self, request):
        """Получить и обновить информацию о текущем пользователе."""
        serializer = self.get_serializer(
            request.user, data=request.data, partial=True
        )
        if serializer.is_valid():
            if self.request.method == "PATCH":
                serializer.validated_data.pop("role", None)
            serializer.save()
            return Response(serializer.data, status=status.HTTP_200_OK)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class TokenObtainWithConfirmationView(CreateAPIView):
    """Создаёт токен по запросу пользователя."""

    serializer_class = TokenObtainWithConfirmationSerializer
    permission_classes = (AllowAny,)

    def get_queryset(self):
        """Получить объект пользователя."""
        return get_object_or_404(User, username=self.kwargs["username"])

    def create(self, request, *args, **kwargs):
        """Создать токен."""
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        username = serializer.validated_data["username"]
        confirmation_code = serializer.validated_data["confirmation_code"]

        if username == "me":
            return Response(status=status.HTTP_400_BAD_REQUEST)

        user = get_object_or_404(User, username=username)

        if confirmation_code == user.confirmation_code:
            token = AccessToken.for_user(user)
            return Response(
                {"token": str(token)},
                status=status.HTTP_200_OK,
            )
        return Response(status=status.HTTP_400_BAD_REQUEST)


class SignupView(APIView):
    """Регистрирует нового пользователя."""

    def post(self, request, *args, **kwargs):
        """Проверить и зарегистрировать нового пользователя."""

        username = request.data.get("username", None)
        email = request.data.get("email", None)

        if username == "me":
            return Response(
                {"detail": 'Недопустимое значение "me" для username'},
                status=status.HTTP_400_BAD_REQUEST,
            )

        # Проверить, существует ли пользователь с таким именем пользователя.
        existing_user = User.objects.filter(username=username).first()
        if existing_user:
            if existing_user.email != email:
                return Response(
                    {
                        "detail": (
                            "Несоответствие email для зарегистрированного"
                            " пользователя"
                        )
                    },
                    status=status.HTTP_400_BAD_REQUEST,
                )
            return Response(
                {"detail": "Пользователь уже зарегистрирован"},
                status=status.HTTP_200_OK,
            )

        serializer = SignUpSerializer(data=request.data)
        if serializer.is_valid():
            user = serializer.save()

            # Отправить письмо с кодом.
            confirmation_code = send_confirmation_email(user.email)

            user.confirmation_code = confirmation_code
            user.save()

            return Response(serializer.data, status=status.HTTP_200_OK)

        errors = serializer.errors
        return Response(errors, status=status.HTTP_400_BAD_REQUEST)


class ReviewViewSet(viewsets.ModelViewSet):
    """Обрабатывает информацию об отзывах."""

    serializer_class = ReviewSerializer
    permission_classes = (
        IsAuthenticatedOrReadOnly,
        IsAuthorModerAdminOrReadOnly,
    )
    http_method_names = [
        m for m in viewsets.ModelViewSet.http_method_names if m not in ["put"]
    ]

    def get_title(self):
        """Получить произведение."""
        title = self.kwargs.get("title_id")
        return get_object_or_404(Title, id=title)

    def get_queryset(self):
        """Вернуть все отзывы к произведению."""
        title = self.get_title()
        queryset = title.reviews.all()
        return queryset

    def perform_create(self, serializer):
        """Добавить автора отзыва и id произведения."""
        title = self.kwargs.get("title_id")
        if Review.objects.filter(
            title=title, author=self.request.user
        ).exists():
            raise SuspiciousOperation("Invalid JSON")
        if serializer.is_valid():
            serializer.save(
                author=self.request.user, title=self.get_title()
            )

    def create(self, request, *args, **kwargs):
        return super().create(request, *args, **kwargs)


class CommentViewSet(viewsets.ModelViewSet):
    """Обрабатывает информацию о комментариях."""

    serializer_class = CommentSerializer
    permission_classes = (
        IsAuthenticatedOrReadOnly,
        IsAuthorModerAdminOrReadOnly,
    )
    http_method_names = [
        m for m in viewsets.ModelViewSet.http_method_names if m not in ["put"]
    ]

    def get_review(self):
        """Получить отзыв."""
        review_id = self.kwargs.get("review_id")
        return get_object_or_404(Review, id=review_id)

    def get_queryset(self):
        """Вернуть все комментарии к отзыву."""
        review = self.get_review()
        return review.comments.all()

    def perform_create(self, serializer):
        """Добавить автора комментария и id отзыва."""
        serializer.save(author=self.request.user, review_id=self.get_review())
