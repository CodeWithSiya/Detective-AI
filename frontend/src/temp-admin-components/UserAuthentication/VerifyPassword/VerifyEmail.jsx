/**
 * VerifyEmail Component
 * 
 * Provides an interface for users to verify their email address using a 6-digit code
 * 
 * authors: Siyabonga Madondo, Ethan Ngwetjana, Lindokuhle Mdlalose
 * version: 13/09/2025
 */

import "./VerifyEmail.css";
import React, { useState, useEffect } from "react";
import { Typewriter } from 'react-simple-typewriter';
import { useNavigate, useLocation } from "react-router-dom";

// Import API functions for email verification
import { verifyEmail, resendVerification, getPendingVerification } from '../AuthHandler';

/**
 * Renders the component for email verification
 * @returns {JSX.Element} The VerifyEmail component
 */
const VerifyEmail = () => {
    const [pin, setPin] = useState(["", "", "", "", "", ""]); // 6-digit code
    const [isLoading, setIsLoading] = useState(false);
    const [errorMessage, setErrorMessage] = useState('');
    const [successMessage, setSuccessMessage] = useState('');
    const [isResending, setIsResending] = useState(false);
    const [email, setEmail] = useState('');
    
    // Initialize navigator for navigation between routes
    const navigate = useNavigate();
    const location = useLocation();

    useEffect(() => {
        // Get email from navigation state or localStorage
        const stateEmail = location.state?.email;
        const pendingVerification = getPendingVerification();
        
        if (stateEmail) {
            setEmail(stateEmail);
        } else if (pendingVerification?.email) {
            setEmail(pendingVerification.email);
        } else {
            // No email found, redirect to signup
            navigate('/signup');
        }
    }, [location.state, navigate]);

    // Function to handle changes in the PIN input fields
    const handleChange = (index, value) => {
        if (/^[0-9]?$/.test(value)) {
            const newPin = [...pin];
            newPin[index] = value;
            setPin(newPin);
            
            // Auto-focus next input
            if (value && index < 5) {
                const nextInput = document.querySelector(`input[data-index="${index + 1}"]`);
                if (nextInput) nextInput.focus();
            }
        }
    };

    // Handle backspace to move to previous input
    const handleKeyDown = (index, e) => {
        if (e.key === 'Backspace' && !pin[index] && index > 0) {
            const prevInput = document.querySelector(`input[data-index="${index - 1}"]`);
            if (prevInput) prevInput.focus();
        }
    };

    // Function to handle resending verification code
    const handleResendCode = async () => {
        if (!email) {
            setErrorMessage('Email not found. Please try signing up again.');
            return;
        }

        setIsResending(true);
        setErrorMessage('');
        setSuccessMessage('');

        try {
            const result = await resendVerification(email);
            
            if (result.success) {
                setSuccessMessage('Verification code resent successfully! Please check your email.');
                // Clear the PIN inputs
                setPin(["", "", "", "", "", ""]);
            } else {
                setErrorMessage(result.message || 'Failed to resend verification code.');
            }
        } catch (error) {
            console.error('Resend verification error:', error);
            setErrorMessage('Failed to resend verification code. Please try again.');
        } finally {
            setIsResending(false);
        }
    };

    /**
     * Handles form submission when the "Verify" button is clicked
     * @param {Event} e 
     */
    const handleSubmit = async (e) => {
        // Prevents default submit behaviour
        e.preventDefault();
        
        setErrorMessage('');
        setSuccessMessage('');
        setIsLoading(true);
        
        const code = pin.join("");
        
        if (code.length !== 6) {
            setErrorMessage("Please enter the complete 6-digit verification code.");
            setIsLoading(false);
            return;
        }

        if (!email) {
            setErrorMessage('Email not found. Please try signing up again.');
            setIsLoading(false);
            return;
        }

        try {
            // Verify the email - this returns token and user data
            const result = await verifyEmail(email, code);
            
            if (result.success) {
                setSuccessMessage('Email verified successfully! Logging you in...');
                
                // The verifyEmail already stores the token and user data in localStorage
                console.log('User verified and logged in:', result.user);
                
                setTimeout(() => {
                    // Go to dashboard after successful verification
                    navigate('/detective');
                }, 1500);
            } else {
                setErrorMessage(result.message || 'Invalid verification code. Please try again.');
                // Clear the PIN on error
                setPin(["", "", "", "", "", ""]);
                // Focus first input
                const firstInput = document.querySelector(`input[data-index="0"]`);
                if (firstInput) firstInput.focus();
            }
        } catch (error) {
            console.error('Email verification error:', error);
            setErrorMessage('An unexpected error occurred. Please try again.');
        } finally {
            setIsLoading(false);
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
                    We have sent a 6-digit code to <strong>{email}</strong>
                </p>

                <form className="verify-form" onSubmit={handleSubmit}>
                    {errorMessage && (
                        <div style={{ 
                            color: '#ef4444', 
                            backgroundColor: '#fef2f2', 
                            border: '1px solid #fecaca',
                            padding: '0.75rem', 
                            borderRadius: '0.375rem', 
                            marginBottom: '1rem',
                            fontSize: '0.875rem'
                        }}>
                            {errorMessage}
                        </div>
                    )}
                    
                    {successMessage && (
                        <div style={{ 
                            color: '#059669', 
                            backgroundColor: '#ecfdf5', 
                            border: '1px solid #a7f3d0',
                            padding: '0.75rem', 
                            borderRadius: '0.375rem', 
                            marginBottom: '1rem',
                            fontSize: '0.875rem'
                        }}>
                            {successMessage}
                        </div>
                    )}

                    <div className="pin-input-group">
                        {pin.map((digit, i) => (
                            <input
                                key={i}
                                type="text"
                                maxLength="1"
                                value={digit}
                                onChange={(e) => handleChange(i, e.target.value)}
                                onKeyDown={(e) => handleKeyDown(i, e)}
                                className="pin-input"
                                data-index={i}
                                disabled={isLoading}
                                autoComplete="off"
                            />
                        ))}
                    </div>

                    <button type="submit" className="verify-button" disabled={isLoading}>
                        {isLoading ? 'Verifying...' : 'Verify Email'}
                    </button>
                    
                    <div style={{ marginTop: '1rem', textAlign: 'center' }}>
                        <p style={{ color: '#6b7280', fontSize: '0.875rem', marginBottom: '0.5rem' }}>
                            Didn't receive the code?
                        </p>
                        <button
                            type="button"
                            onClick={handleResendCode}
                            disabled={isResending || isLoading}
                            style={{
                                background: 'none',
                                border: 'none',
                                color: '#3b82f6',
                                textDecoration: 'underline',
                                cursor: (isResending || isLoading) ? 'not-allowed' : 'pointer',
                                fontSize: '0.875rem',
                                opacity: (isResending || isLoading) ? 0.6 : 1
                            }}
                        >
                            {isResending ? 'Resending...' : 'Resend Code'}
                        </button>
                    </div>
                </form>
            </div>
        </div>
    );
};

export default VerifyEmail;