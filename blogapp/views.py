from django.shortcuts import render, redirect, reverse, get_object_or_404
from django.urls import reverse_lazy
from django.views import View
from django.views.generic import ListView, DetailView, CreateView, UpdateView, DeleteView, FormView
from django.contrib.auth.decorators import login_required
from django.utils.decorators import method_decorator

from .models import Post, Comment, Category
from .forms import PostForm, CommentForm


class Home(ListView):
    model = Post
    template_name = 'blog/home.html'
    context_object_name = 'posts'
    ordering = '-pub_date'
    paginate_by = 3
    """
    # 디폴트 템플릿명 : <app_label>/<model_name>_list.html
    # 디폴트 컨텍스트 변수명 :  <object>_list
    
    paginate_by = 한 페이지에 보여줄 오브젝트의 갯수
    컨텍스트 변수명 = page_obj 
    이전 .has_previous - 현재 .number - 다음 .has_next
    
    출처 : https://wayhome25.github.io/django/2017/05/02/CBV/
    """


# class Home 의 설정을 그대로 가져다 쓰고 template_name 만 커스터마이징함
@method_decorator(login_required, name='dispatch')
class Dashboard(View):
    def get(self, request, *args, **kwargs):
        view = Home.as_view(
            template_name='blog/admin_page.html',
            paginate_by=4,
        )
        return view(request, *args, **kwargs)


class PostDisplay(DetailView):
    model = Post
    template_name = 'blog/post_detail.html'

    """
    # 디폴트 템플릿명 : <app_label>/<model_name>_detail.html
    # 디폴트 컨텍스트 변수명 :  <object>
    출처 : https://wayhome25.github.io/django/2017/05/02/CBV/
    """
    # 조회수
    def get_object(self, queryset=None):
        object = super(PostDisplay, self).get_object()
        object.view_count += 1
        object.save()
        return object

    # 댓글
    def get_context_data(self, **kwargs):
        context = super(PostDisplay, self).get_context_data(**kwargs)
        context['comments'] = Comment.objects.filter(post=self.get_object())
        context['form'] = CommentForm
        return context


@method_decorator(login_required, name='dispatch')
class PostComment(FormView):
    form_class = CommentForm
    template_name = 'blog/post_detail.html'

    def form_valid(self, form):
        form.instance.by = self.request.user
        post = Post.objects.get(pk=self.kwargs['pk'])
        form.instance.post = post
        form.save()
        return super(PostComment, self).form_valid(form)

    def get_success_url(self):
        return reverse_lazy('post_detail', kwargs={'pk': self.kwargs['pk']})


class PostDetail(View):
    def get(self, request, *args, **kwargs):
        view = PostDisplay.as_view()
        return view(request, *args, **kwargs)

    def post(self, request, *args, **kwargs):
        view = PostComment.as_view()
        return view(request, *args, **kwargs)
    '''
    post_detail 에서 처리하는게 두가지이다
    1. post 내용 보여주기
    2. 코멘트 달기
    그래서 여기서 get 방식인 내용보기와 post 방식인 코멘트처리를 분류하고 각각 클래스를 만들어서 처리한다
    '''


@method_decorator(login_required, name='dispatch')
class PostCreate(CreateView):
    model = Post
    fields = (
        'title',
        'category',
        'content',
    )
    template_name = 'blog/post_form.html'

    def form_valid(self, form):
        form.instance.author = self.request.user
        form.save()
        return super(PostCreate, self).form_valid(form)

    """
    # 디폴트 템플릿명 : <app_label>/<model_name>_form.html
    출처 : https://wayhome25.github.io/django/2017/05/02/CBV/
    """


@method_decorator(login_required, name='dispatch')
class PostUpdate(UpdateView):
    model = Post
    template_name = 'blog/post_form.html'
    fields = (
        'title',
        'category',
        'content',
    )


@method_decorator(login_required, name='dispatch')
class PostDelete(DeleteView):
    model = Post
    template_name = 'blog/post_confirm_delete.html'
    context_object_name = 'post'
    success_url = reverse_lazy('dashboard')


class PostCategory(ListView):
    model = Post
    template_name = 'blog/post_category.html'

    def get_queryset(self):
        self.category = get_object_or_404(Category, pk=self.kwargs['pk'])
        return Post.objects.filter(category=self.category)

    def get_context_data(self, *, object_list=None, **kwargs):
        context = super(PostCategory, self).get_context_data(**kwargs)
        context['category'] = self.category
        return context

