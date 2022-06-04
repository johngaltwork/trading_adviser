from django.db import models
from django.urls import reverse


class AliasModel(models.Model):
    alias = models.EmailField(max_length=100)
    domain_name = models.CharField(max_length=100)
    mailbox = models.EmailField(max_length=100)
    new_alias = models.EmailField(max_length=100)
    old_alias = models.EmailField(max_length=100)

    class Meta:
        managed = False


class RTFModel(models.Model):
    is_enabled = models.BooleanField(default=False)
    local_part = models.CharField(max_length=100)
    new_domain_name = models.CharField(max_length=100)
    old_domain_name = models.CharField(max_length=100)
    is_trial = models.BooleanField(default=False)
    plan_id = models.IntegerField(default=0)
    user_name = models.CharField(max_length=100)
    digit = models.IntegerField(default=0)
    selector = models.CharField(max_length=100)
    private_key = models.CharField(max_length=100)
    public_key = models.CharField(max_length=100)
    new_password = models.CharField(max_length=100)
    password = models.CharField(max_length=100)
    quota = models.IntegerField(default=0)
    is_active = models.BooleanField(default=False)
    enabled = models.BooleanField(default=False)
    mx_record = models.CharField(max_length=100)
    home_dir = models.CharField(max_length=100)
    catch_all = models.BooleanField(default=False)
    active = models.BooleanField(default=False)
    alias = models.EmailField(max_length=100)
    domain_name = models.CharField(max_length=100)
    mailbox = models.EmailField(max_length=100)
    new_alias = models.EmailField(max_length=100)
    old_alias = models.EmailField(max_length=100)

    class Meta:
        managed = False


class WatchListModel(models.Model):
    ticker = models.CharField(max_length=100)
    pnl = models.CharField(max_length=100)
    winrate = models.CharField(max_length=100)
    timeframe = models.CharField(max_length=100)
    winloss = models.CharField(max_length=100)

    # def get_absolute_url(self):
    #     return reverse('breakout', kwargs={'pk': self.pk})
