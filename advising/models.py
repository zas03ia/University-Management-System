from core.models import *
from session.models import *
from department.models import *
import datetime

# Create your models here.
class StudentSession(BaseModel):
    student = models.ForeignKey(User, on_delete=models.CASCADE)
    session = models.ForeignKey(Session, on_delete=models.CASCADE) 
    section = models.ForeignKey(Section, on_delete=models.CASCADE)
    fee_status = models.BooleanField(default=False)
    organization = models.ForeignKey(Organization, on_delete=models.CASCADE, null=True, blank=True)
    gpa = models.DecimalField(default=0, decimal_places=2, max_digits=3)
    class Meta:
        constraints = [
            models.UniqueConstraint(fields=['student', 'session','organization'], name='student_session_pk1'),
            models.UniqueConstraint(fields=['student','organization'], name='student_session_pk2')
        ]
    