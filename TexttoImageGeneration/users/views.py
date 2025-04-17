from django.contrib import messages
from django.shortcuts import render, HttpResponse
from django.core.files.storage import FileSystemStorage
import os, torch, uuid, time
from django.conf import settings
from users.forms import UserRegistrationForm
from .models import UserRegistrationModel
from diffusers import StableDiffusionPipeline
from PIL import Image
# from better_profanity import profanity

def UserRegisterActions(request):
    if request.method == 'POST':
        form = UserRegistrationForm(request.POST)
        if form.is_valid():
            print('Data is Valid')
            form.save()
            messages.success(request, 'You have been successfully registered')
            form = UserRegistrationForm()
            return render(request, 'UserRegistrations.html', {'form': form})
        else:
            messages.success(request, 'Email or Mobile Already Existed')
            print("Invalid form")
    else:
        form = UserRegistrationForm()
    return render(request, 'UserRegistrations.html', {'form': form})


def UserLoginCheck(request):
    if request.method == "POST":
        loginid = request.POST.get('loginid')
        pswd = request.POST.get('pswd')
        print("Login ID = ", loginid, ' Password = ', pswd)
        try:
            check = UserRegistrationModel.objects.get(loginid=loginid, password=pswd)
            status = check.status
            print('Status is = ', status)
            if status == "activated":
                request.session['id'] = check.id
                request.session['loggeduser'] = check.name
                request.session['loginid'] = loginid
                request.session['email'] = check.email
                print("User id At", check.id, status)
                return render(request, 'users/UserHomePage.html', {})
            else:
                messages.success(request, 'Your Account Not at activated')
                return render(request, 'UserLogin.html')
        except Exception as e:
            print('Exception is ', str(e))
            pass

        messages.success(request, 'Invalid Login id and password')
    return render(request, 'UserLogin.html', {})


def UserHome(request):
    return render(request, 'users/UserHomePage.html', {})


def test_text_to_image(request):
    if request.method == "POST":
        description = request.POST.get('description')
        print("Description is:", description)

        # profanity.load_censor_words()

        # def sanitize_prompt(user_input):
        #     if profanity.contains_profanity(user_input):
        #         return None  # Inappropriate content found
        #     return user_input

        # description = sanitize_prompt(description)

        # if description is None:
        #     # Redirect back to the same page if input is inappropriate
        #     pass
        # messages.success(request, "Image is not generated due to inappropriate content.")
        # return render(request, "users/test_form.html", {})

        # Load the pre-trained Stable Diffusion model
        model_id = "CompVis/stable-diffusion-v1-4"
        device = "cuda" if torch.cuda.is_available() else "cpu"
        # Initialize the pipeline
        pipe = StableDiffusionPipeline.from_pretrained(model_id)
        pipe = pipe.to(device)

        # Function to generate image from text
        def generate_image_from_text(prompt, num_inference_steps=20, guidance_scale=7.5):
            # Generate image
            with torch.autocast("cuda"):
                image = pipe(prompt, num_inference_steps=num_inference_steps, guidance_scale=guidance_scale).images[0]
            return image

        prompt = description
        generated_image = generate_image_from_text(prompt)

        # Save or display the generated image
        # unique_filename = f"generated_image_{uuid.uuid4().hex}.png"
        unique_filename = f"generated_image_{int(time.time())}.png"
        path = os.path.join(settings.MEDIA_ROOT, unique_filename)
        generated_image.save(path)
        image_url = os.path.join(settings.MEDIA_URL, unique_filename)
        # generated_image.show()
        return render(request, "users/test_form_result.html", {"path": path, "image_url": image_url, "text": description})
    else:
        return render(request, "users/test_form.html", {})