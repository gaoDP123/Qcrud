from crud.service import v
from django.utils.safestring import mark_safe
from . import models
from django.conf.urls import url
from django.shortcuts import HttpResponse,render,redirect
from django.forms import ModelForm

#自定制的ModelForm
class UserInfoModelForm(ModelForm):
    class Meta:
        model=models.UserInfo
        fields="__all__"
        error_messages={
            "name":{
                "required":"用户名不能为空"
            }
        }
###########################

class UserInfoConfig(v.CrudConfig):

    #重写方法,用于做权限验证,是否有权限去删除,添加,修改
    # def get_list_display(self):
    #     data=[]
    #     if self.list_display:
    #         data.extend(self.list_display)
    #         data.append(v.CrudConfig.edit)
    #         data.append(v.CrudConfig.delete)
    #         data.insert(0,v.CrudConfig.checkbox)
    #     return data

    #定制页表页面显示的列
    list_display=["id","name","email","ut_id"]
    #精确查找或者模糊查找由这里决定
    search_fields = ["name__contains","email__contains"]
    show_search_form = True

    #用于扩展功能
    def extra_url(self):
        url_list=[
            url(r"^login/$", self.login),
        ]
        return url_list

    def login(self,request):
        return HttpResponse("Ok")
    #####

    #自定制是否显示添加按钮,可根据权限去决定是否显示
    show_add_btn = True
    def get_show_add_btn(self):
        #Session中查看是否有添加的权限
        return self.show_add_btn

    #自定制ModelForm因为每个注册的表中的字段都是不一样,没法去写错误信息
    model_form_class = UserInfoModelForm

    #定制actions
    def multi_del(self,request):
        pk_list = request.POST.getlist("pk")
        self.model_class.objects.filter(pk__in=pk_list).delete()
    multi_del.short_desc="批量删除"

    def multi_init(self,request):
        pk_list = request.POST.getlist("pk")
        # self.model_class.objects.filter(pk__in=pk_list).delete()
    multi_init.short_desc="批量初始化"
    actions = [multi_del,multi_init]
    show_actions = True

class UserTypeConfig(v.CrudConfig):
    list_display = ["id","title"]

class RoleConfig(v.CrudConfig):
    list_display = ["id","caption"]
    show_add_btn=True

v.site.register(models.UserInfo,UserInfoConfig)
v.site.register(models.UserType,UserTypeConfig)
v.site.register(models.Role,RoleConfig)



class HostModelForm(ModelForm):
    class Meta:
        model=models.Host
        fields="__all__"
        error_messages={
            "hostname":{
                'required':"主机名不能为空",
            },
            "ip":{
                'required':"IP不能为空",
                'invalid':"IP格式错误"
            }
        }

class HostConfig(v.CrudConfig):
    def ip_port(self,obj=None,is_header=False):
        if is_header:
            return "自定义列"
        return "%s:%s"%(obj.ip,obj.port)

    list_display = ["id","hostname","ip","port",ip_port]
    #get_list_display

    show_add_btn = True
    #get_show_add_btn

    model_form_class =HostModelForm
    #get_model_form_class

    def extra_url(self):
        urls=[
            url('report/$',self.report_view)
        ]
        return urls

    def report_view(self,request,*args,**kwargs):
        return HttpResponse("自定义报表")

    def delete_view(self,request,nid,*args,**kwargs):
        if request.method=="GET":
            return render(request, "crud/my_delete.html")
        else:
            self.model_class.objects.filter(pk=nid).delete()
            return redirect(self.get_changelist_url())

v.site.register(models.Host,HostConfig)