'''
用法:
    base_url=request.path
    user_length=models.UserInfo.objects.all().count()
    user_obj=Pagination(request.GET.get("page",1),user_length,base_url,request.GET,per_page_count=2)
    data_list=models.UserInfo.objects.all()[user_obj.start_data:user_obj.end_data]
    html_list=user_obj.get_html()

    #跳到编辑页面保留原页面搜索条件
    param=QueryDict(mutable=True)
    param["_list_filter"]=request.GET.urlencode()
    list_condition=param.urlencode()
    return render(request,"userinfo.html",{"list_condition":list_condition,"data_list":data_list,"html_list":html_list})
'''

import copy


class Pagination(object):
    def __init__(self,current_page,total_count,base_url,param,per_page_count=10,show_pagination=11):
        #当前请求在哪一页
        try:
            current_page=int(current_page)
        except Exception as e:
            current_page=1

        #为了动态生成页码地址,获取base_url去生成Url
        self.base_url=base_url
        self.current_page=current_page
        #总数据量
        self.total_count=total_count
        #每页数据量
        self.per_page_count=per_page_count
        #展示页码数量
        self.show_pagination=show_pagination
        max_page_count, remainder = divmod(self.total_count, self.per_page_count)
        if remainder:
            max_page_count = max_page_count + 1
        #最大页码数
        self.max_page_count=max_page_count
        #数据开始位置
        self.start_data = (self.current_page - 1) * self.per_page_count
        #数据结束位置
        self.end_data=self.current_page*self.per_page_count
        #一半的页码数
        self.half_pagination=int(self.show_pagination/2)
        if self.max_page_count<=self.show_pagination:
            start_pagination=1
            end_pagination=self.max_page_count
        else:
            if self.current_page<=self.half_pagination:
                start_pagination=1
                end_pagination=self.show_pagination
            else:
                if self.current_page >= (self.max_page_count - self.half_pagination):
                    start_pagination = self.max_page_count - self.show_pagination + 1
                    end_pagination = max_page_count
                else:
                    start_pagination = self.current_page - self.half_pagination
                    end_pagination = self.current_page + self.half_pagination

        #分页的开始和结尾
        self.start_pagination=start_pagination
        self.end_pagination=end_pagination

        #保留原搜索条件
        new_param=copy.deepcopy(param)
        new_param._mutable=True
        self.param=new_param


    def get_html(self):
        html_list=[]
        self.param["page"]=1
        html_list.append('<a href="%s?%s" style="text-decoration: none" class="pagination">首页</a>' % (self.base_url,self.param.urlencode(),))
        if self.current_page <= 1:
            val1 = '<a  style="text-decoration: none" disabled class="pagination">上一页</a>'
        else:
            self.param["page"]=self.current_page - 1
            val1 = '<a href="%s?%s" style="text-decoration: none" class="pagination">上一页</a>' % (self.base_url,self.param.urlencode())
        html_list.append(val1)

        for i in range(self.start_pagination, self.end_pagination + 1):
            self.param["page"]=i
            if i == self.current_page:
                html_list.append(
                    '<a href="%s?%s" style="text-decoration: none" class="active pagination">%s</a>' % (self.base_url,self.param.urlencode(), i,))
                continue
            html_list.append('<a href="%s?%s" style="text-decoration: none" class="pagination">%s</a>' % (self.base_url,self.param.urlencode(), i,))

        if self.current_page >= self.max_page_count:
            val2 = '<a  style="text-decoration: none" disabled class="pagination">下一页</a>'
        else:
            self.param["page"]=self.current_page+1
            val2 = '<a href="%s?%s" style="text-decoration: none" disabled class="pagination">%s</a>' % (self.base_url,self.param.urlencode(), "下一页",)
        html_list.append(val2)
        self.param["page"]=self.max_page_count
        html_list.append(
            '<a href="%s?%s" style="text-decoration: none" class="pagination">尾页</a>' % (self.base_url,self.param.urlencode()))

        page_html="".join(html_list)

        return page_html

    #引入bootstrap的样式
    def bootstrap_html(self):
        html_list=[]
        self.param["page"]=1
        html_list.append('<li><a href="%s?%s" style="text-decoration: none">首页</a></li>' % (self.base_url,self.param.urlencode(),))
        if self.current_page <= 1:
            val1 = '<li><a  style="text-decoration: none" disabled>上一页</a></li>'
        else:
            self.param["page"]=self.current_page - 1
            val1 = '<li><a href="%s?%s" style="text-decoration: none">上一页</a></li>' % (self.base_url,self.param.urlencode())
        html_list.append(val1)

        for i in range(self.start_pagination, self.end_pagination + 1):
            self.param["page"]=i
            if i == self.current_page:
                html_list.append(
                    '<li class="active"><a href="%s?%s" style="text-decoration: none">%s</a></li>' % (self.base_url,self.param.urlencode(), i,))
                continue
            html_list.append('<li><a href="%s?%s" style="text-decoration: none">%s</a></li>' % (self.base_url,self.param.urlencode(), i,))

        if self.current_page >= self.max_page_count:
            val2 = '<li><a  style="text-decoration: none" disabled >下一页</a></li>'
        else:
            self.param["page"]=self.current_page+1
            val2 = '<li><a href="%s?%s" style="text-decoration: none" disabled>%s</a></li>' % (self.base_url,self.param.urlencode(), "下一页",)
        html_list.append(val2)
        self.param["page"]=self.max_page_count
        html_list.append(
            '<li><a href="%s?%s" style="text-decoration: none">尾页</a></li>' % (self.base_url,self.param.urlencode()))

        page_html="".join(html_list)

        return page_html
