from django.db import models

class Client(models.Model):
    fname = models.CharField(max_length=50)
    lname = models.CharField(max_length=50)
    username = models.CharField(max_length=50, unique=True)
    password = models.CharField(max_length=20)
    email = models.EmailField(max_length=50, unique=True)
    phone = models.FloatField(max_length=10)

    class Meta:
        managed = False
        db_table = 'client'  # Specify the exact name of your table if it differs

    def __str__(self):
        return self.username
