from django.db import models

class DailyAttendance(models.Model):
    date = models.DateField()
    arrived_at = models.TimeField(null=True, blank=True)
    left_at = models.TimeField(null=True, blank=True)
    student = models.ForeignKey('core.Student', on_delete=models.CASCADE, null=True, blank=True)

    class Meta:
        unique_together = ['date', 'student']

    def __str__(self):
        return f"{self.student.full_name if self.student else 'Unknown'} ({self.date})"