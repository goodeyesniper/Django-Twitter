from django.contrib.auth.models import User
from django.views.generic import DetailView, View
from django.contrib.auth.mixins import LoginRequiredMixin
from feed.models import Post
from django.http import JsonResponse, HttpResponseBadRequest
from followers.models import Follower

from django.shortcuts import render, redirect
from django.views import View
from django.contrib.auth import update_session_auth_hash


class AccountSettingsView(LoginRequiredMixin, View):
    template_name = 'profiles/account_settings.html'

    def get(self, request, *args, **kwargs):
        return render(request, self.template_name, {'user': request.user})

    def post(self, request, *args, **kwargs):
        user = request.user
        
        if 'username' in request.POST:
            user.username = request.POST.get('username')
        
        if 'first_name' in request.POST:
            user.first_name = request.POST.get('first_name')
        
        if 'last_name' in request.POST:
            user.last_name = request.POST.get('last_name')
        
        if 'email' in request.POST:
            user.email = request.POST.get('email')
        user.save()

        if 'profile_image' in request.FILES:
            profile = user.profile
            profile.image = request.FILES['profile_image']
            profile.save()

        old_password = request.POST.get('old_password')
        new_password = request.POST.get('new_password')
        new_password_confirm = request.POST.get('new_password_confirm')
        
        if old_password and new_password and new_password_confirm:
            if new_password == new_password_confirm and user.check_password(old_password):
                user.set_password(new_password)
                user.save()
                update_session_auth_hash(request, user)
        
        return redirect('profiles:account_settings')

class ProfileDetailView(DetailView):
    http_method_names = ["get"]
    template_name = "profiles/detail.html"
    model = User
    context_object_name = "user"
    slug_field = "username"
    slug_url_kwarg = "username"

    def dispatch(self, request, *args, **kwargs):
        self.request = request
        return super().dispatch(request, *args, **kwargs)

    def get_context_data(self, **kwargs):
        user = self.get_object()
        context = super().get_context_data(**kwargs)
        context['total_posts'] = Post.objects.filter(author=user).count()
        context['total_followers'] = Follower.objects.filter(following=user).count()
        if self.request.user.is_authenticated:
            context['you_follow'] = Follower.objects.filter(following=user, followed_by=self.request.user).exists()
        return context

class FollowView(LoginRequiredMixin, View):
    http_method_names = ["post"]

    def post(self, request, *args, **kwargs):
        data = request.POST.dict()

        if "action" not in data or "username" not in data:
            return HttpResponseBadRequest("Missing data")
        
        try:
            other_user = User.objects.get(username=data['username'])

        except User.DoesNotExist:
            return HttpResponseBadRequest("Missing user")
        
        if data['action'] == 'follow':
            # Follow
            follower, created = Follower.objects.get_or_create(
                followed_by=request.user,
                following=other_user
            )
        else:
            # Unfollow
            try:
                follower = Follower.objects.get(
                    followed_by=request.user,
                    following=other_user,
                )
            except Follower.DoesNotExist:
                follower = None
            
            if follower:
                follower.delete()

        return JsonResponse({
            'success': True,
            'wording': "Unfollow" if data['action'] == "follow" else "Follow"
        })