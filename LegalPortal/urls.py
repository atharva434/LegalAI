from django.urls import path,include
from LegalPortal import views
from django.contrib.auth.views import LogoutView

urlpatterns = [
    path("",views.home),
    path("client_registration",views.client_registration, name='client_registration'),
    path("logout",LogoutView.as_view(next_page="user_login"),name="logout"),
    path("lawyer_registration",views.lawyer_registration, name='lawyer_registration'),
    path("user_login",views.user_login, name='user_login'),
    path("dashboad_redirect",views.dashboard_redirect,name='dashboard_redirect'),
    path("client_dashboard",views.client_dashboard, name='client_dashboard'),
    # path("lawyer_dashboard",views.lawyer_dashboard, name='lawyer_dashboard'),
    path('get_lawyers_by_type/', views.get_lawyers_by_type, name='get_lawyers_by_type'),
    path('payment-status', views.payment_status, name='payment-status'),
    path('chatbot', views.chatbot, name='chatbot'),
    path('documentChatbot', views.chat_with_doc, name='chat_with_doc'),
    path('get_qa_model', views.get_qa_model, name='get_qa_model'),
    path('nda', views.nda, name='nda'),
    path("client_appointment",views.client_appointment_dashboard, name='client_appointment_dashboard'),
    path("lawyer_appointment",views.lawyer_appointment_dashboard, name='lawyer_appointment_dashboard'),
    path("client_appointment_upcoming",views.client_appointment_upcoming, name='client_appointment_upcoming'),
    path("lawyer_appointment_upcoming",views.lawyer_appointment_upcoming, name='lawyer_appointment_upcoming'),
    path("client_appointment_completed",views.client_appointment_completed, name='client_appointment_completed'),
    path("lawyer_appointment_completed",views.lawyer_appointment_completed, name='lawyer_appointment_completed'),
    path("",views.home,name="home"),
    path("edit_document/<operation>",views.edit_document,name="edit_document"),
    path("complete/<int:pk>",views.complete_appointment,name="complete")
]