from django.shortcuts import render,HttpResponse,redirect
from utils.page import Pagination
from django.http import QueryDict
from app01 import models


# Create your views here.

USER_LIST=[]
for i in range(1,304):
    USER_LIST.append("路过打酱油的用户%s"%i)



HOST_LIST=[]
for i in range(1,20):
    HOST_LIST.append("主机%s"%i)

def user(request):
    # #当前在那一页
    # current_page=int(request.GET.get("page"))
    # #每页数据条数
    # per_page_count=10
    # #总共数据量
    # total_count=len(USER_LIST)
    # #最大页码数
    # max_page_count,remainder=divmod(total_count,per_page_count)
    # if remainder:
    #     max_page_count=max_page_count+1
    # start_data=(current_page-1)*per_page_count
    # #显示的最大页码数
    # show_pagination=11
    # #一半的页码数
    # half_pagination=int(show_pagination/2)
    # if current_page<=half_pagination:
    #     start_pagination=1
    #     end_pagination=show_pagination
    # else:
    #     if current_page>=(max_page_count-half_pagination):
    #         start_pagination = max_page_count - show_pagination+1
    #         end_pagination = max_page_count
    #     else:
    #         start_pagination=current_page-half_pagination
    #         end_pagination=current_page+half_pagination
    #
    # end_data=current_page*per_page_count
    #
    #
    # data_list=USER_LIST[start_data:end_data]
    # html_list=[]
    # html_list.append('<a href="?page=%s" style="text-decoration: none" class="pagination">%s</a>'%(1,"首页",))
    # if current_page<=1:
    #     val1='<a  style="text-decoration: none" disabled class="pagination">%s</a>'%("上一页",)
    # else:
    #     val1='<a href="?page=%s" style="text-decoration: none" class="pagination">%s</a>'%(current_page-1,"上一页",)
    # html_list.append(val1)
    #
    #
    # for i in range(start_pagination,end_pagination+1):
    #     if i==current_page:
    #         html_list.append('<a href="?page=%s" style="text-decoration: none" class="active pagination">%s</a>' % (i, i,))
    #         continue
    #     html_list.append('<a href="?page=%s" style="text-decoration: none" class="pagination">%s</a>'%(i,i,))
    #
    #
    # if current_page>=max_page_count:
    #     val2='<a  style="text-decoration: none" disabled class="pagination">%s</a>'%("下一页",)
    # else:
    #     val2='<a href="?page=%s" style="text-decoration: none" disabled class="pagination">%s</a>'%(current_page+1,"下一页",)
    # html_list.append(val2)
    # html_list.append('<a href="?page=%s" style="text-decoration: none" class="pagination">%s</a>' % (max_page_count, "尾页",))


    base_url=request.path
    user_length=models.UserInfo.objects.all().count()
    user_obj=Pagination(request.GET.get("page"),user_length,base_url,request.GET,per_page_count=2)
    data_list=models.UserInfo.objects.all()[user_obj.start_data:user_obj.end_data]
    html_list=user_obj.get_html()

    #跳到编辑页面保留原页面搜索条件
    param=QueryDict(mutable=True)
    param["_list_filter"]=request.GET.urlencode()
    list_condition=param.urlencode()

    return render(request,"userinfo.html",{"list_condition":list_condition,"data_list":data_list,"html_list":html_list})


def host(request):
    base_url = request.path

    host_obj = Pagination(request.GET.get("page"), len(HOST_LIST), base_url,request.GET)
    data_list = models.UserInfo.objects.all()[host_obj.start_data:host_obj.end_data]
    html_list = host_obj.get_html()

    return render(request, "userinfo.html", {"data_list": data_list, "html_list": html_list})


def edit(request):
    if request.method=="GET":
        print(request.GET)
        return render(request,"edit.html")
    else:
        url="/user/?%s"%(request.GET.get("_list_filter"))
        print(url)
        return redirect(url)