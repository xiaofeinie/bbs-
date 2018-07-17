from django.db import models

# Create your models here.
from django.contrib.auth.models import AbstractUser

class UserInfo(AbstractUser):
    """
    用户表
    """
    # 设置主键
    nid = models.AutoField(primary_key=True)
    # 练习电话，长度11，不能为空且唯一
    telephon = models.CharField(max_length=11, null=True, unique=True)
#
    avatar = models.FileField(upload_to='avatars/', default='avatars/defaule.png')
    create_time = models.DateTimeField(verbose_name='创建时间',auto_now_add=True)

    blog = models.OneToOneField(to='Blog', to_field='nid', null=True, on_delete=models.CASCADE)

    def __str__(self):
        return self.username


class Blog(models.Model):
    """
    博客信息，与UserInfro(用户)表是一对一的关系、
    """
    nid = models.AutoField(primary_key=True)
    title=models.CharField(verbose_name='个人博客信息', max_length=64)
    site_name=models.CharField(verbose_name='站点名称', max_length=64)
    them=models.CharField(verbose_name='博客主题', max_length=32)

    def __str__(self):
        return self.title


class Category(models.Model):
    '''
    博客个人文章分类表,与Blog（博客）表是多对一的关系
    一个博客用户可以创建多个分类（Category）
    '''
    nid = models.AutoField(primary_key=True)
    title = models.CharField(verbose_name='分类标题', max_length=32)
    blog = models.ForeignKey(verbose_name='博客人', to='Blog', to_field='nid', null=True, on_delete=models.CASCADE)
    def __str__(self):
        return self.title


class Tag(models.Model):
    '''
    标签表,与Blog（博客）表是一对多的关系
    一个博客人可以创建多个标签（Tag）
    '''
    nid = models.AutoField(primary_key=True)
    title = models.CharField(verbose_name='个人博客标签', max_length=32)
    blog = models.ForeignKey(verbose_name='对用博客人', to='blog', to_field='nid', null=True, on_delete=models.CASCADE)

    def __str__(self):
        return self.title


class Article(models.Model):
    '''
    文章表，与分类（Category）表是一对多的关系
        与标签（Tag）表是多对多的关系
        一个分类可以有多篇文章，一篇文章不能在多个分类里
        一个标签可以有多篇文章，一篇文章可以在多个标签里
        文章与作者也要建立一个一对多的关系
    '''
    nid = models.AutoField(primary_key=True)
    title = models.CharField(verbose_name='文章标题', max_length=50)
    desc = models.CharField(max_length=255, verbose_name='文章描述')
    create_time = models.DateTimeField(verbose_name='创建时间', auto_now_add=True)
    #文本内容TextField
    content = models.TextField()

    comment_count = models.IntegerField(default=0)
    up_count = models.IntegerField(default=0)
    down_count = models.IntegerField(default=0)

    user = models.ForeignKey(verbose_name='作者', to='UserInfo', to_field='nid', null=True, on_delete=models.CASCADE)
    category = models.ForeignKey(verbose_name='分类', to='Category', to_field='nid', null=True, on_delete=models.CASCADE)
    # through = '')有这个字段，django就不会创建多对多的第三张表了，会根据你写的来
    tags = models.ManyToManyField(verbose_name='标签',to='Tag', through='Article2Tag')
    def __str__(self):
        return self.title


class Article2Tag(models.Model):
    nid = models.AutoField(primary_key=True)
    article = models.ForeignKey(verbose_name='文章', to='Article', to_field='nid', on_delete=models.CASCADE)
    tag = models.ForeignKey(verbose_name='标签', to='Tag', to_field='nid', on_delete=models.CASCADE)



    def __str__(self):
        v = self.article.title+'<----->'+self.tag.title
        return v

class ArticleUpDown(models.Model):
    '''
    点赞表，
    与文章表是一对多的关系：一篇文章可以有多个赞
    与作者表是一对多的关系：一个作者可以个多个文章点赞
    '''
    nid = models.AutoField(primary_key=True)
    user = models.ForeignKey(verbose_name='作者', to='UserInfo', to_field='nid', null=True, on_delete=models.CASCADE)
    article = models.ForeignKey(verbose_name='文章', to='Article', to_field='nid', null=True, on_delete=models.CASCADE)
    is_up = models.BooleanField(default=True)
    class Meta:
        unique_together = [
            ('article', 'user'),
        ]

class Comment(models.Model):
    '''
    评论表，
    与用户表是一对多的关系：一条评论只能是一个用户的
    还需要自己关联自己
    与文章是一对多的关系：一条评论只能是一个文章的
    '''
    nid = models.AutoField(primary_key=True)
    content = models.CharField(verbose_name='评论内容', max_length=255)
    create_time = models.DateTimeField(verbose_name='评论时间', auto_now_add=True)
    user = models.ForeignKey(verbose_name='评论人', to='UserInfo', to_field='nid', null=True, on_delete=models.CASCADE)
    article = models.ForeignKey(verbose_name='评论文章', to='Article', to_field='nid', null=True, on_delete=models.CASCADE)
    parent_comment = models.ForeignKey('Comment', to_field='nid', null=True, on_delete=models.CASCADE,verbose_name='关联自己的')

    def __str__(self):
        return self.content





