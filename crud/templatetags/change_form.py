from django.template import Library
from crud.service.v import site
from django.urls import reverse
from django.forms import ModelChoiceField,ModelMultipleChoiceField
register=Library()

@register.inclusion_tag("crud/form.html")
def form(model_form_obj):
    new_form = []
    for bfield in model_form_obj:
        tmp = {"is_popup": False, "item": bfield}
        # bfield是ModelForm读取对应读取对应models类,然后根据每一个数据库字段,生成Form的字段,BoundField
        if isinstance(bfield.field, ModelChoiceField):
            # 如果是fk,或者m2m的话关联的表
            related_class_name = bfield.field.queryset.model
            if related_class_name in site._registry:
                app_model_name = related_class_name._meta.app_label, related_class_name._meta.model_name
                # 反向生成popup的地址,光有地址不够,假如页面上存在多个popup不知道传给谁
                base_url = reverse("crud:%s_%s_add" % app_model_name)
                # bfield.auto_id查看有ModelForm生成的input标签时自动生成的标签id
                pop_url = "%s?_pop_back_id=%s" % (base_url, bfield.auto_id)
                tmp["is_popup"] = True
                tmp["popup_url"] = pop_url
        new_form.append(tmp)
    return {"form":new_form}