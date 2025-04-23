from django.db import models

# Create your models here.
class FundNotification(models.Model):
    fund_id = models.CharField(max_length=20)
    notify_date = models.DateField()
    notify_count = models.IntegerField(default=0)

    class Meta:
        verbose_name = "fund_notification"
        verbose_name_plural = verbose_name
        constraints = [
            models.UniqueConstraint(
                fields=["fund_id", "notify_date"],
                name="unique_fund_notification"
            )
        ]

    def __str__(self):
        return f"{self.fund_id} - {self.notify_date}"
