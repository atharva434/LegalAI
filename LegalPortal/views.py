from django.shortcuts import render,redirect
from django.contrib.auth import authenticate,login
from django.contrib.auth.decorators import login_required
from .forms import ClientRegistrationForm, LawyerRegistrationForm,UserInfo
from django.contrib.auth.models import User, Group
from .models import Lawyer,Transactions,Client
from datetime import datetime,timedelta
from django.contrib import auth
from django.utils import timezone
import random
import razorpay
from .search import predict,get_chain
from .documentdrafting import nda_sections,add,amend,intro
from django.template.loader import get_template
from django.template import Context
from xhtml2pdf import pisa
from io import BytesIO
from django.core.files.storage import FileSystemStorage
from langchain.document_loaders import PyPDFLoader
from django.http import JsonResponse
# Create your views here.
# def is_admin(user):
#     return user.groups.filter(name='ADMIN').exists()

sections={}
introduction=""
company_name=""
emp_name=""



def get_lawyers_by_type(request):
    lawyer_type = request.GET.get('lawyer_type')
    lawyers = Lawyer.objects.filter(lawyer_type=lawyer_type).values_list('lawyer_name', flat=True)
    lawyer_names = list(lawyers)
    return JsonResponse({'lawyer_names': lawyer_names})

def edit_document(request,operation):

    global sections
    try:
        if operation=="add":
            points=request.POST["points"]
            section_name=request.POST["section_name"]
            key,value=add(doc_type="NDA",section_name=section_name, section_desc=points)
            temp={section_name:value}
            sections.update(temp)

        elif operation=="amend":
            points=request.POST["points"]
            section_name=request.POST["section_name"]
            sections[section_name]=amend(doc_type="NDA", section_name=section_name, add=points, sections=sections)


        elif operation=="delete":
            section_name=request.POST["section_name"]
            sections.pop(section_name)

        return render(request,"NDA.html",{"sections":sections,"intro":introduction,"doc_type":"NON-DISCLOSURE AGREEMENT","options":sections.keys(),"emp_name":emp_name,"company_name":company_name})
    except:
        return render(request,"NDA.html",{"sections":sections,"intro":introduction,"doc_type":"NON-DISCLOSURE AGREEMENT","options":sections.keys(),"emp_name":emp_name,"company_name":company_name})





def nda(request):
    global sections
    global introduction,company_name,emp_name
    if request.method=="POST":
        emp_name=request.POST["emp_name"]
        company_name=request.POST["company_name"]
        emp_title=request.POST["emp_title"]
        company_title=request.POST["company_title"]
        date=request.POST["Date"]
        emp_address=request.POST["emp_address"]
        company_address=request.POST["company_address"]
        # intro=introduction(emp_name, emp_title, company_name, company_title, date)
        # sconclusion=conclusion()
        introduction=intro(emp_name,company_name,emp_title,company_title,date)["nda"]
        sections=nda_sections()
        return render(request,"NDA.html",{"sections":sections,"intro":introduction,"doc_type":"NON-DISCLOSURE AGREEMENT","options":sections.keys(),"emp_name":emp_name,"company_name":company_name})
    return render(request,"NDA.html")
    

def pdf_generation(request):

    template = get_template("templates/pdf.html")
    context = {"sections":sections,"intro":introduction}
    html  = template.render(context)
    result = open(f"static/Agreements/agreement_{request.user.userid}.pdf", 'wb') # Changed from file to filename
    pdf = pisa.pisaDocument(BytesIO(html.encode("UTF-8")), result)
    result.close()
    return render(request,"nda.html",{"filepath":f"static/Agreements/agreement_{request.user.userid}.pdf"})

def feedback(request,id):
    feedback=request.POST["feedback"]
    rating=request.POST["rating"]
    # # Transaction=Transactions.objects.get(id=id)
    # Transaction.feedback=feedback
    # Transaction.rating=rating
    # Transaction.save()
    return 


def convert(time_str,date_str):

    # Combine date and time into a datetime object
    date_format = "%Y-%m-%d"  # Adjust the format as per your HTML input format
    time_format = "%H:%M"  # Adjust the format as per your HTML input format

    # Convert date and time strings to datetime objects
    date_obj = datetime.strptime(date_str, date_format)
    time_obj = datetime.strptime(time_str, time_format).time()

    # Create a full datetime object by combining the date and time
    datetime_obj = datetime.combine(date_obj, time_obj)
    return datetime_obj

def is_client(user):
    return user.groups.filter(name='Client').exists()
def is_lawyer(user):
    return user.groups.filter(name='Lawyer').exists()

def dashboard_redirect(request):
    if is_client(request.user):
        return redirect("home")
    
    elif is_lawyer(request.user):
        return redirect("lawyer_appointment_dashboard")
    else:
        return redirect("client_registration")

@login_required(login_url='/user_login')
def lawyer_appointment_dashboard(request):
    if is_lawyer(request.user):
        user=request.user.id
        # print(request.user)
        print(user)
        lawyer=Lawyer.objects.get(user_id=user)
        # print(lawyer.values())
        pending=Transactions.objects.filter(Lawyerid=user,completed=False).values()
        completed=Transactions.objects.filter(Lawyerid=user,completed=True).values()
        
        
        # print(pending)
        for j in completed:
            user_id=j["userid"]
            print(user_id)
            client_info=Client.objects.filter(user_id=user_id)
            client_info = list(client_info.values())
            j.update(client_info[0])

        return render(request,"Dashboard_lawyer.html",{"pending":pending,"completed":completed,"lawyer":lawyer})
    return redirect("user_login")

@login_required(login_url='/user_login')
def client_appointment_dashboard(request):
    if is_client(request.user):
        user=request.user.id
        # print(request.user)
        print(user)
        lawyer=Client.objects.get(user=user)
        # print(lawyer.values())
        # pending=Transactions.objects.filter(userid=user,completed=False).values()
        # completed=Transactions.objects.filter(userid=user,completed=True).values()
        
        
        # # print(pending)
        # for j in completed:
        #     user_id=j["userid"]
        #     print(user_id)
        #     client_info=Lawyer.objects.filter(user=user_id)
        #     client_info = list(client_info.values())
        #     j.update(client_info[0])

        return render(request,"Dashboard_client.html",{"lawyer":lawyer})
    return redirect("user_login")


def complete_appointment(request,pk):
    print(type(id))
    
    transaction=Transactions.objects.get(id=pk)
    # print(transaction.values())
    transaction.completed=True
    transaction.save()
    return redirect("lawyer_appointment_upcoming")



@login_required(login_url='/user_login')
def lawyer_appointment_upcoming(request):
    if is_lawyer(request.user):
        user=request.user.id
        # print(request.user)
        print(user)

        pending=Transactions.objects.filter(Lawyerid=user,completed=False).values()
        for i in pending:
            # print(i)
            user_id=i["userid"]
            # print(user_id)
            client_info=Client.objects.filter(user_id=user_id)
            client_info = list(client_info.values())
            # print(client_info)
            id=i["id"]
            i.update(client_info[0])
            i["id"]=id
            i["day"] = i["start_time"].day
            i["month"]= i["start_time"].strftime("%b")
            i["start_time"]=i["start_time"].time()
            i["end_time"]=i["end_time"].time()
            # i = date_object.year
        print(pending)
        return render(request,"upcoming_lawyer.html",{"pending":pending})
    return redirect("user_login")

@login_required(login_url='/user_login')   
def client_appointment_upcoming(request):
    if is_client(request.user):
        user=request.user.id
        # print(request.user)
        print(user)
        pending=Transactions.objects.filter(userid=user,completed=False).values()
        print(pending)
        for i in pending:
            # print(i)
            user_id=i["Lawyerid"]
            print(user_id)
            client_info=Lawyer.objects.filter(user=user_id)
            client_info = list(client_info.values())
            print(client_info)
            i.update(client_info[0])

            i["day"] = i["start_time"].day
            i["month"]= i["start_time"].strftime("%b")
            i["start_time"]=i["start_time"].time()
            i["end_time"]=i["end_time"].time()
            # i = date_object.year
        print(pending)
        return render(request,"upcoming_client.html",{"pending":pending})
    
@login_required(login_url='/user_login')
def lawyer_appointment_completed(request):
    if is_lawyer(request.user):
        user=request.user.id
        # print(request.user)
        print(user)
        completed=Transactions.objects.filter(Lawyerid=user,completed=True).values()
        for i in completed:
            print(i)
            user_id=i["userid"]
            print(user_id)
            client_info=Client.objects.filter(user_id=user_id)
            client_info = list(client_info.values())
            print(client_info)
            i.update(client_info[0])
            i["day"] = i["start_time"].day
            i["month"]= i["start_time"].strftime("%b")
            i["start_time"]=i["start_time"].time()
            i["end_time"]=i["end_time"].time()
        return render(request,"completed_appointment_lawyer.html",{"completed":completed})
    return redirect("user_login")
def client_appointment_completed(request):
    if is_client(request.user):
        user=request.user.id
        # print(request.user)
        print(user)
        completed=Transactions.objects.filter(userid=user,completed=True).values()
        for i in completed:
            print(i)
            user_id=i["Lawyerid"]
            print(user_id)
            client_info=Lawyer.objects.filter(user_id=user_id)
            client_info = list(client_info.values())
            print(client_info)
            i.update(client_info[0])
            i["day"] = i["start_time"].day
            i["month"]= i["start_time"].strftime("%b")
            i["start_time"]=i["start_time"].time()
            i["end_time"]=i["end_time"].time()
        return render(request,"completed_appointment_client.html",{"completed":completed})
    return redirect("user_login")


@login_required(login_url='/user_login')
# def client_appointment(request):
#     if is_client(request.user):
#         user=request.user.id
#         pending=Transactions.objects.filter(userid=user,completed=False).values()
#         completed=Transactions.objects.filter(userid=user,completed=True).values()
#         for i in pending:
#             user_id=i["Lawyerid"]
#             Lawyer_info=Lawyer.objects.filter(Lawyerid=user_id)
#             Lawyer_info = list(Lawyer_info.values())
#             i.update(Lawyer_info[0])
#         # print(pending)
#         for j in completed:
#             user_id=j["Lawyerid"]
#             Lawyer_info=Lawyer.objects.filter(Lawyerid=user_id)
#             Lawyer_info = list(Lawyer_info.values())
#             j.update(Lawyer_info[0])

#         return render(request,"lawyer.html",{"pending":pending,"completed":completed})
#     return redirect("user_login")
    



@login_required(login_url='/user_login')
def client_dashboard(request):
    if is_client(request.user):
        if request.method == "POST":
            print(request.POST)
            lawyer_type=request.POST["lawyer_type"]
            query=request.POST["query"]
            start_time=request.POST["start_time"]
            
            date=request.POST["date"]
            duration=request.POST["duration"]
            duration=int(duration)
            duration_to_add = timedelta(days=0, hours=duration)
            lawyerlist = Lawyer.objects.filter(lawyertype=lawyer_type)
            lawyer_list = lawyerlist.values_list("user_id", flat = True)
            start_time = convert(start_time,date)
            end_time = start_time + duration_to_add
            amount =500*duration
            notavalawyers=Transactions.objects.filter(Lawyerid__in = lawyer_list,completed=False,start_time__range=[start_time,end_time]) | Transactions.objects.filter(Lawyerid__in = lawyer_list,completed=False,end_time__range=[start_time,end_time])
            lawyer_list_not_avalaible = notavalawyers.values_list("Lawyerid", flat = True)
            print(lawyer_list_not_avalaible)
            available=set(lawyer_list)-set(lawyer_list_not_avalaible)
            print(available)
            chooseLawyer = random.choice(list(available))
            print(chooseLawyer)
            client = razorpay.Client(auth=('rzp_test_A0pbku9Y5vKP6Z', 'V70rauYt6WIeDQi7vfMmhQD5')) # create Razorpay client

            response_payment = client.order.create(dict(amount=amount*100, currency='INR'))# create order
            order_id = response_payment['id']
            order_status = response_payment['status']
            if order_status == 'created':
                transaction=Transactions(query=query,order_id=order_id,start_time=start_time,end_time=end_time,Lawyerid=chooseLawyer,userid=request.user.id,amount=500,completed=False,paid=False)
                transaction.save()  

                # response_payment["name"]=request.user.name
                # response_payment["number"]=request.user.phno
                return render(request,"coffee_payment.html",{"payment":response_payment}) 

        lawyersType=Lawyer.objects.all()
        lawyersType=lawyersType.values_list("lawyertype", flat = True)  
        lawyersType = list(set(lawyersType))
        print(lawyersType)
        return render(request,"client.html",{'lawyersType':lawyersType})
    return redirect("user_login")

def payment_status(request):
    responses = request.POST['razorpay_order_id']
    response=request.POST
    print(responses)
    params_dict = {
        'razorpay_order_id': response['razorpay_order_id'],
        'razorpay_payment_id': response['razorpay_payment_id'],
        'razorpay_signature': response['razorpay_signature']
    }

    # client instance
    client = razorpay.Client(auth=('rzp_test_A0pbku9Y5vKP6Z', 'V70rauYt6WIeDQi7vfMmhQD5'))
    status = client.utility.verify_payment_signature(params_dict)
    cold_coffee = Transactions.objects.get(order_id=response['razorpay_order_id'])
    cold_coffee.transactionid = response['razorpay_payment_id']
    # cold_coffee.userid=request.user.id
    cold_coffee.paid = True
    cold_coffee.save()
    return render(request,"home.html")
def user_login(request):
    global sections
    sections={}
    if request.method == "POST":
        username = request.POST['username']
        password = request.POST['password']
        user = authenticate(username=username, password=password)
        if user is not None:
            login(request,user)
            return redirect("dashboard_redirect")
        else:
            return redirect("user_login") 
    return render(request,"client_login.html")


def client_registration(request):
    if request.method == 'POST':
        regform = ClientRegistrationForm(request.POST)
        userinfo=UserInfo(request.POST)
        if userinfo.is_valid() and regform.is_valid():
            user = userinfo.save()
            user.set_password(user.password)
            user.save()
            patientForm = regform.save(commit=False)
            patientForm.user = user
            patientForm.save()
            my_patient_group = Group.objects.get_or_create(name='Client')
            my_patient_group[0].user_set.add(user)
            auth.login(request,user)
            return redirect('home') # Replace with the client dashboard URL
    
    return render(request, 'client_registration.html')

def lawyer_registration(request):
    print(request.method)
    if request.method == 'POST':
        regform = LawyerRegistrationForm(request.POST)
        userinfo=UserInfo(request.POST)
        print(userinfo.is_valid())
        print(regform.is_valid())
        if userinfo.is_valid() and regform.is_valid():
            print("valid")
            user = userinfo.save()
            user.set_password(user.password)
            user.save()
            patientForm = regform.save(commit=False)
            patientForm.user = user
            patientForm.save()
            my_patient_group = Group.objects.get_or_create(name='Lawyer')
            my_patient_group[0].user_set.add(user)
            auth.login(request,user)
            return redirect('lawyer_appointment_dashboard') # Replace with the client dashboard URL
    
    return render(request, 'lawyer_registration.html')

responses={}
responses_doc={}
qa_model=None
@login_required(login_url='/user_login')
def chatbot(request):
    global responses
    if request.method == 'POST':
        print("hi")            
        inp= request.POST.get('inp')
        print(inp)
        predictions=predict(inp)
        responses[inp]=predictions
        print(responses)
        return render(request,"chatbot.html",{"responses":responses})
    responses={}
    return render(request,"chatbot.html")

def get_qa_model(request):
    global qa_model
    fileObj=request.FILES['filePath']
    fs=FileSystemStorage()
    filePathName=fs.save(fileObj.name,fileObj)
    filePathName=fs.url(filePathName)
    testpdf='.'+filePathName
    loader = PyPDFLoader(testpdf)
    pages = loader.load_and_split()
    qa_model=get_chain(pages)
    print(qa_model)
    return render(request,"documentChatbot.html",{"document":True})

def chat_with_doc(request):

    global responses_doc
    if qa_model:
        if request.method=="POST":
            query=request.POST["inp"]
            result = qa_model({"question": query})
            source = result['source_documents']
            pages = set()
            for i in source:
                pages.add(i.metadata['page'])

            print(pages)
            result["source"]=list(pages)
            responses_doc[query]=result
            print(responses_doc)
            return render(request,"documentChatbot.html",{"responses":responses_doc,"document":True})
        else:
            responses_doc={}
    responses_doc={}
    return render(request,"documentChatbot.html")
    

def home(request):
    return render(request,"home.html")
