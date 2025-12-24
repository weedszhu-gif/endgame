
from django.urls import path, include
from rest_framework.routers import DefaultRouter
from . import views

# 创建路由器并注册视图集
router = DefaultRouter()
router.register(r'questions', views.QuestionViewSet)
router.register(r'hint-rules', views.HintRuleViewSet)
router.register(r'answer-records', views.AnswerRecordViewSet)

# API URL由路由器自动确定
urlpatterns = [
    path('', include(router.urls)),
]
