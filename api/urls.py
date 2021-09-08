from django.urls import path
from .views import *

urlpatterns = [
    path('hello/', HelloView.as_view(), name='hello'),
    path('projects/', ProjectView.as_view(), name='projects'),
    path('product', ProductView.as_view(), name='products'),
    path('product/steps', ProductStepView.as_view(), name='productstep'),
    path('step', ProductStepView.as_view(), name='step'),
    path('project/view/', ProjectGraph.as_view(), name='projectview'),
    path('files/', FilesView.as_view(), name='files'),
    
]
