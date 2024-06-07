from typing import List
from django.utils import timezone
from ninja import NinjaAPI, ModelSchema, Schema
from pydantic import BaseModel
from django.shortcuts import get_object_or_404
from django.contrib.auth import authenticate, login as auth_login, logout as auth_logout
from .models import Blogpost
from django.contrib.auth.models import User
from django.http import JsonResponse

api = NinjaAPI()

class BlogpostSchema(ModelSchema):
    class Meta:
        model = Blogpost
        fields = "__all__"

class BlogpostCreateSchema(Schema):
    title: str
    body: str

class BlogpostUpdateSchema(Schema):
    title: str = None
    body: str = None

class SignupSchema(BaseModel):
    username: str
    password: str

class LoginSchema(BaseModel):
    username: str
    password: str

@api.get("/blogs", response=List[BlogpostSchema], tags=["blogs"])
def get_blogs(request):
    return Blogpost.objects.all()

@api.post("/signup/", tags=["authentication"])
def signup(request, payload: SignupSchema):
    try:
        user = User.objects.create_user(username=payload.username, password=payload.password)
        return JsonResponse({"success": True, "user_id": user.id})
    except Exception as e:
        return JsonResponse({"success": False, "error": str(e)})

@api.post("/login/", tags=["authentication"])
def login(request, payload: LoginSchema):
    user = authenticate(request, username=payload.username, password=payload.password)
    if user is not None:
        auth_login(request, user)
        return JsonResponse({"success": True})
    else:
        return JsonResponse({"success": False, "error": "Invalid credentials"})

@api.post("/logout/", tags=["authentication"])
def logout(request):
    auth_logout(request)
    return JsonResponse({"success": True})

@api.post("/blogs", response={201: BlogpostSchema, 400: str}, tags=["blogs"])
def post_blog(request, blog: BlogpostCreateSchema):
    try:
        post = Blogpost.objects.create(
            title=blog.title,
            body=blog.body,
            author=request.user,
        )
        return 201, post
    except Exception as e:
        return 400, str(e)

@api.get("/blogs/{blog_id}", response={200: BlogpostSchema, 404: str}, tags=["blogs"])
def get_blog(request, blog_id: int):
    blog = get_object_or_404(Blogpost, id=blog_id)
    return blog

@api.patch("/blogs/{blog_id}", response={200: BlogpostSchema, 403: str, 404: str}, tags=["blogs"])
def update_blog(request, blog_id: int, data: BlogpostUpdateSchema):
    blog = get_object_or_404(Blogpost, id=blog_id)
    if blog.author != request.user:
        return 403, "You do not have permission to edit this blog post."
    
    for attr, value in data.dict().items():
        if value is not None:
            setattr(blog, attr, value)
    blog.edited = True
    blog.last_edit = timezone.now()
    blog.save()
    return blog

@api.delete("/blogs/{blog_id}", response={204: None, 403: str, 404: str}, tags=["blogs"])
def delete_blog(request, blog_id: int):
    blog = get_object_or_404(Blogpost, id=blog_id)
    if blog.author != request.user and not request.user.is_superuser:
        return 403, "You do not have permission to delete this blog post."
    
    blog.delete()
    return 204, None
