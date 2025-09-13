/**
 * Forgot Password Component
 * 
 * Provides an interface for users to initiate password reset by entering their email
 * 
 * author: Siyabonga Madondo, Ethan Ngwetjana, Lindokuhle Mdlalose
 * version: 10/09/2025
 */

import React, { useRef, useState } from 'react';
import "./ForgotPassword.css";
import { Typewriter } from 'react-simple-typewriter';
import { useNavigate } from 'react-router-dom';
import { forgotPassword } from '../AuthHandler';

let emailValue = null;

/**
 * Function that sets the email for the password reset
 * @param {string} email 
 */
export const setEmail = (email) => {
  emailValue = email;
};

/**
 * Function that gets the email value for the password reset
 * @returns {string|null}
 */
export const getEmail = () => {
  return emailValue;
};

/**
 * Function that renders the form for forgot password component
 * @returns {JSX.Element} ForgotPasswordComponent
 */
const ForgotPassword = () => {
    //Initialise navigator for navigating between routes
    const navigate = useNavigate();

    //Create ref to access email input field
    const emailRef = useRef();
    
    // State for loading and error handling
    const [isLoading, setIsLoading] = useState(false);
    const [errorMessage, setErrorMessage] = useState('');
    const [successMessage, setSuccessMessage] = useState('');

    /**
     * Function gets called when the submit button gets pressed
     * @param {Event} e 
     */
    const handleSubmit = async (e) => {
        //prevents default submission behaviour
        e.preventDefault();
        
        // Clear previous messages
        setErrorMessage('');
        setSuccessMessage('');
        setIsLoading(true);

        const email = emailRef.current.value;

        try {
            // Check if the entered email exists in the system via API
            const result = await forgotPassword(email);

            if (result.success) {
                // If successful, store email for next step and show success message
                setEmail(email);
                setSuccessMessage(result.message);
                
                // Navigate to verify email after showing success message
                setTimeout(() => {
                    navigate('/login');
                }, 5000);
            } else {
                // Error message if not found/invalid
                setErrorMessage(result.message);
            }
        } catch (error) {
            console.error('Forgot password error:', error);
            setErrorMessage('An unexpected error occurred. Please try again.');
        } finally {
            setIsLoading(false);
        }
    };

    return (
        <div className="forgot-container">
            <div className="forgot-card">
                <h1 className="forgot-title">
                <Typewriter
                    words={["Forgot your Password?", "We'll help you reset it!"]}
                    loop={true}
                    cursor
                    cursorStyle="_"
                    typeSpeed={70}
                    deleteSpeed={50}
                    delaySpeed={1000}
                />
                </h1>

                <p className="forgot-subtitle">
                Enter your email below to receive a password reset link
                </p>

                <form className="forgot-form" onSubmit={handleSubmit}>
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
                
                <div className="form-group">
                    <label>Email<span className="required">*</span></label>
                    <input
                    type="email"
                    placeholder="e.g. johndoe@example.com"
                    ref={emailRef}
                    required
                    />
                </div>

                <button type="submit" className="forgot-button" disabled={isLoading}>
                    {isLoading ? 'Sending Reset Link...' : 'Request Reset'}
                </button>
                </form>
            </div>
        </div>
    );
};
export default ForgotPassword;