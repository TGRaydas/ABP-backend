from django.urls import path
from .views import *

urlpatterns = [
    path('session/', SessionView.as_view(), name='session'),
    path('users/', UserView.as_view(), name='user'),
    path('hello/', HelloView.as_view(), name='hello'),
    path('projects/', ProjectView.as_view(), name='projects'),
    path('product', ProductView.as_view(), name='products'),
    path('product/steps', ProductStepView.as_view(), name='productstep'),
    path('step', ProductStepView.as_view(), name='step'),
    path('project/view/', ProjectGraph.as_view(), name='projectview'),
    path('project/group/', GroupView.as_view(), name='projectgroup'),
    path('project/user/group/', UserGroupView.as_view(), name='usergroup'),
    path('files/', FilesView, name='files'),
    path('assigment-delivery/', AssignmentDeliveryView, name='files'),
]
