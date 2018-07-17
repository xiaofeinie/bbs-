from django import template
from django.db.models import Count
from blog import models

register = template.Library()

@register.inclusion_tag("my_de_tags.html")
def get_query_data(username):
    user = models.UserInfo.objects.filter(username=username).first()
    bolg = user.blog



    ret = models.Category.objects.filter(blog=bolg).annotate(c=Count('article__category_id'))

    # 查询当前站点	每一个标签的名称以及对应的文章数
    tag = models.Tag.objects.filter(blog=bolg).annotate(c=Count('article__title'))

    # 日期
    date_list = models.Article.objects.filter(user=user).extra(
        select={'y_m_data': "strftime('%%Y/%%m',create_time)"}).values('y_m_data').annotate(c=Count('title')).values(
        'y_m_data', 'c')


    return {'blog':bolg,'user':user,'ret':ret,'tag':tag,'date_list':date_list,'username':username}