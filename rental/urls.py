from django.urls import path, include
from rental import views
from dynamic_rest.routers import DynamicRouter

router = DynamicRouter()
friends = router.register(r'friends', views.FriendViewSet)
router.register(r'belongings', views.BelongingViewSet)
router.register(r'borrowings', views.BorrowedViewSet)

urlpatterns = [
    path('', include(router.urls)),
    path('signin/', views.signin),
    path('user-info/', views.user_info),
    path('users/', views.UserCreate.as_view(), name='account-create'),
]
