import copy,json
from django.conf.urls import url,include
from django.shortcuts import render,HttpResponse,redirect
from django.utils.safestring import mark_safe
from django.urls import reverse
from django.forms import ModelForm
from utils.page import Pagination
from django.http import QueryDict
from django.db.models import Q
from django.db.models import ForeignKey,ManyToManyField
from django.forms.models import ModelChoiceField
from django.db import transaction

#组合搜索,搜索条件判断是否是多选,或者是单选类,option选择
class FilterOption(object):
    def __init__(self,field_name,multi=False,condition=None,is_choice=False):
        """

        :param field_name:字段
        :param multi:是否多选
        :param condition:显示数据的筛选条件
        :param is_choice:是否是choice
        """
        self.field_name=field_name
        self.multi=multi
        #由权限去判断是否取出全部的数据
        self.condition=condition
        #判断是否是choice,前端页面好直接用choice的文本
        self.is_choice=is_choice

    #拿到有字段的存在数据库的数据
    def get_queryset(self,_field):
        if self.condition:
            return _field.rel.to.objects.filter(**self.condition)
        return _field.rel.to.objects.all()

    #拿到存在内存中的数据
    def get_choices(self,_field):
        return _field.choices



#组合搜索封装类,用来给前端页面做生成器的
class FilterRow(object):
    def __init__(self,option,data,request):
        self.data=data
        #下面备用,放置以后FilterOption加其他参数
        self.option = option
        self.request=request


    def __iter__(self):
        params=copy.deepcopy(self.request.GET)
        params._mutable=True
        #请求发过来的值
        current_id=params.get(self.option.field_name)
        current_id_list=params.getlist(self.option.field_name)
        if self.option.field_name in params:
            origin_list=params.pop(self.option.field_name)
            url = "{0}?{1}".format(self.request.path_info, params.urlencode())
            yield mark_safe("<a href='{0}'>全部</a>".format(url))
            params.setlist(self.option.field_name,origin_list)
        else:
            url = "{0}?{1}".format(self.request.path_info, params.urlencode())
            yield mark_safe("<a class='active' href='{0}'>全部</a>".format(url))
        for val in self.data:
            if self.option.is_choice:
                pk,text=str(val[0]),val[1]
            else:
                pk,text=str(val.pk),str(val)
            #当前url?option.field_name
            #当前url?gender=pk
            #self.request.path_info#http://127.0.0.1:8000/gdp/app02/userinfo
            #self.request.GET['gender']=1#gender=1
            if not self.option.multi:
                #单选
                params[self.option.field_name]=pk
                url="{0}?{1}".format(self.request.path_info,params.urlencode())
                if current_id==pk:
                    yield mark_safe("<a class='active' href='{0}'>{1}</a>".format(url,text))
                else:
                    yield mark_safe("<a href='{0}'>{1}</a>".format(url, text))
            else:
                #多选
                # 为了不被干扰创建一个新的_params
                _params = copy.deepcopy(params)
                id_list = params.getlist(self.option.field_name)
                if pk in current_id_list:
                    id_list.remove(pk)
                    _params.setlist(self.option.field_name,id_list)
                    url = "{0}?{1}".format(self.request.path_info, _params.urlencode())
                    yield mark_safe("<a class='active' href='{0}'>{1}</a>".format(url, text))
                else:
                    #[1,2]


                    id_list.append(pk)
                    # [1,2,3]
                    #_params中被重新赋值
                    _params.setlist(self.option.field_name,id_list)
                    url = "{0}?{1}".format(self.request.path_info, _params.urlencode())
                    yield mark_safe("<a href='{0}'>{1}</a>".format(url, text))


#列表页面整合类
class ChangeList(object):
    def __init__(self,config,queryset):
        #config是CrudConfig的对象
        self.config=config
        #[checkbox,"id","name",edit,delete]
        self.list_display=config.get_list_display()
        self.model_class=config.model_class
        self.request=config.request
        #最开始的时候就把分页对象创建了
        current_page = self.request.GET.get("page", 1)
        total_count = queryset.count()
        page_obj = Pagination(current_page, total_count, self.request.path_info, self.request.GET, per_page_count=2)
        self.page_obj=page_obj
        self.data_list=queryset[self.page_obj.start_data:self.page_obj.end_data]
        self.show_add_btn=config.get_show_add_btn()
        #是否展示搜索页面
        self.show_search_form=config.get_show_search_form
        self.search_form_value=config.request.GET.get(config.search_key,"")
        #批量删除,actions
        self.actions=config.get_actions()
        self.show_actions=config.get_show_actions()
        #组合搜索
        self.comb_filter=config.get_comb_filter()

    #前端拿到action就直接执行了,所以写一个方法
    def modify_actions(self):
        result=[]
        for func in self.actions:
            tmp={"name":func.__name__,"text":func.short_desc}
            result.append(tmp)
        return result

    #列表页面
    def head_list(self):
        """
        构造表头
        :return:
        """
        result=[]
        for field_name in self.list_display:
            if isinstance(field_name,str):
                verbose_name=self.model_class._meta.get_field(field_name).verbose_name
            else:
                verbose_name=field_name(self.config,is_header=True)
            result.append(verbose_name)
        return result

    def body_list(self):
        """
        把拿到的数据重构结构
        :return:
        """
        data_list =self.data_list
        new_data_list = []
        for data in data_list:
            tmp = []
            for field_name in self.list_display:
                if isinstance(field_name, str):
                    val = getattr(data, field_name)
                else:
                    val = field_name(self.config, data)
                tmp.append(val)
            new_data_list.append(tmp)
        return new_data_list

    def add_url(self):
        return self.config.get_add_url()

    #展示组合搜索
    def gen_comb_filter(self):
        """
        生成器函数
        :return:
        """
        #["gender","depart","roles"]
        #self.model_class=>>models.UserInfo
        for option in self.comb_filter:
            _field=self.model_class._meta.get_field(option.field_name)
            if isinstance(_field,ForeignKey):
                #获取当前字段depart,关联的表Department表并获取其所有数据
                # print(_field.rel.to.objects.all())
                # data_list.append(FilterRow(_field.rel.to.objects.all()))
                row=FilterRow(option,option.get_queryset(_field),self.request)
            elif isinstance(_field,ManyToManyField):
                # print(_field.rel.to.objects.all())
                # data_list.append(FilterRow(_field.rel.to.objects.all()))
                row=FilterRow(option,option.get_queryset(_field),self.request)
            else:
                # data_list.append(FilterRow(_field.choices))
                # print(_field.choices)
                row=FilterRow(option,option.get_choices(_field),self.request)
            #可迭代对象
            yield row


class CrudConfig(object):
    #构造方法
    def __init__(self, model_class, site):
        self.model_class = model_class
        self.site = site
        #方便别人看构造方法的时候知道里面都有说明
        self.request=None
        #list_filter可能很多地方会用,假如要改名字的话要改太多,
        #所以写成活的,这个参数是搜索条件
        self.query_param="list_filter"
        #搜索条件
        self.search_key="_q"


    #列表页面显示内容
    def edit(self,obj=None,is_header=False):
        if is_header:
            return "编辑"
        #获取条件
        query_str=self.request.GET.urlencode()
        if query_str:
            #重新构造
            params=QueryDict(mutable=True)
            params[self.query_param]=query_str
            return mark_safe("<a href='%s?%s'>编辑</a>"%(self.get_change_url(obj.id),params.urlencode(),))
        return mark_safe("<a href='%s'>编辑</a>" % (self.get_change_url(obj.id),))

    def checkbox(self,obj=None,is_header=False):
        if is_header:
            return "选择"
        return mark_safe("<input type='checkbox' name='pk' value='%s' >"%(obj.id))

    def delete(self,obj=None,is_header=False):
        if is_header:
            return "删除"
        return mark_safe("<a href='%s'>删除</a>"%(self.get_delete_url(obj.id)))
    #######################

    list_display = []

    #是否显示添加按钮
    show_add_btn=False
    def get_show_add_btn(self):
        return self.show_add_btn


    #获取list_display
    def get_list_display(self):
        data=[]
        if self.list_display:
            data.extend(self.list_display)
            data.append(CrudConfig.edit)
            data.append(CrudConfig.delete)
            data.insert(0,CrudConfig.checkbox)
        return data


    #因为form错误信息不清楚每个表都有哪些字段,所以在注册页面自己定制,
    #假如没有定制就用默认的
    model_form_class=None
    def get_model_form_class(self):
        if self.model_form_class:
            return self.model_form_class
        #类型一：
        # class TestModelForm(ModelForm):
        #     class Meta:
        #         model = self.model_class
        #         fields = "__all__"

        #类型二:用原类type创建
        meta=type("Meta",(object,),{"model":self.model_class,"fields":"__all__"})
        TestModelForm=type("TestModelForm",(ModelForm,),{"Meta":meta})
        return TestModelForm

    #4.关键字搜索配置
    show_search_form=False
    def get_show_search_form(self):
        return self.show_search_form

    search_fields=[]
    def get_search_fields(self):
        result=[]
        if self.search_fields:
            result.extend(self.search_fields)
        return result

    def get_search_condition(self):
        key_word = self.request.GET.get(self.search_key)
        # search_fields=["name_contains","email__contains"]
        search_fields = self.get_search_fields()

        condition = Q()
        condition.connector = "or"
        if key_word and self.get_show_search_form():
            for field_name in search_fields:
                condition.children.append((field_name, key_word))
                # name__contains="艾" or email="艾"
        return condition

    #5.actions定制
    show_actions=False
    def get_show_actions(self):
        return self.show_actions
    actions=[]
    def get_actions(self):
        result=[]
        if self.actions:
            result.extend(self.actions)
        return result


    #6.组合搜索
    comb_filter=[]
    def get_comb_filter(self):
        result=[]
        if self.comb_filter:
            result.extend(self.comb_filter)
        return result


    ###########URL相关###########
    #用来做保存登录状态的装饰器
    def wrap(self,function_view):
        def inner(request,*args,**kwargs):
            self.request=request
            return function_view(request,*args,**kwargs)
        return inner

    def get_urls(self):
        app_model_name=(self.model_class._meta.app_label,self.model_class._meta.model_name,)
        url_list=[
            url(r"^$",self.wrap(self.changelist_view),name="%s_%s_changelist"%app_model_name),
            url(r"^add/$",self.wrap(self.add_view),name="%s_%s_add"%app_model_name),
            url(r"^(\d+)/change/$",self.wrap(self.change_view),name="%s_%s_change"%app_model_name),
            url(r"^(\d+)/del/$",self.wrap(self.delete_view),name="%s_%s_del"%app_model_name),
        ]
        url_list.extend(self.extra_url())
        return url_list

    def extra_url(self):
        return []

    @property
    def urls(self):
        return self.get_urls()

    def get_change_url(self,nid):
        name = "crud:%s_%s_change" % (self.model_class._meta.app_label,
                                      self.model_class._meta.model_name)
        edit_url = reverse(name, args=(nid,))
        return edit_url

    def get_changelist_url(self,):
        name = "crud:%s_%s_changelist" % (self.model_class._meta.app_label,
                                          self.model_class._meta.model_name)
        changelist_url = reverse(name)
        return changelist_url

    def get_add_url(self,):
        name = "crud:%s_%s_add" % (self.model_class._meta.app_label,
                                   self.model_class._meta.model_name)
        add_url = reverse(name)
        return add_url

    def get_delete_url(self,nid):
        name = "crud:%s_%s_del" % (self.model_class._meta.app_label,
                                   self.model_class._meta.model_name)
        delete_url = reverse(name, args=(nid,))
        return delete_url
    ##############处理请求的方法#########

    '''
    
    [
        [checkbox,"id","name",edit],
        [checkbox,"id","name",edit],
    ]
    
    ["选择","id","用户名","邮箱","用户类型","编辑"]
    '''

    #视图函数
    #列表视图(查)
    def changelist_view(self,request,*args,**kwargs):
        #用于调用edit的时候携带?后面的数据
        # self.request=request
        #但是调用了装饰器,所以这句可以不用写了

        #做action
        if request.method=="POST" and self.get_show_actions():
            func_name_str=request.POST.get("list_action")
            action_func=getattr(self,func_name_str)
            ret=action_func(request)
            if ret:
                return ret

        #组合搜索的条件,可以是Q也可以是字典
        comb_condition={}
        option_list=self.get_comb_filter()
        for key in request.GET.keys():
            value_list=request.GET.getlist(key)
            flag=False
            for option in option_list:
                if option.field_name==key:
                    flag=True
                    break
            if flag:
                comb_condition["%s__in"%key]=value_list


        #处理列表页面的类,把这个对象传进去
        queryset=self.model_class.objects.filter(self.get_search_condition()).filter(**comb_condition).distinct()
        cl=ChangeList(self,queryset)

        #处理分页,因为有分页这个数据就不能完整的拿下来了.
        # current_page=request.GET.get("page",1)
        # total_count=self.model_class.objects.all().count()
        # page_obj=Pagination(current_page,total_count,request.path_info,request.GET,per_page_count=2)
        #有了page_obj后就能把数据切片了
        return render(request, "crud/changelist.html", {"cl":cl})

    #增加视图(增)
    def add_view(self,request,*args,**kwargs):
        model_form_class=self.get_model_form_class()
        _pop_back_id=request.GET.get("_pop_back_id")
        if request.method=="GET":
            form=model_form_class()
            return render(request, "crud/add.html", {"form":form})
        else:
            form=model_form_class(request.POST)
            if form.is_valid():
                #验证成功,在数据库中创建数据
                #有返回值,就是新创建的那条数据
                new_obj=form.save()
                if _pop_back_id:
                    #是popup请求
                    #render一个页面,写自执行函数
                    result={"id":new_obj.pk,"text":str(new_obj),"pop_back_id":_pop_back_id}
                    json_result=json.dumps(result)
                    return render(request, "crud/popup_response.html",{"json_result":json_result})
                else:
                    return redirect(self.get_changelist_url())
            return render(request, "crud/add.html", {"form": form})

    #修改视图(改)
    def change_view(self,request,nid,*args,**kwargs):
        obj=self.model_class.objects.filter(pk=nid).first()
        if not obj:
            return redirect(self.get_changelist_url())

        model_form_class=self.get_model_form_class()
        #GET请求,显示标签+默认值
        if request.method=="GET":
            form=model_form_class(instance=obj)
            return render(request, "crud/change.html", {"form":form})
        else:
            form=model_form_class(instance=obj,data=request.POST)
            if form.is_valid():
                form.save()
                list_query_str=request.GET.get(self.query_param)
                list_url="%s?%s"%(self.get_changelist_url(),list_query_str)
                return redirect(list_url)
            return render(request, "crud/change.html", {"form": form})

    #删除视图(删)
    def delete_view(self,request,nid,*args,**kwargs):
        self.model_class.objects.filter(pk=nid).delete()
        return redirect(self.get_changelist_url())

######################################3




class CrudSite(object):
    def __init__(self):
        self._registry={}

    def register(self,model_class,crud_class=None):
        if not crud_class:
            crud_class=CrudConfig
        self._registry[model_class]=crud_class(model_class,self)

    @property
    def urls(self):
        return self.get_urls(),None,"crud"

    def get_urls(self):
        urlpatterns=[]
        for model_class,crud_class_obj in self._registry.items():
            child_url=url(r"^%s/%s/"%(model_class._meta.app_label,
                                     model_class._meta.model_name),
                          include(crud_class_obj.urls))
            urlpatterns.append(child_url)
        return urlpatterns


site=CrudSite()