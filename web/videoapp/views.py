from django.http import HttpResponse
from django.shortcuts import render
import requests
from django.views.decorators.csrf import csrf_exempt
from instaloader import Instaloader, Post, ConnectionException
import base64
from .forms import URLForm
@csrf_exempt
def enter_url(request):
    if request.method == 'POST':
        form = URLForm(request.POST)

        if form.is_valid():
            url = form.cleaned_data['url']
            if url.startswith("https://www.instagram.com"):
                try:
                    response, title = get_video_info(url)
                    video_url = url
                    return render(request, 'success_page.html', {'title': title,'response': response, 'video_url': video_url})
                except Exception as e:
                    return HttpResponse("An error occurred while processing the URL: {}".format(str(e)), status=500)
            else:
                return HttpResponse("URL is not from Instagram", status=400)
        else:
            return HttpResponse("Invalid form data", status=400)
    else:
        # If it's a GET request or a failed form submission, initialize the form with empty fields
        form = URLForm()

    return render(request, 'enter_url.html', {'form': form})

@csrf_exempt
def get_video_info(url):
    try:
        L = Instaloader()
        post = Post.from_shortcode(L.context, url.split("/")[-2])
        # Fetch video thumbnail
        thumbnail = post._full_metadata_dict['thumbnail_src']
        response = requests.get(thumbnail)
        image_data = base64.b64encode(response.content).decode('utf-8')  # Convert image content to base64
        title = post._full_metadata['edge_media_to_caption']['edges'][0]['node']['text']
        return image_data, title
    except Exception as e:
        raise e

@csrf_exempt
def show_success_page(request,url):
    try:
        response, title = get_video_info(url)
        return render(request, 'success_page.html', {'title': title, 'response': response})
    except Exception as e:
        return render(request, 'error_page.html', {'error_message': str(e)})


@csrf_exempt
def download_video(request):
    try:
        url = request.GET.get('url')
        print("Received URL:", url) # Extract the URL parameter from the request
        if url:
            # You might want to validate the URL here if needed
            L = Instaloader()
            post = Post.from_shortcode(L.context, url.split("/")[-2])
            print("Downloading video",post)
            if post.is_video:
                # Download the video
                target_filename = str(post.mediaid) + ".mp4"
                L.download_post(post, target=target_filename)

                # Set content disposition header for download
                response = HttpResponse("Video downloaded successfully")
                response['Content-Disposition'] = f'attachment; filename="{target_filename}"'
                return response
            else:
                return HttpResponse("The provided URL does not point to a video", status=400)
        else:
            return HttpResponse("URL parameter is missing", status=400)
    except Exception as e:
        return HttpResponse(f"Failed to download video: {str(e)}", status=500)
