from django.shortcuts import get_object_or_404
from rest_framework import filters, status, viewsets
from rest_framework.decorators import action
from rest_framework.pagination import LimitOffsetPagination
from rest_framework.permissions import IsAuthenticated, IsAuthenticatedOrReadOnly
from rest_framework.response import Response

from .models import Achievement, Cat, Shelter, ShelterEmployee, User
from .permissions import IsShelterOwner, IsShelterStaff
from .serializers import (
    AchievementSerializer,
    CatSerializer,
    ShelterEmployeeSerializer,
    ShelterSerializer,
    UserSerializer,
)


class CatViewSet(viewsets.ModelViewSet):
    queryset = Cat.objects.all()
    serializer_class = CatSerializer

    def perform_create(self, serializer):
        serializer.save(owner=self.request.user)


class UserViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = User.objects.all()
    serializer_class = UserSerializer


class AchievementViewSet(viewsets.ModelViewSet):
    queryset = Achievement.objects.all()
    serializer_class = AchievementSerializer


class ShelterPagination(LimitOffsetPagination):
    default_limit = 10
    max_limit = 100


class ShelterViewSet(viewsets.ModelViewSet):
    queryset = Shelter.objects.all()
    serializer_class = ShelterSerializer
    permission_classes = (IsAuthenticatedOrReadOnly, IsShelterOwner)
    pagination_class = ShelterPagination
    filter_backends = (filters.SearchFilter, filters.OrderingFilter)
    search_fields = ('name', 'address')
    ordering_fields = ('name', 'created_at')
    ordering = ('-created_at',)

    def perform_create(self, serializer):
        shelter = serializer.save(owner=self.request.user)
        ShelterEmployee.objects.create(
            shelter=shelter, user=self.request.user, role='owner')

    # --- custom action: POST /shelters/{id}/join/ ---
    @action(detail=True, methods=['post'],
            permission_classes=[IsAuthenticated])
    def join(self, request, pk=None):
        """Пользователь подаёт заявку на вступление в приют как сотрудник."""
        shelter = self.get_object()
        if ShelterEmployee.objects.filter(
                shelter=shelter, user=request.user).exists():
            return Response(
                {'detail': 'Вы уже являетесь сотрудником этого приюта.'},
                status=status.HTTP_400_BAD_REQUEST)
        ShelterEmployee.objects.create(
            shelter=shelter, user=request.user, role='employee')
        return Response(
            {'detail': 'Вы успешно присоединились к приюту.'},
            status=status.HTTP_201_CREATED)

    # --- nested: GET /shelters/{id}/cats/ ---
    @action(detail=True, methods=['get'])
    def cats(self, request, pk=None):
        shelter = self.get_object()
        cats_qs = shelter.cats.all()
        serializer = CatSerializer(cats_qs, many=True,
                                   context={'request': request})
        return Response(serializer.data)

    # --- nested: GET|POST /shelters/{id}/employees/ ---
    @action(detail=True, methods=['get', 'post'],
            permission_classes=[IsAuthenticatedOrReadOnly, IsShelterStaff])
    def employees(self, request, pk=None):
        shelter = self.get_object()
        if request.method == 'GET':
            qs = shelter.employees.select_related('user')
            serializer = ShelterEmployeeSerializer(qs, many=True)
            return Response(serializer.data)
        # POST — добавить сотрудника (только owner/moderator)
        serializer = ShelterEmployeeSerializer(
            data=request.data,
            context={'request': request, 'shelter': shelter})
        serializer.is_valid(raise_exception=True)
        serializer.save(shelter=shelter)
        return Response(serializer.data, status=status.HTTP_201_CREATED)


class ShelterEmployeeViewSet(viewsets.ModelViewSet):
    """Управление конкретными сотрудниками приюта."""
    serializer_class = ShelterEmployeeSerializer
    permission_classes = (IsAuthenticatedOrReadOnly, IsShelterStaff)

    def get_queryset(self):
        return ShelterEmployee.objects.filter(
            shelter_id=self.kwargs['shelter_pk']
        ).select_related('user', 'shelter')

    def get_serializer_context(self):
        ctx = super().get_serializer_context()
        ctx['shelter'] = get_object_or_404(
            Shelter, pk=self.kwargs['shelter_pk'])
        return ctx

    def perform_create(self, serializer):
        shelter = get_object_or_404(Shelter, pk=self.kwargs['shelter_pk'])
        serializer.save(shelter=shelter)
