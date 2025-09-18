# Uncomment the required imports before adding the code
from django.contrib.auth.models import User
from django.contrib.auth import logout
from django.http import JsonResponse
from django.contrib.auth import login, authenticate
import logging
import json
from django.views.decorators.csrf import csrf_exempt
from .populate import initiate
from .models import CarMake, CarModel
from .restapis import analyze_review_sentiments  # Adjust the path as needed
from .restapis import get_request, post_review
import requests

# Get an instance of a logger
logger = logging.getLogger(__name__)


@csrf_exempt
def login_user(request):
    data = json.loads(request.body)
    username = data['userName']
    password = data['password']

    user = authenticate(username=username, password=password)
    response_data = {"userName": username}

    if user is not None:
        login(request, user)
        response_data = {
            "userName": username,
            "status": "Authenticated"
        }

    return JsonResponse(response_data)


def logout_request(request):
    logout(request)
    return JsonResponse({"userName": ""})


@csrf_exempt
def registration(request):
    data = json.loads(request.body)
    username = data['userName']
    password = data['password']
    first_name = data['firstName']
    last_name = data['lastName']
    email = data['email']
    username_exist = False

    try:
        User.objects.get(username=username)
        username_exist = True
    except User.DoesNotExist:
        logger.debug(f"{username} is a new user")

    if not username_exist:
        user = User.objects.create_user(
            username=username,
            first_name=first_name,
            last_name=last_name,
            password=password,
            email=email
        )
        login(request, user)
        return JsonResponse({
            "userName": username,
            "status": "Authenticated"
        })

    return JsonResponse({"userName": username, "error": "Already Registered"})


def get_cars(request):
    if CarMake.objects.count() == 0:
        initiate()

    car_models = CarModel.objects.select_related('car_make')
    cars = [
        {"CarModel": car_model.name, "CarMake": car_model.car_make.name}
        for car_model in car_models
    ]
    return JsonResponse({"CarModels": cars})


#Update the `get_dealerships` render list of dealerships all by default, particular state if state is passed
def get_dealerships(request, state="All"):
    if(state == "All"):
        endpoint = "/fetchDealers"
    else:
        endpoint = "/fetchDealers/"+state
    dealerships = get_request(endpoint)
    return JsonResponse({"status":200,"dealers":dealerships})


def get_dealer_details(request, dealer_id):
    if dealer_id:
        endpoint = f"/fetchDealer/{dealer_id}"
        dealerships = get_request(endpoint)

        if dealerships and isinstance(dealerships, list):
            dealer = dealerships[0]  # take the first dealer
        else:
            dealer = dealerships  # already a single object

        return JsonResponse({"status": 200, "dealer": dealer})
    else:
        return JsonResponse({"status": 400, "message": "Bad Request"})


def get_dealer_reviews(request, dealer_id): 
    # if dealer id has been provided 
    if(dealer_id): 
        endpoint = "/fetchReviews/dealer/"+str(dealer_id) 
        reviews = get_request(endpoint) 
        for review_detail in reviews: 
            response = analyze_review_sentiments(review_detail['review']) 
            print(response) 
            review_detail['sentiment'] = response['sentiment'] 
        return JsonResponse({"status":200,"reviews":reviews}) 
    else: 
        return JsonResponse({"status":400,"message":"Bad Request"})

def add_review(request):
    if request.method == "POST":
        try:
            data = json.loads(request.body)
            # Optional: If you want to enforce auth, check here
            if request.user.is_anonymous:
                logger.warning("Anonymous user posting review")
                # return JsonResponse({"status":403,"message":"Unauthorized"})
                # OR just allow it:
                pass  

            response = post_review(data)
            return JsonResponse({"status":200})
        except Exception as e:
            logger.error(f"Error posting review: {e}")
            return JsonResponse({"status":400,"message":str(e)})
    else:
        return JsonResponse({"status":405,"message":"Method not allowed"})
