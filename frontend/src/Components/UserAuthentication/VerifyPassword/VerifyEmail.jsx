/**
 * VerifyEmail Component
 * 
 * Provides an interface for users to verify their email address using a PIN code
 * 
 * authors: Siyabonga Madondo, Ethan Ngwetjana, Lindokuhle Mdlalose
 * version: 22/08/2025
 */

import React, { useState } from "react";
import "./VerifyEmail.css";
import { Typewriter } from 'react-simple-typewriter';
import { useNavigate } from "react-router-dom";

// Import utility function to get the email from the forgot password step
import { getEmail } from '../ForgotPassword/ForgotPassword';

/**
 * Renders the component for email verfication
 * @returns {JSX.Element} The VerifyEmail component
 */
const VerifyEmail = () => {
    const [pin, setPin] = useState(["", "", "", ""]);

    //Initialise navigator for navigation between routes
    const navigate = useNavigate();

    // Function to handle changes in the PIN input fields
    const handleChange = (index, value) => {
        if (/^[0-9]?$/.test(value)) {
        const newPin = [...pin];
        newPin[index] = value;
        setPin(newPin);
        }
    };

    /**
     * Handles form submission when the "Verify" button is clicked
     * @param {Event} e 
     */
    const handleSubmit = (e) => {
        // Prevents default submit behaviour
        e.preventDefault();
        const code = pin.join("");
        if (code.length === 4){
            navigate('/change-password');
        }
        else {
            alert("Please enter the 4-digit code sent to your email.");
        }
    };

    return (
        <div className="verify-container">
            <div className="verify-card">
                <h1 className="verify-title">
                <Typewriter
                    words={["Verify your Email"]}
                    loop={1}
                    cursor
                    cursorStyle="_"
                    typeSpeed={70}
                    deleteSpeed={50}
                    delaySpeed={1000}
                />
                </h1>

                <p className="verify-subtitle">
                We have sent a code to <strong>{getEmail()}</strong>
                </p>

                <form className="verify-form" onSubmit={handleSubmit}>
                <div className="pin-input-group">
                    {pin.map((digit, i) => (
                    <input
                        key={i}
                        type="text"
                        maxLength="1"
                        value={digit}
                        onChange={(e) => handleChange(i, e.target.value)}
                        className="pin-input"
                    />
                    ))}
                </div>

                <button type="submit" className="verify-button">
                    Verify Email
                </button>
                </form>
            </div>
        </div>
    );

};

export default VerifyEmail