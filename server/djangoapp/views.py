from django.http import JsonResponse
from django.contrib.auth import login, authenticate, logout
from django.contrib.auth.models import User
from django.views.decorators.csrf import csrf_exempt
import logging
import json
import traceback

from .models import CarMake, CarModel
from .populate import initiate
from .restapis import get_request, analyze_review_sentiments, post_review

logger = logging.getLogger(__name__)


@csrf_exempt
def login_user(request):
    """Handle user login via AJAX."""
    try:
        data = json.loads(request.body)
        username = data.get("userName")
        password = data.get("password")

        if not username or not password:
            return JsonResponse({"error": "Missing credentials"}, status=400)

        user = authenticate(username=username, password=password)
        if user is not None:
            login(request, user)
            return JsonResponse({"userName": username, "status": "Authenticated"})
        return JsonResponse({"userName": username, "error": "Invalid credentials"}, status=401)
    except Exception as e:
        logger.error(f"Login failed: {str(e)}")
        return JsonResponse({"error": "Server error"}, status=500)


def logout_request(request):
    """Handle user logout."""
    logout(request)
    return JsonResponse({"userName": ""})


@csrf_exempt
def registration(request):
    """Handle user registration via AJAX."""
    try:
        data = json.loads(request.body)
        username = data.get("userName")
        password = data.get("password")
        first_name = data.get("firstName")
        last_name = data.get("lastName")
        email = data.get("email")

        if User.objects.filter(username=username).exists():
            return JsonResponse(
                {"userName": username, "error": "Already Registered"}, status=400
            )

        user = User.objects.create_user(
            username=username,
            first_name=first_name,
            last_name=last_name,
            password=password,
            email=email,
        )
        login(request, user)
        return JsonResponse({"userName": username, "status": "Authenticated"})
    except Exception as e:
        logger.error(f"Registration failed: {str(e)}")
        return JsonResponse({"error": "Server error"}, status=500)


def get_dealerships(request, state="All"):
    """Fetch dealerships (all or by state)."""
    endpoint = "/fetchDealers" if state == "All" else f"/fetchDealers/{state}"
    dealerships = get_request(endpoint)
    return JsonResponse({"status": 200, "dealers": dealerships})


def get_dealer_details(request, dealer_id):
    """Fetch details for a single dealer."""
    if not dealer_id:
        return JsonResponse({"status": 400, "message": "Bad Request"}, status=400)

    endpoint = f"/fetchDealer/{dealer_id}"
    dealer = get_request(endpoint)
    return JsonResponse({"status": 200, "dealer": dealer})


def get_dealer_reviews(request, dealer_id):
    """Fetch reviews for a dealer and add sentiment analysis."""
    print(f"Received dealer_id: {dealer_id} (type: {type(dealer_id)})")

    if not dealer_id:
        return JsonResponse({"status": 400, "message": "Bad Request"}, status=400)

    endpoint = f"/fetchReviews/dealer/{dealer_id}"
    print(f"Calling endpoint: {endpoint}")

    try:
        raw_response = get_request(endpoint)
        print("Raw response from get_request:", type(raw_response), raw_response)

        # Safely extract reviews list
        if isinstance(raw_response, dict):
            print("Response is dict, keys:", list(raw_response.keys()))
            reviews = raw_response.get("reviews", []) or raw_response.get("data", [])
        elif isinstance(raw_response, list):
            reviews = raw_response
        else:
            reviews = []
            print("Unexpected response type:", type(raw_response))

        print(f"Number of reviews before sentiment: {len(reviews)}")

        # Add sentiment to each review
        for review in reviews:
            if not isinstance(review, dict):
                print("Skipping non-dict review:", review)
                continue

            review_text = review.get("review", "")
            if not review_text:
                review["sentiment"] = "neutral"
                continue

            try:
                sentiment_data = analyze_review_sentiments(review_text)
                review["sentiment"] = sentiment_data.get("sentiment", "neutral")
                print(f"Sentiment for '{review_text[:30]}...': {review['sentiment']}")
            except Exception as sent_err:
                print(f"Sentiment failed: {sent_err}")
                review["sentiment"] = "neutral"

        return JsonResponse({"status": 200, "reviews": reviews})

    except Exception as e:
        print("CRITICAL ERROR in get_dealer_reviews:")
        print(traceback.format_exc())
        return JsonResponse(
            {"status": 500, "message": f"Server error: {str(e)}"},
            status=500,
        )


def add_review(request):
    """Submit a new review (authenticated users only)."""
    if request.user.is_anonymous:
        return JsonResponse({"status": 403, "message": "Unauthorized"}, status=403)

    try:
        data = json.loads(request.body)
        post_review(data)
        return JsonResponse({"status": 200, "message": "Review posted"})
    except Exception as e:
        logger.error(f"Review submission failed: {str(e)}")
        return JsonResponse({"status": 401, "message": "Error posting review"}, status=401)


def get_cars(request):
    """Return list of car models with their makes."""
    if CarMake.objects.count() == 0:
        initiate()

    car_models = CarModel.objects.select_related("car_make")
    cars = [
        {"CarModel": model.name, "CarMake": model.car_make.name}
        for model in car_models
    ]
    return JsonResponse({"CarModels": cars})
