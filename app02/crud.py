from crud.service import v
from . import models

class RoleConfig(v.CrudConfig):
    list_display = ["id","title"]
    show_add_btn = True

v.site.register(models.Role,RoleConfig)

class DepartmentConfig(v.CrudConfig):
    list_display = ["id","caption"]
    show_add_btn = True

v.site.register(models.Department,DepartmentConfig)

class UserInfoConfig(v.CrudConfig):
    def display_gender(self,obj=None,is_header=False):
        if is_header:
            return "性别"
        #语法固定obj.get_对应choice的对象_display(),就能拿到对应的中文
        return obj.get_gender_display()

    def display_roles(self,obj=None,is_header=False):
        if is_header:
            return "角色"
        html=[]
        role_list=obj.roles.all()
        for role in role_list:
            html.append(role.title)
        return ",".join(html)

    comb_filter=[
        v.FilterOption("gender",is_choice=True),
        v.FilterOption("depart",),
        v.FilterOption("roles",multi=True),
    ]

    list_display = ["id","name","email",display_gender,"depart",display_roles]
    show_add_btn = True


v.site.register(models.UserInfo,UserInfoConfig)
