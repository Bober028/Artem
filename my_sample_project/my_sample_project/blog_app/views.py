from django.shortcuts import render, get_object_or_404
from django.views.generic.list import ListView
from django.views.generic import DetailView
from django.urls import reverse_lazy
from django.http import Http404
from django.views.decorators.http import require_POST
from django.db.models import Q
from .models import BlogPost
from .forms import CommentForm
from .ownerviews import OwnerDeleteView, OwnerCreateView, OwnerUpdateView


# Список всіх постів з пагінацією
class BlogListView(ListView):
    model = BlogPost
    paginate_by = 5
    queryset = BlogPost.objects.all()  # Вибір всіх постів


# Список опублікованих постів
class MyPostsListView(ListView):
    model = BlogPost
    paginate_by = 5
    queryset = BlogPost.published_objects.all()  # Вибір тільки опублікованих постів


# Детальний перегляд посту
class BlogDetailView(DetailView):
    model = BlogPost

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["comment_form"] = CommentForm()
        return context

    def get_object(self, queryset=None):
        pk = self.kwargs.get("pk")
        year = self.kwargs.get("year")
        month = self.kwargs.get("month")
        day = self.kwargs.get("day")
        slug_id = self.kwargs.get("slug_id")

        if pk:
            return get_object_or_404(self.model, pk=pk)
        elif slug_id:
            return get_object_or_404(
                self.model,
                created_at__year=year,
                created_at__month=month,
                created_at__day=day,
                slug=slug_id,
            )
        else:
            raise Http404("No object found matching the provided criteria.")


# Видалення посту
class BlogDeleteView(OwnerDeleteView):
    model = BlogPost
    success_url = reverse_lazy("blog_app:posts")


# Створення нового посту
class BlogPostCreateView(OwnerCreateView):
    model = BlogPost
    fields = ["title", "text", "status", "tags"]
    success_url = reverse_lazy("blog_app:posts")


# Оновлення існуючого посту
class BlogUpdateView(OwnerUpdateView):
    model = BlogPost
    fields = ["title", "text", "status", "tags"]
    success_url = reverse_lazy("blog_app:posts")


# Додавання коментаря до посту
@require_POST
def post_comment(request, post_id):
    post = get_object_or_404(BlogPost, id=post_id)  # Знаходження посту
    comment = None

    form = CommentForm(data=request.POST)
    if form.is_valid():
        comment = form.save(commit=False)
        comment.post = post
        comment.save()

    return render(
        request,
        "blog_app/comment.html",
        {"blogpost": post, "form": form, "comment": comment},
    )


# Пошук постів
# Пошук постів
def search_posts(request):
    query = request.GET.get('q')  # Отримуємо запит
    results = BlogPost.objects.all()

    if query:
        # Використовуємо фільтрацію по заголовку
        results = results.filter(title__icontains=query)  # Пошук по заголовку

    # Створюємо змінну, яку передамо в шаблон
    some_variable = "Це тестова змінна яку ми передамо в шаблон <b>Тестуємо HTML</b>"

    # Передаємо results та some_variable в контекст шаблону
    return render(request, 'blog_app/search_results.html', {'results': results, 'query': query, 'some_variable': some_variable})




