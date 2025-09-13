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
// Import API functions for email verification
import { verifyEmail, resendVerification } from '../AuthHandler';

/**
 * Renders the component for email verfication
 * @returns {JSX.Element} The VerifyEmail component
 */
const VerifyEmail = () => {
    const [pin, setPin] = useState(["", "", "", ""]);
    const [isLoading, setIsLoading] = useState(false);
    const [errorMessage, setErrorMessage] = useState('');
    const [successMessage, setSuccessMessage] = useState('');
    const [isResending, setIsResending] = useState(false);
    
    //Initialise navigator for navigation between routes
    const navigate = useNavigate();

    // Function to handle changes in the PIN input fields
    const handleChange = (index, value) => {
        if (/^[0-9]?$/.test(value)) {
            const newPin = [...pin];
            newPin[index] = value;
            setPin(newPin);
            
            // Auto-focus next input
            if (value && index < 3) {
                const nextInput = document.querySelector(`input[data-index="${index + 1}"]`);
                if (nextInput) nextInput.focus();
            }
        }
    };

    // Function to handle resending verification code
    const handleResendCode = async () => {
        setIsResending(true);
        setErrorMessage('');
        setSuccessMessage('');

        try {
            const result = await resendVerification(getEmail());
            
            if (result.success) {
                setSuccessMessage(result.message);
            } else {
                setErrorMessage(result.message);
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
        
        if (code.length !== 4) {
            setErrorMessage("Please enter the complete 4-digit code.");
            setIsLoading(false);
            return;
        }

        try {
            const result = await verifyEmail(getEmail(), code);
            
            if (result.success) {
                setSuccessMessage(result.message);
                // Store the reset token if provided for password reset
                if (result.token) {
                    localStorage.setItem('resetToken', result.token);
                }
                // Navigate to change password page after verification
                setTimeout(() => {
                    navigate('/change-password');
                }, 1500);
            } else {
                setErrorMessage(result.message);
                // Clear the PIN on error
                setPin(["", "", "", ""]);
            }
        } catch (error) {
            console.error('Email verification error:', error);
            setErrorMessage('An unexpected error occurred. Please try again.');
        } finally {
            setIsLoading(false);
        }
    };

    // COMMENTED OUT: Original synchronous verify handler
    /*
    /**
     * Handles form submission when the "Verify" button is clicked
     * @param {Event} e 
     */
    /*
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
    */

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
                        className="pin-input"
                        data-index={i}
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
                        disabled={isResending}
                        style={{
                            background: 'none',
                            border: 'none',
                            color: '#3b82f6',
                            textDecoration: 'underline',
                            cursor: isResending ? 'not-allowed' : 'pointer',
                            fontSize: '0.875rem',
                            opacity: isResending ? 0.6 : 1
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

export default VerifyEmail