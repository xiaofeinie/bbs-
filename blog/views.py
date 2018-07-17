from django.shortcuts import render, redirect, HttpResponse
from blog import models
from django.contrib import auth
from utils.code import check_cord
# Create your views here.


def code(requset):
    '''
    生成图片验证码
    :param requset:
    :return:
    '''
    print('来了')
    img,random_code = check_cord()
    requset.session['random_code'] = random_code
    from io import BytesIO
    stream = BytesIO()
    img.save(stream,'png')

    return HttpResponse(stream.getvalue())




def login(request):

    if request.method == 'GET':
        return render(request, 'login.html')


    user = request.POST.get('user')
    pwd = request.POST.get('pwd')
    cod = request.POST.get('code')
    print(cod)
    print(request.session['random_code'])
    if cod.upper() != request.session['random_code'].upper():
        return render(request,'login.html',{'msg':'验证码错误'})

    user = auth.authenticate(username=user,password=pwd)
    if user:
        auth.login(request,user)
        return redirect('/index/')

    return render(request, 'login.html', {'msg': '用户名或密码错误'})



def index(request):
    article_list = models.Article.objects.all()

    return render(request,'index.html',{'article_list':article_list})


def logout(request):
    auth.logout(request)
    return redirect('/index/')


def on_found(request):
    return render(request,'on_found.html')


def homesite(request, username, **kwargs):
    '''
    个人站点

    '''
    user = models.UserInfo.objects.filter(username=username).first()
    if user:
        # 查询当前站点的对象，bolg表中的title
        bolg = user.blog
        if kwargs:
            condition = kwargs.get('condition')
            params = kwargs.get('params')
            if condition == 'tag':
                article_list = models.Article.objects.filter(user__username=username).filter(tags__title=params)

            elif condition == 'category':
                article_list = models.Article.objects.filter(user__username=username).filter(category__title=params)

            else:
                year,month = params.split('/')
                article_list = models.Article.objects.filter(user__username=username).filter(create_time__month=month,user__create_time__year=year)
        else:
            # 查询当前站点的文章
            article_list = models.Article.objects.filter(user__username=username)

        # # 查询当前站点每一个分类的名称以及对应的文章数
        # ret = models.Category.objects.filter(blog=bolg).annotate(c=Count('article__category_id'))
        #
        #
        # # 查询当前站点	每一个标签的名称以及对应的文章数
        # tag = models.Tag.objects.filter(blog=bolg).annotate(c = Count('article__title'))
        #
        # # 日期
        # date_list = models.Article.objects.filter(user=user).extra(select={'y_m_data':"strftime('%%Y/%%m',create_time)"}).values('y_m_data').annotate(c = Count('title')).values('y_m_data','c')

        return render(request,'homesite.html', {'bolg':bolg,'article_list':article_list,'username':username})
    else:
        return render(request,'on_found.html')


def article_detail(request,username,article_id):

    user = models.UserInfo.objects.filter(username=username).first()
    bolg = user.blog

    article_obj = models.Article.objects.filter(nid=article_id).first()

    user_denglu = auth.get_user(request)

    comment_list = models.Comment.objects.filter(article_id=article_id)


    # ret = models.Category.objects.filter(blog=bolg).annotate(c=Count('article__category_id'))
    #
    # # 查询当前站点	每一个标签的名称以及对应的文章数
    # tag = models.Tag.objects.filter(blog=bolg).annotate(c=Count('article__title'))
    #
    # # 日期
    # date_list = models.Article.objects.filter(user=user).extra(
    #     select={'y_m_data': "strftime('%%Y/%%m',create_time)"}).values('y_m_data').annotate(c=Count('title')).values(
    #     'y_m_data', 'c')
    return render(request,'article_detail.html',{'request':request,'comment_list':comment_list,'bolg': bolg,'article_obj':article_obj,'username':username,'user_denglu':user_denglu})

from django.db import transaction
from django.db.models import F
from django.http import JsonResponse
import json
def digg(request):
    # 获取前端传来的值
    user_id = request.user.pk
    article_id = request.POST.get('pk')
    is_up = json.loads(request.POST.get('is_up'))
    # 定义一个字典
    response={
        "state":True,
        "msg":None
    }
    # 查询这个点赞有没有已经点过了
    obj = models.ArticleUpDown.objects.filter(user_id=user_id,article_id=article_id).first()

    if obj:
        # 如果已经点过了，将这些变量赋值给response，返回给前端
        response['state']=False
        response['handled']=obj.is_up

    else:
        # with transaction.atomic():这是用来服务器回滚，保持ArticleUpDown和Article两个表的数据一致
        with transaction.atomic():

            # 创建点赞记录
            new_obj = models.ArticleUpDown.objects.create(user_id=user_id,article_id=article_id,is_up=is_up)

            # 根据判断在Article表中把up_count或者down_count字段加1
            if is_up:
                models.Article.objects.filter(pk=article_id).update(up_count=F('up_count')+1)
            else:
                models.Article.objects.filter(pk=article_id).update(down_count=F('down_count')+1)
    return JsonResponse(response)


def pinglun(request):
    # 获取前端发来的数据
    content = request.POST.get('content')
    parent_comment_id = request.POST.get('parent_comment_id',None)
    article_id = request.POST.get('article_id')
    user_id = request.user.pk
#     评论对象
    with transaction.atomic():
        content_obj = models.Comment.objects.create(content=content,article_id=article_id,user_id=user_id,parent_comment_id=parent_comment_id)
        models.Article.objects.filter(pk=article_id).update(comment_count=F('comment_count')+1)

    response={'state':True}
    response['timer']=content_obj.create_time.strftime('%Y-%m-%d %X')
    response['content']=content_obj.content
    if parent_comment_id:
        response['fat_content']=content_obj.parent_comment.content
        response['fat_user'] = content_obj.user.username

    return JsonResponse(response)


def backend(request):
    user = request.user
    article_list=models.Article.objects.filter(user=user)
    return render(request,'backend/backend.html',{'article_list':article_list,'user':user})


def add_article(request):
    if request.method == "POST":
        titlet = request.POST.get('title')
        content = request.POST.get('content')
        categ_id = request.POST.get('categ_id')
        tags = request.POST.getlist('tags_id')
        user = request.user


        from bs4 import BeautifulSoup

        content =BeautifulSoup(content,'html.parser')

    #     文章过滤，过滤script标签
        for lin in content.find_all():
            if lin.name == 'script':
                lin.decompose()

    #     soup之后就是纯文章文本了，可以直接切片，写到数据库里面
        desc = content.text[:150]

        article_obj = models.Article.objects.create(title=titlet,desc=desc,user=user,category_id=categ_id,content=str(content))
        for i in tags:
            models.Article2Tag.objects.create(article_id=article_obj.pk,tag_id=i)
        return redirect('/backend/')


    blog = request.user.blog
    category_list=models.Category.objects.filter(blog=blog)
    tag_list=models.Tag.objects.filter(blog=blog)
    return render(request,'backend/add_article.html',{'category_list':category_list,'tag_list':tag_list})


def upparticle(request,id):
    if request.method == 'POST':
        user = request.user
        tag_id = request.POST.getlist('tag_id')
        title = request.POST.get('title')
        content = request.POST.get('content')
        categ_id = request.POST.get('categ_id')
        from bs4 import BeautifulSoup

        content = BeautifulSoup(content, 'html.parser')

        #     文章过滤，过滤script标签
        for lin in content.find_all():
            if lin.name == 'script':
                lin.decompose()

        #     soup之后就是纯文章文本了，可以直接切片，写到数据库里面
        desc = content.text[:150]+'...'


        models.Article.objects.filter(pk=id).update(title=title, desc=desc, user=user, category_id=categ_id,
                                                    content=str(content))


        for i in tag_id:
            ret = models.Article2Tag.objects.filter(article_id=id)
            if i in ret:
                models.Article2Tag.objects.filter(article_id=id).update(tag_id=i)
            else:
                models.Article2Tag.objects.create(article_id=id, tag_id=i)

        return redirect('/backend/')


    article_obj = models.Article.objects.filter(pk=id).first()
    blog = request.user.blog
    category_list = models.Category.objects.filter(blog=blog)
    tag_list = models.Tag.objects.filter(blog=blog)


    return render(request,'backend/upparticle.html',{'article_obj':article_obj,'category_list':category_list,'tag_list':tag_list})


def delarticle(request):
    id = request.POST.get('pk')

    models.Article.objects.filter(pk=id).delete()

    return HttpResponse('Ture')


from cnblog import settings
import os


def upload(request):
    print(request.FILES)
    obj = request.FILES.get('upload_img')
    name = obj.name
    path = os.path.join(settings.BASE_DIR,'static','upload',name)
    with open(path,'wb') as f:
        for i in obj:
            f.write(i)
    import json
    ret = {
        'error':0,
        'url':'/static/upload/'+name
    }

    return HttpResponse(json.dumps(ret))





