from django.db import models


class Teacher(models.Model):
    first_name = models.CharField(max_length=100)
    last_name = models.CharField(max_length=100)
    email = models.CharField(max_length=50)
    phone = models.CharField(max_length=20)
    room = models.CharField(max_length=20)
    photo = models.ImageField(upload_to='photos/%Y/%m/%d/', default='prof_avatar.jpg')
    created = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.first_name


class Subject(models.Model):
    teacher = models.ForeignKey(Teacher, on_delete=models.CASCADE)
    subject = models.CharField(max_length=100)

    def __str__(self):
        return self.teacher.first_name + 'subject'

