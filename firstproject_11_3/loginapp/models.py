from django.db import models

# 會議室表


class Room(models.Model):
    room_id = models.IntegerField(null=False)
    rName = models.CharField(max_length=15, null=True)
    num = models.IntegerField('可容納人數', null=20)  # 容纳人数

    def __str__(self):
        return self.rName


class customer(models.Model):
    cName = models.CharField(max_length=20, null=False)
    cEmail = models.EmailField(max_length=30, null=False)
    cPassword = models.CharField(max_length=10, null=False)

    def __str__(self):
        return self.cName


# 會議室 預訂資訊
class Book(models.Model):
    user = models.ForeignKey("customer", on_delete=models.CASCADE)
    room = models.ForeignKey("Room", on_delete=models.CASCADE)
    meetingName = models.CharField(max_length=20, null=True)
    meetingInfo = models.CharField(max_length=500, null=True)

    date = models.DateField()
    sessionMember = models.ManyToManyField(
        customer, blank=True, related_name='members')
    time_choice = (
        (1, '8:00'),
        (2, '9:00'),
        (3, '10:00'),
        (4, '11:00'),
        (5, '12:00'),
        (6, '13:00'),
        (7, '14:00'),
        (8, '15:00'),
        (9, '16:00'),
        (10, '17:00'),
        (11, '18:00'),
        (12, '19:00'),
        (13, '20:00'),
    )
    time_id = models.IntegerField(choices=time_choice)

    def __str__(self):
        return (f"{self.user.cName}, {self.room.rName}, {self.date}, {self.time_choice[self.time_id-1][1]}")

    def get_sessionMembers(self):
        return {x for x in self.sessionMember.all()}

    class Meta:
        unique_together = (
            ('room', 'date', 'time_id'),
        )
