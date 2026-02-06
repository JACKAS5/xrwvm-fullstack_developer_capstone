import React, { useState, useEffect } from 'react';
import { useParams } from 'react-router-dom';
import "./Dealers.css";
import "../assets/style.css";
import positive_icon from "../assets/positive.png";
import neutral_icon from "../assets/neutral.png";
import negative_icon from "../assets/negative.png";
import review_icon from "../assets/reviewbutton.png";
import Header from '../Header/Header';

const Dealer = () => {
  const { id } = useParams(); // Cleaner way to get dealer ID

  const [dealer, setDealer] = useState(null);
  const [reviews, setReviews] = useState([]);
  const [loadingDealer, setLoadingDealer] = useState(true);
  const [loadingReviews, setLoadingReviews] = useState(true);
  const [error, setError] = useState(null);
  const [postReviewLink, setPostReviewLink] = useState(null);

  // Use window.location.origin for reliable base URL in proxy/lab environments
  const baseUrl = window.location.origin;
  const dealerUrl = `${baseUrl}/djangoapp/dealer/${id}`;
  const reviewsUrl = `${baseUrl}/djangoapp/reviews/dealer/${id}`;
  const postReviewUrl = `${baseUrl}/postreview/${id}`;

  const fetchDealer = async () => {
    try {
      const res = await fetch(dealerUrl, {
        method: "GET",
        credentials: "include", // Include cookies if auth is needed later
      });

      if (!res.ok) {
        throw new Error(`HTTP error! Status: ${res.status}`);
      }

      const data = await res.json();
      console.log('Dealer API Response:', data);

      if (data.status === 200 && data.dealer) {
        setDealer(data.dealer);
      } else {
        setError("Dealer not found or invalid response");
      }
    } catch (err) {
      console.error("Error fetching dealer:", err);
      setError(`Failed to load dealer: ${err.message}`);
    } finally {
      setLoadingDealer(false);
    }
  };

  const fetchReviews = async () => {
    try {
      const res = await fetch(reviewsUrl, {
        method: "GET",
        credentials: "include",
      });

      if (!res.ok) {
        throw new Error(`HTTP error! Status: ${res.status}`);
      }

      const data = await res.json();
      console.log('Reviews API Response:', data);

      if (data.status === 200) {
        if (data.reviews?.length > 0) {
          setReviews(data.reviews);
        } else {
          setReviews([]);
        }
      } else {
        setError(data.message || "Failed to load reviews");
      }
    } catch (err) {
      console.error("Error fetching reviews:", err);
      setError(`Failed to load reviews: ${err.message}`);
    } finally {
      setLoadingReviews(false);
    }
  };

  const getSentimentIcon = (sentiment) => {
    if (sentiment === "positive") return positive_icon;
    if (sentiment === "negative") return negative_icon;
    return neutral_icon;
  };

  useEffect(() => {
    fetchDealer();
    fetchReviews();

    if (sessionStorage.getItem("username")) {
      setPostReviewLink(
        <a href={postReviewUrl} title="Post a Review">
          <img
            src={review_icon}
            style={{ width: '40px', marginLeft: '15px', marginTop: '5px', cursor: 'pointer' }}
            alt="Post Review"
          />
        </a>
      );
    }
  }, [id]); // Re-run if dealer ID changes

  if (loadingDealer) {
    return <div style={{ textAlign: 'center', margin: '50px' }}>Loading dealer information...</div>;
  }

  if (error) {
    return (
      <div style={{ textAlign: 'center', margin: '50px', color: 'red' }}>
        <h2>Error</h2>
        <p>{error}</p>
        <p>Check console for details or try refreshing.</p>
      </div>
    );
  }

  if (!dealer) {
    return <div style={{ textAlign: 'center', margin: '50px' }}>No dealer found</div>;
  }

  return (
    <div style={{ margin: "20px" }}>
      <Header />

      <div style={{ marginTop: "20px" }}>
        <div style={{ display: 'flex', alignItems: 'center' }}>
          <h1 style={{ color: "grey", margin: 0 }}>
            {dealer.full_name}
          </h1>
          {postReviewLink}
        </div>

        <h4 style={{ color: "grey", marginTop: "8px" }}>
          {dealer.city}, {dealer.address}, Zip - {dealer.zip}, {dealer.state}
        </h4>
      </div>

      <div className="reviews_panel" style={{ marginTop: "30px" }}>
        {loadingReviews ? (
          <div>Loading Reviews...</div>
        ) : reviews.length === 0 ? (
          <div style={{ fontStyle: 'italic', color: '#666' }}>No reviews yet. Be the first to review!</div>
        ) : (
          reviews.map((review) => (
            <div className="review_panel" key={review.id || Math.random()}>
              <img
                src={getSentimentIcon(review.sentiment)}
                className="emotion_icon"
                alt={review.sentiment || "Neutral"}
                style={{ width: '32px', height: '32px' }}
              />
              <div className="review">{review.review}</div>
              <div className="reviewer">
                {review.name || "Anonymous"} • 
                {review.car_make || ""} {review.car_model || ""} 
                {review.car_year ? ` (${review.car_year})` : ""}
              </div>
            </div>
          ))
        )}
      </div>
    </div>
  );
};

export default Dealer;