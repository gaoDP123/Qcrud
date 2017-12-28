from django.db import models


# Create your models here.
class UserInfo(models.Model):
    name=models.CharField(verbose_name="用户名",max_length=32)
    email=models.EmailField(verbose_name="邮箱")
    ut=models.ForeignKey(verbose_name="用户类型",to="UserType")

    def __str__(self):
        return self.name

    class Meta:
        verbose_name_plural="用户信息"

class UserType(models.Model):
    title=models.CharField(verbose_name="用户类型",max_length=32)

    def __str__(self):
        return self.title

    class Meta:
        verbose_name_plural="用户类型"

class Role(models.Model):
    caption=models.CharField(verbose_name="角色名",max_length=32)

    def __str__(self):
        return self.caption

    class Meta:
        verbose_name_plural="角色信息"

#写个Host类去使用crud组件
class Host(models.Model):
    hostname=models.CharField(verbose_name="主机名",max_length=32)
    ip=models.GenericIPAddressField(verbose_name="IP",protocol="both")
    port=models.IntegerField(verbose_name="端口")