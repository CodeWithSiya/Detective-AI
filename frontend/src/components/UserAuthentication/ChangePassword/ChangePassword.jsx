/**
 * ChangePassword Component
 * Provides an interface for a user to change the password of their account
 * 
 * author: Siyabonga Madondo, Ethan Ngwetjana, Lindokuhle Mdlalose
 * version: 10/09/2025
 */

import React, { useRef, useState, useEffect } from 'react';
import "./ChangePassword.css";
import { Typewriter } from 'react-simple-typewriter';
import { useNavigate, useSearchParams } from 'react-router-dom';
import {Eye, EyeOff} from 'lucide-react';
import axios from 'axios';

const ChangePassword = () => {
    // Get uid and token from URL query params
    const [searchParams] = useSearchParams();
    const uid = searchParams.get('uid');
    const token = searchParams.get('token');
    
    const passwordRef = useRef();
    const confirmPasswordRef = useRef();

    const [showPassword, setShowPassword] = useState(false);
    const [showConfirmPassword, setShowConfirmPassword] = useState(false);
    const [passwordStrength, setPasswordStrength] = useState(0);
    const [passwordMatch, setPasswordMatch] = useState(true);
    const [isLoading, setIsLoading] = useState(false);
    const [errorMessage, setErrorMessage] = useState('');
    const [successMessage, setSuccessMessage] = useState('');

    const navigate = useNavigate();

    // Check if uid and token exist when component loads
    useEffect(() => {
        if (!uid || !token) {
            setErrorMessage('Invalid or missing reset token. Please request a new password reset link.');
        }
    }, [uid, token]);

    const handlePasswordChange = (e) => {
        const value = e.target.value;
        passwordRef.current.value = value;

        let strength = 0;
        if (value.length >= 6) strength += 25;
        if (/[A-Z]/.test(value)) strength += 25;
        if (/[0-9]/.test(value)) strength += 25;
        if (/[^A-Za-z0-9]/.test(value)) strength += 25;

        setPasswordStrength(strength);
    };

    const handleConfirmPasswordChange = (e) => {
        const confirmValue = e.target.value;
        const passwordValue = passwordRef.current.value;
        setPasswordMatch(
            confirmValue === passwordValue || confirmValue === '' || passwordValue === ''
        );
    };

    const handleSubmit = async (e) => {
        e.preventDefault();

        setErrorMessage('');
        setSuccessMessage('');
        setIsLoading(true);

        const password = passwordRef.current.value;
        const confirmPassword = confirmPasswordRef.current.value;

        // Validate uid and token exist
        if (!uid || !token) {
            setErrorMessage("Invalid or missing reset token. Please request a new password reset link.");
            setIsLoading(false);
            return;
        }

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
            // Send uid, token, and new password to backend
            const response = await axios.post('http://localhost:8000/api/users/reset-password/', {
                uid: uid,
                token: token,
                new_password: password,
                confirm_password: confirmPassword
            });

            if (response.data.success) {
                setSuccessMessage(response.data.message || 'Password reset successful! Redirecting to login...');
                
                // Navigate to login page after showing success message
                setTimeout(() => {
                    navigate("/login");
                }, 2000);
            } else {
                setErrorMessage(response.data.error || 'Failed to reset password. The link may have expired.');
            }
        } catch (error) {
            console.error('Password reset error:', error);
            const errorMsg = error.response?.data?.error || 'An unexpected error occurred. Please try again or request a new reset link.';
            setErrorMessage(errorMsg);
        } finally {
            setIsLoading(false);
        }
    };

    // Show error if no uid or token
    if (!uid || !token) {
        return (
            <div className="change-password-container">
                <div className="error-box">
                    <h2>Invalid Reset Link</h2>
                    <p>The password reset link is invalid or has expired.</p>
                    <button onClick={() => navigate('/forgot-password')}>
                        Request New Link
                    </button>
                </div>
            </div>
        );
    }
    
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