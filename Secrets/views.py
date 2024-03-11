from django.shortcuts import render, redirect, get_object_or_404
from django.contrib import messages
from .models import Profile, Smitch
from .forms import SmitchForm, SignUpForm, ProfilePicForm, UserUpdateForm
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.forms import UserCreationForm
from django import forms
from django.contrib.auth.models import User

# Create your views here.
def home(request):
    if request.user.is_authenticated:
        form = SmitchForm(request.POST or None)
        if request.method == "POST":
            if form.is_valid():
                smitch = form.save(commit=False)
                smitch.user = request.user
                smitch.save()
                messages.success(request, ("Your Smitch Has Been Posted"))
                redirect('home')

        smitches = Smitch.objects.all().order_by("-created_at")
        return render(request, 'home.html', {"smitches":smitches, "form":form})
    else:
        smitches = Smitch.objects.all().order_by("-created_at")
        return render(request, 'home.html', {"smitches":smitches})
    

def profile_list(request):
    if request.user.is_authenticated:
        profiles = Profile.objects.exclude(user = request.user)

        return render(request, 'profile_list.html',{"profiles":profiles})
    else:
        messages.success(request, ("You Must Be Logged In To View This Page..."))
        return redirect('home')


def unfollow(request, pk):
    if request.user.is_authenticated:
        # get user
        profile = Profile.objects.get(user_id=pk)
        # unfollow user
        request.user.profile.follows.remove(profile)  
        request.user.profile.save()
        messages.success(request, (f"You unfollowed {profile}"))
        return redirect(request.META.get('HTTP_REFERER'))
    else:
        messages.success(request, ("You Must Be Logged In To View This Page..."))
        return redirect('home')


def follow(request, pk):
    if request.user.is_authenticated:
        # get user
        profile = Profile.objects.get(user_id=pk)
        # unfollow user
        request.user.profile.follows.add(profile)  
        request.user.profile.save()
        messages.success(request, (f"You just followed {profile}"))
        return redirect(request.META.get('HTTP_REFERER'))
    else:
        messages.success(request, ("You Must Be Logged In To View This Page..."))
        return redirect('home')


def profile(request, pk):
    if request.user.is_authenticated:
        profile = Profile.objects.get(user_id=pk)
        smitches = Smitch.objects.filter(user_id=pk).order_by("-created_at")

        # Post form logic
        if request.method == "POST":
            # Get current user id
            current_user_profile = request.user.profile
            # Get form data
            action = request.POST['follow']
            # Decide to follow or unfollow
            if action == 'unfollow':
                current_user_profile.follows.remove(profile)
            elif action == 'follow':
                current_user_profile.follows.add(profile)
            #Save the profile
            current_user_profile.save()
            
        return render(request, "profile.html", {"profile":profile, "smitches":smitches})
    else:
        messages.success(request, ("You Must Be Logged In To View This Page..."))
        return redirect('home')


def followers(request, pk):
    if request.user.is_authenticated:
        if request.user.id == pk:
            profiles = Profile.objects.get(user_id = pk)
            return render(request, 'followers.html',{"profiles":profiles})
        else:
            messages.success(request, ("Not your Profile."))
            return redirect('home')
    else:
        messages.success(request, ("You Must Be Logged In To View This Page..."))
        return redirect('home')
    

def follows(request, pk):
    if request.user.is_authenticated:
        if request.user.id == pk:
            profiles = Profile.objects.get(user_id = pk)
            return render(request, 'follows.html',{"profiles":profiles})
        else:
            messages.success(request, ("Not your Profile."))
            return redirect('home')
    else:
        messages.success(request, ("You Must Be Logged In To View This Page..."))
        return redirect('home')


def login_user(request):
    if request.method == "POST":
        username = request.POST['username']
        password = request.POST['password']
        user = authenticate(request, username=username, password=password)
        if user is not None:
            login(request, user)
            messages.success(request, ("You Have Been Logged In!"))
            return redirect('home')
        else:
            messages.success(request, ("There was an error logging in. Please Try Again..."))
            return redirect('login')
        
    else:
        return render(request, "login.html", {})

    
def logout_user(request):
    logout(request)
    messages.success(request, ("You Have Been Logged Out"))
    return redirect('home')


def register_user(request):
    form = SignUpForm()
    if request.method == 'POST':
        form = SignUpForm(request.POST)

        if form.is_valid():
            form.save()
            username = form.cleaned_data['username']
            password = form.cleaned_data['password1']
            # first_name = form.cleaned_data['first_name']
            # last_name = form.cleaned_data['last_name']
            # email = form.cleaned_data['email']
            #Log in User
            user = authenticate(username=username, password=password)
            login(request,user)
            messages.success(request, ("You Have Been successefully registered!"))
            return redirect('home')
        
    return render(request, "register.html", {'form':form})


def update_user(request):
    if request.user.is_authenticated:
        current_user = User.objects.get(id=request.user.id)
        profile_user = Profile.objects.get(user__id=request.user.id)
        # Get Forms 
        user_form = UserUpdateForm(request.POST or None, request.FILES or None, instance=current_user)
        profile_form = ProfilePicForm(request.POST or None, request.FILES or None, instance=profile_user)

        if user_form.is_valid() and profile_form.is_valid():
            user_form.save()
            profile_form.save()
            login(request, current_user)
            messages.success(request, ("Your Profile Has Been Updated!"))
            return redirect('home')
        
        return render(request, "update_user.html", {'user_form':user_form, 'profile_form':profile_form})  
    else:
        messages.success(request, ("You Must Be Logged In To View This Page..."))
        return redirect('home')
        
        
def smitch_like(request, pk):
    if request.user.is_authenticated:
        smitch = get_object_or_404(Smitch, id=pk)
        if smitch.likes.filter(id=request.user.id):
            smitch.likes.remove(request.user)
        else:
            smitch.likes.add(request.user)

        return redirect(request.META.get('HTTP_REFERER'))

    else:
        messages.success(request, ("You Must Be Logged In To View This Page..."))
        return redirect('home')
    
def smitch_share(request, pk):
    smitch = get_object_or_404(Smitch, id=pk)
    if smitch:
       return render(request, "share_smitch.html", {'smitch':smitch}) 
    else:
        messages.success(request, ("The Smitch doesn't exists."))
        return redirect('home')
    

def delete_smitch(request,pk):
    if request.user.is_authenticated:
        smitch = get_object_or_404(Smitch, id=pk)
        if request.user.username == smitch.user.username:
            smitch.delete()
            messages.success(request, ("Your Smitch has been deleted."))
            return redirect(request.META.get('HTTP_REFERER'))
        else:
            messages.success(request, ("That's not your smitch."))
            return redirect('home')
    else:
        messages.success(request, ("The Smitch doesn't exists."))
        return redirect(request.META.get('HTTP_REFERER'))
    

def search(request):
    if request.method == "POST":
        search = request.POST['search']
        searched = Smitch.objects.filter(body__contains = search)
        return render(request, 'search.html', {'search':search, 'searched':searched})
    else:
        return render(request, 'search.html', {})