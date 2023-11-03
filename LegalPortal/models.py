from django.db import models
from django.contrib.auth.models import User
# # Create your models here.
class Client(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    name=models.CharField(max_length=100)
    phno=models.BigIntegerField()
    email=models.EmailField()
    state=models.CharField(max_length=100)
    Pincode=models.BigIntegerField()

class Lawyer(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    name=models.CharField(max_length=100)
    lawyertype=models.CharField(max_length=50)
    phno=models.BigIntegerField()
    email=models.EmailField()
    Pincode=models.BigIntegerField()
    enrollmentno=models.BigIntegerField()
    enrollmentstate=models.CharField(max_length=100)
    upi_id=models.CharField(max_length=100)

class Transactions(models.Model):
    userid=models.CharField(max_length=100)
    Lawyerid=models.IntegerField(max_length=100)
    amount=models.IntegerField()
    start_time=models.DateTimeField()
    end_time=models.DateTimeField()
    completed=models.BooleanField()
    feedback=models.TextField(blank=True,null=True)
    rating=models.IntegerField(blank=True,null=True)
    paid =models.BooleanField()
    query = models.TextField()
    order_id = models.CharField(max_length=100, blank=True)
    transactionid=models.CharField(max_length=100,blank=True,null=True)




    