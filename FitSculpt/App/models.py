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
    status=models.IntegerField()
    profile_picture=models.FileField(upload_to='client_profile/', blank=True, null=True)
    # class Meta:
    #     managed = False
    #     db_table = 'client'
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
    service_no = models.IntegerField()  # Assuming service_id relates to some service in your application
    
    # class Meta:
    #     managed = False
    #     db_table = 'tbl_plans'
    def __str__(self):
        return self.plan_name

from django.db import models
from django.utils import timezone


class Payment(models.Model):
    payment_id = models.AutoField(primary_key=True)
    plan_id = models.IntegerField() 
    user_id=models.IntegerField()
    payment_date = models.DateTimeField(default=timezone.now)  
    mode = models.CharField(max_length=50) 
    status = models.CharField(max_length=50)  
    active=models.IntegerField()
    # class Meta:
    #     managed = False
    #     db_table = 'tbl_payment'
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
    status=models.IntegerField()
    interview_time=models.DateTimeField()


    # class Meta:
    #     managed = False
    #     db_table = 'tbl_fitness_manager'
    def __str__(self):
        return self.name
    
class Qualifications(models.Model):
    qualification_id=models.AutoField(primary_key=True)
    qualification=models.CharField(max_length=50)
    certification=models.CharField(max_length=100)
    # class Meta:
    #     managed = False
    #     db_table = 'tbl_qualifications'

class Designations(models.Model):
    designation_id=models.AutoField(primary_key=True)
    designation=models.CharField(max_length=50)

    # class Meta:
    #     managed = False
    #     db_table = 'tbl_designations'
    

class Service(models.Model):
    service_id = models.AutoField(primary_key=True)
    service_no=models.IntegerField()
    service_type = models.CharField(max_length=100)
    workout_id = models.IntegerField()
    nutrition_no = models.IntegerField()
    description = models.TextField()
    category = models.CharField(max_length=100)
    day=models.IntegerField()
    # class Meta:
    #     managed = False
    #     db_table = 'tbl_services'

    def __str__(self):
        return self.description

class Workout(models.Model):
    workout_id = models.AutoField(primary_key=True)
    workout_name = models.CharField(max_length=100)
    description = models.TextField()
    body_part = models.CharField(max_length=100)
    duration = models.IntegerField()  
    workout_image = models.FileField(upload_to='workout_img/', blank=True, null=True)
    reference_video=models.CharField(max_length=200)

    # class Meta:
    #     managed = False
    #     db_table = 'tbl_workouts'

    def __str__(self):
        return self.workout_name
    
from django.db import models
    
class FoodDatabase(models.Model):
    food_id = models.AutoField(primary_key=True)
    food_name = models.CharField(max_length=100)
    calories = models.FloatField()
    proteins = models.FloatField()
    carbs = models.FloatField()
    fats = models.FloatField()
    food_type = models.CharField(max_length=50)  

    # class Meta:
    #     managed = False
    #     db_table = 'tbl_food_database'

    def __str__(self):
        return self.food_name

class Nutrition(models.Model):
    nutrition_id = models.AutoField(primary_key=True)
    nutrition_no = models.IntegerField()
    food = models.ForeignKey(FoodDatabase, on_delete=models.CASCADE, related_name='nutritions')
    description = models.TextField()

    # class Meta:
    #     managed = False
    #     db_table = 'tbl_nutritions'

    def __str__(self):
        return self.nutrition_no


class ClientFM(models.Model):
    id=models.AutoField(primary_key=True)
    client_id=models.IntegerField()
    fm_id=models.IntegerField()
    client_name=models.CharField(max_length=50)
    fm_name=models.CharField(max_length=50)
    class_link=models.CharField(max_length=200)
    timing=models.CharField(max_length=50)
    status = models.IntegerField()
    class_time=models.DateTimeField()

    # class Meta:
    #     managed=False
    #     db_table= 'tbl_client_fm'

    def __str__(self):
        return f"{self.client_name} with {self.fm_name}"
    

class ClientFM2(models.Model):
    id=models.AutoField(primary_key=True)
    client_id=models.IntegerField()
    fm_id=models.IntegerField()
    client_name=models.CharField(max_length=50)
    fm_name=models.CharField(max_length=50)
 
    # class Meta:
    #     managed=False
    #     db_table= 'tbl_clientfm2'

    def __str__(self):
        return f"{self.client_name} with {self.fm_name}"


class Message(models.Model):
    id = models.AutoField(primary_key=True)
    sender_id = models.IntegerField()  
    receiver_id = models.IntegerField()  
    message_text = models.CharField(max_length=1000)
    message_reply = models.CharField(max_length=1000)


    # class Meta:
    #     managed=False
    #     db_table = 'tbl_messages'

    def __str__(self):
        return f"Message from {self.sender_id} to {self.receiver_id}"



class EatingHabit(models.Model):
    id = models.AutoField(primary_key=True)
    habit = models.CharField(max_length=50)
    food_item = models.CharField(max_length=50)
    food_type = models.CharField(max_length=50)
    intake_time=models.CharField(max_length=50)
    habit_no=models.IntegerField()  
    intake_no=models.IntegerField()


    # class Meta:
    #     managed=False
    #     db_table='tbl_food_habits'

    def __str__(self):
        return f"{self.habit} - {self.food_item} ({self.food_type})"
    
class EatingHabit2(models.Model):
    id = models.AutoField(primary_key=True)
    client_id=models.IntegerField()
    fm_id=models.IntegerField()
    habit_no=models.IntegerField()
    status=models.IntegerField()
    intake_no=models.IntegerField()

    # class Meta:
    #     managed=False
    #     db_table='tbl_eating_habit'

    def __str__(self):
        return self.habit_no

class Feedback(models.Model):
    id = models.AutoField(primary_key=True)
    user_id=models.IntegerField()
    content=models.CharField(max_length=1000)
    star_rating=models.IntegerField(default=0)
    
    # class Meta:
    #     managed=False
    #     db_table='tbl_feedback'

    def __str__(self):
        return self.id
    
class MentalFitness(models.Model):
    id = models.AutoField(primary_key=True)
    client_id=models.IntegerField()
    fm_id=models.IntegerField()
    client_name=models.CharField(max_length=50)
    fm_name=models.CharField(max_length=50)
    current_mood=models.CharField(max_length=1000)
    distribution=models.CharField(max_length=1000)
    session_link=models.CharField(max_length=500)
    timing=models.CharField(max_length=50)
    class_time=models.DateTimeField()
    status=models.IntegerField()
    
    # class Meta:
    #     managed=False
    #     db_table='tbl_mental_fitness'

    def __str__(self):
        return self.id
    
class Goal(models.Model):
    id = models.AutoField(primary_key=True)
    target_type=models.CharField(max_length=50)
    starting_value=models.IntegerField()
    target_value=models.IntegerField()
    current_value=models.IntegerField()
    user_id=models.IntegerField()
    no_of_days=models.IntegerField()
    start_date=models.DateField()
    end_date=models.DateField()
    description=models.CharField(max_length=500)

    # class Meta:
    #     managed=False
    #     db_table='tbl_goal'

    def __str__(self):
        return self.id

class Progress(models.Model):
    id = models.AutoField(primary_key=True)
    user_id=models.IntegerField()
    starting_bmi=models.FloatField()
    target_bmi=models.CharField(max_length=50)
    current_bmi=models.FloatField()
    current_bmi_date=models.DateField()

    # class Meta:
    #     managed=False
    #     db_table='tbl_progress'

    def __str__(self):
        return self.id

class FMSkills(models.Model):
    id = models.AutoField(primary_key=True)
    fm_id=models.IntegerField()
    gym_pic=models.FileField(upload_to='gym_pic/', blank=True, null=True)
    skills=models.CharField(max_length=500)
    achievements=models.CharField(max_length=500)
    achievement_proof=models.FileField(upload_to='achievement_proof/', blank=True, null=True)
    rating=models.FloatField(default=0)
    rating_count = models.IntegerField(default=0)
    # class Meta:
    #     managed=False
    #     db_table='tbl_fm_skills'

    def __str__(self):
        return self.skills
