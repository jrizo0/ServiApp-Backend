from django.db import models
# from django.contrib import admin

class Usuario(models.Model):
    nombre_usuario = models.CharField(max_length=200)
    apellido_usuario = models.CharField(max_length=200)
    celular = models.CharField(max_length=200)
    correo_electronico = models.CharField(max_length=200)
    def __str__(self):
        return self.correo_electronico

class Domiciliario(models.Model):
    usuario = models.ForeignKey(Usuario, on_delete=models.CASCADE)
    def __str__(self):
        return self.usuario.correo_electronico

class Cliente(models.Model):
    usuario = models.ForeignKey(Usuario, on_delete=models.CASCADE)
    direccion = models.CharField(max_length=200)
    def __str__(self):
        return self.usuario.correo_electronico

# class Question(models.Model):
#     question_text = models.CharField(max_length=200)
#     pub_date = models.DateTimeField('date published')
#     def __str__(self):
#         return self.question_text
#
#     @admin.display(
#         boolean=True,
#         ordering='pub_date',
#         description='Published recently?',
#     )
#     def was_published_recently(self):
#         now = timezone.now()
#         return now - datetime.timedelta(days=1) <= self.pub_date <= now
#
# class Choice(models.Model):
#     question = models.ForeignKey(Question, on_delete=models.CASCADE)
#     choice_text = models.CharField(max_length=200)
#     votes = models.IntegerField(default=0)
#     def __str__(self):
#         return self.choice_text
