/**
 * ChangePassword Component
 * Provides an interface for a user to change the password of their account
 * 
 * author: Siyabonga Madondo, Ethan Ngwetjana, Lindokuhle Mdlalose
 * version: 10/09/2025
 */

import React, { useRef, useState } from 'react';
import "./ChangePassword.css";
import { Typewriter } from 'react-simple-typewriter';
import { useNavigate } from 'react-router-dom';
// Import for utility functions for email retrieval and password changing
import { getEmail } from '../forgotPassword/ForgotPassword';
import { resetPassword } from '../AuthHandler';
import {Eye, EyeOff} from 'lucide-react';
/**
 * Function that renders the form for changing password functionality
 * @returns {JSX.Element} ChangePassword Component
 */

const ChangePassword = () => {
    //store references from fields directly
    const passwordRef = useRef();
    const confirmPasswordRef = useRef();

    const [showPassword, setShowPassword] = useState(false);
    const [showConfirmPassword, setShowConfirmPassword] = useState(false);
    const [passwordStrength, setPasswordStrength] = useState(0);
    const [passwordMatch, setPasswordMatch] = useState(true);
    const [isLoading, setIsLoading] = useState(false);
    const [errorMessage, setErrorMessage] = useState('');
    const [successMessage, setSuccessMessage] = useState('');

    //Initialise navigator for navigation between routes
    const navigate = useNavigate();

    const handlePasswordChange = (e) => {
        const value = e.target.value;
        passwordRef.current.value = value;

        // Simple password strength check
        let strength = 0;
        if (value.length >= 6) strength += 25;
        if (/[A-Z]/.test(value)) strength += 25;
        if (/[0-9]/.test(value)) strength += 25;
        if (/[^A-Za-z0-9]/.test(value)) strength += 25;

        setPasswordStrength(strength);
    };

    // Live check for password match
    const handleConfirmPasswordChange = (e) => {
        const confirmValue = e.target.value;
        const passwordValue = passwordRef.current.value;
        setPasswordMatch(
            confirmValue === passwordValue || confirmValue === '' || passwordValue === ''
        );
    };

    /**
     * Function that gets called when submit button is pressed
     * @param {Event} e - the form submission event
     */
    const handleSubmit = async (e) => {
        //prevents default behaviour from an event occuring
        e.preventDefault();

        // Clear previous messages
        setErrorMessage('');
        setSuccessMessage('');
        setIsLoading(true);

        //extract values form the password input fields
        const password = passwordRef.current.value;
        const confirmPassword = confirmPasswordRef.current.value;

        // Validate passwords match
        if (password !== confirmPassword) {
            setErrorMessage("Passwords do not match");
            setIsLoading(false);
            return;
        }

        // Check password strength
        if (passwordStrength < 75) {
            setErrorMessage("Please choose a stronger password (should contain uppercase letters, numbers, and special characters)");
            setIsLoading(false);
            return;
        }

        try {
            // Get the reset token from localStorage (set during email verification)
            const resetToken = localStorage.getItem('resetToken');
            
            if (!resetToken) {
                setErrorMessage("Invalid session. Please restart the password reset process.");
                setIsLoading(false);
                return;
            }

            // API call to reset password
            const result = await resetPassword(resetToken, password);

            if (result.success) {
                setSuccessMessage(result.message);
                // Clean up stored data
                localStorage.removeItem('resetToken');
                
                // Navigate to login page after showing success message
                setTimeout(() => {
                    navigate("/login");
                }, 2000);
            } else {
                setErrorMessage(result.message);
            }
        } catch (error) {
            console.error('Password reset error:', error);
            setErrorMessage('An unexpected error occurred. Please try again.');
        } finally {
            setIsLoading(false);
        }
    };
    
    return (
        <div className="change-container">
            <div className="change-card">
                <h1 className="change-title">
                <Typewriter
                    words={["Change your Password"]}
                    loop={1}
                    cursor
                    cursorStyle="_"
                    typeSpeed={70}
                    deleteSpeed={50}
                    delaySpeed={1000}
                />
                </h1>

                <p className="change-subtitle">Don't forget it this time!</p>

                <form className="change-form" onSubmit={handleSubmit}>
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
                        <label>New Password<span className="required">*</span></label>
                        <div className="password-input-wrapper">
                            <input
                                type={showPassword ? "text" : "password"}
                                onChange={handlePasswordChange}
                                ref={passwordRef}
                                required
                            />
                            <button
                                type="button"
                                onClick={() => setShowPassword((prev) => !prev)}
                                className="toggle-password"
                                tabIndex={-1}
                            >
                                {showPassword ? <EyeOff className="icon-sm" /> : <Eye className="icon-sm" />}
                            </button>
                        </div>

                        <div className="password-strength-bar">
                            <div
                                className={`password-strength-fill ${
                                passwordStrength < 50
                                    ? "weak"
                                    : passwordStrength < 75
                                    ? "medium"
                                    : "strong"
                                }`}
                                style={{ width: `${passwordStrength}%` }}
                            ></div>
                        </div>
                        <p className="password-strength-label">
                        {passwordStrength === 0
                            ? "Enter a password"
                            : passwordStrength < 50
                            ? "Weak"
                            : passwordStrength < 75
                            ? "Medium"
                            : "Strong"}
                        </p>
                    </div>

                    <div className="form-group">
                        <label>Confirm Password<span className="required">*</span></label>
                        <div className="password-input-wrapper">
                            <input
                                type={showConfirmPassword ? "text" : "password"}
                                ref={confirmPasswordRef}
                                required
                                onChange={handleConfirmPasswordChange}
                            />
                            <button
                                type="button"
                                onClick={() => setShowConfirmPassword((prev) => !prev)}
                                className="toggle-password"
                                tabIndex={-1}
                            >
                                {showConfirmPassword ? <EyeOff className="icon-sm" /> : <Eye className="icon-sm" />}
                            </button>
                        </div>
                        {!passwordMatch && (
                            <p style={{ color: '#ef4444', fontWeight: 600, marginTop: '0.5rem' }}>
                                Passwords do not match!!
                            </p>
                        )}
                    </div>

                    <button type="submit" className="change-button" disabled={isLoading || !passwordMatch || passwordStrength < 50}>
                        {isLoading ? 'Changing Password...' : 'Submit'}
                    </button>
                </form>
            </div>
        </div>
    );
};

export default ChangePassword