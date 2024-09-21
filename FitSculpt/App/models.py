from datetime import date, datetime
from django.db import models

class Client(models.Model):
    user_id = models.AutoField(primary_key=True)
    name = models.CharField(max_length=100)  
    username = models.CharField(max_length=50, unique=True)
    password = models.CharField(max_length=20)
    email = models.EmailField(max_length=50, unique=True)
    phone = models.CharField(max_length=10) 
    dob = models.DateField() 
    gender=models.CharField(max_length=10)
    age=models.IntegerField(blank=True, null=True)
    height=models.FloatField()
    weight=models.FloatField()
    food_type=models.CharField(max_length=20)
    date_joined=models.DateField(auto_now_add=True) 

    class Meta:
        managed = False
        db_table = 'client'

    def __str__(self):
        return self.username
    @property
    def calculate_age(self):
        today = datetime.today().date()
        age = today.year - self.dob.year - ((today.month, today.day) < (self.dob.month, self.dob.day))
        return age

from django.db import models

class Plan(models.Model):
    plan_id = models.AutoField(primary_key=True)  # Auto-incrementing primary key
    plan_name = models.CharField(max_length=100)  # Name of the plan
    amount = models.DecimalField(max_digits=10, decimal_places=2)  # Amount for the plan
    description = models.TextField()  # Description of the plan
    service_id = models.IntegerField()  # Assuming service_id relates to some service in your application
    
    class Meta:
        managed = False
        db_table = 'tbl_plans'
    def __str__(self):
        return self.plan_name

from django.db import models
from django.utils import timezone


class Payment(models.Model):
    payment_id = models.AutoField(primary_key=True)
    plan_id = models.IntegerField() 
    user_id=models.IntegerField()
    payment_date = models.DateTimeField(default=timezone.now)  # Use DateTimeField to store both date and time
    mode = models.CharField(max_length=50) 
    status = models.CharField(max_length=50)  
    class Meta:
        managed = False
        db_table = 'tbl_payment'
    def __str__(self):
        return f"Payment {self.payment_id} - {self.status}"


class FitnessManager(models.Model):
    user_id = models.AutoField(primary_key=True) 
    name = models.CharField(max_length=50)
    email = models.CharField(max_length=50)
    phone = models.CharField(max_length=10)
    qualification_id = models.IntegerField()
    designation_id = models.IntegerField()
    username = models.CharField(max_length=20, unique=True)
    password = models.CharField(max_length=20)
    certificate_proof = models.FileField(upload_to='certificates/', blank=True, null=True)
    date_joined=models.DateField(auto_now_add=True) 

    class Meta:
        managed = False
        db_table = 'tbl_fitness_manager'
    def __str__(self):
        return self.name
    
class Qualifications(models.Model):
    qualification_id=models.AutoField(primary_key=True)
    qualification=models.CharField(max_length=50)
    certification=models.CharField(max_length=50)
    class Meta:
        managed = False
        db_table = 'tbl_qualifications'

class Designations(models.Model):
    designation_id=models.AutoField(primary_key=True)
    designation=models.CharField(max_length=50)

    class Meta:
        managed = False
        db_table = 'tbl_designations'
    